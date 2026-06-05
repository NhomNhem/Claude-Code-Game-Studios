# Design Review Log: Save/Profile Persistence

## Review 1 — 2026-05-26

**Verdict**: MAJOR REVISION NEEDED — 8 ship-blocking issues

**Reviewers**: economy-designer, systems-designer, qa-lead, game-designer

### Blockers (Pre-Revision)

| # | Severity | Issue | Resolution |
|---|----------|-------|------------|
| 1 | Ship | Cross-device sync design incomplete: conflicted profile merge is undefined, no sync queue for pending changes, no visual feedback during sync | Added `lastModified` timestamps per entity + union-merge for lists; persisted sync queue in `ProfileSyncQueue.json`; non-blocking toast for sync status |
| 2 | Ship | Offline mode economy integrity: offline-earned currency trust model is unspecified, no offline session tracking, risk of save-scumming during sync windows | `OfflineSessionRewardCalculator` with `lastRunTimestamp` tracking; `SyncBehaviour` enum (Authenticated/Pending); server-side `lastModified` validation with signed checksums |
| 3 | Ship | Profile corruption handling: JSON deserialization errors have no recovery strategy, save validation is missing, no graceful fallback | `ProfileSerializer` using Newtonsoft.Json with try-catch per entity; corrupted entities reset to defaults while preserving healthy data |
| 4 | Ship | Server-authoritative anti-cheat gaps: client pushes `RunResultData` unverified, run duration vs. damage-dealt ratio has no validation, currency delta unvalidated | Server validates `RunResultData` end timestamp vs. actual duration; `CurrencyDelta` includes checksum signed on server after validation |
| 5 | Ship | GDD uses fixed keys like `"profile"`, `"currencies"`, `"inventory"` as top-level JSON keys — brittle if any backend service adds or renames keys | All top-level keys defined as `public const string` in `ProfileKeys` static class with validation that every key resolves at startup |
| 6 | Ship | Save-scum exit prevention: no mechanism to prevent Alt+F4 force-close before autosave writes, allowing rollback | Atomic write via `WriteToTempThenReplace()` writing to temp file then `File.Replace`; retry-on-checksum-mismatch with exponential backoff |
| 7 | Blocking | GDD serialization approach contradicts TD-SYSTEM-BOUNDARY C5: C5 mandates Save/Profile owns Build State serialization but GDD delegates it to `BuildStateSerializer` in a different GDD | Added `IBuildStateSerializer` interface owned by Save/Profile; implementation delegates to BuildState's concrete serializer via DI (satisfies C5 without coupling) |
| 8 | Blocking | Duplicate rule conflict: Rule S19 says "No forced-sync loop" but S15 says "If lastWrite > lastRead → force flush on next load screen" — these are contradictory | S19 is primary (no forced sync); S15 revised: "If lastWrite > lastRead → queue a pending sync notification (visual toast only, no blocking)" |

### Revisions Applied

- Changed serializer: JsonUtility → Newtonsoft.Json with try-catch per-entity recovery
- Added `lastModified` timestamps per entity, union-merge for lists
- Rewrote sync queue: `ProfileSyncQueue.json`, toast-based sync status, exponential backoff retry
- Added `IBuildStateSerializer` interface owned by Save/Profile
- Removed rate-limiting rule; replaced with atomic write + retry-on-checksum
- Resolved S15 vs S19 contradiction: visual-only pending notification, no blocking
- Added `OfflineSessionRewardCalculator` with `lastRunTimestamp` and `SyncBehaviour` tracking
- Added server-side `RunResultData` validation (end timestamp vs. actual duration) + signed `CurrencyDelta` checksums
- Defined all JSON keys as `public const string` in `ProfileKeys` with startup validation
- Added `InventoryChangedEvent` and `ProfileSavedEvent` to Event Bus compatibility section
- Rewrote 21 acceptance criteria (5→26), all 21 with concrete assertions

### Post-Revision Verdict

Resubmitted for re-review in a new session.

## Review 2 — 2026-05-26

**Verdict**: NEEDS REVISION — 8 new ship-blocking issues (6 pre-existing, 2 v2 regressions)

**Reviewers**: economy-designer, systems-designer, qa-lead, game-designer, creative-director

### Pre-Revision Blockers (Re-review v2 → v3)

| # | Severity | Issue | Resolution |
|---|----------|-------|------------|
| 1 | Ship | Additive per-device delta unbounded — device rotation inflates balance with 3+ devices | **Server-authoritative balance with per-device earnings credits.** Balance = sum(earned) - sum(spent). 15min min sync interval + 50k/24h rolling window cap. |
| 2 | Ship (v2 reg) | Read-modify-write race — write semaphore guards writes but not reads; two consumers both write 150 from gold=100, first delta lost | **Accumulative API.** `ModifyGoldAsync(delta)` replaces `WriteGoldAsync(absolute)`. Read + apply + write all under same semaphore. |
| 3 | Ship | Cross-file write has no transaction boundary — 2/4 files written creates ghost state | **Single-file consolidation.** `persistent.json` covers profile + world + settings. One atomic write = one transaction. |
| 4 | Ship | `totalRunsCompleted`/`totalRunsWon` use max-wins — wrong for multi-device cumulative (Device A=3, B=2 → 3, not 5) | **Additive merge** with per-device last-seen baselines: `merged = server + localDelta`. |
| 5 | Ship (v2 reg) | ZoneCompletionEntry field-level merge undefined — which of 3 modes applies to which field? | **Per-field rules**: `completed` = OR, `bestSurvivalTimeSeconds` = max, `totalKillsInZone` = max, `isUnlocked` = OR, `lastModified` = newest-wins. |
| 6 | Ship | No `[JsonProperty]` attributes + IL2CPP — reflection-accessed fields silently dropped on device builds | All `PersistentSaveData` and `ZoneCompletionEntry` fields annotated with `[JsonProperty("key")]`. link.xml updated. |
| 7 | Ship | No pre-save validation — garbage input (negative gold, NaN volume) corrupts save irrecoverably | **SaveDataValidator** with gold≥0, volume [0,1], skillId not null, bestSurvivalTimeSeconds≥0, no NaN. |
| 8 | Ship | Mid-run gold loss on Alt+F4 — fantasy claim "no mid-run gold is lost" contradicted by 3 separate mechanisms | **Orphan runstate credits gold before discard.** Fantasy text revised to honest "best-effort" language. |

### Additional v3 Improvements Applied

- Toast copy: "Recovered while away" → "Earned while away"
- API renamed: `SaveAllAsync` → `PersistStateAsync`, `WriteGoldAsync` → `ModifyGoldAsync`
- Offline earnings diminishing returns: 0-4h 100%, 4-24h 50%, 24-168h 10%
- Premium PPH lowered to 1-3 (was 1-10), PDR to 1.0-1.5 (was 1.0-3.0), capped at 12h offline
- Net balance fraud detection: `if (currentBalance > maxPossibleGold + startingGold)` not gross earnings
- Premium currency spending velocity check: ≤500/h, flag spend >50% of lifetime earnings
- `.synclog` atomic write pattern (same as main files), last-attempt expiry
- Notification log (menu-accessible) for offline earning recall
- Quarantine overwrite UX: non-blocking notification with support contact copy
- In-camp currency spend autosave trigger added as fourth trigger
- 4 autosave triggers total (was 3)
- ACs rewritten: 22 → 29, all with proper GIVEN/WHEN/THEN, mockable sources, split visual assertions
- 17 tuning knobs (was 9), including diminishing returns curves, velocity limits, sync intervals
- Resolved open questions table added tracking all decisions
- No "Saving..." indicator anywhere — system is invisible
- Dependencies flag Currency System GDD as Not Started (formula coupling risk)

### Creative Director Synthesis

Overlap clusters identified:
1. **Delta sync breaks multi-device balance** — same root: merge strategy composition unsound for 3+ devices
2. **Concurrency corruption** — same root: shared-state access has no read-side sync
3. **Write atomicity gap** — same root: multi-file writes need rollback
4. **"No mid-run gold lost" false** — same root: three mechanisms contradict the guarantee
5. **IL2CPP serialization risk** — same root: no device-platform validation
6. **Player-fantasy language contamination** — same root: implementation vocabulary in public surface

### Post-Revision Verdict

Resubmitted for re-review in a new session. GDD v3 ready at 449 lines, 18 rules, 29 ACs.

## Review 3 — 2026-05-26 — Verdict: MAJOR REVISION NEEDED (v4 revision applied)

**Scope signal**: M

**Specialists**: economy-designer, systems-designer, qa-lead, game-designer, creative-director

**Blocking items**: 5 | **Recommended**: 11 | **Minor**: 8

**Summary**: 5 ship-blocking issues found and resolved in v4: (1) two contradictory fraud formulas unified, (2) double-counted startingGold fixed, (3) MissingMemberHandling.Error→Ignore with saveVersion-based migration, (4) semaphore vs coalescing resolved via dirty-flag+debounce mechanism, (5) orphan double-credit prevented via idempotent check and write ordering. 11 important items flagged (active-offline false positive risk, undefined mock interfaces, lastSeen ambiguity, quarantine notification language, settings I/O thrashing, session-hour velocity ambiguity, public LoadPersistentAsync RMW risk, synclog compaction underspecified, "Earned while away" framing, in-camp Alt+F4 double-positive, 30s toast timeout). 8 minor items noted.

**Prior verdict resolved**: Yes (8 Review 2 blockers confirmed fixed in v3; 5 new blockers found in v3 and resolved in v4)
