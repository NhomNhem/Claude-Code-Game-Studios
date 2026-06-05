# Story 003: SkillInstance C3 Compliance & Serialization

- **Epic**: Skill Data System
- **Layer**: Foundation
- **Type**: Integration
- **Priority**: P1 — Important (enables save/load, network sync reference format)
- **Estimate**: 2h
- **Manifest Version**: 2026-06-01

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-PLACEHOLDER-SKILL-012` | SkillInstance serializes via JsonUtility with skillDefinitionId + currentTier only | ✅ ADR-001 |

## ADR Guidance

**ADR-001 (VContainer DI Architecture):**
- SkillInstance is a pure data struct — no DI registration needed
- C3 constraint: no Unity Object references in data-layer types
- String-key references for cross-layer communication

**Control Manifest (Foundation Layer):**
- Foundation layer is pure data — no Unity Object refs to higher layers

## Description

Verify that `SkillInstance` is C3 compliant by testing its JSON serialization output. The `SkillInstance` struct has `[NonSerialized]` runtime-only fields (`Definition`, `CooldownTimer`, `OrbitCurrentAngle`, `IsActive`) and a `[SerializeField]` private `_skillDefinitionId` string that survives serialization. The JSON produced by `JsonUtility.ToJson()` must contain only `skillDefinitionId` (the string ID) and `currentTier` (int), with no Unity Object serialization artifacts.

This story also verifies the deserialization round-trip: JSON → `SkillInstance` restores the ID and tier, but `Definition` is null (must be re-resolved by the caller via `SkillRegistry`).

## Design

### SkillInstance Struct (reproduced from Story 002 for reference)

```csharp
[System.Serializable]
public struct SkillInstance
{
    [NonSerialized] public SkillDefinition Definition;    // Runtime only
    [SerializeField] private string _skillDefinitionId;   // Serializable
    public int CurrentTier;
    [NonSerialized] public float CooldownTimer;
    [NonSerialized] public float OrbitCurrentAngle;
    [NonSerialized] public bool IsActive;

    public string SkillDefinitionId => _skillDefinitionId;
    internal void SetSkillDefinitionId(string id) => _skillDefinitionId = id;
}
```

### Expected JSON

```json
{"skillDefinitionId":"skill_fire_orb","currentTier":1}
```

### Round-Trip Flow

```
SkillInstance (runtime)
  → JsonUtility.ToJson() → JSON string
  → JsonUtility.FromJson<SkillInstance>() → SkillInstance (Definition=null)
  → Caller resolves Definition via SkillRegistry.GetDefinition(skillDefinitionId)
```

## Acceptance Criteria

- [ ] **AC-11a**: `JsonUtility.ToJson()` on a `SkillInstance` with `CurrentTier=1` and valid `_skillDefinitionId` produces JSON containing `"skillDefinitionId":"skill_fire_orb"` and `"currentTier":1`, and does NOT contain Unity serialization artifacts (`"fileID"`, `"guid"`, `"prefabInstance"`).
- [ ] **AC-11b**: Runtime-only fields (`CooldownTimer`, `OrbitCurrentAngle`, `IsActive`) and `Definition` are excluded from JSON output.
- [ ] **AC-11c**: Deserialization round-trip: JSON → `JsonUtility.FromJson<SkillInstance>()` produces a struct with `SkillDefinitionId == "skill_fire_orb"`, `CurrentTier == 1`, and `Definition == null`.
- [ ] **AC-11d**: A default `SkillInstance` (all zero/empty) serializes to `{"skillDefinitionId":"","currentTier":0}`.

## Implementation Notes

*Derived from ADR-001 Implementation Guidelines and QA Lead review:*

- `[NonSerialized]` on struct fields works correctly with `JsonUtility` — excluded from output
- `[SerializeField] private string` is serialized as public field in JSON (Unity serialization convention)
- Round-trip leaves `Definition` null — callers must resolve via `SkillRegistry.GetDefinition(SkillDefinitionId)`
- `SkillInstance.SetSkillDefinitionId()` is `internal` — only SkillRegistry calls it. Consumers read via the public `SkillDefinitionId` property.

## Out of Scope

- Save/load system integration (handled by Save Profile epic)
- Network sync byte format (handled by Network epic)
- SkillInstance creation from deserialized data (caller resolves Definition via SkillRegistry)

## QA Test Cases

- **AC-11a**: JSON output format
  - Given: A `SkillInstance` with `_skillDefinitionId="skill_fire_orb"`, `CurrentTier=1`, `CooldownTimer=3.5`, `OrbitCurrentAngle=45.0`, `IsActive=true`, `Definition` set to a valid `SkillDefinition`
  - When: `JsonUtility.ToJson(instance)` is called
  - Then: JSON string contains `"skillDefinitionId":"skill_fire_orb"` and `"currentTier":1`; does NOT contain `"fileID"`, `"guid"`, `"prefabInstance"`, or Unity object ref patterns
  - Edge cases: SkillId with special chars `"skill_fire_orb_v2-beta"` (JSON-encodes correctly); long SkillId (256+ chars)

- **AC-11b**: Runtime fields excluded
  - Given: Same instance as AC-11a
  - When: JSON string is parsed
  - Then: No `"CooldownTimer"`, `"OrbitCurrentAngle"`, `"IsActive"`, or `"Definition"` keys present
  - Edge cases: `[NonSerialized]` on float fields with non-default values (3.5, 45.0) — still excluded

- **AC-11c**: Round-trip deserialization
  - Given: A JSON string `{"skillDefinitionId":"skill_fire_orb","currentTier":2}`
  - When: `JsonUtility.FromJson<SkillInstance>(json)` is called
  - Then: Result has `SkillDefinitionId == "skill_fire_orb"`, `CurrentTier == 2`, `Definition == null`
  - Edge cases: JSON with extra unknown fields (ignored by JsonUtility); JSON with `currentTier` as string `"2"` (JsonUtility does not coerce types — may fail)

- **AC-11d**: Default instance serialization
  - Given: `default(SkillInstance)` (all zero, empty string)
  - When: `JsonUtility.ToJson(instance)` is called
  - Then: Returns `{"skillDefinitionId":"","currentTier":0}`
  - Edge cases: `null` SkillId (it's a string, defaults to empty `""`)

## Test Evidence

- **Story Type**: Integration
- **Required evidence**: `Assets/_TinyRift/Tests/EditMode/SkillData/SkillInstanceSerializationTests.cs` — all 4 ACs as individual test methods
- **Status**: Not yet created

## Dependencies

- Depends on: Story 002 (SkillInstance struct definition + SkillRegistry)
- Unlocks: Save Profile serialization, Network sync format
