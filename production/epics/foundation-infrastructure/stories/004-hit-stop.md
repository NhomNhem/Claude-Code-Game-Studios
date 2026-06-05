# Story 004: Hit-Stop

- **Epic**: Foundation Infrastructure
- **System**: Time System
- **Type**: Logic
- **Priority**: P1 — Important (hit-stop needed before combat feel work)
- **Estimate**: 2h
- **Status**: Complete
- **Last Updated**: 2026-06-02

## GDD Requirements

*From [Time System GDD](design/gdd/time-system.md):*


| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-PLACEHOLDER-019` | Hit-stop triggered via TimeManager.TriggerHitStop(duration) | ✅ ADR-004 |
| `TR-PLACEHOLDER-020` | Hit-stop uses unscaled time; restores pre-hit-stop timeScale | ✅ ADR-004 |
| `TR-PLACEHOLDER-021` | Hit-stop and pause compose correctly | ✅ ADR-004 |

## ADR Guidance

**ADR-004 (Time System & Hit-Stop):**
- Hit-stop sets Time.timeScale to 0 (like pause) but in unscaled time
- Hit-stop owns the timeScale exclusively during its duration
- Pre-hit-stop timeScale is saved and restored when hit-stop ends
- hit-stop + pause: if paused during hit-stop, the hit-stop timer pauses; on unpause, hit-stop resumes for remaining duration
- pause + hit-stop: if hit-stop triggered during pause, it applies after unpause

**Control Manifest (Foundation Layer):**
- Time.timeScale never written outside TimeManager — source: ADR-004

## Description

Implement hit-stop (time-freeze on impact). `TimeManager.TriggerHitStop(duration)` freezes game time for a short duration in unscaled time, then restores the previous timeScale. Hit-stop composes correctly with pause: it pauses during pause, and hit-stop triggered during pause applies after unpause.

## Design

```csharp
public interface ITimeManager
{
    /// <param name="duration">Duration in seconds (unscaled). Capped at 2s.</param>
    /// <param name="timeScale">Target timeScale during hit-stop. Default 0 (full freeze).</param>
    void TriggerHitStop(float duration, float timeScale = 0f);
}
```

**M0 scope note**: `timeScale` parameter defaults to 0. Non-zero hit-stop (e.g., 0.1f slow-motion) is deferred. The parameter exists on the API for forward compatibility but M0 always passes 0.

### Hit-Stop State Machine

States for the hit-stop subsystem:
1. **Idle**: no hit-stop active
2. **Active**: hit-stop running, timeScale == 0
3. **PausedWhileHitStopped**: hit-stop was active when game paused
4. **HitStopPending**: TriggerHitStop called while game is paused — applies after unpause

### Duration Tracking

- `_remainingHitStopDuration` counts down in unscaled time
- On `Update()`:
  - `_remainingHitStopDuration -= Time.unscaledDeltaTime` (always — hit-stop must expire even when paused per ADR-004)
  - Restoration gated by `!_isPaused`: if paused, don't change timeScale (pause owns it)
  - When `_remainingHitStopDuration <= 0` and not paused: restore `_preHitStopTimeScale`
- Rationale per ADR-004: "Hit-stop duration elapses in unscaled time during pause. On unpause, if expired, restores pre-hit-stop scale."

### Composition Logic

| Scenario | What happens |
|----------|-------------|
| Hit-stop during gameplay | timeScale = 0 for duration, then restore |
| Pause during hit-stop | Hit-stop timer freezes; after unpause, timer resumes |
| Hit-stop during pause | Store pending flag; after unpause, apply hit-stop |
| Hit-stop ends during pause | timeScale stays 0 (because pause), pre-scale saved for pause restore |

### Pre-scale tracking

- `_preHitStopTimeScale`: captured when hit-stop starts (last call wins — overwrites on rapid hit-stops)
- `_preHitStopTimeScaleForPause`: captured when pause starts (saves `Time.timeScale` at pause entry, which is 0 during hit-stop — no issue since pause restore uses this instead of hit-stop's pre-scale)
- On unpause: if hit-stop was active before pause:
  - Restore hit-stop timer (resume countdown)
  - timeScale stays 0 (hit-stop still active)
  - When hit-stop expires, restore `_preHitStopTimeScale`
- On hit-stop end: if game is paused, don't change timeScale (pause owns it)

### Edge Cases

- Hit-stop triggered during hit-stop: ignore (or reset timer — design choice: reset)
- Zero-duration hit-stop: no-op
- Very long hit-stop: capped at 2 seconds
- Multiple rapid hit-stops: last one wins (reset timer)

## Acceptance Criteria

1. **TriggerHitStop works**: `TriggerHitStop(0.1f)` sets timeScale to 0.
2. **Duration in unscaled time**: Hit-stop lasts exactly 0.1 seconds of real time (tolerance ±16.6ms / 1 frame at 60fps) regardless of pre-hit-stop timeScale.
3. **Pre-scale restored**: After hit-stop, timeScale returns to the value before hit-stop (not always 1.0).
4. **Pause during hit-stop**: Hit-stop timer continues in unscaled time during pause (per ADR-004). Expected expiry accounts for both pre-pause and during-pause elapsed time. After unpause, if still active, hit-stop resumes for remaining duration.
5. **Hit-stop during pause**: `TriggerHitStop(0.1f)` while paused is stored; after unpause, hit-stop duration runs.
6. **Zero-duration hit-stop**: `TriggerHitStop(0f)` is a no-op (timeScale unchanged).
7. **Multiple rapid hit-stops**: Second call resets timer; total duration = last call's duration (not sum).
8. **Hit-stop does not affect run timer**: `RunElapsedTime` does not advance during hit-stop.
9. **Hit-stop expires during pause**: If hit-stop would end while game is paused, timeScale stays 0 (because pause). After unpause, no hit-stop resume occurs.
10. **Duration cap**: `TriggerHitStop(3f)` is capped to 2 seconds maximum.

## Engine Notes

- **Knowledge Risk**: LOW — `Time.timeScale`, `Time.unscaledDeltaTime`, `Time.unscaledTime` are stable APIs unchanged in Unity 6 (per ADR-004).
- **Performance Budget**: Hit-stop adds unscaled delta-time subtraction in `Update()`. Budget: < 0.001ms per frame.
- **Hidden dependency**: AC-8 requires `RunElapsedTime` to be exposed via `ITimeManager` from Story 003 (already implemented).

## Test Evidence Path

- `Assets/_TinyRift/Tests/EditMode/TimeSystem/HitStopTests.cs`
- All 9 acceptance criteria as individual test methods
- Time-sensitive tests use `ITimeProvider` abstraction
- Must verify pre-scale preservation with values other than 1.0

## Dependencies

- Story 003 (Time System Core) — extends ITimeManager with TriggerHitStop

## Risks

- **MEDIUM**: Composition with pause requires careful state machine. Mitigation: document state transitions clearly; exhaustive test coverage of all combinations.

## Completion Notes
**Completed**: 2026-06-02
**Criteria**: 10/10 passing
**Deviations**: SetPaused on ITimeManager instead of Event Bus subscription (deferred to Story 006). Hardcoded 2s cap (M0 scope). No external Time.timeScale change detection (debug aid only).
**Test Evidence**: `Assets/_TinyRift/Tests/EditMode/TimeSystem/HitStopTests.cs` — 10 test methods, all ACs covered
**Code Review**: Complete — APPROVED WITH SUGGESTIONS after AC-4 reconciliation (hit-stop ticks during pause, aligns with ADR-004)
