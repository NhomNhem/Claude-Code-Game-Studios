# Story 001: Connection State Machine

- **Epic**: Network & Object Pooling
- **System**: Network Manager — State Machine
- **Type**: Logic
- **Priority**: P0
- **Estimate**: 3h
- **Status**: Ready
- **Last Updated**: 2026-06-02

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-network-001` | Online ConnectAsync → State=Connected on success | ✅ ADR-001 |
| `TR-network-002` | Offline ConnectAsync → Connected immediately | ✅ ADR-001 |
| `TR-network-008` | Wraps IBackendService with state machine | ✅ ADR-001 |

## ADR Guidance

**ADR-001 (VContainer DI Architecture):**
- `INetworkManager` registered as interface singleton in TinyRiftScope
- `IBackendService` injected into NetworkManager constructor

## Description

Implements the core connection state machine that wraps `IBackendService`. Exposes `ConnectAsync()` which routes to the appropriate backend implementation (online or offline) and transitions the internal state from Disconnected → Connecting → Connected. Provides synchronous `State` property for consumers.

## Design

- `ConnectionState` enum: `Disconnected`, `Connecting`, `Connected`, `Reconnecting`, `Disconnected`
- `INetworkManager` interface:
  - `ConnectionState State { get; }`
  - `IAsyncConnectResult ConnectAsync(CancellationToken ct)`
  - `event Action<ConnectionState> OnStateChanged`
  - `bool IsOnline { get; }` — reflects BackendSettings asset
- `ConnectionStateMachine` (internal state engine):
  - Guards against duplicate ConnectAsync calls
  - Online path: calls `_backend.ConnectAsync()` → on success → `Connected`; on failure → `Disconnected`
  - Offline path: immediately → `Connected` (no-op backend)
  - Syncs `State` property and fires `OnStateChanged`
- BackendSettings asset read at ConnectAsync time (not cached) to allow runtime config changes
- `IAsyncConnectResult`: `bool Success`, `string ErrorMessage`
- All state transitions logged via `Debug.Log`

## Acceptance Criteria

1. Online ConnectAsync succeeds → State transitions: Disconnected → Connecting → Connected
2. Online ConnectAsync fails → State returns to Disconnected with error message
3. Offline ConnectAsync → State goes Disconnected → Connecting → Connected immediately (no network call)
4. Duplicate ConnectAsync while Connecting → second call is ignored, returns failure result
5. ConnectAsync while Connected → returns success immediately (idempotent)
6. OnStateChanged fires for every state transition
7. State getter is readable from any thread (intent — main thread only in practice)
8. INetworkManager wraps IBackendService (injected, not instantiated)

## Test Evidence Path

- `tests/Foundation/Network/TestConnectionStateMachine.cs`
- Unit tests with mock IBackendService for online/offline/failure paths
- State transition assertions with event spy

## Dependencies

- **Depends on**: None (wraps IBackendService from template)
- **Unlocks**: Story 002 (Reconnection & Error Handling)

## Risks

- `IBackendService.ConnectAsync` may have side effects (UI blocking, scene loading) — ensure cancellation token is respected
- BackendSettings asset might not exist in test environment — default to Offline if missing
