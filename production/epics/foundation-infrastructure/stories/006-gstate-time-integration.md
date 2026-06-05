# Story 006: GState → Time System Integration

- **Epic**: Foundation Infrastructure
- **Systems**: Game State Manager, Time System
- **Type**: Integration
- **Priority**: P0 — Blocking (pause/unpause must control timeScale)
- **Estimate**: 2h
- **Manifest Version**: 2026-06-01
- **Last Updated**: 2026-06-02

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-PLACEHOLDER-025` | Pause sets Time.timeScale = 0 | ✅ ADR-001, ADR-004 |
| `TR-PLACEHOLDER-026` | Pre-pause timeScale restored on unpause | ✅ ADR-001, ADR-004 |
| `TR-PLACEHOLDER-027` | Auto-pause via Application focus loss | ✅ ADR-001, ADR-004 |
| `TR-PLACEHOLDER-028` | Slow-mo pre-pause scale preserved through pause cycle | ✅ ADR-001, ADR-004 |
| `TR-PLACEHOLDER-029` | Unity lifecycle events (OnApplicationFocus) trigger GState transition | ✅ ADR-001 |

## ADR Guidance

**ADR-001 (VContainer DI Architecture):**
- `IGameStateManager` consumed by `TimeManager` via DI
- `TimeManager` subscribes to `GameStateChanged` to react to pause/unpause
- Auto-pause wiring: `MonoBehaviour` in VContainer scope handles `OnApplicationFocus`

**ADR-004 (Time System & Hit-Stop):**
- `TimeManager` is sole writer of `Time.timeScale`
- On `GameStateChanged` → Paused: set timeScale to 0 (if not hit-stop)
- On unpause: restore pre-pause timeScale (could be 1.0 or slow-mo value)
- Slow-mo: timeScale might be 0.3 before pause; after unpause, restore 0.3

**Control Manifest (Foundation Layer):**
- Time.timeScale never written outside TimeManager — source: ADR-004
- Subscribe in Awake/Start — source: ADR-002

## Description

Wire TimeManager to react to GameState changes for pause/unpause timeScale control. This is the connection between the logical state machine (GState) and the temporal authority (TimeManager).

### Pause Flow

1. GState transitions InRun → Paused
2. GState publishes `GameStateChanged(Paused)` via Event Bus
3. TimeManager (subscribed to `GameStateChanged`) receives the event
4. TimeManager saves current `Time.timeScale` as `_prePauseTimeScale`
5. TimeManager sets `Time.timeScale = 0`
6. On unpause (Paused → InRun):
7. TimeManager receives `GameStateChanged(InRun)`
8. TimeManager restores `_prePauseTimeScale`

### Slow-Mo Preservation

- If timeScale was 0.3 before pause, it must be 0.3 after unpause
- TimeManager tracks `_prePauseTimeScale` independently of the current timeScale
- Hit-stop's `_preHitStopTimeScale` and pause's `_prePauseTimeScale` are separate variables

### Auto-Pause on Focus Loss

A `MonoBehaviour` (e.g., `FocusLossHandler`) registered in VContainer:
1. Subscribes to `OnApplicationFocus(false)`
2. Calls `_gameStateManager.TransitionTo(Paused)` if current state allows
3. On focus regain, does NOT auto-unpause (player must manually unpause via escape)

**Design decision**: Rather than testing `OnApplicationFocus` directly (which requires playmode), extract an `IFocusLossHandler` interface that can be unit-tested with a mock implementation. The production `FocusLossHandler` MonoBehaviour adapts `OnApplicationFocus` to `IFocusLossHandler`. This keeps ACs 4-6 in edit-mode tests.

### TimeScale Arbitration

When both hit-stop and pause are active:
- Hit-stop saves `_preHitStopTimeScale` (could be 0.3 for slow-mo)
- Pause saves `_prePauseTimeScale` (could be 0.0 from hit-stop or 0.3 from slow-mo)
- On unpause: if hit-stop is active, restore hit-stop state
- On hit-stop end: if game is paused, don't change timeScale (pause owns it)

**Simplified approach for M0:**
- `_prePauseTimeScale` is captured when pause starts
- `_preHitStopTimeScale` is captured when hit-stop starts
- On unpause: restore `_prePauseTimeScale` (which might be 0 from hit-stop, or slow-mo value)
- TimeManager uses a priority: hit-stop pending > pause > normal

### Tick Behavior

- `TimeManager.Update()` runs every frame
- If timeScale == 0 (paused OR hit-stop): cooldowns with `pausedSafe=true` don't tick
- If timeScale == 0 (paused OR hit-stop): cooldowns with `pausedSafe=false` still tick
- Rationale: hit-stop uses timeScale == 0, so `pausedSafe` semantics also apply. This may be tuned post-M0 if combat feel requires cooldowns to advance during hit-stop.

## Acceptance Criteria

1. **Pause sets timeScale to 0**: GState transitions to Paused → `Time.timeScale == 0`.
2. **Unpause restores timeScale**: Paused → InRun → `Time.timeScale` returns to pre-pause value.
3. **Slow-mo preserved**: Set timeScale to 0.3, pause, unpause → timeScale is 0.3 (not 1.0).
4. **Auto-pause on focus loss**: `IFocusLossHandler.OnFocusLost()` triggers `TransitionTo(Paused)` when in InRun or BossFight.
5. **Auto-pause does not trigger in Menu**: `IFocusLossHandler.OnFocusLost()` in Menu is ignored.
6. **Focus regain does not auto-unpause**: `IFocusLossHandler.OnFocusGained()` does not call unpause.
7. **Auto-pause during hit-stop**: Focus loss during hit-stop pauses; on unpause, hit-stop timer resumes.
8. **Run elapsed time freezes during pause**: `RunElapsedTime` does not increase while paused.
9. **Composed hit-stop → pause → unpause**: Hit-stop active → pause → unpause → hit-stop resumes for remaining duration.

## Test Evidence Path

- `Assets/_TinyRift/Tests/EditMode/TimeSystem/TimeSystemGStateIntegrationTests.cs`
- All 9 acceptance criteria as individual test methods

## Dependencies

- Story 001 (GState Core) — FSM
- Story 002 (Event Bus Core) — messaging
- Story 003 (Time System Core) — time management
- Story 004 (Hit-Stop) — hit-stop
- Story 005 (GState → Event Bus) — event publishing

## Risks

- **HIGH**: Arbitration between hit-stop, pause, and slow-mo timeScale values is the most complex logic in the Foundation layer. 5-story dependency chain. Mitigation: state machine with clear priority hierarchy; exhaustive test coverage of all 9 combinations; manual timeScale arbitration table in code comments.
- **MEDIUM**: `IFocusLossHandler` abstraction adds a layer of indirection for testability. The production `FocusLossHandler` MonoBehaviour must be verified manually since it bridges Unity lifecycle → interface.
