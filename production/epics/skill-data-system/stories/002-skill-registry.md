# Story 002: SkillRegistry — Lookup, Validation & Instance Lifecycle

- **Epic**: Skill Data System
- **Layer**: Foundation
- **Type**: Logic
- **Priority**: P0 — Blocking (all downstream systems consume skills through SkillRegistry)
- **Estimate**: 3h
- **Manifest Version**: 2026-06-01

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-PLACEHOLDER-SKILL-006` | SkillDatabase.GetAllSkillIds() returns all registered skill IDs | ✅ ADR-001 |
| `TR-PLACEHOLDER-SKILL-007` | Duplicate SkillId logs warning, last-loaded wins | ✅ ADR-001 |
| `TR-PLACEHOLDER-SKILL-008` | SkillRegistry.CreateInstance(id) creates tier-0 SkillInstance | ✅ ADR-001 |
| `TR-PLACEHOLDER-SKILL-009` | SkillRegistry.UpgradeInstance bumps tier | ✅ ADR-001 |
| `TR-PLACEHOLDER-SKILL-010` | UpgradeInstance at tier 2 is no-op | ✅ ADR-001 |
| `TR-PLACEHOLDER-SKILL-011` | GetDefinition(invalid_id) returns null | ✅ ADR-001 |

## ADR Guidance

**ADR-001 (VContainer DI Architecture):**
- `ISkillRegistry` as interface, `SkillRegistry` as implementation
- Singleton in `TinyRiftScope`
- Registration order-independent within Foundation batch

**Control Manifest (Foundation Layer):**
- Interface-first: consumers depend on `ISkillRegistry`, not `SkillRegistry`
- One registration per file

## Description

Implement the runtime `SkillRegistry` that bridges string IDs to `SkillDefinition` assets. The registry loads all definitions at startup, validates against duplicates, and exposes lookup, instance creation, and upgrade APIs. Downstream systems (Orbit Combat, Burst Skill, Rune Draft, HUD, etc.) never reference `SkillDefinition` assets directly — they go through `ISkillRegistry`.

## Design

```csharp
public interface ISkillRegistry
{
    SkillDefinition GetDefinition(string skillId);
    IReadOnlyCollection<string> GetAllSkillIds();
    SkillInstance CreateInstance(string skillId);
    SkillInstance UpgradeInstance(SkillInstance instance);
}

public class SkillRegistry : ISkillRegistry
{
    private readonly Dictionary<string, SkillDefinition> _definitions = new();
    private int _nextInstanceId;

    public SkillRegistry(List<SkillDefinition> allDefinitions)
    {
        foreach (var def in allDefinitions)
        {
            if (_definitions.ContainsKey(def.SkillId))
            {
                Debug.LogWarning($"SkillRegistry: Duplicate SkillId '{def.SkillId}' — last loaded wins.");
                _definitions[def.SkillId] = def;
            }
            else
            {
                _definitions.Add(def.SkillId, def);
            }
        }
    }

    public SkillDefinition GetDefinition(string skillId)
    {
        if (skillId == null)
            throw new ArgumentNullException(nameof(skillId));

        _definitions.TryGetValue(skillId, out var def);
        return def; // null if not found
    }

    public IReadOnlyCollection<string> GetAllSkillIds()
        => _definitions.Keys;

    public SkillInstance CreateInstance(string skillId)
    {
        var def = GetDefinition(skillId);
        if (def == null)
        {
            Debug.LogError($"SkillRegistry: CreateInstance called with invalid SkillId '{skillId}'.");
            return default;
        }

        return new SkillInstance
        {
            Definition = def,
            CurrentTier = 0,
            CooldownTimer = 0f,
            OrbitCurrentAngle = 0f,
            IsActive = false
        };
    }

    public SkillInstance UpgradeInstance(SkillInstance instance)
    {
        if (instance.Definition == null)
        {
            Debug.LogError("SkillRegistry: UpgradeInstance called on instance with null Definition.");
            return instance;
        }

        if (instance.CurrentTier >= 2)
            return instance; // no-op at max tier

        instance.CurrentTier++;
        return instance;
    }
}
```

### SkillInstance Struct (C3 Compliant)

```csharp
[System.Serializable]
public struct SkillInstance
{
    [NonSerialized] public SkillDefinition Definition;    // Runtime only — not serialized
    [SerializeField] private string _skillDefinitionId;   // Serializable ID reference
    public int CurrentTier;
    [NonSerialized] public float CooldownTimer;           // Runtime only
    [NonSerialized] public float OrbitCurrentAngle;       // Runtime only
    [NonSerialized] public bool IsActive;                 // Runtime only

    public string SkillDefinitionId => _skillDefinitionId;

    // Called by SkillRegistry when creating/loading instances
    internal void SetSkillDefinitionId(string id) => _skillDefinitionId = id;
}
```

## Acceptance Criteria

- [ ] **AC-2**: `GetAllSkillIds()` returns exactly 5 string IDs for a registry initialized with 5 `SkillDefinition` assets with unique IDs.
- [ ] **AC-3**: Two definitions with the same `SkillId` log a warning containing `"duplicate"` and `"skill_fire_orb"`. The last-loaded definition wins.
- [ ] **AC-4**: `CreateInstance("skill_fire_orb")` returns a `SkillInstance` with `Definition != null`, `Definition.SkillId == "skill_fire_orb"`, `CurrentTier == 0`, `CooldownTimer == 0`, `OrbitCurrentAngle == 0`, `IsActive == false`.
- [ ] **AC-5**: `UpgradeInstance()` on a tier-0 instance returns a new instance with `CurrentTier == 1`, `Definition` unchanged, other fields preserved.
- [ ] **AC-6**: `UpgradeInstance()` on a tier-2 instance returns the same instance (no-op). Multiple calls are idempotent.
- [ ] **AC-7**: `GetDefinition("nonexistent")` returns `null`. `GetDefinition("")` returns `null`. `GetDefinition(null)` throws `ArgumentNullException`.

## Implementation Notes

*Derived from ADR-001 Implementation Guidelines:*

- SkillRegistry is registered as `ISkillRegistry` singleton in TinyRiftScope
- SkillDatabase ScriptableObject feeds the list of SkillDefinition assets to SkillRegistry at construction
- ID lookup is case-sensitive (`"skill_Fire_Orb"` ≠ `"skill_fire_orb"`)
- Duplicate detection logs a warning per GDD Edge Cases — last-loaded wins

## Out of Scope

- [Story 001]: SkillDefinition ScriptableObject schema and OnValidate
- [Story 003]: SkillInstance serialization format and round-trip testing

## QA Test Cases

- **AC-2**: GetAllSkillIds correct count
  - Given: A SkillRegistry initialized with 5 definitions: `["skill_fire_orb", "skill_ice_shard", "skill_lightning_bolt", "skill_fire_blast", "skill_wind_blade"]`
  - When: `GetAllSkillIds()` is called
  - Then: Returns a collection with exactly 5 elements, all unique, matching the input set
  - Edge cases: Registry with 0 definitions (returns empty); Registry with 50+ definitions (no crash)

- **AC-3**: Duplicate ID warning
  - Given: Two definitions with `SkillId = "skill_fire_orb"`, second has `BaseDamage = 20` (first has 15)
  - When: Registry is constructed
  - Then: `Debug.LogWarning` called with `"duplicate"` + `"skill_fire_orb"`; `GetDefinition("skill_fire_orb").BaseDamage` == 20
  - Edge cases: 3+ duplicates; duplicate where second def has empty/null fields (last-wins may corrupt data)

- **AC-4**: CreateInstance at tier 0
  - Given: Registry contains `"skill_fire_orb"` definition
  - When: `CreateInstance("skill_fire_orb")` is called
  - Then: `Instance.CurrentTier == 0`, `Definition.SkillId == "skill_fire_orb"`, `CooldownTimer == 0`, `OrbitCurrentAngle == 0`, `IsActive == false`
  - Edge cases: Two calls return independent instances (struct copy); instance with invalid ID returns default

- **AC-5**: UpgradeInstance tier 0→1
  - Given: A SkillInstance at `CurrentTier = 0`
  - When: `UpgradeInstance(instance)` is called
  - Then: Returned instance has `CurrentTier == 1`, same `Definition`, `CooldownTimer` preserved
  - Edge cases: Sequential upgrades 0→1→2; upgrade on null-definition instance

- **AC-6**: UpgradeInstance at tier 2 is no-op
  - Given: A SkillInstance at `CurrentTier = 2`
  - When: `UpgradeInstance(instance)` is called
  - Then: Returned instance has `CurrentTier == 2`, all fields equal to input
  - Edge cases: Multiple no-op calls (idempotent); tier values above 2 (clamp? no-op? not specified — implement as no-op)

- **AC-7**: Invalid ID returns null
  - Given: A Registry with no `"skill_nonexistent"` entry
  - When: `GetDefinition("skill_nonexistent")` is called
  - Then: Returns `null`
  - Edge cases: `GetDefinition("")` returns `null`; `GetDefinition(null)` throws `ArgumentNullException`; case mismatch `"SKILL_FIRE_ORB"` vs `"skill_fire_orb"` returns `null`

## Test Evidence

- **Story Type**: Logic
- **Required evidence**: `Assets/_TinyRift/Tests/EditMode/SkillData/SkillRegistryTests.cs` — all 6 ACs as individual test methods
- **Status**: Not yet created

## Dependencies

- Depends on: Story 001 (SkillDefinition schema — must exist as a type)
- Unlocks: Story 003 (SkillInstance serialization)
