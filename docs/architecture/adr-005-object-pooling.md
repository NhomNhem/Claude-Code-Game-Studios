# ADR-005: Object Pooling Strategy

## Status

Accepted

## Date

2026-06-01

## Decision Makers

user + agents (technical-director, architecture-decision skill)

## Summary

Wrap Unity's built-in `UnityEngine.Pool.ObjectPool<T>` in a `PoolManager` service that manages prefab-keyed pools with configurable pre-warm counts via `PoolProfile` ScriptableObjects. All pooled objects implement `IPoolable` for lifecycle callbacks. AOT preservation via static type forcing method. `ClearAll()` called explicitly on scene transitions (per ADR-001 scope resolution).

## Engine Compatibility

| Field | Value |
|-------|-------|
| **Engine** | Unity 6000.3.11f1 (Unity 6 Update 3) |
| **Domain** | Core (Object Pooling) |
| **Knowledge Risk** | MEDIUM — `UnityEngine.Pool.ObjectPool<T>` is available since Unity 2021 and confirmed present in Unity 6. No API changes reported. However, IL2CPP stripping of generic `ObjectPool<T>` is a common pitfall. |
| **References Consulted** | `docs/engine-reference/unity/VERSION.md` (AOT section), `docs/engine-reference/unity/deprecated-apis.md` (no ObjectPool deprecation) |
| **Post-Cutoff APIs Used** | None — `ObjectPool<T>` is stable API |
| **Verification Required** | IL2CPP build must compile all `ObjectPool<T>` concrete types without stripping. Run a server IL2CPP build that calls `PoolManager.Get<T>()` for each pool type. |

## ADR Dependencies

| Field | Value |
|-------|-------|
| **Depends On** | ADR-001 (TinyRiftScope registration + scope lifecycle — PoolManager is app-scoped, ClearAll() is explicit) |
| **Enables** | All Feature systems that need pooled objects (Orbit Combat, Burst Skill, Wave Spawning, VFX, Damage & Health) |
| **Blocks** | Combat system implementation — projectile and enemy spawning depend on pools |
| **Ordering Note** | Must be implemented before any combat Feature story. PoolProfile ScriptableObjects must be created alongside Scene Manager scene definitions. |

## Context

### Problem Statement

Without object pooling, every projectile fired, enemy spawned, or VFX burst allocates a new `GameObject` (heap allocation) and eventually triggers a GC collection when destroyed — causing frame hitches under dense combat. Unity's built-in `ObjectPool<T>` solves the allocation problem, but we need a manager that routes prefab requests to the correct pool, handles pre-warming via configurable profiles, survives IL2CPP stripping, and respects the app-scoped lifecycle (ClearAll explicit, not scope-disposal based).

### Current State

- GDD specifies PoolManager wrapping `UnityEngine.Pool.ObjectPool<T>`
- PoolManager scope already resolved by ADR-001: app-scoped in TinyRiftScope, explicit ClearAll() on scene transitions
- GDD updated to reflect app-scoped + explicit ClearAll()
- No PoolManager implementation exists yet
- Template has its own `MonsterPool`/`DropPool` — separate concern

### Constraints

- **Template boundary**: Our PoolManager handles `Assets/_TinyRift/` content only. Template's `MonsterPool`/`DropPool` continue to serve template scenes.
- **No custom pool class**: Wrap `UnityEngine.Pool.ObjectPool<T>` — do not write a custom pool from scratch.
- **AOT safety**: Every concrete `ObjectPool<T>` used at runtime must be forced through IL2CPP compilation via a static reference method.
- **Scene transitions**: `PoolManager.ClearAll()` is called explicitly by SceneManager (per ADR-001). Pools are NOT cleaned up by scope disposal.

### Requirements

- Zero GC allocation per `Get()`/`Return()` on hot path (allocations happen at pool creation and growth only)
- Configurable pre-warm counts per scene via `PoolProfile` ScriptableObject
- Pool auto-growth when exhausted (configurable batch size, with warning)
- `IPoolable` lifecycle interface for spawn/despawn callbacks
- Externally-destroyed objects must not break the pool (null entry pruning)
- IL2CPP AOT preservation for all concrete pool types
- PoolManager registered as singleton in TinyRiftScope Foundation layer

## Decision

### Architecture

```
                   PoolProfile SO (per scene)
                   ├── Projectile: prewarm=50, max=100, grow=5
                   ├── Enemy: prewarm=30, max=50, grow=5
                   ├── VfxController: prewarm=100, max=200, grow=10
                   └── DamageNumber: prewarm=30, max=60, grow=5

                   PoolManager (TinyRiftScope singleton)
                   ├── Dictionary<GameObject, ObjectPool<T>>
                   │   ├── projectilePrefab → ObjectPool<Projectile>
                   │   ├── enemyPrefab → ObjectPool<Enemy>
                   │   ├── vfxPrefab → ObjectPool<VfxController>
                   │   └── damageNumPrefab → ObjectPool<DamageNumber>
                   │
                   │  Methods:
                   │    Get<T>(prefab, pos, rot) → T
                   │    Return<T>(instance)
                   │    EnsureCapacity(prefab, count)
                   │    ClearAll()
                   │    GetReport() → PoolReport (dev builds only)
                   │
                   └── Pre-warms from PoolProfile on scene transition
                        (called by SceneManager after ClearAll)

                   Pooled Objects (implement IPoolable)
                   ├── Projectile: OnSpawned() → reset state, launch
                   │              OnDespawned() → clear state
                   ├── Enemy: OnSpawned() → reset AI, health
                   │           OnDespawned() → clean up
                   ├── VfxController: OnSpawned() → play effect
                   │                 OnDespawned() → stop effect
                   └── DamageNumber: OnSpawned() → set text, animate
                                     OnDespawned() → clear
```

### Key Interfaces

```csharp
public interface IPoolable
{
    void OnSpawned();
    void OnDespawned();
}

public interface IPoolManager
{
    T Get<T>(GameObject prefab, Vector3 position, Quaternion rotation) where T : class;
    void Return<T>(T instance) where T : class;
    void EnsureCapacity(GameObject prefab, int count);
    void ClearAll();
    PoolReport GetReport(); // DEV_BUILD only
}

// Internal PoolManager implementation
public sealed class PoolManager : IPoolManager
{
    private readonly Dictionary<GameObject, object> _pools = new();
    private readonly Dictionary<GameObject, int> _activeCounts = new(); // dev profiling

    public T Get<T>(GameObject prefab, Vector3 position, Quaternion rotation) where T : class
    {
        if (prefab == null) return null;

        if (!_pools.TryGetValue(prefab, out var rawPool))
        {
            Debug.LogWarning($"[PoolManager] Creating new pool for {prefab.name} — no PoolProfile entry found");
            rawPool = CreatePool<T>(prefab, 0, int.MaxValue, 5);
            _pools[prefab] = rawPool;
        }

        var pool = (ObjectPool<T>)rawPool;
        var instance = pool.Get();
        if (instance is MonoBehaviour mb) mb.transform.SetPositionAndRotation(position, rotation);

        _activeCounts[prefab] = _activeCounts.TryGetValue(prefab, out var c) ? c + 1 : 1;
        return instance;
    }

    public void Return<T>(T instance) where T : class
    {
        // Pool-safe: ObjectPool handles null/invalid internally
        // Actual return is handled by ObjectPool<T>.Release()
        if (instance is IPoolable poolable) poolable.OnDespawned();
    }

    public void ClearAll()
    {
        foreach (var kvp in _pools)
        {
            var poolType = kvp.Key.GetType();
            // ObjectPool<T>.Clear() is accessible via reflection or by storing
            // the pool as non-generic IObjectPool reference
        }
        _pools.Clear();
        _activeCounts.Clear();
    }
}

public struct PoolReport
{
    public int TotalPools;
    public int TotalActive;
    public int TotalInactive;
    public Dictionary<GameObject, PoolStats> PerPrefab;
}

// AOT Preservation
internal static class PoolAotHelper
{
    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
    private static void PreserveTypes()
    {
        _ = new ObjectPool<Projectile>(null, null, null, null, false);
        _ = new ObjectPool<Enemy>(null, null, null, null, false);
        _ = new ObjectPool<VfxController>(null, null, null, null, false);
        _ = new ObjectPool<DamageNumber>(null, null, null, null, false);
    }
}
```

### Implementation Guidelines

1. **Pool wrapping**: Each prefab maps to one `ObjectPool<T>`. The `T` type parameter is the MonoBehaviour component on the prefab's root. The pool's `createFunc` calls `Object.Instantiate(prefab)`, `actionOnRelease` calls `gameObject.SetActive(false)`.

2. **Pool profile loading**: SceneManager calls `PoolManager.EnsureCapacity()` for each entry in the scene's `PoolProfile` after `ClearAll()` and before the scene's gameplay systems activate.

3. **Externally destroyed objects**: In `Get<T>()`, check `obj != null && obj.gameObject != null` before returning. Prune null entries from pool's internal stack.

4. **Return mechanics**: Three return paths:
   - Explicit: `PoolManager.Return(this)` inside the pooled object
   - Timer: IPoolable.OnSpawned() starts a coroutine that returns after lifetime expires
   - Safety net: `OnDisable()` detection in a base class catches unexpected deactivation

5. **No event bus coupling**: PoolManager is event-bus agnostic. Pooled objects (Projectile, Enemy, VFX) may publish events from their OnSpawned/OnDespawned via Event Bus, but PoolManager itself never touches the bus.

6. **AOT preservation list**: Must be updated whenever a new pool type is added. CI should grep for `ObjectPool<` in `_TinyRift/` and cross-reference against `PoolAotHelper.PreserveTypes()`.

## Alternatives Considered

### Alternative 1: Custom pool implementation

- **Description**: Write a custom pool class from scratch instead of wrapping `ObjectPool<T>`.
- **Pros**: Full control over pool behavior, no wrapping complexity.
- **Cons**: Reinventing a wheel that Unity has provided since 2021. No benefit over built-in.
- **Rejection Reason**: `ObjectPool<T>` is stable, tested by Unity, and available in Unity 6. No need for custom code.

### Alternative 2: Template's MonsterPool/DropPool

- **Description**: Extend or reuse the template's built-in MonsterPool and DropPool for custom content.
- **Pros**: No new pool system, reuses existing template assets.
- **Cons**: Requires modifying template code or creating tight coupling. Template pools are designed for template spawning patterns, not our skill-based combat.
- **Rejection Reason**: Template boundary rule — never modify `Assets/BulletHellTemplate/`.

### Alternative 3: Per-scene pools via VContainer child scopes

- **Description**: Each scene creates its own LifetimeScope child of TinyRiftScope with scene-specific pool registrations. Pool cleanup happens on scope disposal.
- **Pros**: ClearAll() is automatic via scope dispose. No explicit ClearAll() calls needed.
- **Cons**: PoolManager would need to be per-scene, not a singleton. Systems that cross scene boundaries (e.g., VFX system) would need to re-register per scene. Significantly more complexity.
- **Rejection Reason**: ADR-001 already resolved this — PoolManager is app-scoped, ClearAll() is explicit. Per-scene scopes add complexity without proportional benefit.

## Consequences

### Positive

- Zero GC allocation per spawn/despawn in hot path
- Configurable pre-warm per scene via PoolProfile ScriptableObjects
- Template pools (MonsterPool/DropPool) untouched
- AOT preservation forced by static method — clear failure mode (MissingMethodException at startup)
- Pool auto-growth with warning prevents silent out-of-pool failures
- IPoolable interface provides standard lifecycle contract for all pooled objects

### Negative

- AOT preservation list must be manually maintained when adding new pool types
- PoolManager wraps `ObjectPool<T>` via non-generic dictionary — requires `object` boxing for pool storage
- `ClearAll()` requires iterating all pools and calling Clear() — acceptable for scene transition cost
- Externally-destroyed objects cause null entries in pool stack (pruned on next Get) — edge case, not a bug

### Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| AOT type missing — MissingMethodException at runtime | Medium | High — crash on first pool usage | Static PreserveTypes() method + CI check |
| Pool entry for prefab that doesn't exist in build | Low | Medium — null reference | Null guard in Get() returns null; caller must handle |
| ClearAll() called while objects are mid-publish on Event Bus | Low | Low — Event Bus is sync, ClearAll() is called at scene transition boundary (no gameplay code active) | Document: Call ClearAll() at scene transition, not mid-frame |
| Two systems share a pool for the same prefab but expect different T types | Low | Low — prefab determines pool, not T. ObjectPool<T> cast fails at runtime. | Convention: prefab root component is the pool type. Document in team conventions. |

## Performance Implications

| Metric | Before | Expected After | Budget |
|--------|--------|---------------|--------|
| CPU (per Get/Return) | N/A | ~0.001ms (stack pop from ObjectPool<T>) | 0.01ms per call |
| Memory (per pool entry) | N/A | ~8 bytes per inactive instance (stack slot) | Negligible |
| GC (per Get/Return) | N/A | 0 — no allocations | 0 |
| Scene transition (ClearAll) | N/A | ~0.1ms per 200 pooled objects | 1ms budget |

## Migration Plan

1. Create `IPoolManager.cs` and `IPoolable.cs` interfaces in `Assets/_TinyRift/Runtime/Foundation/Pooling/`
2. Create `PoolManager.cs` implementing `IPoolManager`
3. Create `PoolProfile.cs` ScriptableObject in `Assets/_TinyRift/Runtime/Foundation/Pooling/`
4. Create `PoolAotHelper.cs` with initial AOT preservation
5. Create PoolProfile assets for each scene type (arena, camp)
6. Register `IPoolManager` in TinyRiftScope.ConfigureFoundation()
7. Update SceneManager to call `PoolManager.ClearAll()` on scene transitions (per ADR-001)
8. Update Feature systems to use `IPoolManager.Get<T>()` instead of `Instantiate()`

**Rollback plan**: Remove PoolManager registration. Feature systems use `Instantiate()`/`Destroy()` directly — no crash, but GC pressure returns. Gate with a compile-time switch.

## Validation Criteria

- [ ] `Get<T>()` returns a deactivated instance with `OnSpawned()` invoked
- [ ] `Return<T>()` deactivates instance and invokes `OnDespawned()`
- [ ] Pool auto-grows when exhausted and logs warning
- [ ] Externally destroyed object does not cause exception on next `Get<T>()`
- [ ] `ClearAll()` destroys all pooled objects and clears all pools
- [ ] IL2CPP build resolves all `ObjectPool<T>` types without `MissingMethodException`
- [ ] PoolProfile pre-warms are available immediately after `EnsureCapacity()` call
- [ ] Template MonsterPool/DropPool are unaffected by our PoolManager

## GDD Requirements Addressed

| GDD Document | System | Requirement | How This ADR Satisfies It |
|-------------|--------|-------------|--------------------------|
| `design/gdd/object-pooling.md` | Object Pooling | Wrap Unity's built-in ObjectPool<T> | PoolManager wraps ObjectPool<T> with prefab-keyed dictionary |
| `design/gdd/object-pooling.md` | Object Pooling | PoolManager registered in TinyRiftScope | Per ADR-001 — registered in Foundation layer |
| `design/gdd/object-pooling.md` | Object Pooling | PoolProfile ScriptableObject for pre-warm config | PoolProfile SO with prefab, prewarm, max, grow fields |
| `design/gdd/object-pooling.md` | Object Pooling | IPoolable lifecycle | OnSpawned()/OnDespawned() interface |
| `design/gdd/object-pooling.md` | Object Pooling | ClearAll() on scene transition | SceneManager calls PoolManager.ClearAll() explicitly (per ADR-001) |
| `design/gdd/object-pooling.md` | Object Pooling | AOT code stripping protection | PoolAotHelper.PreserveTypes() static method |
| `design/gdd/object-pooling.md` | Object Pooling | No dependency on template MonsterPool/DropPool | Completely separate pool system in Assets/_TinyRift/ |

## Related

- ADR-001: VContainer DI — PoolManager is app-scoped in TinyRiftScope, ClearAll() is explicit
- `design/gdd/object-pooling.md` — Full GDD with PoolProfile spec, edge cases, acceptance criteria
- `architecture.md:161` — Foundation layer includes Object Pooling
