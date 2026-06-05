# UX Spec: Pause Menu

> **Status**: In Review
> **Author**: user + ux-designer
> **Last Updated**: 2026-06-01
> **Platform Target**: PC (Keyboard/Mouse, Gamepad), Mobile (Touch)
> **Journey Phase(s)**: Mid-run pause, Camp pause
> **Template**: UX Spec

---

## Purpose & Player Need

The player arrives at pause wanting to stop the game, adjust settings, or
exit the run. Pause is a utility screen — the player is not here for content
or discovery. They want minimum friction: freeze the action, see a clear set
of options, make a choice, and get back to what matters (gameplay or quitting).

---

## Player Context on Arrival

| Origin | What they were doing | Emotional state | Design implication |
|--------|---------------------|-----------------|--------------------|
| **InRun** | Mid-combat, dodging enemies | Urgent, time-pressured | Pause must be instant — zero animation delay on open |
| **HeroCamp** | Browsing upgrades or codex | Calm, exploratory | Standard fade-in transition acceptable |

The player chose to pause voluntarily (it is never forced). They arrive knowing
what they want — exit, settings check, or just a breather. The UI should not add
cognitive load.

---

## Navigation Position

The pause menu is an overlay on top of the frozen game world — it does not navigate
to a separate scene. The game world is visible (dimmed) behind it.

```
InRun ──[Escape]──→ Pause Overlay ──[Resume]──→ InRun
                         │
                    [Quit Run]──→ HeroCamp
                         │
                    [Quit to Desktop]──→ (app exit)
                         │
                    [Settings]──→ Settings Overlay
                              │
                         [Back]──→ Pause Overlay
```

---

## Entry & Exit Points

| Entry Source | Trigger | Context carried |
|-------------|--------|----------------|
| InRun | Escape / Start / Pause button | Run state (wave, HP, build, timer) preserved in memory, timeScale=0 |
| HeroCamp | Escape / Start / Pause button | Camp state preserved |
| Settings overlay | "Back" button | Returns to pause with any settings changes applied |

| Exit Destination | Trigger | Notes |
|-----------------|--------|-------|
| InRun | "Resume" button or Escape toggle | Restores pre-pause timeScale, HUD re-shows |
| HeroCamp | "Quit Run" button | Tears down run, saves currency/lore earned, transitions to camp scene |
| App exit | "Quit to Desktop" button | Clean app exit with autosave |
| Settings overlay | "Settings" button | Opens settings within the same pause context |

---

## Layout Specification

### Information Hierarchy

1. **Resume** — primary action, gets player back to the game
2. **Run summary** — time, wave, kills (informational, glanceable)
3. **Settings** — mid-session adjustments
4. **Quit Run** — exit run to camp (only relevant from InRun)
5. **Quit to Desktop** — exit app

### Layout Zones

Single centered modal panel over a dimmed game world background. The panel
occupies ~35% of screen width, vertically centered. Two internal zones:
- **Top**: Title + Run summary (informational, static)
- **Bottom**: Action buttons (interactive)

### Component Inventory

| Component | Type | Interactive | Pattern | Notes |
|-----------|------|-------------|---------|-------|
| Title "PAUSED" | Text label | No | — | Brief uppercase text |
| Run time | Text label | No | — | `12:34` format |
| Wave counter | Text label | No | — | `Wave 5/8` or `FINAL WAVE` |
| Kill counter | Text label | No | — | `142 Kills` |
| Resume button | Text button | Yes | Standard button | Primary action, also triggered by Escape |
| Settings button | Text button | Yes | Standard button | Opens settings overlay |
| Quit Run button | Text button | Yes | Standard button | Only visible when paused from InRun |
| Quit to Desktop button | Text button | Yes | Standard button | Shows confirmation dialog before executing |
| Dimmed game world | Background overlay | No | — | Semi-transparent dark overlay over frozen game |

### ASCII Wireframe

```
┌────────────────────────────────────┐
│         PAUSED                     │
│                                    │
│  ┌── Run Summary ────┐           │
│  │ Time:   12:34     │           │
│  │ Wave:   5/8       │           │
│  │ Kills:  142       │           │
│  └───────────────────┘           │
│                                    │
│  [ Resume ]                        │
│  [ Settings ]                      │
│  [ Quit Run ]                      │
│  [ Quit to Desktop ]               │
│                                    │
│  Escape to resume                  │
└────────────────────────────────────┘
```

"Quit Run" button and run summary are hidden when paused from HeroCamp (no active run).

---

## States & Variants

| State | Trigger | Changes from Default |
|-------|---------|---------------------|
| **Default (InRun)** | Escape during combat | All 4 buttons visible. Game world dimmed behind. |
| **Camp Pause** | Escape in HeroCamp | "Quit Run" hidden (no run to quit). Only 3 buttons. |
| **Settings sub-overlay** | Click Settings | Pause panel replaced by settings panel. Back button returns to pause. |
| **Quit confirmation** | Click Quit Run or Quit to Desktop | Confirmation dialog: "Quit run? Progress will be saved." [Confirm] [Cancel] |
| **Save failure** | Autosave fails during Quit Run | Error toast appears on pause: "Failed to save progress. Try again?" [Retry] [Cancel]. Stays on pause panel. |
| **Loading error** | Scene load fails during Quit Run transition | Error text on black screen: "Failed to load camp." [Retry] [Return to pause]. |
| **Loading transition** | Confirm Quit Run | Brief loading state while camp scene loads |

---

## Interaction Map

| Component | KBM | Gamepad | Touch |
|-----------|-----|---------|-------|
| Resume (button) | Click or press Escape | Navigate to + A, or press Start/B | Tap |
| Settings (button) | Click | Navigate to + A | Tap |
| Quit Run (button) | Click | Navigate to + A | Tap |
| Quit to Desktop (button) | Click | Navigate to + A | Tap |
| Navigation between buttons | Arrow keys / Tab | D-pad / Left stick | Direct tap |
| Confirm in dialog | Enter / Space | A button | Tap Confirm |
| Cancel in dialog | Escape | B button | Tap Cancel or back swipe |
| Toggle pause | Escape | Start button | Pause gesture/button |

---

## Events Fired

| Action | Event | Notes |
|--------|-------|-------|
| Resume | `GameStateChanged(Paused → originState)` | Origin = InRun or HeroCamp |
| Settings | None (UI layer only) | Overlay swaps within pause — no game state change |
| Quit Run | `RunEndedEvent(RunResult.Quit)` then `GameStateChanged(Paused → HeroCamp)` | Run result saved before transition |
| Quit to Desktop | `GameStateChanged(Paused → (quit))` | App triggers autosave then exits |
| Back from Settings | None (UI layer only) | Returns to pause panel |

---

## Transitions & Animations

| Transition | Duration | Behavior |
|-----------|----------|----------|
| Pause open (InRun origin) | 0s (instant) | Game freezes on frame, dim overlay appears. No animation delay — safety-critical for combat pause. |
| Pause open (HeroCamp origin) | 0.15s | Fade dim overlay in. Brief transition acceptable since no combat pressure. |
| Pause close → resume | 0s (instant) | Dim overlay disappears, game resumes on next frame. |
| Settings panel swap | 0.2s | Crossfade between pause panel and settings panel content. |
| Quit confirmation dialog | 0.2s | Scale-up from center (0.8→1.0) with dim backdrop. |
| Quit Run → HeroCamp | 0.5s | Fade to black → loading → camp scene. |
| Quit to Desktop | 0.3s | Brief fade to black, then app exit. |

---

## Data Requirements

| Data | Source System | Read / Write | Notes |
|------|--------------|--------------|-------|
| Run elapsed time | Time System (`RunElapsedTime`) | Read | `MM:SS` format. Freezes on pause (scaled time). |
| Current wave | Wave Spawning (`WaveStartedEvent`) | Read | `Wave 5/8` or `FINAL WAVE`. Hidden when no active run (Camp Pause state). |
| Kill count | Enemy killed events | Read | Cumulative kill count for current run. Hidden when no active run. |
| Pause origin | Game State Manager (`pauseOrigin`) | Read | Determines whether "Quit Run" button and run summary are shown. |
| Autosave trigger | Save/Profile (`IPersistStateService`) | Write | On "Quit Run" and "Quit to Desktop": save before transitioning. |

---

## Accessibility

WCAG-AA baseline (accessibility tier not yet formally defined — see Open Questions).

| Requirement | Implementation |
|-------------|---------------|
| **Keyboard navigation** | Tab / Arrow keys navigate all buttons in logical order: Resume → Settings → Quit Run → Quit to Desktop. Enter/Space to activate. |
| **Gamepad navigation** | D-pad / Left stick navigates buttons. A to confirm, B to go back (acts as Resume). |
| **Focus indicators** | All buttons have visible focus ring or highlight (not just colour change). |
| **Color independence** | Buttons are text-labeled — no icon-only or color-only communication. |
| **Contrast** | White text on dark modal background ≥ 7:1. Button highlights achieve ≥ 4.5:1. |
| **Screen reader** | All buttons have descriptive text. Run summary uses labelled fields ("Run time: 12 minutes 34 seconds"). |
| **No timing pressure** | Pause is fully static — no auto-dismiss timers, no time-limited interactions. |
| **Motion reduction** | Pause open/close from InRun is instant (0s). Settings and confirmation transitions are short (≤0.2s) and use simple fades. |

---

## Localization Considerations

| Text | English | Max visible chars | Risk |
|------|---------|-------------------|------|
| Title | PAUSED | 6 | Safe — short in all target languages |
| Button | Resume | 6 | Safe |
| Button | Settings | 8 | Safe |
| Button | Quit Run | 8 | Moderate — `Run beenden` (DE, 12 chars) fits |
| Button | Quit to Desktop | 16 | **HIGH** — `Desktop verlassen` (DE, 18), `Quitter vers le bureau` (FR, 23). Button width must accommodate ~40% expansion. |
| Confirm | Quit run? | 9 | Moderate |
| Confirm | Progress will be saved. | 25 | **HIGH** — ~35 chars in German/French. Dialog width must accommodate. |

All buttons should use horizontal padding that allows 40% text expansion without breaking layout.

---

## Acceptance Criteria

- [ ] Pause opens instantly (≤1 frame) when Escape/Start is pressed during InRun — no animation delay
- [ ] All buttons are reachable via keyboard Tab/Arrow in order: Resume → Settings → Quit Run → Quit to Desktop
- [ ] All buttons are reachable via gamepad D-pad in the same order
- [ ] "Quit Run" button and run summary are hidden when the game is paused from HeroCamp
- [ ] Run summary displays correct time, wave, and kill count for the active run
- [ ] "Quit Run" triggers autosave before transitioning to HeroCamp — save file reflects current run state
- [ ] "Quit to Desktop" shows confirmation dialog; confirming exits the app cleanly; cancelling returns to pause
- [ ] Escape toggles pause — pressing Escape in pause resumes the game, pressing Escape in InRun opens pause
- [ ] Pause correctly preserves `_prePauseTimeScale` — if slow-mo was active, Time.timeScale restores correctly on resume
- [ ] Game world is visible (dimmed) behind the pause overlay — not a black screen
- [ ] Pause panel renders correctly at 1280x720 and 1920x1080 — no text overflow or button clipping

---

## Open Questions

1. **Settings overlay content** — This spec references a Settings overlay but does not define its content (volume, display, input remapping). Needs a separate UX spec when settings are designed.
2. **Accessibility tier** — `design/accessibility-requirements.md` does not exist. This spec assumes WCAG-AA. Formalize the tier before implementation.
3. **Player journey map** — `design/player-journey.md` does not exist. Created at `.claude/docs/templates/player-journey.md` if needed for full player context.
4. **Kill counter source** — Kill count for run summary needs a `KillCountChangedEvent` or similar. Not confirmed to exist in current event catalogue. May need to add to Event Bus message types.
5. **Confirmation dialog design** — "Quit to Desktop" confirmation uses a simple modal. Should this match the camp's confirmation style? Consider consistent dialog pattern across all screens.
