# Story 002: Version Migration & Corruption Recovery

- **Epic**: Save & Profile
- **System**: Save/Profile Persistence
- **Type**: Logic
- **Priority**: P0
- **Estimate**: 3h
- **Status**: Ready
- **Last Updated**: 2026-06-02

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-saveprofile-004` | Version migration upgrades old saveVersion | ✅ ADR-006 |
| `TR-saveprofile-005` | Newer saveVersion rejected with warning, file preserved | ✅ ADR-006 |
| `TR-saveprofile-006` | Corrupt JSON caught, defaults for corrupt fields, original preserved | ✅ ADR-006 |
| `TR-saveprofile-019` | Migration failure: restore original from backup | ✅ ADR-006 |
| `TR-saveprofile-020` | Partial corruption: corrupt field reset, healthy preserved | ✅ ADR-006 |
| `TR-saveprofile-024` | MissingMemberHandling.Ignore: unknown fields skipped | ✅ ADR-006 |

## ADR Guidance

**ADR-006 (Save/Profile Serialization):**
- `MissingMemberHandling.Ignore` — unknown fields silently ignored
- Migration functions registered per version step
- Backup created before migration, restored on failure
- Field renames require `saveVersion` bump + migration function

## Description

Implement version migration and corruption recovery for save files. On load, compare `saveVersion` against the current version. If older, run registered migration functions step-by-step. If newer, reject load and preserve the file. Handle corrupt JSON with per-field try-catch recovery and MissingMemberHandling.Ignore.

## Design

### Version Migration

```csharp
private Dictionary<int, Action<PersistentSaveData>> _migrations;

// Migration registered at init:
_migrations[1] = MigrateV1ToV2; // adds premiumCurrency field

private void MigrateV1ToV2(PersistentSaveData data)
{
    data.premiumCurrency = 0;
    data.premiumCurrencyLastModified = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
}
```

- Create backup before migration
- Apply migrations sequentially from `loaded.saveVersion → current - 1`
- After all migrations applied, write migrated file to disk
- On migration failure: restore original from backup, log error

### Newer Version Rejection

If `loaded.saveVersion > currentSaveVersion`:
- Log warning containing "newer version"
- Return default `PersistentSaveData()` (fresh state)
- Original file NOT deleted (preserved for future upgrade)
- Error is non-fatal — game continues with defaults

### Corruption Recovery

- Wrap deserialization in try-catch
- On `JsonException`: log warning containing "corruption"
- Initialize all fields to defaults
- Original file preserved on disk (no destructive recovery)
- Per-field try-catch on deserialization — healthy fields preserved, corrupt fields reset to defaults

### MissingMemberHandling.Ignore

- Configured in `JsonSerializerSettings` at startup
- Unknown fields in JSON are silently ignored
- All known fields deserialize normally

## Acceptance Criteria

1. **GIVEN** `persistent.json` exists with `saveVersion = 1` AND game expects `saveVersion = 2` AND `MigrateV1ToV2` is registered, **WHEN** `LoadPersistentAsync()` is called, **THEN** migration adds `premiumCurrency = 0` AND `saveVersion` becomes `2` AND migrated file is written to disk.
2. **GIVEN** `persistent.json` exists with `saveVersion = 3` AND game expects `saveVersion <= 2`, **WHEN** `LoadPersistentAsync()` is called, **THEN** it returns `PersistentSaveData()` with default values AND warning contains "newer version" AND original file is NOT deleted.
3. **GIVEN** `persistent.json` contains invalid JSON (truncated mid-object), **WHEN** deserialization is attempted with `MissingMemberHandling.Ignore`, **THEN** `JsonReaderException` is caught AND `PersistentSaveData` is initialized with defaults AND original file is preserved AND warning contains "corruption".
4. **GIVEN** migration fails mid-step (exception in `MigrateV1ToV2`), **WHEN** load completes, **THEN** original file is restored from backup AND error contains "migration failed".
5. **GIVEN** `persistent.json` has corrupt fields (e.g., `gold = null`) AND `runstate.json` is valid, **WHEN** initialization completes, **THEN** corrupt fields are reset to defaults (gold = 0) AND healthy fields are preserved AND `runstate.json` loads normally AND warning contains "persistent.json corruption".
6. **GIVEN** `persistent.json` contains unknown field `"futureField": "test"` AND `MissingMemberHandling.Ignore` is configured, **WHEN** deserialization runs, **THEN** unknown field is silently ignored AND all known fields deserialize correctly AND no exception is thrown.

## Test Evidence Path

- `Assets/_TinyRift/Tests/EditMode/SaveProfile/VersionMigrationTests.cs`
- All 6 acceptance criteria as individual test methods
- Pre-built JSON files at various save versions for migration testing
- Corrupt JSON files for corruption recovery tests

## Dependencies

- **Save Story 001** — Core Persistence Layer (file I/O, write pattern)

## Unlocks

- None (standalone error recovery)

## Risks

- **LOW**: Multiple migration versions may need sequential application. Mitigation: dictionary of version→function ensures ordered, documented steps.
