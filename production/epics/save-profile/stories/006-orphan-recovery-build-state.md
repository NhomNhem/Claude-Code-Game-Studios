# Story 006: Orphan Recovery & Build State

- **Epic**: Save & Profile
- **System**: Save/Profile Persistence
- **Type**: Logic
- **Priority**: P1
- **Estimate**: 3h
- **Status**: Ready
- **Last Updated**: 2026-06-02

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-saveprofile-011` | Missing skill in runstate: skip entry, log warning | ✅ ADR-006 |
| `TR-saveprofile-021` | Orphan runstate recovery: credit delta with idempotent check | ✅ ADR-006 |

## ADR Guidance

**ADR-006 (Save/Profile Serialization):**
- Orphan detection: stale `runstate.json` on launch triggers credit path
- Idempotent gold credit: `persistent.json.gold - runStartBookmark.gold >= runstate.goldEarnedThisRun` → skip
- Missing skill: skip null entries during Build State deserialization

## Description

Implement orphan runstate recovery on app launch and Build State deserialization with missing-skill handling. If `runstate.json` exists on launch (crash/Alt+F4 mid-run), credit the delta with an idempotency check to prevent double-credit.

## Design

### Orphan Runstate Detection

On initialization:
1. Check if `runstate.json` exists
2. If yes, check staleness: if file age > 24h, discard without credit (log warning)
3. Idempotent check: `persistent.json.gold - runStartBookmark.gold >= runstate.goldEarnedThisRun` → skip credit (earnings already committed)
4. Otherwise, credit `ModifyGoldAsync(+goldEarnedThisRun)` and `ModifyPremiumCurrencyAsync(+premiumCurrencyEarnedThisRun)`
5. Delete `runstate.json`
6. Log warning with zone ID and elapsed time for analytics

### Missing Skill in Build State

During `LoadRunStateAsync()`:
1. Iterate `draftedSkills` list
2. For each entry, call `SkillDatabase.GetById(skillId)`
3. If null: skip entry, log warning containing skillId
4. Return parsed `RunStateSaveData` with valid entries only

## Acceptance Criteria

1. **GIVEN** `persistent.json.gold = 500` before run AND `runstate.json` exists with `goldEarnedThisRun = 300` AND `premiumCurrencyEarnedThisRun = 10` AND file < 24h old AND `persistent.json.gold` is still 500 (earnings not yet committed), **WHEN** initialization completes, **THEN** `persistent.json.gold == 800` AND `persistent.json.premiumCurrency == previous + 10` AND `runstate.json` does NOT exist.
2. **GIVEN** `persistent.json.gold = 1000` (already includes run earnings) AND `runstate.json` exists with `goldEarnedThisRun = 300`, **WHEN** initialization completes, **THEN** `persistent.json.gold` remains 1000 (idempotent check — skip credit).
3. **GIVEN** `runstate.json` contains `draftedSkills: [{ skillId: "obsolete_skill", currentTier: 1 }]` AND `SkillDatabase.GetById("obsolete_skill")` returns null, **WHEN** `LoadRunStateAsync()` completes, **THEN** entry for `"obsolete_skill"` is absent from deserialized list AND warning contains "obsolete_skill".

## Test Evidence Path

- `Assets/_TinyRift/Tests/EditMode/SaveProfile/OrphanRecoveryTests.cs`
- All 3 acceptance criteria as individual test methods
- Mock file system to simulate crash-persisted `runstate.json`
- Stale runstate test (file > 24h) verifies discard-without-credit

## Dependencies

- **Save Story 001** — Core Persistence Layer (file I/O, ModifyGoldAsync)
- **Skill Data System** — `SkillDatabase.GetById()` for Build State deserialization

## Unlocks

- None (standalone recovery)

## Risks

- **LOW**: Orphan check may fire on legitimate first launch after clean exit. Mitigation: runstate is always deleted on Defeat/Victory/clean exit — its presence is reliable crash indicator.
