# Codex / Collection UI

> **Status**: Designed

> **System ID**: #34 | **Layer**: UI | **MVP**: Yes
> **Depends on**: Lore Fragment System (#17), Save/Profile (#10)

## 1. Overview

The Codex displays all collected lore fragments and provides narrative context for the world. It's the player's library of discovered memories, organized by zone.

## 2. Detailed Rules

- Tab in Camp Menu UI, also accessible from Run Completion screen
- Layout: zone tabs (Fractured Pass, Crystal Caverns, Ash Circle) → fragment grid
- Each fragment shows: title, flavor text (2-3 sentences), zone origin
- Uncollected fragments show as silhouettes with "???" title
- Newly collected fragments have a "NEW" badge (clears on first view)
- Fragment data read from `ILoreFragmentService.GetAllFragments()` — returns list of `LoreFragmentEntry`
- Sort: by zone, then by collection order within zone
- MVP: no audio playback, no artwork — text-only

## 3. ACs

1. Collected fragments display title and flavor text
2. Uncollected fragments show as hidden (silhouette + "???")
3. "NEW" badge shows on fragments collected but not yet viewed
4. Zone tabs filter fragments by zone origin
5. Fragment data persists via Save/Profile
6. New fragments from run appear in Codex on return to camp
