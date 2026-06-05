# ADR-002: Event Bus Contract & Message Type Catalogue

## Status

Accepted

## Date

2026-06-01

## Decision Makers

user + agents (technical-director, architecture-decision skill)

## Summary

Define the Event Bus as the sole cross-system communication mechanism for the game. All 35 systems communicate through typed `readonly record struct` events — never through direct system references. Establishes the split interface pattern (`IEventBus` for publishers, `ISubscriber` for read-only consumers), the reentrancy guard design, the complete event type catalogue, and AOT safety requirements for IL2CPP.

## Engine Compatibility

| Field | Value |
|-------|-------|
| **Engine** | Unity 6000.3.11f1 (Unity 6 Update 3) |
| **Domain** | Core (Cross-cutting Messaging) |
| **Knowledge Risk** | LOW — pure C# patterns (`Action<T>`, `WeakReference<T>`, `readonly record struct`). No Unity engine API dependency beyond `Debug.LogException`. |
| **References Consulted** | `docs/engine-reference/unity/VERSION.md` (AOT/IL2CPP section), `docs/engine-reference/unity/deprecated-apis.md` (no deprecated C# APIs) |
| **Post-Cutoff APIs Used** | None — `readonly record struct` is C# 9 (available in .NET Standard 2.1 with Unity 6), `Action<T>` and `WeakReference<T>` are standard .NET |
| **Verification Required** | IL2CPP build must preserve all event `Action<T>` delegate types via `link.xml`. Run a server IL2CPP build and verify no `ExecutionEngineException` on first `Publish<T>()` call. |

## ADR Dependencies

| Field | Value |
|-------|-------|
| **Depends On** | ADR-001 (VContainer DI — Event Bus registers in TinyRiftScope as singleton) |
| **Enables** | ADR-003 (Input System — InputRouter publishes input events), ADR-004 (Time System — receives GameStateChangedEvent) |
| **Blocks** | All Feature and Presentation stories that depend on event-based communication (Damage & Health, VFX, Audio, HUD, Screen Shake, Currency, Level-Up, etc.) |
| **Ordering Note** | Must be Accepted before any cross-system communication is implemented. ADR-001 must be Accepted first (defines the scope Event Bus registers into). |

## Context

### Problem Statement

Without a decoupled messaging layer, every pair of communicating systems requires a direct reference — creating a dense dependency graph where adding a new consumer of an existing event means modifying the producer. The architecture principle "Event Bus as the nervous system" (architecture.md:270) mandates typed publish/subscribe as the primary communication mechanism, but several design decisions remain: single vs split interface, reentrancy handling strategy, the complete event type catalogue, AOT safety for generic delegates under IL2CPP, and the resolution of open questions QQ-02 (profiling threshold) and the GDD split-interface question.

### Current State

- Event Bus GDD (`design/gdd/event-bus.md`) specifies typed `readonly record struct` events, `IEventBus` interface, reentrancy guard at depth 16
- GDD has 3 open questions: split interface, profiling threshold, and Clear() behavior
- Clear() behavior already resolved by ADR-001: explicit per scope
- Architecture doc defines the `IEventBus` interface prototype in the API Boundaries section
- 15+ systems identified as Event Bus producers or consumers in the GDD interactions table
- No central event type catalogue exists — event types are mentioned across multiple GDDs but never listed in one place
- QQ-02 (profiling threshold) must be deferred to prototype measurement

### Constraints

- **AOT safety**: All `Action<T>` variants used at runtime must be preserved via `link.xml`. No runtime `Delegate.Combine`/`Remove` on untyped delegates (casts to `Action<T>` only).
- **Performance**: Zero GC allocation per publish. Event structs passed by `in` (readonly reference).
- **Thread safety**: Not required — all Unity callbacks execute on the main thread.
- **Reentrancy**: Must handle subscriber publishing (nested events) without stack overflow or deadlock.
- **IL2CPP reads**: [`WeakReference` with target tracking](https://learn.microsoft.com/en-us/dotnet/api/system.weakreference-1) works correctly under IL2CPP — it uses the tracking mechanism, not runtime generation.

### Requirements

- Zero heap allocation per `Publish<T>()` call
- A single broken subscriber must never kill the bus or prevent other subscribers from receiving the event
- Reentrant publishes (subscriber publishes while handling an event) must be safe up to depth 16
- Event types must be discoverable in a single document (this ADR's catalogue)
- Consumers that should never publish (e.g., HUD) must not have `Publish()` accessible in their injected interface
- Event types must be defined near their publisher, not in a central file — but a reference catalogue belongs in architecture docs
- `Clear()` is explicit per scope (per ADR-001 — SceneManager calls it on scene transitions)

## Decision

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Event Bus                              │
│                                                             │
│  Subscribers by Type:                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ Action<  │  │ Action<  │  │ Action<  │                  │
│  │ Damage   │  │ Entity   │  │ GameState│  ... (8 types)    │
│  │ DealtEvt>│  │ DiedEvt> │  │ ChgdEvt> │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
│       │              │             │                         │
│       ▼              ▼             ▼                         │
│  Publish<T>(in T) — sync dispatch, per-subscriber try/catch │
│  Reentrancy Guard: ThreadStatic depth counter (max 16)      │
│  WeakReference pruning: dead subscriber detection on publish │
└─────────────────────────────────────────────────────────────┘
       ▲                                         │
       │ Implements                  Implements  │
       │                             │
┌──────────────────┐     ┌──────────────────────┐
│    IEventBus     │     │    ISubscriber       │
│  Publish<T>()   │     │  Subscribe<T>()      │
│  Subscribe<T>() │     │  UnsubscribeAll()    │
│  UnsubscribeAll()│     │                      │
│  Clear()        │     │                      │
└──────────────────┘     └──────────────────────┘
       │                           │
       │ Injected to               │ Injected to
       ▼                           ▼
  Publishers only           Consumer-only systems
  (Game State, Hit          (HUD, Audio, VFX,
   Detect, Damage etc.)      Screen Shake etc.)
```

### Key Interfaces

```csharp
// ── Full interface (publishers + subscribers) ──
public interface IEventBus
{
    void Publish<T>(in T eventData) where T : struct;
    IDisposable Subscribe<T>(Action<T> handler) where T : struct;
    IDisposable Subscribe<T>(object subscriber, Action<T> handler) where T : struct;
    void UnsubscribeAll(object subscriber);
    void Clear();
}

// ── Read-only interface (subscribers only) ──
public interface ISubscriber
{
    IDisposable Subscribe<T>(Action<T> handler) where T : struct;
    IDisposable Subscribe<T>(object subscriber, Action<T> handler) where T : struct;
    void UnsubscribeAll(object subscriber);
}

// ── Concrete implementation ──
public sealed class EventBus : IEventBus
{
    private readonly Dictionary<Type, object> _subscribers = new();
    [ThreadStatic] private static int _publishDepth;
    private bool _clearPending;

    public void Publish<T>(in T eventData) where T : struct
    {
        if (!_subscribers.TryGetValue(typeof(T), out var list)) return;

        _publishDepth++;
        if (_publishDepth > 16)
        {
            Debug.LogError($"[EventBus] Reentrancy depth exceeded 16 — dropping event {typeof(T).Name}");
            _publishDepth--;
            return;
        }

        var handlers = (List<Subscription>)list;
        // Snapshot to avoid CollectionModified during iteration
        Subscription[] snapshot;
        lock (handlers) { snapshot = handlers.ToArray(); }

        foreach (var sub in snapshot)
        {
            try
            {
                sub.Handle(eventData); // internal delegate dispatch
            }
            catch (Exception ex)
            {
                Debug.LogException(ex);
                // continue to next subscriber
            }
        }

        _publishDepth--;

        if (_publishDepth == 0 && _clearPending)
        {
            _subscribers.Clear();
            _clearPending = false;
        }
    }
}

// ── Event type convention ──
// Note: C# 9.0 (Unity .NET Standard 2.1) does not support `record struct`.
// Event types use `readonly struct` with manual constructor + properties instead.
// When the project migrates to C# 10+, these should become `readonly record struct`.
public readonly struct GameStateChangedEvent
{
    public GamePhase Previous { get; }
    public GamePhase Current { get; }
    public GameStateChangedEvent(GamePhase previous, GamePhase current)
    {
        Previous = previous;
        Current = current;
    }
}

public readonly record struct HitEvent(
    EntityId Source,
    EntityId Target,
    Vector3 HitPosition
);

// All event types follow this pattern.
// Full catalogue in Event Type Catalogue section below.
```

### Implementation Guidelines

1. **Subscribe in Awake/Start, never constructor** — VContainer injection happens after construction. `Subscribe<T>()` before `Awake()` is a silent no-op.
2. **Store the IDisposable token** from `Subscribe<T>()` — dispose in `OnDestroy()` or at scope teardown.
3. **Use `Subscribe(object, Action<T>)` overload** as the default — enables `UnsubscribeAll(owner)` for batch cleanup and `WeakReference`-based dead-subscriber pruning.
4. **Never allocate closure lambdas** — `_bus.Subscribe<DamageEvent>((e) => Handle(e))` allocates a closure per call. Use `_bus.Subscribe<DamageEvent>(Handle)` (method group).
5. **Define events near their publisher** — `GameStateChangedEvent` lives near `GameStateManager`; `HitEvent` lives near `HitDetectionService`. Not in a central Events.cs file.
6. **No event batching** — each `Publish<T>()` dispatches immediately. No end-of-frame queue.
7. **VContainer registration** — `EventBus` registers as `IEventBus` and casts to `ISubscriber` for read-only consumers. In `ConfigureFoundation()`:
   ```csharp
   var bus = new EventBus();
   builder.RegisterInstance(bus).As<IEventBus>().As<ISubscriber>();
   ```

### Event Type Catalogue

All events use `readonly struct` (C# 9 compatible — `readonly record struct` when C# 10+ is available) with the `Event` suffix.

| Event Type | Fields | Publisher | Consumers | Layer Boundary |
|-----------|--------|-----------|-----------|---------------|
| `GameStateChangedEvent` | `Previous: GamePhase, Current: GamePhase` | Game State Manager (Foundation) | Input, Time, Scene, Audio, HUD, Wave Spawn, Run Mgr | Foundation → Core/Feature (read) |
| `HitEvent` | `Source: EntityId, Target: EntityId, HitPosition: Vector3` | Hit Detection (Foundation) | Damage & Health (Feature) | Foundation → Feature |
| `DamageDealtEvent` | `Source: EntityId, Target: EntityId, Amount: float, Element: ElementType, IsCrit: bool` | Damage & Health (Feature) | VFX, Audio, Screen Shake, HUD | Feature → Presentation (via read) |
| `EntityDiedEvent` | `EntityId: EntityId, KillerId: EntityId, DeathType: DeathType` | Damage & Health (Feature) | Level-Up, Currency, VFX, Audio, Screen Shake, Analytics, Wave Spawn | Feature → Core/Feature/Presentation |
| `CurrencyChangedEvent` | `CurrencyId: string, Delta: long, NewBalance: long, Source: CurrencySource` | Currency System (Core) | HUD, Analytics | Core → Presentation |
| `LevelUpEvent` | `NewLevel: int, UnlockedRunes: int` | Level-Up System (Feature) | Rune Draft, HUD, VFX, Audio | Feature → Feature/Presentation |
| `ZoneRestoredEvent` | `ZoneId: string, RestoreLevel: int` | World State System (Core) | VFX, Audio | Core → Feature/Presentation |
| `LoreFragmentCollectedEvent` | `FragmentId: string, TotalCollected: int` | Lore System (Core) | HUD, Codex, Analytics | Core → Presentation |

**Future event types** (not in MVP, listed for catalogue completeness):
| Event Type | Publisher | Planned For |
|-----------|-----------|-------------|
| `SkillUnlockedEvent` | Level-Up / Draft | Post-MVP skill tree |
| `AchievementEvent` | Achievement System | Post-MVP achievements |
| `DailyQuestProgressEvent` | Quest System | Post-MVP daily quests |

### AOT Safety

```xml
<!-- link.xml — preserve all Event Bus delegate types -->
<linker>
  <assembly fullname="Assembly-CSharp">
    <type fullname="TinyRift.Runtime.EventBus.GameStateChangedEvent" preserve="all"/>
    <type fullname="TinyRift.Runtime.EventBus.HitEvent" preserve="all"/>
    <type fullname="TinyRift.Runtime.EventBus.DamageDealtEvent" preserve="all"/>
    <type fullname="TinyRift.Runtime.EventBus.EntityDiedEvent" preserve="all"/>
    <type fullname="TinyRift.Runtime.EventBus.CurrencyChangedEvent" preserve="all"/>
    <type fullname="TinyRift.Runtime.EventBus.LevelUpEvent" preserve="all"/>
    <type fullname="TinyRift.Runtime.EventBus.ZoneRestoredEvent" preserve="all"/>
    <type fullname="TinyRift.Runtime.EventBus.LoreFragmentCollectedEvent" preserve="all"/>
  </assembly>
</linker>
```

Additionally, a static AOT-code-generation method forces IL2CPP to compile `Action<T>` for each event type:

```csharp
// AOT type preservation — called once at startup, body never executes
internal static void AotPreserve()
{
    var _1 = new Action<GameStateChangedEvent>(_ => {});
    var _2 = new Action<HitEvent>(_ => {});
    var _3 = new Action<DamageDealtEvent>(_ => {});
    var _4 = new Action<EntityDiedEvent>(_ => {});
    var _5 = new Action<CurrencyChangedEvent>(_ => {});
    var _6 = new Action<LevelUpEvent>(_ => {});
    var _7 = new Action<ZoneRestoredEvent>(_ => {});
    var _8 = new Action<LoreFragmentCollectedEvent>(_ => {});
}
```

### Open Questions Resolved

| ID | Question | Resolution |
|----|----------|-----------|
| GDD Q1 | Split interface? | **Yes** — `IEventBus` (full) + `ISubscriber` (read-only). VContainer injects `ISubscriber` to consumer-only systems (HUD, Audio, VFX, Screen Shake) to prevent accidental publishes. |
| QQ-02 | Profiling threshold? | **Deferred to prototype** — measure actual dispatch times during first integration test, then set threshold in `UNITY_EDITOR || DEVELOPMENT_BUILD` profiling code. Default suggestion: 0.5ms per handler. |
| QQ-03 | Clear() automatic? | **Resolved by ADR-001** — explicit per scope. `SceneManager` calls `EventBus.Clear()` on scene transitions. |

## Alternatives Considered

### Alternative 1: Single IEventBus (no split interface)

- **Description**: One interface with `Publish`, `Subscribe`, `UnsubscribeAll`, `Clear`. All systems get the same interface.
- **Pros**: Simpler API surface, fewer types to maintain.
- **Cons**: Any consumer with an `IEventBus` reference can accidentally call `Publish<T>()`. A HUD bug could publish fake events. No compiler-level protection.
- **Rejection Reason**: VContainer makes the split trivial — registering the same instance under two interfaces costs nothing. The protection against accidental misuse is worth the trivial API surface increase.

### Alternative 2: Centralized Events.cs file

- **Description**: All event types defined in a single file (`Assets/_TinyRift/Runtime/Foundation/EventBus/Events.cs`).
- **Pros**: Single file to read for the full event catalogue.
- **Cons**: Every event type change requires editing a central file — violates cohesion (event should live near its publisher). Merge conflicts in a shared file.
- **Rejection Reason**: Defining events near their publisher is better separation of concerns. This ADR serves as the discoverable reference catalogue instead.

### Alternative 3: Deferred dispatch (event queue processed end-of-frame)

- **Description**: `Publish<T>()` queues events; a flush pass at end-of-frame dispatches all queued events.
- **Pros**: Predictable dispatch timing, easier to debug (single dispatch point per frame).
- **Cons**: Gameplay events (damage → health change → death → XP) must resolve atomically within a single frame. Deferred dispatch breaks this — damage registered but health not updated until end of frame.
- **Rejection Reason**: Gameplay correctness requires immediate dispatch. Damage → health → death → XP must resolve atomically per the combat rules.

## Consequences

### Positive

- Split interface (`ISubscriber`) prevents accidental publishes by consumer systems — compiler-enforced safety
- All event types catalogued in one place (this ADR) while keeping type definitions near their publishers
- Reentrancy guard at depth 16 prevents stack overflow from accidental publish loops
- Per-subscriber try/catch ensures one broken subscriber never kills the bus
- Zero GC allocation per publish (structs passed by `in`, no closures)
- WeakReference pruning handles destroyed subscribers gracefully

### Negative

- No ordering guarantees between subscribers — systems that need ordered processing must use pipeline-pattern events (`BeforeX`, `X`, `AfterX`)
- Reentrancy buffer adds minor complexity (depth tracking, flush logic)
- Clear() deferral (waits for publish cycle completion) adds edge case: subscribers added between flag and actual clear may miss events
- AOT preservation requires manual `link.xml` and static method — easy to forget when adding new event types

### Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| Developer adds new event type but forgets AOT preservation | Medium | High — IL2CPP build fails at runtime with `ExecutionEngineException` | Add `link.xml` validation step to CI: grep for `readonly record struct.*Event` and cross-check against `link.xml` entries |
| Closure lambda in Subscribe creating GC allocations from hot path | Medium | Medium — frame rate hitch under heavy combat | Enforce in code review: `Subscribe<T>(Handle)` method group only. Add `[Pure]`-style comment convention. |
| Event struct grows beyond 32 bytes (copy cost) | Low | Low — `in` parameter passes by readonly reference; no copy on publish | Review event struct fields during Feature implementation. Keep under 64 bytes. |

## Performance Implications

| Metric | Before | Expected After | Budget |
|--------|--------|---------------|--------|
| CPU (per publish) | N/A | ~0.001ms for 5 handlers (delegate dispatch) | 0.01ms (100 publishes/frame @ 5 handlers) |
| Memory (per subscribe) | N/A | ~48 bytes (Action<T> delegate + Subscription wrapper) | Negligible — one-time cost |
| GC (per publish) | N/A | 0 — no allocations (struct by `in`, no closures) | 0 |
| Profiling threshold | N/A | TBD — measure during prototype | Suggestion: 0.5ms/handler |

## Migration Plan

1. Create `EventBus.cs` implementing both `IEventBus` and `ISubscriber` in `Assets/_TinyRift/Runtime/Foundation/EventBus/`
2. Create event type files near their publishers (one file per event type)
3. Add `link.xml` entries for all 8 event types
4. Add AOT preservation static method
5. Register in TinyRiftScope.ConfigureFoundation() as both interfaces
6. Update SceneManager to call `IEventBus.Clear()` and `IPoolManager.ClearAll()` on scene transitions
7. Add CI validation step for link.xml completeness

**Rollback plan**: Replace `IEventBus`/`ISubscriber` with a single `IEventBus` reference everywhere. The API surface change is mechanical (just remove the `ISubscriber` cast, inject `IEventBus` to all consumers). No behavior change.

## Validation Criteria

- [ ] `Publish<T>()` with 0 subscribers is a silent no-op (no allocations)
- [ ] `Publish<T>()` with N subscribers invokes all N handlers in sequence
- [ ] Subscriber exception does not prevent other subscribers from receiving the event
- [ ] Reentrant publish (nested depth < 16) is queued and flushed after current cycle
- [ ] Reentrant publish at depth 16 logs error and drops the event
- [ ] `Clear()` during publish cycle is deferred until cycle completes
- [ ] Subscriber destroyed without unsubscribing is silently pruned (WeakReference check)
- [ ] IL2CPP build fires all 8 event types without `ExecutionEngineException`
- [ ] `ISubscriber`-injected system cannot call `Publish<T>()` (compile-time check)
- [ ] No `new Action<T>(...)` or closure lambdas in Subscribe calls (code review check)

## GDD Requirements Addressed

| GDD Document | System | Requirement | How This ADR Satisfies It |
|-------------|--------|-------------|--------------------------|
| `design/gdd/event-bus.md` | Event Bus | Typed publish/subscribe with `readonly record struct` events | Full IEventBus + ISubscriber API defined, reentrancy guard, Clear() policy |
| `design/gdd/event-bus.md` | Event Bus | "registered as a VContainer singleton in TinyRiftScope" | Per ADR-001 — EventBus registers in TinyRiftScope Foundation layer |
| `design/gdd/game-state-manager.md` | Game State | GState publishes state transitions via Event Bus | `GameStateChangedEvent` defined, publisher pattern established |
| `design/gdd/hit-detection.md` | Hit Detection | Hit events published to Event Bus | `HitEvent` defined with EntityId fields |
| `design/gdd/damage-health-system.md` | Damage & Health | Damage events, death events | `DamageDealtEvent`, `EntityDiedEvent` defined |
| `design/gdd/currency-system.md` | Currency | Currency change events | `CurrencyChangedEvent` defined |
| `design/gdd/level-up-system.md` | Level-Up | Level-up event triggers draft | `LevelUpEvent` defined |
| `design/gdd/world-state-system.md` | World State | Zone restored event | `ZoneRestoredEvent` defined |
| `design/gdd/lore-system.md` | Lore | Lore fragment collection event | `LoreFragmentCollectedEvent` defined |
| 12+ consumer GDDs (Audio, VFX, Screen Shake, HUD, etc.) | Various | Subscribe to game events | ISubscriber pattern enables consumer-only injection |

> Foundational decision — this ADR enables all cross-system communication. Every system that publishes or subscribes to events depends on this contract.

## Related

- ADR-001: VContainer DI Architecture — defines TinyRiftScope that registers EventBus
- `architecture.md:172-182` — IEventBus prototype interface (this ADR finalizes)
- `architecture.md:270` — "Event Bus as the nervous system" architecture principle
- `design/gdd/event-bus.md` — GDD that motivated this ADR
