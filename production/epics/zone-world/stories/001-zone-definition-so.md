# Story 001: ZoneDefinitionSO

- **Epic**: Zone & World
- **System**: Zone Definition System
- **Type**: Config/Data
- **Priority**: P0
- **Estimate**: 3h
- **Status**: Ready
- **Last Updated**: 2026-06-02

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-zonedef-001` | ScriptableObject-based wave composition configs per zone | ✅ ADR-001 |
| `TR-zonedef-002` | Enemy spawn tables per zone | ✅ ADR-001 |
| `TR-zonedef-003` | Boss data per zone | ✅ ADR-001 |

## ADR Guidance

**ADR-001 (VContainer DI Architecture):**
- Interface-first: `IZoneDefinitionRegistry`, `IWaveTableProvider`, `IZoneAudioProvider`, `IZoneEnvironmentProvider`
- `ZoneBootstrap` as `IInitializable` in `TinyRiftScope`
- Registry is read-only dictionary after init

**Control Manifest (Core Layer):**
- `ZoneId` as `readonly struct` wrapping string for type safety
- Load-time validation (non-empty waveTable, valid ZoneId, no duplicate IDs)
- Missing zone: `HasZone()` check before querying

## Description

Create the `ZoneDefinitionSO` ScriptableObject asset schema defining each zone's metadata, wave composition tables, elite spawn rules, boss encounter data, and environment cues. Implement `ZoneBootstrap` to load all assets into an `IZoneDefinitionRegistry` at app start with load-time validation.

## Design

### ZoneDefinitionSO Schema

```csharp
[CreateAssetMenu(menuName = "TinyRift/Zone Definition")]
public class ZoneDefinitionSO : ScriptableObject
{
    public string zoneId;
    public ZoneMetadata metadata;
    public ZoneDifficulty difficulty;
    public List<WaveTableEntry> waveTable;
    public EliteSpawnConfig eliteSpawn;
    public BossEncounterData bossEncounter;
    public EnvironmentCues environmentCues;
}
```

### ZoneId Struct

```csharp
public readonly struct ZoneId : IEquatable<ZoneId>
{
    public string Value { get; }
    public ZoneId(string value) => Value = value;

    public static readonly ZoneId FracturedPass = new("zone_fractured_pass");
    public static readonly ZoneId CrystalCaverns = new("zone_crystal_caverns");
    public static readonly ZoneId AshCircle = new("zone_ash_circle");
}
```

### Registry Interface

```csharp
public interface IZoneDefinitionRegistry
{
    bool HasZone(ZoneId zoneId);
    ZoneDefinitionSO GetZone(ZoneId zoneId);
    int ZoneCount { get; }
}
```

### Load-Time Validation

| Check | Action |
|-------|--------|
| Empty/null/whitespace ZoneId | Exclude zone, log error |
| Duplicate ZoneId | Skip duplicate, log warning |
| Empty waveTable | Exclude zone, log "minimum wave requirement not met" |
| triggerWave > waveTable.Count | Disable boss encounter, log warning |
| Empty eliteSpawn.elites + baseProbability > 0 | Clamp probability to 0, log warning |
| Negative preWaveDelay/duration | Clamp to 0, log warning |
| All spawnGroups have count = 0 in a wave | Log warning per wave index |

### Interface Segregation

```csharp
public interface IWaveTableProvider { ... }
public interface IZoneAudioProvider { ... }
public interface IZoneEnvironmentProvider { ... }
```

## Acceptance Criteria

1. **GIVEN** valid `ZoneDefinitionSO` assets with unique ZoneIds and populated waveTable entries, **WHEN** `ZoneBootstrap` executes, **THEN** `IZoneDefinitionRegistry` is registered as singleton containing all loaded zones AND `HasZone()` returns `true` for each.
2. **GIVEN** two assets sharing the same ZoneId, **WHEN** `ZoneBootstrap` executes, **THEN** duplicate-ID warning is logged AND second occurrence is excluded.
3. **GIVEN** a zone with null/whitespace ZoneId, **WHEN** `ZoneBootstrap` executes, **THEN** that zone is excluded AND validation warning is logged.
4. **GIVEN** a zone with empty waveTable, **WHEN** `ZoneBootstrap` executes, **THEN** zone is excluded AND "minimum wave requirement not met" error is logged.
5. **GIVEN** `bossEncounter.triggerWave > waveTable.Count`, **WHEN** `ZoneBootstrap` executes, **THEN** warning logged AND boss encounter disabled for that zone.
6. **GIVEN** a loaded zone, **WHEN** accessed via `IWaveTableProvider`, **THEN** `GetWave()` returns correct `WaveTableEntry` with matching SO data.

## Test Evidence Path

- `Assets/_TinyRift/Tests/EditMode/ZoneWorld/ZoneDefinitionTests.cs`
- All 6 acceptance criteria as individual test methods
- ScriptableObject instances created via `ScriptableObject.CreateInstance` in tests

## Dependencies

- **None** (pure config layer, no runtime dependencies)

## Unlocks

- Zone Story 002: World State
- Wave Spawning System, Audio System, VFX System

## Risks

- **LOW**: ScriptableObject serialization issues in builds. Mitigation: all fields are serializable structs; SOs are loaded via Resources or Addressables.
