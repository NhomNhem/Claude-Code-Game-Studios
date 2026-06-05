# UX Spec: Hero Camp

> **Status**: Reviewed — Needs Revision (blocking issues resolved)
> **Author**: user + ux-designer
> **Last Updated**: 2026-06-01
> **Journey Phase(s)**: Between-run hub
> **Template**: UX Spec

---

## Purpose & Player Need

The Hero Camp serves one primary purpose: **spend currency earned from runs to make the next run easier.** The player arrives after every run (Victory or Defeat) and leaves when they choose to start the next one. The camp is a safe, reflective space where progression happens — a warm hearth between battles.

Secondary purposes:
- **Read lore**: Open the Codex to review newly discovered Memory Fragments
- **Plan the next run**: Check which zones are unlocked, select hero loadout
- **Absorb atmosphere**: The camp visually reflects progress — restored color, new structures, growing collection
- **Exit to Main Menu**: Option to return to the title screen

---

## Player Context on Arrival

**First arrival (first run complete)**: Player has just finished their first run (Victory or Defeat). Emotional state: accomplished, curious, eager to spend and explore. The camp is a reward — a quiet moment after combat intensity.

**Returning after Victory**: Player just cleared a zone. Emotional state: triumphant, flush with currency, looking to spend on upgrades and see what new zone unlocked. They want to spend fast and queue the next run.

**Returning after Defeat**: Player just died. Emotional state: frustrated but motivated, eager to spend what they earned and try again. The camp is a soft landing — comforting atmosphere, clear "get stronger" path.

**First-ever login** (no runs completed yet): Player sees the camp for the first time. Emotional state: curious, exploring controls, understanding the hub layout. They need clear affordances for what to do here.

---

## Navigation Position

```
[Bootstrap] → [Auth] → [Main Menu] → [Hero Camp]
                                           │
                                    ┌──────┼──────────┐
                                    │      │          │
                                    ▼      ▼          ▼
                              [Camp Menu]  [Codex]  [Start Run]
                              ┌─────────┐  (overlay) (zone select)
                              │Upgrades │
                              │Map      │
                              └─────────┘

Return paths: Hero Camp → Main Menu (via pause menu)
                          → Loading → InRun (via Start Run)
                          → Main Menu (via pause → quit to menu)
```

Hero Camp is the game's central hub — the player returns here after every run and launches every run from here.

---

## Entry & Exit Points

| Entry Source | Trigger | Player carries this context |
|---|---|---|
| Run complete (Victory) | Run Completion flow → "Continue" button | Currency earned this run, new lore fragments, zone completion data |
| Run complete (Defeat) | Run Completion flow → "Return to Camp" button | Currency earned this run (partial) |
| Main Menu | Player presses "Play" / "Hero Camp" | Profile data, unlocked zones, persistent state |
| Game launch (cached session) | Auto-login → Hero Camp directly (skip Main Menu) | Session token, cached profile |

| Exit Destination | Trigger | Notes |
|---|---|---|
| Zone Select → Loading → InRun | Player activates Start Run | Carries zone choice, hero choice, build state |
| Pause Menu → Main Menu | Player opens pause → "Main Menu" | Returns to title screen |
| Game quit | OS-level or Alt+F4 | Save already persisted on last currency mutation |

---

## Layout Specification

### Information Hierarchy

**Camp Environment (always visible):**

1. **Camp visuals** — Atmospheric environment: campfire, structures, NPCs (if any), particle effects. Sets the mood. Player character stands near campfire/table.
2. **Currency bar** — Persistent at top or top-right of screen: Gold icon + amount, Memory Shard icon + amount. Always visible during camp exploration.
3. **Interact prompts** — Context-sensitive UI near interactable objects: "[F] Upgrades", "[C] Codex", "[Enter] Start Run"

**Camp Menu Overlay (opens on Interact):**

1. **Upgrades tab** (default) — Upgrade tree: list of available upgrades with current level, cost, effect preview, purchase button. Most-used tab.
2. **Map / Zones tab** — Zone progress showing restored (lit) and locked (grayed) zones
3. **Codex tab** — Lore fragments collected, organized by zone or by figure
4. **Back / Close** — Exit the overlay

### Layout Zones

**Camp Environment:**

```
┌────────────────────────────────────────────────┐
│  ┌─── Currency Bar ──────────────────────┐     │
│  │  ★ 1,250 Gold    ◆ 35 Shards          │     │
│  └────────────────────────────────────────┘     │
│                                                 │
│                                                 │
│               CAMP ENVIRONMENT                  │
│        (walkable 2D scene)                      │
│                                                 │
│    ╔═══╗                                        │
│    ║ P ║  ← Player character                    │
│    ╚═══╘══════════════════════╗                 │
│           ┌─ Campfire ───────┐ │                 │
│           │🔥🔥🔥🔥🔥         │ │                 │
│           └──────────────────┘ │                 │
│                               ╘═════════════════╝│
│    ┌───── Interact Prompts ──────┐               │
│    │ [F] Upgrades  [C] Codex     │               │
│    │ [Enter] Start Run           │               │
│    └─────────────────────────────┘               │
│                                         [Menu]   │
└────────────────────────────────────────────────┘
```

**Camp Menu Overlay (opens on Interact, covers center of screen):**

```
┌────────────────────────────────────────────────┐
│  ┌────────── Camp Menu ────────────────────✕ ┐ │
│  │                                           │ │
│  │  ┌────┐  ┌──────┐  ┌─────┐               │ │
│  │  │▸UPGR│  │ MAP  │  │CODEX│ ← tabs        │ │
│  │  └────┘  └──────┘  └─────┘               │ │
│  │                                           │ │
│  │  ┌─ Upgrade Tree ────────────────────┐    │ │
│  │  │  Vitality      Lv.3  400g   [buy] │    │ │
│  │  │  Force          Lv.2  400g   [buy] │    │ │
│  │  │  Fortune        Lv.1  400g   [buy] │    │ │
│  │  │  Resilience     Lv.0  300g   [MAX] │    │ │
│  │  │  Fragments      Lv.0  100msh [buy] │    │ │
│  │  └────────────────────────────────────┘    │ │
│  │                                           │ │
│  └───────────────────────────────────────────┘ │
│                                                 │
│  (Camp environment visible behind at 30%         │
│   brightness with blur)                         │
└────────────────────────────────────────────────┘
```

### Component Inventory

| Zone | Component | Type | Interactive | Pattern |
|------|-----------|------|-------------|---------|
| Environment | Player character | 2D pixel-art sprite | Move (WASD/Stick) | New |
| Environment | Campfire | Animated visual element | No (atmosphere) | New |
| Environment | Upgrade table / area | Interactable hotspot | Yes — opens Camp Menu (Interact key) | New |
| Environment | Start Run portal / gate | Interactable hotspot | Yes — opens Zone Select or starts run | New |
| HUD (persistent) | Currency bar | HUD element (Gold + Shards) | No (read-only) | New |
| HUD (persistent) | Interact prompts | Context-sensitive text hints | No (informational) | New |
| HUD (persistent) | Menu button (pause) | Small icon/button | Yes — opens Pause menu | New |
| Overlay | Camp Menu panel | Modal-like overlay (darkened background) | Container | New |
| Overlay | Tab bar | 3 tabs: Upgrades, Map, Codex | Yes — switches active tab | New |
| Overlay | Upgrade list | Scrollable list of upgrade rows | Each row has [buy] button | New |
| Overlay | Purchase button | Text button per upgrade row | Yes | New |
| Overlay | Zone progress grid | Grid of zone icons (lit/grayed) | Yes — select zone to view details | New |
| Overlay | Codex entry list | Scrollable list of lore fragments | Yes — select to read | New |
| Overlay | Codex reader panel | Full-screen text card for fragment | No (read-only content) | New |
| Overlay | Close (✕) button | Icon button, top-right | Yes — closes overlay | New |

---

## States & Variants

| State / Variant | Trigger | What Changes |
|-----------------|---------|--------------|
| **Loading Profile Data** | Scene loaded, save data not yet available | Camp environment visible with reduced lighting (10% dimmer, 0% blur). Campfire lit but animated at half speed. Player character at spawn but idle. Currency bar shows "-" dashes in place of amounts. Interact prompts hidden. Brief pulsing "Loading..." text near currency bar (fades after 3s if still loading). Enter/Start disabled. Timeout: if load exceeds 5s, transitions to Data Load Error state. |
| **Default (camp exploration)** | Save data loaded | Currency bar populates from IPersistStateService. Interact prompts appear. Environment lighting returns to full brightness. Player controls enabled. |
| **Camp Menu Open (Upgrades)** | Player presses Interact near upgrade table | Semi-transparent overlay opens with dark blur behind. Tab set to Upgrades — upgrade list displayed with costs and purchase buttons. |
| **Camp Menu Open (Map)** | Player clicks Map tab | Zone progress grid shown — lit zones (completed/unlocked) vs grayed (locked). Selected zone shows details. |
| **Camp Menu Open (Codex)** | Player clicks Codex tab | Lore fragment list by zone. First unread fragment highlighted. Selecting opens reader panel. |
| **Reader Open** | Player selects a lore fragment from Codex list | Full-screen reading card: white/cream text on dark background. Fragile parchment aesthetic per art bible. "Close" button returns to Codex list. |
| **Zone Select (start run)** | Player activates Start Run | Zone selection UI: available zones with difficulty, rewards, completion status. "Confirm" starts the run. |
| **First Visit** | No runs completed yet | Subtle tutorial hint: "Approach the table to view upgrades" or similar. Interact prompts pulse gently. |
| **New Lore Available** | New fragment auto-collected from last run | Codex tab has a subtle unread badge/dot. Toast: "New lore discovered" on Hero Camp entry. |
| **Enough currency for upgrade** | Currency balance changes | Upgrade rows where player can now afford appear highlighted or with green [buy] button. Previously unaffordable rows become interactive. |
| **Purchase Error** | Purchase RPC fails (insufficient funds race, network error, save write failure) | Toast: "Purchase failed. Please try again." (3s display). Currency bar re-syncs to authoritative balance from ICurrencyService. Purchase button re-enables after toast dismiss. No further auto-retry. |
| **Save Error** | IPersistStateService write failure detected | Subtle save icon indicator appears in currency bar (small ⚠ icon, fades after 5s or on next successful save). Auto-retry per ADR-006 debounce (500ms coalescing). No disruption to camp gameplay — purchase appears applied locally, retry transparent. If retry fails 5 consecutive times, escalate to persistent toast: "Progress not saving. Check disk space." |
| **Data Load Error** | Save data fails to load (corrupt profile, version incompatibility, disk I/O error) | Error overlay: "Could not load profile data. [Error detail]" with two buttons: "Retry" (re-attempts load) and "Return to Main Menu" (GState → Menu). Player cannot interact with camp until resolved. |
| **Sync Conflict** | Server sync returns conflict (ADR-006 conflict resolution applied) | Toast: "Your data was updated from another device." (3s display). Affected values (currency, upgrade levels, zone unlocks) update to resolved values. No blocking modal — conflict is resolved server-side; toast is informational. |

### Platform Variants

| Platform | Changes |
|----------|---------|
| **PC (keyboard + mouse)** | Full camp navigation with WASD + mouse click on overlay elements. Tab to switch between environment controls and menu controls. |
| **Gamepad** | Left stick/WASD for movement. Interact = A. Camp Menu navigation: D-pad for tab switching, list navigation. Close = B. Start = pause. |
| **Mobile (touch)** | Virtual joystick for movement. Tap interactable hotspots (table, portal). Camp Menu: tap tabs, tap upgrade rows, tap close. Touch targets 44x44pt minimum. |

---

## Interaction Map

| Component | Action | Platform Input(s) | Feedback | Outcome |
|-----------|--------|-------------------|----------|---------|
| Player movement | Move | WASD/Arrows, Left Stick, Virtual joystick | Character walks in direction. Footstep SFX (subtle). | Character position updates in environment |
| Upgrade table | Interact | F key, A/Cross, Tap on hotspot | Character faces table. Brief "open" animation. Overlay fades in. | Camp Menu opens (Upgrades tab default) |
| Start Run portal | Interact | Enter key, A/Cross (near portal), Tap | Character faces portal. Portal glow intensifies. | Zone Select UI opens |
| Codex object | Interact | C key, Y button, Tap | Character faces codex stand. | Codex tab opens directly (skip Camp Menu) |
| Camp Menu tab switch | Click tab | Mouse click, D-pad L/R, Tap | Tab highlight animates to selection. Panel content crossfades. | Active tab changes |
| Upgrade purchase | Click [buy] | Mouse click, A/Cross (on selected row), Tap | Button press animation. Currency amounts update with brief animation. Row shows new level. | Currency deducted, upgrade applied, save triggered |
| Lore fragment select | Click entry | Mouse click, A/Cross, Tap | Entry highlight. Reader panel slides in. | Fragment text displayed |
| Reader close | Click close | Close button, Esc, B, Tap outside | Reader panel slides out. | Returns to Codex list |
| Close Camp Menu | Click ✕ | Esc, B (in menu), Tap ✕ | Overlay fades out with blur reverse. | Returns to camp exploration |
| Open pause | Pause | Escape, Start, pause button | Pause overlay fades in. | Game paused (TimeManager handles timeScale) |
| Start Run confirm | Click Confirm | Enter, A/Cross, Tap | Brief flash/transition. Scene load begins. | GState → Loading → InRun |

---

## Events Fired

| Player Action | Event Fired | Payload / Data |
|---|---|---|
| Purchase upgrade | `UpgradePurchased(upgradeId, newLevel, cost)` | upgradeId string, newLevel int, cost CurrencyAmount |
| Purchase upgrade fails | `PurchaseFailed(upgradeId, reason, cost)` | upgradeId string, reason string, cost CurrencyAmount. Reason: InsufficientFunds, NetworkError, SaveError |
| Save error detected | `EventBus: ErrorEvent(SaveError, message)` (via Error Service) | Error message, retry count |
| Data load error | `EventBus: ErrorEvent(DataLoadError, message)` (via Error Service) | Error message, corrupt file path |
| Sync conflict resolved | `DataChangedEvent(CurrencyUpdate(amounts))` + subsequent `DataChangedEvent(CampUpgradeLevels(levels))` | Updated values post-resolution |
| Open Camp Menu | `UIEvent(camp, menu_opened)` (analytics) | Timestamp |
| Close Camp Menu | `UIEvent(camp, menu_closed)` (analytics) | Timestamp, duration open |
| Open Codex | `LoreFragmentViewed(fragmentIds)` | List of fragment IDs viewed this session (for analytics) |
| Start Run | None (via GState: HeroCamp → Loading → InRun) | ZoneId carried in GameStateContext |
| Open Pause | None (via GState: HeroCamp → Paused) | Origin state = HeroCamp |

---

## Transitions & Animations

| Transition | Animation | Duration | Notes |
|------------|-----------|----------|-------|
| Hero Camp scene enter | Fade in from black. Warm golden light ramps up. Player character appears at spawn point near campfire. | 0.5s | Gentle, welcoming. |
| Camp Menu open | Overlay fades in + slight scale (0.95→1.0). Backdrop blurs and dims (brightness 100%→30%). | 0.25s | Fast, responsive. |
| Camp Menu close | Overlay fades out, backdrop unblurs and brightens. | 0.2s | Same speed. |
| Tab switch | Content crossfade (current panel alpha 1→0, new panel 0→1, 50ms offset). Tab underline slides. | 0.15s | Very fast — no waiting for tab switches. |
| Reader panel open | Panel slides in from right (X offset +200→0). | 0.3s | Feels like page turning. |
| Reader panel close | Panel slides out to right. | 0.25s | Same direction. |
| Purchase confirm | Currency number animates (spin/scale). Row briefly flashes green. Button changes to "Purchased" then back to new level state. | 0.5s total | Satisfying feedback — the spend feels tangible. |
| New lore toast | Slides in from top (same as Main Menu welcome toast pattern): "New lore discovered" | 0.3s in, 2.5s hold, 0.3s out | Consistent toast pattern. |
| Start Run transition | Brief light bloom at portal, fade to black (0.3s), Scene Manager handles rest. | 0.3s | Decisive — no lingering in camp. |
| Purchase error toast | Slides in from top: "Purchase failed. Please try again." with subtle red tint. | 0.3s in, 3.0s hold, 0.3s out | Error-specific toast — distinct from informational toasts. |
| Save error indicator | Small ⚠ icon fades in near currency bar, no other disruption. Auto-retry transparent. | 0.2s fade in, 5.0s hold, 0.3s fade out | Non-blocking — gameplay continues. |
| Data load error overlay | Error panel fades in (0.3s) with two buttons. Player cannot dismiss without action. | 0.3s | Blocking — must retry or exit. |
| Loading indicator | "Loading..." text pulses at 1s cycle (alpha 0.6→1.0). Campfire animation at half speed. | 0.5s delay before appearing, continuous until loaded | Subtle — environment already visible. Timeout at 5s → error state. |

---

## Data Requirements

| Data | Source System | Read / Write | Update Trigger | Notes |
|------|--------------|--------------|---------------|-------|
| Gold balance | ICurrencyService | Read | Event-driven (subscribe to `CurrencyChangedEvent`) | Displayed in currency bar. Updates on purchase or sync. Fallback: show "—" if service unavailable in loading state. |
| Memory Shard balance | ICurrencyService | Read | Event-driven (subscribe to `CurrencyChangedEvent`) | Same as Gold. Fallback: show "—" if service unavailable. |
| Upgrade definitions | UpgradeDefinition ScriptableObjects (ICampProgressionService) | Read | Read once on scene mount | Static — changes only in game updates. Fallback: empty list with toast "Upgrades unavailable" if null. |
| Upgrade levels (purchased) | IPersistStateService (SaveData.CampUpgrades) | Read / Write | Read on mount. Write on purchase. | Dictionary<string, int>. Write triggers PersistStateAsync. Fallback: empty dict (all levels 0). PersistStateAsync failure handled by Save Error state. |
| Unlocked zone IDs | IPersistStateService (PersistentSaveData) | Read | Read once on scene mount | Determines Map tab state (lit vs grayed). Fallback: empty (no zones unlocked — unlikely but handles new profile). |
| Zone completion data | IPersistStateService (PersistentSaveData.ZoneCompletions) | Read | Read once on scene mount | Best times, kills, completion status. Fallback: empty dict (no completions recorded). |
| Lore fragment IDs | IPersistStateService (PersistentSaveData.collectedLoreFragmentIds) | Read | Read once on scene mount | Determines Codex entries. Fallback: empty list (no fragments collected). |
| Lore fragment content | Skill Data / Lore Data (ScriptableObject registry) | Read | Read on Codex tab open | Static content. ID-to-content mapping. Fallback: "Content unavailable" placeholder if ScriptableObject asset missing. |
| Pending offline rewards flag | IProfileSyncService | Read (bool only) | Event-driven (subscribe to `OfflineRewardData`) | Show toast on Hero Camp entry if pending. Fallback: no toast (false assumed if service unavailable). |
| Player display name | Auth / Profile | Read | Read once on scene mount | Not currently displayed in Hero Camp (no welcome toast here). |

The Hero Camp is **read + write** — it reads progression data and writes upgrade purchases via ICampProgressionService → IPersistStateService.

---

## Accessibility

Same WCAG-AA baseline as Main Menu spec.

**Keyboard navigation**:
- Camp exploration: WASD moves character. F = interact (upgrades), C = codex, Enter = start run, Escape = pause.
- Camp Menu overlay: Tab cycles: tab bar → upgrade list → close button. Enter activates. Escape closes overlay.
- Within upgrade list: Up/Down arrows navigate rows. Enter purchases selected row.
- No keyboard traps — Escape always closes the current overlay.

**Gamepad navigation**:
- Exploration: Left stick/D-pad moves character. A = interact/confirm. B = back (close overlay). Start = pause.
- Camp Menu: D-pad Left/Right switches tabs. D-pad Up/Down navigates list. A confirms purchase. B closes overlay.
- D-pad navigation follows visual layout: tabs at top → list below → close button at top-right.

**Contrast & text**:
- Overlay text: minimum 16px, white on dark blur backdrop (>4.5:1)
- Upgrade cost text: minimum 14px, gold accent color (#FFD700) on dark background
- Codex reader text: 18px cream (#F0E6D2) on dark (#1A1A2E) — >7:1 contrast
- Interactive elements (buy buttons) have 2px gold focus indicator

**Color independence**:
- Affordability is shown through button state (enabled/disabled), not just color
- Zone progress uses icon brightness + border (full color = restored, grayscale + dashed = locked), not just color
- Unread codex badge uses shape (dot) + position, not color alone

**Motion sensitivity**:
- All overlay animations < 0.5s (meet WCAG 2.3.3)
- No parallax or continuous background motion
- Camp fire has gentle idle animation but no strobing — particle rate < 15fps simulation
- Reader slide: reduced-motion query makes it instant appear/dismiss

---

## Localization Considerations

| Element | Risk | Mitigation |
|---------|------|------------|
| Upgrade names ("Vitality", "Force", etc.) | Short words, low risk | Fixed-width card layout — 200px min per row. Truncation not allowed. |
| Upgrade effect descriptions | Medium-length text — expansion risk | Description area: 400px max width, can wrap to 2 lines at 40% expansion. |
| Zone names | Short to medium — moderate risk | Zone name area: 250px min width. |
| Codex fragment text | Long text — highest risk | Reader panel width flexible (60-80% of screen width). Text wraps naturally. Full scroll support. |
| "New lore discovered" toast | Short, low risk | Same 40% buffer pattern. |
| Purchase button text ("Buy", "Purchased", "MAX") | Very short, low risk | 80px min button width. |

**Text expansion buffer**: All interactive elements reserve 40% additional width. Upgrade rows min-width: 500px to accommodate effect descriptions at 140% length.

---

## Acceptance Criteria

- [ ] Hero Camp scene loads within 500ms of transition (Main Menu → Hero Camp or Run Complete → Hero Camp)
- [ ] Player character can move freely in the camp environment with WASD/Stick
- [ ] Interact prompts appear near hotspots (Upgrade table, Codex, Start Run portal)
- [ ] Pressing Interact near upgrade table opens Camp Menu overlay (Upgrades tab default)
- [ ] Currency bar updates immediately after a purchase without reloading the scene
- [ ] Upgrade purchase deducts correct cost, applies upgrade, and persists (verified by reloading scene)
- [ ] Insufficient currency shows [buy] button disabled/grayed with no interaction
- [ ] Max-level upgrade shows "MAX" with disabled button
- [ ] Map tab shows correct lit/grayed zone states matching saved progress
- [ ] Codex tab shows collected fragments; selecting one opens reader panel with content
- [ ] Reader panel dismisses with Esc/B/close button and returns to Codex list
- [ ] "New lore discovered" toast appears on Hero Camp entry when new fragments exist
- [ ] Start Run opens zone selection and transitions to Loading → InRun on confirm
- [ ] Escape/Start opens pause overlay; B/Resume returns to camp
- [ ] Tab order in Camp Menu: tab bar → upgrade list → close button (linear, no traps)
- [ ] Gamepad D-pad navigates all Camp Menu tabs and lists; A confirms, B closes
- [ ] All overlay text meets WCAG-AA 4.5:1 contrast ratio
- [ ] With `prefers-reduced-motion: reduce`, all animations are instantaneous
- [ ] All overlay layouts render correctly at 1280×720, 1920×1080, and 3840×2160 (no clipping, no overflow)
- [ ] Purchase failure shows error toast and re-syncs currency bar to correct balance
- [ ] Data load failure shows error overlay with Retry and Return to Main Menu; Retry recovers on next attempt

---

## Open Questions

| Question | Options | Impact | Target |
|----------|---------|--------|--------|
| Should the Camp Menu auto-open on first arrival (new player sees it immediately)? | Yes (guided) vs No (exploration-first) | Affects onboarding flow — first-time player may not know to interact | During implementation |
| Zone Select — is it a sub-panel of the Camp Menu or a separate overlay triggered by Start Run portal? | Camp Menu tab vs Separate overlay | Affects navigation structure and information architecture | Before HUD design starts |
| Hero select — does the player choose a hero in Hero Camp or before each run in a separate screen? | Camp hero pedestal vs Pre-run draft | Affects Camp layout — needs hero display area | Before implementation |
| Notification log overlay — where does it live in the camp? | In Camp Menu tab vs HUD accessible overlay | Affects spec ownership | Before HUD design starts |
| Is there a "return to Main Menu" from the Camp Menu, or only from the pause overlay? | In menu vs Pause only | Affects exit flow | During implementation |
