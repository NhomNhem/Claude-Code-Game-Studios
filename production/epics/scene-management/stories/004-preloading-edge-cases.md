# Story 004: Preloading & Edge Cases

- **Epic**: Scene Management
- **System**: Scene Manager
- **Type**: Logic
- **Priority**: P1
- **Estimate**: 2h
- **Status**: Complete
- **Last Updated**: 2026-06-05

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-scene-012` | Loading/Paused/Defeat/Victory transitions are silent no-ops | ✅ ADR-001 |
| `TR-scene-015` | PreloadZoneAsync cancelled by incoming GStateChange | ✅ ADR-001 |

## ADR Guidance

**ADR-001 (VContainer DI Architecture):**
- Interface singleton, preload uses `UniTask` + `CancellationToken`
- Silent no-ops are pure state checks — no Event Bus publication

**Control Manifest (Core Layer):**
- Preload is optional — zones can load normally without preload
- CancellationToken linked to Scene Manager lifecycle

## Description

Implement preload support for background zone asset loading and cover edge cases for silent-no-op state transitions. `PreloadZoneAsync` loads a zone scene in the background without activating it. Cancellation is triggered when a conflicting `GameStateChanged` event arrives before preload completes.

## Design

### Preload API

```csharp
UniTask PreloadZoneAsync(ZoneId zoneId, CancellationToken cancellationToken = default);
```

- Initiate `SceneManager.LoadSceneAsync` with `allowSceneActivation = false`
- Store reference to the preload async op
- If preload completes (progress reaches 0.9) before cancellation: scene is ready, activation still requires `ActivateScene()`
- On cancellation: cancel the async op via `CancellationToken`, reset state

### Cancellation on GStateChange

- When `GameStateChanged` arrives during an active preload targeting a different scene:
  1. Cancel the preload (trigger `CancellationToken`)
  2. Start the new scene load immediately
  3. Preloaded assets are released on scene destruction per Unity lifecycle

### Silent No-Ops

Scenes with no corresponding scene to load:

| GameState | Action |
|-----------|--------|
| Loading | Silent no-op |
| Paused | Silent no-op |
| Defeat | Silent no-op |
| Victory | Silent no-op |

No log, no event, no scene operation. Current scene remains loaded.

### Pending Queue Edge Case

If pending request is buffered and its target equals the just-loaded scene, discard silently.

## Acceptance Criteria

1. **GIVEN** `GameStateChanged` with target `Loading`, `Paused`, `Defeat`, or `Victory` is received, **WHEN** Scene Manager processes the event, **THEN** no scene load is initiated and no event is published (silent no-op).
2. **GIVEN** `PreloadZoneAsync(zoneId)` is called and a `GameStateChanged` event arrives for a different scene before preload completes, **WHEN** Scene Manager processes the event, **THEN** the preload `CancellationToken` is triggered and the load proceeds normally.
3. **GIVEN** preload is in progress and completes without cancellation, **WHEN** the load is ready, **THEN** the scene is prepared with `allowSceneActivation = false` and awaits `ActivateScene()`.
4. **GIVEN** a buffered pending request whose target equals the just-loaded scene, **WHEN** the current load completes, **THEN** the pending request is discarded silently (no load initiated).

## QA Test Cases

- **AC1 (Silent no-ops)**: Fire GameStateChanged with Loading, Paused, Defeat, Victory. Verify no scene load, no event published.
- **AC2 (Preload cancelled)**: Start PreloadZoneAsync(A). Fire GameStateChanged targeting scene B before preload completes. Verify CancellationToken triggered, new load proceeds.
- **AC3 (Preload completes)**: Start PreloadZoneAsync(A). Let it reach 0.9. Verify scene ready with allowSceneActivation=false, awaiting ActivateScene().
- **AC4 (Pending discard)**: Buffer a pending request for scene A. Current load completes on scene A. Verify pending request silently discarded.

**Edge cases**: Multiple preload calls in sequence, preload cancelled at exactly 0.9 progress.

## Test Evidence Path

- `Assets/_TinyRift/Tests/EditMode/SceneManager/SceneManagerPreloadEdgeTests.cs`
- All 4 acceptance criteria as individual test methods
- CancellationToken tests simulate race between preload and GStateChange

## Dependencies

- **Scene Story 003** — Activation & Completion Flow (for activation handshake after preload)

## Unlocks

- None (terminal story in Scene Management epic)

## Risks

- **LOW**: Preload may waste memory if cancelled after assets are loaded. Mitigation: Unity releases preloaded assets on scene destruction — no manual cleanup needed.

## Completion Notes
**Completed**: 2026-06-05
**Criteria**: 4/4 passing
**Deviations**: QA identified advisory coverage gaps (sequential preload calls, cancellation at 0.9 edge case)
**Test Evidence**: Logic: test file at Assets/_TinyRift/Tests/EditMode/SceneManager/SceneManagerPreloadEdgeTests.cs
**Code Review**: APPROVED WITH SUGGESTIONS — 1 blocking fix applied (CTS leak), remaining suggestions non-blocking
