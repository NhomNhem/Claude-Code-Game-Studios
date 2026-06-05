# ADR-004: Time System & Hit-Stop Ownership

## Status

Accepted

## Date

2026-06-01

## Decision Makers

user + agents (technical-director, architecture-decision skill)

## Summary

Establish `TimeManager` as the sole authority over `Time.timeScale`. All time-related queries (cooldowns, elapsed run timer, hit-stop, pause state) route through the `ITimeManager` interface. No system other than `TimeManager` reads or writes `Time.timeScale`.

## Engine Compatibility

| Field | Value |
|-------|-------|
| **Engine** | Unity 6000.3.11f1 (Unity 6 Update 3) |
| **Domain** | Core (Time Management) |
| **Knowledge Risk** | LOW — `Time.timeScale`, `Time.deltaTime`, `Time.unscaledDeltaTime`, `Time.unscaledTime` are stable APIs unchanged in Unity 6 |
| **References Consulted** | `docs/engine-reference/unity/VERSION.md` (no breaking changes to Time API) |
| **Post-Cutoff APIs Used** | None |
| **Verification Required** | Verify `Time.timeScale = 0` correctly pauses cooldowns and animations. Verify `Time.unscaledDeltaTime` continues ticking during hit-stop for proper duration tracking. |

## ADR Dependencies

| Field | Value |
|-------|-------|
| **Depends On** | ADR-001 (TinyRiftScope registration in Foundation layer), ADR-002 (Event Bus — subscribes to `GameStateChangedEvent` for pause/unpause) |
| **Enables** | All combat systems (Orbit/Burst cooldowns via `RegisterCooldown`/`IsReady`), Screen Shake (hit-stop via `TriggerHitStop`), HUD (timer display via `RunElapsedTime`) |
| **Blocks** | Combat system story work — until ADR-004 is Accepted, developers cannot know which cooldown API to call |
| **Ordering Note** | Must be implemented after Event Bus exists (ADR-002) |

## Context

### Problem Statement

`Time.timeScale` is a global singleton mutable by any code. Without a single authority, multiple systems could set conflicting scales — hit-stop sets 0, pause sets 0, a slow-mo zone sets 0.3 — with no coordination. The architecture principle "Time System owns Time.timeScale exclusively" (architecture.md:271) mandates a single owner, but the ownership model, hit-stop behavior (stacking vs overwriting), cooldown API shape, and pause scale preservation require formal decision.

### Current State

- Architecture doc lists Time under Foundation (order-independent)
- GDD specifies `ITimeManager` interface, cooldown registry, and `TriggerHitStop`
- `GameStateChangedEvent` already defined in ADR-002 catalogue with `GameState.Paused`
- No `TimeManager` implementation exists

### Constraints

- **Sole owner**: No other system may read or write `Time.timeScale`. All time-scale modifications go through `ITimeManager`.
- **Pause correctness**: `Time.timeScale = 0` on pause must preserve the pre-pause scale, including a pre-hit-stop scale if hit-stop was active.
- **Hit-stop does not pause**: Hit-stop (`Time.timeScale = 0` for a duration) should freeze visual action but cooldowns and timers must track duration in unscaled time — hit-stop must expire even if the game is effectively paused visually.
- **Cooldown correctness**: Cooldown timer must respect `Time.timeScale` — cooldowns freeze during pause and slow down during slow-mo.
- **Run timer correctness**: `RunElapsedTime` (scaled) freezes on pause; `RunElapsedTimeUnscaled` runs through everything.

### Requirements

- `Time.timeScale` must never be written outside `TimeManager`
- Pause must preserve the effective scale at entry and restore it on exit
- Hit-stop must overwrite (not stack) — last call wins
- Cooldown registry must be thread-safe for string-based ID access (at minimum, no concurrent modification from multiple Unity update loops)
- External `Time.timeScale` changes must be detected and synced (with warning)

## Decision

### Architecture

```
                    GameStateChangedEvent (from Event Bus)
                         │
                         ▼ ITimeManager
                    ┌─────────────────────────────────┐
                    │         TimeManager              │
                    │                                  │
                    │  State:                          │
                    │    _prePauseTimeScale: float     │
                    │    _hitStopRemaining: float       │
                    │    _lastKnownTimeScale: float     │
                    │    _runStartTime: float           │
                    │    _cooldowns: Dictionary<str,float>│
                    │                                  │
                    │  Unity API owned:                │
                    │    Time.timeScale (write only)   │
                    │    Time.deltaTime (read, scaled) │
                    │    Time.unscaledDeltaTime (read) │
                    │    Time.unscaledTime (read)      │
                    └─────────────────────────────────┘
                         │
                    ┌────┴────┬─────────┬──────────┐
                    │         │         │          │
                    ▼         ▼         ▼          ▼
                Combat    Screen    HUD      Status
                Systems   Shake     (timer)   Effects
              (cooldowns) (hit-stop)          (tick timers)
```

### Key Interfaces

```csharp
public interface ITimeManager
{
    float RunElapsedTime { get; }
    float RunElapsedTimeUnscaled { get; }
    float TimeScale { get; }

    void RegisterCooldown(string id, float duration);
    bool IsReady(string id);
    float GetRemaining(string id);
    float GetProgress(string id);
    void ResetCooldown(string id, float duration);
    void CancelCooldown(string id);

    void TriggerHitStop(float duration, float timeScale = 0f);

    event Action<float> OnTimeScaleChanged;
    event Action<float> OnRunTimerUpdated;
}
```

### Implementation Guidelines

1. **Pause flow**:
   ```csharp
   private void OnGameStateChanged(GameStateChangedEvent evt)
   {
       if (evt.Current == GameState.Paused)
       {
           _prePauseTimeScale = _hitStopRemaining > 0
               ? _preHitStopTimeScale  // hit-stop was active — restore to pre-hit-stop
               : Time.timeScale;       // normal pause — save current scale
           Time.timeScale = 0;
       }
       else if (evt.Previous == GameState.Paused)
       {
           Time.timeScale = _prePauseTimeScale;
       }

       if (evt.Current == GameState.InRun) ResetRunTimer();
       if (evt.Previous == GameState.InRun && evt.Current != GameState.Paused) StopRunTimer();
   }
   ```

2. **Hit-stop flow**:
   ```csharp
   public void TriggerHitStop(float duration, float timeScale = 0f)
   {
       if (_hitStopRemaining > 0 && duration > _hitStopRemaining)
           Debug.LogWarning($"[TimeManager] Hit-stop overwritten: {_hitStopRemaining}s remaining → {duration}s");

       if (Time.timeScale > 0) _preHitStopTimeScale = Time.timeScale;

       _hitStopRemaining = duration;
       _hitStopTimeScale = timeScale;
       Time.timeScale = timeScale;
   }

   private void Update()
   {
       if (_hitStopRemaining > 0)
       {
           _hitStopRemaining -= Time.unscaledDeltaTime;
           if (_hitStopRemaining <= 0)
           {
               _hitStopRemaining = 0;
               if (Time.timeScale == _hitStopTimeScale) // don't overwrite if pause changed it
                   Time.timeScale = _preHitStopTimeScale;
           }
       }

       // External change detection
       if (Math.Abs(Time.timeScale - _lastKnownTimeScale) > 0.001f)
       {
           Debug.LogWarning($"[TimeManager] External Time.timeScale change detected: {_lastKnownTimeScale} → {Time.timeScale}");
           _lastKnownTimeScale = Time.timeScale;
           OnTimeScaleChanged?.Invoke(Time.timeScale);
       }
   }
   ```

3. **Cooldown tick**: Cooldowns decrement by `Time.deltaTime` each frame (respects time scale). At `Time.deltaTime == 0` (pause), cooldowns do not tick.

4. **Run timer**: Increments by `Time.deltaTime` (scaled) / `Time.unscaledDeltaTime` (unscaled) in `Update()`. Resets on `InRun` entry, stops on `InRun` exit (except pause).

5. **AOT safety**: `Dictionary<string, float>` is standard .NET — safe under IL2CPP. No generic delegates beyond `Action<float>` (preserved per ADR-002 AOT rules).

## Alternatives Considered

### Alternative 1: Scattered time management

- **Description**: Each system reads/writes `Time.timeScale` directly. Cooldowns managed per-system.
- **Pros**: No central service, minimal abstraction.
- **Cons**: Race conditions on `Time.timeScale`. Debugging impossible — who set the scale to 0? No pause coordination. Duplicated cooldown logic.
- **Rejection Reason**: Guaranteed bugs and debugging nightmare. Sole ownership is necessary for correctness.

### Alternative 2: Separate hit-stop and time-scale managers

- **Description**: `HitStopManager` handles `TriggerHitStop()`. `TimeScaleManager` handles pause. `CooldownRegistry` handles cooldowns. Three separate services.
- **Pros**: Single responsibility per service.
- **Cons**: Complex coordination — hit-stop must coordinate with pause scale preservation. Three VContainer registrations instead of one. Cross-service race conditions.
- **Estimated Effort**: Higher setup, lower maintenance.
- **Rejection Reason**: The GDD specifies a single `ITimeManager` interface. The coordination between hit-stop and pause is the hard part — splitting doesn't simplify it.

### Alternative 3: No scaled time

- **Description**: All systems use unscaled `Time.unscaledDeltaTime`. No `Time.timeScale` modifications. Pause is handled by disabling MonoBehaviours.
- **Pros**: Simple, no coordination needed.
- **Cons**: No hit-stop mechanic. No slow-mo zones. Pause requires every MonoBehaviour to check a flag. No cooldown scaling for gameplay effects.
- **Rejection Reason**: Hit-stop is a core visual feedback mechanic (Pillar 3 — snappy sessions). The game cannot ship without it.

## Consequences

### Positive

- Single authority prevents `Time.timeScale` conflicts
- Hit-stop correctly overwrites (last call wins) — always know which hit-stop is active
- Pause preserves pre-pause scale including pre-hit-stop scale
- Cooldown registry is simple (flat dictionary) — no entity management
- External time scale changes detected with warning (debug aid)
- Zero additional GC allocation (no per-frame allocations)

### Negative

- Hit-stop overwrite means rapid successive calls can shorten effective hit-stop (last call wins with its own duration)
- Cooldown registry is string-based — no compile-time safety on cooldown IDs
- `Update()` loop runs even when paused (checking hit-stop expiry) — negligible cost but still runs
- External change detection can fire spuriously during normal hit-stop → restore cycle (mitigated by guard condition checking `_hitStopTimeScale`)

### Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| System writes `Time.timeScale` directly despite ADR | Medium | Medium — breaks pause/hit-stop authority | Code review rule: grep for `Time.timeScale =` in `Assets/_TinyRift/`. Only `TimeManager.cs` may contain it. |
| Hit-stop called during pause (scale already 0) | Low | Low — `_prePauseTimeScale` already saved hit-stop's pre-h scale. Hit-stop duration elapses in unscaled time during pause. On unpause, if expired, restores pre-hit-stop scale. GDD explicitly handles this. | Edge case documented and handled. |
| Cooldown id collision (two systems use same string) | Low | Medium — wrong cooldown data | Convention: prefix cooldown IDs with system name (e.g., `"orbit_slot_0"`, `"burst_skill_fireball"`) |

## Performance Implications

| Metric | Before | Expected After | Budget |
|--------|--------|---------------|--------|
| CPU (per frame) | N/A | ~0.001ms (deltaTime read + cooldown decrement scan) | 0.01ms |
| Memory (per cooldown) | N/A | ~32 bytes (string key + float value in dictionary) | Negligible (< 100 cooldowns at any time) |
| GC (per frame) | N/A | 0 — no allocations in Update path | 0 |

## Migration Plan

1. Create `TimeManager.cs` in `Assets/_TinyRift/Runtime/Foundation/Time/` implementing `ITimeManager`
2. Create `ITimeManager.cs` interface file
3. Register in TinyRiftScope.ConfigureFoundation()
4. Wire Event Bus subscription to `GameStateChangedEvent`
5. Update Screen Shake system to call `ITimeManager.TriggerHitStop()` instead of `Time.timeScale`
6. Update combat systems to use `RegisterCooldown()`/`IsReady()`

**Rollback plan**: Remove TimeManager registration. Systems fall back to `Time.timeScale` directly — no crash, but pause/hit-stop coordination is lost. Gate with a compile-time `#if` check.

## Validation Criteria

- [ ] `Time.timeScale` is never assigned outside `TimeManager.cs` (grep test)
- [ ] Pause sets `Time.timeScale = 0`, unpause restores pre-pause scale
- [ ] Hit-stop sets `Time.timeScale = 0` for specified duration, then restores to pre-hit-stop scale
- [ ] Hit-stop called during pause does not break pause scale preservation
- [ ] Cooldown with 3s duration is ready after 3 scaled seconds
- [ ] Cooldown does not tick during pause (`Time.deltaTime == 0`)
- [ ] `RunElapsedTime` freezes on pause, continues on unpause
- [ ] `RunElapsedTime` resets to 0 on InRun → non-InRun transition
- [ ] External `Time.timeScale` modification fires `OnTimeScaleChanged` warning

## GDD Requirements Addressed

| GDD Document | System | Requirement | How This ADR Satisfies It |
|-------------|--------|-------------|--------------------------|
| `design/gdd/time-system.md` | Time System | Singleton service registered in TinyRiftScope as ITimeManager | Per ADR-001 — TimeManager registered in Foundation layer |
| `design/gdd/time-system.md` | Time System | Sole owner of Time.timeScale | ADR enforces: only TimeManager.cs may write Time.timeScale |
| `design/gdd/time-system.md` | Time System | GState-aware pause with pre-pause scale preservation | `_prePauseTimeScale` logic handles pause entry/exit |
| `design/gdd/time-system.md` | Time System | Hit-stop with overwrite (last call wins) | `TriggerHitStop()` overwrites `_hitStopRemaining` |
| `design/gdd/time-system.md` | Time System | Cooldown registry with string keys | `RegisterCooldown()`, `IsReady()`, `GetRemaining()` |
| `design/gdd/time-system.md` | Time System | Run elapsed timer | `RunElapsedTime`/`RunElapsedTimeUnscaled` reset on InRun entry |
| `design/gdd/game-state-manager.md` | Game State | Paused state affects time scale | TimeManager subscribes to GameStateChangedEvent |
| `design/gdd/screen-shake.md` | Screen Shake | Hit-stop via time scale | Calls `ITimeManager.TriggerHitStop()` |
| `design/gdd/orbit-combat-system.md` | Orbit Combat | Cooldowns per orbit slot | Orbit calls `RegisterCooldown()` with slot IDs |
| `design/gdd/burst-skill-system.md` | Burst Skill | Cooldowns per skill slot | Burst calls `RegisterCooldown()` with skill IDs |

## Related

- ADR-001: VContainer DI — TimeManager registered in TinyRiftScope Foundation layer
- ADR-002: Event Bus — TimeManager subscribes to GameStateChangedEvent
- `architecture.md:196-206` — ITimeManager prototype interface
- `design/gdd/time-system.md` — Full GDD with cooldown API, hit-stop spec, edge cases
