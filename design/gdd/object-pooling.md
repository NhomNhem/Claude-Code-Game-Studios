# Object Pooling

> **Status**: In Design
> **Author**: user + agents
> **Last Updated**: 2026-05-26
> **Implements Pillar**: P3 (Snappy Sessions) — pooling prevents GC spikes that cause frame hitches

## Overview

Object Pooling is a performance infrastructure layer that pre-allocates and recycles frequently-spawned GameObjects — projectiles, enemies, VFX particles, damage numbers — instead of creating and destroying them at runtime. Each pool holds a configurable number of pre-instantiated instances that are activated on request and deactivated on return, eliminating heap allocation and garbage collection spikes from the hot path. Without it, every projectile fired, enemy spawned, and VFX burst triggers a GC allocation that compounds under heavy combat, producing frame hitches that erode the game's 60 FPS target.

## Player Fantasy

Object Pooling has no direct player fantasy — players never interact with it consciously. What they feel is the absence of frame hitches during dense combat: projectiles fly without stutter, enemies spawn smoothly, VFX bursts don't cause a freeze. The pool is the game's reusable parts bin — invisible, but the difference between a 60 FPS run and a stuttering one.

## Detailed Design

### Core Rules

1. Object Pooling wraps Unity's built-in `UnityEngine.Pool.ObjectPool<T>` — a generic stack-based pool that has been available since Unity 2021 and is fully supported in Unity 6000.3.x. No custom pool class is needed.
2. All pools are managed by a single `PoolManager` VContainer service. Consumers never create or own pools directly.
3. The `PoolManager` holds a `Dictionary<GameObject, IObjectPool>` keyed by prefab reference. Each prefab gets exactly one pool, shared across all consumers.
4. Pools pre-warm at scene load by instantiating a configurable number of instances and immediately returning them to the pool. Pre-warm counts are defined in a `PoolProfile` ScriptableObject per scene.
5. When a pool is exhausted and `Get()` is called, the pool batch-grows by a configurable increment (default 5) and logs a warning suggesting a higher pre-warm value.
6. Pooled objects implement `IPoolable` for lifecycle callbacks:
   ```csharp
   public interface IPoolable
   {
       void OnSpawned();       // Called after Get() — reset state, start behaviors
       void OnDespawned();     // Called before Return() — clean up state
   }
   ```
7. Objects return to the pool via three mechanisms:
   - **Explicit**: `PoolManager.Return<T>(T component)` — primary path
   - **Timer**: `IPoolable.OnSpawned()` starts a lifetime; object auto-returns when timer expires
   - **Safety net**: `OnDisable()` detection catches unexpected deactivation
8. Pooled objects are parented under `_PoolRoot/[PoolName]` in the scene hierarchy. Each pool type gets a child transform for organization.
9. On scene transition, `SceneManager` calls `PoolManager.ClearAll()` explicitly, which returns all objects to their pools and destroys them. Pools are app-scoped in `TinyRiftScope` (not disposed on scene change) — `ClearAll()` is the explicit cleanup mechanism, not scope disposal. See ADR-001 for scope architecture.
10. The `PoolManager` is registered in `TinyRiftScope` as a cross-scene singleton. Each scene transition calls `ClearAll()` to reset pools for the new scene's content.
11. AOT code stripping protection: a static AOT-code-generation method forces IL2CPP to compile `ObjectPool<T>` for each concrete `T` used at runtime.

### Pool Types

| Pool | Prefab Type | Pre-warm | Max | Used By | Lifetime |
|------|-------------|----------|-----|---------|----------|
| Projectile | Projectile (MonoBehaviour) | 50 | 100 | Orbit Combat, Burst Skill | Until hit/expire |
| Enemy | Enemy (MonoBehaviour) | 30 | 50 | Wave Spawning | Until death |
| VFX | Particle FX (MonoBehaviour) | 100 | 200 | VFX System, DmgHealth, SkillPresentationAdapter | Duration of effect |
| DamageNumber | FloatingText (MonoBehaviour) | 30 | 60 | Damage & Health | 1.5s float + fade |

*Pre-warm and max values are per PoolProfile. Values above are for arena combat scenes. Camp scenes use smaller profiles.*

**API Surface:**
```csharp
public class PoolManager
{
    // Get a pooled instance. Creates pool for prefab on first call.
    public T Get<T>(GameObject prefab, Vector3 position, Quaternion rotation) where T : class;

    // Return an instance to its pool.
    public void Return<T>(T instance) where T : class;

    // Ensure a prefab's pool has at least `count` instances pre-warmed.
    public void EnsureCapacity(GameObject prefab, int count);

    // Return all pooled objects and destroy their GameObjects. Called on scene transition.
    public void ClearAll();

    // Dev-build profiling
    public PoolReport GetReport();
}

public struct PoolReport
{
    public int TotalPools;
    public int TotalActive;
    public int TotalInactive;
    public Dictionary<GameObject, PoolStats> PerPrefab;
}
```

**PoolProfile ScriptableObject:**
```csharp
[CreateAssetMenu(menuName = "TinyRift/PoolProfile")]
public class PoolProfile : ScriptableObject
{
    public PoolEntry[] Entries;
}

[System.Serializable]
public struct PoolEntry
{
    public GameObject Prefab;
    public int PrewarmCount;
    public int MaxSize;
    public int GrowIncrement;    // default 5
}
```

**AOT code generation (prevents IL2CPP stripping):**
```csharp
// In PoolManager.cs or a dedicated AOT helper
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

**Example usage (projectile spawn):**
```csharp
// Orbit Combat System
var proj = _poolManager.Get<Projectile>(_fireOrbPrefab, spawnPos, Quaternion.identity);
proj.Launch(direction, speed);
// When projectile hits:
// proj calls _poolManager.Return(this) or:
// poolManager timer auto-returns after 5 seconds
```

### Interactions with Other Systems

| System | Interface | Direction | Data |
|--------|-----------|-----------|------|
| VFX System | Calls `PoolManager.Get<VfxController>(prefab, pos, rot)` | VFX → PoolManager | VFX prefab key resolved by VFX System to actual prefab → pool returns typed instance |
| Orbit Combat | Calls `PoolManager.Get<Projectile>(prefab, pos, rot)` to spawn orbit projectiles | Orbit → PoolManager | Projectile prefab reference; pool manages lifecycle |
| Burst Skill | Calls `PoolManager.Get<Projectile>(prefab, pos, rot)` for burst projectiles and skill VFX | Burst → PoolManager | Projectile prefab reference; pool manages lifecycle |
| Wave Spawning | Calls `PoolManager.Get<Enemy>(prefab, pos, rot)` to spawn enemies | Wave → PoolManager | Enemy prefab per wave definition; pool manages lifecycle |
| Damage & Health | Calls `PoolManager.Get<DamageNumber>(prefab, pos, rot)` for floating damage numbers | DmgHealth → PoolManager | Damage number prefab |
| SkillPresentationAdapter | Calls `PoolManager.Get<VfxController>(prefab, pos, rot)` for skill VFX | Adapter → PoolManager | VFX prefab per PresentationProfile |
| Scene Manager | Calls `PoolManager.ClearAll()` on scene transition (indirect — PoolManager is scene-scoped via VContainer dispose) | Scene → PoolManager | Pool teardown |
| Event Bus | PoolManager does not use the Event Bus. Pooled objects (Projectile, Enemy, VFX) may publish events via Event Bus in their `OnSpawned`/`OnDespawned` lifecycle, but PoolManager itself is event-bus agnostic. | PoolManager → (none) | No event coupling |

*Note: The template's built-in `MonsterPool` and `DropPool` continue to serve template-internal spawning. Our `PoolManager` handles all custom content in `Assets/_TinyRift/`. The two systems never interact.*

## Formulas

None. Object Pooling is a lifecycle management system with no mathematical calculations. Pool sizing (pre-warm counts, max sizes) are designer-configured values in `PoolProfile` assets, not computed values.

## Edge Cases

- **If `PoolManager.Get()` is called for a prefab that has never been seen before**: A new pool is created on demand with default pre-warm (0 — first call instantiates a single instance). A warning is logged. The caller still receives a valid instance.
- **If a pooled object is destroyed externally** (via `Destroy(gameObject)` instead of `PoolManager.Return()`): The pool's stack retains a null reference. On the next `Get()`, the pool checks `obj != null && obj.gameObject != null` before returning. Null entries are silently pruned.
- **If the pool is exhausted and `Get()` is called**: The pool batch-grows by `GrowIncrement` (default 5) and logs a warning with the prefab name and a suggested pre-warm update. The caller receives a valid instance.
- **If `ClearAll()` is called while pooled objects are still active** (scene transition mid-combat): All active instances are deactivated via `ObjectPool.Clear()`. `OnDespawned()` runs. Active behaviors are interrupted — expected during scene transitions.
- **If a pooled object tries to `Return()` after `ClearAll()` has destroyed it**: The call checks if the pool still exists and if the instance is in the active set. If not, it silently ignores the return.
- **If `EnsureCapacity()` is called with a count lower than the pool's active count**: Only adds capacity — never removes active instances. Warning logged.
- **If two systems `Get()` from the same prefab pool on the same frame**: Each pops independently from the stack. No race condition (Unity single-threaded). Both receive distinct instances.
- **If `PoolProfile` defines a prefab that no longer exists**: `PoolManager.Get()` guards with a null prefab check and returns null. Caller must handle null.
- **If an AOT-stripped `ObjectPool<T>` is encountered**: Throws `MissingMethodException`. Fix: add concrete `T` to `PoolAotHelper.PreserveTypes()`.

## Dependencies

| System | Dependency | Direction | Notes |
|--------|-----------|-----------|-------|
| VFX System | Requires PoolManager to be registered in VContainer | VFX → PoolManager | No circular dependency |
| Orbit Combat | Requires PoolManager for projectile pooling | Orbit → PoolManager | |
| Burst Skill | Requires PoolManager for projectile pooling | Burst → PoolManager | |
| Wave Spawning | Requires PoolManager for enemy pooling | Wave → PoolManager | |
| Damage & Health | Requires PoolManager for damage number pooling | DmgHealth → PoolManager | |
| SkillPresentationAdapter | Requires PoolManager for VFX pooling | Adapter → PoolManager | |
| Scene Manager | Indiretly via VContainer scope lifecycle | Scene → PoolManager | PoolManager is scene-scoped |
| Event Bus | No dependency | — | PoolManager is event-bus agnostic |
| Custom code (`_TinyRift/`) | Requires PoolManager | All → PoolManager | No dependency on template systems |

PoolManager **depends on**:
- `UnityEngine.Pool.ObjectPool<T>` (built-in)
- `VContainer` (registration in TinyRiftScope)
- `System.Collections.Generic` (Dictionary, Stack)
- `PoolProfile` ScriptableObject (for pre-warm configuration)

PoolManager **does NOT depend on**:
- Event Bus (decoupled by design)
- Any template system (MonsterPool, DropPool, etc.)
- Fusion
- Backend service

## Tuning Knobs

| Knob | Type | Default | Range | Used By | Notes |
|------|------|---------|-------|---------|-------|
| PrewarmCount | int | Per prefab (PoolProfile) | 0–500 | PoolProfile | Per prefab; arena vs camp profiles differ |
| MaxSize | int | Per prefab (PoolProfile) | 20–1000 | PoolProfile | Hard cap per prefab |
| GrowIncrement | int | 5 | 1–50 | PoolProfile | Batch growth size when pool exhausted |
| Profiling enabled | bool | false | true/false | Dev builds only | Enables PoolReport generation |

## Visual/Audio Requirements

None. Object Pooling is invisible to the player. Visual effects and audio are authored on the prefabs themselves, not on the pool manager.

## UI Requirements

None. Object Pooling exposes no UI. Dev-build profiling (PoolReport) may be displayed via a debug overlay, but no production UI.

## Acceptance Criteria

1. Given a PoolProfile asset, when a scene loads, each prefab in the profile has the specified pre-warm count available in its pool (inactive).
2. When `PoolManager.Get()` is called for a prefab, a deactivated instance from that prefab's pool is returned with `OnSpawned()` invoked.
3. When `PoolManager.Return()` is called, the instance is deactivated and returned to the pool.
4. When the pool is exhausted and `Get()` is called, the pool batch-grows by GrowIncrement and logs a warning.
5. When a pooled object is destroyed externally, the pool silently prunes the null entry on the next `Get()` without throwing.
6. When `ClearAll()` is called, all pooled objects are destroyed and `OnDespawned()` is invoked on active instances.
7. When a new prefab is passed to `Get()` without prior registration, a new pool is created on demand and a warning is logged.
8. When `EnsureCapacity()` is called, the pool grows to at least the requested count without exceeding MaxSize.
9. When `EnsureCapacity()` is called with a value below the current active count, a warning is logged and capacity is not reduced.
10. In an IL2CPP build, all used `ObjectPool<T>` concrete types resolve without `MissingMethodException`.

## Open Questions

1. Should pooled objects auto-return via a coroutine timer (Component-based) or a master timer manager (pool-managed)?
   → **Recommendation**: `IPoolable` with self-managed `StartCoroutine(AutoReturn(lifetime))`. Keeps lifetime logic co-located with the pooled object. Resolved during implementation review.
2. Should overlapping pools share a global warm-up phase, or should each scene's PoolProfile handle it independently?
   → **Recommendation**: Independent PoolProfile per scene. Reduces coupling and makes each scene self-describing. Resolved.
3. Should we expose a hot-reload pool inspector for dev builds?
   → **Recommendation**: Yes — a debug panel showing active/inactive counts per pool, displayed via Unity UI in dev builds only. Deferred to Polish phase.
