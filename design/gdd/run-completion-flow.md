# Run Completion Flow

> **Status**: Designed

> **System ID**: #35 | **Layer**: UI | **MVP**: Yes
> **Depends on**: Game State (#1), Currency (#11), World State (#13), Lore Fragment (#17), Level-Up (#22)

## 1. Overview

The Run Completion Flow handles the end-of-run transition — victory or defeat. It shows a summary screen, awards currency and lore fragments, updates world state, and transitions back to Hero Camp.

## 2. Detailed Rules

**Victory Flow:**
1. Boss defeat → `GameStateChangedEvent(InRun, Victory, ZoneId)`
2. Play victory sequence (zone restore VFX sweep, audio harmonic)
3. Show Victory screen: zone name, run time, levels gained, gold earned, fragments found, enemies killed
4. Auto-award rewards (gold, fragments) — no "collect" button needed
5. Mark zone as restored in World State
6. "Continue" button → Load Hero Camp scene

**Defeat Flow:**
1. Player death → `GameStateChangedEvent(InRun, Defeat)`
2. Play defeat sequence (brief pause, dim screen)
3. Show Defeat screen: zone name, waves survived, levels gained, gold earned, fragments found
4. Award gold earned during run (reduced: 50% of earned gold)
5. Fragments collected during run are kept (full award)
6. "Try Again" button → restart same zone, "Return to Camp" → Hero Camp

**Reward Calculation:**
```
goldAwarded(victory) = goldEarnedDuringRun
goldAwarded(defeat) = floor(goldEarnedDuringRun × 0.5)
fragmentsAwarded = fragmentsCollectedDuringRun (always full)
xpConversion = 0 (no bonus XP — level-up is run-only)
```

## 3. ACs

1. Victory screen shows after boss defeat with run summary
2. Defeat screen shows after player death with run summary
3. Gold awarded on victory = full amount
4. Gold awarded on defeat = 50% (floored)
5. Fragments awarded on any outcome = full amount
6. World State updated on victory (zone restored)
7. "Continue" on victory loads Hero Camp
8. "Try Again" on defeat restarts same zone
9. "Return to Camp" on defeat loads Hero Camp
