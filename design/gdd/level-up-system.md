# Level-Up System

> **Creative Director Review (CD-GDD-ALIGN)**: APPROVED — 2026-05-29
> **Status**: Designed

> **System ID**: #22
> **Layer**: Progression
> **Priority**: MVP
> **Created**: 2026-05-29
> **Design Order**: 20 (Foundation → Core → Feature → Presentation → Polish)
> **Depends on**: Event Bus (#2), Save/Profile (#10)
> **Depended by**: Rune Draft (#23), HUD (#30)

## 1. Overview

The Level-Up System manages per-run XP accumulation and level progression. It subscribes to `EntityDiedEvent`, awards XP based on the killed enemy's value, tracks the current level's XP threshold, and publishes `LevelUpEvent` when the threshold is crossed. The system resets each run — level is a single-run progression, not persistent.

## 2. Player Fantasy

Every kill feeds your growth. Each enemy you defeat adds to your XP bar, and when it fills, you gain a level — a burst of power and a choice of new skills. The cadence creates a rhythm: fight → level → choose → fight harder. Levels are the heartbeat of each run.

## 3. Detailed Rules

**Architecture:**
- `ILevelUpService` (interface) injected via VContainer in `GameplayLifetimeScope`
- `LevelUpService` subscribes to `EntityDiedEvent` in `Start()`
- `LevelRuntimeState`: `int CurrentLevel`, `int CurrentXp`, `int XpToNextLevel`

**XP Award:**
- On `EntityDiedEvent.Target`: look up enemy's XP value from enemy definition (in Enemy AI or Zone Definition)
- `CurrentXp += xpValue`
- If `CurrentXp >= XpToNextLevel`: level up
- Excess XP carries over to next level (no reset on level-up)
- XP is accumulated only for the player (enemy deaths award XP to player only, regardless of killer)

**Level-Up Flow:**
1. `CurrentXp >= XpToNextLevel` detected after XP addition
2. `CurrentXp -= XpToNextLevel` (excess carries over)
3. `CurrentLevel += 1`
4. Recalculate `XpToNextLevel` using level curve formula
5. Publish `LevelUpEvent(NewLevel, CurrentLevel)`
6. Trigger Rune Draft via GState (publish `GameStateChangedEvent(InRun, InRun, DraftContext.LevelUp)`)
7. Audio System plays level-up chime (via LevelUpEvent subscriber)
8. VFX System plays level-up burst (via LevelUpEvent subscriber)

**XP Threshold Curve (MVP):**
- Level 1→2: 100 XP
- Level 2→3: 150 XP
- Level 3→4: 225 XP
- Level 4→5: 338 XP
- Level 5+: `previousThreshold × 1.5` (capped at 2000 XP per level)
- Max level in a single run: 10 (soft cap — XP continues to accumulate but no more level-ups)

**XP Per Enemy:**
- Basic enemy: 10 XP
- Elite enemy: 30 XP
- Boss: 100 XP
- XP values are configured per enemy type in Enemy AI definition

**Run Reset:**
- On run start (InRun state entered): `CurrentLevel = 1`, `CurrentXp = 0`, `XpToNextLevel = 100`
- On run end (Defeat/Victory): state is discarded (no persistence)
- Hero Camp progression uses a separate, persistent progression system

**XP Notifications:**
- `CurrentXp` changes are exposed via `OnXpChanged(Action<int, int>)` for HUD bar display
- HUD subscribes to `LevelUpEvent` for level indicator updates

## 4. Formulas

```
xpToNextLevel(level) = min(baseThreshold × growthFactor^(level-1), 2000)
baseThreshold = 100
growthFactor = 1.5
maxLevelPerRun = 10
```

Where:
- `baseThreshold` — XP needed for level 1→2
- `growthFactor` — geometric growth per level
- `maxLevelPerRun` — soft cap; XP accumulates past this but no level-ups occur

## 5. Edge Cases

- **If XP is earned after max level**: `CurrentXp` continues to increase but no `LevelUpEvent` is published. XP bar shows "MAX" state.
- **If multiple enemies die in the same frame**: Each `EntityDiedEvent` is processed independently. If two kills push XP past the threshold, only one level-up occurs (excess carries to next level as normal). Sequential processing ensures correct count.
- **If Rune Draft is triggered but no skills are available** (misconfigured): `GameStateChangedEvent` still fires. Draft Panel handles empty draft state (show "no choices" message). Level-up still occurs.
- **If EntityDiedEvent has no XP value** (missing config): XP is 0. No crash. Log a warning.
- **If player levels up at exact same frame as dying**: Both events process in order they're published. If `EntityDiedEvent(Player)` fires before the kill that would level the player, the run ends before the level-up. If the kill fires first, the player levels up before the dying event — valid sequence.
- **If run is restarted mid-level**: State is discarded. Fresh `LevelRuntimeState` on new `InRun` state. No leftover data.
- **If XP threshold exceeds int range** (impossible at 1.5 growth with 10 level cap — max is ~3840): Threshold stored as `int`. No overflow risk.

## 6. Dependencies

| System | ID | Direction | Notes |
|--------|----|-----------|-------|
| Event Bus | #2 | Consumer | Subscribes to `EntityDiedEvent`, publishes `LevelUpEvent` |
| Save/Profile | #10 | None (run-reset) | Level state is per-run, not persisted |
| Game State | #1 | Producer | Publishes `GameStateChangedEvent` to trigger Draft |
| Enemy AI | #24 | Data | Reads per-enemy XP value from definition |
| Rune Draft | #23 | Trigger | Level-up triggers draft panel |
| Audio System | #14 | Consumer | Plays level-up chime on `LevelUpEvent` |
| VFX System | #15 | Consumer | Plays level-up burst on `LevelUpEvent` |

## 7. Tuning Knobs

| Knob | Default | Range | Effect When Max | Effect When Min | Owner |
|------|---------|-------|-----------------|-----------------|-------|
| Base XP threshold | 100 | 50–300 | Slow early progression | Fast early levels | LevelUpService |
| Growth factor | 1.5 | 1.2–2.0 | Steep curve, few late levels | Shallow curve, many levels per run | LevelUpService |
| Max level per run | 10 | 5–20 | Caps build power growth | Too few levels to build | LevelUpService |
| XP cap per level | 2000 | 1000–5000 | High ceiling for late levels | Hard cap slows late progression | LevelUpService |
| Basic enemy XP | 10 | 5–25 | Fast leveling from mobs | Leveling tied to elites/bosses | Enemy definition |
| Elite enemy XP | 30 | 15–60 | Elites are primary level sources | Barely worth more than basics | Enemy definition |
| Boss XP | 100 | 50–200 | Big boss level reward | Boss kill = ~1 level | Boss definition |

## 8. Acceptance Criteria

1. **XP awarded on enemy death** — When `EntityDiedEvent` fires, XP value from the killed enemy's definition is added to `CurrentXp`.
2. **Level-up fires at threshold** — When `CurrentXp >= XpToNextLevel`, `LevelUpEvent` is published with correct `NewLevel`.
3. **Excess XP carries over** — If XP gain exceeds the threshold, remaining XP carries to the next level.
4. **XP curve grows per level** — Each subsequent level requires more XP following the `1.5×` growth formula.
5. **Max level blocks further level-ups** — At level 10, `LevelUpEvent` is no longer published, but XP still accumulates.
6. **Rune Draft triggered on level-up** — When level-up occurs, `GameStateChangedEvent(InRun, InRun, DraftContext.LevelUp)` is published.
7. **State resets on run start** — When entering `InRun`, level state is reset to level 1, 0 XP.
8. **State discarded on run end** — When leaving `InRun` (Defeat or Victory), level state is cleared.
9. **Multiple simultaneous kills produce correct count** — Multiple `EntityDiedEvent` in one frame each add XP. Only one level-up if threshold crossed once.
10. **XP bar updates via callback** — `CurrentXp` changes invoke `OnXpChanged` for HUD display.
11. **Missing XP value is handled** — `EntityDiedEvent` with no XP config results in 0 XP and a logged warning.
12. **Level-up at max level still accumulates XP** — Post-max-level XP bar shows "MAX" but `CurrentXp` continues incrementing.
