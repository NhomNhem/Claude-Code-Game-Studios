# Accessibility Requirements: Tiny Rift Survivors

> **Status**: Committed
> **Author**: ux-designer
> **Last Updated**: 2026-06-01
> **Accessibility Tier Target**: Standard
> **Platform(s)**: PC (Steam), Mobile (iOS / Android — deferred)
> **External Standards Targeted**:
> - WCAG 2.1 Level AA
> - AbleGamers CVAA Guidelines
> - Xbox Accessibility Guidelines (XAG) — Partial (if console port)
> - PlayStation Accessibility (Sony Guidelines) — N/A (no console port planned)
> - Apple / Google Accessibility Guidelines — N/A (mobile deferred)
> **Accessibility Consultant**: None engaged
> **Linked Documents**: `design/gdd/systems-index.md`, `design/ux/interaction-patterns.md`, `design/ux/main-menu.md`, `design/ux/hero-camp.md`, `design/ux/hud.md`, `design/ux/pause-menu.md`

> **Why this document exists**: Per-screen accessibility annotations belong in
> UX specs. This document captures the project-wide accessibility commitments,
> the feature matrix across all systems, the test plan, and the audit history.
> It is created once during Technical Setup by the UX designer and producer,
> then updated as features are added and audits are completed. If a feature
> conflicts with a commitment made here, this document wins — change the feature,
> not the commitment, unless the producer approves a formal revision.
>
> **When to update**: After each `/gate-check` pass, after any accessibility
> audit, and whenever a new game system is added to `systems-index.md`.

---

## Accessibility Tier Definition

> **Why define tiers**: Accessibility is not binary. Defining four tiers gives
> the team a shared vocabulary, forces an explicit commitment at the start of
> production, and prevents scope creep in both directions ("we'll add it later"
> and "we have to support everything"). The tiers below are this project's
> definitions — the industry uses similar but not identical language. Commit to
> a tier with specific feature targets, not just the tier name.

### Tier Definitions

| Tier | Core Commitment | Typical Effort |
|------|----------------|----------------|
| **Basic** | Critical player-facing text is readable at standard resolution. No feature requires color discrimination alone. Volume controls exist for music, SFX, and voice independently. The game is completable without photosensitivity risk. | Low — primarily design constraints |
| **Standard** | All of Basic, plus: full input remapping on all platforms, subtitle support with speaker identification, adjustable text size, at least one colorblind mode, and no timed input that cannot be extended or toggled. | Medium — requires dedicated implementation work |
| **Comprehensive** | All of Standard, plus: screen reader support for menus, mono audio option, difficulty assist modes, HUD element repositioning, reduced motion mode, and visual indicators for all gameplay-critical audio. | High — requires platform API integration and significant UI architecture |
| **Exemplary** | All of Comprehensive, plus: full subtitle customization (font, size, color, background, position), high contrast mode, cognitive load assist tools, tactile/haptic alternatives for all audio-only cues, and external third-party accessibility audit. | Very High — requires dedicated accessibility budget and specialist consultation |

### This Project's Commitment

**Target Tier**: Standard

**Rationale**: Tiny Rift Survivors is a real-time survivor-like with auto-attacks,
aimed burst skills, and dodge-based movement. The game's fast-twitch combat
creates motor barriers (rapid movement, aim precision, simultaneous inputs) and
visual barriers (tracking many entities in a dense pixel-art field, reading HUD
elements under combat pressure). WCAG 2.1 Level AA (Standard tier) addresses all
of these: input remapping for motor accessibility, colorblind modes for the
elemental color-coding system, adequate contrast for pixel art on varied
backgrounds, and pause-anywhere for cognitive load management. Comprehensive
tier features (screen reader, HUD repositioning, mono audio) would require
significant Unity UI Toolkit / UGUI architecture work beyond the project's
Pre-Production scope and budget. Dropping to Basic would exclude the estimated
8-12% of the target audience who rely on input remapping or colorblind modes.
Standard tier is achievable with the team's existing Unity skills and the
template's Input System wrapper infrastructure.

**Features explicitly in scope (beyond tier baseline)**:
- Reduced motion mode — elevated from Comprehensive because hit-stop, screen
  shake, and flash-heavy VFX are core combat feedback that can trigger motion
  sickness. Implemented from Day 1 as a toggle in Settings > Accessibility.
- Pause anywhere — Basic tier feature but critical for a fast-paced survivor-like.
  Pause must be instant (≤1 frame) during combat with no animation delay.

**Features explicitly out of scope**:
- Screen reader for in-game world — requires Unity UI toolkit accessibility
  tree integration beyond current scope. All menu screens will be navigable via
  keyboard/gamepad (Standard tier). Documented in Known Intentional Limitations.
- Mono audio mode — Comprehensive tier. Not planned for Steam v1.0. Deferred to
  post-launch if community requests it.

---

## Visual Accessibility

> **Why this section comes first**: Visual impairments affect the largest
> proportion of players who use accessibility features. Color vision deficiency
> alone affects approximately 8% of men and 0.5% of women. Text legibility at
> TV viewing distance is frequently the single largest accessibility failure
> in shipped games. Document every visual feature before implementation begins,
> because retrofitting minimum text sizes or color decisions after assets are
> locked is expensive.

| Feature | Target Tier | Scope | Status | Implementation Notes |
|---------|-------------|-------|--------|---------------------|
| Minimum text size — menu UI | Standard | All menu screens | Not Started | 16px minimum at 1080p for body text. 24px minimum for headings. Pixel art upscaled — verify at 1280x720 internal res. |
| Minimum text size — HUD | Standard | In-game HUD | Not Started | 11px minimum for critical info (HP, XP, timer). Lore toast at 11px borderline — increase to 12px if readability issues surface in testing. Damage numbers scale independently (configurable). |
| Text contrast — UI text on backgrounds | Standard | All UI text | Not Started | Minimum 4.5:1 ratio for body text (WCAG AA). White (#FFFFFF) on dark semi-transparent bg targets ~7:1. Test with automated contrast checker on final color values. |
| Text contrast — subtitles | Standard | Subtitle display | Not Started | Minimum 7:1 ratio (WCAG AAA) for subtitles — use opaque background box by default. |
| Colorblind mode — Protanopia | Standard | All color-coded gameplay | Not Started | Red-green — affects ~6% of men. Shift red signals to orange/yellow. Primary concern: elemental affinity colors (fire=red→orange, blood=dark red→crimson), enemy health bar states, burst skill targeting indicators. |
| Colorblind mode — Deuteranopia | Standard | All color-coded gameplay | Not Started | Green-red — affects ~1% of men. Same palette adjustment typically covers both Protanopia and Deuteranopia. Verify with Coblis simulator. |
| Colorblind mode — Tritanopia | Standard | All color-coded gameplay | Not Started | Blue-yellow — rarer (~0.001%). Shift blue UI elements to purple; shift yellow to orange. Primary concern: rift energy blue, lore fragment glow. |
| Color-as-only-indicator audit | Basic | All UI and gameplay | Not Started | List every place color is the SOLE differentiator in the table below. Each must have a non-color backup (icon, shape, pattern, text label) before shipping. |
| UI scaling | Standard | All UI elements | Not Started | Range: 75% to 150%. Default: 100%. Scaling must not break layout — test all screens at min and max. HUD scaling should be independent from menu scaling. |
| High contrast mode | Comprehensive | Menus (minimum); HUD (preferred) | Not Started | Deferred — Comprehensive tier. Replace semi-transparent backgrounds with opaque. All interactive elements outlined. Not planned for v1.0. |
| Brightness/gamma controls | Basic | Global | Not Started | Exposed in graphics settings. Include reference calibration image. Range: -50% to +50% from default. |
| Screen flash / strobe warning | Basic | All cutscenes, VFX | Not Started | (1) Pre-launch warning screen with photosensitivity seizure notice. (2) Audit all flash-heavy VFX against Harding FPA standard. (3) Flash reduction mode that lowers flash amplitude by 80%. |
| Motion/animation reduction mode | Standard | All UI transitions, camera shake, VFX | Not Started | Reduce or eliminate: screen shake, camera bob, motion blur, parallax scrolling in menus, looping background animations. Cannot fully eliminate: player movement animation. Toggle in Settings > Accessibility. |
| Subtitles — on/off | Basic | All voiced content | Not Started | Default: OFF. Prominently offered at first launch. |
| Subtitles — speaker identification | Standard | All voiced content | Not Started | Speaker name displayed before dialogue line. Color-coded by speaker IF colors differ by more than hue alone (test for colorblind compatibility). |
| Subtitles — style customization | Comprehensive | Subtitle display | Not Started | Deferred — Comprehensive tier. Provide two preset subtitle styles (default and high-readability) as a partial mitigation. |
| Subtitles — sound effect captions | Comprehensive | Gameplay-critical SFX | Not Started | Deferred — Comprehensive tier. See Auditory Accessibility section for which SFX qualify. |
| Damage numbers | Standard | In-combat feedback | Not Started | Cannot be disabled entirely (core tactical info — element type, crit status, damage tier). Size and duration configurable in Settings > Accessibility > "Damage text size" (Normal / Large). |
| Low-health vignette | Standard | Screen feedback | Not Started | Optional toggle in Settings > Accessibility > "Damage vignette". Default: on. |
| Alert banners and level-up effects | Standard | HUD notifications | Not Started | Use scale-up + fade, not hard flashes. Respect reduced-motion setting. |

### Color-as-Only-Indicator Audit

> Fill in every gameplay or UI element where color is currently the sole
> differentiator. Resolve each before shipping. A resolved entry has a non-color
> backup that works in all three colorblind modes above.

| Location | Color Signal | What It Communicates | Non-Color Backup | Status |
|----------|-------------|---------------------|-----------------|--------|
| Elemental affinity (fire/ice/lightning/blood/rift) | Element color (red/blue/yellow/dark red/purple) | Skill element type, damage type, VFX color | Element icon (flame/snowflake/bolt/drop/crystal) displayed next to skill name and damage numbers | Not Started |
| Health bar fill | Red = low health, green = safe | Player near-death status | Bar also shows numeric value; low-health vignette pulses; heartbeat audio cue | Not Started |
| Enemy health bar | Color gradient green→yellow→red | Remaining HP percentage | Bar length also communicates; numeric percentage on boss bars | Not Started |
| Item/currency rarity | Border color (grey/blue/purple/gold) | Quality tier | Rarity name shown on hover/focus; icon border pattern (solid/serrated/gem-cut/radiant) | Not Started |
| Zone restoration state | Color shift (desaturated→full color) | Zone progress (locked→unlocked→restored) | Icon shape (lock/x/star); brightness level changes (3 levels) | Not Started |
| Rune draft card rarity | Card border glow color | Rune quality tier | Card border pattern (none/runes/glowing runes/particle border); text label below card | Not Started |
| Damage numbers | Color (white/red/gold/crit color) | Damage type (normal/critical/elemental/synergy) | Damage number prefix icon (—/★/element icon/synergy icon) | Not Started |
| Minimap entities | Dot color (red=enemy, green=player, blue=ally/neutral) | Entity type on minimap | Shape (triangle=player, square=enemy, circle=neutral) + pulsing ring for threats | Not Started |

---

## Motor Accessibility

> **Why motor accessibility matters for games**: Games are more motor-demanding
> than most software. A web form requires precise clicks; a game may require
> rapid simultaneous button combinations held for specific durations. Motor
> impairments span a wide range — from tremor (affecting precision) to
> hemiplegia (one functional hand) to RSI (affecting hold duration). The AbleGamers
> Able Assistance program estimates 35 million gamers in the US have a disability
> affecting their ability to play. Many of the features below cost very little
> to implement if planned from the start, and are extremely expensive to add post-launch.

| Feature | Target Tier | Scope | Status | Implementation Notes |
|---------|-------------|-------|--------|---------------------|
| Full input remapping | Standard | All gameplay inputs, all platforms | Not Started | Every input bound by default must be rebindable via IInputRouter. Remapping applies to keyboard, mouse, and controller independently. Persist to player profile. |
| Input method switching | Standard | PC | Not Started | Player must be able to switch between keyboard/mouse and gamepad at any moment without restarting. UI must update prompts dynamically (show correct button icons for active input method). |
| One-hand mode | Comprehensive | Combat inputs | Not Started | Deferred — Comprehensive tier. Survivor-like genre is inherently one-hand-friendly (movement + auto-attack). Burst skill activation (shoulder button) and dodge (trigger) may need L1/R1 reassignability via remapping. |
| Hold-to-press alternatives | Standard | All hold inputs | Not Started | Every "hold [button] to [action]" must offer a toggle alternative. List of hold inputs: dodge (hold to run?), interact (hold to pick up lore), confirm/dismiss. |
| Rapid input alternatives | Standard | Any button mashing / rapid input sequences | Not Started | Survivor-like genre has minimal button mashing. Burst skill cooldowns prevent spamming. If any rapid-escape mechanic is added (e.g., stun break), it must support toggle. |
| Input timing adjustments | Standard | QTEs, timed button presses | Not Started | No QTEs planned for MVP. If added in future content, provide timing window multiplier (0.5x to 3.0x). |
| Aim assist | Standard | Burst skill targeting | Not Started | Aim assist for burst skills: snap-to-nearest-enemy within angle threshold. Strength slider (0–100%) in Settings > Accessibility. Assist radius configurable. |
| Auto-sprint / movement assists | Standard | Movement systems | Not Started | Survivor-like movement is primarily WASD/stick with auto-attack always active. No sprint mechanic. If dodge-cooldown-based movement, provide toggle for "hold to dodge" → "press to dodge". |
| Platforming / traversal assists | Basic | None | N/A | No platforming mechanics. Player moves freely on 2D plane. N/A. |
| HUD element repositioning | Comprehensive | All HUD elements | Not Started | Deferred — Comprehensive tier. Not planned for v1.0. |

---

## Cognitive Accessibility

> **Why cognitive accessibility is often under-specced**: Cognitive accessibility
> affects players with ADHD, dyslexia, autism spectrum conditions, acquired brain
> injuries, and anxiety disorders — a larger combined population than many studios
> realize. It also benefits all players in high-stress moments. The most common
> failures are: no pause anywhere, tutorial information that can only be seen once,
> and systems that require tracking too many simultaneous states.

| Feature | Target Tier | Scope | Status | Implementation Notes |
|---------|-------------|-------|--------|---------------------|
| Difficulty options | Standard | All gameplay difficulty parameters | Not Started | Survivor-like genre has natural difficulty scaling (wave escalation). Provide granular sliders: damage dealt multiplier (0.5x–2.0x), damage received multiplier (0.5x–2.0x), enemy speed multiplier (0.5x–1.5x), wave delay multiplier. |
| Pause anywhere | Basic | All gameplay states | Not Started | Pause must be available during combat, boss encounters, and wave transitions. Zero-delay instant pause from InRun (≤1 frame). Pause during cutscenes and dialogue also supported. |
| Tutorial persistence | Standard | All tutorials and help text | Not Started | Tutorial prompts dismissable. Retrievable from Help section in pause menu. Do not rely on first-encounter absorption. |
| Quest / objective clarity | Standard | Wave and boss objectives | Not Started | Current wave number and type always visible on HUD. Boss phase indicators shown. Zone objective: "Survive X waves" always displayed. No inference required. |
| Visual indicators for audio-only information | Standard | All SFX that carry gameplay information | Not Started | See Gameplay-Critical SFX Audit below. Primary concern: off-screen enemy audio cues need visual direction indicator. Boss phase-change audio needs HUD banner. |
| Reading time for UI | Standard | All auto-dismissing dialogs | Not Started | No auto-dismissing dialogs containing actionable information. Lore toasts and zone intro banners dismiss on player action or after 5s minimum. |
| Cognitive load documentation | Comprehensive | Per game system | Not Started | Deferred — Comprehensive tier. Survivor-like inherently tracks many things: position, enemies, cooldowns, HP, wave progress. The minimal HUD philosophy (HUD UX spec) mitigates this by showing only critical info always-visible. |
| Navigation assists | Standard | World navigation | Not Started | Survivor-like arena is single screen — no world navigation. Enemy direction indicators (screen edge arrows) serve as navigation assist for threat awareness. |

---

## Auditory Accessibility

> **Why auditory accessibility matters even for players without hearing loss**:
> 7% of players are deaf or hard of hearing. Additionally, a large portion of
> players regularly play in environments where audio is reduced or absent (commute,
> shared household, infant sleeping). Any gameplay-critical information delivered
> only through audio is a design failure even before accessibility is considered.

| Feature | Target Tier | Scope | Status | Implementation Notes |
|---------|-------------|-------|--------|---------------------|
| Subtitles for all spoken dialogue | Basic | All voiced content | Not Started | 100% coverage — no exceptions. Includes lore fragment narration, zone intro voice-over (if any), tutorial voice. |
| Closed captions for gameplay-critical SFX | Comprehensive | Identified SFX list (below) | Not Started | Deferred — Comprehensive tier. Not planned for v1.0. |
| Mono audio option | Comprehensive | Global audio output | Not Started | Deferred — Comprehensive tier. |
| Independent volume controls | Basic | Music / SFX / Voice / UI audio buses | Not Started | Four independent sliders minimum. Persist to player profile. Range: 0–100%, default 80%. Exposed in both main settings and pause menu settings. |
| Visual representations for directional audio | Comprehensive | All off-screen threats | Not Started | Deferred — Comprehensive tier. Screen-edge indicators for off-screen enemies. Opacity scales with proximity. |
| Hearing aid compatibility mode | Standard | High-frequency audio cues | Not Started | Audit all audio cues for frequency range. Any cue that communicates critical information only through high-frequency sound (above 4kHz) must have a low-frequency or visual equivalent. |
| Audio cues in HUD notifications | Standard | Wave start, boss engagement, damage taken, lore collected | Not Started | All contextual events have paired audio cues. HUD is not the sole channel for critical information — audio and visual both used. |

### Gameplay-Critical SFX Audit

> Identify every sound effect that communicates state the player needs to act on.
> Each entry in this table requires either a confirmed visual backup or a caption.

| Sound Effect | What It Communicates | Visual Backup | Caption Required | Status |
|-------------|---------------------|--------------|-----------------|--------|
| Enemy attack windup | Incoming damage — player should dodge | Enemy animation telegraph visible from all angles (glow/windup VFX) | No — visual is sufficient | Not Started |
| Boss phase transition | Boss is changing attack pattern | HUD banner: "Phase 2" + boss visual transformation | No — visual is sufficient | Not Started |
| Player hit sound | Damage taken | Health bar decreases, damage number appears, screen shake | No — visual is sufficient | Not Started |
| Low health heartbeat | Player health critical | Health bar shows critical state, vignette pulses, health bar flashes | No — visual is sufficient | Not Started |
| Level-up chime | Level gained — draft available | Level-up VFX on player, HUD shows "+1 Level", draft prompt appears | No — visual is sufficient | Not Started |
| Rune draft card sounds | Card selection feedback | Card animates on selection, highlight changes | No — visual is sufficient | Not Started |
| Wave start horn | New wave incoming | HUD banner: "Wave X/Y" with zone name, enemy spawn VFX | No — visual is sufficient | Not Started |
| Currency pickup | Gold/shards earned | Floating text "+X Gold", currency counter animates | No — visual is sufficient | Not Started |
| Off-screen enemy proximity sound | Enemy approaching from off-screen | Screen-edge enemy indicator arrow | Yes — pending Comprehensive tier | Not Started |

---

## Platform API Integration

> **Why this section exists**: Each platform provides native accessibility APIs
> that, when used, allow OS-level features (system screen readers, display
> accommodations, motor accessibility services) to work with your game.

| Platform | API / Standard | Features Planned | Status | Notes |
|----------|---------------|-----------------|--------|-------|
| Steam (PC) | Steam Input / SDL | Controller input remapping via Steam Input; subtitle support | Not Started | Steam Input allows system-level remapping independent of in-game remapping. In-game remapping still required for keyboard/mouse. |
| PC (Screen Reader) | Windows Narrator / NVDA | Menu navigation announcements (Unity UI accessibility tree) | Not Started | Requires UI elements to expose accessible names. Unity UGUI has accessibility support via UIAccessibility namespace. Verify UI Toolkit accessibility tree support in Unity 6000.3. |
| iOS | UIAccessibility / VoiceOver | N/A — mobile deferred | N/A | Review when mobile port begins. |
| Android | AccessibilityService / TalkBack | N/A — mobile deferred | N/A | Review when mobile port begins. |

---

## Per-Feature Accessibility Matrix

> **Why this matrix exists**: Accessibility is not a list of settings — it is a
> property of every game system. This matrix creates the "accessibility impact"
> view of the game.

| System | Visual Concerns | Motor Concerns | Cognitive Concerns | Auditory Concerns | Addressed | Notes |
|--------|----------------|---------------|-------------------|------------------|-----------|-------|
| Input System | None | Full remapping required; hold-to-press alternatives | None | None | Partial | Remapping mapped to Standard tier; one-hand mode deferred |
| Game State Manager | None | None | Pause-anywhere required (pause during all gameplay states) | None | Not Started | Already designed — verify GState allows pause in all states |
| Time System | None | None | None | None | N/A | Pure data — no accessibility concerns |
| Event Bus | None | None | None | Audio cues for events paired with visual equivalents | N/A | Design requirement: event creators must provide both audio + visual |
| Skill Data System | None | None | None | None | N/A | Data-only — no accessibility concerns |
| Hit Detection | None | Aim assist for burst skills | None | None | Not Started | Aim assist in scope for Standard tier |
| Object Pooling | None | None | None | None | N/A | Infrastructure — no accessibility concerns |
| Scene Manager | None | None | Loading screen duration — show progress indicator | None | Not Started |
| Save/Profile Persistence | None | Settings persistence (accessibility prefs saved per profile) | None | None | Not Started | Accessibility settings must persist across sessions |
| Currency System | Currency icon + number — colorblind safe | None | Currency spending confirmation | Pickup audio + floating text | Partial | No color-only dependency |
| Status Effect System | Element icon + color for status type | None | Track active statuses — show on HUD with duration | Status application sound | Not Started | Element icon provides non-color backup |
| Damage & Health System | Health bar color + numeric value; damage number element icons | Invincibility frames eliminate precision timing after hit | Health awareness always visible on HUD | Hit sound, low-health heartbeat, death sound | Not Started | Colorblind mode for health bar gradient; damage numbers always show element icon |
| Orbit Combat System | Orbit icon + cooldown sweep visible | Auto-attack — no motor load | Track orbit skill cooldowns | Orbit activation sound | Not Started | Auto-attack is inherently accessible (no input required) |
| Burst Skill System | Aim reticle + cooldown indicator | Aim assist; rapid-input alternative for combo skills | Track cooldowns per skill | Burst activation sound | Not Started | Aim assist in Standard tier |
| Level-Up System | XP bar fill + numeric level | No motor load | Draft decision time — no timer pressure | Level-up chime + VFX | Not Started | No timed choices |
| Rune Draft System | Card visual (icon + name + rarity) | Navigate 3 cards + select | Compare 3 choices — no time pressure | Card selection sounds | Not Started | Rarity shown via text + border pattern + glow, not color alone |
| Enemy AI | Enemy visual telegraphs for attacks | Dodge timing — generous i-frames | Track multiple enemy patterns | Attack windup sounds | Partial | Telegraphs always visible; i-frames are generous |
| Wave Spawning System | Wave counter on HUD | None | Wave progression always visible | Wave start horn + banner | Not Started |
| Boss Encounter System | Boss HP bar + phase indicator | Dodge boss telegraphed attacks | Track phase changes (max 3 phases) | Phase transition audio + HUD banner | Not Started |
| Screen Shake & Feedback | Shake + vignette + glow | None | None | Hit sound, critical warning | Not Started | Shake toggle required; vibration toggle for controller haptics |
| HUD | Element icons + color; text contrast | HUD is static — repositions in Comprehensive tier | 9 must-show + 8 contextual — notification priority queue | Damage, level-up, wave sounds | Partial | HUD UX spec defined; visual budget keeps cognitive load manageable |
| Camp Menu UI | Text + button contrast; keyboard/gamepad nav | Navigate tabs + lists with D-pad | Upgrade tree, codex navigation | Menu navigation sounds | Not Started |
| Pause Menu | Text + button contrast; all platforms | Keyboard Tab/Arrow, gamepad D-pad, touch tap | No timed interactions; instant pause | Pause/resume sounds | Not Started | UX spec AC covers all platforms |
| Lore Fragment System | Fragment icon + text display | None | Reading view — optional rune→text toggle | Fragment pickup sound | Not Started |
| Audio System | Volume sliders (4 buses) | None | None | Subtitles for all voiced content | Not Started | 4 independent volume sliders in Standard tier |

---

## Accessibility Test Plan

> **Why testing accessibility separately from QA**: Standard QA tests whether
> features work. Accessibility testing tests whether features work for players
> who use them. These are different tests.

| Feature | Test Method | Test Cases | Pass Criteria | Responsible | Status |
|---------|------------|------------|--------------|-------------|--------|
| Text contrast ratios | Automated — contrast analyzer on all UI screenshots | All text/background combinations at all game states | All body text ≥ 4.5:1; all large text ≥ 3:1 | ux-designer | Not Started |
| Colorblind modes | Manual — Coblis simulator on all game screenshots with modes enabled | Gameplay in combat, camp, menus in each mode (Protanopia/Deuteranopia/Tritanopia) | No essential information is lost in any mode; player can complete all objectives without color discrimination | ux-designer | Not Started |
| Color-as-only-indicator audit | Manual — walk each entry in the audit table and verify non-color backup exists | Every row in the Color-as-Only-Indicator Audit table | Each row has a working non-color backup confirmed by visual inspection | ux-designer | Not Started |
| Input remapping | Manual — remap all inputs, complete tutorial and first wave | All default inputs rebound; gameplay functions correctly; conflict prevention works | All actions accessible after remapping; conflict prevention works; bindings persist across restart | qa-tester | Not Started |
| Input method switching | Manual — swap KBM↔gamepad during gameplay | Press key, then press gamepad button; verify UI prompts update | No input loss; prompts update within 1 frame of input method switch | qa-tester | Not Started |
| Hold input toggles | Manual — enable all toggle alternatives, complete combat | All hold inputs in toggle mode | All hold actions completable in toggle mode | qa-tester | Not Started |
| Reduced motion mode | Manual — enable mode, navigate all menus and combat | All menu transitions; all HUD animations; all camera shake; all VFX flashes | No screen shake, no camera bob, no parallax scrolling, all VFX reduced to non-flashing variants | ux-designer | Not Started |
| Pause anywhere | Manual — pause during every gameplay state | Combat, boss fight, wave transition, cutscene, dialogue, camp | Pause opens in ≤1 frame in all states; no state where pause is blocked without design justification | qa-tester | Not Started |
| Keyboard navigation (all menus) | Manual — Tab/Arrow through every menu screen | Main menu, hero camp, pause menu, settings, draft panel, codex | All interactive elements reachable via keyboard; focus indicator visible; no keyboard traps | qa-tester | Not Started |
| Gamepad navigation (all menus) | Manual — D-pad through every menu screen | Same menu screens | All interactive elements reachable via D-pad; A to confirm; B to back | qa-tester | Not Started |
| Volume sliders | Manual — adjust each slider independently | Music 0%, SFX 100%; Music 100%, SFX 0%; all at 0% | Each bus responds independently; no crackling or audio artifacts at extreme values | qa-tester | Not Started |
| Screen flash / strobe audit | Manual — play through all VFX-heavy content | All VFX events, boss phase transitions, screen shake profiles | No event exceeds Harding FPA standard; flash reduction mode reduces amplitude by 80% | ux-designer | Not Started |
| User testing — colorblind | User testing with colorblind participants | Full game session with each colorblind mode | Participants complete all content without requesting color clarification | producer | Not Started |
| User testing — motor impairment | User testing with participants using one hand or adaptive controllers | Full game session with toggle and remapping modes | Participants complete all MVP content without assistance | producer | Not Started |

---

## Known Intentional Limitations

> **Why document what is NOT included**: Omissions left undocumented become
> surprises at certification or in community feedback. Documenting a limitation
> with a rationale demonstrates that it was a deliberate choice, not an oversight.

| Feature | Tier Required | Why Not Included | Risk / Impact | Mitigation |
|---------|--------------|-----------------|--------------|------------|
| Screen reader support for menus | Comprehensive | Unity UGUI/UI Toolkit accessibility tree integration requires dedicated UI architecture work beyond current scope | Affects blind players who rely on screen readers for menu navigation | All menus are fully navigable via keyboard and gamepad — no mouse precision required. Screen reader can be added post-launch when UI Toolkit accessibility support matures in Unity 6000. |
| Mono audio option | Comprehensive | Requires audio bus architecture change to fold stereo/spatial to mono correctly | Affects players with single-sided deafness who miss directional audio cues | All gameplay-critical audio has visual backup. HUD notifies of off-screen threats via screen-edge indicators (Comprehensive tier). Headphone/Speaker mode toggle may partially compensate. |
| HUD element repositioning | Comprehensive | HUD layout is tightly coupled to the pixel art composition and screen-safe-zone constraints | Affects players with peripheral field loss who cannot see edges of screen | HUD uses 10-element budget with <15% screen coverage — most elements are center-weighted. |
| Full subtitle customization | Comprehensive | Custom font rendering and subtitle UI configuration pipeline beyond scope | Affects deaf/HoH players with specific legibility needs | Provide two subtitle presets (default + high-readability). High-readability preset uses larger font, higher contrast, opaque background. |
| One-hand mode | Comprehensive | Survivor-like genre inherently low motor load (auto-attack); dedicated one-hand mode would require input remapping architecture changes | Affects hemiplegic players | Full input remapping (Standard tier) effectively enables one-hand play. Player can rebind all actions to one side of controller/keyboard. |

---

## Audit History

| Date | Auditor | Type | Scope | Findings Summary | Status |
|------|---------|------|-------|-----------------|--------|
| 2026-06-01 | ux-designer | Internal review | Pre-Production accessibility requirements document creation | Document created from UX specs across 5 screens. Standard tier committed. 8 open test plan items. | Current |

---

## External Resources

| Resource | URL | Relevance |
|----------|-----|-----------|
| WCAG 2.1 (Web Content Accessibility Guidelines) | https://www.w3.org/TR/WCAG21/ | Foundational accessibility standard — contrast ratios, text sizing, input requirements |
| Game Accessibility Guidelines | https://gameaccessibilityguidelines.com | Comprehensive game-specific checklist organized by category and cost |
| AbleGamers Player Panel | https://ablegamers.org/player-panel/ | User testing service and consulting with disabled gamers |
| Colour Blindness Simulator (Coblis) | https://www.color-blindness.com/coblis-color-blindness-simulator/ | Free tool for simulating colorblind modes on screenshots |
| Accessible Games Database | https://accessible.games | Research and examples of accessible game design decisions |

---

## Open Questions

| Question | Owner | Deadline | Resolution |
|----------|-------|----------|-----------|
| Does Unity 6000.3 UGUI/UI Toolkit support accessibility tree (UIAccessibility) navigation for screen readers on Windows? | ux-designer | Before Production gate | Unresolved — check Unity 6000.3 release notes for accessibility API support |
| Does Steam Input provide keyboard remapping, or only controller remapping? | lead-programmer | Before Production gate | Unresolved — if Steam Input only supports controller, in-game keyboard remapping architecture is required |
| Should the reduced motion toggle affect VFX particle counts or just screen shake and camera bob? | lead-programmer | During Technical Design | Unresolved |
| Are there any auto-dismissing dialogs planned that contain actionable information? | producer | Before Production gate | Unresolved — review all notification types against this requirement |
| Will the dialogue system support timed choice extensions without a full architecture change? | lead-programmer | During Technical Design | Unresolved — no timed dialogue choices currently planned for MVP |
