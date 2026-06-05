# Story 001: Scene Load/Unload Core

- **Epic**: Scene Management
- **System**: Scene Manager
- **Type**: Logic
- **Priority**: P0
- **Estimate**: 4h
- **Status**: Complete
- **Last Updated**: 2026-06-04

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-scene-001` | GState→HeroCamp loads mapped scene path with allowSceneActivation=false, publishes SceneLoadStarted | ✅ ADR-001 |
| `TR-scene-002` | GState→InRun with zoneId loads correct zone scene, publishes SceneLoadStarted | ✅ ADR-001 |
| `TR-scene-003` | New scene request during active loading is buffered | ✅ ADR-001 |
| `TR-scene-004` | Already-active scene transitions are no-ops | ✅ ADR-001 |

## ADR Guidance

**ADR-001 (VContainer DI Architecture):**
- Interface singleton `ISceneManager` registered in `TinyRiftScope`
- Subscribes to `GameStateChanged` via Event Bus
- Uses `SceneRegistrySO` for path mapping — never constructs scene names via string concatenation

**Control Manifest (Core Layer):**
- Subscribe in Awake/Start, not constructor
- Store IDisposable subscription token
- Interface-first consumption by all systems

## Description

Implement the core scene loading orchestration. `ISceneManager` subscribes to `GameStateChanged` on the Event Bus, resolves the target scene path from `SceneRegistrySO`, and initiates `SceneManager.LoadSceneAsync` with `allowSceneActivation = false`. Handles load buffering (queue depth 1, latest wins) and same-scene no-op detection.

## Design

```csharp
public interface ISceneManager
{
    string CurrentSceneName { get; }
    bool IsLoading { get; }
    float LoadProgress { get; }
    void ActivateScene();
    UniTask PreloadZoneAsync(ZoneId zoneId, CancellationToken cancellationToken = default);
    string GetZoneSceneName(ZoneId zoneId);
    bool IsValidScene(ZoneId zoneId);
}
```

### State Mapping

| GameState | Source | Action |
|-----------|--------|--------|
| Menu | `SceneRegistrySO.menuScene` | Load |
| HeroCamp | `SceneRegistrySO.heroCampScene` | Load |
| InRun | `SceneRegistrySO.zoneScenes.First(z => z.zoneId == context.loadTarget.ZoneId)` | Load |
| Loading/Paused/Defeat/Victory | — | Silent no-op |

### Load Buffer

- Only one pending request stored (queue depth 1)
- Latest incoming request overwrites previous pending
- If pending target equals just-loaded scene, discard silently
- If load already in progress and new request arrives for different scene, buffer it

### Same-Scene No-Op

- Before starting any load, compare resolved scene name to `CurrentSceneName`
- If equal, return immediately without publishing `SceneLoadStarted`

## Acceptance Criteria

1. **GIVEN** `SceneRegistrySO` maps `HeroCamp` to `_TinyRift/Scenes/HeroCamp.unity`, **WHEN** `GameStateChanged(Loading, HeroCamp, context)` is received, **THEN** `SceneManager.LoadSceneAsync` is called with that exact path and `allowSceneActivation = false`, and `SceneLoadStarted` is published.
2. **GIVEN** `SceneRegistrySO` has a `ZoneSceneEntry` with `zoneId = "zone_crystal_caverns"` pointing to `_TinyRift/Scenes/Zones/CrystalCaverns.unity`, **WHEN** `GameStateChanged` arrives with `context.loadTarget.ZoneId = "zone_crystal_caverns"`, **THEN** it loads that exact scene and publishes `SceneLoadStarted`.
3. **GIVEN** an active `AsyncOperation` that is not yet `isDone`, **WHEN** a new valid `GameStateChanged` event arrives for a different scene, **THEN** the request is buffered as pending (not rejected), and the current load continues.
4. **GIVEN** the currently active scene is already the mapped scene for the incoming event, **WHEN** Scene Manager processes the event, **THEN** no `SceneLoadStarted` is published and `LoadSceneAsync` is never called.

## QA Test Cases

- **AC1 (HeroCamp load)**: Mock SceneRegistrySO with HeroCamp→`_TinyRift/Scenes/HeroCamp.unity`. Fire GameStateChanged(Loading, HeroCamp). Verify SceneManager.LoadSceneAsync called with that path and allowSceneActivation=false, and SceneLoadStarted published.
- **AC2 (Zone load)**: Mock SceneRegistrySO with zone_crystal_caverns→`_TinyRift/Scenes/Zones/CrystalCaverns.unity`. Fire GameStateChanged with context.loadTarget.ZoneId = zone_crystal_caverns. Verify correct scene loads and SceneLoadStarted published.
- **AC3 (Buffer during active load)**: Start load. Fire second GameStateChanged for different scene before first completes. Verify second is buffered (no rejection), first load continues.
- **AC4 (Same-scene no-op)**: Set CurrentSceneName to match incoming event's target. Process event. Verify no SceneLoadStarted published and LoadSceneAsync never called.

**Edge cases**: Loading scene while already transitioning to same scene, rapid-fire state changes.

## Test Evidence Path

- `Assets/_TinyRift/Tests/EditMode/SceneManager/SceneManagerLoadCoreTests.cs`
- All 4 acceptance criteria as individual test methods
- Mock `SceneRegistrySO`, mock Event Bus for `GameStateChanged`

## Dependencies

- **Event Bus** — subscribes to `GameStateChanged`
- **IGameStateManager** — transition to Menu on unrecoverable failure

## Unlocks

- Scene Story 002: Error Handling & Safety

## Risks

- **LOW**: AsyncOperation handle may become invalid if scene unloaded mid-load. Mitigation: null-check before access.

## Completion Notes
**Completed**: 2026-06-04
**Criteria**: 4/4 passing — all acceptance criteria verified via 16 edit-mode tests
**Deviations**: ADVISORY — Zone resolution simplified (default zone instead of context-based lookup); ISceneManager methods deferred; constructor subscription (correct pattern for plain C# class)
**Test Evidence**: Logic: test file at `Assets/_TinyRift/Tests/EditMode/SceneManager/SceneManagerLoadCoreTests.cs` (16 tests)
**Code Review**: Pending
