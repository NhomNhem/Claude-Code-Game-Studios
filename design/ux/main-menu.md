# UX Spec: Main Menu

> **Status**: In Design
> **Author**: user + ux-designer
> **Last Updated**: 2026-06-01
> **Journey Phase(s)**: Unknown — no player journey map
> **Template**: UX Spec

---

## Purpose & Player Need

The Main Menu serves one primary goal: **get the player into a run as fast as possible.** The "Play" action is the hero — the largest, most prominent, most immediately actionable element. All secondary functions (settings, lore codex, stats, notification log) are tucked behind corners or accessible from the Hero Camp after the first run.

Secondary functions the Main Menu serves:
- **Auth gate**: Player connects/logs in before entering the game proper
- **Settings entry**: Volume, controls, resolution — accessible without needing to start a run
- **Notification access**: Offline reward summary from previous session (per save-profile-persistence GDD)
- **Lore taste**: Optional atmospheric hint of the world's theme without forcing reading
- **Quit**: Exit the application cleanly

---

## Player Context on Arrival

**First-ever launch**: Player has just installed/booted the game. They've seen trailers or store page art. Emotional state: excited, curious, slightly impatient. They want to see gameplay, not menus.

**Returning player**: Player has completed at least one run. Emotional state: comfortable, goal-oriented (specific run type or upgrade target in mind). They want to reach the action with minimal friction.

**Post-auth**: The template's `GameManager` handles Login → Home flow. On first launch, this means account creation or auth. On subsequent launches, auto-login if session is valid. The Main Menu appears after auth succeeds.

**Assumption**: The game boots to a branded title/logo screen (template-managed) → auth flow (template-managed) → Main Menu (this spec).

---

## Navigation Position

The Main Menu sits at the root of the game's navigation hierarchy:

```
[Bootstrap] → [Auth / Login] → [Main Menu]
                                   ├── [Hero Camp]     (primary — "Play")
                                   ├── [Settings]       (overlay)
                                   ├── [Notification Log] (overlay, from save-profile)
                                   └── [Quit]           (exit application)
```

From Hero Camp, the player can reach all other screens (Codex, Zone Select, etc.) — those are specced separately. The Main Menu is the first interactive screen after auth and the return point for "return to menu" actions.

---

## Entry & Exit Points

| Entry Source | Trigger | Player carries this context |
|---|---|---|
| Auth flow complete | Template GameManager transitions to Menu state | PlayerId, auth token, session validity |
| Hero Camp → "Main Menu" | Player selects "Main Menu" from camp pause/options | Current persistent state (currency, unlocks, etc.) |
| Failed zone load | Scene Manager error fallback per scene-manager GDD | None — fresh state, logged error |

| Exit Destination | Trigger | Notes |
|---|---|---|
| Hero Camp | Player presses "Play" | Navigate to Hero Camp as the run-prep hub |
| Settings overlay | Player presses "Settings" | Overlay on top of main menu, not a new scene |
| Notification Log overlay | Player opens notification log | Overlay, accessible if offline rewards pending |
| Application quit | Player presses "Quit" | Clean shutdown via Application.Quit() |
| OS-level | System forces close | No special handling — save already persisted |

---

## Layout Specification

### Information Hierarchy

Ranked by importance:

1. **Play button** — Hero action. Largest, most prominent. Text: "Play" (first run / fresh state) or "Hero Camp" (returning player with saved progress)
2. **Settings** — Full settings overlay (audio, video, controls, language). Accessible via icon or text button, visually secondary to Play
3. **Quit** — Small text button, bottom area. Low visual weight
4. **Notification badge** — Small unread indicator on or near Play/Hero Camp area if offline rewards are pending. No text — just a visual indicator (dot, glow, or subtle pulse)
5. **Welcome back toast** — Transient toast near top-center: "Welcome back, [name]". Auto-dismisses after 3s. Does not block interaction.
6. **Version number** — Bottom-right or bottom-center, 10px font, hex value like "v0.1.0"

### Layout Zones

Three-zone vertical stack centered on screen:

```
┌──────────────────────────────────────────────┐
│                TOP ZONE                      │
│     [Welcome back toast — transient]         │
│                                              │
│              CENTER ZONE                     │
│                                              │
│            ┌──────────────┐                  │
│            │    PLAY      │  ← hero button   │
│            │  /HERO CAMP  │                  │
│            └──────────────┘                  │
│                                              │
│          [Settings]   [Quit]                 │
│                                              │
│              BOTTOM ZONE                     │
│         v0.1.0          [notif dot]          │
└──────────────────────────────────────────────┘
```

**Layout rationale**:
- Center zone gets the player's immediate attention — the play button dominates
- Settings and Quit are grouped together below, with Settings first (more likely to be used)
- Bottom zone carries low-importance chrome (version) and a subtle notification indicator
- Welcome toast is top-center, out of the way, transient

**Background**: The menu scene shows atmospheric ruin imagery (per Art Bible: fractured world, sepia/charcoal base, elemental glow hints). The UI overlays this with semi-transparent dark panel behind the center zone for readability.

### Component Inventory

| Zone | Component | Type | Interactive | Pattern |
|------|-----------|------|-------------|---------|
| Center | Play/Hero Camp button | Large button (primary CTA) | Yes | New (first spec — add to pattern library) |
| Center | Settings button | Text/icon button (secondary) | Yes | New |
| Center | Quit button | Small text button (tertiary) | Yes | New |
| Top | Welcome back toast | Auto-dismiss transient toast | No (informational) | New |
| Bottom | Version label | Static text label | No | New |
| Bottom | Notification indicator | Dot/badge icon | No (visual only) | New |

### ASCII Wireframe

```
┌────────────────────────────────────────────────┐
│                                                │
│           ┌──────────────────────┐              │
│           │ Welcome back, Rift. │  ← toast,    │
│           │   (auto-dismiss)    │    transient  │
│           └──────────────────────┘              │
│                                                │
│                                                │
│              ╔══════════════════╗              │
│              ║                  ║              │
│              ║     ▸ PLAY ◀    ║  ← primary   │
│              ║    Hero Camp     ║    CTA       │
│              ║                  ║              │
│              ╚══════════════════╝              │
│                                                │
│               ⚙ Settings    ✕ Quit             │
│                                                │
│          v0.1.0                  ● (notif)     │
│                                                │
│  [Background: fractured ruin, sepia/charcoal,  │
│   subtle elemental particle glow behind UI]    │
└────────────────────────────────────────────────┘
```

---

## States & Variants

| State / Variant | Trigger | What Changes |
|-----------------|---------|--------------|
| **Default** | Menu scene loaded, auth complete | Play button shows "Play" (first run) or "Hero Camp" (returning). No toast. |
| **Welcome Back** | Menu scene loaded, returning player with profile | Play button shows "Hero Camp". Welcome back toast appears top-center, auto-dismisses after 3s. |
| **First Launch** | Menu scene loaded, no profile data | Play button shows "Play". No toast. No notification indicator. |
| **Offline Rewards Pending** | ProfileSyncService has pending offline rewards | Small glowing dot appears near Play button (bottom-right of button or separate indicator). No text. |
| **Settings Open** | Player clicks Settings | Full settings overlay fades in over main menu (semi-transparent backdrop). Menu remains visible behind at reduced brightness. |
| **Loading / Transitioning** | Player clicks Play, scene load initiated | Play button shows brief "Entering..." state or transitions immediately to loading screen (handled by Scene Manager + Loading/Transition system). |
| **Disconnected (offline)** | Auth fails or backend unreachable | Small "Offline" indicator (icon or text) appears near version. Play button still functional (uses OfflineBackendService fallback). |
| **Recovery (post-error)** | Arriving from failed zone load (scene-manager GDD) or auth timeout | Same as Default state, plus subtle banner at top of screen (below welcome toast area): "Returned from [reason]" in muted tone. Auto-dismisses after 5s. Does not block interaction. |

### Platform Variants

| Platform | Changes |
|----------|---------|
| **PC (keyboard + mouse)** | Full layout as designed. Mouse hover effects on all buttons. Keyboard Tab navigation between all interactive elements. |
| **Gamepad** | Same layout. Focus indicator (highlight ring) moves between buttons via D-pad/L-stick. Confirm = A/Cross. Back = B/Circle. Start = Start button. |
| **Mobile (touch)** | Touch target sizes increased by 20% minimum (44x44pt per Apple HIG). Same layout, larger hit areas. No hover states. |

---

## Interaction Map

| Component | Action | Platform Input(s) | Feedback | Outcome |
|-----------|--------|-------------------|----------|---------|
| Play / Hero Camp | Tap/Click | Mouse L-click, Keyboard Enter/Space, Gamepad A | Button press animation (shrink 95%, release). Audio: UI confirm click. Transitions to loading screen. | `GameState.Menu → Loading → HeroCamp` (Scene Manager handles) |
| Settings | Tap/Click | Mouse L-click, Keyboard S (or Tab+Enter), Gamepad A | Icon press animation. Overlay fades in. | Settings overlay opens (UX spec: settings) |
| Quit | Tap/Click | Mouse L-click, keyboard Q (or Tab+Enter), Gamepad B (hold) | Brief fade to black (0.3s), then application quits. | Application.Quit() |
| Welcome back toast | None (auto) | None | Toast slides in from top (0.3s), holds 3s, slides out (0.3s). | No persistent state change |
| Notification indicator | Visual only | None (no tap target) | Pulse animation (subtle scale 1.0→1.1→1.0, 2s cycle). | Visual signal only — actual rewards viewed in Hero Camp or notification log |
| Settings overlay dismiss | Tap/Click outside panel, or specific close button | Mouse L-click outside, Keyboard Esc, Gamepad B | Overlay fades out (0.2s). | Returns to menu state |

---

## Events Fired

| Player Action | Event Fired | Payload / Data |
|---|---|---|
| Click Play / Hero Camp | None (Scene Manager subscribes to GState change, not a direct event from this button) | N/A — Scene Manager handles via GameStateManager |
| Open Settings | `UIEvent(menu, settings_opened)` (analytics) | Timestamp, session ID |
| Close Settings | `UIEvent(menu, settings_closed)` (analytics) | Timestamp, session ID |
| Quit | `UIEvent(menu, quit)` (analytics) | Timestamp, session ID |
| Welcome back toast dismiss | None (transient, no event) | N/A |

**Note**: The Play button does NOT publish a custom event. Per ADR-002, cross-system communication goes through the Event Bus. The button calls `IGameStateManager.TransitionTo(HeroCamp)`, which publishes `GameStateChangedEvent`. Scene Manager subscribes to that event and loads the scene. This avoids coupling the UI button directly to Scene Manager.

---

## Transitions & Animations

| Transition | Animation | Duration | Notes |
|------------|-----------|----------|-------|
| Menu scene enter | Fade in from black. UI elements stagger: background first (0.3s), Play button (0.4s), settings/quit (0.6s), version/chrome (0.8s). Subtle upward slide (10px). | 0.8s total stagger | Avoids overwhelming the player with everything appearing at once. Prioritizes Play button appearing early. |
| Menu scene exit (Play) | Fade to black (0.3s), then Scene Manager handles loading screen | 0.3s | Brief, decisive. No lingering. |
| Menu scene exit (Quit) | Fade to black (0.3s), Application.Quit() | 0.3s | Same as Play exit feel. |
| Settings overlay appear | Overlay fades in + slight upward slide (backdrop alpha 0→0.7) | 0.2s | Fast — player expects instant settings access. |
| Settings overlay dismiss | Overlay fades out (backdrop alpha 0.7→0) | 0.2s | Same speed as appear. |
| Welcome back toast | Slide down from top (hidden→visible, Y offset -40→0) | 0.3s in, 3s hold, 0.3s out | Gentle, unobtrusive. |
| Notification indicator | Subtle pulse scale (1.0→1.1→1.0) | 2s cycle, continuous | Low priority — does not demand attention. |

---

## Data Requirements

| Data | Source System | Read / Write | Update Trigger | Notes |
|------|--------------|--------------|---------------|-------|
| Player display name | Auth / Profile | Read | Read once on scene mount | Used for welcome toast. If unavailable, skip toast. |
| First launch flag | IPersistStateService | Read | Read once on scene mount | Determines button text: "Play" vs "Hero Camp". Read from profile (no profile = first launch). |
| Pending offline rewards flag | IProfileSyncService | Read | Event-driven (subscribe to `OfflineRewardData` on Event Bus) | Shows/hides notification indicator. Does NOT read reward details — only a bool. |
| Offline/connection status | INetworkManager | Read | Event-driven (subscribe to `ConnectionStateChanged` on Event Bus) | Shows/hides offline indicator. Does not block play — uses OfflineBackendService. |
| Version string | Application.version (build constant) | Read | Read once on scene mount | Displayed as label. No write. |

The Main Menu is **read-only** — it displays data but writes nothing to persistence or server in this state.

---

## Accessibility

No accessibility tier has been defined for this project. This section assumes WCAG-AA as a reasonable baseline.

**Keyboard navigation**:
- Tab order: Play/Hero Camp → Settings → Quit (linear, in visual order)
- Focus indicator: 2px gold/yellow outline on all interactive elements
- Enter/Space activates focused element
- Escape closes Settings overlay if open
- No keyboard traps — all interactive elements reachable

**Gamepad navigation**:
- D-pad/L-stick: move focus between buttons (vertical: Play → Settings → Quit)
- A/Cross: confirm/activate
- B/Circle: back (close settings if open, otherwise no-op)
- Start: open settings (secondary entry)

**Contrast & text**:
- Button text: minimum 16px font, white (#FFFFFF) on dark semi-transparent background. Contrast ratio > 4.5:1.
- Version text: 10px, grey (#888888) — informational only, no interaction required
- All interactive text elements meet WCAG-AA minimum contrast

**Color independence**:
- No information is conveyed by color alone
- Notification indicator uses shape (dot) + animation (pulse), not just color
- Hover states use brightness change, not color change exclusively

**Motion sensitivity**:
- All animations are < 1s (meet WCAG 2.3.3 — animation from interactions threshold)
- No parallax or continuous motion in background
- Welcome toast slides, does not flash or strob
- Reduced-motion media query support: if `prefers-reduced-motion: reduce`, all animations skip to end state instantly

---

## Localization Considerations

| Element | Risk | Mitigation |
|---------|------|------------|
| Play / Hero Camp button | Button text length varies significantly by language (e.g., German "Spielen" vs "Heldenlager") | Button minimum width: 200px. Text truncation not allowed — button grows to fit. Max width: 320px. |
| Settings | Short word, low risk | Single word, minimal expansion. No action needed. |
| Quit | Short word, low risk | Same as Settings. |
| Welcome back toast | "Welcome back, {name}" template. Name order varies by locale. | Use `string.Format` with positional placeholder, not string concatenation. |
| Version number | Numbers only, no translation needed | No localization action needed. |

**Text expansion buffer**: All interactive elements reserve 40% additional width for translation expansion. Button minimum size accounts for the longest expected translation.

---

## Acceptance Criteria

- [ ] Main Menu appears within 200ms of auth completion (or within 500ms on first launch)
- [ ] "Play" button is the largest interactive element and appears first in Tab order
- [ ] Clicking Play/Hero Camp transitions to Hero Camp scene (via GameStateManager → Scene Manager)
- [ ] Welcome back toast appears when returning player is detected, and auto-dismisses within 3.5s
- [ ] Welcome back toast does NOT appear on first launch
- [ ] Notification indicator appears when IProfileSyncService reports pending offline rewards
- [ ] Full Settings overlay opens and dismisses with correct animations (0.2s fade)
- [ ] Quit fades to black and exits the application (verified in editor: Application.Quit() is called)
- [ ] Keyboard Tab navigates Play → Settings → Quit in order, with visible focus indicators
- [ ] Gamepad D-pad navigates all interactive elements; A confirms, B closes Settings
- [ ] Offline indicator appears when INetworkManager reports disconnected state
- [ ] All text elements meet WCAG-AA 4.5:1 contrast ratio (verified with color picker)
- [ ] With `prefers-reduced-motion: reduce`, all animations are instantaneous

---

## Open Questions

| Question | Options | Impact | Target |
|----------|---------|--------|--------|
| Player journey map not yet created | Run `/ux-design` Phase 2b or create manually | Without it, player context assumptions are unvalidated | Before Pre-Production gate |
| Accessibility tier not yet defined | WCAG-AA assumed above | May need to be stricter or looser | Before Pre-Production gate |
| Should "Hero Camp" button text change to "Continue" if camp already loaded? | Yes (camp is cached scene) vs No (always navigate fresh) | Affects player expectation of scene loading behavior | During implementation |
| Should the Main Menu show a "New Game" vs "Continue" split if the player has a saved runstate? | Yes (resume risk/reward) vs No (always start fresh in camp) | Save/Profile + Run State integration | During Run State design |
| Notification log overlay — is it a separate spec or part of HUD? | Separate overlay spec vs HUD element | Affects spec ownership | Before HUD design starts |
