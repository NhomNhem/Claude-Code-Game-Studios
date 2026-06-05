# Story 001: GState Core State Machine

- **Epic**: Foundation Infrastructure
- **System**: Game State Manager
- **Type**: Logic
- **Priority**: P0 — Blocking (every other system depends on GState)
- **Estimate**: 3h
- **Status**: Complete
- **Last Updated**: 2026-06-02

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-PLACEHOLDER-001` | GameStateManager maintains single active state | ✅ ADR-001 |
| `TR-PLACEHOLDER-003` | GState exposes `TransitionTo(phase) → bool` | ✅ ADR-001 |
| `TR-PLACEHOLDER-004` | Invalid transitions silently rejected (returns false) | ✅ ADR-001 |
| `TR-PLACEHOLDER-005` | bossActive flag snapshot across pause cycles | ✅ ADR-001 |
| `TR-PLACEHOLDER-006` | Defeat has higher priority than Victory when simultaneous | ✅ ADR-001 |

## ADR Guidance

**ADR-001 (VContainer DI Architecture):**
- Interface-first: `IGameStateManager` consumed by all systems, not concrete `GameStateManager`
- Registration order-independent (Foundation batch)
- Singleton in `TinyRiftScope`

**Control Manifest (Foundation Layer):**
- Foundation registration batch is order-independent
- All systems register as interface singletons

## Description

Implement the core FSM for Game State Manager. The state machine manages top-level game phases (`None`, `Menu`, `Loading`, `InRun`, `BossFight`, `Paused`, `Victory`, `Defeat`, `HeroCamp`) with a strict transition matrix. Invalid transitions are silently rejected. The `bossActive` flag survives pause/resume cycles. On simultaneous state conflicts, Defeat beats Victory.

This story covers the pure state machine logic only — no Event Bus publishing, no Time System integration. Those are in Stories 005 and 006.

## Design

```csharp
public enum GamePhase
{
    None,
    Menu,
    Loading,
    InRun,
    BossFight,
    Paused,
    Victory,
    Defeat,
    HeroCamp
}

public interface IGameStateManager
{
    GamePhase CurrentPhase { get; }
    bool IsBossActive { get; }
    bool TransitionTo(GamePhase phase);
    void SetBossActive(bool active);
}
```

### Transition Matrix

| From ↓ / To → | Menu | Loading | InRun | BossFight | Paused | Victory | Defeat | HeroCamp |
|---------------|------|---------|-------|-----------|--------|---------|--------|----------|
| None          | ✅   | ✅      | ❌    | ❌        | ❌     | ❌      | ❌     | ❌       |
| Menu          | —    | ✅      | ❌    | ❌        | ❌     | ❌      | ❌     | ✅       |
| Loading       | ❌   | —       | ✅    | ❌        | ❌     | ❌      | ❌     | ❌       |
| InRun         | ❌   | ❌      | —     | ✅        | ✅     | ✅      | ✅     | ❌       |
| BossFight     | ❌   | ❌      | ❌    | —         | ✅     | ✅      | ✅     | ❌       |
| Paused        | ❌   | ❌      | ✅    | ❌        | —      | ❌      | ❌     | ❌       |
| Victory       | ❌   | ❌      | ❌    | ❌        | ❌     | —       | ❌     | ✅       |
| Defeat        | ❌   | ❌      | ❌    | ❌        | ❌     | ❌      | —      | ✅       |
| HeroCamp      | ❌   | ❌      | ❌    | ❌        | ❌     | ❌      | ❌     | —        |

### Conflict Priority

Avoids the need for deferred transitions or frame buffering. Instead, uses a **priority override** in `TransitionTo`: if the target phase has higher priority than the current phase, the matrix check is bypassed. This ensures `Defeat` can always override any other phase.

Priority values:
- `Defeat` = 100
- `Victory` = 50
- All others = 0

```csharp
public bool TransitionTo(GamePhase phase)
{
    int newPrio = GetPhasePriority(phase);
    int curPrio = GetPhasePriority(_currentPhase);
    bool highPriorityOverride = newPrio > curPrio;

    if (!_transitionMatrix[_currentPhase, phase] && !highPriorityOverride)
        return false;

    var previous = CurrentPhase;
    _currentPhase = phase;
    _eventBus?.Publish(new GameStateChanged(previous, phase));
    return true;
}
```

How conflict scenarios resolve:

| Call Sequence | Phase Before | TransitionTo(Victory) | TransitionTo(Defeat) | Result |
|---------------|-------------|----------------------|----------------------|--------|
| Victory then Defeat | InRun | ✅ matrix, phase=Victory | ✅ priority override (100>50), phase=Defeat | Defeat wins |
| Defeat then Victory | InRun | ✅ matrix, phase=Defeat | ❌ matrix (Defeat→Victory), no override | Defeat wins |
| Both InRun | Menu | ❌ matrix (Menu→InRun) | N/A | Both return false |

Self-transitions (e.g., Paused → Paused) return `true` with no event published.

**Important**: Priority override only fires when `newPrio > curPrio`. Same-priority overrides (e.g., Menu → Loading → InRun chain) use the matrix normally.

### BossFight Design Decision

The GDD treats `BossFight` as a sub-state flag (`bossActive` property). This story elevates it to a full `GamePhase` enum value for cleaner FSM logic. The `bossActive` boolean is retained as a convenience accessor for systems that need a quick check. See ADR-001 for interface-first pattern — the concrete implementation details (enum vs flag) are transparent to consumers via `IGameStateManager`.

### bossActive Flag

- `IsBossActive` is an independent property, not derived from `CurrentPhase`
- Survives Paused → InRun transition (set once, cleared when boss fight ends, not on pause)
- Cleared on returning to Menu/HeroCamp

## Acceptance Criteria

1. **Startup**: After construction, `CurrentPhase` is `GamePhase.None`.
2. **Menu transition**: `TransitionTo(Menu)` from None returns true and sets phase to Menu.
3. **Invalid transition**: `TransitionTo(InRun)` from Menu returns false; phase stays Menu.
4. **Loading → InRun**: Loading → InRun succeeds.
5. **InRun → Paused**: InRun → Paused succeeds.
6. **Paused → InRun**: Paused → InRun succeeds (resume).
7. **Double-pause**: Calling `TransitionTo(Paused)` while already Paused returns false.
8. **bossActive survives pause**: Set `IsBossActive = true`, Paused → InRun, `IsBossActive` remains true.
9. **bossActive cleared on Menu**: Set `IsBossActive = true`, transition to Menu, `IsBossActive` becomes false.
10. **Menu → Loading**: None → Menu → Loading succeeds; first TransitionTo(Menu) returns true, then TransitionTo(Loading) from Menu returns true.
11. **InRun → BossFight**: InRun → BossFight succeeds.
12. **Victory → HeroCamp**: Victory → HeroCamp succeeds.
13. **Defeat → HeroCamp**: Defeat → HeroCamp succeeds.
14. **Loading not pausable**: `TransitionTo(Paused)` from Loading returns false.
15. **Defeat beats Victory (Victory first)**: `TransitionTo(Victory)` returns true (matrix), then `TransitionTo(Defeat)` returns true (priority override 100>50); current phase is Defeat.
16. **Defeat beats Victory (Defeat first)**: `TransitionTo(Defeat)` returns true (matrix). `TransitionTo(Victory)` returns false (Defeat→Victory invalid, no override since 50<100). Current phase is Defeat.
17. **Self-transition no-op**: `TransitionTo(Menu)` from Menu returns true; no event published (no phase change).
18. **Same-target concurrent callers**: Two callers both invoke `TransitionTo(InRun)` from Loading. First succeeds (phase=InRun). Second checks InRun→InRun (self) which returns true. Phase stays InRun. No double-event.
19. **HeroCamp → Loading fails**: HeroCamp → Loading returns false (go to Menu first).
20. **Dispose is idempotent**: `Dispose()` called multiple times does not throw; state is clean after disposal.
21. **BossFight → Paused → InRun preserves bossActive**: After BossFight → Paused → InRun, `IsBossActive` remains true.

## Test Evidence Path

- `Assets/_TinyRift/Tests/EditMode/GameStateManager/GameStateManagerCoreTests.cs`
- All 21 acceptance criteria as individual `[UnityTest]` or `[Test]` methods
- Transition matrix fully covered (exhaustive pair-wise at minimum)
- Test must NOT depend on Event Bus or Time System

## Dependencies

- **None** — this story is independently testable with pure C#

## Risks

- **MEDIUM**: BossFight as enum value vs sub-state flag diverges from GDD. The `bossActive` flag is retained as a convenience accessor but may confuse consumers. Mitigation: document this in ADR-001 or a new ADR.
- **MEDIUM**: Priority override mechanism is a design addition not in the GDD. The GDD specifies "check Defeat first in frame processing order" which is a convention, not an API guarantee. The priority override makes it a hard guarantee at the cost of a slightly more complex TransitionTo. All callers must handle `TransitionTo` returning `true` even when the phase doesn't reach the expected target (due to higher-priority override). Mitigation: document in code that only `Defeat` uses non-zero priority.

## Completion Notes
**Completed**: 2026-06-02
**Criteria**: 21/21 passing (all auto-verified via unit tests)
**Deviations**: XML doc comments missing on public members (nice-to-have); asmdef + manifest.json modified for test compilation infrastructure
**Test Evidence**: Logic: `Assets/_TinyRift/Tests/EditMode/GameStateManager/GameStateManagerCoreTests.cs` (31 tests, all passing)
**Code Review**: Approved (LP-CODE-REVIEW: APPROVE; QL-TEST-COVERAGE: GAPS → 3 missing tests added)
