# Interaction Pattern Library

> **Status**: Committed
> **Author**: ux-designer
> **Last Updated**: 2026-06-02
> **Platform Target**: PC (Keyboard/Mouse, Gamepad), Mobile (Touch)
> **Accessibility**: WCAG-AA baseline (see design/ux/accessibility-requirements.md)

Extracted and standardized from UX specs for Main Menu (main-menu.md),
Hero Camp (hero-camp.md), HUD (hud.md), and Pause Menu (pause-menu.md).

---

## Pattern 1: Primary CTA Button

*Used in: Main Menu (Play/Hero Camp), Pause Menu (Resume)*

| Property | Value |
|----------|-------|
| **Visual** | Large rectangular button, centered, element-themed accent border |
| **Text** | 16px+ white, center-aligned, 40% horizontal padding for loc |
| **States** | Default, Hover (brightness +15%, scale 1.02), Pressed (scale 0.95), Disabled (alpha 40%) |
| **Input** | Mouse click, Keyboard Enter/Space, Gamepad A |
| **Focus** | 2px gold/yellow outline ring |
| **Audio** | UI confirm click on press |

**Platform notes:**
- PC: Mouse hover + click, keyboard Tab + Enter
- Gamepad: D-pad/Stick navigation, A to confirm, Start as secondary
- Mobile: Touch target ≥44×44pt, no hover states

---

## Pattern 2: Secondary Text/Icon Button

*Used in: Main Menu (Settings, Quit), Pause Menu (Settings, Quit Run, Quit to Desktop), Hero Camp (Menu)*

| Property | Value |
|----------|-------|
| **Visual** | Text-only or icon+text, smaller than primary CTA, grouped with peers |
| **States** | Default, Hover (underline or brightness shift), Pressed (scale 0.95) |
| **Input** | Mouse click, Keyboard Tab + Enter, Gamepad D-pad + A |
| **Focus** | Same 2px gold/yellow ring as primary |

**Layout rule**: Secondary buttons are visually subordinate to primary CTA. Grouped below or beside, not competing for center stage.

---

## Pattern 3: Transient Toast

*Used in: Main Menu (Welcome Back), Hero Camp (New Lore, Purchase Error, Sync Conflict), HUD (Lore Toast)*

| Property | Value |
|----------|-------|
| **Visual** | Compact pill/bar, semi-transparent background, auto-dismiss |
| **Position** | Top-center (menus), mid-right edge (HUD lore toasts) |
| **Timing** | 0.3s slide-in, 2–3s hold, 0.3s slide-out |
| **Interaction** | Non-blocking (informational only) |
| **Z-order** | Above UI panels, below connection banners |

**Variants:**
| Type | Background | Text | Duration |
|------|-----------|------|----------|
| Informational | 30% alpha dark | White | 2–3s |
| Error | Red tint | White | 3s |
| Success | Green tint | White | 2s |

**Accessibility**: No time pressure (informational only). Reduced-motion: skip animation, show then hide.

---

## Pattern 4: Modal Overlay / Dialog

*Used in: Pause Menu (Quit confirmation, error dialogs), Hero Camp (Data Load Error)*

| Property | Value |
|----------|-------|
| **Visual** | Centered panel, backdrop dimmed to 30–40% brightness + optional blur |
| **Transition** | Scale 0.95→1.0 + fade (0.2–0.3s) |
| **Closure** | Explicit action button (Confirm/Cancel/Close) or Escape/B button |
| **Z-order** | Above all other UI |

**Rules:**
- Must have a clear dismiss action (no click-outside-dismiss for blocking errors)
- Escape always closes non-blocking overlays
- Gamepad B always acts as Cancel/Back

---

## Pattern 5: Tab Bar

*Used in: Hero Camp (Camp Menu: Upgrades / Map / Codex)*

| Property | Value |
|----------|-------|
| **Visual** | Horizontal row of text/icon labels, underline or highlight on active |
| **Transition** | Content crossfade (0.15s), underline slides to active tab |
| **Navigation** | Mouse click, D-pad Left/Right, Tab (through tabs only) |
| **States** | Active (accent color, underline), Inactive (dimmed), Hover (brightness) |

**Layout rule**: Tabs sit at top of overlay panel. Active tab content fills remaining panel area.

---

## Pattern 6: Scrollable List

*Used in: Hero Camp (Upgrade rows, Codex fragment list, Zone grid)*

| Property | Value |
|----------|-------|
| **Visual** | Vertical list of rows, each row is a selectable/interactive item |
| **Navigation** | Mouse scroll, Up/Down arrows, D-pad Up/Down |
| **Selection** | Click/tap row, or highlight + Enter/A |
| **Scrollbar** | Thin, auto-hiding, draggable |

**Row anatomy**: Icon/name left → value/state center → action button right (if applicable).

---

## Pattern 7: Pause Overlay (Transient Full-Screen)

*Used in: Pause Menu (during InRun and HeroCamp)*

| Property | Value |
|----------|-------|
| **Visual** | Full-screen semi-transparent dark overlay, game world visible behind |
| **Open** | Instant (0s) from InRun (safety-critical), 0.15s fade from camp |
| **Close** | Instant (0s) — resumes game on next frame |
| **Toggle** | Escape / Start button (same input to open and close) |
| **Content** | Centered modal panel with action buttons + context info |

**Critical rule**: Never animate pause open/close during InRun. Player safety (combat pause) demands zero delay.

---

## Pattern 8: HUD Element (Persistent)

*Used in: HUD (HP bar, XP bar, currency, timer, skill icons)*

| Property | Value |
|----------|-------|
| **Position** | Peripheral zones (top/bottom edges), never over combat center |
| **Opacity** | 100% normal, 30% during pause |
| **Z-order** | World < vignette < damage numbers < banners < bars |
| **Information** | Max 10 simultaneous, ~7–8 typical |
| **Screen coverage** | Never exceed 15% of screen area |

**Elements:**
- Bars: Left-aligned, horizontal fill + text overlay (HP, XP)
- Counters: Right-aligned, icon + compact number (currency, timer)
- Icons: Bottom bar, circular, element-colored border (skills)
- Transient numbers: Spawn at world position, float upward + fade (damage)

---

## Pattern 9: Contextual Banner

*Used in: HUD (Wave counter, Boss HP bar, Level-up, Connection status, Zone intro)*

| Property | Value |
|----------|-------|
| **Position** | Top-center below HUD bar, or top-center above all |
| **Behavior** | Appears on trigger, auto-dismisses or persists per type |
| **Priority** | Connection > Boss > Wave > Level-Up > Zone > Lore (see HUD priority table) |
| **Queueing** | Lower-priority notifications wait for higher to dismiss |

---

## Pattern 10: Confirmation Dialog

*Used in: Pause Menu (Quit to Desktop), potentially in Hero Camp*

| Property | Value |
|----------|-------|
| **Visual** | Small centered modal, "Are you sure?" text + two buttons |
| **Buttons** | Confirm (primary, left or top), Cancel (secondary, right or bottom) |
| **Input** | Enter/Space/A = Confirm, Escape/B = Cancel |
| **Transition** | Scale 0.8→1.0 + fade (0.2s) |
| **Z-order** | Above the overlay that triggered it |

---

## Keyboard Navigation Standard

| Key | Action |
|-----|--------|
| Tab | Forward through interactive elements (visual order) |
| Shift+Tab | Backward through interactive elements |
| Arrow keys | Nested navigation (list rows, tab bar items) |
| Enter/Space | Activate focused element |
| Escape | Close current overlay / dialog / return to previous state |
| F / C / specific keys | Direct shortcuts (camp interact, codex) |

Visible focus indicator (2px gold/yellow outline) on all interactive elements at all times.

## Gamepad Navigation Standard

| Input | Action |
|-------|--------|
| D-pad / Left stick | Move focus between elements (vertical stacks, rows) |
| A / Cross | Confirm / activate |
| B / Circle | Back / cancel / close overlay |
| Start | Open pause (in gameplay) / Settings (in menus) |
| Select / View | (reserved for future use) |

First focus lands on the primary action (Play, Resume). D-pad wraps at list ends.

## Animation Timing Standards

| Use Case | Duration | Easing |
|----------|----------|--------|
| Scene enter/exit | 0.3–0.8s (staggered) | Ease-out |
| Overlay open/close | 0.2–0.3s | Ease-out |
| InRun pause toggle | 0.0s (instant) | None |
| Button press | 0.1s | Squash → stretch |
| Toast slide | 0.3s | Ease-out |
| Content crossfade (tab) | 0.15s | Linear |
| Purchase confirm | 0.5s total | Sequence |
| Hover (brightness) | 0.1s | Ease-out |

Reduced motion: All animations skip to end state instantly when `prefers-reduced-motion: reduce`.
