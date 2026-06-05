# Zone Definition System

> **Status**: Designed
> **Author**: game-designer
> **Last Updated**: 2026-05-29
> **Creative Director Review (CD-GDD-ALIGN)**: APPROVED 2026-05-29
> **Implements Pillar**: P1 (Rifts Tell Stories) — zones are narrative containers. P4 (World Reactivity) — provides zone identity data consumed by World State for reactivity. P3 (Snappy Sessions) — zone configs must load fast.

## Overview

The Zone Definition System is a data layer providing ScriptableObject-based configurations that define each zone's identity and gameplay composition. For each zone, it stores: metadata (zoneId, displayName, description, visual theme), wave composition tables (enemy types, quantities, spawn timing per wave), elite spawn rules, boss encounter data, and environment cues (audio ambience, post-processing profile, memory color). The system is read-only at runtime — zone definitions are authored as ScriptableObject assets loaded at app start and referenced by ZoneId. Wave Spawning System consumes these definitions to drive runtime wave logic. Scene Manager provides the ZoneId-to-scene mapping; this system provides the per-zone gameplay config.

## Player Fantasy

The player never interacts with the Zone Definition System directly. They experience it as the conviction that each zone has a distinct identity — enemy compositions, wave pacing, and boss encounters that feel purposefully arranged to tell that zone's chapter of the world's story. Moving from zone to zone feels like descending deeper into the corpse of a fallen civilization: the Ash Wastes are crust (surface scars, sparse enemies, wide-open attrition), Crystal Caverns are bone (dense formations, corridor ambushes, crystal-shard elites), the Ash Circle is the heart (relentless pressure, boss as climax). Each zone teaches a different combat language — and the system that makes that possible is invisible.

## Detailed Design

### Core Rules

1. **ScriptableObject-based** — All zone definitions are authored as `ZoneDefinitionSO` assets (CreateAssetMenu). No runtime creation or mutation.

2. **ZoneDefinitionSO schema**:

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

[System.Serializable]
public struct ZoneMetadata
{
    public string displayName;
    public string description;
    public string scenePath;
    public VisualTheme visualTheme;
}

public enum ZoneDifficulty { Easy, Medium, Hard }
public enum VisualTheme { Wasteland, Crystal, Ash }

[System.Serializable]
public struct WaveTableEntry
{
    public int waveIndex;
    public float preWaveDelay;
    public float duration;
    public List<SpawnGroup> spawnGroups;
}

[System.Serializable]
public struct SpawnGroup
{
    public string enemyId;
    public int count;
    public float spawnInterval;
    public string spawnPatternId;
}

[System.Serializable]
public struct EliteSpawnConfig
{
    public List<EliteEntry> elites;
    public int firstWave;
    public int interval;
    public float baseProbability;
    public float probabilityGrowthPerInterval;
}

[System.Serializable]
public struct EliteEntry
{
    public string eliteId;
    public float weight;
}

[System.Serializable]
public struct BossEncounterData
{
    public string bossId;
    public int triggerWave;
    public float introDelay;
    public List<BossPhase> phases;
}

[System.Serializable]
public struct BossPhase
{
    public int phaseIndex;
    public float healthPercent;
    public string attackPatternId;
    public string telegraphVfxId;
}

[System.Serializable]
public struct EnvironmentCues
{
    public string ambienceId;
    public string musicTrackId;
    public string postProcessingProfileId;
    public string memoryColorId;
    public string zoneEntryTitleCardId;
}
```

3. **Loading and indexing** — A `ZoneBootstrap` (VContainer `IInitializable` registered in `TinyRiftScope`) loads all `ZoneDefinitionSO` assets into a `Dictionary<string, ZoneDefinitionSO>` at app start and registers `IZoneDefinitionRegistry` as a singleton. Registry is read-only after initialization.

4. **ZoneId** — A `readonly struct` wrapping a string for type safety. Consistent with Scene Manager's convention.

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

5. **Wave composition resolution** — Wave Spawning System calls `registry.GetZone(zoneId).waveTable[waveIndex]` to get the `WaveTableEntry` for the next wave, then iterates `spawnGroups` spawning enemies. Elite insertion is a separate probability check per eligible wave. Boss trigger fires when `currentWave >= bossEncounter.triggerWave`.

6. **Missing zone handling** — If a zone asset fails to load (missing SO, deserialization error), the registry logs a warning and initializes without that zone. `HasZone()` returns false. Callers must check `HasZone()` before querying.

### States and Transitions

No runtime state machine. Single lifecycle:

| Phase | Description |
|-------|-------------|
| Initialize | `ZoneBootstrap` loads all SOs, builds registry dictionary, registers `IZoneDefinitionRegistry` |
| Ready | Registry available for querying. Remains for entire app lifetime. |
| (shutdown) | Registry garbage-collected with scope |

One-way: `Initialize → Ready → (app exit)`. No pause, resume, or re-initialization.

### Interactions with Other Systems

**Interface segregation** — Multiple fine-grained interfaces, each consumed by a single downstream system:

```csharp
// Consumed by: Wave Spawning (#25)
public interface IWaveTableProvider
{
    WaveTableEntry GetWave(ZoneId zoneId, int waveIndex);
    int WaveCount(ZoneId zoneId);
    EliteSpawnConfig GetEliteSpawnConfig(ZoneId zoneId);
    BossEncounterData GetBossEncounterData(ZoneId zoneId);
}

// Consumed by: Audio System (#14)
public interface IZoneAudioProvider
{
    string GetAmbienceId(ZoneId zoneId);
    string GetMusicTrackId(ZoneId zoneId);
}

// Consumed by: VFX (#15), Post-Processing, Loading/Transition (#35)
public interface IZoneEnvironmentProvider
{
    string GetPostProcessingProfileId(ZoneId zoneId);
    string GetMemoryColorId(ZoneId zoneId);
    string GetZoneEntryTitleCardId(ZoneId zoneId);
}
```

**System interaction matrix:**

| System | Direction | What Flows | Contract |
|--------|-----------|------------|----------|
| Wave Spawning (#25) | Outbound | Wave table entries, elite rules, boss trigger | `IWaveTableProvider.GetWave()` called each new wave |
| Boss Encounter (#26) | Outbound | Boss ID, phase list, intro delay | `IWaveTableProvider.GetBossEncounterData()` at boss trigger wave |
| Scene Manager (#9) | Inbound | `ZoneId` via `GameStateContext.loadTarget` | Zone Definition does NOT call Scene Manager. ZoneId flows through GState context. Scene Manager uses its own `SceneRegistrySO` for scene mapping — Zone Definition's `scenePath` is a metadata reference, not runtime source of truth. |
| Audio System (#14) | Outbound | Ambience + music track IDs | `IZoneAudioProvider` on zone entry |
| VFX System (#15) / Post-Processing | Outbound | PP profile, memory color, title card | `IZoneEnvironmentProvider` on zone entry |
| World State (#13) | None | Zone Definition does not read/write world state | World State owns `ZoneCompletionEntry`. Zone Definition is unaware of completion tracking. |
| Save/Profile (#10) | None (game-flow only) | Player zone unlock data | Zone Definition does not call Save/Profile directly. The dependency is game-flow: player must have unlocked a zone (from Save data) before entering it, but Zone Definition itself is pure config — no save dependency at the code level. |
| Loading/Transition (#35) | Outbound | Title card key | Via `IZoneEnvironmentProvider.GetZoneEntryTitleCardId()` |

## Formulas

None. The Zone Definition System is a pure data container with no mathematical calculations. All values are authored directly in ScriptableObject fields.

## Edge Cases

- **If a zone asset's serialized data is corrupted** (null lists, zero values): `ZoneBootstrap` loads it with no validation, producing a zone that appears valid but has no functional content. Callers calling `GetWave(0)` on an empty `waveTable` throws `ArgumentOutOfRangeException`. **Remedy**: `IZoneDefinitionRegistry` validates each zone on load — at least 1 `waveTable` entry required, `waveTable[0]` must have at least 1 `spawnGroup`. Zones failing validation are excluded with a logged error.

- **If the zone asset is modified in the Inspector while the game is running**: Changes apply immediately to the live `ScriptableObject`. The one-way lifecycle has no reload mechanism, so mid-session modifications produce undefined behavior. **Remedy**: Not handled. This is a non-issue in release builds (scripts are built, no Inspector access). Development builds rely on discipline and the fact that zone data rarely changes during play sessions.

- **If two zones share the same `ZoneId`**: The second zone overwrites the first in the dictionary on insertion, silently losing the first zone's data. **Remedy**: `ZoneBootstrap` checks for duplicate `ZoneId` during load, logs a warning, and skips the duplicate.

- **If `bossEncounter.triggerWave > waveTable.Count`**: The boss trigger wave never arrives because the wave progression never reaches it. The boss encounter never activates. **Remedy**: Load-time validation on `ZoneDefinitionSO` — `triggerWave` must be ≤ `waveTable.Count` or the zone is logged as a warning (not excluded; the zone still loads and plays, just without its boss).

- **If all `spawnGroups` in a wave have `count = 0`**: The wave timer starts, runs to full duration, and zero enemies spawn — an empty wave blocking progression. **Remedy**: Load-time validation — each `WaveTableEntry` must have at least one `SpawnGroup` with `count > 0`. Failing waves log a warning.

- **If `eliteSpawn.elites` is empty but `baseProbability > 0`**: Elite probability rolls succeed but there are no elite types to select from. **Remedy**: `ZoneBootstrap` clamps `baseProbability` to 0 and logs a warning when `elites` is empty.

- **If `bossEncounter` is null** (no boss defined for this zone): Any code path that assumes `bossEncounter != null` throws `NullReferenceException`. **Remedy**: Boss data is a nullable struct in the API. `IWaveTableProvider.GetBossEncounterData()` returns a nullable. Consuming systems (Boss Encounter System) must check `HasValue` before reading.

- **If `baseProbability + probabilityGrowthPerInterval` exceeds 1.0**: Elite spawn probability exceeds 100%, guaranteeing an elite every eligible wave after enough intervals. **Remedy**: `EliteSpawnConfig` is a designer-tuned field. No runtime clamp — the designer is responsible for keeping this ≤ 1.0. A load-time warning is logged if the sum exceeds 1.0.

- **If `preWaveDelay` or `duration` is negative**: Negative durations cause timer systems to misbehave (wave never completes). **Remedy**: Load-time validation clamps negative duration values to 0. `preWaveDelay` clamps to ≥ 0.

- **If `ZoneId` is empty or whitespace**: Dictionary lookups match unintentionally. **Remedy**: `ZoneBootstrap` validates `ZoneId` is not null/empty/whitespace on load. Zones with empty `ZoneId` are excluded with a logged error.

## Dependencies

### Hard Dependencies

None at the code level. The Zone Definition System is a pure config layer — ScriptableObjects loaded at startup. It has no runtime dependencies on other systems.

### Soft Dependencies / Data Consumers

| System | Direction | What Flows | Contract |
|--------|-----------|------------|----------|
| Wave Spawning System (#25) | Outbound | Wave table entries, elite rules, boss trigger data | `IWaveTableProvider` |
| Boss Encounter System (#26) | Outbound | Boss ID, phase list, intro delay | `IWaveTableProvider.GetBossEncounterData()` |
| Audio System (#14) | Outbound | Ambience and music track IDs | `IZoneAudioProvider` |
| VFX System (#15) / Post-Processing | Outbound | PP profile, memory color ID | `IZoneEnvironmentProvider` |
| Loading/Transition System (#35) | Outbound | Title card key | `IZoneEnvironmentProvider.GetZoneEntryTitleCardId()` |

### Game-Flow Dependencies

| System | Nature |
|--------|--------|
| Save/Profile (#10) | Player must have unlocked a zone (from Save unlock state) before they can enter it. Zone Definition does not call Save directly — the dependency is at the game flow level, resolved by World State / Hero Camp Progression. |
| Scene Manager (#9) | `ZoneId` arrives via `GameStateContext.loadTarget`. Scene Manager uses its own `SceneRegistrySO` for scene path mapping — Zone Definition's `scenePath` is a metadata reference, not runtime source of truth. |

### Bidirectional Consistency

- Scene Manager lists "Zone Definition System — Provides `ZoneId` → scene name mapping (via registry)" and "Core Rule 5 requires ZoneId to be a string matching the Zone Definition System's key format" (✓ consistent)
- Save/Profile Persistence — does not reference Zone Definition directly. The dependency is resolved as game-flow only (✓ per clarification in this GDD)

## Tuning Knobs

All tuning knobs are authored per-zone in `ZoneDefinitionSO` ScriptableObject fields. There is no global runtime config — each zone carries its own values.

| Knob | Field | Type | Range | Typical Values | Owner |
|------|-------|------|-------|----------------|-------|
| Pre-wave delay | `WaveTableEntry.preWaveDelay` | float | 0–30s | 1–3s | Level designer |
| Wave duration | `WaveTableEntry.duration` | float | 5–120s | 20–60s | Level designer |
| Spawn interval | `SpawnGroup.spawnInterval` | float | 0.1–10s | 0.5–3s | Level designer |
| Enemies per group | `SpawnGroup.count` | int | 1–50 | 3–15 | Level designer |
| First elite wave | `EliteSpawnConfig.firstWave` | int | 1–∞ | 3–5 | Level designer |
| Elite recheck interval | `EliteSpawnConfig.interval` | int | 1–∞ | 2–4 | Level designer |
| Elite base probability | `EliteSpawnConfig.baseProbability` | float | 0.0–1.0 | 0.1–0.3 | Level designer |
| Elite probability growth | `EliteSpawnConfig.probabilityGrowthPerInterval` | float | 0.0–1.0 | 0.05–0.15 | Level designer |
| Boss trigger wave | `BossEncounterData.triggerWave` | int | 1–∞ | 5–8 | Level designer |
| Boss intro delay | `BossEncounterData.introDelay` | float | 0–10s | 1–3s | Level designer |

All knobs are designer-configured per zone asset. No runtime code changes needed to tune any zone.

## Acceptance Criteria

### Load & Initialization

- **AC1** — **GIVEN** a set of valid `ZoneDefinitionSO` assets with unique `ZoneId` values and populated `waveTable` entries, **WHEN** `ZoneBootstrap` executes, **THEN** `IZoneDefinitionRegistry` is registered as a singleton containing all loaded zones AND `HasZone()` returns `true` for each loaded `ZoneId`.

- **AC2** — **GIVEN** two `ZoneDefinitionSO` assets sharing the same `ZoneId`, **WHEN** `ZoneBootstrap` executes, **THEN** a duplicate-ID warning is logged AND the second occurrence is excluded from the registry.

- **AC3** — **GIVEN** a `ZoneDefinitionSO` with a null or whitespace `ZoneId`, **WHEN** `ZoneBootstrap` executes, **THEN** that zone is excluded from the registry AND a validation warning is logged.

- **AC4** — **GIVEN** a `ZoneDefinitionSO` whose `waveTable` is empty, **WHEN** `ZoneBootstrap` executes, **THEN** that zone is excluded from the registry AND a "minimum wave requirement not met" error is logged.

- **AC5** — **GIVEN** a `ZoneDefinitionSO` whose `bossEncounter.triggerWave` exceeds `waveTable.Count`, **WHEN** `ZoneBootstrap` executes, **THEN** a warning is logged AND `bossEncounter` is disabled for that zone (zone still loads and plays without boss encounter).

### Registry Queries

- **AC6** — **GIVEN** a loaded zone with `waveTable` of `N` entries, **WHEN** `GetWave(zoneId, i)` is called for `0 ≤ i < N`, **THEN** the returned `WaveTableEntry` matches the asset data at index `i`.

- **AC7** — **GIVEN** a `ZoneId` that was loaded and one that was not, **WHEN** `HasZone()` is called, **THEN** it returns `true` for the loaded ID and `false` for the missing one.

- **AC8** — **GIVEN** any `ZoneId` not present in the registry, **WHEN** `GetWave(zoneId, 0)` is called, **THEN** the return value is `null`.

- **AC9** — **GIVEN** a loaded zone with `waveTable` of size `N`, **WHEN** `WaveCount(zoneId)` is called, **THEN** it returns `N`.

### Interface Segregation

- **AC10** — **GIVEN** a loaded zone, **WHEN** accessed via `IWaveTableProvider`, **THEN** `GetWave()` returns a `WaveTableEntry` with `spawnGroups`, `preWaveDelay`, and `duration` matching the SO data.

- **AC11** — **GIVEN** a loaded zone, **WHEN** accessed via `IZoneAudioProvider`, **THEN** `GetAmbienceId()` returns the ambience ID AND `GetMusicTrackId()` returns the music track ID from the zone's environment cues.

- **AC12** — **GIVEN** a loaded zone, **WHEN** accessed via `IZoneEnvironmentProvider`, **THEN** `GetPostProcessingProfileId()`, `GetMemoryColorId()`, and `GetZoneEntryTitleCardId()` return values matching the SO data.

### Edge Case Validation

- **AC13** — **GIVEN** zero `ZoneDefinitionSO` assets exist, **WHEN** `ZoneBootstrap` executes, **THEN** the registry is empty (`WaveCount` returns 0 for any query) AND no duplicate-ID or minimum-wave errors are logged.

- **AC14** — **GIVEN** a `ZoneDefinitionSO` whose `eliteSpawn.elites` list is empty but `baseProbability > 0`, **WHEN** the zone is loaded, **THEN** `baseProbability` is clamped to 0 AND a warning is logged.

- **AC15** — **GIVEN** a `WaveTableEntry` with `preWaveDelay = -1.5f`, **WHEN** the zone is loaded, **THEN** the stored `preWaveDelay` is clamped to `0f` AND a clamping warning is logged.

- **AC16** — **GIVEN** a `SpawnGroup` with `count = 0` in the only group of a `WaveTableEntry`, **WHEN** the zone is loaded, **THEN** a warning is logged for that wave index AND the wave is excluded from playable waves. **GIVEN** a `SpawnGroup` with `count = 0` alongside other groups with `count > 0`, **WHEN** the zone is loaded, **THEN** the zero-count group is silently skipped (no spawn) and valid groups continue to function.
