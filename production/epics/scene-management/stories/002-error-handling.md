# Story 002: Error Handling & Safety

- **Epic**: Scene Management
- **System**: Scene Manager
- **Type**: Logic
- **Priority**: P1
- **Estimate**: 3h
- **Status**: Complete
- **Last Updated**: 2026-06-05

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-scene-005` | Null/empty ZoneId defaults to GetDefaultZoneScene() with warning | ✅ ADR-001 |
| `TR-scene-006` | Missing scene in BuildSettings → SceneLoadFailed, GState→Menu | ✅ ADR-001 |
| `TR-scene-007` | 5 consecutive SceneLoadFailed → halt all loading, fatal log | ✅ ADR-001 |
| `TR-scene-014` | Null SceneRegistrySO → fatal error, no subscription (safe disabled) | ✅ ADR-001 |

## ADR Guidance

**ADR-001 (VContainer DI Architecture):**
- Interface singleton in `TinyRiftScope`
- Safe disabled state on init failure
- Fatal errors logged, game continues in degraded state

**Control Manifest (Core Layer):**
- Never throw on expected failure paths (null registry, missing scene)
- Log errors and degrade gracefully

## Description

Implement error handling for the Scene Manager: fallback zone scene for null/empty ZoneId, missing scene detection, consecutive failure escalation, and null registry safe-disabled state.

## Design

### ZoneId Fallback

If `context.loadTarget.ZoneId` is null or empty when transitioning to `InRun`, call `SceneRegistrySO.GetDefaultZoneScene()` and log a warning containing `"ZoneId empty, using default"`.

### Missing Scene Detection

Before calling `LoadSceneAsync`, check if the resolved scene name exists in `EditorBuildSettings.scenes`. If not found:
1. Log error with scene name
2. Publish `SceneLoadFailed(scenePath, exception)` to Event Bus
3. Increment session failure counter
4. Call `GState.TransitionTo(Menu)`

### Consecutive Failure Escalation

- `_consecutiveFailureCount` is a session-scoped integer
- Incremented on every `SceneLoadFailed`
- Reset to 0 on any successful `SceneLoadComplete`
- At count == 5: log fatal error (`Debug.LogError` with `FATAL` prefix), halt all loading — no further `TransitionTo` calls
- Prevent infinite recovery loop if Menu scene itself is broken

### Null Registry Safe Disabled

- In `Start()`/`Awake()`, check `SceneRegistrySO` asset reference
- If null: log fatal error, set `_safeDisabled = true`
- When `_safeDisabled`, do NOT subscribe to `GameStateChanged`
- All public API calls return early (no-op or default values)

## Acceptance Criteria

1. **GIVEN** `context.loadTarget.ZoneId` is null or empty during transition to `InRun`, **WHEN** Scene Manager processes the event, **THEN** it uses `SceneRegistrySO.GetDefaultZoneScene()` and logs a `Warning` containing `"ZoneId empty, using default"`.
2. **GIVEN** the scene path resolved from `SceneRegistrySO` is not present in `EditorBuildSettings.scenes`, **WHEN** `LoadSceneAsync` would be called, **THEN** Scene Manager publishes `SceneLoadFailed(scenePath, reason)`, increments session failure counter, and calls `GState.TransitionTo(Menu)`.
3. **GIVEN** `SceneLoadFailed` fires 5 consecutive times in a single session, **WHEN** the 5th failure occurs, **THEN** Scene Manager halts all loading and logs a fatal error (no further `TransitionTo` calls).
4. **GIVEN** the `SceneRegistrySO` asset reference is null at initialization, **WHEN** Scene Manager starts, **THEN** it logs a fatal error and does not subscribe to `GameStateChanged` (safe disabled state).

## QA Test Cases

- **AC1 (Null ZoneId)**: Fire GameStateChanged with null/empty ZoneId. Verify GetDefaultZoneScene() used and Warning logged containing "ZoneId empty, using default".
- **AC2 (Missing scene)**: Set resolved scene name not in EditorBuildSettings. Verify SceneLoadFailed published, failure counter incremented, GState→Menu.
- **AC3 (5 consecutive failures)**: Fire 5 SceneLoadFailed in a row. Verify 5th triggers fatal log and halts all loading — no further TransitionTo.
- **AC4 (Null registry)**: Set SceneRegistrySO to null. Init Scene Manager. Verify fatal error logged, no subscription to GameStateChanged, all public API no-ops.

**Edge cases**: Consecutive counter resets after successful load, Menu scene itself missing during recovery.

## Test Evidence Path

- `Assets/_TinyRift/Tests/EditMode/SceneManager/SceneManagerErrorHandlingTests.cs`
- All 4 acceptance criteria as individual test methods
- Mock `EditorBuildSettings` for missing scene tests

## Dependencies

- **Scene Story 001** — Scene Load Core (scene resolution logic)

## Unlocks

- Scene Story 003: Activation & Completion Flow

## Risks

- **LOW**: Consecutive failure counter persists across scene loads. Mitigation: this is intentional — the count tracks session-level health, not per-load.
