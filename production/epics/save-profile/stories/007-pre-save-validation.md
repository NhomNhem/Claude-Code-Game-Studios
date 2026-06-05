# Story 007: Pre-Save Validation

- **Epic**: Save & Profile
- **System**: Save/Profile Persistence
- **Type**: Logic
- **Priority**: P1
- **Estimate**: 2h
- **Status**: Ready
- **Last Updated**: 2026-06-02

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-saveprofile-026` | Pre-save validation: negative gold rejected | ✅ ADR-006 |

## ADR Guidance

**ADR-006 (Save/Profile Serialization):**
- `SaveDataValidator` rejects invalid delta before disk write
- Validation covers: non-negative currency, in-range settings, non-null skill IDs, valid floats

## Description

Implement `SaveDataValidator` that checks all outgoing data before serialization. Rejects invalid state (negative gold, out-of-range settings, non-finite floats) with logged errors. Data is never written to disk if validation fails.

## Design

### Validator API

```csharp
public static class SaveDataValidator
{
    public static ValidationResult Validate(PersistentSaveData data)
    {
        // All checks return first failure
        if (data.gold < 0) return Failure("negative gold");
        if (data.premiumCurrency < 0) return Failure("negative premiumCurrency");
        if (data.masterVolume < 0f || data.masterVolume > 1f) return Failure("masterVolume out of range");
        if (data.sfxVolume < 0f || data.sfxVolume > 1f) return Failure("sfxVolume out of range");
        if (data.musicVolume < 0f || data.musicVolume > 1f) return Failure("musicVolume out of range");
        if (string.IsNullOrEmpty(data.playerId)) return Failure("playerId null or empty");
        if (data.resolutionWidth <= 0) return Failure("resolutionWidth <= 0");
        if (data.resolutionHeight <= 0) return Failure("resolutionHeight <= 0");
        if (float.IsNaN(data.masterVolume) || float.IsInfinity(data.masterVolume)) return Failure("masterVolume NaN/Inf");
        // Same NaN/Inf check for all float fields
        return Success();
    }
}
```

### Validation Hooks

- `PersistStateAsync()` calls `Validate()` before snapshot is written
- `ModifyGoldAsync(delta)` checks `current + delta >= 0` before applying
- `ApplySettingsAsync()` validates ranges before snapshot capture
- On validation failure: log error containing rejection reason, reject the persist, data unchanged

### Integration

- Validator is called in the write pipeline, inside the dirty-flag snapshot capture
- Consumer systems receive error feedback via returned `UniTask` completion (log only, no exception thrown)

## Acceptance Criteria

1. **GIVEN** `ModifyGoldAsync(-100)` is called when `persistent.json.gold` is 50 (would result in negative gold), **WHEN** validation runs, **THEN** persist is rejected with error containing "negative gold" AND `gold` remains 50.
2. **GIVEN** `ApplySettingsAsync(masterVolume: 1.5f, ...)` is called (out of range), **WHEN** validation runs, **THEN** persist is rejected with error containing "masterVolume" AND `masterVolume` remains unchanged.

## Test Evidence Path

- `Assets/_TinyRift/Tests/EditMode/SaveProfile/SaveDataValidatorTests.cs`
- All 2 acceptance criteria as individual test methods
- Exhaustive validation field coverage (each validation rule tested independently)
- Boundary tests: gold=0 allowed, gold=-1 rejected; volume=1.0 allowed, volume=1.01 rejected

## Dependencies

- **Save Story 001** — Core Persistence Layer (IPersistStateService, data model)

## Unlocks

- None (standalone validation)

## Risks

- **LOW**: Validator may reject legitimate data if ranges are too tight. Mitigation: ranges align with GDD tuning knobs and Currency System defaults.
