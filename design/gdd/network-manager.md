# Network Manager

> **Status**: Designed (pending review)
> **Author**: user + agents
> **Last Updated**: 2026-05-26
> **Implements Pillar**: N/A (infrastructure)

## Overview

The Network Manager manages the WebSocket connection lifecycle between the game client and the tiny-rift-server. It wraps the template's `IBackendService` (via `WebSocketSqlBackendService` for online mode or `OfflineBackendService` for dev/fallback) and provides a unified connection state machine with auto-reconnect, connection status queries, and connection state events.

## Player Fantasy

The player never interacts directly with the Network Manager. They experience it as seamless connectivity: the game connects on startup, reconnects automatically if the connection drops, and shows appropriate UI feedback (loading spinner, "reconnecting..." banner) during transient outages. In offline/dev mode, the game works identically with no network dependency visible.

## Detailed Design

### Core Rules

1. **Wraps IBackendService** — NetworkManager receives `IBackendService` via VContainer (injected by `BackendLifetimeScope` or our `TinyRiftScope`). It calls `ConnectAsync()`, `DisconnectAsync()`, and monitors the connection through the service's own state or heartbeat.
2. **Connection state machine** — States: `Disconnected → Connecting → Connected → Disconnecting → Disconnected`. Also `Reconnecting` (sub-state of Disconnected with auto-retry).
3. **Auto-reconnect** — On unexpected disconnect, transitions to `Reconnecting`. Waits `1s → 2s → 4s → 8s → 16s → 30s` exponential backoff, then retries `ConnectAsync()`. Resets to 1s on successful connect. Max retries: 5, then transitions to `Disconnected` permanently and emits a critical event.
4. **Connection health** — Sends a heartbeat ping every 30 seconds. If no pong received within 10 seconds, marks connection as stale and triggers reconnect.
5. **State queries** — Exposes `ConnectionState State`, `bool IsConnected`, `bool IsOnline`.
6. **Startup connection** — On app launch (after VContainer resolve), begins connecting automatically. No blocking — game UI loads with a "connecting..." state.
7. **Scene transitions** — Maintains connection across scene loads (registered in `TinyRiftScope`, which is cross-scene — functionally equivalent to app-scope). See ADR-001 for scope architecture. Only disconnects on explicit disconnect or app quit.
8. **Offline mode** — If `BackendSettings.BackendMode == Offline`, NetworkManager immediately sets state to `Connected` (no real network needed). All state queries work identically.

### State Machine

```
Disconnected ──[ConnectAsync]──→ Connecting ──[success]──→ Connected
    ↑                              │                          │
    │                              │ [failure]                │ [disconnect]
    │                              ↓                          ↓
    └──[reconnect failed]── Reconnecting ←──[unexpected disconnect]
                                │
                                └──[backoff timer]──→ Connecting
```

### API Surface

```csharp
public interface INetworkManager
{
    ConnectionState State { get; }
    bool IsConnected { get; }
    bool IsOnline { get; }      // true if backend mode is Online

    Task ConnectAsync();
    Task DisconnectAsync();

    event Action<ConnectionState> OnStateChanged;
}

public enum ConnectionState
{
    Disconnected,
    Connecting,
    Connected,
    Reconnecting
}
```

### Interactions with Other Systems

| System | Interface | Direction | Data |
|--------|-----------|-----------|------|
| BackendBootstrap | Calls `ConnectAsync()` on startup | Bootstrap → Network | Connection result |
| Account/Profile | Checks `IsConnected` before login call | Account → Network | Connection state |
| Currency System | Checks `IsConnected` before sync call | Currency → Network | Connection state |
| Save/Profile | Checks `IsConnected` before save call | Save → Network | Connection state |
| Event Bus | Publishes `OnNetworkStateChanged` | Network → Event Bus | Connection state enum |
| OfflineBackendService | Auto-sets Connected state | Network → Backend | No-op connection |
| HUD | Shows reconnecting banner on `Reconnecting` | Network → HUD | State change event |

## Formulas

None. Connection state management has no mathematical calculations.

## Edge Cases

- **If `ConnectAsync()` is called while already Connected**: Returns immediately. No-op.
- **If `ConnectAsync()` is called while Reconnecting**: Cancels the current backoff timer and starts a fresh connect attempt.
- **If the game is in Offline mode and `ConnectAsync()` is called**: Immediately transitions to Connected without any network I/O.
- **If all 5 reconnect retries are exhausted**: Transitions to Disconnected and emits a critical `OnNetworkStateChanged`. The HUD shows "Connection lost — check your internet" persistently.
- **If the app quits mid-reconnect**: `Application.quitting` handler calls `DisconnectAsync()` and cancels the backoff timer. No exception.
- **If the heartbeat pong is delayed but eventually arrives**: The connection is not marked stale. The stale detection requires 10 seconds of silence after the 30-second ping. Edge case: delayed pong arriving during reconnect — the stale detection was already triggered and the reconnect is already in flight. The stale pong is silently ignored.
- **If the device loses internet during InRun**: Network transitions to Reconnecting. Gameplay continues uninterrupted (economy updates are queued). On reconnect, queued operations sync. On permanent failure, the run completes with local-only currency that syncs on next successful connection.

## Dependencies

| System | Dependency | Direction | Notes |
|--------|-----------|-----------|-------|
| IBackendService (template) | Required | Network → Backend | `ConnectAsync`/`DisconnectAsync` calls |
| VContainer | Required | Scope → Network | Registered at app-scope |
| Event Bus | Required | Network → Bus | Connection state events |
| BackendSettings.asset | Required | Config → Network | Online/Offline toggle |

## Tuning Knobs

| Knob | Type | Default | Range | Notes |
|------|------|---------|-------|-------|
| Reconnect backoff base | float (s) | 1 | 0.5–10 | First retry delay |
| Reconnect max backoff | float (s) | 30 | 10–120 | Cap on backoff |
| Max reconnect retries | int | 5 | 0–20 | Before permanent failure |
| Heartbeat interval | float (s) | 30 | 10–120 | Ping frequency |
| Heartbeat timeout | float (s) | 10 | 5–30 | Pong timeout before stale |

## Visual/Audio Requirements

None. The Network Manager provides state events but does not render its own UI. The HUD/loading screen is responsible for showing connection feedback.

## UI Requirements

None directly. HUD and loading screen consume `OnStateChanged` to show connection status banners, but those are UI system concerns.

## Acceptance Criteria

- **GIVEN** the app starts in Online mode, **WHEN** `ConnectAsync()` completes successfully, **THEN** `State == Connected` and `IsConnected == true`.
- **GIVEN** the app starts in Offline mode, **WHEN** `ConnectAsync()` is called, **THEN** `State == Connected` immediately with no network I/O.
- **GIVEN** the connection drops unexpectedly, **WHEN** the disconnect is detected, **THEN** `State == Reconnecting` and an exponential backoff timer begins.
- **GIVEN** the connection drops and reconnects, **WHEN** `ConnectAsync()` succeeds during Reconnecting, **THEN** `State == Connected` and the backoff resets to 1s.
- **GIVEN** 5 reconnect attempts have failed, **WHEN** the 5th attempt fails, **THEN** `State == Disconnected` and a critical event is emitted.
- **GIVEN** the game is in InRun and connection drops, **WHEN** gameplay continues, **THEN** no exceptions are thrown and queued operations are stored locally.
- **GIVEN** the app quits during Reconnecting, **WHEN** `Application.quitting` fires, **THEN** the backoff timer is cancelled cleanly.

## Open Questions

1. Should we use the template's `IBackendService.IsConnected` property or implement our own heartbeat? → **Recommendation**: Implement our own heartbeat (more reliable, template-agnostic). The template's connection state may not detect half-open TCP connections.
