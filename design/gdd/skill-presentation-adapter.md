# Skill Presentation Adapter

> **Status**: Designed

> **System ID**: #32 (was #34) | **Layer**: Meta | **MVP**: Yes
> **Depends on**: Hit Detection (#8), Damage & Health (#19), Skill Data (#3), VFX (#15), Audio (#14)

## 1. Overview

The Skill Presentation Adapter bridges the gap between abstract skill data and concrete visual/audio presentation. It maps `SkillDefinition` data (element, type, projectile key) to VFX prefabs, audio cues, and animation timing. This is an adapter layer — it does not contain gameplay logic, only presentation routing.

## 2. Detailed Rules

- `ISkillPresentationAdapter` — injected, resolves `ProjectileKey → VfxPrefab`, `SkillId → CastAnimationTiming`
- `ProjectileRegistry` — ScriptableObject dictionary: string key → GameObject prefab reference
- Consumed by Orbit Combat and Burst Skill on activation/skill spawn
- Routes:
  - `GetCastVfx(SkillId) → VfxKey` for cast VFX (elemental burst at player position)
  - `GetProjectile(ProjectileKey) → GameObject` from pool
  - `GetHitVfx(ElementType) → VfxKey` for hit impacts
  - `GetCastSound(SkillId) → AudioCueKey` for cast SFX
  - `GetAnimationTiming(SkillId) → CastTiming` (wind-up frames, active frames, recovery)
- All references are resolved at startup into lookup tables — no runtime string-to-asset resolution on hot path

## 3. ACs

1. ProjectileKey resolves to pooled projectile prefab
2. Cast VFX resolves and plays on skill activation
3. Hit VFX resolves per element type
4. Cast audio cue plays on skill activation
5. Animation timing returned in structured CastTiming
6. Missing key returns null with warning log
7. All lookups pre-resolved at startup
