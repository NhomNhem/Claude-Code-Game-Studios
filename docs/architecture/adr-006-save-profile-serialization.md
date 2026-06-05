# ADR-006: Save/Profile Serialization & Merge Strategy

## Status

Accepted

## Date

2026-06-01

## Decision Makers

user + agents (technical-director, architecture-decision skill)

## Summary

Establish the persistence architecture for player progress: JSON serialization via Newtonsoft.Json with single-file consolidation (`persistent.json`), atomic write pattern, versioned schema migration, dirty-flag+debounce write coalescing, server-authoritative economy with per-device earnings credits, and field-type-specific conflict resolution strategies. ProfileSyncService acts as the intermediate sync orchestrator between Save/Profile and the backend transport.

## Engine Compatibility

| Field | Value |
|-------|-------|
| **Engine** | Unity 6000.3.11f1 (Unity 6 Update 3) |
| **Domain** | Core (Persistence / Serialization) |
| **Knowledge Risk** | LOW — Newtonsoft.Json is a bundled NuGet package (`com.unity.nuget.newtonsoft-json`). File I/O uses standard `System.IO` APIs (`FileStream`, `File.Move`, `File.Delete`). No Unity engine API dependency beyond `Application.persistentDataPath`. |
| **References Consulted** | `docs/engine-reference/unity/VERSION.md` (AOT/IL2CPP section), `design/gdd/save-profile-persistence.md` |
| **Post-Cutoff APIs Used** | None — Newtonsoft.Json is library-defined. File I/O APIs are stable and unchanged. |
| **Verification Required** | IL2CPP build must preserve all `[JsonProperty]`-annotated types via `link.xml`. Run a server IL2CPP build that serializes and deserializes `PersistentSaveData` to verify no silent field drop. |

## ADR Dependencies

| Field | Value |
|-------|-------|
| **Depends On** | ADR-001 (TinyRiftScope registration — IPersistStateService replaces IProfileService in Foundation layer; IProfileSyncService in Core layer), ADR-002 (Event Bus GameStateChangedEvent for autosave triggers) |
| **Renames From** | `IProfileService` (ADR-001 Core layer) → `IPersistStateService` (this ADR, Foundation layer). Breaks the ADR-001 registration table — ADR-001 must be updated to reflect the rename and new layer. |
| **New Event for ADR-002** | `OfflineRewardData` — published by ProfileSyncService on reconnect after offline earnings. Must be added to ADR-002's Event Type Catalogue. |
| **Enables** | All systems consuming persistence: Currency, Hero Camp Progression, Lore, World State, Settings, Build State |
| **Blocks** | Epic: Player Progression & Persistence — cannot start until this ADR is Accepted |
| **Ordering Note** | GDD `design/gdd/save-profile-persistence.md` v4 is complete and in review. This ADR captures architecture-level decisions and refers to the GDD for implementation details (schema, formulas, edge cases). |

## Context

### Problem Statement

Player progress — currency, unlocks, world state, lore collections, settings, and per-run build state — must persist across game sessions, survive crashes, sync with the server when online, and resolve conflicts when the same account plays on multiple devices. The system must be invisible to the player (no save-system language, no manual sync buttons) while providing best-effort persistence and crash recovery. Additionally, the economy must be server-authoritative to prevent fraud while supporting offline play with eventual consistency.

### Constraints

- **Local-first with async sync**: Saves write to local disk first, then sync to server if connected. Saves must never block on network availability.
- **IL2CPP / AOT compatibility**: All serialized types must survive code stripping. No `BinaryFormatter` (removed in .NET, unsafe). No reflection-only serialization without AOT preservation.
- **Single-threaded Unity environment**: File I/O must use async patterns (`UniTask`) but all Unity API access remains on the main thread.
- **Crash resilience**: A crash mid-write must never corrupt the player's save file. A crash mid-run must recover earnings at the next launch.
- **Multi-device support**: The same account on multiple devices must not lose progress. Conflict resolution must be deterministic and fair.
- **Fraud prevention**: Server must validate sync payloads against theoretical maximums. No absolute balance pushed from client.

### Requirements

- Serialization must use Newtonsoft.Json JSON for debugging, forward-compatible schema evolution, and .NET Standard 2.1 compatibility
- All persistent data must consolidate into a single file (`persistent.json`) for cross-field atomicity
- Ephemeral per-run state must be separate (`runstate.json`) and cleared on run end
- All file writes must use atomic temp → rename pattern
- Schema must be versioned with migration functions for forward upgrades
- Write coalescing must prevent redundant disk I/O from rapid sequential persist calls
- Sync orchestration must be delegated to ProfileSyncService (not owned by Save/Profile or Network Manager directly)
- Server must maintain authoritative balance; clients report earnings deltas, not absolute balances
- Conflict resolution must use different strategies per field type (scalar, list, cumulative, composite)
- Pending sync queue must survive app termination (`.synclog`)
- All serialized fields must use `[JsonProperty]` annotations for IL2CPP safety
- All serialized fields must use `MissingMemberHandling.Ignore` for forward compatibility
- Autosave must trigger on GState transitions: HeroCamp entry, Defeat, Victory, and in-camp currency spend

## Decision

### Layer Placement

`IPersistStateService` registers in the **Foundation layer** (TinyRiftScope Foundation — file I/O is infrastructure, must be available before domain services): `builder.Register<SaveManager>(Lifetime.Singleton).As<IPersistStateService>()`.

`IProfileSyncService` registers in the **Core layer** (sync orchestration requires domain awareness — currency context, world state, lore ownership): `builder.Register<ProfileSyncService>(Lifetime.Singleton).As<IProfileSyncService>()`.

This replaces the existing `IProfileService → ProfileService` registration from ADR-001 Core layer (see Renames From above).

### A. JSON Serialization via Newtonsoft.Json

Use `com.unity.nuget.newtonsoft-json` (already bundled in the template) as the sole serialization engine. All save files are plain-text JSON. This decision gates debugging, forward-compatible schema evolution, and human-readable inspection during development.

**Rationale**: BinaryFormatter is removed in .NET 5+ and unsafe. PlayerPrefs has no conflict resolution, no schema versioning, and a size limit. Newtonsoft.Json is already present in the project — the only addition is AOT preservation.

### B. Single-File Consolidation with Atomic Write

All persistent data — profile (currency, unlocks), world state (zone completions), and settings — lives in one file: `Application.persistentDataPath/persistent.json`. This guarantees cross-field atomicity: one atomic write covers all persistent data together. If a crash occurs mid-write, the original file is untouched.

Ephemeral per-run state (current zone, elapsed time, skills drafted, gold earned this run) lives in a separate `runstate.json`. This file is deleted on Defeat/Victory after `persistent.json` is verified written. If `runstate.json` survives a crash (orphan state), the system credits the orphan earnings to `persistent.json` via an idempotent check — preventing both double-credit and lost earnings.

**Write pattern**: All file writes use temp → rename:
1. Serialize to `persistent.json.tmp`
2. Verify integrity via SHA256 hash computed over serialized bytes before the write
3. `File.Delete(persistent.json)` (explicit delete for platform compatibility — `File.Move` with `overwrite: true` is not reliably atomic on all mobile storage backends)
4. `File.Move(persistent.json.tmp, persistent.json)` (atomic rename on same filesystem)
5. On failure: log error, original file untouched

**Integrity hash**: SHA256 is computed over the serialized byte array before the temp write. The hash is stored in a sidecar file (`persistent.json.hash`). On load, the byte stream is hashed before deserialization and compared to the sidecar. Mismatch triggers corruption recovery (reset corrupt fields to defaults). Sidecar approach avoids the chicken-and-egg problem of embedding a hash within the JSON payload.

### C. Versioned Schema with Migration Functions

Every save file includes a `saveVersion` integer:
- On load: compare `saveVersion` against `CurrentSaveVersion` (compile-time constant)
- If loaded version < current: apply migration functions sequentially (v1→v2, v2→v3, etc.)
- If loaded version > current: reject load, log warning, initialize defaults. Original file retained on disk for recovery if player upgrades back.

Migration functions operate on typed `PersistentSaveData` via `JsonConvert.DeserializeObject<T>()` — never `JObject.ToObject<T>()`, which uses runtime `Reflection.Emit` and breaks under IL2CPP. Each migration function receives a deserialized `PersistentSaveData`, transforms it (adds/renames fields), increments `saveVersion`, and returns the modified instance. The migration runner serializes the result back via `JsonConvert.SerializeObject()`. Backup of the original file is created before migration begins; on failure, the backup is restored.

**Write pattern variant for migration safety**:
- Backup: `File.Copy(persistent.json, persistent.json.bak)`
- Migrate in-memory
- Atomic temp → rename write of migrated data
- On success: delete `.bak`
- On failure: `File.Copy(persistent.json.bak, persistent.json, overwrite: true)`, delete `.bak`, log error

### D. Dirty-Flag + Debounce Coalescing

Multiple concurrent `PersistStateAsync()` calls coalesce into a single disk write to prevent I/O thrashing:
1. Each `PersistStateAsync()` call captures the current data snapshot, sets `_dirty = true`, and returns immediately
2. A background loop polls the dirty flag at a debounce interval (default 100ms). If dirty, it serializes the latest snapshot, writes to disk, and clears the flag.
3. If a write is already in-flight when new calls arrive, the pending snapshot is updated — only one write fires when the debounce triggers.
4. Settings writes use an additional 500ms debounce specific to slider-drag thrashing.

This is distinct from a write semaphore — the semaphore protects actual disk I/O, while the dirty-flag layer above provides coalescing.

### E. ProfileSyncService as Sync Orchestrator

ProfileSyncService is a dedicated intermediate service, not owned by Save/Profile or Network Manager:

```
Save/Profile (data provider)
    ↓ reads PersistentSaveData, maps to sync payload
ProfileSyncService (orchestrator)
    ↓
    ├── owns: sync payload mapping, dirty state tracking, retry/error policy
    ├── owns: offline/online fallback rules, conflict resolution
    ├── owns: future cloud sync / account-linking behavior
    └── calls: IBackendService or WebSocketSQL endpoint
```

Save/Profile knows nothing about transport. ProfileSyncService knows nothing about disk layout. This separation lets the sync strategy evolve independently (retry policy, conflict resolution rules, future cloud providers) without touching save/load code.

### F. Server-Authoritative Balance with Per-Device Earnings Credits

The server maintains the authoritative balance for gold and premiumCurrency. Client devices never push absolute balance values:
- Each device reports earnings deltas: `earnedThisSession` (gold and premiumCurrency earned during run).
- The server tracks `totalEarnedPerDevice[deviceId]` — a running total of all earnings reported by that device.
- **Balance = sum(earnedAcrossAllDevices) - sum(spentAcrossAllDevices)**
- Spends are server-applied (server receives spend requests, validates against authoritative balance, deducts).
- On sync success, the server returns the authoritative balance. Client overwrites local balance.
- Minimum sync interval per device: 15 minutes. Rolling-window cap: 50,000 gold per 24 hours across all devices.

### G. Conflict Resolution Strategies

Four resolution modes per field type:

1. **Scalar currency fields (gold, premiumCurrency)**: Per-field `lastModified` timestamp comparison. Most recent wins. Server rejects future timestamps and timestamps ≤ `lastAcceptedTimestamp` per field (replay attack prevention). Tiebreaker: device-ID lexicographic order.

2. **Progression lists (unlockedHeroIds, unlockedZoneIds, collectedLoreFragmentIds)**: Union-merge — `mergedList = union(localList, serverList)`. Monotonic append-only. Once unlocked, never removed.

3. **Cumulative progression fields (totalRunsCompleted, totalRunsWon)**: Additive merge — `merged = server + localDelta` where `localDelta = newLocalValue - deviceLastSeenValue`. Per-device last-seen tracking prevents double-counting when syncing from multiple devices.

4. **ZoneCompletionEntry composite fields**: Per-field merge within each entry — `completed` = logical OR (once true, stays true); `bestSurvivalTimeSeconds` = max-wins; `totalKillsInZone` = max-wins; `isUnlocked` = logical OR; `lastModified` = newest-wins.

### H. Sync Queue (.synclog)

Pending sync entries are persisted as an append-only transaction log at `Application.persistentDataPath/.synclog`:
- **Write**: Each pending sync appends an entry. `.synclog` uses the same atomic write pattern (write to `.synclog.tmp`, verify, rename).
- **Replay**: On app start, `.synclog` is replayed before any new sync is initiated.
- **Pruning**: Entries removed only after server confirms receipt.
- **Compaction**: Before sending to server, entries are merged into a single latest-state payload — entries are not replayed one-by-one.
- **Expiry**: Uses last-attempt timestamp (not creation timestamp). An entry is valid until successfully synced, not until a wall-clock TTL expires.

### I. AOT Safety & Forward Compatibility

- All serialized fields use `[JsonProperty("keyName")]` annotations to prevent IL2CPP metadata stripping from dropping reflection-accessed fields.
- A `link.xml` in `Assets/_TinyRift/` preserves all save schema types: `PersistentSaveData`, `ZoneCompletionEntry`, `RunStateSaveData`, `SavedSkillEntry`. Additionally preserves Newtonsoft.Json internal types: `Newtonsoft.Json.Serialization.*`, `Newtonsoft.Json.Converters.*`, and all `Newtonsoft.Json.Utilities.*` used by deserialization paths.
- Deserialization uses `MissingMemberHandling.Ignore` — unknown fields in newer save versions are silently dropped instead of throwing.
- Field renames require a `saveVersion` bump and migration function mapping the old key name to the new one — not handled via `MissingMemberHandling`.

### Key Interfaces

All async methods accept an optional `CancellationToken` for shutdown safety. On mobile, if the OS backgrounds or terminates the app mid-write, the operation is cancelled rather than leaving a partial file.

```csharp
// Primary persistence contract
// NOTE on accumulative methods (ModifyGoldAsync, AddUnlockAsync, etc.):
//   These are write-semaphore-protected accumulators that atomically read-modify-write
//   the save data under a single lock. They are NOT domain logic — domain validation
//   (e.g., "can player afford this?") is owned by domain services (ICurrencyService,
//   IWorldStateService, ILoreService). These methods are the final write gate that
//   guarantees no lost updates when multiple systems mutate persistence in the same frame.
public interface IPersistStateService
{
    UniTask PersistStateAsync(CancellationToken ct = default);
    UniTask<PersistentSaveData> LoadPersistentAsync(CancellationToken ct = default);
    UniTask<RunStateSaveData> LoadRunStateAsync(CancellationToken ct = default);

    // Accumulative writes (protected by write semaphore — domain services call these,
    // not IPersistStateService directly. Domain validation is upstream in domain services.)
    UniTask ModifyGoldAsync(long delta, CancellationToken ct = default);
    UniTask ModifyPremiumCurrencyAsync(long delta, CancellationToken ct = default);
    UniTask AddUnlockAsync(string heroId, string zoneId, CancellationToken ct = default);
    UniTask AddLoreFragmentAsync(string fragmentId, CancellationToken ct = default);
    UniTask ApplySettingsAsync(float masterVolume, float sfxVolume, float musicVolume,
                                bool screenShakeEnabled, string languageCode,
                                CancellationToken ct = default);

    UniTask RunMigrationAsync(CancellationToken ct = default);
    event Action<PersistentSaveData> OnPersisted;
}

// Sync orchestrator — decoupled from save/load and transport
public interface IProfileSyncService
{
    UniTask SyncProfileAsync(PersistentSaveData data, CancellationToken ct = default);
    UniTask QueueSyncAsync(PersistentSaveData data, CancellationToken ct = default);
    UniTask ReplaySyncLogAsync(CancellationToken ct = default);
    UniTask CompactionSyncLogAsync(CancellationToken ct = default);
    bool IsSyncPending { get; }
}
```

### Architecture Diagram

```
                                    ╔══════════════════╗
                                    ║  Game Systems    ║
                                    ║  (Currency, Camp,║
                                    ║   Lore, etc.)    ║
                                    ╚═══════╤══════════╝
                                            │ ModifyGoldAsync / AddUnlockAsync / ApplySettingsAsync
                                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    IPersistStateService                              │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ SaveManager (IPersistStateService impl)                       │  │
│  │  - persistent.json → Newtonsoft.Json serialization            │  │
│  │  - runstate.json  → per-run ephemeral state                   │  │
│  │  - Dirty-flag + debounce coalescing                           │  │
│  │  - Pre-save validation (SaveDataValidator)                    │  │
│  │  - Versioned migration (MigrationRegistry)                    │  │
│  └───────────────────────┬───────────────────────────────────────┘  │
└──────────────────────────┼──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    IProfileSyncService                               │
│  ProfileSyncService (IProfileSyncService impl)                        │
│  ├── Payload mapping (PersistentSaveData → server payload)          │
│  ├── Dirty state tracking + retry/error policy                      │
│  ├── .synclog persistence + compaction                              │
│  ├── Conflict resolution (merge rules per field type)               │
│  └── Offline reward notification (OfflineRewardData)                │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    IBackendService / WebSocketSQL                    │
│  Backend Transport                                                    │
│  ├── Receives synced profile payload                                 │
│  ├── Server validates: maxBalanceGold, maxPremiumCurrency, velocity  │
│  └── Returns authoritative snapshot or quarantines                   │
└─────────────────────────────────────────────────────────────────────┘

Event Bus subscriptions:
  SaveManager        ← GameStateChangedEvent   (autosave triggers)
  ProfileSyncService ← GameStateChangedEvent   (sync on Victory/Defeat)
  ProfileSyncService → OfflineRewardData       (toast on reconnect)
```

## Alternatives Considered

### Alternative 1: Binary serialization via Unity's JsonUtility
- **Description**: Use Unity's built-in `JsonUtility` with a `.dat` binary file extension. Strictly typed, no Newtonsoft.Json dependency.
- **Pros**: Zero extra dependencies. Works with IL2CPP out of the box. Supports `[Serializable]` types. Slightly faster serialization.
- **Cons**: No `DateTime` support — requires Unix timestamp wrappers. No `MissingMemberHandling` — unknown fields throw. No JObject manipulation for migration — must deserialize into specific types. No `JsonProperty` attribute for key naming. Cannot serialize `List<ZoneCompletionEntry>` directly (requires wrapper class). Debugging requires manual asset extraction.
- **Rejection Reason**: The template already bundles Newtonsoft.Json. JsonUtility's limitations (no DateTime, no forward-compatible handling, no JObject migration) would require custom wrapper code that replaces Newtonsoft.Json's built-in features — increasing complexity and maintenance burden without removing any dependency.

### Alternative 2: Multi-file split (file per domain)
- **Description**: Separate files for profile (`profile.json`), world state (`world.json`), settings (`settings.json`), and run state (`runstate.json`). Each written independently.
- **Pros**: Smaller individual writes. Partial corruptions only affect one domain. Parallel writes possible.
- **Cons**: No cross-field atomicity — a crash between writing `profile.json` and `world.json` leaves inconsistent state where, e.g., currency reflects a zone unlock but the zone completion is lost. Requires transaction-like coordination or accept data races between domains.
- **Rejection Reason**: Cross-field atomicity is a hard requirement. The multi-file approach would need a transaction coordinator (write-ahead log or two-phase commit) that is more complex than the single-file solution. Single-file with `persistent.json` + `runstate.json` (two files with explicit ordering) provides atomicity for persistent data while keeping ephemeral state separate.

### Alternative 3: Server-authoritative with absolute balance push
- **Description**: Client pushes its absolute gold and premiumCurrency values to the server on each sync. Server trusts the client value.
- **Pros**: Simpler client logic. No per-device earnings tracking. No earnings delta reporting.
- **Cons**: Any client bug, memory corruption, or deliberate manipulation permanently alters the authoritative balance. No fraud prevention. No reliable multi-device merge — absolute values from two devices race, and newest-wins means whichever device syncs last overwrites the other's earnings.
- **Rejection Reason**: Single-device fraud and multi-device merge conflicts are unacceptable. The delta-reporting model with `totalEarnedPerDevice` tracking provides server-authoritative balance while supporting offline play, multi-device, and fraud detection.

## Consequences

### Positive
- Single-file `persistent.json` guarantees cross-field atomicity — one atomic write covers profile, world, and settings together
- Atomic write pattern (temp → rename) prevents corruption from crashes mid-write
- Plain-text JSON enables debugging, manual editing (dev only), and forward-compatible schema evolution
- Dirty-flag+debounce coalescing prevents I/O thrashing from rapid sequential persist calls
- Server-authoritative economy prevents fraud while supporting offline play with eventual consistency
- ProfileSyncService separation keeps transport concerns out of Save/Profile, enabling independent evolution of sync strategy
- Conflict resolution per field type handles all scenarios without forcing an inappropriate one-size-fits-all strategy

### Negative
- Single-file atomic writes serialize all persistent data together — settings slider drag triggers a full profile write (mitigated by 500ms settings-specific debounce)
- JSON is slower to serialize/deserialize than binary — mitigated by small data size (< 1KB typical for profile state)
- Orphan runstate recovery is inherently imperfect: worst case loses this run's uncommitted earnings since last autosave
- `.synclog` adds a file on disk that must be replayed on start — adds ~50ms to boot time on average

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| IL2CPP strips Newtonsoft.Json reflection-accessed types | Silent field loss on device builds | `[JsonProperty]` annotations + `link.xml` preservation (including Newtonsoft.Json internals) + CI IL2CPP build verification |
| `JObject.ToObject<T>()` uses `Reflection.Emit` at runtime | Crash on any IL2CPP build | Migration functions use `JsonConvert.DeserializeObject<T>()` exclusively — never `JObject.ToObject<T>()` or `Populate()` |
| `File.Move` with `overwrite: true` not atomic on iOS/Android storage backends | Partial write corruption | Explicit `File.Delete(dest)` + `File.Move(src, dest)` two-step pattern. No reliance on the `overwrite` overload. |
| OS terminates app during async I/O (mobile background/terminate) | Data loss of in-flight write | All async APIs accept `CancellationToken`. Shutdown hooks (`Application.wantsToQuit`) block until pending write completes. |
| Disk full mid-write | Save rejected, game data unchanged | IOException caught, original file intact, error logged |
| Migrations fail mid-step (exception in migration function) | Data loss | Backup created before migration, restored on failure. Migration runs in-memory — no write occurs until migration completes. |
| Newtonsoft.Json 3.2.1 regression with IL2CPP generic collections (Unity 6000.0–6000.1.x) | Deadlock on `DeserializeObject` under IL2CPP | Verify patch status on Unity 6000.3.11f1 before implementation. If unpatched, add `AOTPreserve()` for generic collection types. |
| `.synclog` unbounded append growth on mobile with frequent sync | Disk space exhaustion | Max 100 entries before forced sync. Max 5MB file size before truncation with warning. Per-entry creation timestamp capped at 7 days. |
| `link.xml` insufficient for Newtonsoft.Json internal types | Runtime `MissingMethodException` on device | Include exact type entries: `Newtonsoft.Json.Serialization.*`, `Newtonsoft.Json.Converters.*`, `Newtonsoft.Json.Utilities.*`, and all concrete `JsonConverter<T>` implementations. |
| Malicious client replays old snapshot with bumped timestamp | Fraud | Server validates timestamps (rejects ≤ `lastAcceptedTimestamp` + future timestamps) |
| Multiple rapid autosaves (GState transitions in quick succession) | I/O thrashing | Dirty-flag+debounce coalescing — 60 calls = 1 disk write |
| Newtonsoft.Json version conflict if Unity updates the package | Serialization incompatibility | Pin to bundled version; migration path if `saveVersion` changes |

## GDD Requirements Addressed

| GDD System | Requirement | How This ADR Addresses It |
|------------|-------------|--------------------------|
| save-profile-persistence.md | Local-first, JSON via Newtonsoft.Json (Rules 1–2) | Decision A — serialization engine choice with `[JsonProperty]` IL2CPP safety |
| save-profile-persistence.md | Single-file consolidation + atomic write (Rules 3, 11, 15) | Decision B — `persistent.json` consolidation with temp→rename pattern |
| save-profile-persistence.md | Versioned schema with migration functions (Rule 3) | Decision C — `saveVersion` comparison + sequential migration map |
| save-profile-persistence.md | Coalesced writes dirty-flag+debounce (Rule 19) | Decision D — coalescing layer above write semaphore |
| save-profile-persistence.md | ProfileSyncService orchestrator (Rule 9) | Decision E — intermediate service defining interface boundaries |
| save-profile-persistence.md | Server-authoritative balance + per-device credits (Rule 7) | Decision F — delta-reporting economy model |
| save-profile-persistence.md | Conflict resolution per field type (Rule 6) | Decision G — four strategies with per-field assignment |
| save-profile-persistence.md | Sync queue persisted to `.synclog` (Rule 16) | Decision H — append-only log, compaction, last-attempt expiry |
| save-profile-persistence.md | AOT safety / MissingMemberHandling (Platform section + Rule 3) | Decision I — `[JsonProperty]`, `link.xml`, `MissingMemberHandling.Ignore` |
| save-profile-persistence.md | Async API (Rule 13) | Key Interfaces return `UniTask` for all operations |

## Performance Implications

| Metric | Impact |
|--------|--------|
| **CPU** | Negligible — serialization is sub-ms for < 1KB payloads. Debounce ensures max 10 disk writes/second. |
| **Memory** | Payload held in memory only during serialization and sync window (~100KB max for worst-case profile). Released after write/sync completes. |
| **Load Time** | ~5ms for deserialization + migration check. `.synclog` replay adds ~50ms. No blocking on network. |
| **Network** | Sync payload < 2KB. Min 15-minute interval per device. 50K gold/day rolling cap bounds worst-case data transfer. |

## Migration Plan

No existing save data to migrate — this is a greenfield project. The migration system (Decision C) is implemented upfront to support future schema evolution:
1. `CurrentSaveVersion` set to 1 at implementation
2. Migration registry empty (no v1→v2 function yet)
3. Forward migration tested via AC4 (upgrade v1→v2) and AC5 (reject v3 from future build)

## Validation Criteria

- **AC1-AC29** from `design/gdd/save-profile-persistence.md` Acceptance Criteria — all pass
- Cross-field atomicity: crash during `persistent.json` write never corrupts existing save
- Orphan recovery: crash between Defeat write and runstate deletion credits earnings exactly once
- Conflict resolution: union-merge never removes unlocks; newest-wins timestamps deterministic
- Sync queue persistence: `.synclog` survives app termination; entries replayed on restart; compaction reduces N entries to 1
- IL2CPP preservation: server IL2CPP build serializes + deserializes `PersistentSaveData` without silent field loss
- Debounce coalescing: 60 rapid `PersistStateAsync()` calls produce exactly 1 disk write

## Related Decisions

- **ADR-001 (update required)**: Rename `IProfileService` → `IPersistStateService` in Core layer registration table. Move to Foundation layer. ADR-001's `ConfigureCore` must change to `builder.Register<SaveManager>(Lifetime.Singleton).As<IPersistStateService>()` in `ConfigureFoundation`. `IProfileSyncService` registers in Core.
- **ADR-002 (update required)**: Add `OfflineRewardData` as a new event type in the Event Type Catalogue. Publisher: ProfileSyncService. Subscribers: HUD system (toast display). Published on reconnect after offline earnings are applied.
- GDD: `design/gdd/save-profile-persistence.md` — full design with schema, formulas, edge cases, ACs
- GDD: `design/gdd/lore-fragment-system.md:68` — references `SaveProfile.AddLoreFragmentAsync(fragmentId)` — must be updated to `IPersistStateService.AddLoreFragmentAsync()`
