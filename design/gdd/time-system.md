# Time System

> **Status**: Designed (pending review)
> **Author**: user + agents
> **Last Updated**: 2026-05-26
> **Implements Pillar**: Pillar 3 — Snappy 20–30 Minute Sessions (timer, cooldowns, pause handling)

## Overview

The Time System provides a single source of truth for all time-related queries across the game. It wraps Unity's `Time` API and adds GState-aware time scale management, a run elapsed timer, and a cooldown tracking API. Its core responsibility is ensuring that every system (combat, UI, animations, audio) reads time from a unified source that respects pause state and time scale modifiers.

## Player Fantasy

The player never interacts with the Time System directly. They feel it as responsive gameplay: skills cool down at the expected rate, the run timer ticks up during combat and freezes on pause, hit-stop pauses the action for impactful moments, and everything resumes correctly after alt-tab or menu navigation.

## Detailed Design

### Core Rules

1. **Singleton service** — `TimeManager` is registered via VContainer in `TinyRiftScope` as `ITimeManager`. One instance per scene.
2. **GState-aware time scale (ownership)** — Subscribes to `GameStateChanged`. Time System is the sole owner of `Time.timeScale`:
   - On `Paused` entry: saves the current effective time scale as `_prePauseTimeScale`, then sets `Time.timeScale = 0f`.
   - On exit from `Paused` (to `InRun` or `HeroCamp`): restores `Time.timeScale = _prePauseTimeScale`.
   - `_prePauseTimeScale` captures the effective scale at the moment of pause, excluding transient hit-stop (scale=0). If hit-stop was active when pause was entered, records the pre-hit-stop scale instead of 0.
   - Does NOT modify unscaled time.
3. **Run elapsed timer** — Exposes `float RunElapsedTime` (scaled) and `float RunElapsedTimeUnscaled` (unscaled). Timer starts at `InRun` entry, resets to 0 on `InRun` exit. Incremented from `Time.deltaTime` / `Time.unscaledDeltaTime` in `Update()`.
4. **Cooldown registry** — `RegisterCooldown(string id, float duration)` and `bool IsReady(string id)` / `float GetRemaining(string id)`. Drives skill and status effect cooldowns. `duration` is in scaled seconds — respects time scale and pause.
5. **Pause-respecting cooldowns** — When `Time.timeScale == 0`, cooldown timers do NOT tick. This is automatic via `Time.deltaTime == 0`.
6. **Hit-stop support** — `TriggerHitStop(float duration, float scale = 0f)` sets `Time.timeScale = scale` for `duration` unscaled seconds, then restores to 1f. Used by Screen Shake and SkillPresentationAdapter.
7. **No per-entity state** — Cooldown registry is a flat dictionary of `string → float`. Entities manage their own cooldown IDs. No entity ownership in `TimeManager`.
8. **External time scale sync** — If `Time.timeScale` is modified externally, `TimeManager` detects the change in `Update()` and syncs its internal state, firing `OnTimeScaleChanged`.

### API Surface

```csharp
public interface ITimeManager
{
    float RunElapsedTime { get; }          // scaled (freezes on pause)
    float RunElapsedTimeUnscaled { get; }  // unscaled (runs through pause)
    float TimeScale { get; }               // current effective scale

    // Cooldown API
    void RegisterCooldown(string id, float duration);
    bool IsReady(string id);
    float GetRemaining(string id);          // seconds remaining (0 if ready)
    float GetProgress(string id);           // 0.0–1.0, 0 = ready/not registered
    void ResetCooldown(string id, float duration);  // overwrites existing
    void CancelCooldown(string id);

    // Hit-stop
    void TriggerHitStop(float duration, float timeScale = 0f);

    // Events
    event Action<float> OnTimeScaleChanged;   // new time scale
    event Action<float> OnRunTimerUpdated;    // current elapsed seconds
}
```

### Interactions with Other Systems

| System | Interface | Direction | Data |
|--------|-----------|-----------|------|
| Game State Manager | Subscribes to `GameStateChanged` | GState → Time | State enum → pause/unpause time scale |
| Orbit Combat | Calls `RegisterCooldown()`, `IsReady()` | Orbit → Time | Cooldown IDs per orbit slot |
| Burst Skill | Calls `RegisterCooldown()`, `IsReady()` | Burst → Time | Cooldown IDs per skill slot |
| Status Effect | Calls `RegisterCooldown()` for tick timers | Status → Time | Tick interval per effect |
| HUD | Reads `RunElapsedTime`, `GetProgress()` | Time → HUD | Elapsed seconds, cooldown progress (0–1) |
| Screen Shake | Calls `TriggerHitStop()` | Shake → Time | Hit-stop duration and scale |
| SkillPresentationAdapter | Calls `TriggerHitStop()` | Adapter → Time | Hit-stop on skill impact |

## Formulas

None. Time tracking and cooldown management are linear counters driven by `Time.deltaTime`. No multiplicative scaling formulas exist.

## Edge Cases

- **If `TriggerHitStop(0.1f)` is called while already in hit-stop**: The new hit-stop overwrites the remaining duration. Last call wins. A warning is logged.
- **If `RegisterCooldown(id, duration)` is called for an id with a running cooldown**: The existing cooldown is NOT overwritten. A warning is logged. Caller must use `ResetCooldown(id, duration)` to overwrite.
- **If `RunElapsedTime` is queried during Menu (before any run)**: Returns 0. Does not throw.
- **If game window loses focus during InRun**: GState auto-pauses. TimeManager receives `GameStateChanged(InRun, Paused)` and sets `Time.timeScale = 0`. No additional handling needed.
- **If a cooldown is registered with `duration = 0`**: Immediately ready (`IsReady` returns true). Valid for instant-use items or effects with no cooldown.
- **If `Time.timeScale` is modified externally**: TimeManager detects the change in `Update()` by comparing `Time.timeScale` against its last-known value. If different, it syncs internal state and fires `OnTimeScaleChanged`. It does NOT overwrite the external change — it syncs to it.
- **If a cooldown id is never registered and `IsReady()` is called**: Returns `true` (unregistered ids are treated as ready). No exception.
- **If `Paused` is entered during an active hit-stop** (Time.timeScale already 0 from `TriggerHitStop`): `_prePauseTimeScale` is set to the time scale that was active before hit-stop was triggered (not 0). The hit-stop duration continues to elapse in unscaled time. On unpause, if the hit-stop has already expired, the time scale restores to the pre-hit-stop value. If hit-stop is still active, it completes normally and restores to the pre-hit-stop scale.

## Dependencies

| System | Dependency | Direction | Notes |
|--------|-----------|-----------|-------|
| Game State Manager | Required | GState → Time | `GameStateChanged` events for pause/unpause |
| Unity Time API | Required | TimeManager → Engine | `Time.timeScale`, `Time.deltaTime`, `Time.unscaledDeltaTime` |
| VContainer | Required | Scope → Time | Registration in TinyRiftScope |
| All gameplay systems | Consumer | Time → Systems | Cooldowns, elapsed time, hit-stop |

## Tuning Knobs

| Knob | Type | Default | Range | Notes |
|------|------|---------|-------|-------|
| Hit-stop duration (min) | float | 0.05s | 0.0–0.5 | Minimum hit-stop on any damage |
| Hit-stop duration (elite) | float | 0.1s | 0.0–0.5 | Hit-stop on elite hit |
| Hit-stop duration (boss) | float | 0.15s | 0.0–0.5 | Hit-stop on boss hit |
| Hit-stop time scale | float | 0.0 | 0.0–0.5 | Time scale during hit-stop |

## Visual/Audio Requirements

None. The Time System is invisible to the player. Any audio/visual effects of hit-stop are orchestrated by the systems that call `TriggerHitStop()`.

## UI Requirements

None directly. The HUD reads `RunElapsedTime` from the Time System for the run timer display, but that integration is documented in the HUD GDD.

## Acceptance Criteria

- **GIVEN** GState transitions to Paused, **WHEN** the transition completes, **THEN** `Time.timeScale == 0`.
- **GIVEN** GState transitions from Paused back to InRun after `Time.timeScale` was 0.5 before pause entry (slow-mo active), **WHEN** the transition completes, **THEN** `Time.timeScale == 0.5` (pre-pause scale restored, not 1.0).
- **GIVEN** a cooldown is registered with `duration = 5`, **WHEN** 3 seconds pass in scaled time, **THEN** `GetRemaining(id)` returns ~2 and `IsReady(id)` returns false.
- **GIVEN** a cooldown is registered with `duration = 3`, **WHEN** 3 seconds pass, **THEN** `IsReady(id)` returns true.
- **GIVEN** `TriggerHitStop(0.5f)` is called, **WHEN** 0.1 unscaled seconds pass, **THEN** `Time.timeScale == 0`.
- **GIVEN** `TriggerHitStop(0.5f)` is called, **WHEN** 0.6 unscaled seconds pass, **THEN** `Time.timeScale == 1`.
- **GIVEN** the game is in InRun for 10 seconds, **WHEN** the HUD queries `RunElapsedTime`, **THEN** the value is approximately 10.
- **GIVEN** the game is paused for 5 seconds, **WHEN** `RunElapsedTime` is queried, **THEN** the value is unchanged from when pause began.
- **GIVEN** `RegisterCooldown("dodge", 0)` is called, **WHEN** checked immediately, **THEN** `IsReady("dodge")` returns true.
- **GIVEN** `IsReady("unknown")` is called without prior registration, **THEN** it returns true (no exception).

## Open Questions

1. Should hit-stop stack or overwrite? → **Recommendation**: Overwrite (last call wins). Stacking would require subtracting from remaining, which makes debugging hit-stop feel impossible. Resolved.
