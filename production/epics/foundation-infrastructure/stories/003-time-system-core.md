# Story 003: Time System Core

- **Epic**: Foundation Infrastructure
- **System**: Time System
- **Type**: Logic
- **Priority**: P0 — Blocking (most gameplay systems depend on cooldowns and timing)
- **Estimate**: 3h
- **Status**: Complete
- **Last Updated**: 2026-06-02

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-PLACEHOLDER-014` | TimeManager is sole authority over Time.timeScale | ✅ ADR-004 |
| `TR-PLACEHOLDER-015` | Cooldown registration and query API | ✅ ADR-004 |
| `TR-PLACEHOLDER-016` | Cooldowns can be registered as paused-safe or not | ✅ ADR-004 |
| `TR-PLACEHOLDER-017` | Run elapsed time (paused-safe) | ✅ ADR-004 |
| `TR-PLACEHOLDER-018` | Zero-duration cooldowns return true immediately | ✅ ADR-004 |

## ADR Guidance

**ADR-004 (Time System & Hit-Stop):**
- `TimeManager` is the sole class that writes `Time.timeScale`
- Cooldown registry: `RegisterCooldown(float duration) → CooldownHandle`, `CooldownHandle.IsReady` accessor
- Pause-safe timing: cooldown timer does NOT advance while paused
- Run timer: tracks elapsed real time, FREEZES during pause
- Zero-duration cooldown: immediately ready (`IsReady == true`)
- Unregistered cooldown: `IsReady` returns true (safe default)

**Control Manifest (Foundation Layer):**
- `Time.timeScale` never written outside TimeManager — source: ADR-004
- Foundation registration batch is order-independent — source: ADR-001

## Description

Implement the Time System core. `TimeManager` owns all time-related state: `Time.timeScale`, cooldown registry, and run elapsed timer. Cooldowns are pause-safe (don't tick during pause). The run timer also freezes during pause. Zero-duration and unregistered cooldowns return ready.

This story covers standalone time logic only — no GState integration, no hit-stop. Those are in Stories 004 and 006.

## Design

```csharp
public interface ITimeManager
{
    float RunElapsedTime { get; }
    CooldownHandle RegisterCooldown(float duration, bool pausedSafe = true);
    bool TryGetCooldown(CooldownHandle handle, out float remaining, out float total);
}

public readonly struct CooldownHandle : IEquatable<CooldownHandle>
{
    private readonly int _id;
    // value semantics — can be stored in collections
}
```

### Cooldown Registry

- Internal class `CooldownRegistry` holds `List<CooldownEntry>`
- Each entry: `{ handle, duration, elapsed, pausedSafe }`
- Every `Update()` tick:
  - If not paused: `elapsed += deltaTime` for each cooldown
  - If paused: only non-pausedSafe cooldowns advance
  - `IsReady` = `elapsed >= duration`
- `RegisterCooldown(0f)`: mark as immediately ready (or insert with `elapsed = duration`)

### Run Timer

- `_runElapsed` accumulates `Time.unscaledDeltaTime` each tick
- Skips accumulation when `Time.timeScale == 0` (paused state is set by Story 006)
- Resets on new run start via `ResetRunTimer()`
- `RunElapsedTimeUnscaled` is deferred (M0 scope decision) — Story 003 only tracks the scaled run timer

### ITimeProvider Abstraction

All time-sensitive operations use `ITimeProvider` to allow deterministic testing:

```csharp
public interface ITimeProvider
{
    float DeltaTime { get; }
    float UnscaledDeltaTime { get; }
    float TimeScale { get; set; }
    float RealtimeSinceStartup { get; }
}
```

- **Production**: `UnityTimeProvider` wraps `Time.deltaTime`, `Time.unscaledDeltaTime`, `Time.timeScale`, `Time.realtimeSinceStartup`
- **Test**: `ManualTimeProvider` lets tests advance time by explicit increments
- Defined in `Assets/_TinyRift/Tests/Helpers/ITimeProvider.cs` (shared across Stories 003, 004, 006)

### Tick Method

TimeManager needs a `Tick()` method called from a `MonoBehaviour`'s `Update()`. The VContainer lifecycle registration handles this.

### Edge Cases

- `RegisterCooldown(0)`: immediately ready
- `RegisterCooldown(-1)`: clamp to 0 or treat as immediately ready
- Unregistered handle: `TryGetCooldown` returns false
- Multiple cooldowns with same duration: independently tracked
- Very long cooldowns (>1 hour): overflow-safe (use double or clamp)

## Acceptance Criteria

1. **TimeManager sole writer**: `Time.timeScale` is only set via `ITimeProvider.TimeScale` inside `TimeManager`. A reflection-based test scans `_TinyRift/` assemblies and asserts no `Time.timeScale` assignment exists outside `TimeManager`. Test file: `TimeSystemCoreTests.cs`.
2. **Cooldown registration**: `RegisterCooldown(5f)` returns a valid handle.
3. **Cooldown expiry**: After 5 seconds of game time, `IsReady` is true.
4. **Cooldown not yet ready**: At 3 seconds of a 5-second cooldown, `IsReady` is false.
5. **Pause-safe cooldown**: `pausedSafe=true` cooldown doesn't tick while timeScale == 0.
6. **Non-pause-safe cooldown**: `pausedSafe=false` cooldown still ticks while timeScale == 0.
7. **Zero-duration cooldown**: `RegisterCooldown(0f)` returns immediately ready.
8. **Unregistered cooldown**: Default `CooldownHandle` (never registered) — `IsReady` returns true, `TryGetCooldown` returns false.
9. **Run elapsed time starts at 0**: `RunElapsedTime` is 0.0 at start.
10. **Run elapsed time accumulates**: After 10 game seconds, `RunElapsedTime` ≈ 10.0 (within tolerance).
11. **Negative duration clamp**: `RegisterCooldown(-1f)` clamps to 0 and returns immediately ready.
12. **Handle equality**: Two handles from same registration are equal; handles from different registrations are not.
13. **TryGetCooldown**: For valid handle, returns remaining and total duration.

## Test Evidence Path

- `Assets/_TinyRift/Tests/EditMode/TimeSystem/TimeSystemCoreTests.cs`
- All 13 acceptance criteria as individual test methods
- Time-sensitive tests use `TimeProvider` abstraction or manual time advance (not wall clock)
- Test must NOT depend on GState or Event Bus

## Dependencies

- **UnityEngine.Time** — wrapped via `ITimeProvider` (`UnityTimeProvider` in production, `ManualTimeProvider` in tests)
- **Shared test helper**: `Assets/_TinyRift/Tests/Helpers/ITimeProvider.cs` (created in this story, shared with 004 and 006)

## Deferred API Items (M0 Scope)

| GDD API | Priority | Rationale |
|---------|----------|-----------|
| `RunElapsedTimeUnscaled` | P2 | Not needed until systems compare real-time vs game-time |
| `OnTimeScaleChanged` event | P2 | Consumers can poll `CurrentScale` or react via `GameStateChanged` events |
| `GetProgress(handle) → float 0.0–1.0` | P2 | Callers can compute `elapsed/duration` themselves |
| `ResetCooldown(handle, duration)` | P2 | Not needed for initial skill system |
| `CancelCooldown(handle)` | P2 | Cooldown expiry handles natural cleanup |

## Risks

- **LOW**: time-sensitive tests need deterministic time simulation. Mitigation: `ManualTimeProvider` in shared test helpers.
- **LOW**: Run timer using `Time.unscaledDeltaTime` may accumulate drift. Mitigation: use `Time.realtimeSinceStartup` as source of truth for run timer.

## Completion Notes
**Completed**: 2026-06-02
**Criteria**: 13/13 passing
**Deviations**: ADR DRIFT (CooldownHandle vs string IDs) — M0 scope decision per Deferred API Items section. Minor: ITimeProvider abstraction, simplified interface (4/12 members), automated AC-1 scan.
**Test Evidence**: `Assets/_TinyRift/Tests/EditMode/TimeSystem/TimeSystemCoreTests.cs` — 13 test methods, one per AC
**Code Review**: Complete — APPROVED WITH SUGGESTIONS after fixing B1 (default handle id collision)
