# Story 005: GState → Event Bus Integration

- **Status**: Complete
- **Last Updated**: 2026-06-02
- **Epic**: Foundation Infrastructure
- **Systems**: Game State Manager, Event Bus
- **Type**: Integration
- **Priority**: P0 — Blocking (most systems subscribe to GameStateChanged)
- **Estimate**: 2h

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-PLACEHOLDER-022` | GState publishes GameStateChanged event on each transition | ✅ ADR-002 |
| `TR-PLACEHOLDER-023` | GameStateChanged event contains Previous and Current phases | ✅ ADR-001, ADR-002 |
| `TR-PLACEHOLDER-024` | Pause preserves origin phase for correct unpause behavior | ✅ ADR-001 |

## ADR Guidance

**ADR-001 (VContainer DI Architecture):**
- `IGameStateManager` and `IEventBus` registered via VContainer in `TinyRiftScope`
- `GameStateManager` depends on `IEventBus`
- Registration order-independent

**ADR-002 (Event Bus Contract):**
- `GameStateChanged` is a `readonly record struct` with `Previous` and `Current` phases
- Publish before returning from `TransitionTo`
- Subscription tokens stored by the subscriber (not in this story)

**Control Manifest (Foundation Layer):**
- Subscribe in Awake/Start — source: ADR-002
- Store IDisposable token — source: ADR-002
- No closure lambdas — source: ADR-002

## Description

Wire GameStateManager to publish `GameStateChanged(Previous, Current)` via Event Bus every time a transition succeeds. The event is published synchronously before `TransitionTo` returns true. This integration enables all downstream systems to react to game phase changes.

The `GameStateChanged` event record:
```csharp
public readonly record struct GameStateChanged(GamePhase Previous, GamePhase Current);
```

### Pause Origin Tracking

When transitioning to Paused, store the origin phase. When unpausing (Paused → InRun), publish:
- Previous: InRun (paused from)
- Current: InRun (returning to)

The origin field is separate from the Event Bus event (not needed by subscribers — they just see the transition event).

### Wire-Up

In `GameStateManager.TransitionTo`:
1. Validate transition
2. Store `_previousPhase`
3. Set `_currentPhase = phase`
4. `_eventBus.Publish(new GameStateChanged(_previousPhase, _currentPhase))`
5. Return true

## Acceptance Criteria

1. **GameStateChanged published on transition**: `TransitionTo(InRun)` publishes `GameStateChanged` with `Previous=None, Current=InRun`.
2. **Event not published on failed transition**: Invalid transition does not publish any event.
3. **Previous and Current correct**: All valid transitions publish correct Previous/Current values.
4. **Pause origin preserved**: After Paused → InRun, the transition event shows `Previous=Paused, Current=InRun`.
5. **Event published synchronously**: Subscriber receives the event before `TransitionTo` returns.
6. **Multiple subscribers all receive event**: 3 subscribers for `GameStateChanged` all receive it on a single transition.
7. **Event Bus registration works**: `IGameStateManager` is registered as singleton; `IEventBus` injected via constructor.
8. **Subscriber does not cause issues if it unsubscribes during handler**: Per-subscriber isolation protects against subscription modification during publish cycle.

## Test Evidence Path

- `Assets/_TinyRift/Tests/EditMode/GameStateManager/GameStateManagerEventBusIntegrationTests.cs`
- All 8 acceptance criteria as individual test methods
- Uses mock subscribers attached to the Event Bus

## Dependencies

- Story 001 (GState Core) — provides the FSM
- Story 002 (Event Bus Core) — provides the event bus

## Risks

- **LOW**: Reentrancy — if a subscriber calls `TransitionTo` inside its handler, it creates nested publish. Mitigation: reentrancy guard in Event Bus (Story 002) caps at depth 16.

## Completion Notes
**Completed**: 2026-06-02
**Criteria**: 8/8 passing (all auto-verified via tests)
**Deviations**: ADR-002 drift (event type signature) — fixed during implementation. Minor reentrancy throw-vs-log ADR drift deferred (non-blocking).
**Test Evidence**: Integration test at `Assets/_TinyRift/Tests/EditMode/GameStateManager/GameStateManagerEventBusIntegrationTests.cs` — 9 tests, all passing (87/87 total edit mode)
**Code Review**: Complete — APPROVED via LP-CODE-REVIEW gate. EventBus publish loop bug fixed. ADR-002 synced.
