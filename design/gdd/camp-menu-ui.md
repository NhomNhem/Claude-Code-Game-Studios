# Camp Menu UI

> **Status**: Designed

> **System ID**: #33 | **Layer**: UI | **MVP**: Yes
> **Depends on**: Hero Camp Progression (#28), Currency (#11), World State (#13)

## 1. Overview

The Camp Menu is the persistent between-run hub. It shows upgrade trees for purchase, zone/run history, and visual representation of camp growth. Players spend currency here between runs.

## 2. Detailed Rules

- Shown in Hero Camp scene, accessible via Camp interaction
- Tabs: Upgrades (tree with purchase buttons), Codex (lore fragments), Map (zone progress)
- Upgrade tree: list of available upgrades with current level, cost, effect preview, purchase button
- Purchase flow: click → confirm → deduct currency → apply upgrade → update UI
- Currency display at top: Gold, Memory Shards
- Zone progress: shows restored zones (lit) and locked zones (grayed out) per World State
- Camp visual state: not rendered in MVP (text-only upgrade list)

## 3. ACs

1. Upgrade list shows all available upgrades with current level and cost
2. Purchase button is disabled if insufficient currency
3. Purchase deducts currency and applies upgrade immediately
4. Currency display updates on purchase
5. Zone progress tab shows restored/locked zones
6. Codex tab shows collected lore fragments
