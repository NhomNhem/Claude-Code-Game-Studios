# Story 002: Elemental VFX Library

- **Epic**: VFX System
- **System**: VFX System
- **Type**: Visual/Feel
- **Priority**: P1
- **Estimate**: 4h
- **Status**: Ready
- **Last Updated**: 2026-06-02

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-vfx-002` | Elemental VFX library (fire scorches, ice fractures, lightning arcs) | ✅ ADR-001, ADR-005 |

## ADR Guidance

**ADR-001 (VContainer DI Architecture):**
- VFX prefab references registered via `VfxLibrarySO` ScriptableObject
- `IVfxService.ResolvePairVfx()` returns null for MVP (synergy hook, no-op)

**ADR-005 (Object Pooling Strategy):**
- Each elemental VFX type has dedicated pool sizes
- Ground decals use pooled decal projector (max 64 concurrent)

**Control Manifest (relevant rules):**
- All VFX prefabs stored in `Assets/_TinyRift/Art/VFX/Prefabs/`
- `VfxLibrarySO` ScriptableObject maps element → VfxKey → prefab
- Intensity scaling multiplies particle count by up to 1.5x in late waves

## Description

Author the elemental VFX library — the visual identity of each element. Fire scorches with orange embers and upward bursts, Ice fractures into white polygon shards with frost patterns, Lightning arcs with branching bolts. Each element has hit VFX, death VFX, level-up burst, trail, and ground decal variants. All prefabs are pooled, intensity-scaled by run time, and compatible with URP 17.3.

## Design

### Elemental Hit VFX

| Element | Hit VFX | Death VFX | Level-Up Burst | Trail |
|---------|---------|-----------|----------------|-------|
| Fire | Orange fast-burn burst, 0.3s | Expanding ring + upward embers, 1.2s | Vertical flame column, 1.0s | Orange ember trail, pool 30 |
| Ice | White shard burst, 0.4s | Frozen polygon spray, 1.5s | Expanding crystal ring, 1.2s | White particle trail, pool 20 |
| Lightning | Lightning bolt arc, 0.2s | Branching arcs, 1.0s | Upward electric spire, 0.8s | Blue arc trail, pool 15 |

### Ground Decals (Persistent World VFX)

| Element | Decal Prefab | Visual | Lifetime |
|---------|------------|--------|----------|
| Fire | `vfx_decal_fire` | Dark scorch ring with orange embers at edge | 30s |
| Ice | `vfx_decal_ice` | White frost crack pattern radiating from center | 30s |
| Lightning | `vfx_decal_lightning` | Dark branching fissure pattern | 30s |

- Placed at enemy death position
- Max 64 concurrent decals via pooled decal projector
- Oldest reclaimed when pool exhausted (circular buffer)
- All decals cleaned up on zone transition

### Intensity Scaling

```
IntensityScale(runTime, wave) = lerp(1.0, 1.5, runTime / maxRunTime)
```

Applied as particle count multiplier on VFX prefabs. Late-wave VFX at 1.5x intensity.

### Synergy VFX Hook (MVP No-Op)

```csharp
public VfxKey? ResolvePairVfx(Element a, Element b) => null;
```

Architectural hook for Alpha. Returns null for all pairs in MVP. No crash, no effect.

### Zone Restore Color Sweep

Full-screen overlay: Canvas + RawImage + shader-based sweep material. `_SweepOffset` animated 0→1 over 2s. Color resolved from `IZoneEnvironmentProvider.GetZoneColor()`. After sweep, alpha fades to 0 over 0.5s.

## Acceptance Criteria

1. **Fire hit VFX**: When fire damage lands, an orange fast-burn burst plays at the hit position for 0.3s.
2. **Ice shard spray**: When ice damage lands, white shards burst for 0.4s.
3. **Lightning arc**: When lightning damage lands, a bolt arc plays for 0.2s.
4. **Death VFX per element**: Each element spawns its configured death VFX with correct visual and duration.
5. **Zone restore color sweep**: When `ZoneRestoredEvent` fires, a full-screen sweep plays using the zone's environment color.
6. **Level-up burst by element**: Level-up burst uses the last equipped skill's element for visual resolution.
7. **Ground decal on death**: When an enemy dies, a pooled decal projector spawns at death position matching the killing element.
8. **Decal cleanup on zone transition**: When `GameStateChanged(HeroCamp)` fires, all decals are despawned.
9. **Synergy VFX hook returns null**: `ResolvePairVfx(Element, Element)` returns null for all pairs.
10. **Intensity scaling active**: Late-wave VFX shows visibly higher particle count (1.5x).

## Test Evidence Path

- `Assets/_TinyRift/Tests/PlayMode/VfxSystem/ElementalVfxLibraryTests.cs`
- Visual evidence docs in `production/qa/evidence/vfx-elemental-library/`
- Per-element VFX verified: correct prefab, duration, pool behavior

## Dependencies

- **VFX Story 001** — `IVfxService` event consumption, `PoolManager` integration, `VfxHandle` lifecycle
- **Zone Definition System** — `IZoneEnvironmentProvider.GetZoneColor()` for sweep color

## Unlocks

- Skill Presentation Adapter (consumes `IVfxService` for per-skill cast VFX)

## Risks

- **HIGH**: URP 17.3 RenderGraph may affect custom shader materials for zone sweep. Mitigation: zone sweep uses Canvas + RawImage with MaterialPropertyBlock (no CommandBuffer), making it RenderGraph-safe.
- **MEDIUM**: 64 concurrent decals at high kill density may cause visual degradation. Mitigation: circular buffer reclaims oldest first; no error log — expected at high density.
