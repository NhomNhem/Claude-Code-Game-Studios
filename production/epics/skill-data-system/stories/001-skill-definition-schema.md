# Story 001: SkillDefinition ScriptableObject Data Schema

- **Epic**: Skill Data System
- **Layer**: Foundation
- **Type**: Logic (with Editor sub-type for AC 12)
- **Priority**: P0 — Blocking (all downstream systems read SkillDefinition fields)
- **Estimate**: 5h
- **Manifest Version**: 2026-06-01
- **Status**: Complete
- **Last Updated**: 2026-06-02

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-PLACEHOLDER-SKILL-001` | SkillDefinition ScriptableObject with identity, mechanics, upgrade, narrative, presentation fields | ✅ ADR-001 |
| `TR-PLACEHOLDER-SKILL-002` | OnValidate warnings for BaseDamage=0 or negative | ✅ ADR-001 |
| `TR-PLACEHOLDER-SKILL-003` | Orbit type validates orbit fields non-zero, burst fields zero | ✅ ADR-001 |
| `TR-PLACEHOLDER-SKILL-004` | Burst type validates burst fields non-zero, orbit fields zero | ✅ ADR-001 |
| `TR-PLACEHOLDER-SKILL-005` | Inspector exposes string keys as text fields, not object pickers | ✅ ADR-001 |

## ADR Guidance

**ADR-001 (VContainer DI Architecture):**
- Interface-first: `ISkillRegistry` consumed by all systems, not concrete `SkillRegistry`
- Singleton in `TinyRiftScope`
- `SkillDefinition` ScriptableObject assets are pure data — no DI registration needed

**Control Manifest (Foundation Layer):**
- One registration per file
- Foundation registration batch is order-independent

## Description

Implement the `SkillDefinition` ScriptableObject data schema and its supporting enums and structs. Every skill in the game is defined by one `SkillDefinition` asset containing identity, mechanics, upgrades, narrative, and presentation fields. The schema is C3 compliant — pure data references (IDs/keys/enums) only, no Unity Object refs to higher-layer prefabs.

## Design

### Enums

```csharp
public enum SkillType { Orbit, Burst }
public enum ElementType { None = 0, Fire, Ice, Lightning }
public enum Rarity { Common, Uncommon, Rare }
public enum TargetPriority { None = 0, Nearest, LowestHp, Random }

[Flags]
public enum DamageTypeFlags
{
    None = 0,
    Projectile = 1 << 0,
    Melee = 1 << 1,
    Aoe = 1 << 2,
    Dot = 1 << 3
}
```

### SkillUpgradeTier Struct

```csharp
[System.Serializable]
public struct SkillUpgradeTier
{
    public int TierLevel;
    public string UpgradeNameKey;
    public string UpgradeDescriptionKey;
    public float DamageMultiplier;
    public float CooldownMultiplier;
    public int AdditionalProjectiles;
    public float AdditionalAoeRadius;
    public float AdditionalOrbitSpeed;
    public string UpgradeVfxKey;
    public string SynergyOverrideKey;
}
```

### SkillDefinition ScriptableObject

```csharp
public class SkillDefinition : ScriptableObject
{
    [Header("Identity")]
    public string SkillId;
    public string SkillNameKey;
    public SkillType SkillType;
    public ElementType ElementType;
    public Rarity Rarity;

    [Header("Mechanics — Shared")]
    public float BaseDamage;
    public float CooldownSeconds;
    public DamageTypeFlags DamageTypeFlags;

    [Header("Mechanics — Orbit")]
    public float OrbitSpeed;
    public float OrbitRadius;
    public int ProjectileCount;
    public TargetPriority TargetPriority;
    public string ProjectileKey;

    [Header("Mechanics — Burst")]
    public float CastRange;
    public float AoeRadius;
    public float AimAngle;

    [Header("Upgrades")]
    public SkillUpgradeTier[] UpgradeTiers;

    [Header("Narrative")]
    public string LoreFragmentKey;
    public string ZoneAffinityKey;

    [Header("Presentation")]
    public string IconKey;
    public Color ElementColor;
    public string VfxProfileKey;
    public string HitVfxKey;
    public string AudioCueKey;
    public string HitAudioCueKey;
    public string PresentationProfileKey;

    private void OnValidate()
    {
        if (BaseDamage <= 0f)
            Debug.LogWarning($"SkillDefinition [{SkillId}]: BaseDamage ({BaseDamage}) is zero or negative.");
        if (SkillType == SkillType.Orbit && string.IsNullOrEmpty(ProjectileKey))
            Debug.LogWarning($"SkillDefinition [{SkillId}]: Orbit type has no ProjectileKey.");
        if (SkillType == SkillType.Burst && string.IsNullOrEmpty(ProjectileKey))
            Debug.LogWarning($"SkillDefinition [{SkillId}]: Burst type has no ProjectileKey.");
    }
}
```

## Acceptance Criteria

*From GDD `design/gdd/skill-data-system.md`, scoped to this story:*

- [ ] **AC-1**: A `SkillDefinition` asset created with all fields populated returns every field exactly as authored when read. The full field list validated:
  - **Identity**: `SkillId`, `SkillNameKey`, `SkillType`, `ElementType`, `Rarity`
  - **Shared mechanics**: `BaseDamage`, `CooldownSeconds`, `DamageTypeFlags`
  - **Orbit**: `OrbitSpeed`, `OrbitRadius`, `ProjectileCount`, `TargetPriority`, `ProjectileKey`
  - **Burst**: `CastRange`, `AoeRadius`, `AimAngle`
  - **Upgrades**: 3 `SkillUpgradeTier` entries with all 10 sub-fields populated
  - **Narrative**: `LoreFragmentKey`, `ZoneAffinityKey`
  - **Presentation**: `IconKey`, `ElementColor`, `VfxProfileKey`, `HitVfxKey`, `AudioCueKey`, `HitAudioCueKey`, `PresentationProfileKey`
- [ ] **AC-8**: `BaseDamage = 0` (and negative values) log a warning via `OnValidate()`. The asset remains accessible and is not rejected.
- [ ] **AC-9**: `SkillType = Orbit` → orbit fields (`OrbitSpeed`, `OrbitRadius`, `ProjectileCount`, `TargetPriority`) are non-zero; burst fields (`CastRange`, `AoeRadius`, `AimAngle`) are zero. This is a data-structure assertion (field values read from the instance), not an OnValidate check. `TargetPriority` uses `None = 0` enum sentinel so `TargetPriority != TargetPriority.None` is the correct assertion.
- [ ] **AC-10**: `SkillType = Burst` → burst fields (`CastRange`, `AoeRadius`, `AimAngle`) are non-zero; orbit fields (`OrbitSpeed`, `OrbitRadius`, `ProjectileCount`, `TargetPriority`) are zero; shared fields (`BaseDamage`, `CooldownSeconds`) are independent of type. This is a data-structure assertion (field values read from the instance), not an OnValidate check.
- [ ] **AC-12 (Editor)**: In the Unity Inspector, all string key fields (`SkillId`, `SkillNameKey`, `IconKey`, `VfxProfileKey`, `HitVfxKey`, `AudioCueKey`, `HitAudioCueKey`, `PresentationProfileKey`, `ProjectileKey`, `LoreFragmentKey`, `ZoneAffinityKey`, `UpgradeTiers[].UpgradeNameKey`, `UpgradeTiers[].UpgradeDescriptionKey`, `UpgradeTiers[].UpgradeVfxKey`, `UpgradeTiers[].SynergyOverrideKey`) are editable text fields (`SerializedPropertyType.String`), not object pickers.

## Implementation Notes

*Derived from ADR-001 Implementation Guidelines:*

- SkillDefinition is a pure data ScriptableObject — no MonoBehaviour, no GameObject references
- `OnValidate()` for data integrity warnings only — no asset rejection, no crash
- All string keys are plain `string` fields, not `AssetReference` or object picker types (C3 enforcement)
- `SkillUpgradeTier[3]` array size is a hard design decision; `OnValidate` may log a warning if length != 3
- AC-9/10 are data-structure assertions (field values read from instance in test), not OnValidate warnings — the OnValidate method only checks BaseDamage and ProjectileKey per the Design section

## Out of Scope

- [Story 002]: SkillRegistry runtime lookup, CreateInstance, UpgradeInstance, duplicate ID detection
- [Story 003]: SkillInstance serialization format, C3 compliance verification via serialization

## QA Test Cases

- **AC-1**: Full field round-trip
  - Given: A `SkillDefinition` created via `ScriptableObject.CreateInstance<SkillDefinition>()` with all ~30 fields populated with distinct non-default values
  - When: Each field is read directly from the instance
  - Then: Every field matches the authored value. Test enumerates the full field list from the schema above.
  - Edge cases: Default-constructed definition (all zero/empty — no throw); `float.MaxValue` / `int.MaxValue` fields; `DamageTypeFlags = None` enum zero-value

- **AC-8**: BaseDamage zero/negative warning
  - Given: A `SkillDefinition` with `BaseDamage = 0`
  - When: `OnValidate()` is invoked
  - Then: `Debug.LogWarning` is called with a message containing `"BaseDamage"`
  - Edge cases: `BaseDamage = -1` (also warns); `BaseDamage = float.Epsilon` (non-zero, does NOT warn)

- **AC-9**: Orbit type field validation (data-structure test)
  - Given: A `SkillDefinition` with `SkillType = Orbit`, all orbit fields non-zero, all burst fields zero
  - When: Fields are read
  - Then: `OrbitSpeed > 0`, `OrbitRadius > 0`, `ProjectileCount > 0`, `TargetPriority != TargetPriority.None`, `CastRange == 0`, `AoeRadius == 0`, `AimAngle == 0`
  - Edge cases: Orbit with `OrbitSpeed = 0` (invalid data — no AC, but a concern); Orbit with `AoeRadius > 0` (both type's fields set — invalid)

- **AC-10**: Burst type field validation (data-structure test)
  - Given: A `SkillDefinition` with `SkillType = Burst`, all burst fields non-zero, all orbit fields zero
  - When: Fields are read
  - Then: `CastRange > 0`, `AoeRadius >= 0`, `AimAngle > 0`, `OrbitSpeed == 0`, `OrbitRadius == 0`, `ProjectileCount == 0`, `TargetPriority == TargetPriority.None`; shared fields (`BaseDamage`, `CooldownSeconds`) are independent of type
  - Edge cases: Burst with `ProjectileCount > 0` (orbit field set on burst — invalid); `AoeRadius = 0` on an AoE-type burst

- **AC-12**: Inspector text fields (Editor)
  - Given: A `SkillDefinition` asset inspected via `SerializedProperty`
  - When: Each string field's `SerializedProperty.propertyType` is checked
  - Then: All string fields (see full list in AC-12) have `propertyType == SerializedPropertyType.String`, not `ObjectReference`
  - Edge cases: Nested `SkillUpgradeTier` sub-fields require `SerializedProperty` path traversal

## Test Evidence

- **Story Type**: Logic (ACs 1, 8, 9, 10) + Editor sub-type (AC 12)
- **Required evidence**:
  - `Assets/_TinyRift/Tests/EditMode/SkillData/SkillDefinitionSchemaTests.cs` — ACs 1, 8, 9, 10
  - `Assets/_TinyRift/Tests/Editor/SkillData/SkillDefinitionEditorTests.cs` — AC 12 (in `Editor/` folder, `#if UNITY_EDITOR` guard)
- **Status**: Not yet created

## Dependencies

- **None** — pure ScriptableObject + serialization, no upstream dependencies

## Completion Notes
**Completed**: 2026-06-02
**Criteria**: 5/5 passing (AC-1 round-trip, AC-8 BaseDamage warning, AC-9 orbit shape, AC-10 burst shape, AC-12 inspector strings)
**Files Added**:
- `Assets/_TinyRift/Runtime/SkillData/SkillType.cs`
- `Assets/_TinyRift/Runtime/SkillData/ElementType.cs`
- `Assets/_TinyRift/Runtime/SkillData/Rarity.cs`
- `Assets/_TinyRift/Runtime/SkillData/TargetPriority.cs`
- `Assets/_TinyRift/Runtime/SkillData/DamageTypeFlags.cs` ([Flags])
- `Assets/_TinyRift/Runtime/SkillData/SkillUpgradeTier.cs` ([Serializable] struct)
- `Assets/_TinyRift/Runtime/SkillData/SkillDefinition.cs` (ScriptableObject, OnValidate)
- `Assets/_TinyRift/Tests/EditMode/SkillData/SkillDefinitionSchemaTests.cs` (5 tests)
- `Assets/_TinyRift/Tests/Editor/SkillData/SkillDefinitionEditorTests.cs` (1 test)
**Deviations**: None — pure data schema per C3, no DI registration, all string keys are plain string fields
**Engine Risk**: LOW (ScriptableObject + serialization only, no runtime DI)
