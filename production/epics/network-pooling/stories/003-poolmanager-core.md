# Story 003: PoolManager Core

- **Epic**: Network & Object Pooling
- **System**: Object Pooling — Core
- **Type**: Logic
- **Priority**: P0
- **Estimate**: 4h
- **Status**: Complete
- **Last Updated**: 2026-06-02

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-objpool-001` | PoolProfile pre-warm counts available on scene load | ✅ ADR-005 |
| `TR-objpool-002` | PoolManager.Get() returns instance with OnSpawned() | ✅ ADR-005 |
| `TR-objpool-003` | PoolManager.Return() deactivates and returns | ✅ ADR-005 |
| `TR-objpool-011` | Wraps UnityEngine.Pool.ObjectPool<T> | ✅ ADR-005 |
| `TR-objpool-012` | VContainer singleton in TinyRiftScope | ✅ ADR-001 |
| `TR-objpool-013` | IPoolable with OnSpawned()/OnDespawned() | ✅ ADR-005 |
| `TR-objpool-014` | Pooled objects under _PoolRoot/[PoolName] | ✅ ADR-005 |

## ADR Guidance

**ADR-005 (Object Pooling Strategy):**
- PoolManager wraps `UnityEngine.Pool.ObjectPool<T>` internally per prefab
- PoolProfile ScriptableObject defines pre-warm counts per prefab
- IPoolable interface: `void OnSpawned()`, `void OnDespawned()`
- Pooled objects parented to `_PoolRoot/[PoolName]` for hierarchy cleanliness
- VContainer singleton registration in TinyRiftScope

**ADR-001 (VContainer DI Architecture):**
- `IPoolManager` registered as interface singleton

## Description

Implements the core PoolManager that creates and manages `ObjectPool<T>` instances keyed by prefab reference. Supports pre-warming from `PoolProfile` ScriptableObjects on scene load, provides Get/Return API, and invokes IPoolable lifecycle callbacks. Manages all pooled objects under a dedicated scene hierarchy root.

## Design

- `IPoolable` interface:
  - `void OnSpawned()` — called after Get, before object active
  - `void OnDespawned()` — called before Return, after deactivation
- `PoolProfile` ScriptableObject:
  - `List<PoolProfileEntry> entries` where each entry has:
    - `GameObject Prefab`
    - `int PreWarmCount`
    - `int GrowIncrement` (default 5)
    - `int MaxSize` (default 50)
- `PoolManager` (MonoBehaviour, `IPoolManager`):
  - Configuration Source: The `PoolProfile` is injected into the `PoolManager` constructor via VContainer.
  - `Dictionary<GameObject, IObjectPool<GameObject>> _pools` keyed by prefab
  - `GameObject _poolRoot` — created as `_PoolRoot` child of DontDestroyOnLoad
  - `Get(GameObject prefab)`: resolves or creates pool, calls `pool.Get()`, invokes `OnSpawned()`, parents to `_PoolRoot/[PoolName]`
  - `Return(GameObject instance)`: deactivates, invokes `OnDespawned()`, calls `pool.Release(instance)`
  - Pre-warm: on Start, reads PoolProfile entries, creates pools, Get+Return for each pre-warm count
  - Pool creation: `new ObjectPool<GameObject>(createFunc, actionOnGet, actionOnRelease, actionOnDestroy, maxSize)`
  - Edge Case Handling:
    - Unknown Prefabs: If `Get(prefab)` is called for a prefab not in the `PoolProfile`, a dynamic pool is created using defaults (`GrowIncrement=5`, `MaxSize=50`) and a warning is logged.
    - Invalid Returns: `Return(null)` is ignored. Returning an unmanaged object logs a warning. Double-returns are prevented by checking instance activity.
  - ObjectPool<T> wrapping:
  - createFunc: `Object.Instantiate(prefab, _poolRoot.transform)`
  - actionOnGet: `gameObject.SetActive(true)`
  - actionOnRelease: `gameObject.SetActive(false)`
  - actionOnDestroy: `Object.Destroy(gameObject)`
- Pooled objects parented under `_PoolRoot/{PrefabName}` for clean hierarchy

## Acceptance Criteria

1. PoolProfile pre-warm: after PoolManager Start, pool for each entry has `CountAll >= PreWarmCount`
2. PoolManager.Get(prefab) returns a valid GameObject (new or recycled)
3. OnSpawned() called on returned object's IPoolable component immediately after Get
4. PoolManager.Return(instance) deactivates the GameObject
5. OnDespawned() called on instance's IPoolable component before Return
6. Returned object becomes available for next Get (same instance reused)
7. Pooled objects parented to `_PoolRoot/{PrefabName}` during both active and pooled states
8. IPoolManager registered via VContainer as singleton in TinyRiftScope
9. PoolManager wraps ObjectPool<GameObject> internally (not a custom pool)
10. AC10 (Dynamic Pool Creation): Calling Get(prefab) for a prefab not in the PoolProfile returns a valid object and logs a warning.
11. AC11 (Safe Return): Calling Return(null) or returning an unmanaged object results in no exception and a warning for unmanaged objects.
12. AC12 (Double Return Prevention): Returning the same instance twice does not corrupt the internal pool stack.

## QA Test Cases

- **AC1 (Pre-warm)**: Create PoolProfile with PreWarmCount=5. Init PoolManager. Verify pool.CountAll >= 5 and 5 instances available inactive.
- **AC2 (Get returns GameObject)**: Call Get(prefab). Verify returned object is non-null, active in hierarchy.
- **AC3 (OnSpawned called)**: Get(prefab). Verify IPoolable.OnSpawned() was invoked on returned object.
- **AC4 (Return deactivates)**: Get then Return. Verify object.SetActive(false) was called.
- **AC5 (OnDespawned before Return)**: Return(instance). Verify OnDespawned() called before deactivation.
- **AC6 (Reuse)**: Get A, Return A, Get B. Verify A and B are the same instance.
- **AC7 (Hierarchy parenting)**: Verify active and inactive objects parented to `_PoolRoot/{PrefabName}`.
- **AC8 (VContainer singleton)**: Verify IPoolManager registered as singleton in TinyRiftScope.
- **AC9 (Wraps ObjectPool<GameObject>)**: Verify PoolManager uses ObjectPool<GameObject> internally via reflection or type check of _pools values.

**Edge cases**: Get before pre-warm (empty pool), Return null instance, Return destroyed instance (MissingReferenceException), null PoolProfile (graceful skip).

## Test Evidence Path

- `tests/Foundation/ObjectPooling/TestPoolManagerCore.cs`
- Unit tests: PoolProfile pre-warm, Get/Return cycle, IPoolable invocation, hierarchy parenting

## Dependencies

- **Depends on**: None
- **Unlocks**: Story 004 (Pool Growth, Safety & AOT Preservation)

## Completion Notes
**Completed**: 2026-06-02
**Criteria**: 12/12 passing
**Deviations**: ADVISORY: AC8 and AC9 lack automated verification. ADVISORY: null PoolProfile edge case not unit tested.
**Test Evidence**: Logic: test file at Assets/_TinyRift/Tests/EditMode/Pooling/TestPoolManagerCore.cs
**Code Review**: Complete (Lead Programmer approved)
