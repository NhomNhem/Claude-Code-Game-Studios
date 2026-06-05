# VFX System

> **Creative Director Review (CD-GDD-ALIGN)**: CONCERNS — accepted 2026-05-29 (persistent ground decals added, synergy VFX replaced with empty registry hook for Alpha)
> **Status**: Designed

> **System ID**: #15
> **Layer**: Core
> **Priority**: MVP
> **Created**: 2026-05-29
> **Design Order**: Foundation → Core → Feature → Presentation → Polish
> **Depends on**: Object Pooling (#8), Event Bus (#6)
> **Depended by**: Zone Definition (#12), Skill Presentation (#34), Lore Fragment (#17), World State (#13), Currency (#11)

## 1. Overview

The VFX System owns all particle effects, non-UI visual feedback, and screen-space secondary effects (color sweeps, bursts, trails). It consumes events from the Event Bus and spawns/pre-scripted VFX sequences using a pooled object model. Elemental VFX are a core identity — fire scorches, ice fractures, lightning arcs. The system wraps Unity's Particle System and handles effect lifecycle, pooling, and intensity scaling.

## 2. Player Fantasy

Every action has a visual weight. Fire leaves scorch marks on the ground, Ice fractures into frost polygons, Lightning forks across the arena. When a zone restores, a color sweep washes over the screen. Level-ups explode with elemental energy. Ground decals persist through the run, building a visual history of the battle. Synergy VFX (element pair reactions) are deferred to Alpha.

## 3. Detailed Rules

**Architecture:**
- `IVfxService` (interface) injected via VContainer — registered in `VfxLifetimeScope` (child of GameplayLifetimeScope)
- `VfxService` (implementation) — subscribes to Event Bus events in `Start()`, holds pool references
- `VfxHandle` (IDisposable) — returned on spawn, controls lifetime, allows early despawn

**Event → VFX Mapping:**

| Event | VFX | Behavior |
|-------|-----|----------|
| `DamageDealtEvent` | Elemental hit FX | Spawn at hit position, rotate toward hit normal. Prefab resolved from Element → VfxKey map. |
| `EntityDiedEvent` | Death explosion | Spawn at corpse position, 1.5s auto-despawn. Larger entities get bigger death VFX. |
| `ZoneRestoredEvent` | Color sweep | Full-screen overlay sweep from bottom to top, 2s duration. Color matches zone. |
| `LevelUpEvent` | Level-up burst | Radial burst from player center, 1s duration. Element-resolved from last equipped skill. |
| `LoreFragmentCollectedEvent` | Fragment catch VFX | Sparkle burst at fragment transform, 1.2s duration. Soft glow lingers 3s. |
| `CurrencyChangedEvent` | Coin sparkle | Brief sparkle (0.3s) at last drop position. Only on gain, not loss. |

**Pooling:**
- All VFX prefabs are pooled via `IPooledObject<T>` from Object Pooling System (#8)
- Pool sizes configured per VFX type (see Tuning Knobs)
- Despawn returns to pool; pool returns default state (position zero, rotation identity, particles stopped)

**Elemental VFX Library:**

| Element | Hit VFX | Death VFX | Level-Up Burst | Trail |
|---------|---------|-----------|----------------|-------|
| Fire | `vfx_hit_fire` — orange fast-burn burst, 0.3s | `vfx_death_fire` — expanding ring + upward embers, 1.2s | `vfx_levelup_fire` — vertical flame column, 1.0s | `vfx_trail_fire` — orange ember trail, pool 30 |
| Ice | `vfx_hit_ice` — white shards, 0.4s | `vfx_death_ice` — frozen polygon spray, 1.5s | `vfx_levelup_ice` — expanding crystal ring, 1.2s | `vfx_trail_ice` — white particle trail, pool 20 |
| Lightning | `vfx_hit_lightning` — lightning bolt arc, 0.2s | `vfx_death_lightning` — branching arcs, 1.0s | `vfx_levelup_lightning` — upward electric spire, 0.8s | `vfx_trail_lightning` — blue arc trail, pool 15 |

**Persistent World VFX (Ground Decals):**
- When a hit kills an enemy, a ground decal is placed at the death position.
- Decals fade over 30s (configurable) and are cleaned up on zone transition.
- Decals use a pooled decal projector (not particle system) — max 64 concurrent.
- If pool is exhausted, oldest decal is reclaimed.

| Element | Decal Prefab | Visual | Lifetime |
|---------|------------|--------|----------|
| Fire | `vfx_decal_fire` | Dark scorch ring with orange embers at edge | 30s |
| Ice | `vfx_decal_ice` | White frost crack pattern radiating from center | 30s |
| Lightning | `vfx_decal_lightning` | Dark branching fissure pattern | 30s |

**Synergy VFX (Deferred — Alpha):**
- Element pair → VfxKey registry via `Dictionary<(Element, Element), VfxKey>`. Empty for MVP.
- When synergy system (#40 Alpha) triggers an `ElementalReactionEvent`, VFX system resolves the paired key.
- Example future entries: `(Fire, Ice) → vfx_synergy_steam`, `(Fire, Lightning) → vfx_synergy_plasma`, `(Ice, Lightning) → vfx_synergy_shatter`
- Architectural hook implemented in `IVfxService.ResolvePairVfx(Element a, Element b)` returning `null` (no-op) until filled.

**Event Bus subscriptions:** Registered in `VfxService.Start()`, unregistered in `OnDestroy()` via `UnsubscribeAll(this)`.

**Zone Restore Color Sweep:**
- Full-screen overlay rendered via a Canvas with RawImage and a shader-based sweep material
- Sweep bottom-to-top over 2s using a `_SweepOffset` shader property animated from 0→1
- Color resolved from `IZoneEnvironmentProvider.GetZoneColor()` (Zone Definition System)
- After sweep completes, overlay alpha fades to 0 over 0.5s, then canvas is deactivated

## 4. Formulas

```
VfxSpawnLife(config) = config.BaseDuration × IntensityScale(runTime, wave)
VfxPoolSize(config) = max(config.MinPool, ceil(config.AvgInstancesPerFrame × 1.5))
```

Where:
- `config.BaseDuration` — from VfxLibrarySO, per-element per-VFX-type
- `IntensityScale(runTime, wave)` — linear 1.0→1.5 over run length (scales particle count by 1.5x in late waves)
- `config.MinPool` — per-element per-VFX-type minimum pool size
- `config.AvgInstancesPerFrame` — observed average, measured during playtest, used for pool sizing

No other formulas. VFX lifecycle is duration-driven, not math-driven.

## 5. Edge Cases

- **If a VFX prefab is null at spawn time**: Log error, skip spawn. Pool returns a sentinel handle (IsValid = false). No crash.
- **If a pooled VFX is still alive when the pool is destroyed** (scene unload): Pool's `OnDestroy()` despawns and destoys all owned handles. No orphaned particles.
- **If 100+ hit VFX spawn in a single frame** (rapid orbit skill on large group): Pool starvation — `TrySpawn` returns false, VFX is dropped. Log a warning at first drop per frame, then silence until next frame. No per-instance log flood.
- **If the player levels up at the exact moment they die**: Events are published atomically. If `EntityDiedEvent` fires before `LevelUpEvent` in the same publish chain, VFX for level-up is still processed (player is dead but VFX system doesn't gate on alive state). Acceptable — the VFX is harmless and short-lived.
- **If a DamageDealtEvent has no valid position** (zero vector): VFX system treats zero vector as invalid. Log warning, skip spawn.
- **If ZoneRestoredEvent fires rapidly** (rapid zone completion): Current sweep is cancelled immediately. New sweep starts from bottom with full duration. No queueing.
- **If an element key is not found in the VFX library** (missing prefab): Fall back to `vfx_hit_default` (white generic burst). Log a configuration error once.
- **If VfxService is not yet initialized when events arrive**: Events are published immediately, so VFX may miss the first few frames of gameplay. `VfxService.Start()` subscribes before `VfxService.OnDestroy()` unsubscribes. If a timing gap exists, events are dropped silently.
- **If pool size is exhausted and overflow is disabled**: `TrySpawn` returns false. Visual feedback is degraded but gameplay is unaffected. No error log — this is a performance/quality tradeoff, not a bug.
- **If decal pool is exhausted** (64 concurrent): Oldest decal is reclaimed immediately. Decal manager tracks spawn order in a circular buffer. No error log — expected at high kill density.
- **If decal is still alive when zone transitions**: All decals are cleaned up on `GameStateChangedEvent(Hub, HeroCamp)`. Decal projector objects returned to pool silently.
- **If ElementPair VFX key is queried and registry is empty** (MVP): `ResolvePairVfx()` returns null. Caller handles null gracefully (no spawn). Deferred to Alpha.

## 6. Dependencies

| System | ID | Direction | Notes |
|--------|----|-----------|-------|
| Event Bus | #6 | Consumer | Subscribes to 6 event types |
| Object Pooling | #8 | Dependency | All VFX prefabs are pooled objects |
| Zone Definition | #12 | Consumer | Resolves `IZoneEnvironmentProvider.GetZoneColor()` for sweep |
| Skill Data | — | Data | Resolves element strings to VFX keys |
| Save/Profile | #10 | None | No persistence for VFX state |

## 7. Tuning Knobs

| Knob | Default | Range | Effect When Max | Effect When Min | Owner |
|------|---------|-------|-----------------|-----------------|-------|
| Pool size (hit VFX per element) | 20 | 5–50 | No pool starvation even with dense combat | Frequent drops, visual degradation | VfxService |
| Pool size (death VFX per element) | 10 | 3–25 | Handles large death waves | Drops on boss death + adds | VfxService |
| Pool size (level-up burst) | 3 | 1–5 | No starvation on rapid leveling | Drops on quick double-level | VfxService |
| Zone sweep duration | 2.0s | 1.0–4.0s | Slow, meditative restoration | Fast, action-forward sweep | ZoneRestoreVfx |
| Zone sweep fade-out | 0.5s | 0.2–1.0s | Gentle transition back to gameplay | Snappy, minimal overlay | ZoneRestoreVfx |
| Intensity scale max | 1.5x | 1.0–2.0x | Dramatic late-wave VFX | Consistent VFX throughout run | VfxService |
| Hit VFX base duration (fire) | 0.3s | 0.15–0.6s | Long-lasting embers | Quick flash, barely visible | VfxLibrarySO |
| Hit VFX base duration (ice) | 0.4s | 0.2–0.8s | Shatter lingers | Shatter is a blink | VfxLibrarySO |
| Hit VFX base duration (lightning) | 0.2s | 0.1–0.4s | Arc persists across frames | Arc is a micro-flash | VfxLibrarySO |

## 8. Acceptance Criteria

1. **Hit VFX spawn at damage position** — When `DamageDealtEvent` is published, a pooled VFX matching the damage element is spawned at the event's position.
2. **Death VFX auto-despawn after duration** — When `EntityDiedEvent` is published, death VFX spawns and despawns after the configured base duration.
3. **Zone restore color sweep** — When `ZoneRestoredEvent` fires, a full-screen color sweep plays from bottom to top, using the zone's environment color.
4. **Level-up burst from player center** — When `LevelUpEvent` fires, a radial burst VFX appears at the player's position, resolved from the last equipped skill's element.
5. **Lore fragment catch VFX** — When `LoreFragmentCollectedEvent` fires, a sparkle burst plays at the fragment transform, followed by a 3s soft glow.
6. **Currency sparkle on gain** — When `CurrencyChangedEvent` fires with a delta > 0, a brief sparkle plays at the last known drop position.
7. **Pool starvation does not crash** — When pool is exhausted, `TrySpawn` returns false gracefully and a single warning is logged per frame.
8. **Null prefab does not crash** — When a VFX key resolves to null, an error is logged and the spawn is skipped.
9. **Zone sweep cancellation** — When `ZoneRestoredEvent` fires while a sweep is in progress, the current sweep is cancelled and a new one starts from the bottom.
10. **Missing element fallback** — When an element key has no VFX entry, `vfx_hit_default` is used and a configuration error is logged once.
11. **VFX pool returns to clean state on despawn** — After despawn, the VFX object is at position (0,0,0), rotation identity, and all particle systems are stopped.
12. **VfxService unsubscribes on destroy** — When `VfxService.OnDestroy()` runs, `UnsubscribeAll(this)` is called and no further events are received.
13. **Ground decal placed on enemy death** — When an enemy dies, a pooled decal projector spawns at the death position matching the killing element.
14. **Decal cleaned up on zone transition** — When `GameStateChangedEvent(Hub, HeroCamp)` fires, all decals are despawned.
15. **Synergy VFX hook returns null** — `IVfxService.ResolvePairVfx(Element, Element)` returns null for all pairs in MVP. No crash or error.
