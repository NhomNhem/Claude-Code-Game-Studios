# Game State Manager

> **Status**: In Design
> **Author**: game-designer + technical-director
> **Last Updated**: 2026-05-26
> **Implements Pillar**: P3 (Snappy Sessions)

## Overview

The Game State Manager is a lightweight finite state machine that governs the game's top-level phase transitions. It maintains a single active state at any time (`Menu`, `Loading`, `InRun`, `BossFight`, `Paused`, `Victory`, `Defeat`, `HeroCamp`) and publishes state-change events via the Event Bus so downstream systems can react without coupling to each other. It owns no per-entity data and accumulates no state history — it is a pure phase tracker. The game would lose all phase coordination without it: scene transitions, pause behavior, enemy AI activation, HUD visibility, and input processing all depend on knowing the current game phase.

## Player Fantasy

The Game State Manager has no direct player fantasy — players never interact with it consciously. What they feel is the absence of friction: scene transitions that don't glitch, pause that works instantly, menus that disable combat input cleanly. The game state machine is the invisible stagehand.

## Detailed Design

### Core Rules

1. Only one state is active at any time. State is represented by a `GameState` enum.
2. State transitions are instantaneous — GState changes immediately; visual transitions (fade, ink-stamp, parchment-tear) are owned by the Loading/Transition System.
3. On every state change, GState publishes `GameStateChanged(State previous, State current, GameStateContext context)` to the Event Bus. `context` is optional and carries extra data (e.g., `reason: "quit"`, `loadTarget: SceneId`).
4. `InRun` has a sub-state flag `bossActive: bool`. When `bossActive = true`, systems may behave differently (e.g., boss health bar shown, arena music, no new wave spawns). The sub-state flag is read-only to subscribers — only GState sets it.
5. `Paused` tracks its origin state (`InRun` or `HeroCamp`) so `Unpause()` resumes correctly.
6. `Loading` is a transitional state. The Loading/Transition System owns scene-load callbacks and calls `GState.TransitionTo(target)` when loading completes.
7. GState owns no per-entity data, no history stack, no timers, and no entity references. It stores only: `currentState`, `previousState`, `pauseOrigin`, `bossActive`. Time scale management is delegated to the Time System via `GameStateChanged` events.
9. Invalid transitions are silently rejected (log at Debug level, return `false` from `TransitionTo`).
10. Transition to the current state is a silent no-op (log at Debug level).
11. GState is a singleton registered via VContainer in TinyRiftScope. Systems access it via interface `IGameStateManager`.

### States and Transitions

**Enum definition:**
```csharp
public enum GameState
{
    Menu,
    Loading,
    HeroCamp,
    InRun,
    Paused,
    Victory,
    Defeat
}
```

**Transition matrix** (rows = from, columns = to, ✓ = allowed):

| From → To | Menu | Loading | HeroCamp | InRun | Paused | Victory | Defeat |
|-----------|------|---------|----------|-------|--------|---------|--------|
| Menu | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Loading | ✗ | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ |
| HeroCamp | ✓ | ✓ | ✗ | ✗ | ✓ | ✗ | ✗ |
| InRun | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✓ |
| Paused | ✗ | ✗ | ✓ | ✓* | ✗ | ✗ | ✗ |
| Victory | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| Defeat | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |

*\*Paused → InRun resumes with `bossActive` flag preserved from origin.*

**Allowed transition flows:**

```
Menu → Loading → HeroCamp          (startup)
HeroCamp → Loading → InRun          (start run)
InRun → Paused → InRun             (pause toggle during combat)
InRun → Paused → HeroCamp          (quit run from pause)
InRun → Defeat → Loading → HeroCamp (player death → reload camp)
HeroCamp → Paused → HeroCamp       (pause toggle in camp)
Defeat → Menu                      (back to title)
Victory → Menu                     (back to title)
Victory → Loading → HeroCamp       (return to camp after boss kill)
Defeat → Loading → HeroCamp        (return to camp after death)
```

**Transition trigger ownership:**

| Transition | Triggered By | Notes |
|-----------|-------------|-------|
| Menu → Loading | GameStateManager.Startup() | Called by BootstrapRunner on first frame |
| Loading → HeroCamp | Loading/Transition System | Scene load complete |
| Loading → InRun | Loading/Transition System | Scene load complete, with context carrying the ZoneDefinition |
| HeroCamp → Loading | Camp Menu UI start-run button | Context carries ZoneDefinition |
| HeroCamp → Menu | Camp Menu UI quit button | |
| InRun → Paused | Input System (Escape/Menu button) | Toggles |
| Paused → InRun | Input System (Escape/Menu button) | Toggles, resumes bossActive flag |
| Paused → HeroCamp | Pause Menu "Quit Run" button | Must clean up in-run state first |
| InRun → Defeat | Health System (player HP <= 0) | |
| Victory → HeroCamp | Run Completion summary "Continue" button | |
| Victory → Menu | Run Completion "Quit to Menu" button | |
| Defeat → HeroCamp | Run Completion "Continue" button | |
| Defeat → Menu | Run Completion "Quit to Menu" button | |
| HeroCamp → Paused | Input System (Escape/Menu button) | Toggles, pauseOrigin = HeroCamp |

### Interactions with Other Systems

| System | Interface | Direction | Data |
|--------|-----------|-----------|------|
| Event Bus | `IBus.Publish(GameStateChanged)` | GState → Event Bus | `previous`, `current`, `context` |
| Scene Manager | Subscribes to `GameStateChanged` → loads/unloads scenes | Event Bus → Scene Manager | `current` state maps to scene name. `context.loadTarget` for zone-specific loads. |
| Input System | Subscribes to `GameStateChanged` → enables/disables action maps | Event Bus → Input System | Menu → UI map, InRun → Gameplay map, Paused → UI map |
| Audio System | Subscribes to `GameStateChanged` → crossfade music, play SFX | Event Bus → Audio System | State maps to music track. Paused → duck. Victory → fanfare. Defeat → sting. |
| HUD | Subscribes to `GameStateChanged` → show/hide | Event Bus → HUD | InRun/BossFight → visible. Menu/HeroCamp/Paused → hidden. |
| Enemy AI | Reads `currentState` to determine active/inactive | GState → Enemy AI (poll) | `currentState != InRun` → AI disabled |
| Wave Spawning | Subscribes to `GameStateChanged.BossActive` | Event Bus → Wave Spawn | `bossActive = true` → stop regular wave spawning, enable boss encounter |
| Screen Shake | Checks `currentState` before applying shake | Screen Shake → GState (poll) | `currentState == Paused` → suppress shake |
| Pause Menu | Calls `GState.TransitionTo(Paused)` and `GState.TransitionTo(origin)` | Pause Menu → GState | Origin tracking for correct resume |
| Loading/Transition | Subscribes to `GameStateChanged` for visual triggers, calls `TransitionTo()` on load complete | Bidirectional | Loading → target state callback |
| Time System | Subscribes to `GameStateChanged` → manages `Time.timeScale` (pause, hit-stop, slow-mo preservation) | GState → Time (event) | Time System is the sole owner of `Time.timeScale`. GState removed timeScale management in cross-GDD review R1. |
| Analytics | Subscribes to `GameStateChanged` → log player journey events | Event Bus → Analytics | Every state transition is a funnel event |
| Save System | Subscribes to `GameStateChanged(HeroCamp)` and `(Defeat)` → autosave | Event Bus → Save System | `HeroCamp` entry = load. `Defeat` = autosave progression. |
| Run Manager | Subscribes to `GameStateChanged(previous: InRun, current: HeroCamp)` or `(Defeat)` → tear down run state | Event Bus → Run Manager | Cleanup of per-run systems (enemies, wave state, player temp stats, draft state). See also Run Completion system. |

## Formulas

None. Game State Manager is a pure state machine with no mathematical calculations. All behavior is governed by the state transition matrix defined in Section C.

## Edge Cases

- **If `TransitionTo(currentState)` is called**: Silent no-op. Log at Debug level. Return `true`.
- **If an invalid transition is requested (e.g., `Menu → InRun`)**: Log error. No state change. Return `false`. Caller must handle the failure.
- **If `Paused` toggle is triggered during `Loading`**: Ignored. `Loading` is not a pausable state.
- **If `Time.timeScale` was already 0 when entering `Paused`** (e.g., from a slow-mo power-up): Save current `Time.timeScale` as `previousTimeScale` on pause entry, restore on unpause. This preserves any external time-scale manipulation.
- **If `Defeat` and `Victory` arrive simultaneously** (boss dies on same frame as player): `Defeat` wins. Check `Defeat` trigger first in the frame processing order. (Implementation note: Health System resolves player damage before boss damage each frame.)
- **If two systems call `TransitionTo` on the same frame**: First call wins. Subsequent calls check `currentState` against requested — if the first call already changed state, the second sees a mismatch and returns `false`.
- **If `bossActive` flag is set when state is not `InRun`**: Silently ignored. Flag is only meaningful when `currentState == InRun`.
- **If a subscriber to `GameStateChanged` is not yet initialized** (race condition during scene load): Event Bus handles null subscribers gracefully (no-op). Systems must subscribe in their `Start()` or `OnEnable()`.
- **If Pause Menu calls `TransitionTo(HeroCamp)` while no run is active** (pauseOrigin was HeroCamp): Safe — the `Paused → HeroCamp` transition is valid regardless of origin. Run Manager checks if there is a run to tear down; if not, it's a no-op.
- **If the player triggers pause, then immediately quits to menu from pause**: Two sequential transitions: `InRun → Paused` (frame 1), then `Paused → Menu` (frame 2). Both valid. `previousTimeScale` restored on `Menu` entry.
- **If `Loading` takes longer than expected (e.g., timeout)**: Loading/Transition System owns the timeout logic, not GState. It may call `TransitionTo(HeroCamp)` with a fallback scene, or call `TransitionTo(Menu)` if loading is unrecoverable.
- **If the game window loses focus while in `InRun`**: Unity's `OnApplicationFocus(false)` handler calls `TransitionTo(Paused)` — auto-pause on focus loss.
- **If multiple `Loading` transitions are requested** (e.g., two systems both try to trigger a load): The first one creates a `Loading` state; subsequent calls check `currentState == Loading` and are rejected.

## Dependencies

**Upstream (this system depends on these)**: None. Game State Manager is a Foundation-layer system with zero upstream dependencies. It requires only the C# runtime and Unity engine lifecycle (`MonoBehaviour.Start`, `Update`).

**Downstream (systems that depend on this one)**:
| System | Type | Interface |
|--------|------|-----------|
| Scene Manager | Hard | Subscribes to `GameStateChanged` → loads/unloads scenes |
| Input System | Hard | Subscribes to `GameStateChanged` → enables/disables action maps |
| Audio System | Soft | Subscribes to `GameStateChanged` → music transitions |
| HUD | Hard | Subscribes to `GameStateChanged` → show/hide |
| Enemy AI | Hard | Polls `currentState` to determine active flag |
| Wave Spawning | Hard | Subscribes to `bossActive` flag changes |
| Screen Shake | Soft | Polls `currentState` to suppress during pause |
| Pause Menu | Hard | Calls `TransitionTo(Paused)` and `TransitionTo(origin)` |
| Loading/Transition | Hard | Calls `TransitionTo(target)` on load complete |
| Run Manager | Hard | Subscribes to `InRun → non-InRun` transitions for teardown |
| Save System | Soft | Subscribes to `HeroCamp` entry for autosave |
| Analytics | Soft | Subscribes to all state changes for funnel events |

*Hard = system cannot function without this. Soft = enhanced by this but works without it.*

## Tuning Knobs

| Knob | Default | Range | Effect When Max | Effect When Min | Owner |
|------|---------|-------|-----------------|-----------------|-------|
| Auto-pause on focus loss | Enabled | {Enabled, Disabled} | Game pauses when window loses focus | Game continues in background | Game State Manager |
| Pause menu allowed in HeroCamp | Enabled | {Enabled, Disabled} | Player can open pause menu in camp | Pause is restricted to in-run only | Game State Manager |

No other tuning knobs. State definitions, transitions, and trigger ownership are hard-coded design decisions (Section C) — changing them alters game flow architecture.

## Visual/Audio Requirements

Game State Manager itself has no visual or audio output. It triggers state-change events that other systems respond to:

| State Change | Expected Visual Response | Expected Audio Response | Owner |
|-------------|-------------------------|------------------------|-------|
| Menu → Loading | Ink-stamp title card (art bible Section 6.3) | Short horn blast | Loading/Transition, Audio |
| Loading → HeroCamp | Camp scene fade-in | Camp ambient starts | Loading/Transition, Audio |
| HeroCamp → Loading | Camp fade-out | Ambient crossfade | Loading/Transition, Audio |
| Loading → InRun | Zone entry title card + arena reveal | Combat track starts | Loading/Transition, Audio |
| InRun → BossFight | Boss warning UI, screen rim pulse (art bible Section 6.3) | Boss intro sting | HUD, Audio |
| InRun → Paused | Arena dims to 20%, motion blur, parchment panel slides down | Ink-pot lid clink | Pause Menu, Audio, VFX |
| Paused → InRun | Parchment panel slides up, arena brightness restores | Ink-pot lid clink | Pause Menu, Audio, VFX |
| Defeat triggered | Void vignette creeps in, parchment tear overlay (Section 6.3) | Single cello note | Screen Shake, Audio, VFX |
| Victory triggered | Gold-ink bloom, victory text stamp (Section 6.3) | Fanfare (4 notes) | HUD, Audio, VFX |

GState publishers the event; the above systems are responsible for the actual feedback.

## UI Requirements

Game State Manager has no direct UI. It provides the state information that UI systems use:

| UI Element | Reads From GState | Purpose |
|-----------|-------------------|---------|
| HUD | `currentState == InRun` | Visible only during InRun |
| Draft Panel | `currentState == InRun` (with level-up flag from Level-Up System) | Appears over HUD during draft |
| Pause Menu | `currentState == Paused` | Open during Paused state |
| Camp Menu | `currentState == HeroCamp` | Full camp interface |
| Victory Screen | `currentState == Victory` | End-of-run summary |
| Defeat Screen | `currentState == Defeat` | Death summary |
| Loading Screen | `currentState == Loading` | Loading progress |

The UI layer maps GState to active screen. No per-state UI is owned by GState itself.

## Open Questions

| Question | Options | Impact | Target Resolution |
|----------|---------|--------|-------------------|
| Should `HeroCamp` have a sub-state for draft/upgrade menus? | Separate sub-state vs. top-level overlay | Affects pause behavior in upgrade screens | After Camp Menu GDD |
| Should analytics events include duration-in-state? | Yes (each state-change carries previous state duration) vs. No (analytics queries time separately) | Adds ~2 bytes per event vs. cleaner separation | After Event Bus GDD |
| Who owns the `BossFight` flag state transition? | Boss Encounter System sets `bossActive = true` when boss spawns, Wave Spawning sets `false` when boss defeated | Determines which system has the authority to toggle the flag | During Boss Encounter GDD |

## Acceptance Criteria

- **GIVEN** the game just launched, **WHEN** GameStateManager.Startup() runs, **THEN** the current state is `Menu` and a `GameStateChanged(None, Menu)` event is published.
- **GIVEN** current state is `InRun`, **WHEN** the player presses Escape, **THEN** `TransitionTo(Paused)` succeeds and a `GameStateChanged(InRun, Paused)` event is published (Time System handles `Time.timeScale = 0` via its GState-aware rule).
- **GIVEN** current state is `Paused` with `pauseOrigin = InRun`, **WHEN** the player presses Escape, **THEN** `TransitionTo(InRun)` succeeds, `Time.timeScale` restores to its pre-pause value, and a `GameStateChanged(Paused, InRun)` event is published.
- **GIVEN** current state is `Paused`, **WHEN** `TransitionTo(Paused)` is called (double-pause), **THEN** the call is silently rejected (no state change, no event published).
- **GIVEN** current state is `Menu`, **WHEN** `TransitionTo(InRun)` is requested, **THEN** the call is rejected (returns `false`, no state change, error logged).
- **GIVEN** current state is `InRun` and `bossActive = true`, **WHEN** `TransitionTo(Paused)` is called, **THEN** the pause state preserves `bossActive` flag; on resume, `bossActive` remains `true`.
- **GIVEN** current state is `InRun`, **WHEN** `OnApplicationFocus(false)` fires, **THEN** `TransitionTo(Paused)` is called automatically.
- **GIVEN** current state is `Loading`, **WHEN** any system calls `TransitionTo(Paused)`, **THEN** the call is rejected (`Loading` is not pausable).
- **GIVEN** `Defeat` and `Victory` arrive on the same frame from different sources, **WHEN** the frame resolves, **THEN** the final state is `Defeat` (Defeat takes priority).
- **GIVEN** `Time.timeScale` was 0.5 before entering `Paused` (slow-mo active), **WHEN** the player pauses and unpauses via GState, **THEN** the Time System's `_prePauseTimeScale` preserves the 0.5 value (verified in Time System AC).
- **GIVEN** two systems call `TransitionTo` on the same frame, **WHEN** the first call succeeds, **THEN** the second call is rejected (returns `false`).
- **GIVEN** the game window has been running for 5 minutes across 3 sessions, **WHEN** state transitions are audited, **THEN** GState has leaked no memory (no accumulating history, no stale subscriptions, no orphaned event handlers).
