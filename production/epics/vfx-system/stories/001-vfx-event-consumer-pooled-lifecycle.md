# Story 001: VFX Event Consumer & Pooled Lifecycle

- **Epic**: VFX System
- **System**: VFX System
- **Type**: Integration
- **Priority**: P0
- **Estimate**: 4h
- **Status**: Ready
- **Last Updated**: 2026-06-02

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-vfx-001` | Particle spawn/manage via Event Bus consumption (6 event types) | ✅ ADR-002, ADR-005 |

## ADR Guidance

**ADR-002 (Event Bus Contract):**
- Subscribes to 6 event types: `DamageDealtEvent`, `EntityDiedEvent`, `ZoneRestoredEvent`, `LevelUpEvent`, `LoreFragmentCollectedEvent`, `CurrencyChangedEvent`
- Subscriptions in `Start()`, unsubscribed in `OnDestroy()` via `UnsubscribeAll(this)`

**ADR-005 (Object Pooling Strategy):**
- All VFX prefabs are pooled via `PoolManager` using `IPooledObject<T>` interface
- `OnSpawned()` resets position/rotation, starts particle systems
- `OnDespawned()` stops particles, resets to default state
- Pool sizes configured per VFX type

**Control Manifest (relevant rules):**
- `IVfxService` interface registered in `VfxLifetimeScope` (child of `GameplayLifetimeScope`)
- `VfxHandle` implements `IDisposable` for early despawn
- Never modify template's Particle System or vendor prefabs

## Description

Implement the core `IVfxService` that subscribes to 6 Event Bus event types and dispatches pooled VFX prefabs at the correct world position. Manages effect lifecycle from spawn through auto-despawn. Uses `PoolManager` for all pooled VFX controllers and returns `VfxHandle` instances for lifetime control. Handles pool starvation gracefully with logged warnings per frame.

## Design

```csharp
public interface IVfxService
{
    VfxHandle SpawnVfx(string vfxKey, Vector3 position, Quaternion rotation, float intensityScale = 1.0f);
    void DespawnVfx(VfxHandle handle);
    bool TrySpawnVfx(string vfxKey, Vector3 position, Quaternion rotation, out VfxHandle handle);
    void ClearAll();
}
```

### Event → VFX Mapping

| Event | VFX | Spawn Position | Auto-Despawn |
|-------|-----|---------------|--------------|
| `DamageDealtEvent` | Elemental hit FX | Hit position, rotated toward hit normal | Per-config base duration |
| `EntityDiedEvent` | Death explosion | Corpse position | 1.5s |
| `ZoneRestoredEvent` | Color sweep (full-screen overlay) | Screen-space (Canvas) | 2.0s sweep + 0.5s fade |
| `LevelUpEvent` | Level-up burst | Player center | 1.0s |
| `LoreFragmentCollectedEvent` | Fragment catch VFX | Fragment transform | 1.2s sparkle + 3s glow |
| `CurrencyChangedEvent` | Coin sparkle | Last drop position | 0.3s (gain only) |

### Pooled Lifecycle

1. Event fires → VfxService resolves VFX key → calls `PoolManager.TrySpawn<VfxController>(prefabKey, out controller)`
2. If pool exhausted → log warning (once per frame), skip spawn
3. Controller.OnSpawned() resets state, starts particle system
4. Auto-despawn timer starts (configurable per VFX type)
5. On despawn: stop particles → `PoolManager.Despawn(controller)` → pool returns to clean state
6. Manual early despawn via `VfxHandle.Dispose()`

### Pool Starvation Handling

- `TrySpawn` returns false when pool exhausted
- Single warning logged at first drop per frame, then silenced until next frame
- No per-instance log flood

### Error Handling

- Null prefab at spawn time: log error, skip spawn, return sentinel handle (`IsValid = false`)
- Zero-vector position: log warning, skip spawn
- Missing element key in VFX library: fall back to `vfx_hit_default`, log config error once

## Acceptance Criteria

1. **Hit VFX at damage position**: When `DamageDealtEvent` fires, a pooled VFX matching the damage element spawns at the event's position.
2. **Death VFX auto-despawn**: When `EntityDiedEvent` fires, death VFX spawns and despawns after configured base duration.
3. **Level-up burst from player center**: When `LevelUpEvent` fires, a radial burst VFX appears at the player's position.
4. **Lore fragment catch VFX**: When `LoreFragmentCollectedEvent` fires, a sparkle burst plays at the fragment transform with 3s glow.
5. **Currency sparkle on gain**: When `CurrencyChangedEvent` fires with delta > 0, a brief sparkle plays at last known drop position.
6. **Pool starvation graceful**: When pool exhausted, `TrySpawn` returns false and a single warning is logged per frame.
7. **Null prefab non-crash**: When a VFX key resolves to null, an error is logged and spawn is skipped.
8. **Pool return to clean state**: After despawn, VFX object is at position (0,0,0), rotation identity, and all particle systems stopped.
9. **Subscriptions unregistered on destroy**: When `OnDestroy()` runs, `UnsubscribeAll(this)` is called and no further events are received.
10. **Missing element fallback**: When element key has no VFX entry, `vfx_hit_default` is used and a config error logged once.

## Test Evidence Path

- `Assets/_TinyRift/Tests/EditMode/VfxSystem/VfxEventConsumerTests.cs`
- Event → VFX routing for all 6 event types
- Pool starvation handling (exhaust pool, verify graceful fallback)
- Pool lifecycle (spawn → auto-despawn → clean state)

## Dependencies

- **Event Bus** — 6 event type subscriptions
- **PoolManager (from network-pooling epic)** — `IPooledObject<T>` lifecycle for all VFX prefabs

## Unlocks

- VFX Story 002 (Elemental VFX Library)

## Risks

- **HIGH**: URP 17.3 RenderGraph replaces CommandBuffer for custom passes. Zone restore color sweep uses Canvas with RawImage (no CommandBuffer), so this story is low-risk for RenderGraph. Particle System is unaffected by RenderGraph.
- **MEDIUM**: Pool exhaustion at high kill density (100+ VFX in one frame). Mitigation: pool sizes configured per VFX type with 1.5x safety margin.
