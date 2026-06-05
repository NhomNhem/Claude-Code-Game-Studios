# HUD

> **Status**: Designed

> **System ID**: #30 | **Layer**: UI | **MVP**: Yes
> **Depends on**: Damage & Health (#19), Currency (#11), Skill Data (#3), Build State (#29), Game State (#1)

## 1. Overview

The HUD is the player's primary source of real-time game state information during a run. It displays health bar, XP bar, currency, active skills (orbit/burst), level indicator, wave/boss status, and incoming damage warnings.

## 2. Detailed Rules

- Player HP bar (top-left): Current/Max HP, with damage flash (red pulse on hit)
- XP bar (below HP): Current XP / XP to next level, fills smoothly
- Level indicator (next to XP): current level number, burst animation on level-up
- Currency display (top-right): Gold count, Memory Shard count
- Orbit skill indicators (bottom-left): one icon per active orbit skill, shows element + tier via border color
- Burst skill indicators (bottom-center): two slots (0 and 1), shows skill icon, cooldown overlay (radial fill)
- Wave/boss status (top-center): "Wave 3/8" during waves, "BOSS" when boss active, boss HP bar when boss phase
- Damage numbers: floating text at damage position, element-colored, critical hits larger
- Alert system: zone entry lore text (5s fade), boss warning ("BOSS INCOMING" 3s), level-up banner

**MVP Damage Numbers:**
- White for normal, element-tinted for elemental damage
- Critical: 1.5x size, bold font
- Stacked damage numbers combine into one (same source, same frame)
- Duration: 1.0s fade-out

## 3. ACs

1. HP bar reflects Current/Max HP with real-time updates
2. XP bar fills as XP is earned, updates on kill
3. Currency display updates on CurrencyChangedEvent
4. Orbit skill indicators show active orbit skills from Build State
5. Burst skill slots show cooldown overlay that depletes over time
6. Wave count displays during wave phase
7. Boss HP bar appears when boss is active
8. Damage numbers float at hit position with element color
9. Level-up banner appears on LevelUpEvent
10. HUD hides during pause menu and draft panel
