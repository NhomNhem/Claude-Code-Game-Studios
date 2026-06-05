# Build State

> **CD-GDD-ALIGN**: N/A (runtime data container)
> **Status**: Designed

> **System ID**: #29 | **Layer**: Gameplay | **MVP**: Yes
> **Depends on**: Skill Data System (#3)
> **Depended by**: Rune Draft (#23), Orbit Combat (#20), Burst Skill (#21), HUD (#30)

## 1. Overview

Build State is the runtime container for the player's current skill loadout within a run. It tracks which skills are drafted, their upgrade tiers, and which slots they occupy. It provides the single source of truth that combat systems and UI read from.

## 2. Detailed Rules

- `IBuildState` — injectable interface exposed as a singleton in `GameplayLifetimeScope`
- Data: `List<SkillInstance> Skills`, `Dictionary<string, int> UpgradeTiers` (SkillId → tier), `int[] BurstSlotMap` (slot index → SkillId)
- Orbit skills are not slot-mapped — any orbit skill in the list is active
- Burst skills occupy slot 0 or slot 1 (max 2)
- `AddSkill(SkillId)`: creates `SkillInstance`, assigns to first available burst slot or adds to orbit list
- `UpgradeSkill(SkillId)`: increments tier, notifies combat systems via `SkillUpgradedEvent`
- `RemoveSkill(SkillId)`: removes from list, frees burst slot — used by draft re-roll
- `GetActiveOrbits()`: returns all orbit-type `SkillInstance`s
- `GetBurstSkill(slot)`: returns burst `SkillInstance` for slot 0 or 1
- State is reset on run start, serialized for save only if mid-run save is needed (deferred)

## 3. ACs

1. `AddSkill` adds orbit skill to list and burst skill to first free slot
2. `UpgradeSkill` increments tier and publishes event
3. `RemoveSkill` removes from list and frees slot
4. `GetActiveOrbits` returns only orbit-type skills
5. `GetBurstSkill(slot)` returns burst for that slot or null
6. State resets on run start (InRun → new BuildState)
7. Adding when burst slots full (2 burst already) rejects the skill
