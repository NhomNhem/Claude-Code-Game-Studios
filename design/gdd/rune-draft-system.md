# Rune Draft System

> **Creative Director Review (CD-GDD-ALIGN)**: CONCERNS — accepted 2026-05-29 (upgrade picks now player-curated, maxed-skill auto-close after 3s)
> **Status**: Designed

> **System ID**: #23
> **Layer**: Progression
> **Priority**: MVP
> **Created**: 2026-05-29
> **Design Order**: 21 (Foundation → Core → Feature → Presentation → Polish)
> **Depends on**: Level-Up System (#22), Skill Data System (#3), Build State (#29)
> **Depended by**: Draft Panel UI (#31), HUD (#30)

## 1. Overview

The Rune Draft System manages the level-up choice flow. When the player levels up, the system generates a set of skill options from the global skill pool, offers them to the player via the Draft Panel UI, and commits the chosen skill to the player's Build State. Draft options are weighted by rarity, filtered against the player's existing build, and generated fresh per level.

## 2. Player Fantasy

Each level-up is a moment of power and possibility. Three runes appear — each a different skill, each with its own element, rarity, and potential. You read them, weigh your options, and pick the one that fits your evolving build. The draft is the core decision moment of every run: choose wisely, and your build comes together; choose carelessly, and you'll feel the gap.

## 3. Detailed Rules

**Architecture:**
- `IRuneDraftService` (interface) injected via VContainer in `GameplayLifetimeScope`
- `RuneDraftService` — generates options, validates picks, commits to Build State
- No UI logic — Draft Panel UI (#31) calls `IRuneDraftService` to get options and commit picks

**Draft Trigger:**
- Level-Up System publishes `GameStateChangedEvent(InRun, InRun, DraftContext.LevelUp)`
- `RuneDraftService` listens for `DraftContext.LevelUp` state changes
- On trigger: generate 3 options, publish `DraftOfferedEvent(Option[3])` for UI
- Game is paused while draft is open (Time System scale = 0)

**Option Generation:**
- Pool: all `SkillDefinition` assets in `SkillDatabase` (MVP: 5-6 skills)
- Filter out skills already in the player's Build State (no duplicates in MVP)
- Filter out skills the player has already seen in this draft cycle (same session)
- If pool is empty after filtering (all skills owned): offer upgrade choices for 3 random owned skills — player picks which to upgrade
- If player has maxed all owned skills: offer 3 utility choices (deferred to Alpha) or auto-close after 3s with no selection

**Rarity Weights:**
- Common: 60% weight
- Uncommon: 30% weight
- Rare: 10% weight
- Weighted random selection per option slot (3 independent rolls)
- Slots are independent — two options may be the same skill (low probability with 5-6 skill pool; if it happens, re-roll)

**Rarity Floor:**
- First draft of the run (level 1→2): at least one Uncommon+ option guaranteed (prevents 3× common start)
- No other rarity guarantees. Variance is intentional — some drafts are stronger than others.

**Draft Commitment:**
- Player picks one option via Draft Panel UI → `IRuneDraftService.CommitPick(SkillId)`
- If skill is new: `BuildState.AddSkill(SkillId)` creates a `SkillInstance` at tier 0
- If skill is owned (upgrade pick): `BuildState.UpgradeSkill(SkillId)` increments tier
- Publish `SkillDraftedEvent(SkillId, IsUpgrade)` for UI/Audio/VFX
- Resume game (Time System scale = 1)

**Rerolls (MVP):**
- One free reroll per run. Reroll generates 3 fresh options.
- Additional rerolls are deferred to Alpha (currency-based rerolls, premium rerolls)

## 4. Formulas

```
optionRarity = weightedRandom({Common: 60, Uncommon: 30, Rare: 10})
poolSize = count(availableSkills) - count(ownedSkills)
upgradeChance = poolSize <= 0 ? 1.0 : 0.0
firstDraftFloor = guaranteeOneUncommonPlus ? true : false
```

Where:
- `weightedRandom` — picks a rarity tier by weight; if the filtered pool has no skills of the chosen tier, falls back to the next available tier
- `poolSize` — the number of skills not yet owned (excluding those filtered out by current draft cycle)

## 5. Edge Cases

- **If all skills are owned** (full build, 5 orbit + 2 burst = 7 skills): Offer upgrade choices for random owned skills instead of new skills.
- **If all skills are max tier** (all owned skills at tier 3): Pool is empty. Offer "no choices" state. Draft auto-closes after 3s.
- **If only 1 skill is unowned**: Generate options with that skill + upgrade choices for the remaining slots.
- **If player levels up while draft panel is already open** (shouldn't happen — game is paused): Queue level-up. Process after current draft commits.
- **If player disconnects mid-draft** (online): Draft state is in-memory only. On reconnect, the run state reloads from server — the draft choice will not be persisted mid-transaction. Player picks again on next level-up.
- **If weighted random picks a tier with no available skills**: Fall back to next available tier (e.g., Rare has no candidates → choose Uncommon instead).
- **If two options are the same skill**: Reroll the duplicate slot. This is rare (e.g., 2 out of 3 slots rolling same Common skill with a pool of 5).

## 6. Dependencies

| System | ID | Direction | Notes |
|--------|----|-----------|-------|
| Skill Data System | #3 | Data | Reads `SkillDefinition` assets from `SkillDatabase` |
| Level-Up System | #22 | Trigger | Listens for `GameStateChangedEvent(DraftContext.LevelUp)` |
| Build State | #29 | Data | Commits picked skill to `BuildState.AddSkill()` / `BuildState.UpgradeSkill()` |
| Time System | #6 | Consumer | Pauses game (timeScale = 0) while draft is open |
| Draft Panel UI | #31 | Consumer | Receives `DraftOfferedEvent`, calls `CommitPick()` |
| Game State | #1 | Consumer | Listens for `GameStateChangedEvent` to trigger/resume |

## 7. Tuning Knobs

| Knob | Default | Range | Effect When Max | Effect When Min | Owner |
|------|---------|-------|-----------------|-----------------|-------|
| Options per draft | 3 | 2–5 | More choice, analysis paralysis | Fewer choices, faster drafting | RuneDraftService |
| Common weight | 60 | 40–80 | Most drafts are common skills | Rarity feels meaningless | RuneDraftService |
| Uncommon weight | 30 | 15–40 | Balanced mix | Rare-heavy drafts | RuneDraftService |
| Rare weight | 10 | 5–25 | Rare is genuinely special | Players expect rare every draft | RuneDraftService |
| Free rerolls per run | 1 | 0–3 | Flexible build fixing | Committed to choices | RuneDraftService |
| First draft floor | 1 Uncommon+ | — | Strong start guarantee (always on) | — | RuneDraftService |

## 8. Acceptance Criteria

1. **Draft offers 3 options on level-up** — When level-up triggers draft, 3 skill options are generated and published via `DraftOfferedEvent`.
2. **Options are filtered against owned skills** — Drafted skills are not offered again as new skills (may appear as upgrade choices).
3. **Rarity weighted selection** — Option rarity distribution matches weighted random (over many drafts, ~60% Common, ~30% Uncommon, ~10% Rare).
4. **First draft guarantees one Uncommon+** — The first draft (level 1→2) always includes at least one Uncommon or Rare option.
5. **Pick commits to Build State** — When `CommitPick(SkillId)` is called, the skill is added to Build State via `AddSkill()`.
6. **Upgrade pick upgrades owned skill** — If the picked skill is already owned, `UpgradeSkill()` increments its tier instead of creating a new instance.
7. **Duplicate skill re-roll** — If two generated options are the same skill, the duplicate slot is re-rolled.
8. **Empty pool falls back to upgrades** — If all skills are owned, options are upgrade choices for random owned skills.
9. **Game pauses during draft** — When draft is open, Time System timeScale is set to 0.
10. **Game resumes after draft** — After `CommitPick()` returns, timeScale returns to 1.
11. **Reroll generates fresh options** — When reroll is used, 3 completely new options are generated.
12. **Fallback tier on empty pool** — If weighted random selects a tier with no available skills, the next available tier is used instead.
