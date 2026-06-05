# Story 002: Event Bus Core

- **Epic**: Foundation Infrastructure
- **System**: Event Bus
- **Type**: Logic
- **Priority**: P0 — Blocking (GState and all other systems publish/subscribe)
- **Estimate**: 4h
- **Status**: Complete
- **Last Updated**: 2026-06-02

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-PLACEHOLDER-007` | Event Bus supports typed readonly record struct events | ✅ ADR-002 |
| `TR-PLACEHOLDER-008` | Event Bus has split interface (IEventBus + ISubscriber) | ✅ ADR-002 |
| `TR-PLACEHOLDER-009` | Subscribe returns IDisposable token for unsubscribe | ✅ ADR-002 |
| `TR-PLACEHOLDER-010` | Event Bus protects against reentrant publish up to depth 16 | ✅ ADR-002 |
| `TR-PLACEHOLDER-011` | Per-subscriber try/catch, one fault never kills other subscribers | ✅ ADR-002 |
| `TR-PLACEHOLDER-012` | Zero GC allocation per publish (no closure lambdas) | ✅ ADR-002 |
| `TR-PLACEHOLDER-013` | AOT/IL2CPP compatible via link.xml delegate preservation | ✅ ADR-002 |

## ADR Guidance

**ADR-002 (Event Bus Contract):**
- Typed `readonly record struct` for all event types
- Split interface: `IEventBus` (Publish, Subscribe generic) + `ISubscriber` (Subscribe with owner-ref)
- Return `IDisposable` subscription token
- Reentrancy guard: max depth 16, `Publish` throws on overflow
- Per-subscriber try/catch: log exception, continue to next subscriber
- Zero GC allocation: cache `Action<T>` delegates, forbid closure allocation
- AOT: preserve delegate types in `link.xml`
- Subscribe in `Awake`/`Start`, never in constructor
- Expose `Clear()` to reset all subscriptions (deferred during active publish)
- `ISubscriber` overload: `Subscribe(IOwner owner, Action<T> handler)` where `IOwner` is the subscribing system

**Control Manifest (Foundation Layer):**
- Subscribe in Awake/Start, not constructor — source: ADR-002
- Store IDisposable token returned by Subscribe — source: ADR-002
- Use owner-ref overload (IOwner) — source: ADR-002
- No closure lambdas in Subscribe calls — source: ADR-002
- Never use single IEventBus interface (no monolithic event bus) — source: ADR-002
- Never centralize events (no global Events.cs) — source: ADR-002

## Description

Implement the Event Bus core. All event types are `readonly record struct`. The bus provides a typed publish/subscribe mechanism with per-subscriber error isolation, reentrancy protection, and zero GC allocation. Two interfaces separate the publishing role from the subscribing role.

The `ISubscriber` interface offers an `IOwner` overload that ties subscription lifetime to the subscribing system's lifetime.

## Design

```csharp
// Event contract: all events are readonly record structs
public readonly record struct GameStateChanged(GamePhase Previous, GamePhase Current);

// Publishing role
public interface IEventBus
{
    void Publish<T>(T eventData) where T : struct;
    IDisposable Subscribe<T>(Action<T> handler) where T : struct;
}

// Subscribing role (adds owner-ref for lifetime management)
public interface ISubscriber
{
    IDisposable Subscribe<T>(object owner, Action<T> handler) where T : struct;
}

// Owner marker — attaching systems implement this
public interface IOwner { }
```

### Reentrancy Guard

- `_publishDepth` counter incremented on enter, decremented on exit
- If depth > 16, throw `EventBusReentrancyException`
- Counter is per-bus-instance (thread safety not needed — Unity single-threaded)

### Per-Subscriber Error Isolation

```csharp
foreach (var sub in _subscribers)
{
    try { sub.handler(eventData); }
    catch (Exception ex) { Debug.LogException(ex); }
}
```

### Zero-Alloc

- Store `Action<T>` delegates directly in a list per event type
- Maintain a `Dictionary<Type, object>` mapping event type → subscriber list
- Subscribe returns a `SubscriptionToken` (struct implementing `IDisposable`) that removes itself from the list
- NO closure allocations — forbid patterns like `bus.Subscribe<X>(e => { ... })` in production code

### Clear()

- Sets a `_clearing` flag; during active `Publish`, defers the clear
- After `Publish` completes, performs the deferred clear
- Double-clear guard (idempotent)

### AOT / link.xml

Preserve all event handler delegate types:
```xml
<linker>
  <assembly fullname="Assembly-CSharp">
    <type fullname="*" preserve="methods"/>
  </assembly>
</linker>
```

## Acceptance Criteria

1. **Typed publish/subscribe**: `bus.Publish(new MyEvent(42))` reaches all subscribers of `MyEvent`.
2. **Split interface**: `IEventBus` has `Publish` and `Subscribe`; `ISubscriber` has owner-ref `Subscribe`.
3. **Subscription token**: `Subscribe` returns `IDisposable`; disposing it removes the subscription.
4. **Unsubscribe isolation**: After disposing token, handler no longer receives events.
5. **Reentrancy depth limit**: Publishing an event whose handler publishes another event increments depth. At depth 17, throws `EventBusReentrancyException`.
6. **Reentrancy within limit**: Depth 16 succeeds (16 nested publishes).
7. **Per-subscriber isolation**: If subscriber A throws, subscriber B still receives the event.
8. **Zero allocated bytes**: `Publish` with 3 subscribers allocates 0 bytes on GC (measured via `GC.GetAllocatedBytesForCurrentThread()` or profiler marker).
9. **Clear removes all subscriptions**: After `Clear()`, no subscribers receive events.
10. **Clear during publish is deferred**: Calling `Clear()` inside a handler takes effect after current `Publish` completes (not immediately).
11. **Clear is idempotent**: Calling `Clear()` twice is safe (no exception).
12. **IOwner overload works**: `Subscribe(owner, handler)` ties subscription lifetime to owner; owner disposal triggers automatic unsubscribe.
13. **Different event types are independent**: Subscribers for `EventA` don't receive `EventB`.
14. **Clear during publish uses snapshot**: When `Clear()` is called inside a handler, the current publish iteration continues with a snapshot of the subscriber list taken at publish start. Remaining subscribers still receive the event. New subscribers added after `Clear()` are not invoked in the current publish cycle.

## Test Evidence Path

- `Assets/_TinyRift/Tests/EditMode/EventBus/EventBusCoreTests.cs`
- All 14 acceptance criteria as individual test methods
- Zero-alloc test uses `Assert.That(allocated, Is.Zero)` or equivalent
- Reentrancy test constructs nested publish graph explicitly
- Test must NOT depend on GState or Time System

## Dependencies

- **None** — pure C# data structures, no Unity engine runtime dependencies beyond `Debug.LogException`

## Conventions (Enforced by Code Review, Not Automated Tests)

- **No closure lambdas**: `int x = 5; bus.Subscribe<EventA>(e => { _ = x; })` captures local variable `x`, allocating a closure. All `Subscribe` calls must use static methods or instance methods, not lambdas that capture locals.
- **Subscribe in Awake/Start, not constructor.**

## GDD Deviations (M0 Scope Decisions)

| GDD Spec | Story Decision | Rationale |
|----------|---------------|-----------|
| `in T eventData` parameter | `T eventData` (by value) | By-value is simpler; `in` is a micro-optimization for large structs. Event structs are small (typically 2-3 fields). |
| Nested events queued and flushed after current publish | Throw at depth 17 | Queue-and-flush is silent about infinite recursion bugs. Depth-throw surfaces them immediately. Safer for M0. |
| `IEventBus.UnsubscribeAll(object owner)` | Deferred (not in M0 scope) | Individual `IDisposable` token disposal suffices. Batch unsubscribe adds complexity without immediate need. |
| `WeakReference` pruning for dead subscribers | Deferred (not in M0 scope) | Subscriber lifetime is managed via `IOwner`/`IDisposable` tokens. WeakReference adds GC complexity without immediate benefit. |

## Risks

- **HIGH**: IL2CPP delegate stripping. Mitigation: link.xml with delegate-type preservation patterns documented in ADR-002.
- **MEDIUM**: Must measure zero-allocation reliably. Mitigation: use `[AllocatorMonitor]` or manual `GC.GetAllocatedBytesForCurrentThread()` before/after measurement.

## Completion Notes
**Completed**: 2026-06-02
**Criteria**: 14/14 passing (all auto-verified via unit tests)
**Deviations**: `in T eventData` used in Publish (matches ADR, deviates from story's by-value note — functionally equivalent for small structs)
**Test Evidence**: Logic: `Assets/_TinyRift/Tests/EditMode/EventBus/EventBusCoreTests.cs` (14 tests, all passing)
**Code Review**: Pending
