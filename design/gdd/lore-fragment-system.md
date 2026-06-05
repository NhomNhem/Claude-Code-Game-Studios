# Lore Fragment System

> **Status**: Designed
> **Design Order**: #17 (MVP)
> **Category**: Narrative
> **Layer**: Core
> **Implements Pillar**: P1 (Rifts Tell Stories)
> **Depends On**: Save/Profile Persistence (#10)
> **Depended On By**: Codex UI (#33), Hero Camp Progression (#28), Run Completion (#36)

---

## 1. Overview

The Lore Fragment System is both a data layer and a narrative delivery mechanic. When an elite or boss dies, the system checks whether the player has already collected the entity's assigned memory fragment — if not, it auto-credits the fragment via Save/Profile persistence and publishes a collection event. The HUD shows a brief toast ("Memory Fragment recovered"); the VFX system spawns a zone-color ripple ring at the collection point. Between runs, the Codex UI reads the fragment database to display collected memories as runic cards with readable text. Every elite is a potential story beat: the system connects combat outcomes to world-building without requiring the player to stop fighting.

The system owns fragment data definitions (`MemoryFragmentData` ScriptableObjects), collection trigger logic (responding to `EntityDiedEvent`), and a read-only query layer for the Codex. It does not own lore text authoring (Writer), Codex rendering (Codex UI), or VFX playback (VFX System). All formula fields are locked in for future narrative power track integration, but MVP lore is passive Codex text only.

---

## 2. Player Fantasy

**Discovery moment**: When the ripple ring flares and the stinger hits, the player doesn't see a loot notification — they feel an echo. *Something just dropped that mattered.* A 3-frame camera micro-freeze on the kill, a half-second audio swell, the memory tablet visible on the ground for ~1s before auto-collect. The player's gut says: *"Whose memory was that?"*

**Codex moment**: In the Hero Camp, they open a white-on-black runic card and read first-person testimony — a technician's final report, a queen's order to freeze her own people, an archmage's last incantation. The fragments are intimate and unreliable; each one shifts the player's theory about the central mystery (accident? sacrifice? intention?). The Codex is quiet, the text is unskippable on first read, and the player feels *they found something precious and sad*.

**Replay incentive**: Players will revisit zones they've outgeared just for the next fragment. That's P1 working — not a failure. Codex progress is never gated (no unlockable tied to "read all fragments"). The reward is the story itself, pure.

**P1 delivery (MVP)**: Lore is passive text only in MVP. The narrative power track (mechanical benefit for lore-correct picks) is deferred per CD-SYSTEMS. But the collection feel (micro-freeze, stinger, ripple) and the Codex presentation (rune card, unskippable first read) ship in MVP — the fantasy is the *story*, not the stat bonus.

---

## 3. Detailed Rules

### 3.1 Fragment Data Model

Each fragment is defined as a ScriptableObject (`MemoryFragmentData`):

| Field | Type | Example | Description |
|-------|------|---------|-------------|
| `fragmentId` | string | `"memory_fire_archmage_warning"` | Unique ID, matches SkillData `LoreFragmentKey` |
| `zoneId` | string | `"zone_fire"` | Which zone this fragment belongs to |
| `figureId` | string | `"fire_archmage"` | Named figure associated with this fragment |
| `dropSource` | enum | `Elite / Boss` | What triggers this fragment (MVP: Elite and Boss only) |
| `rarity` | enum | `Common / Rare / StoryCritical` | Display priority in Codex |
| `memoryText` | string | `"The Archmage sealed the first Rift..."` | The readable lore text |
| `runeGlyph` | string | `"ᚠ"` | Decorative glyph for the Codex card face |
| `worldStateEffect` | enum | `None` | Reserved for post-MVP. Always `None` in MVP. |

Drop table mappings are defined in `LoreDropTable` ScriptableObjects per zone, referenced by entity type ID. Each elite type specifies one unique first-kill fragment ID and (optionally) a fallback generic pool. Boss types specify one story-critical fragment ID.

### 3.2 Collection Triggers

1. **Elite kills** (first kill): The first time the player kills a given named elite type in any run, a guaranteed unique fragment drops. The Lore Fragment System tracks `killedEliteTypesThisRun: List<string>` in run-state to enforce first-kill detection.
2. **Elite kills** (repeat): Subsequent kills of the same elite type draw from a small generic pool (1-2 "Fragment of a Life" entries per zone). These entries are repeatable — the same generic text may appear across multiple runs. Once the generic pool is fully collected, no further lore drops from that elite type.
3. **Boss kills**: Guaranteed drop of 1 story-critical fragment unique to the boss. Boss fragments are always first-kill guaranteed (bosses are single-encounter per run).
4. **Run-completion bonus**: Not an MVP trigger. Awarding zone fragments on boss kill undermines P1 discovery (the journey, not the destination). Deferred.
5. **Future: Hidden/side fragments**: Non-combat discoverable fragments placed in the arena (deferred from MVP).

**Duplicate prevention**: If all fragments from an elite type are already collected, the elite still shows a brief dimmed flash on death — a visual nod that lore was "checked" but nothing new was found. No toast, no stinger, no ripple VFX. This maintains P1's "every kill matters" feel without the dead-air silence of suppressed feedback.

### 3.3 Collection Flow

1. Entity dies → `EntityDiedEvent` published via Event Bus with `isConfirmedDeath: bool` flag. Lore system only processes events where `isConfirmedDeath == true` (defence against revive/unconfirmed death mechanics).
2. Lore Fragment System receives event, checks the entity's type ID against `killedEliteTypesThisRun` and `collectedLoreFragmentIds`.
3. Resolves which fragment to drop: first-kill guarantee → unique fragment; repeat → generic pool entry if available; exhausted → no fragment (see duplicate prevention visual).
4. If a fragment is eligible, credits it immediately:
   a. Appends fragment ID to `collectedLoreFragmentIds` via `IPersistStateService.AddLoreFragmentAsync(fragmentId)`
   b. Appends entity type ID to `killedEliteTypesThisRun`
5. Publishes `LoreFragmentCollectedEvent(fragmentId, zoneId)` on Event Bus.
6. Consumers fire in ordered sequence (all receive the event simultaneously, but each observes a priority ordering for sequencing):
   - Frame 0: Camera micro-freeze (3-frame hold on kill)
   - Frame 1: Fragment tablet spawns at death location, visible for ~1s
   - Frame 2: Ripple VFX + audio stinger
   - Frame 4: HUD toast ("Memory Fragment recovered", 3s duration)
7. At run end, `loreFragmentIdsThisRun` is flushed to persistent storage. The flush uses union-merge: distinct IDs only, no duplicates persisted. If `AddLoreFragmentAsync` already wrote mid-run, the flush deduplicates against the existing persistent list.

### 3.4 Event Bus Messages

| Event | Direction | Payload | Description |
|-------|-----------|---------|-------------|
| `LoreFragmentCollectedEvent` | Outgoing | `{ fragmentId: string, zoneId: string }` | Published when a fragment is collected. HUD toast, VFX ripple, World State zone restore trigger (future). |
| `EntityDiedEvent` | Incoming | `{ entityId, faction, isConfirmedDeath: bool, eliteTypeId: string }` | Consumed only when `isConfirmedDeath == true`. `eliteTypeId` must be populated for loot-eligible entities. |

### 3.5 Codex Data Provider

Exposes read-only data for Codex UI:

```
GetAllFragments() → List<MemoryFragmentData>
GetCollectedFragmentIds() → List<string>
GetFragmentById(string id) → MemoryFragmentData
GetFragmentsByZone(string zoneId) → List<MemoryFragmentData>
GetFragmentsByFigure(string figureId) → List<MemoryFragmentData>
GetUncollectedCount() → int
GetFragmentReadState(string id) → bool
MarkFragmentRead(string id)
```

Read state is local-only (never synced). A fragment transitions from "unread" to "read" when the player explicitly clicks the "translate" toggle on the fragment card in the Codex (switching from runic glyph view to readable text). This allows a "New" badge on fragments that have been collected but not yet read in the Codex.

### 3.6 Save/Profile Integration

Per Save/Profile GDD:
- `collectedLoreFragmentIds`: `List<string>` in `persistent.json` — union-merge persistence (once collected, never removed)
- `loreFragmentIdsThisRun`: `List<string>` in `runstate.json` — ephemeral per-run tracking
- `AddLoreFragmentAsync(fragmentId)`: appends to persistent list during run (mid-run persist for crash safety)
- On run end, run-state fragments are flushed to persistent storage. The flush uses union-merge: `collectedLoreFragmentIds = collected.Union(loreFragmentIdsThisRun).Distinct().ToList()`. Mid-run writes (`AddLoreFragmentAsync`) and run-end flush coexist; the union-merge deduplicates any overlap.
- `killedEliteTypesThisRun`: `List<string>` in `runstate.json` — tracks first-kill guarantee per run. Reset on run start.

**Force-quit edge**: Mid-run fragment persistence means the player keeps lore from a run they force-quit. This is accepted — premium single-player game with no competitive economy. The player keeps the story reward even if the run "didn't happen."

### 3.7 MVP Scope Note

MVP lore is **passive text in the Codex** only. The narrative power track (P1 deferred feature — mechanical reward for lore-correct elemental picks) is post-MVP. MVP design ensures:
- Fragment data model reserves future fields (`worldStateEffect`, `mechanicalRewardId`) but both are `None` / empty in MVP — no unused serialization
- Lore Fragment System does NOT need to know about skills, damage, or combat mechanics
- The system is a pure data layer — collect, persist, display
- Only Elite and Boss drop sources are active in MVP. ZoneCompletion trigger is removed from the trigger enum.
- Generic "Fragment of a Life" pool is MVP-optional (default: include with 1 entry per zone). If narrative content is the bottleneck, remove the pool and accept that some elite types become lore-complete after the first kill.

---

## 4. Formulas

None. The Lore Fragment System is a data collection and display layer with no mathematical calculations. All behavior is governed by the collection rules in Section 3.

---

## 5. Edge Cases

### 5.1 Player Collects the Same Fragment Twice (Crash + Rollback)

The `collectedLoreFragmentIds` union-merge in Save/Profile prevents duplicates. If the fragment is already in the persistent list, the second `AddLoreFragmentAsync` call appends a duplicate string ID. On next load, the union-merge deduplicates — no harm, but log a warning. **Mitigation**: The Lore Fragment System checks `collectedLoreFragmentIds.Contains(fragmentId)` before calling `AddLoreFragmentAsync` in non-crash scenarios. In crash scenarios, the redundant `AddLoreFragmentAsync` call with a duplicate is harmless (union-merge cleans it up).

### 5.2 Player Repeats a Zone After Collecting All Fragments

All elite types in the zone have exhausted their unique and generic fragment pools. On kill, a dimmed flash appears at the death location — visual feedback that lore was "checked" but nothing new was found. No toast, no stinger, no ripple VFX. The player completes the run without new lore rewards; satisfaction shifts to currency and progression.

### 5.3 Elite Killed Off-Screen (Lore Pops Without Context)

The fragment collection is silent in combat — a brief toast in the HUD corner suffices. The player reads the fragment later in the Codex. No modal, no mid-combat text.

### 5.4 New Fragments Added in a Patch (Player Has Existing Save)

New fragments are added to the ScriptableObject database. Existing players find them as new drops on their next elite/boss kill. The `collectedLoreFragmentIds` union-merge means old collections are preserved; new IDs are simply uncollected. No migration needed.

### 5.5 Player Uninstalls and Reinstalls (Server Restore)

On reinstall, the server sync restores `collectedLoreFragmentIds` via union-merge. If the player has a cloud-synced profile, all collected fragments are restored. If the player chose to start fresh (no cloud), fragment list is empty.

### 5.6 Player Force-Quits Mid-Run After Collecting a Fragment

Mid-run `AddLoreFragmentAsync` already committed the fragment to persistent storage. On next launch, the persistent data includes the fragment — the player keeps lore from a run that "didn't happen." This is accepted for a premium single-player game: the story reward is retained even if the run was abandoned. No competitive advantage exists.

### 5.7 Elite Dies with `isConfirmedDeath = false`

If the Hit Detection system emits an `EntityDiedEvent` with `isConfirmedDeath = false` (e.g., a revive mechanic, phylactery, or cancelled death), the Lore Fragment System ignores the event entirely. No fragment is credited, no tracking state is updated. The system waits for the confirmed death event before crediting lore.

### 5.8 Entity Has No Drop Table

If an entity dies but has no `eliteTypeId` or no matching `LoreDropTable` entry, the Lore Fragment System silently ignores it. No error, no fragment. This handles the expected case of non-elite enemies dying — they never carry lore.

---

## 6. Dependencies

### Hard Dependencies (must exist before implementation)

| System | # | Nature of Dependency |
|--------|---|----------------------|
| Save/Profile Persistence | 10 | Persists `collectedLoreFragmentIds` (union-merge). API: `AddLoreFragmentAsync()`. Provides run-state tracking for `loreFragmentIdsThisRun` and `killedEliteTypesThisRun`. |
| Event Bus | 5 | Consumes `EntityDiedEvent` with required fields `isConfirmedDeath: bool` and `eliteTypeId: string`. Publishes `LoreFragmentCollectedEvent`. |

### Soft Dependencies (consume this system)

| System | # | Nature of Dependency |
|--------|---|----------------------|
| Codex UI | 33 | Reads fragment data via `GetAllFragments()`, `GetCollectedFragmentIds()`, `GetFragmentReadState()`. Calls `MarkFragmentRead()`. |
| HUD | 30 | Subscribes to `LoreFragmentCollectedEvent` for "Memory Fragment recovered" toast. |
| Camera System | — | Subscribes to `LoreFragmentCollectedEvent` for 3-frame micro-freeze. |
| VFX System | 15 | Subscribes to `LoreFragmentCollectedEvent` for zone-color ripple at collection point. |
| Audio System | 14 | Subscribes to `LoreFragmentCollectedEvent` for collection stinger. |
| World State | 13 | Future: subscribes to `LoreFragmentCollectedEvent` for zone restoration triggers. |

---

## 7. Tuning Knobs

| Knob | Default | Range | Affects | Owner |
|------|---------|-------|---------|-------|
| Fragment toast display duration | 3s | 1–10s | How long the "Memory Fragment recovered" toast stays visible | Designer |
| Max unread badge count | 99 | 1–999 | Caps "New" badge in Codex | Designer |
| Elite unique fragment pool size | 3 per zone | 1–10 | Number of unique fragments per zone for first-kill guarantee | Writer |
| Generic pool size per zone | 1 | 0–3 | Number of repeatable "Fragment of a Life" entries. Set to 0 to disable generic pool. | Designer |
| Story-critical fragment count per zone | 1 | 0–3 | Number of boss-only unique fragments | Writer |

No mathematical tuning knobs — fragment data is authored as ScriptableObject content, not parameter-driven.

---

## 8. Acceptance Criteria

### Collection (First-Kill Guarantee)

- **AC1** — **GIVEN** an elite entity dies with `eliteTypeId = "fire_elite_01"` AND `isConfirmedDeath = true` AND `killedEliteTypesThisRun` does NOT contain `"fire_elite_01"` AND `collectedLoreFragmentIds` does NOT contain `"memory_fire_elite_01"`, **WHEN** the Lore Fragment System processes the kill, **THEN** `killedEliteTypesThisRun` contains `"fire_elite_01"`, `AddLoreFragmentAsync("memory_fire_elite_01")` is called, AND a `LoreFragmentCollectedEvent` is published with correct `fragmentId` and `zoneId`.
- **AC2** — **GIVEN** a boss entity dies with `isConfirmedDeath = true` AND a unique story-critical fragment `"memory_boss_fire_01"`, **WHEN** processed, **THEN** the story-critical fragment is credited AND no other zone fragment is credited.
- **AC3** — **GIVEN** the same elite type dies a second time in the same run (`killedEliteTypesThisRun` already contains `"fire_elite_01"`) AND the generic pool has uncollected entries, **WHEN** processed, **THEN** a generic "Fragment of a Life" entry is credited IF one remains in the pool, or a dimmed flash appears with no credit IF the pool is exhausted.

### Collection (Unconfirmed Death)

- **AC4** — **GIVEN** an elite entity dies with `isConfirmedDeath = false` AND `killedEliteTypesThisRun` does NOT contain its `eliteTypeId`, **WHEN** processed, **THEN** no fragment is credited, no tracking state is updated, and no event is published.

### Persistence

- **AC5** — **GIVEN** `collectedLoreFragmentIds = ["memory_01"]` before a run AND `"memory_02"` is collected during the run, **WHEN** the run ends and autosave completes, **THEN** `persistent.json.collectedLoreFragmentIds` contains both `"memory_01"` AND `"memory_02"`.
- **AC6** — **GIVEN** a crash occurs mid-run after collecting `"memory_03"` AND the player relaunches the game, **WHEN** runstate recovery completes (save system detects orphan `loreFragmentIdsThisRun` and flushes to persistent), **THEN** `collectedLoreFragmentIds` contains `"memory_03"` on the next persistent read.
- **AC7** — **GIVEN** `collectedLoreFragmentIds = ["memory_01"]` before a run AND `loreFragmentIdsThisRun = ["memory_01"]` at run end (player re-collected same fragment after crash rollback), **WHEN** the run-end flush runs union-merge, **THEN** `GetCollectedFragmentIds()` returns `["memory_01"]` (no duplicate persisted).

### Codex

- **AC8** — **GIVEN** `GetCollectedFragmentIds()` returns `["memory_01", "memory_03"]` AND `GetAllFragments()` returns 5 fragments, **WHEN** the Codex UI queries `GetUncollectedCount()`, **THEN** it returns 3.
- **AC9** — **GIVEN** a fragment is collected but `GetFragmentReadState(id)` returns false, **WHEN** the Codex UI renders the fragment grid, **THEN** the fragment shows a "New" badge AND `MarkFragmentRead(id)` is called when the player clicks the "translate" toggle on the fragment card.
- **AC10** — **GIVEN** `GetFragmentById("memory_fire_archmage_warning")` is called, **WHEN** the Codex UI renders the fragment card, **THEN** the returned data includes all fields from the `MemoryFragmentData` schema (§3.1): `fragmentId`, `zoneId`, `figureId`, `dropSource`, `rarity`, `memoryText`, `runeGlyph`.

### Collection Feedback

- **AC11** — **GIVEN** a fragment is collected (`LoreFragmentCollectedEvent` published), **WHEN** the VFX System receives the event, **THEN** a ripple ring VFX spawns at the death location AND the Audio System plays the collection stinger AND the HUD shows "Memory Fragment recovered" toast for the configured duration.
- **AC12** — **GIVEN** an elite dies but all fragment pools are exhausted (dimmed flash scenario), **WHEN** the Lore Fragment System processes the kill, **THEN** a dimmed flash appears at the death location AND no toast/stinger/ripple VFX is triggered.

### Codex States

- **AC13** — **GIVEN** `GetCollectedFragmentIds()` returns an empty list (first-time player), **WHEN** the Codex UI queries `GetAllFragments()`, **THEN** all fragments render with locked/greyed appearance AND `GetUncollectedCount()` equals the total fragment count.

### Cross-Session Persistence

- **AC14** — **GIVEN** a player collects `"memory_01"` in run 1 AND `"memory_02"` in run 2, **WHEN** run 2 autosave completes and the game is relaunched, **THEN** `GetCollectedFragmentIds()` returns both `"memory_01"` AND `"memory_02"`.

### Edge Cases

- **AC15** — **GIVEN** a new zone is added in a patch with `"memory_new_zone_01"`, **WHEN** the existing player loads the game, **THEN** the new fragment ID is present in `GetAllFragments()` AND absent from `GetCollectedFragmentIds()` (available for new drops).
- **AC16** — **GIVEN** `collectedLoreFragmentIds` contains duplicates from a rare race condition, **WHEN** Save/Profile union-merge runs on next load, **THEN** `GetCollectedFragmentIds()` returns unique IDs (no duplicates).
- **AC17** — **GIVEN** an entity dies with no `eliteTypeId` (standard enemy), **WHEN** the Lore Fragment System receives the `EntityDiedEvent`, **THEN** no fragment is credited silently and the event is ignored.
