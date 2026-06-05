# Event Bus

> **Status**: Drafted (awaiting design review)
> **Creative Director Review (CD-GDD-ALIGN)**: APPROVED 2026-05-26
> **Author**: game-designer + technical-director
> **Last Updated**: 2026-05-26
> **Implements Pillar**: P3 (Snappy Sessions) — decoupled event dispatch prevents systems from blocking each other

## Overview

The Event Bus is a typed publish/subscribe message bus that decouples event producers from event consumers across all layers of the game. Instead of systems calling each other directly (producing tight coupling), event producers publish messages of a known type, and any number of consumers can subscribe to receive those messages without knowing who produced them. The bus owns no game data, performs no game logic, and imposes no ordering guarantees between subscribers — it is a pure routing layer. Without it, systems like Damage & Health, Currency, VFX, Audio, and Screen Shake would need direct references to each other, creating a dependency graph that is brittle and hard to extend.

## Player Fantasy

The Event Bus has no direct player fantasy — players never interact with it consciously. What they feel is the absence of friction: damage numbers appear as hits land, currency updates arrive instantly, VFX plays without delay, and adding a new system never breaks existing ones. The event bus is the game's silent postal service — invisible, but nothing works without it.

## Detailed Design

### Core Rules

1. The Event Bus is a typed publish/subscribe message router. It owns no game data and performs no game logic.
2. Events are defined as `readonly record struct` types with the suffix `Event` (e.g., `DamageDealtEvent`). Each event type is defined near its publisher, not in a central file.
3. Event types must use `readonly record struct` — never `class`. This guarantees zero GC allocation per publish under IL2CPP.
4. Thread safety is not required — all Unity callbacks execute on the main thread. The bus uses no locks.
5. The bus is registered as a VContainer singleton in `TinyRiftScope` and persists across scene loads.
6. Stateless — no state machine, no history, no queues (beyond the reentrancy safety buffer).

**API Surface:**
```csharp
public interface IEventBus
{
    void Publish<T>(in T eventData) where T : struct;
    IDisposable Subscribe<T>(Action<T> handler) where T : struct;
    IDisposable Subscribe<T>(object subscriber, Action<T> handler) where T : struct;
    void UnsubscribeAll(object subscriber);
    void Clear();
}
```

| Method | Purpose |
|--------|---------|
| `Publish<T>(in T)` | Fires an event. All subscribers to `T` are invoked immediately, in registration order. |
| `Subscribe<T>(Action<T>)` | Registers a handler. Returns an `IDisposable` token — disposing it unsubscribes. |
| `Subscribe<T>(object, Action<T>)` | Registers with owner reference. Enables `UnsubscribeAll(owner)` for batch cleanup. |
| `UnsubscribeAll(object)` | Removes all subscriptions for a given subscriber. Called from base class `OnDestroy()`. |
| `Clear()` | Removes all subscriptions. Called during scene transitions as a safety net. |

**Publish Timing — Immediate Dispatch:**
- `Publish<T>()` invokes all subscribers synchronously within the current frame. This is required for gameplay events (damage → health change → death → XP must resolve atomically).
- No events are queued for end-of-frame. The bus has no deferred dispatch lane.
- If a subscriber throws, the exception is caught per-subscriber (see Error Handling) — other subscribers still receive the event.

**Reentrancy Guard:**
- Tracks a per-thread publish depth counter (`[ThreadStatic] private static int _publishDepth`).
- If a subscriber calls `Publish` while inside a publish cycle, the nested event is queued in a frame-local `List<T>` buffer.
- Nested events are flushed after the current publish cycle completes, up to a maximum chain depth of 16.
- If depth exceeds 16, an error is logged and further nested events are dropped. This prevents stack overflow from accidental infinite publish loops.

**Error Handling:**
- Each subscriber invocation is wrapped in `try/catch`. On exception: `Debug.LogException(ex)`, then continue to next subscriber.
- A broken subscriber never kills the bus or blocks other subscribers.
- Null/collected subscribers are detected before invocation — if `handler` is null or `handler.Target` is a `WeakReference` whose target has been GC'd, the handler is silently pruned from the subscription list.

**Performance:**
- `Publish<T>()` with `T : struct` and `in` parameter produces zero heap allocation per call.
- `Subscribe` allocates one `Action<T>` delegate and (with the owner overload) one `WeakReference<T>`. This is a one-time setup cost.
- Subscriber iteration uses a snapshot of the handler list to avoid `CollectionModified` exceptions.
- Profiling hooks (subscriber count per type, events per frame, slow-handler warnings) are available in `UNITY_EDITOR || DEVELOPMENT_BUILD` only — stripped from release builds.

**IL2CPP Compatiblity:**
- All `Action<T>` variants used at runtime must be visible to AOT. A `link.xml` entry preserves all `_TinyRift.Runtime.EventBus` event types.
- The `Dictionary<Type, object>` pattern for storing handler lists by event type is safe under IL2CPP when the concrete `Action<T>` is accessed via `as Action<T>` cast (not `Delegate.Combine`/`Remove` on untyped delegates).

### Subscriber Model

**Lifetime:**
- Subscribe in `Awake()` or `Start()` — never in `OnDestroy()` or constructor.
- Store the returned `IDisposable` token; dispose in `OnDestroy()`.
- The `Subscribe(object subscriber, ...)` overload stores a `WeakReference<T>` to the subscriber. If the subscriber is destroyed without disposing (e.g., from a scene unload), the bus silently prunes dead handlers on the next publish.
- `Clear()` is called on scene transition as a safety net — all subscribers are removed; systems re-subscribe in their `Start()`.

**Ordering:**
- Subscribers are invoked in registration order.
- **No ordering guarantees are provided.** If System A must process before System B for the same event type, the systems should use a pipeline pattern (e.g., `BeforeDamageDealtEvent`, `DamageDealtEvent`, `AfterDamageDealtEvent`) rather than depending on subscription sequence.

**Anti-patterns:**
- ❌ Never allocate a closure lambda as a subscriber (`_bus.Subscribe<DamageEvent>((e) => Handle(e))` allocates a closure per call). Always pass a concrete method reference.
- ❌ Never subscribe/unsubscribe in hot paths (per-frame `Update()`).
- ❌ Never use the bus for request/response patterns — it is fire-and-forget only.

### Interactions with Other Systems

The Event Bus is consumed by every system that produces or consumes events. This section lists only the interfaces — the event type catalogue is defined in the "Core Rules" message type convention, not here.

| System | Relationship | Direction | Events |
|--------|-------------|-----------|--------|
| Game State Manager | Producer | GState → Event Bus | `GameStateChangedEvent(Previous, Current, Context)` |
| Damage & Health | Producer + Consumer | Bidirectional | Producers: `DamageDealtEvent`, `EntityDiedEvent`. Consumers: subscribes to `HitEvent` for damage processing. |
| Hit Detection | Producer | HitDetect → Event Bus | `HitEvent(Source, Target, HitPosition)` |
| Level-Up System | Consumer | Event Bus → LevelUp | `EntityDiedEvent` (XP accumulation) |
| Currency System | Producer + Consumer | Bidirectional | `CurrencyChangedEvent`. Consumer of `EntityDiedEvent` (currency drops). |
| VFX System | Consumer | Event Bus → VFX | `DamageDealtEvent`, `EntityDiedEvent`, `ZoneRestoredEvent` |
| Audio System | Consumer | Event Bus → Audio | `GameStateChangedEvent`, `DamageDealtEvent`, `EntityDiedEvent` |
| Screen Shake | Consumer | Event Bus → ScreenShake | `DamageDealtEvent` (player hit), `EntityDiedEvent` (boss death) |
| World State | Producer | WorldState → Event Bus | `ZoneRestoredEvent(ZoneId, RestoreLevel)` |
| Analytics | Consumer | Event Bus → Analytics | `GameStateChangedEvent`, `EntityDiedEvent`, `CurrencyChangedEvent`, `LevelUpEvent` |
| Save System | Consumer | Event Bus → Save | `GameStateChangedEvent(HeroCamp, Defeat, Victory)` |
| Run Manager | Consumer | Event Bus → RunMgr | `GameStateChangedEvent(InRun → non-InRun)` |
| Wave Spawning | Consumer | Event Bus → WaveSpawn | `GameStateChangedEvent(BossActive)` |

*Note: Systems that subscribe and immediately publish a different event type (e.g., Hit Detection publishes a `HitEvent`, which Damage & Health subscribes to and then publishes `DamageDealtEvent`) create event chains. These are valid and expected — the reentrancy guard handles nested publishes safely.*

## Formulas

None. The Event Bus is a pure routing layer with no mathematical calculations. All behavior is governed by the publish/subscribe API defined in Section C.

## Edge Cases

- **If `Publish<T>()` is called with no subscribers for `T`**: Silent no-op. The bus checks `_subscribers.ContainsKey(typeof(T))` before allocating any iterators.
- **If a subscriber calls `Publish` from inside a handler (re-entrancy)**: The nested publish is queued in a frame-local buffer. Queue depth is capped at 16. If depth exceeds 16, the event is dropped and an error is logged. This prevents stack overflow from accidental infinite publish loops.
- **If a subscriber throws an exception during handler invocation**: The exception is caught by `try/catch`, logged via `Debug.LogException(ex)`, and processing continues to the next subscriber. One broken subscriber never kills the bus.
- **If a subscriber's `MonoBehaviour` is destroyed before unsubscribing**: If the `Subscribe(object, Action<T>)` overload was used, the bus's `WeakReference` is checked before invocation. If the target is null (GC'd or destroyed), the handler is silently pruned. If the simple `Subscribe<T>(Action<T>)` was used without the owner reference, the delegate keeps the subscriber alive (memory leak risk — the owner-ref overload is the recommended default).
- **If `Clear()` is called while a publish cycle is in progress**: The clear is deferred until the current publish cycle completes. `Clear()` sets a `_clearPending` flag; the next publish cycle after completion performs the actual clear. This prevents modifying the subscription list during iteration.
- **If `Dispose()` is called twice on the same subscription token**: Safe — `IDisposable` pattern: the token tracks whether it has been disposed. Second call is a no-op.
- **If `Subscribe<T>()` is called with the same handler instance twice**: The handler is registered twice and will be invoked twice per publish. The bus does not deduplicate handlers. This is intentional — the caller controls registration.
- **If `Subscribe` is called in a `MonoBehaviour` constructor** (before `Awake`): The bus is not yet injected (VContainer injection happens after construction). The call silently fails — the subscriber never receives events. Systems must subscribe in `Awake()` or `Start()`.
- **If 100+ events of the same type are published in a single frame** (e.g., rapid hits from an orbit skill on a large enemy group): Each `Publish<T>()` call iterates the subscriber list once. For a subscriber list of 5 handlers, 100 publishes = 500 handler invocations. At 60 FPS, this is well within budget (~0.01ms at C# delegate dispatch speeds). No event batching is required.
- **If an event struct exceeds 32 bytes** (e.g., carries a large payload): The `in T eventData` parameter passes the struct by read-only reference, avoiding a copy on the stack. The bus does not store or clone event data beyond the scope of the publish call.
- **If a scene unloads while a `Publish` is in flight**: The bus survives scene loads. Subscribers in the unloading scene are destroyed before the scene unload completes. If they were subscribed via `Subscribe(object, ...)`, the `WeakReference` check catches the destruction on the next publish. If purely through `Subscribe<T>(Action<T>)`, the delegate holds a strong reference — the subscriber object is not destroyed until the delegate is collected (the bus still holds it). This is why `UnsubscribeAll` should be called in `OnDestroy()`.
- **If two event types have the same structure but different purposes** (e.g., `PlayerDiedEvent` and `BossDiedEvent` both contain `EntityId Id`): They are separate types. The bus routes by type — `PlayerDiedEvent` subscribers never receive `BossDiedEvent` events. No structural comparison is performed.

## Dependencies

**Upstream (this system depends on these)**: None. Event Bus is a Foundation-layer system with zero upstream dependencies. It requires only the C# runtime and Unity engine lifecycle (MonoBehaviour).

**Downstream (systems that depend on this one)**: Every system that produces or consumes events — see "Interactions with Other Systems" table in Section C for the full list. Of the 35 MVP systems, approximately 15 use the Event Bus as either producer, consumer, or both.

*Hard = system cannot function without this. Soft = enhanced by this but works without it. The Event Bus is a Hard dependency for any system that publishes or subscribes to events — without it, those systems must use direct coupling (method calls between systems).*

## Tuning Knobs

| Knob | Default | Range | Effect When Max | Effect When Min | Owner |
|------|---------|-------|-----------------|-----------------|-------|
| Re-entrancy guard depth | 16 | 1–64 | Allows deeper publish chains before dropping events (safer for complex event chains) | Catches shallow infinite loops faster (lower tolerance for accidental recursion) | Event Bus |

No other tuning knobs. The bus is a fixed routing layer — message types, subscription patterns, and dispatch behavior are hard-coded design decisions.

## Visual/Audio Requirements

The Event Bus itself has no visual or audio output — it is a pure data routing layer. The events it carries trigger visual and audio responses in downstream systems:

| Event Type | Visual Response Owner | Audio Response Owner |
|-----------|----------------------|---------------------|
| `GameStateChangedEvent` | Loading/Transition (ink-stamp, fade, parchment-tear per art bible Section 6.3) | Audio System (music crossfade, state-change SFX) |
| `DamageDealtEvent` | VFX System (hit spark, element-specific VFX per art bible Section 8), Screen Shake | Audio System (hit SFX per element) |
| `EntityDiedEvent` | VFX System (death VFX, loot shimmer) | Audio System (death SFX per enemy type) |
| `ZoneRestoredEvent` | VFX System (color sweep per art bible Section 7.6.1), Post-Processing (color grading shift per 7.3.2) | Audio System (restoration harmonic) |
| `CurrencyChangedEvent` | HUD (currency counter tick) | Audio System (coin clink) |
| `LevelUpEvent` | VFX System (level-up burst), HUD (level indicator change) | Audio System (level-up chime) |

The Event Bus publishers these events; the above systems own the feedback.

## UI Requirements

The Event Bus has no direct UI. UI systems are consumers of events published through the bus:
- HUD subscribes to `CurrencyChangedEvent`, `LevelUpEvent`, `DamageDealtEvent` (damage numbers)
- Draft Panel is triggered by `LevelUpEvent` (shows draft choices)
- Victory/Defeat screens respond to `GameStateChangedEvent`

No per-event UI is owned by the Event Bus itself.

## Open Questions

| Question | Options | Impact | Target Resolution |
|----------|---------|--------|-------------------|
| Should there be a read-only `IEventBus` interface for consumers that only subscribe and never publish? | Yes (separate `ISubscriber<T>` or `IReadOnlyEventBus`) vs. No (single `IEventBus` for all) | Prevents misuse — a HUD system VContainer-injected with `ISubscriber` can never accidentally publish | During implementation of first L3 consumer |
| What profiling threshold should trigger a "slow handler" warning? | 1ms vs. 0.5ms vs. configurable | Controls noise in dev-build profiling output; too low = spam, too high = misses slow handlers | During prototype (measure actual dispatch times) |
| Should `Clear()` be called automatically on `SceneManager.sceneLoaded` or should each scene's lifetime scope call it explicitly? | Automatic (hook in EventBus.Start()) vs. Explicit (each scope calls Clear()) | Automatic reduces boilerplate but couples bus to scene lifecycle; explicit is cleaner DI but requires every scope to remember | During VContainer scope design |
