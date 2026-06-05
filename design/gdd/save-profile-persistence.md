# Save/Profile Persistence

> **Status**: In Review (Revised v4)
> **Author**: game-designer + technical-director
> **Last Updated**: 2026-05-26
> **CD-GDD-ALIGN**: MAJOR REVISION NEEDED — 7 ship-killer findings resolved in revision (v1)
> **Design Review (v2)**: MAJOR REVISION NEEDED — 8 new blockers resolved in this revision (transmission channel, list conflict, multi-device earning, replay detection, premium currency formula, dynamic fraud detection, Offline Rewards UX, public API)
> **Design Review (v3)**: MAJOR REVISION NEEDED — 5 ship-blocking issues found (two fraud formulas, double-counted startingGold, MissingMemberHandling.Error vs AC26, semaphore vs coalescing, orphan double-credit)
> **Design Review (v4)**: Resolved — fraud formulas unified, Ignore adopted, dirty-flag+debounce coalescing added, idempotent orphan credit added, accepted limitation corrected
> **Implements Pillar**: P3 (Snappy Sessions) — fast save/load so players spend time playing, not waiting

## Overview

The Save/Profile Persistence system manages all persistent game data across sessions: player profile (currency, unlocked heroes/zones, settings), per-run build state (drafted skills with tiers), lore fragment collection, and world progression. It provides JSON-serialized save/load operations via Newtonsoft.Json to local disk (`Application.persistentDataPath`) using an atomic write pattern (temp file → rename). All persistent data is consolidated into a single `persistent.json` file to guarantee cross-field atomicity — one atomic write covers profile, world, and settings together. Ephemeral per-run state remains in a separate `runstate.json` file. Sync orchestration is delegated to a **ProfileSyncService** intermediate layer (see Interactions), which owns profile sync, payload mapping, dirty state, retry/error policy, offline fallback, and conflict resolution. The system uses server-authoritative balance with per-device earnings credits (sum of all device earnings minus spends), per-field `lastModified` timestamps for scalar currency fields (newest wins), union-merge for progression lists (never removes unlocks), and additive merge for cumulative counters. Offline-earned progress is applied silently with a brief non-blocking toast notification — no modal, no save-system language. The system triggers autosave on GState transitions (`HeroCamp` entry, `Defeat`, `Victory`) and on in-camp currency spend. Per the C5 constraint (systems-index), this GDD defines the Build State serialization contract — the format in which per-run skill loadouts are persisted and restored.

## Player Fantasy

The player never interacts with the Save/Profile system directly. They experience it as the confidence that their progress is best-effort persisted: currency earned persists after Defeat or Victory, unlocked zones remain available after restart, and lore fragments collected across sessions are always available in the Codex. In the vast majority of sessions, returning to Hero Camp shows currency, unlocks, and settings exactly where they were left — no manual saving, no sync buttons, no "are you sure you want to quit?". The system is invisible but creates the trust that every run's effort counts toward long-term progression.

**Accepted limitation**: If the game crashes before reaching a Defeat/Victory checkpoint, any mid-run earnings that were already committed to `persistent.json` via `ModifyGoldAsync` are preserved. Earnings tracked only in `runstate.json` (not yet committed to persistent storage) are recovered via the orphan credit path (see Edge Cases) as long as `runstate.json` survives the crash. In the worst case — crash before any mid-run persist of runstate — the current run's uncaptured earnings since the last write are lost. Runs that reach a checkpoint or are completed normally are fully preserved.

## Detailed Design

### Core Rules

1. **Local-first** — All saves write to local disk first (`Application.persistentDataPath`). If the Network Manager reports `IsConnected`, a server sync is triggered after the local write completes. This ensures saves never block on network availability.

2. **JSON serialization via Newtonsoft.Json** — All save data uses Newtonsoft.Json for serialization. This enables proper handling of `DateTime`, nested `List<T>`, and `long` values without custom wrappers. Plain-text JSON enables debugging, manual editing (dev only), and forward-compatible schema evolution. **All serialized fields must be annotated with `[JsonProperty]`** to ensure IL2CPP code stripping does not drop reflection-accessed fields on device builds.

3. **Versioned schema** — Every save file includes a `SaveVersion` integer. On load, the system checks the version against the latest known version. If the save version is older, a migration function upgrades it in-place. If the save version is newer (from a newer game build), loading is rejected with a clear error message.

4. **Single-file consolidation** — All persistent data (profile, world state, settings) is consolidated into a single `persistent.json`. This guarantees cross-field atomicity: one atomic temp-then-rename write covers profile, world, and settings together. Ephemeral per-run state remains in a separate `runstate.json` (cleared on run end).

5. **Autosave triggers** — Four autosave points:
   - **HeroCamp entry** (Loading → HeroCamp): Save persistent data
   - **In-camp currency spend** (any currency mutation in Hero Camp): Save persistent data
    - **Defeat** (InRun → Defeat): Save persistent data (currency earned persists), flush per-run state
    - **Victory** (InRun → Victory): Save persistent data + world state (unlock next zone), flush per-run state
    Autosaves write to the same file as manual saves — there is no separate "autosave slot."
    **Write order at Defeat/Victory**: persistent.json is written and verified first. Then runstate.json is deleted. This ordering prevents a crash-after-write from losing the just-committed gold (persistent.json is intact), while the orphan detection path (see Edge Cases) provides an idempotent check to avoid double-credit if crash occurs between the two steps.

6. **Conflict resolution** — Four resolution modes depending on field type:
   - **Scalar currency fields (gold, premiumCurrency)**: Per-field `lastModified` timestamp comparison. The most recent `lastModified` wins, regardless of origin. **Server validates timestamps**: rejects timestamps newer than server's current time and rejects timestamps <= `lastAcceptedTimestamp` for that field per player (prevents replay attacks). Timer tiebreaker: device-ID lexicographic order (deterministic). Settings (resolution, audio volume, control bindings) remain local-only, never synced.
   - **Progression lists (unlockedHeroIds, unlockedZoneIds, collectedLoreFragmentIds)**: **Union-merge** — `mergedList = union(localList, serverList)`. Once unlocked, never removed by sync conflict. These are monotonic append-only fields.
   - **Cumulative progression fields (totalRunsCompleted, totalRunsWon)**: **Additive merge** — `merged = server + localDelta` where `localDelta = newLocalValue - deviceLastSeenValue`. Per-device last-seen tracking (same mechanism as currency earnings credits) ensures cumulative totals sum correctly across devices.
   - **ZoneCompletionEntry fields**: Per-field merge within each entry — `completed` = logical OR (once true, stays true); `bestSurvivalTimeSeconds` = max-wins; `totalKillsInZone` = max-wins (per-run best); `isUnlocked` = logical OR; `lastModified` = newest-wins.

7. **Server-authoritative balance with per-device earnings credits** — The server maintains the authoritative balance for gold and premiumCurrency. Client devices never push absolute balance values. Instead:
   - Each device reports earnings deltas: `earnedThisSession` (gold and premiumCurrency earned during run).
   - The server tracks `totalEarnedPerDevice[deviceId]` — a running total of all earnings reported by that device.
   - **Balance = sum(earnedAcrossAllDevices) - sum(spentAcrossAllDevices)**. Spends are applied server-side (the server receives spend requests, validates them against the authoritative balance, and deducts).
   - On sync success, the server returns the authoritative balance. The client overwrites its local balance with this value.
   - **Minimum sync interval per device**: 15 minutes. A device cannot report earnings more than once per 15-minute window. Combined with a **per-rolling-window earnings cap** (50,000 gold per 24-hour window across all devices) to prevent rapid device oscillation from amplifying earnings.
   - `totalEarnedPerDevice` is stored server-side only (not in persistent.json schema).

8. **Offline reward notification** — Offline-earned progress is applied silently on reconnect. Gold counter animates upward, new unlocks glow, and a brief non-blocking toast appears (e.g., "Earned while away: +500g"). The toast copy uses present-tense "earned" or "accumulated" — never "recovered," "found," or "reclaimed." No modal, no OK/Claim button, no save-system language in release UI. Toast auto-dismisses after a few seconds. A **notification log** (accessible from the main menu) retains the last N offline earning summaries for recall if the toast is missed. Ownership: ProfileSyncService raises `OfflineRewardData` event; HUD system renders the toast.

9. **ProfileSyncService** — Sync orchestration is delegated to a dedicated intermediate service, NOT owned by Save/Profile or Network Manager directly. ProfileSyncService owns: profile sync orchestration, payload mapping, dirty state tracking, retry/error policy, offline/online fallback rules, conflict resolution, and future cloud sync/account-linking behavior. Save/Profile provides the data and knows nothing about transport. ProfileSyncService wires Save/Profile to the backend transport (IBackendService or WebSocketSQL endpoint).

10. **Build State serialization (C5 contract)** — Per-run skill loadouts are serialized as an array of `SavedSkillEntry` (see schema below). The serialized form contains only string IDs and integers — no Unity Object references, no asset paths. The system deserializes Build State on load by resolving each `skillId` via `SkillDatabase.GetById()`.

11. **Save files** — MVP uses two files:
    - `persistent.json`: Consolidated persistent data (profile, world state, settings). Written atomically (temp → rename). One atomic write covers all persistent data.
    - `runstate.json`: Ephemeral per-run state (cleared on run end). Not part of any transaction — if lost, the orphan detection path credits gold to persistent.json.

12. **Offline earnings diminishing returns** — To prevent week-long breaks from replacing active play, offline earnings use a tiered multiplier applied server-side:
    - Hours 0-4 since last sync: 100% of goldEarnedPerMinuteAvg
    - Hours 4-24: 50%
    - Hours 24-168: 10%
    The cap at 168h (7 days synclog max age) with diminishing returns limits max offline gold to ~511,000 at GPM=300 (versus 3,024,000 at flat rate). Premium currency offline earnings capped at 12h max.

13. **Async API** — All save/load operations return `UniTask` for non-blocking I/O. Disk writes are async. Server syncs are async. The calling system awaits completion.

14. **Manual persist** — Exposed as `PersistStateAsync()` for systems that need to trigger a save outside autosave (e.g., Hero Camp Progression after every currency mutation). **In-camp currency spend must call `PersistStateAsync()` after every spend.**

15. **Atomic write pattern** — All file writes use a temp-then-rename pattern: write to `<filename>.tmp`, verify integrity (hash check), then rename to the target path. The original file is never truncated until the new file is verified. Prevents partial-write corruption on crash or power loss.

16. **Sync queue persisted to disk** — The pending sync queue is stored as an append-only transaction log (`.synclog`) alongside the save files. ** `.synclog` entries use the same atomic write pattern as main files** (write to `.synclog.tmp`, verify, rename) to prevent corruption on crash mid-append. On app restart, the log is replayed before any new sync is initiated. Entries are pruned from the log only after the server confirms receipt. Guarantees queued syncs survive app termination. **Compaction**: Before sending to server, `.synclog` entries are merged into a single latest-state payload — individual entries are not replayed one-by-one. **Entry expiry uses last-attempt timestamp**, not creation timestamp: an entry is valid until successfully synced, not until a wall-clock TTL expires.

17. **Server-side economy validation** — When the server receives a sync payload, it validates net balance using the **maxBalanceGold** formula defined in the Formulas section below. The server calculates `actualHoursSinceLastSync` from its own `lastSyncTimestamp` — no client-supplied constants. Values exceeding the cap are quarantined, the authoritative server snapshot is returned, and a fraud flag is raised for admin review. **Premium currency velocity check**: spend no more than X premium currency per session-hour (e.g., 500 per session-hour). Flag any spend >50% of total player lifetime premium earnings in a single session, subject to a floor of 1,000 premium (to avoid false positives on small-fry players).

19. **Coalesced writes (dirty-flag + debounce)** — Multiple concurrent `PersistStateAsync()` calls are coalesced into a single disk write. The mechanism:
    - `PersistStateAsync()` captures the current data snapshot, sets a `_dirty` flag, and returns immediately.
    - A background write loop polls the dirty flag with a debounce interval (default 100ms). If dirty, it writes to disk and clears the flag.
    - If the write is already in-flight and new calls arrive, they update the pending snapshot reference and return immediately — only one disk write occurs when the debounce fires.
    - The write semaphore protects the actual disk I/O (temp → rename), while the dirty-flag layer above it provides coalescing. This means 60 calls in one frame produce exactly one disk write, and the written data reflects the latest snapshot across all callers.
    - Settings writes (`ApplySettingsAsync`) use an additional 500ms debounce specific to settings changes, preventing slider-drag thrashing.

20. **Pre-save validation** — Before any serialization, all outgoing data passes through `SaveDataValidator`:
    - `gold >= 0`, `premiumCurrency >= 0`
    - `masterVolume`, `sfxVolume`, `musicVolume` in [0.0, 1.0]
    - `skillId` not null/empty for all `SavedSkillEntry` entries
    - `bestSurvivalTimeSeconds >= 0`, `totalKillsInZone >= 0`
    - `resolutionWidth`, `resolutionHeight` > 0
    - No `float.NaN` or `float.PositiveInfinity` in any float field
    If validation fails, the save is rejected with a logged error and the data is not written.

### Save Schema

All serialized fields use `[JsonProperty]` to prevent IL2CPP metadata stripping. `MissingMemberHandling.Ignore` is active for forward compatibility — unknown fields in newer save versions are silently ignored. Migration detection uses `saveVersion` comparison instead: if the loaded version is lower than current, a migration function is applied; if higher, loading is rejected with a clear error message. Field renames require a `saveVersion` bump and migration function.

**`persistent.json`** — Consolidated persistent data (single file, atomic write):
```csharp
[System.Serializable]
public class PersistentSaveData
{
    [JsonProperty("saveVersion")] public int saveVersion;                                         // current: 1

    // --- Profile ---
    [JsonProperty("playerId")] public string playerId;                                            // from auth/login (immutable)
    [JsonProperty("gold")] public long gold;                                                      // server-authoritative balance
    [JsonProperty("goldLastModified")] public long goldLastModified;                              // Unix ms — conflict resolution
    [JsonProperty("premiumCurrency")] public long premiumCurrency;                                // server-authoritative balance
    [JsonProperty("premiumCurrencyLastModified")] public long premiumCurrencyLastModified;         // Unix ms

    [JsonProperty("unlockedHeroIds")] public List<string> unlockedHeroIds;                        // union-merge
    [JsonProperty("unlockedZoneIds")] public List<string> unlockedZoneIds;                        // union-merge
    [JsonProperty("collectedLoreFragmentIds")] public List<string> collectedLoreFragmentIds;      // union-merge

    [JsonProperty("totalRunsCompleted")] public int totalRunsCompleted;                           // additive merge (per-device)
    [JsonProperty("totalRunsCompletedLastSeen")] public int totalRunsCompletedLastSeen;            // per-device baseline for delta
    [JsonProperty("totalRunsWon")] public int totalRunsWon;                                       // additive merge (per-device)
    [JsonProperty("totalRunsWonLastSeen")] public int totalRunsWonLastSeen;                        // per-device baseline for delta

    [JsonProperty("lastSaveTime")] public string lastSaveTime;                                    // ISO 8601 UTC — metadata only

    // --- World ---
    [JsonProperty("zoneCompletions")] public List<ZoneCompletionEntry> zoneCompletions;

    // --- Settings (local-only, never synced) ---
    [JsonProperty("masterVolume")] public float masterVolume;                                     // 0.0–1.0, local-only
    [JsonProperty("sfxVolume")] public float sfxVolume;                                           // 0.0–1.0, local-only
    [JsonProperty("musicVolume")] public float musicVolume;                                       // 0.0–1.0, local-only
    [JsonProperty("screenShakeEnabled")] public bool screenShakeEnabled;                          // local-only
    [JsonProperty("resolutionWidth")] public int resolutionWidth;                                 // local-only
    [JsonProperty("resolutionHeight")] public int resolutionHeight;                               // local-only
    [JsonProperty("fullscreen")] public bool fullscreen;                                          // local-only
    [JsonProperty("languageCode")] public string languageCode;                                    // local-only

    [System.Serializable]
    public class ZoneCompletionEntry
    {
        [JsonProperty("zoneId")] public string zoneId;
        [JsonProperty("completed")] public bool completed;                                        // logical OR merge
        [JsonProperty("bestSurvivalTimeSeconds")] public int bestSurvivalTimeSeconds;              // max-wins merge
        [JsonProperty("totalKillsInZone")] public int totalKillsInZone;                           // max-wins (per-run best)
        [JsonProperty("isUnlocked")] public bool isUnlocked;                                      // logical OR merge
        [JsonProperty("lastModified")] public long lastModified;                                  // newest-wins
    }
}
```

**`runstate.json`** — Ephemeral per-run state (cleared on run end, no [JsonProperty] needed if never synced):
```csharp
[System.Serializable]
public class RunStateSaveData
{
    public int saveVersion;                              // current: 1
    public string zoneId;                                // which zone this run is in
    public float elapsedRunTimeSeconds;
    public int killsThisRun;
    public long goldEarnedThisRun;
    public long premiumCurrencyEarnedThisRun;
    public List<SavedSkillEntry> draftedSkills;          // Build State (C5 contract)

    [System.Serializable]
    public class SavedSkillEntry
    {
        [JsonProperty("skillId")] public string skillId;         // matches SkillDatabase key
        [JsonProperty("currentTier")] public int currentTier;    // 0–2
    }

    public List<string> loreFragmentIdsThisRun;
}
```

### Interactions with Other Systems

| System | Interface | Direction | Data |
|--------|-----------|-----------|------|
| Event Bus | Subscribes to `GameStateChanged` for autosave triggers | Event Bus → Save | State + context |
| Game State Manager | Reads `currentState` for autosave timing | Save → GState (poll) | State enum |
| ProfileSyncService | Orchestrates sync: reads save data, maps payload, handles retry/error, routes to backend transport | Save → ProfileSyncService → Backend | PersistentSaveData |
| Backend Transport | WebSocketSQL endpoint (or IBackendService) — receives synced profile payload | ProfileSyncService → BackendTransport | JSON payload |
| Skill Database | Calls `SkillDatabase.GetById()` during Build State deserialization | Save → SkillData | SkillId string |
| Build State | Serializes/deserializes `SavedSkillEntry[]` as per C5 contract | Bidirectional | SkillId + tier arrays |
| Account/Profile | Reads profile data after login to populate initial state | Account → Save | PersistentSaveData |
| Hero Camp Progression | Reads currency/unlocks for UI display; calls `ModifyGoldAsync(-cost)` on spend | CampProg → Save | Gold, unlocked items |
| Currency System | Reads currency; calls `ModifyGoldAsync(delta)` for run earnings | Currency → Save | Gold, premiumCurrency |
| World State | Reads/writes zone completions | World → Save | ZoneCompletionEntry[] |
| Lore Fragment System | Appends fragment IDs on collection | Lore → Save | String IDs |
| Settings UI | Reads/writes settings on change | Settings UI → Save | PersistentSaveData |

### Public API

```csharp
public interface IPersistStateService
{
    // Full persist / load
    UniTask PersistStateAsync();
    UniTask<PersistentSaveData> LoadPersistentAsync();
    UniTask<RunStateSaveData> LoadRunStateAsync();

    // Accumulative writes (protected by write semaphore — no read-modify-write race)
    UniTask ModifyGoldAsync(long delta);
    UniTask ModifyPremiumCurrencyAsync(long delta);
    UniTask AddUnlockAsync(string heroId, string zoneId);
    UniTask AddLoreFragmentAsync(string fragmentId);
    UniTask ApplySettingsAsync(float masterVolume, float sfxVolume, float musicVolume,
                                bool screenShakeEnabled, string languageCode);

    // Migration
    UniTask RunMigrationAsync();

    // Event — systems that cache derived state can invalidate on persist
    event Action<PersistentSaveData> OnPersisted;
}
```

### Platform & Build Requirements

- **Newtonsoft.Json**: Already bundled in the template at `com.unity.nuget.newtonsoft-json@4dfd81071c64`. Must not be removed when stripping Fusion.
- **`link.xml`**: Must be created in `Assets/_TinyRift/` to preserve all save schema types (`PersistentSaveData`, `ZoneCompletionEntry`, `RunStateSaveData`, `SavedSkillEntry`) under IL2CPP AOT compilation. Without this, Newtonsoft.Json silently drops fields on device builds.
- **`[JsonProperty]`**: All serialized fields in `PersistentSaveData` and `ZoneCompletionEntry` must be annotated with `[JsonProperty("keyName")]` to ensure IL2CPP metadata stripping does not eliminate fields accessed via Newtonsoft.Json reflection. `RunStateSaveData` and `SavedSkillEntry` should also use `[JsonProperty]` if ever synced (future).
- **`MissingMemberHandling.Ignore`**: Deserialization uses `MissingMemberHandling.Ignore` for forward compatibility — unknown fields in newer save versions are silently dropped. Migration detection uses `saveVersion` comparison (AC5) rather than exception-catch. Field renames require a `saveVersion` bump and migration function — the old key name is mapped in the migration function, not via deserialization error.
- **Event Bus cross-GDD note (resolved)**: The Event Bus GDD's Interactions table now includes `Victory` in the Save System subscription row. Resolved as part of cross-GDD review (2026-05-27, R2).

## Formulas

### maxBalanceGold (net balance check)

Defines the theoretical maximum gold balance a player could have, used for server-side fraud detection. Uses the **net balance** (not gross earnings) to avoid false positives on players who earned and spent large amounts.

`maxBalanceGold = startingGold + (goldEarnedPerMinuteAvg × effectiveMinutesSinceLastSync)`

Where `effectiveMinutesSinceLastSync` applies the diminishing returns curve:

```
if H <= 4:   effectiveMinutes = H × 60
if 4 < H <= 24: effectiveMinutes = (4 × 60) + ((H - 4) × 60 × 0.5)
if 24 < H <= 168: effectiveMinutes = (4 × 60) + (20 × 60 × 0.5) + ((H - 24) × 60 × 0.1)
```

At H=168 (max): `effectiveMinutes = 240 + 600 + 864 = 1,704` (versus 10,080 at flat rate).

**Variables:**
| Variable | Symbol | Type | Range | Description |
|----------|--------|------|-------|-------------|
| startingGold | — | long | 0–500 | Starting gold for new accounts (from Currency System — default 0) |
| goldEarnedPerMinuteAvg | GPM | int | 100–500 | Average gold earned per minute by a normal player (from Currency System — default 300) |
| actualHoursSinceLastSync | H | float | 0–168 | Hours elapsed since the player's last successful server sync (server-calculated from its own timestamp, not client-supplied) |

**Output Range (with diminishing returns):** At H=168 (max), effective minutes = 1,704 (not 10,080). At GPM=500: ~852,000 gold. At GPM=300: ~511,200 gold.

**Example:** If GPM = 300, H = 10 (10 hours since last sync): `effectiveMinutes = (4 × 60) + (6 × 60 × 0.5) = 240 + 180 = 420`. `maxBalanceGold = startingGold + (300 × 420) = startingGold + 126,000`.

The server maintains this formula and quarantines any sync payload where `currentBalance > maxBalanceGold`. The server uses its own constants and its own `lastSyncTimestamp` — never client-supplied values. Separate fraud formula for PremiumCurrency is defined below.

### maxPremiumCurrency (net balance check)

Defines the theoretical maximum premium currency balance a player could have, for server-side fraud detection. Premium currency uses a lower ceiling than gold and is capped at 12 hours of offline accumulation.

`maxPremiumCurrency = startingPremium + (premiumPerHourAvg × min(actualHoursSinceLastSync, 12) × premiumDropRate)`

**Variables:**
| Variable | Symbol | Type | Range | Description |
|----------|--------|------|-------|-------------|
| startingPremium | — | long | 0–5 | Starting premium for new accounts (from Currency System — default 0) |
| premiumPerHourAvg | PPH | int | 1–3 | Average premium currency earned per hour (from Currency System — default 2) |
| actualHoursSinceLastSync | H | float | 0–168 | Hours since last sync (server-calculated), **capped at 12 for premium** |
| premiumDropRate | PDR | float | 1.0–1.5 | Variance multiplier for lucky drops (from Currency System — default 1.2) |

**Output Range:** 0 to 54 premium currency (at PPH=3, H=12, PDR=1.5).

**Example:** If PPH = 2, H = 10, PDR = 1.2: `maxPremiumCurrency = 2 × 10 × 1.2 = 24`.

The server quarantines any sync payload where `premiumCurrency > maxPremiumCurrency`. Gold and premiumCurrency are validated independently. A player can legitimately have high gold AND high premiumCurrency without triggering a false positive. Premium currency **spending velocity** is additionally checked: flag any spend >50% of total player lifetime premium earnings in a single session.

## Edge Cases

- **If `persistent.json` is corrupted (invalid JSON, truncated write)**: Catch the Newtonsoft.Json deserialization exception per field using try-catch. Fields that deserialize successfully are preserved; corrupt fields are reset to defaults. The player loses the unsaved portion of their last session (at most one run's checkpoint-to-checkpoint earnings) but not their account.

- **If a save file has a higher `saveVersion` than the game build** (player downgraded or restored an old save): Log a warning and reject the load. Initialize with default data. The player's progress is not lost — it's on disk at the newer version. If they upgrade back, the file is intact.

- **If the server is unreachable during sync**: Skip server sync. The local save is still written. Queue the sync in `.synclog` for replay on next successful connection. No data loss — the server may be slightly behind. On next app launch, the `.synclog` is replayed before any new sync is initiated.

- **If local and server timestamps diverge** (offline play on multiple devices):
  - **Scalar currency fields**: Per-field `lastModified` timestamp comparison. The most recent wins. The server validates timestamps (rejects future timestamps, rejects timestamps <= `lastAcceptedTimestamp` per field per player). Tiebreaker: device-ID lexicographic order.
  - **Progression lists**: Union-merge — the merged result contains all elements from both sides. No unlocks are ever removed.
  - **Cumulative progression fields**: Additive merge — `merged = server + localDelta` using per-device last-seen baselines.
  - **ZoneCompletionEntry fields**: Per-field rules — `completed` = logical OR, `bestSurvivalTimeSeconds` = max-wins, `totalKillsInZone` = max-wins, `isUnlocked` = logical OR, `lastModified` = newest-wins.
  - Offline earnings are applied silently on reconnect. A brief non-blocking toast appears (e.g., "Earned while away: +500g"). No modal, no OK/Claim button.

- **If the same player's session arrives from a second device**: The server uses per-device earnings credit tracking (server-authoritative balance model). Each device reports `earnedThisSession` only — never pushes absolute balance. The server calculates authoritative balance as `sum(earnedAcrossAllDevices) - sum(spent)`. Minimum 15-minute sync interval per device prevents oscillation. A rolling-window cap (50,000 gold per 24 hours across all devices) bounds total earning rate.

- **If server-side economy validation fails** (net balance exceeds `maxBalanceGold` or `maxPremiumCurrency`, or spending velocity triggered): The server quarantines the payload, returns the authoritative snapshot, and logs a fraud flag. The client accepts the server snapshot without retry. No local data is destroyed — the discrepancy is logged locally for debug. The Offline reward notification is suppressed when quarantine fires (no conflicting "earned X" then "rolled back X" experience). A non-blocking notification tells the player: "Your balance was adjusted to match the server. Contact support if you believe this is an error."

- **If a malicious client replays an old snapshot with a bumped `lastModified` timestamp**: The server rejects the payload because `newTimestamp <= lastAcceptedTimestamp` for that field. The authoritative server snapshot is returned. No double-spend possible.

- **If `SkillDatabase.GetById()` returns null for a saved `skillId`** (skill was removed from game): Skip the null entry during Build State deserialization. Log a warning with the missing ID. The player's build is still valid — the missing skill is simply absent.

- **If two persist operations are requested simultaneously** (autosave + manual persist in same frame): The atomic write pattern handles this — the second write waits for the first temp-file operation to complete. The accumulative API (`ModifyGoldAsync`) protects against read-modify-write races by having the save system read the current value, apply the delta, and write back — all under the same write semaphore. The `.synclog` serializes pending sync entries, so no sync is lost.

- **If a persist is requested during a scene transition** (GState = Loading): The save completes in the background (async disk write). If the current scene is destroyed during the write, the async continuation runs on the new scene's context. No data loss — the write uses atomic temp-then-rename, so a partially written file never replaces the original.

- **If the disk is full during save**: Catch the `IOException`. Log the error. The temp file write fails before any rename occurs — the original save file remains intact. The player sees a "Storage full — cannot save progress" toast.

- **If the game crashes mid-persist**: The atomic write pattern (temp → rename) ensures the original save file is never truncated. On next load, the game reads the intact previous `persistent.json`. Any pending `.synclog` entries are replayed on restart.

- **If orphan `runstate.json` is found on launch** (game crashed or Alt+F4 mid-run): The system detects stale runstate on initialization. Before discarding, it checks whether the gold and premium currency are **already reflected in persistent.json** (idempotent check): if `persistent.json.gold - runStartBookmark.gold >= runstate.goldEarnedThisRun`, the earnings were already committed via `ModifyGoldAsync` during the run — skip credit. Otherwise, it **credits** the delta to `persistent.json` via `ModifyGoldAsync(+earnedThisRun)` and `ModifyPremiumCurrencyAsync(+earnedThisRun)`. This prevents double-credit when a crash occurs after the Defeat/Victory persistent write but before runstate deletion. The orphan threshold (default 24h) is a tuning knob; beyond it the runstate is discarded without credit as the earnings are considered stale. A warning is logged with the zone ID and elapsed time for analytics.

- **If settings are restored from a different device/resolution**: Settings are local-only and no wider than 10 integers/floats — they are guaranteed to be compatible. If the saved resolution is not supported, fall back to the system default.

- **If two fields have identical `lastModified` timestamps** (race condition within same millisecond): Device-ID lexicographic order wins as deterministic tiebreaker. Log the conflict to the fraud analysis pipeline. This ensures at most one round of conflict on a field per millisecond.

- **If `.synclog` replay encounters an entry that the server rejects** (stale session, expired token): Discard the entry, log a warning, and continue replaying remaining entries. The player reauthenticates via the normal login flow, which triggers a fresh sync.

- **If a consumer system passes invalid data**: The `SaveDataValidator` (Rule 17) rejects the persist before it reaches disk or sync. The data is not written. The consumer system receives an error response and must retry with corrected data.

## Dependencies

**Upstream (this system depends on these):**
| System | Type | Interface |
|--------|------|-----------|
| Event Bus | Hard | Subscribes to `GameStateChanged` for autosave triggers |
| Game State Manager | Soft | Polls `currentState` for autosave timing |
| ProfileSyncService | Hard | Orchestrates sync: reads save data, maps payload, handles retry, routes to backend transport |
| Backend Transport | Hard | WebSocketSQL endpoint (or IBackendService) — receives synced profile payload from ProfileSyncService |
| Skill Database | Hard | Calls `SkillDatabase.GetById()` during Build State deserialization |
| Currency System | Hard (formula) | GPM=300, PPH=2, PDR=1.2, startingGold=0, startingPremium=0 — defined in Currency System GDD Section 4.6. Constants reconciled via cross-GDD review (2026-05-27, R3). |

**Downstream (systems that depend on this one):**
| System | Type | Interface |
|--------|------|-----------|
| ProfileSyncService | Hard | Reads `PlayerProfileSaveData` for sync payload |
| Account/Profile | Hard | Reads/writes `PlayerProfileSaveData` on login/logout |
| Hero Camp Progression | Hard | Reads currency/unlocks for UI; writes on spend |
| Currency System | Hard | Reads/writes gold and premiumCurrency |
| World State | Hard | Reads/writes `WorldSaveData` |
| Lore Fragment System | Soft | Appends `loreFragmentIds` on collection |
| Settings UI | Hard | Reads/writes `SettingsSaveData` |
| Build State | Hard | Serializes/deserializes `SavedSkillEntry[]` |

*Hard = system cannot function without this. Soft = enhanced by this but works without it.*

## Tuning Knobs

| Knob | Default | Range | Effect When Max | Effect When Min | Owner |
|------|---------|-------|-----------------|-----------------|-------|
| Persist rate-limit interval | 1 s | 0.1–10 s | Less frequent disk writes (safer, slower) | More frequent writes (faster, more I/O) | Save/Profile |
| Max save file size | 1 MB | 0.1–10 MB | Larger files allowed (more data cached locally) | Stricter limit (risk of write failure for complex profiles) | Save/Profile |
| Server sync retry interval | 5 s | 1–60 s | Less aggressive retry on failed sync | More aggressive retry (more network chatter) | Save/Profile + Network |
| Server GPM (goldEarnedPerMinuteAvg) | 300 | 100–500 | Higher max, easier to pass validation | Tighter fraud detection, higher false-positive risk | Server |
| Server PPH (premiumPerHourAvg) | 2 | 1–3 | Higher ceiling, supports larger premium earnings | Tighter fraud bound | Server |
| Server premiumDropRate (PDR) | 1.2 | 1.0–1.5 | Higher variance multiplier, fewer false positives | Tighter fraud detection | Server |
| Premium offline max hours | 12 | 0–24 | Longer premium offline earning window | Shorter window, tighter bound | Server |
| Per-device min sync interval | 15 min | 5–60 min | Less frequent per-device delta writes | More frequent syncing, more network chatter | Server |
| Rolling window earnings cap (24h) | 50,000 gold | 10,000–500,000 | Higher ceiling for active players | Tighter fraud bound for device oscillation | Server |
| Offline earnings diminishing: full rate | 4 h | 1–8 h | Longer at full earnings rate | Shorter at full earnings rate, faster taper | Server |
| Offline earnings diminishing: half rate | 20 h | 8–48 h | Longer taper window | Shorter taper window | Server |
| Offline earnings diminishing: tail rate | 0.1 (10%) | 0.05–0.5 | High tail earnings after 24h | Low tail earnings after 24h | Server |
| Sync queue expiry policy | last-attempt | creation / last-attempt | No change (last-attempt only option) | — | Save/Profile |
| Offline Rewards display timeout | 30 s | 10–120 s | Player has more time to review summary | Summary auto-dismisses faster | UI |
| Notification log max entries | 10 | 3–50 | Larger history for recall | Smaller history, less memory | UI |
| Premium currency velocity limit (/hour) | 500 | 100–5000 | Higher spend ceiling for whales | Tighter spend bound, fewer false positives | Server |
| Premium spend fraction of lifetime cap | 0.5 (50%) | 0.2–1.0 | Allow large spends from legitimate accumulation | Flag any spend > half of lifetime earnings | Server |

Save schema and file structure are design-time decisions — changing them requires a migration version bump.

## Visual/Audio Requirements

None. The Save/Profile system has no visual or audio output. All save/persist activity is invisible to the player. No "Saving..." indicator or save-system language appears in the UI. The only visible signals are the reward toast ("Earned while away: +500g") and the gold counter animation — both owned by HUD system, not Save/Profile.

## UI Requirements

The Save/Profile system has no direct UI. The Settings UI panel reads/writes `SettingsSaveData` via the Save/Profile API. Currency displays in the HUD and Camp Menu read profile currency values. These are owned by their respective UI systems.

## Acceptance Criteria

### Persist & Load
- **AC1** — **GIVEN** `GStateManager.CurrentState == HeroCamp` AND `AuthService.CurrentPlayerId` returns `"player_123"` AND `CurrencySystem.GetBalance()` returns `gold = 1000`, **WHEN** `PersistStateAsync()` is called and its `UniTask` completes, **THEN** `Application.persistentDataPath/persistent.json` exists AND `persistent.json.gold` equals `1000` AND `persistent.json.playerId` equals `"player_123"`.
- **AC2** — **GIVEN** `RunState.GoldEarnedThisRun` is `500` AND `RunState.PremiumCurrencyEarnedThisRun` is `0` AND `GStateManager.CurrentState == InRun`, **WHEN** `GState` transitions to Defeat and the autosave completes, **THEN** `persistent.json.gold` equals pre-run gold `+ 500` AND `runstate.json` does NOT exist.
- **AC3** — **GIVEN** `RunState.GoldEarnedThisRun` is `300` AND `RunState.ElapsedRunTimeSeconds` is `450` AND `GStateManager.CurrentState == InRun` AND `ZoneDefinition.CurrentZoneId` is `"zone_fire"`, **WHEN** `GState` transitions to Victory and the autosave completes, **THEN** `persistent.json.zoneCompletions` contains an entry with `zoneId = "zone_fire"` AND `completed == true` AND `bestSurvivalTimeSeconds >= 450` AND `runstate.json` does NOT exist.

### Version Migration
- **AC4** — **GIVEN** `persistent.json` exists with `saveVersion = 1` AND the game expects `saveVersion = 2` AND a migration function `MigrateV1ToV2` is registered, **WHEN** `LoadPersistentAsync()` is called, **THEN** the migration function adds the new field `premiumCurrency` with value `0` AND `saveVersion` is set to `2` AND the migrated file is written to disk.
- **AC5** — **GIVEN** `persistent.json` exists with `saveVersion = 3` AND the game expects `saveVersion <= 2`, **WHEN** `LoadPersistentAsync()` is called, **THEN** the method returns `PersistentSaveData()` with default values AND a warning is logged containing "newer version" AND the original file on disk is NOT deleted.
- **AC6** — **GIVEN** `persistent.json` contains invalid JSON (truncated mid-object), **WHEN** deserialization is attempted with `MissingMemberHandling.Ignore`, **THEN** a `JsonReaderException` is caught AND `PersistentSaveData` is initialized with default values (`gold = 0`, `unlockedHeroIds = new()`) AND the original file on disk is preserved AND a warning is logged containing "corruption".

### Fault Tolerance
- **AC7** — **GIVEN** `IFileSystem` mock throws `IOException` on write (simulated disk full), **WHEN** `PersistStateAsync()` is called, **THEN** the original `persistent.json` contents are unchanged AND an error is logged containing "Storage full".
- **AC8** — **GIVEN** `MockBackendService.ConnectionState == Connected` AND `PersistStateAsync()` completes locally, **WHEN** the sync completes, **THEN** the server mock stores the sent payload AND the server response is received by the client.
- **AC9** — **GIVEN** `MockBackendService.ConnectionState == Disconnected` AND `PersistStateAsync()` completes locally, **WHEN** the sync attempt fails, **THEN** a `.synclog` entry exists at `persistentDataPath/.synclog` containing the unsent persistent data.
- **AC10** — **GIVEN** a `.synclog` file with 1 pending entry AND `MockBackendService.ConnectionState == Connected`, **WHEN** `SaveBootstrapper.OnInitialized` fires (the initialization-complete event), **THEN** the `.synclog` entry is replayed AND the server mock's stored persistent data matches the entry data AND `.synclog` is empty.

### Build State
- **AC11** — **GIVEN** `runstate.json` contains `draftedSkills: [{ skillId: "obsolete_skill", currentTier: 1 }]` AND `SkillDatabase.GetById("obsolete_skill")` returns null, **WHEN** `LoadRunStateAsync()` completes, **THEN** the entry for `"obsolete_skill"` is absent from the deserialized `draftedSkills` list AND a warning is logged containing "obsolete_skill".
- **AC12** — **GIVEN** no files exist in `Application.persistentDataPath`, **WHEN** initialization completes (`SaveBootstrapper.OnInitialized` fires), **THEN** two files exist: `persistent.json` and `runstate.json` AND `persistent.json.saveVersion` equals the current version AND `persistent.json.playerId` is empty string AND `persistent.json.gold` is `0`.

### Conflict Resolution — Scalar Currency
- **AC13** — **GIVEN** local `persistent.json` has `gold = 1000` with `goldLastModified = T1` AND server has `gold = 500` with `goldLastModified = T2` AND `T1 > T2`, **WHEN** sync completes, **THEN** reading `/api/profile` returns `gold = 1000` AND `goldLastModified = T1`.
- **AC14** — **GIVEN** local `persistent.json` has `gold = 500` with `goldLastModified = T1` AND server has `gold = 1000` with `goldLastModified = T2` AND `T2 > T1`, **WHEN** sync completes, **THEN** local `persistent.json.gold` is `1000` AND local `goldLastModified` is `T2`.

### Conflict Resolution — List Union-Merge
- **AC15** — **GIVEN** local `persistent.json` has `unlockedHeroIds = ["warrior", "mage"]` AND server has `unlockedHeroIds = ["warrior", "rogue"]`, **WHEN** sync completes, **THEN** both local and server `unlockedHeroIds` contain `["warrior", "mage", "rogue"]` (union, no duplicates).

### Conflict Resolution — Server Quarantine
- **AC16a (unit)** — **GIVEN** the server quarantines a sync payload (net balance exceeds `maxBalanceGold`), **WHEN** the sync response is received, **THEN** local `persistent.json.gold` is overwritten with the server's authoritative value AND no retry is attempted AND no reward notification toast is shown.
- **AC16b (integration)** — **GIVEN** a quarantine overwrite occurs, **WHEN** the quarantine notification is displayed, **THEN** a non-blocking notification appears with text containing "adjusted to match the server" AND no modal is shown.

### Reward Notification
- **AC17a (unit)** — **GIVEN** `RewardNotificationService` receives an `OfflineRewardData` with `currency = "gold"` AND `amount = 500`, **WHEN** sync completes, **THEN** `RewardNotificationService.ReceivedRewards` contains `{ currency: "gold", amount: 500 }`.
- **AC17b (integration)** — **GIVEN** `RewardNotificationService.ReceivedRewards` contains `{ currency: "gold", amount: 500 }` AND the player is in Hero Camp, **THEN** the gold counter animates from pre-sync value to pre-sync `+ 500` AND a toast appears with text containing "500" AND no modal is displayed.

### Concurrency & Throttling
- **AC18** — **GIVEN** two `PersistStateAsync()` calls are issued in the same synchronous execution slice, **WHEN** both calls return (the dirty flag is set twice), **THEN** exactly one disk write occurs AND the written data reflects the snapshot from the **second** caller (latest wins).
- **AC19** — **GIVEN** 60 `PersistStateAsync()` calls are issued in rapid succession (e.g., within a single frame), **WHEN** the debounce timer fires after 100ms, **THEN** exactly one disk write occurs AND `persistent.json.gold` on disk equals the value from the **last** `PersistStateAsync()` call's data snapshot AND no intermediate values appear on disk.

### Migration & Partial Failure
- **AC20** — **GIVEN** `persistent.json` has `saveVersion = 1`, **WHEN** `LoadPersistentAsync()` completes with game expecting `saveVersion = 2`, **THEN** `persistent.json.saveVersion` is `2` AND all `saveVersion = 1` fields are migrated to their `v2` equivalents.
- **AC21** — **GIVEN** migration fails mid-step (exception in step processing), **WHEN** the load completes, **THEN** the original unmodified file is restored from the backup created before migration started AND an error is logged containing "migration failed".
- **AC22** — **GIVEN** `persistent.json` has corrupt fields (e.g., `gold = null` in JSON) AND `runstate.json` is valid, **WHEN** initialization completes, **THEN** the corrupt fields in `persistent.json` are reset to defaults (gold = 0) AND healthy fields are preserved AND `runstate.json` is loaded normally AND a warning is logged containing "persistent.json corruption".

### Orphan Runstate Recovery (Revised — idempotent gold credit)
- **AC23** — **GIVEN** `persistent.json.gold = 500` before the run AND `runstate.json` exists with `goldEarnedThisRun = 300` AND `premiumCurrencyEarnedThisRun = 10` AND `elapsedRunTimeSeconds = 600` AND the file is less than 24 hours old AND `persistent.json.gold` on launch is still `500` (earnings were NOT committed via `ModifyGoldAsync` before crash), **WHEN** initialization completes, **THEN** `persistent.json.gold == 800` AND `persistent.json.premiumCurrency == previousPremium + 10` AND `runstate.json` does NOT exist.
- **AC23b** — **GIVEN** `persistent.json.gold = 1000` (already includes run earnings committed via `ModifyGoldAsync`) AND `runstate.json` exists with `goldEarnedThisRun = 300`, **WHEN** initialization completes, **THEN** `persistent.json.gold` remains `1000` (idempotent check — skip credit since gold >= runstart + 300).

### Network Disconnect Mid-Sync
- **AC24** — **GIVEN** `MockBackendService.ConnectionState == Connected` AND `PersistStateAsync()` is called, **WHEN** the server request is in flight and `ConnectionState` transitions to `Disconnected`, **THEN** local `persistent.json` data is preserved AND a `.synclog` entry is created with the unsent payload AND no partial server state is committed.

### Concurrent Read During Write
- **AC25** — **GIVEN** `PersistStateAsync()` is in progress (semaphore acquired), **WHEN** `LoadPersistentAsync()` is called, **THEN** the read returns the pre-write state until the write completes AND the write semaphore is released.

### MissingMemberHandling.Ignore
- **AC26** — **GIVEN** `persistent.json` contains an unknown field `"futureField": "test"` AND `MissingMemberHandling.Ignore` is configured, **WHEN** deserialization runs, **THEN** the unknown field is silently ignored AND all known fields (`gold`, `playerId`, etc.) deserialize correctly AND no exception is thrown.

### Synclog Compaction
- **AC27** — **GIVEN** `.synclog` contains 10 pending entries from sequential `PersistStateAsync()` calls, **WHEN** the file is read on next restart before sync, **THEN** only the **most recent** entry per file path is retained (entries are compacted into a single latest-state payload).

### Pre-Save Validation
- **AC28** — **GIVEN** `ModifyGoldAsync(-100)` is called when `persistent.json.gold` is `50` (would result in negative gold), **WHEN** the validation step runs, **THEN** the persist is rejected with an error logged containing "negative gold" AND `persistent.json.gold` remains `50`.
- **AC29** — **GIVEN** `ApplySettingsAsync(masterVolume: 1.5f, ...)` is called (out of range), **WHEN** the validation step runs, **THEN** the persist is rejected with an error logged containing "masterVolume" AND `persistent.json.masterVolume` remains unchanged.

## Open Questions

| Question | Options | Impact | Target Resolution |
|----------|---------|--------|-------------------|
| Should runstate survive a Defeat for "retry" functionality? | Clear on Defeat (default) vs. Preserve for immediate retry | Clear: simpler, encourages camp return. Preserve: enables "try again" without new draft. | During Run Completion GDD — MVP clears on Defeat, retry is future |
| Should achievements/trophies be saved here or in a separate system? | Here (profile field) vs. Separate achievement system | Here: simpler, single save file. Separate: clean separation, but over-engineered for MVP. | During implementation — track in profile for MVP, extract if needed later |

### Resolved

| Question | Decision |
|----------|----------|
| Should settings be synced to server or local-only? | **Local-only for MVP.** Server sync is future (requires `lastModified` fields on settings when implemented). |
| Should the save file be encrypted/obfuscated? | **Plain JSON for MVP.** Server-side validation (net balance formula + spending velocity) is the anti-cheat layer. Obfuscation deferred. |
| Who owns the reward notification toast? | **HUD owns rendering.** ProfileSyncService provides `OfflineRewardData` DTO via Event Bus. Non-blocking toast, no modal, present-tense copy ("Earned while away"). |
| Who owns the quarantine notification? | **HUD owns rendering.** Save/Profile provides the adjustment event. "Your balance was adjusted to match the server. Contact support if you believe this is an error." |
| Public API naming? | Renamed to `IPersistStateService` / `PersistStateAsync()` / `ModifyGoldAsync(delta)` — no save-system language in public surface. |
| Cross-file atomicity? | **Single-file consolidation** — `persistent.json` covers profile + world + settings. One atomic write = one transaction boundary. |
| Per-device delta model? | **Server-authoritative balance with per-device earnings credits** — client never pushes absolute balance. Balance = sum(earned) - sum(spent). |
