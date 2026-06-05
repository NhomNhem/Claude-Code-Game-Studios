# Scene Manager

> **Status**: Revised (pending re-review)
> **Author**: game-designer + technical-director
> **Last Updated**: 2026-05-26 (revised per design review)
> **Implements Pillar**: P3 (Snappy Sessions)

## Overview

The Scene Manager owns the mapping between `GameState` transitions and Unity scene lifecycle. It receives `GameStateChanged` events from the Event Bus, determines which scene to load based on the target state (and optional `context.loadTarget` for zone-specific combat scenes), and orchestrates async scene loading via `SceneManager.LoadSceneAsync`. It provides loading progress to the Loading/Transition System for visual transitions, handles preload and unload lifecycle for zone scenes, and rejects invalid loading requests (double-loads, missing scenes). The template's `LoadingManager` handles the loading screen UI; Scene Manager is the authoritative source of what scene to load and when.

## Player Fantasy

The player never interacts with the Scene Manager directly. They experience it as seamless scene transitions: menus to camp, camp to combat arenas, combat arenas back to camp — with no glitches, dead-ends, or loading hangs. Visual transition effects (ink-stamp, parchment-tear, fade) are owned by the Loading/Transition System; Scene Manager provides the loading infrastructure and activation timing that prevents jarring cuts. The Scene Manager is the invisible logistics layer ensuring the right scene is loaded at the right time.

## Detailed Design

### Core Rules

1. **GState-driven** — Scene Manager subscribes to `GameStateChanged(State previous, State current, GameStateContext context)` on the Event Bus. On each event, it maps `current` to a scene name via the Scene Registry and initiates loading. It does not initiate loads outside of a GState transition.

2. **Scene Registry** — A `SceneRegistryScriptableObject` asset defines every scene the Scene Manager can load. Each entry maps a `GameState` (or `ZoneId` for combat scenes) to a scene name (matching a scene in Build Settings). The registry is the single source of truth — Scene Manager never constructs scene names via string concatenation or convention.

3. **Load mode** — All scene loads use `LoadSceneMode.Single`. The game never requires additive scene loading within a state (HeroCamp and combat zones are mutually exclusive environments). Async operations start with `allowSceneActivation = false` so Scene Manager controls activation timing and prevents black frames during transitions. Loading screen overlays are owned by the Loading/Transition System, not Scene Manager.

4. **Progress reporting** — Scene Manager exposes the current load operation progress (`0.0–0.9` during async load, then 1.0 after activation) for the Loading/Transition System to consume. The minimum loading time (e.g., 0.5s display) is enforced by Loading/Transition, not Scene Manager. Progress beyond 1.0 is not possible since `allowSceneActivation = false` caps the async op at 0.9.

5. **Scene lifecycle** — Scene Manager tracks the currently-loaded scene name and any pending load request. It will not re-load a scene that is already active (detects same-scene request and returns success immediately). If a load is in progress and a new request arrives for a different scene, it buffers one pending request (queue depth of 1, latest wins). When the current load completes, the pending request fires immediately. If the pending target equals the just-loaded scene, the pending request is discarded (silent no-op).

6. **Zone scenes** — When GState transitions `Loading → InRun` and `context.loadTarget` contains a `ZoneId`, Scene Manager looks up the zone's scene in the Scene Registry. If `context.loadTarget` is empty or invalid, it falls back to a default zone scene (if one is defined) or rejects the load.

7. **Error handling** — If a requested scene is not found in the registry or is not in Build Settings, Scene Manager logs an error, fires `SceneLoadFailed(SceneId, reason)` on the Event Bus, and returns to `Menu` state via GState. The game must never hang on a failed load with no recovery path.

8. **Template compatibility** — Scene Manager operates alongside the template's `GameManager` singleton. GameManager manages the Login → Home (main menu) flow for auth. Scene Manager manages all `_TinyRift` scene transitions (Menu, HeroCamp, ZoneScenes). The two do not interfere — Scene Manager only loads scenes defined in its own registry.

9. **Preload support** — Scene Manager exposes `PreloadZoneAsync(ZoneId)` for background asset preloading before the transition visual begins (e.g., while the ink-stamp title card plays). Preload is optional — zones can load normally if preload is not requested.

10. **Scene identity** — Zones are identified by `ZoneId` (a string key like `"zone_crystal_caverns"`), not by numeric ID or scene index. ZoneId maps to scene name through the Scene Registry. This decouples zone ordering from load logic.

11. **Activation handshake** — When `SceneManager.LoadSceneAsync` reaches 0.9 (ready to activate), Scene Manager publishes `SceneReadyToActivate(sceneName)` to the Event Bus. Loading/Transition System completes its visual sequence, then calls `SceneManager.ActivateScene()`. Scene Manager sets `allowSceneActivation = true` on the async op. This handshake prevents a black frame between old scene destruction and new scene display. If `ActivateScene()` is not called within 10 seconds, Scene Manager auto-activates as a safety timeout.

12. **Loading/Transition fallback** — Scene Manager includes a minimal built-in transition (a `CanvasGroup`-based fade to black) that it activates when Loading/Transition System (#35) is not wired up. The fallback fades to black, waits for scene activation, then fades in. This ensures no raw scene swap is ever visible, even during early implementation before #35 exists. The fallback self-disables when Loading/Transition registers itself (via a registration API or presence detection at startup).

13. **Unmapped states produce no scene action** — The following `GameState` values have no corresponding scene to load: `Loading`, `Paused`, `Victory`, `Defeat`. When Scene Manager receives `GameStateChanged` targeting one of these, it is a silent no-op (no log, no event, no scene operation). The current scene remains loaded. These states are managed as UI overlays by their respective owning systems (Run Completion for Defeat/Victory, Pause Menu for Paused). Scene Manager only loads scenes for `Menu`, `HeroCamp`, and `InRun` (zone).

### Scene Registry

**Registry schema (ScriptableObject):**

```csharp
[CreateAssetMenu(menuName = "TinyRift/Scene Registry")]
public class SceneRegistrySO : ScriptableObject
{
    public SceneEntry menuScene;           // GameState.Menu
    public SceneEntry heroCampScene;       // GameState.HeroCamp
    public List<ZoneSceneEntry> zoneScenes; // each entry has ZoneId + SceneEntry
}

[System.Serializable]
public struct ZoneSceneEntry
{
    public string zoneId;            // matches ZoneId used by Zone Definition System
    public SceneEntry sceneEntry;
}
```

**SceneEntry schema:**
```csharp
[System.Serializable]
public struct SceneEntry
{
    public string sceneName;        // matches Build Settings name
    public string displayName;      // player-facing (e.g., "Crystal Caverns")
    public bool preloadAssets;      // hint to preload system
    public bool validateInBuildSettings; // if true, OnValidate warns when scene absent from Build Settings
}
```

**Default registry mapping:**

| GameState | Scene | Action | Notes |
|-----------|-------|--------|-------|
| Menu | `_TinyRift/Scenes/Menu` | Load | Main menu (title, options) |
| HeroCamp | `_TinyRift/Scenes/HeroCamp` | Load | Between-run hub |
| InRun (Zone) | `_TinyRift/Scenes/Zones/{zoneId}` | Load | Per-zone scene, resolved via ZoneId |
| Loading | — | No-op | Intermediate state; zone/camp load happens on next transition |
| Paused | — | No-op | Scene stays as-is; overlay owned by Pause Menu |
| Defeat | — | No-op | Zone scene stays loaded; overlay owned by Run Completion |
| Victory | — | No-op | Zone scene stays loaded; overlay owned by Run Completion |

Defeat and Victory overlays are shown on top of the zone scene. Run Completion system owns the lifecycle for post-run moments. The zone scene remains loaded until the next scene transition (player clicks "Continue" or "Quit to Menu").

**ZoneId → scene mapping (MVP):**

| ZoneId | Scene Name | Notes |
|--------|-----------|-------|
| `zone_fractured_pass` | `_TinyRift/Scenes/Zones/FracturedPass` | First zone, easy |
| `zone_crystal_caverns` | `_TinyRift/Scenes/Zones/CrystalCaverns` | Second zone, medium |
| `zone_ash_circle` | `_TinyRift/Scenes/Zones/AshCircle` | Third zone, hard |

### Loading Flow

```
┌─────────────────────────────────────────────────┐
│ GState transition triggers GameStateChanged      │
│ SceneManager receives event                      │
│ Valid states: Menu, HeroCamp, InRun              │
│ Loading/Paused/Defeat/Victory → silent no-op     │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
           Look up target scene in SceneRegistry
   - Menu     → lookup "menuScene"
   - HeroCamp → lookup "heroCampScene"
   - InRun    → lookup zoneScenes first match zoneId == context.loadTarget.ZoneId
                     │
                     ▼
          Is scene already the active scene?
             ──yes──→ Return success (no-op)
             │ no
                     ▼
          Is a load already in progress?
             ──yes──→ Buffer as pending (queue depth 1, latest wins)
                       When current complete, immediately fire pending
             │ no
                     ▼
Start SceneManager.LoadSceneAsync(sceneName, LoadSceneMode.Single)
  with allowSceneActivation = false
                     │
                     ▼
Publish SceneLoadStarted(sceneName) to Event Bus
  → Loading/Transition System begins visual transition
  → (or SceneManager's built-in fade fallback if Loading/Transition absent)
                     │
                     ▼
While loading: expose progress (0.0–0.9, capped by allowSceneActivation)
                     │
                     ▼
       AsyncOperation.progress reaches 0.9 (ready to activate)
                     │
                     ▼
Publish SceneReadyToActivate(sceneName) to Event Bus
  → Loading/Transition System completes its visual
  → (or built-in fade-to-black completes)
  10s safety timeout starts
                     │
                     ▼
   Loading/Transition calls SceneManager.ActivateScene()
   OR auto-activate fires at 10s timeout
                     │
                     ▼
SceneManager sets allowSceneActivation = true
  Old scene destroyed, new scene activated
                     │
                     ▼
Publish SceneLoadComplete(sceneName) to Event Bus
  → Loading/Transition System finishes (fade-in, reveal new scene)
  → (or built-in fade-in)
```

### API

```csharp
public interface ISceneManager
{
    // State
    string CurrentSceneName { get; }
    bool IsLoading { get; }
    float LoadProgress { get; }          // 0.0–0.9 during loading (capped by allowSceneActivation)

    // Events (Event Bus)
    // Listens: GameStateChanged → auto-load for Menu, HeroCamp, InRun
    // Publishes: SceneLoadStarted, SceneReadyToActivate, SceneLoadComplete, SceneLoadFailed

    // Activation handshake (called by Loading/Transition System)
    void ActivateScene();

    // Manual preload (optional)
    UniTask PreloadZoneAsync(ZoneId zoneId, CancellationToken cancellationToken = default);

    // Query
    string GetZoneSceneName(ZoneId zoneId);
    bool IsValidScene(ZoneId zoneId);     // is in registry + build settings
}
```

## Formulas

None. Scene Manager performs no calculations — all behavior is lookup-driven (GameState → scene name mapping, ZoneId → scene name mapping).

## Edge Cases

- **If `GameStateChanged(Menu → Loading)` arrives while already loading**: The new request is buffered as pending (queue depth 1, latest wins). When the current load completes, the pending fires immediately. If the pending target equals the just-loaded scene, it is discarded silently.

- **If the target scene is already the active scene** (e.g., GState fires HeroCamp→HeroCamp due to double-init): Silent no-op. No load occurs. Return success. Pending queue is not affected.

- **If `GameStateChanged` targets `Loading`, `Paused`, `Defeat`, or `Victory`**: Silent no-op (Rule 13). Scene Manager takes no action regardless of loading state. Pending queue is preserved.

- **If `GameStateChanged` targets `Menu` or `HeroCamp` while a zone preload is active**: The preload is cancelled (its `CancellationToken` is triggered). Scene Manager starts the scene load immediately. Preloaded assets are released on scene destruction per Unity's normal lifecycle.

- **If `context.loadTarget.ZoneId` is missing or invalid during transition to InRun**: Log error. Fall back to a default zone scene if one is defined in the registry. If no default exists, reject the transition (return false to GState) and log a critical error.

- **If the scene name in the registry does not exist in Build Settings**: `SceneManager.LoadSceneAsync` throws. Scene Manager catches the exception, publishes `SceneLoadFailed`, increments a session failure counter, and calls `GState.TransitionTo(Menu)` for recovery. If 5 consecutive failures occur in one session, Scene Manager halts all loading and logs a fatal error (prevents infinite recovery loop if Menu scene itself is broken).

- **If the game is closed mid-load**: Unity aborts all async operations. The async op handle becomes invalid — Scene Manager's coroutine/async method detects this via the `Application.quitting` event or a null check. No cleanup needed — next launch starts fresh.

- **If `ActivateScene()` is never called after `SceneReadyToActivate`** (Loading/Transition hangs): The 10-second safety timeout fires, Scene Manager auto-activates, and logs a warning. The game continues with no visible effect (the scene swap happens slightly later than intended).

- **If a zone scene is unloaded and then re-loaded immediately** (player dies, returns to camp, immediately starts a new run): Normal single load. The `LoadSceneMode.Single` replacement handles unload of the zone and load of HeroCamp, then the next run loads the zone again.

- **If Scene Manager receives `GameStateChanged` before it is initialized** (race condition during app startup): Scene Manager subscribes in `Start()` or `OnEnable()`. If an event arrives before subscription, the Event Bus handles null subscribers gracefully.

- **If the template's `LoadingManager` conflicts with Scene Manager loads**: Template's LoadingManager only activates for loads initiated by template code (Login → Home). Scene Manager loads skip the template's LoadingManager and use a _TinyRift loading flow. Both can coexist without conflict.

- **If the `SceneRegistrySO` asset is null or fails to deserialize**: Scene Manager logs a fatal error at initialization and enters a safe disabled state — it does not subscribe to `GameStateChanged` events and does not load any scene. The game must handle this gracefully (e.g., display an error screen from BootstrapRunner).

- **If a zone scene encounters a critical error mid-load** (asset bundle corruption, disk I/O failure): `SceneLoadFailed` publishes the error context. Recovery path: transition to Menu. Player can re-attempt. The failure should be logged server-side via Network Manager for telemetry.

## Dependencies

**Upstream (this system depends on these):**
| System | Type | Interface |
|--------|------|-----------|
| Event Bus | Hard | Subscribes to `GameStateChanged` |
| Game State Manager | Hard | Receives state transitions; calls `GState.TransitionTo(Menu)` on unrecoverable load failure |

**Downstream (systems that depend on this one):**
| System | Type | Interface |
|--------|------|-----------|
| Loading/Transition System | Hard | Reads `LoadProgress`, shows visual overlay during load |
| Zone Definition System | Soft | Provides `ZoneId` → scene name mapping (via registry) |
| Run Completion | Soft | May read `CurrentSceneName` for result scene context |

*Hard = system cannot function without this. Soft = enhanced by this but works without it.*

## Tuning Knobs

| Knob | Default | Range | Effect When Max | Effect When Min | Owner |
|------|---------|-------|-----------------|-----------------|-------|
| Default zone fallback | `zone_fractured_pass` | any valid ZoneId | All fallback loads go to the hardest zone | All fallback loads go to fracturing pass | Scene Manager |
| Preload budget | 150 MB | 0–500 MB | More assets preloaded in background, smoother zone entry | No preloading, potentially longer load screens | Scene Manager + Asset Management |
| Activation safety timeout | 10 s | 1–30 s | Longer wait before auto-activate | Shorter wait, less tolerance for slow transitions | Scene Manager |
| Max consecutive load failures | 5 | 1–10 | More retries before fatal halt | Fewer retries, faster failure escalation | Scene Manager |

No other tuning knobs. Scene-to-state mapping is a design-time decision in the registry asset, not a runtime knob.

## Visual/Audio Requirements

Scene Manager has minimal built-in visual output when the Loading/Transition System is not yet available. It publishes scene lifecycle events that other systems (or its own fallback) consume:

| Event | Consumer | Response |
|-------|----------|----------|
| `SceneLoadStarted` | Loading/Transition System | Begin visual transition (ink-stamp, parchment-tear, fade) |
| `SceneReadyToActivate` | Loading/Transition System | Complete visual pre-activation (e.g., fade to black), then call `SceneManager.ActivateScene()` |
| `SceneLoadComplete` | Loading/Transition System | End visual transition, fade in to reveal new scene |
| `SceneLoadFailed` | Loading/Transition, GState | Show error screen, return to menu |

The Loading/Transition System (system #35) owns all visual/animation work for transitions. The art bible (Section 6.3) defines the transition style: ink-stamp for navigation, parchment-tear for zone entry, rune-ignite for boss transitions.

**Built-in fallback**: If Loading/Transition is not wired up (early implementation gap), Scene Manager activates a minimal `CanvasGroup`-based fade controller. Sequence: fade canvas alpha 0→1 (0.3s), wait for scene load + activation, fade 1→0 (0.3s). The fallback self-disables when Loading/Transition registers itself via an `ILoadingTransitionRegistrar` API or startup presence check.

## UI Requirements

Scene Manager has no UI. It provides the scene-loading infrastructure that UI screens are loaded into:

| Screen | Scene | Responsibility |
|--------|-------|---------------|
| Title Menu | `_TinyRift/Scenes/Menu` | Player can start, quit, settings |
| Hero Camp | `_TinyRift/Scenes/HeroCamp` | Camp Menu UI, NPCs, lore codex |
| Combat Zone | `_TinyRift/Scenes/Zones/{zoneId}` | HUD, combat arena, boss arena |
| Loading Screen | (overlay, owned by Loading/Transition) | Transition animations |

The Scene Manager loads these scenes; the UI layer activates within them.

## Acceptance Criteria

- **GIVEN** `SceneRegistry` maps `HeroCamp` to scene path `_TinyRift/Scenes/HeroCamp.unity`, **WHEN** Scene Manager receives `GameStateChanged(Loading, HeroCamp, context)`, **THEN** `SceneManager.LoadSceneAsync` is called with that exact path and `allowSceneActivation = false`, and `SceneLoadStarted` is published.
- **GIVEN** `SceneRegistry` has a `ZoneSceneEntry` with `zoneId = "zone_crystal_caverns"` pointing to `_TinyRift/Scenes/Zones/CrystalCaverns.unity`, **WHEN** Scene Manager receives `GameStateChanged` with `context.loadTarget.ZoneId = "zone_crystal_caverns"`, **THEN** it loads that exact scene and publishes `SceneLoadStarted`.
- **GIVEN** Scene Manager has an active `AsyncOperation` that is not yet `isDone`, **WHEN** a new valid `GameStateChanged` event arrives for a different scene, **THEN** the request is buffered as pending (not rejected), and the current load continues.
- **GIVEN** the currently active scene is already the scene mapped to the incoming `GameStateChanged` event, **WHEN** Scene Manager processes the event, **THEN** no `SceneLoadStarted` event is published and `LoadSceneAsync` is never called.
- **GIVEN** `context.loadTarget.ZoneId` is null or empty during transition to `InRun`, **WHEN** Scene Manager processes the event, **THEN** it uses `SceneRegistry.GetDefaultZoneScene()` and logs a `Warning` containing `"ZoneId empty, using default"`.
- **GIVEN** the scene path resolved from `SceneRegistry` is not present in `EditorBuildSettings.scenes`, **WHEN** `LoadSceneAsync` throws, **THEN** Scene Manager publishes `SceneLoadFailed(scenePath, exception)`, increments session failure counter, and calls `GState.TransitionTo(Menu)`.
- **GIVEN** `SceneLoadFailed` fires 5 consecutive times in a single session, **WHEN** the 5th failure occurs, **THEN** Scene Manager halts all loading and logs a fatal error (no further `TransitionTo` calls).
- **GIVEN** `AsyncOperation.progress` reaches 0.9, **WHEN** the async op is running, **THEN** `SceneReadyToActivate(sceneName)` is published and `allowSceneActivation` remains `false`.
- **GIVEN** `SceneReadyToActivate` has been published, **WHEN** `ActivateScene()` is called, **THEN** `allowSceneActivation` is set to `true` and the scene activates within one frame.
- **GIVEN** `SceneReadyToActivate` has been published, **WHEN** 10 seconds elapse without `ActivateScene()` being called, **THEN** Scene Manager auto-activates and logs a warning.
- **GIVEN** a scene load completes with `allowSceneActivation = true`, **WHEN** the async op reaches `isDone`, **THEN** `SceneLoadComplete(loadedSceneName)` is published to the Event Bus.
- **GIVEN** `GameStateChanged` with target `Loading`, `Paused`, `Defeat`, or `Victory` is received, **WHEN** Scene Manager processes the event, **THEN** no scene load is initiated and no event is published (silent no-op).
- **GIVEN** `SceneLoadStarted` is published, **WHEN** Loading/Transition System is not wired up, **THEN** Scene Manager's built-in fade fallback activates (fade to black before `allowSceneActivation = true`, fade in after `SceneLoadComplete`).
- **GIVEN** the `SceneRegistrySO` asset reference is null at initialization, **WHEN** Scene Manager starts, **THEN** it logs a fatal error and does not subscribe to `GameStateChanged` (safe disabled state).
- **GIVEN** `PreloadZoneAsync(zoneId)` is called and a `GameStateChanged` event arrives for a different scene before preload completes, **WHEN** Scene Manager processes the event, **THEN** the preload `CancellationToken` is triggered and the load proceeds normally.
