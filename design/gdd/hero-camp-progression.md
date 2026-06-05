# Hero Camp Progression

> **CD-GDD-ALIGN**: N/A (between-run meta layer)
> **Status**: Designed

> **System ID**: #28 | **Layer**: Progression | **MVP**: Yes
> **Depends on**: Save/Profile (#10), Currency (#11), World State (#13)
> **Depended by**: Camp Menu UI (#33)

## 1. Overview

Hero Camp Progression manages persistent account-wide upgrades purchased with currency earned across runs. Upgrades include stat boosts (max HP +10%, damage +5%), starting-currency bonuses, and cosmetic unlocks. This is the "keep getting stronger" meta-layer that gives every run purpose.

## 2. Player Fantasy

Every run makes you stronger. Even failed runs earn currency that you spend between runs to improve your chances. The camp grows visually as you upgrade — new structures appear, the fire burns brighter, fragments fill display pedestals.

## 3. Detailed Rules

- `ICampProgressionService` — injectable, reads/writes upgrade state via Save/Profile
- Upgrades are ScriptableObject definitions: `UpgradeDefinition` with `upgradeId`, `displayName`, `costCurve`, `maxLevel`, `statModifier` (type, value per level)
- Purchased upgrades stored in `SaveData.CampUpgrades: Dictionary<string, int>` (upgradeId → currentLevel)
- Currency spent: Gold (earned in runs) and Memory Shards (earned from lore fragments)
- Refund/crafting: no refund in MVP

**MVP Upgrade List:**
| Upgrade | Max Level | Cost per Level | Effect per Level |
|---------|-----------|----------------|------------------|
| Vitality | 5 | 100/200/400/800/1600 gold | Max HP +5% |
| Force | 5 | 100/200/400/800/1600 gold | All damage +3% |
| Fortune | 3 | 200/400/800 gold | Starting gold +50 |
| Resilience | 3 | 300/600/1200 gold | First draft guarantees Rare |
| Fragments | 5 | 100/200/400/800/1600 memory shards | Lore fragment drop rate +10% |

## 4. Formulas

`statBonus(upgradeId) = baseValue × upgradeLevel × levelMultiplier`
`totalCost(upgradeId, targetLevel) = sum(costCurve[level] for level = currentLevel to targetLevel)`

## 5. ACs

1. Upgrades persist between runs via Save/Profile
2. Purchasing upgrade deducts currency immediately
3. Insufficient currency blocks purchase
4. Max-level upgrade shows "MAX" state, cannot be purchased
5. Stat bonuses apply at run start (read from save on InRun entry)
6. Camp visual state reflects upgrade level (deferred — MVP uses text only)
7. Upgrade definitions read from ScriptableObject registry
