# Story 003: Activation & Completion Flow

- **Epic**: Scene Management
- **System**: Scene Manager
- **Type**: Logic
- **Priority**: P0
- **Estimate**: 3h
- **Status**: Complete
- **Last Updated**: 2026-06-04

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-scene-008` | AsyncOperation at 0.9 → SceneReadyToActivate with allowSceneActivation=false | ✅ ADR-001 |
| `TR-scene-009` | ActivateScene() sets allowSceneActivation=true, activates in 1 frame | ✅ ADR-001 |
| `TR-scene-010` | 10s timeout on SceneReadyToActivate → auto-activate with warning | ✅ ADR-001 |
| `TR-scene-011` | Load complete → SceneLoadComplete published | ✅ ADR-001 |
| `TR-scene-013` | Built-in fade fallback (fade to black before activation, fade in after) | ✅ ADR-001 |

## ADR Guidance

**ADR-001 (VContainer DI Architecture):**
- Interface singleton, progress exposed via `LoadProgress` property
- Event Bus publishing for scene lifecycle events

**Control Manifest (Core Layer):**
- Built-in fallback self-disables when Loading/Transition System registers itself

## Description

Implement the scene activation handshake and completion flow. When `AsyncOperation.progress` reaches 0.9, publish `SceneReadyToActivate`. Expose `ActivateScene()` for the Loading/Transition System to call. Include 10-second safety auto-activation timeout. Publish `SceneLoadComplete` when activation finishes. Provide a built-in `CanvasGroup`-based fade fallback when Loading/Transition System is absent.

## Design

### Activation Handshake

```
AsyncOperation.progress reaches 0.9
  → Publish SceneReadyToActivate(sceneName)
  → Start 10s safety coroutine
  → (Loading/Transition completes visual → calls ActivateScene())
  → ActivateScene() sets allowSceneActivation = true
  → AsyncOperation completes (isDone = true)
  → Publish SceneLoadComplete(sceneName)
```

### Safety Timeout

- Coroutine waits 10 seconds after `SceneReadyToActivate` publish
- If `ActivateScene()` not called by then, auto-activate with a `Warning` log
- Timeout cancelled if `ActivateScene()` is called before expiry
- Timer reset on each new load (only one timer active at a time)

### Configuration
- `float ActivationTimeoutSeconds = 10f` — configurable via constructor injection or serialized field, allows tests to use short values (e.g., 0.1s) instead of waiting 10 real seconds.

### Built-in Fade Fallback

```csharp
public class BuiltInFadeController
{
    // Sequence: fade alpha 0→1 (0.3s), wait for activation, fade 1→0 (0.3s)
    // Self-disables when ILoadingTransitionRegistrar detects external registration
}
```

- `CanvasGroup` created at runtime on a UI GameObject
- Triggered when `SceneLoadStarted` is published and no Loading/Transition System is wired
- Registration detection: check if any `ILoadingTransitionProvider` is registered in DI at startup
- Fade to black before `allowSceneActivation = true`, fade in after `SceneLoadComplete`

## Acceptance Criteria

1. **GIVEN** `AsyncOperation.progress` reaches 0.9, **WHEN** the async op is running, **THEN** `SceneReadyToActivate(sceneName)` is published and `allowSceneActivation` remains `false`.
2. **GIVEN** `SceneReadyToActivate` has been published, **WHEN** `ActivateScene()` is called, **THEN** `allowSceneActivation` is set to `true` and the scene activates within one frame.
3. **GIVEN** `SceneReadyToActivate` has been published, **WHEN** 10 seconds elapse without `ActivateScene()` being called, **THEN** Scene Manager auto-activates and logs a warning.
4. **GIVEN** a scene load completes with `allowSceneActivation = true`, **WHEN** the async op reaches `isDone`, **THEN** `SceneLoadComplete(loadedSceneName)` is published to the Event Bus.
5. **GIVEN** `SceneLoadStarted` is published, **WHEN** Loading/Transition System is not wired up, **THEN** Scene Manager's built-in fade fallback activates (fade to black before `allowSceneActivation = true`, fade in after `SceneLoadComplete`).

## QA Test Cases

- **AC1 (Ready at 0.9)**: Mock AsyncOperation.progress = 0.9. Verify SceneReadyToActivate published, allowSceneActivation stays false.
- **AC2 (ActivateScene)**: After SceneReadyToActivate, call ActivateScene(). Verify allowSceneActivation = true, scene activates within 1 frame.
- **AC3 (10s timeout)**: Publish SceneReadyToActivate. Wait 10s. Verify auto-activate and Warning log.
- **AC4 (Load complete)**: Set allowSceneActivation = true, AsyncOperation.isDone = true. Verify SceneLoadComplete published.
- **AC5 (Fade fallback)**: Publish SceneLoadStarted with no ILoadingTransitionProvider registered. Verify CanvasGroup.alpha reaches 1f within 3 frames after SceneLoadStarted, and returns to 0f within 3 frames after SceneLoadComplete.

**Edge cases**: Timeout cancelled when ActivateScene called before 10s, multiple loads start/stop fading.

## Test Evidence Path

- `Assets/_TinyRift/Tests/EditMode/SceneManager/SceneManagerActivationTests.cs`
- All 5 acceptance criteria as individual test methods
- Mock async operation, mock Event Bus for lifecycle events

## Dependencies

- **Scene Story 002** — Error Handling & Safety (ensures load is valid before activation)

## Unlocks

- Scene Story 004: Preloading & Edge Cases

## Risks

- **MEDIUM**: Built-in fade fallback may conflict with Loading/Transition System if registration detection fails. Mitigation: explicit registration API checked at startup, fallback disabled when provider found.

## Completion Notes
**Completed**: 2026-06-04
**Criteria**: 5/5 passing
**Deviations**: ADVISORY — IFadeController interface added during code review (ADR DRIFT resolution). _bufferedScenePath removed (dead code). DestroyImmediate guarded. All accepted.
**Test Evidence**: Logic: `Assets/_TinyRift/Tests/EditMode/SceneManager/SceneManagerActivationTests.cs` — 6 tests, all pass
**Code Review**: Complete — APPROVED WITH SUGGESTIONS (fixes applied and verified)
**Gates**: QL-TEST-COVERAGE: ADEQUATE. LP-CODE-REVIEW: APPROVED.
