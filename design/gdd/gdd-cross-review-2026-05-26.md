# Cross-GDD Review Report

**Date**: 2026-05-26
**GDDs Reviewed**: 10 system GDDs + game-concept.md + systems-index.md
**Systems Covered**: Game State Manager, Event Bus, Skill Data System, Object Pooling, Input System, Time System, Network Manager, Hit Detection, Scene Manager, Save/Profile Persistence
**Engine**: Unity 6000.3.11f1 (URP 17.3)
**Entity Registry**: Empty — all 4 sections (entities, items, formulas, constants) have no entries

---

## Consistency Issues

### Blocking

🔴 **R1: Time.timeScale authority conflict — GState vs Time System**
- **GState** (game-state-manager.md:25-27): `Paused → Time.timeScale = 0`; unpause restores `previousTimeScale` to preserve slow-mo effects.
- **GState AC** (game-state-manager.md:222): "GIVEN Time.timeScale was 0.5 before Paused, WHEN unpause, THEN restores to 0.5, not 1.0."
- **Time System** (time-system.md:21): "On Paused: sets Time.timeScale = 0f. On return to InRun/HeroCamp: restores Time.timeScale = 1f."
- **Time System AC** (time-system.md:110): "GIVEN transitions from Paused to InRun, THEN Time.timeScale == 1."
- Two ACs make opposite assertions about the same operation. Must resolve before either system is implemented.

🔴 **R2: Event Bus Interactions table — missing Victory in Save System subscription**
- **Event Bus** (event-bus.md:107): Save System subscribes to `GameStateChangedEvent(HeroCamp, Defeat)` only.
- **Save/Profile** (save-profile-persistence.md:36-38): Lists Victory as one of 4 autosave triggers, with world state unlock responsibilities.
- **Save/Profile** (save-profile-persistence.md:226): Self-documents this as a known cross-doc gap — "must include Victory in the Save System subscription row."
- Still unresolved. Save autosave on Victory has no Event Bus subscription path.

### Warnings

⚠️ **W1: Formula variable `startingGold` undefined in fraud check**
- save-profile-persistence.md:234 uses `startingGold` in `maxBalanceGold` formula
- No variable table entry for `startingGold` exists (lines 248-250 only define GPM and H)
- Currency System (Not Started, #16 in design order) is expected to define this
- Fraud validation cannot be truth-checked until Currency System exists

⚠️ **W2: Event Bus GDD has duplicate/unfilled template sections at end**
- event-bus.md:180-190 contains three `[To be designed]` stubs (`## UI Requirements`, `## Acceptance Criteria`, `## Open Questions`) that duplicate already-filled earlier sections (lines 163, 172). These should be removed.

⚠️ **W3: GPM/PPH/PDR constants are stubs awaiting Currency System**
- save-profile-persistence.md:248-262 defines fraud detection formulas using GPM (100-500), PPH (1-3), PDR (1.0-1.5) — all placeholders from a Not Started GDD.
- save-profile-persistence.md:327 flags this as `⚠ Currency System Not Started — formula coupling risk`.
- Acceptable for now (design order has Currency System at #11, right after Save/Profile at #9), but must be reconciled before implementation.

⚠️ **W4: Entity registry empty — no conflict baseline**
- `entities.yaml`: All sections empty (entities: [], items: [], formulas: [], constants: [])
- Every cross-referenced fact must be manually validated via full GDD reads. No pre-built conflict baseline.

⚠️ **W5: HeroCamp has no keyboard/gamepad UI navigation**
- input-system.md:37-38: HeroCamp action map only defines `Move, Interact, OpenCodex, StartRun, Pause`
- input-system.md:48-51: Routing table shows `NavigateUI`, `Confirm`, `Back` are all ✗ for HeroCamp
- Players must use mouse in camp — cannot navigate UI via keyboard/gamepad. Violates P3 (Snappy Sessions) feel.

⚠️ **W6: GState BossActive flag ownership undefined but referenced**
- game-state-manager.md:108: Wave Spawning subscribes to `GameStateChanged.BossActive`
- game-state-manager.md:209: Open question "Who owns BossFight flag?" with 3 options, unresolved
- event-bus.md:109: Lists this as established interaction with Wave Spawning
- Downstream systems assume this exists; ownership must be resolved before Wave Spawning (#25) is designed.

### Info

ℹ️ **I1: Event Bus defines events for Not Started systems**
- event-bus.md:105, 157: `ZoneRestoredEvent` — World State (#13) Not Started
- event-bus.md:100, 106, 158: `LevelUpEvent` — Level-Up (#22) Not Started, `CurrencyChangedEvent` — Currency (#16) Not Started
- Event shapes assumed by Event Bus author may not match what those GDDs define.

ℹ️ **I2: GState references "Health System" that doesn't exist**
- game-state-manager.md:92: "InRun → Defeat | Health System (player HP <= 0)"
- `Damage & Health System` (#19) is Not Started. Transition trigger undefined.

ℹ️ **I3: Object Pooling → Scene Manager dependency not reciprocal**
- object-pooling.md:136, 167: Asserts Scene Manager calls `PoolManager.ClearAll()` via VContainer scope lifecycle
- scene-manager.md:221-234: No mention of PoolManager in upstream or downstream dependencies
- Works at runtime via VContainer but is an undocumented dependency.

---

## Game Design Issues

### Blocking

🔴 **D1: Currency System not started — the progression loop has no economic definition**
- 6 resource types designed (gold, premiumCurrency, XP, lore fragments, hero/zone unlocks) — 0 source/sink pairs designed.
- Save/Profile fraud detection (maxBalanceGold, maxPremiumCurrency) uses placeholder constants from a non-existent GDD.
- Offline earnings formula assumes GPM=300 with no design validation.
- Hero Camp Progression (#28), Run Completion (#36) both block on Currency System.
- **Architecture cannot begin until Currency System answers**: earning rates, premium scarcity, spend costs, fraud formula alignment.

### Warnings

⚠️ **D2: Draft-in-combat creates 5 active attention channels (exceeds 4-channel threshold)**
- game-state-manager.md:194: Draft Panel appears over HUD during `InRun` — no pause, no sub-state.
- During draft, player simultaneously manages: (1) movement, (2) aim + burst timing, (3) enemy pattern dodging, (4) draft card reading/evaluation, (5) health/cooldown monitoring.
- This exceeds the 3-4 active system comfortable limit. GState needs a `Drafting` sub-state that pauses combat but preserves arena visual context.

⚠️ **D3: MVP dominant strategy is single-skill stacking (no synergy incentive to diversify)**
- systems-index.md:92: Synergy System deferred to Alpha. MVP Rune Draft offers standalone picks only.
- skill-data-system.md:198-199: Upgrade tiers apply `DamageMultiplier` to `BaseDamage` — 3 upgrades = ~8x damage.
- Optimal play: pick highest-rarity skill, upgrade it every time. No mechanical reason to own 3 different skills.
- Save/Profile serializes multi-skill builds (`SavedSkillEntry[]`) for a loop where single-skill stacking may dominate.
- Accepted scope decision (CD-SYSTEMS CONCERNS), but worth surfacing.

⚠️ **D4: Network Manager pillar declaration = N/A, should acknowledge P4 support**
- network-manager.md:6: `Implements Pillar: N/A (infrastructure)`
- Enable the unique hook: "Online from day one with persistent server-authoritative economy" (game-concept.md:10)
- Directly supports P4 (World Reactivity) by syncing world state. Recommend: "Supports P4."

### Info

ℹ️ **D5: 9/10 player fantasies are "absence of pain" — structurally correct for Foundation/Core**
Only Skill Data System delivers active delight ("palette of possibility"). The other 9 GDDs describe invisible infrastructure. This is architecturally appropriate for Foundation/Core systems.
- MVP scope (5-6 standalone skills, no synergies) may not deliver the Skill Data System's promised variety. Known gap.

---

## Cross-System Scenario Issues

### Scenario 1: Defeat Autosave Sequence

**Systems**: Hit Detection → Event Bus → GState → Event Bus → Scene Manager → Save/Profile → Network Manager

**Trigger**: Player HP reaches 0 during InRun

| Step | System | Action | Status |
|------|--------|--------|--------|
| 1 | Hit Detection | Publishes `HitEvent` to Event Bus | ✅ Designed |
| 2 | [Damage & Health] | Receives HitEvent, reduces HP, detects death | ❌ Not Started (#19) |
| 3 | [Damage & Health] | Publishes `EntityDiedEvent` | ❌ Not Started |
| 4 | GState | Receives event, transitions InRun → Defeat | ✅ Designed |
| 5 | Event Bus | Publishes `GameStateChangedEvent(Defeat)` | ✅ Designed |
| 6 | Save/Profile | Subscribes to Defeat — triggers autosave | ✅ Designed (Rule 5) |
| 7 | Scene Manager | Subscribes to Defeat — loads HeroCamp scene | ✅ Designed |
| 8 | Network Manager | Syncs profile after local write | ✅ Designed (Rule 7) |

**Issues**:
- 🔴 Steps 1→4 are completely dependent on Damage & Health System (#19) which is Not Started. The entire defeat sequence has an unbuilt trigger. Save/Profile autosave on Defeat cannot fire without it.
- ℹ️ Steps 6 and 7 run concurrently. Scene Manager may finish loading before Save/Profile completes the atomic write. Save/Profile Rule 13 (line 295) notes: "If persist is requested during a scene transition, the save completes in the background (async disk write). If the current scene is destroyed during the write, the async continuation runs on the new scene's context." This is documented but should be verified in implementation — running UniTask continuation across scene unload is a known Unity footgun.

### Scenario 2: Victory → Zone Unlock

**Systems**: [Damage & Health] → Event Bus → GState → Save/Profile → Event Bus → [World State] → Event Bus → [VFX]

**Trigger**: Boss killed in zone

**Issues**:
- 🔴 Four downstream systems (World State, VFX, Post-Processing, Hero Camp Progression) are all Not Started. The ZoneRestoredEvent that should fire on victory completion (connecting P4 World Reactivity) has no consumer GDDs defining its behavior.
- 🔴 Save/Profile's autosave on Victory needs Event Bus subscription (`GameStateChangedEvent(Victory)`) which is missing from event-bus.md:107. This is R2 from the consistency section — same gap.

### Scenario 3: Draft Level-Up During Combat

**Systems**: [Level-Up System] → Event Bus → [Draft Panel UI] → GState → Time System → Input System

**Trigger**: Player accumulates enough XP during active combat

**Issues**:
- 🔴 Draft-in-combat tension (D2 from design holism). No pause mechanism defined. All 5 active attention channels active simultaneously.
- ⚠️ GState stays `InRun` during draft (game-state-manager.md:194). Time System continues at normal speed. Combat continues uninterrupted while player reads draft cards.
- ℹ️ Input System correctly disables movement/aim during draft (input-system.md:43 — `Drafting` action map).

### Scenario 4: Offline Reward Recovery

**Systems**: Save/Profile → Event Bus → [HUD] → [ProfileSyncService]

**Trigger**: Game launch with offline earnings pending

**Issues**:
- ℹ️ Two downstream consumers (HUD toast rendering, ProfileSyncService payload mapping) are Not Started. The event pipeline for offline rewards is defined but has no consumers.
- ℹ️ Save/Profile v4 idempotent orphan check (newly added) should handle crash-after-sync correctly, but the profile sync service's retry/conflict logic is not defined.

### Scenario 5: Settings Change During Pause

**Systems**: Input System → GState → Settings UI → Save/Profile → Network Manager

**Trigger**: Player presses Escape → pause → changes volume → unpauses

**Issues**:
- 🔴 Time.timeScale conflict (R1) means unpause may have different timeScale depending on which system handles it. If Time System overwrites GState's 0.5 with 1.0, hit-stop and slow-mo effects are lost on every pause cycle.
- ⚠️ Save/Profile settings in consolidated file: a volume slider change during pause triggers full persistent.json serialize + atomic write. With 500ms debounce (Rule 19), a quick pause→change→unpause may not persist the setting before unpause triggers another write. The two writes (settings change + potential Defeat/Victory autosave) are correctly coalesced by the dirty-flag mechanism.

---

## GDDs Flagged for Revision

| GDD | Reason | Type | Priority |
|-----|--------|------|----------|
| game-state-manager.md | Time.timeScale authority conflict with time-system.md (ACs contradict) | Consistency | Blocking |
| time-system.md | Time.timeScale conflict with game-state-manager.md (restores 1f vs previousTimeScale) | Consistency | Blocking |
| event-bus.md | Missing Victory in Save System subscription (known stale reference) | Consistency | Blocking |
| event-bus.md | Stub template sections at end of file (duplicate/empty) | Consistency | Warning |
| input-system.md | No NavigateUI in HeroCamp — keyboard/gamepad can't navigate camp UI | Design | Warning |
| network-manager.md | Pillar declaration = N/A, should acknowledge P4 support | Design | Info |
| save-profile-persistence.md | startingGold variable undefined in fraud formula (awaiting Currency System) | Consistency | Warning |

---

## Verdict: FAIL

One or more blocking issues must be resolved before architecture begins.

### Required actions before re-running:

1. **Resolve R1 (Time.timeScale authority)**: Pick one system to own timeScale management:
   - **Option A**: GState owns it (current behavior: preserves external scales on pause/resume). Time System syncs to GState's value via `OnTimeScaleChanged` event (line 27 already supports this). Modify time-system.md:21 to "sync with GState-managed timeScale" instead of hard-coding 1f. Fix AC at time-system.md:110.
   - **Option B**: Time System owns it (always resets to 1f on unpause). GState defers to Time System for scale management. Remove timeScale from GState's responsibilities (modify game-state-manager.md:25-27). Fix AC at game-state-manager.md:222.

2. **Resolve R2 (Event Bus missing Victory)**: Add `Victory` to event-bus.md:107: Save System row. Data changes from `GameStateChangedEvent(HeroCamp, Defeat)` to `GameStateChangedEvent(HeroCamp, Defeat, Victory)`.

3. **Design Currency System (#11)** before beginning architecture. The entire progression economy — earning rates, premium scarcity, spend costs, fraud formula alignment — must exist as a design document before architecture decisions about save validation, sync protocol, or offline rewards can be finalized.

---

## Resolution — 2026-05-27

### R1: Time.timeScale authority — RESOLVED

**Choice**: Time System owns all `Time.timeScale` management. GState delegates (removed Core Rule 6).

| File | Change |
|------|--------|
| game-state-manager.md | Removed Core Rule 6 (`Time.timeScale` behavior). Removed `previousTimeScale` from stored data. Updated Interactions Time System row. Updated AC 214/222. |
| time-system.md | Updated Rule 2: saves `_prePauseTimeScale` on pause entry, restores on exit (preserves slow-mo). Updated AC 110 (verifies 0.5 → pause → 0.5, not 1.0). Added hit-stop overlap edge case. |

**Rationale**: Option A variant (Time System owns scale, preserves external modifiers across pause). The Time System already subscribes to `GameStateChanged` and manages hit-stop; consolidating all timeScale logic in one system avoids the dual-authority conflict. External slow-mo effects (power-ups, status effects) survive pause/unpause because `_prePauseTimeScale` captures them before pause entry.

### R2: Event Bus missing Victory subscription — RESOLVED

| File | Change |
|------|--------|
| event-bus.md:107 | Added `Victory` to Save System row: `GameStateChangedEvent(HeroCamp, Defeat, Victory)` |
| event-bus.md | Removed duplicate stub template sections (lines 180-190, W2 cleanup). |
| save-profile-persistence.md:226 | Removed "known cross-document gap" note — replaced with "Resolved". |

### R3: Currency System fraud formula reconciliation — RESOLVED

| File | Change |
|------|--------|
| save-profile-persistence.md | Added `startingGold` and `startingPremium` variable tables to fraud formulas. Updated dependency note (removed "Not Started" warning, references Currency System Section 4.6). |
| currency-system.md (Section 4.6) | Already defines GPM=300, PPH=2, PDR=1.2, startingGold=0, startingPremium=0. No changes needed — alignment confirmed. |

**Reconciliation check**: All five constants (GPM, PPH, PDR, startingGold, startingPremium) match between Currency System and Save/Profile. Ranges in Save/Profile (e.g., GPM 100–500) are tuning ranges; defaults now reference Currency System as authoritative source.

### Remaining Blockers

None. All three blocking issues resolved.

### Remaining Warnings

| ID | GDD | Status | Priority |
|----|-----|--------|----------|
| W4 | Entity registry (entities.yaml) | Still empty — not a blocker | Info |
| W5 | input-system.md | HeroCamp keyboard navigation gap | Warning |
| W6 | game-state-manager.md | BossActive flag ownership unresolved | Warning |
| D2 | Level-Up / GState | Draft-in-combat 5-channel overload | Design warning (accepted) |
| D3 | Skill Data / Save | MVP single-skill stacking dominance | Design warning (accepted) |
| D4 | network-manager.md | Pillar declaration N/A vs P4 | Info |
| I1–I3 | Various | Not Started system dependencies | Info |
