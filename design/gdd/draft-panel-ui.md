# Draft Panel UI

> **Status**: Designed

> **System ID**: #31 | **Layer**: UI | **MVP**: Yes
> **Depends on**: Rune Draft (#23), Skill Data (#3)

## 1. Overview

The Draft Panel appears on level-up, presenting 3 skill options for the player to choose from. It overlays the game with a semi-transparent background (game pauses underneath). Each option shows skill name, element, rarity, type (orbit/burst), and a preview of stats.

## 2. Detailed Rules

- Trigger: `DraftOfferedEvent` published by Rune Draft Service
- Layout: 3 cards in a horizontal row, centered on screen
- Each card shows: element icon, skill name, rarity glow (common=gray, uncommon=green, rare=gold), skill type icon, base damage, cooldown (burst) or radius/speed (orbit), upgrade preview if owned
- Player clicks/taps a card to select. Selection commits via `IRuneDraftService.CommitPick(SkillId)`
- Reroll button (bottom-center): available if free reroll remains
- Close behavior: selection closes panel, game resumes
- Empty state: if no options available, show "All skills mastered" message with auto-close after 3s

## 3. ACs

1. Panel opens on `DraftOfferedEvent` with 3 option cards
2. Card shows element, rarity, name, type, and stat preview
3. Rarity glow matches rarity tier
4. Clicking card commits pick and closes panel
5. Reroll button calls reroll and regenerates options
6. Panel pauses game (Time.timeScale = 0)
7. Panel close resumes game (Time.timeScale = 1)
8. Empty state shows message and auto-closes
