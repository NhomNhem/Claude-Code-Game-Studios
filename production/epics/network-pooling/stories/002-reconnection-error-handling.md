# Story 002: Reconnection & Error Handling

- **Epic**: Network & Object Pooling
- **System**: Network Manager — Reconnection
- **Type**: Logic
- **Priority**: P1
- **Estimate**: 3h
- **Status**: Ready
- **Last Updated**: 2026-06-02

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-network-003` | Unexpected disconnect → State=Reconnecting, exponential backoff | ✅ ADR-001 |
| `TR-network-004` | Reconnect success → backoff resets to 1s | ✅ ADR-001 |
| `TR-network-005` | 5 failed reconnects → State=Disconnected, critical event | ✅ ADR-001 |
| `TR-network-006` | InRun disconnect → no exceptions, local queue | ✅ ADR-001 |
| `TR-network-007` | App quitting during Reconnecting → clean cancel | ✅ ADR-001 |

## ADR Guidance

**ADR-001 (VContainer DI Architecture):**
- Reconnection logic lives in `NetworkManager`, not a separate service
- Exposes `INetworkCriticalEvent` for subscribers (UI, save system) to react to permanent disconnection

## Description

Extends the connection state machine with automatic reconnection using exponential backoff. Handles unexpected disconnects by transitioning to Reconnecting state and retrying at geometrically increasing intervals (1s, 2s, 4s, 8s, 16s). On 5th consecutive failure, transitions to Disconnected and publishes a critical disconnection event. During an active run (inRun flag), queued operations buffer locally instead of throwing.

## Design

- `ReconnectionPolicy` config:
  - `int maxRetries = 5`
  - `float baseIntervalSeconds = 1.0f`
  - `float maxIntervalSeconds = 30.0f`
- `ReconnectHandler` (internal, owned by NetworkManager):
  - Listens to `IBackendService.OnDisconnected` event
  - On disconnect → cancels any existing retry → starts retry loop (async with CancellationToken)
  - Each retry: delay(interval), attempt ConnectAsync, on success → reset backoff → Connected
  - On failure after maxRetries → State=Disconnected, publish `INetworkCriticalEvent` via IEventBus
- `INetworkCriticalEvent` (readonly record struct): `string Reason`, `int RetryCount`, `float UptimeBeforeFailure`
- In-run mode (toggleable via `bool IsInRun`): disconnect does not throw exceptions — operations queue locally:
  - `Queue<INetworkOperation> _pendingQueue` in NetworkManager
  - Flushed on reconnect success
- App quit handling:
  - `Application.quitting` event → CancellationTokenSource.Cancel() on the retry loop
  - No reconnect attempt started if `_isQuitting` flag is set
- Backoff reset: any successful manual or auto-reconnect ConnectAsync resets interval to baseIntervalSeconds

## Acceptance Criteria

1. Unexpected disconnect → State transitions to Reconnecting within one frame
2. Reconnect retries at intervals: 1s, 2s, 4s, 8s, 16s (geometric, ±10% jitter allowed)
3. Successful reconnect → backoff resets to 1s, State = Connected
4. 5 consecutive reconnect failures → State = Disconnected, INetworkCriticalEvent published
5. InRun mode: disconnect does not throw, ops stored in local queue
6. InRun mode: on reconnect success → queued ops flushed
7. App quitting during Reconnecting → retry loop cancels, no further attempts
8. Manual ConnectAsync during Reconnecting → cancels retry loop, runs new connection

## Test Evidence Path

- `tests/Foundation/Network/TestReconnection.cs`
- Unit tests: mock IBackendService that fires OnDisconnected, verify backoff sequence with virtual time
- Edge cases: max retries, inRun queue, app quit cancellation

## Dependencies

- **Depends on**: Story 001 (Connection State Machine)
- **Unlocks**: None

## Risks

- Async retry loop must survive scene loads — use a MonoBehaviour-driven coroutine or UniTask with a lifetime scope that outlives scenes
- Exponential backoff timer accuracy: use `Time.realtimeSinceStartup` or `Stopwatch`, not `Time.time` (which pauses)
