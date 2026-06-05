# Story 001: Core Persistence Layer

- **Epic**: Save & Profile
- **System**: Save/Profile Persistence
- **Type**: Logic
- **Priority**: P0
- **Estimate**: 4h
- **Status**: Ready
- **Last Updated**: 2026-06-02

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-saveprofile-001` | PersistStateAsync() writes persistent.json with correct gold/playerId | ✅ ADR-006 |
| `TR-saveprofile-002` | Defeat autosave adds run gold, deletes runstate.json | ✅ ADR-006 |
| `TR-saveprofile-003` | Victory autosave adds gold, updates zoneCompletions, deletes runstate | ✅ ADR-006 |
| `TR-saveprofile-012` | Fresh first launch: both files created with defaults | ✅ ADR-006 |
| `TR-saveprofile-027` | Atomic write pattern (temp→rename) | ✅ ADR-006 |
| `TR-saveprofile-028` | 5 autosave triggers: HeroCamp entry, in-camp spend, Defeat, Victory, runstate | ✅ ADR-006 |
| `TR-saveprofile-029` | JSON via Newtonsoft.Json, all fields [JsonProperty] | ✅ ADR-006 |

## ADR Guidance

**ADR-006 (Save/Profile Serialization):**
- JSON via Newtonsoft.Json with atomic writes
- Single `persistent.json` consolidation (one atomic write covers all persistent fields)
- `[JsonProperty]` on all serialized fields for IL2CPP preservation
- Atomic write pattern: write to `.tmp`, verify, rename to target
- `link.xml` preserves all save schema types

**ADR-001 (VContainer DI Architecture):**
- `IPersistStateService` interface singleton in `TinyRiftScope`

## Description

Implement the core persistence layer: `IPersistStateService` with atomic file writes, Newtonsoft.Json serialization, autosave on game state transitions, and fresh-profile initialization. All persistent data is consolidated into `persistent.json`; ephemeral run state uses `runstate.json`.

## Design

### File Schema

- **persistent.json**: Consolidated persistent data (profile, world, settings). Written atomically (temp → rename).
- **runstate.json**: Ephemeral per-run state (cleared on run end). Not part of any transaction.

### Atomic Write Pattern

```csharp
string tempPath = path + ".tmp";
string backupPath = path + ".bak";
File.WriteAllText(tempPath, json);  // write to temp
// Verify integrity
File.Move(path, backupPath, overwrite: true);  // backup original
File.Move(tempPath, path);  // atomic rename
File.Delete(backupPath);
```

### Autosave Triggers

| Trigger | Action |
|---------|--------|
| HeroCamp entry (Loading → HeroCamp) | Save persistent.json |
| In-camp currency spend | Save persistent.json |
| Defeat (InRun → Defeat) | Add run gold to persistent.json, delete runstate.json |
| Victory (InRun → Victory) | Add gold, update zoneCompletions, delete runstate.json |
| Run state change | Save runstate.json (dirty-flag) |

### Fresh First Launch

If no `persistent.json` exists at init:
- Create both files with default values (empty playerId, gold=0, current saveVersion)
- Log info about first launch

### Newtonsoft.Json Configuration

- `MissingMemberHandling.Ignore` for forward compatibility
- All fields annotated with `[JsonProperty("name")]`
- `PersistentSaveData` and `RunStateSaveData` classes with serializable schema

## Acceptance Criteria

1. **GIVEN** `CurrentState == HeroCamp` AND `AuthService.CurrentPlayerId` returns `"player_123"` AND gold = 1000, **WHEN** `PersistStateAsync()` completes, **THEN** `persistent.json` exists AND `gold == 1000` AND `playerId == "player_123"`.
2. **GIVEN** `goldEarnedThisRun = 500` AND GState transitions to Defeat, **WHEN** autosave completes, **THEN** `persistent.json.gold` equals pre-run gold + 500 AND `runstate.json` does NOT exist.
3. **GIVEN** `goldEarnedThisRun = 300` AND GState transitions to Victory, **WHEN** autosave completes, **THEN** `persistent.json.zoneCompletions` contains an entry with correct `zoneId` AND `completed == true` AND `runstate.json` does NOT exist.
4. **GIVEN** no files exist in `persistentDataPath`, **WHEN** initialization completes, **THEN** both `persistent.json` and `runstate.json` exist with default values and current `saveVersion`.
5. **GIVEN** any write to `persistent.json`, **WHEN** the write completes, **THEN** the temp→rename pattern was used (original file never truncated) AND the final file contains valid JSON.
6. **GIVEN** autosave triggers: HeroCamp entry, in-camp spend, Defeat, Victory, AND runstate change, **WHEN** each trigger fires, **THEN** `PersistStateAsync()` is called (or runstate is written) exactly once per trigger.
7. **GIVEN** the deserialized data, **WHEN** all `PersistentSaveData` fields are inspected, **THEN** each field has a `[JsonProperty]` attribute with a valid key name.

## Test Evidence Path

- `Assets/_TinyRift/Tests/EditMode/SaveProfile/PersistStateServiceCoreTests.cs`
- All 7 acceptance criteria as individual test methods
- Mock file system for atomic write verification
- Verify JSON output schema matches expected format

## Dependencies

- **None** (file I/O only)

## Unlocks

- Save Story 002: Version Migration & Corruption Recovery
- Save Story 003: Fault Tolerance
- Save Story 004: Conflict Resolution
- Save Story 005: Concurrency & Throttling
- Save Story 006: Orphan Recovery
- Save Story 007: Pre-Save Validation
- Save Story 008: Account/Profile System

## Risks

- **MEDIUM**: IL2CPP AOT stripping — `[JsonProperty]` + `link.xml` must be present before device builds. Mitigation: link.xml added in this story, verified in test.
