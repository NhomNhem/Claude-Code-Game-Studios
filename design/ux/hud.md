# HUD Design

> **Status**: In Review
> **Author**: user + ux-designer
> **Last Updated**: 2026-06-01
> **Template**: HUD Design
> **Platform Target**: PC (Keyboard/Mouse, Gamepad), Mobile (Touch)

---

## HUD Philosophy

*Minimal but present.* The player's attention belongs on the combat — dodging enemy
patterns, positioning orbitals, aiming burst skills. The HUD provides the few numbers
that drive tactical decisions (HP, cooldowns, wave progress) and hides everything else
until relevant. Damage numbers, lore toasts, and connection banners appear on demand
and fade. The screen stays readable even at max enemy density.

---

## Information Architecture

### Full Information Inventory

| # | Information | Source System | Category |
|---|-------------|---------------|----------|
| 1 | Player HP (current/max) | Damage & Health (OnHpChanged) | Must Show |
| 2 | XP (current / next level) | Level-Up (OnXpChanged) | Must Show |
| 3 | Level indicator | Level-Up (LevelUpEvent) | Must Show |
| 4 | Gold count | Currency (CurrencyChangedEvent) | Must Show |
| 5 | Memory Shard count | Currency (CurrencyChangedEvent) | Must Show |
| 6 | Orbit skill icons (element + tier border) | Build State + Skill Data | Must Show |
| 7 | Burst skill icons + cooldown radial | Build State + Skill Data + Time | Must Show |
| 8 | Damage numbers (element-colored) | Damage & Health (DamageDealtEvent) | Must Show |
| 9 | Run timer | Time System (RunElapsedTime) | Must Show |
| 10 | Wave counter ("Wave 3/8") | Wave Spawning | Contextual |
| 11 | Boss HP bar | Boss Encounter | Contextual |
| 12 | Alert banners (zone intro, boss warning, level-up) | Various (GameStateChangedEvent) | Contextual |
| 13 | Lore toast ("Fragment recovered") | Lore Fragment (LoreFragmentCollectedEvent) | Contextual |
| 14 | Connection status banner | Network Manager (OnStateChanged) | Contextual |
| 15 | Enemy HP bars (elites/bosses) | Damage & Health | Contextual |
| 16 | Kill/combo counter | (design gap — not in GDD) | Contextual |
| 17 | Low-health warning / damage vignette | Screen Shake & Feedback | Contextual |

### Categorization

| Category | Count | Behavior |
|----------|-------|----------|
| **Must Show** | 9 | Always on screen during InRun. Arranged in peripheral zones (corners/edges) to keep center clear for combat. |
| **Contextual** | 8 | Appear on trigger, auto-dismiss or fade. Remain visible as long as the triggering condition persists (boss HP bar, connection loss). |

No information is On Demand or Hidden — the HUD design is transparent enough that nothing requires a toggle, and no GDD requirement is communicated through world/audio alone at MVP scope.

---

## Layout Zones

Three horizontal bands with a clear combat center — traditional survivor-like arrangement.

```
┌────────────────────────────────────────────────┐
│                     TOP BAR                      │
│  HP/XP          Wave 3/8         Timer          │
│  [████████]                       ★Gold ◆Shards │
│  [██░░░░░░] Lv.5                                 │
├────────────────────────────────────────────────┤
│                                                  │
│                                                  │
│              C O M B A T   A R E A               │
│                                                  │
│          +123         +456  (damage numbers)     │
│                                                  │
│                                                  │
├────────────────────────────────────────────────┤
│  🌀🌀🌀 Orbit skills          🔥❄️ Burst skills │
│  (bottom-left, inline)     (bottom-center, 2 slots)│
└────────────────────────────────────────────────┘
```

**Zone rationale:**
- **Top bar** — peripheral vision zone. HP, XP, currency, timer, wave info are all glanceable without moving eyes from center. Compact single row for 1280px width.
- **Combat area** — center 70% of screen. No persistent HUD elements intrude. Damage numbers are transient and appear at hit location.
- **Bottom bar** — skill zone. Orbits (passive, less frequent attention) on the left, Burst skills (active cooldown management) in center-bottom for easy eye access. 60px tall.

**Safe zones**: All HUD elements are within 10% of screen edge to avoid clipping on 16:9 and 16:10 displays.

---

## Visual Budget

| Metric | Value | Notes |
|--------|-------|-------|
| **Max simultaneous elements** | 10 | 7 Must Show + up to 3 contextual (boss HP, connection banner, one alert/toast) |
| **Typical simultaneous elements** | 7-8 | 7 Must Show + wave counter (dimmed after 3s) |
| **Screen height % (permanent HUD)** | ~10% | Top bar ~5% (32px at 720p), bottom skills ~5% (60px at 720p) |
| **Screen height % (peak, transient)** | ~12% | + boss HP bar (~8px) + alert banner (~20px) |
| **Center play area intrusion** | 0% permanent | Damage numbers are transient, at hit location. No permanent element overlaps center. |
| **Z-order** | Back→Front: world → damage vignette → damage numbers → contextual banners → top/bottom bar | Banners always on top of bars. Vignette is a screen overlay beneath all UI. |

**Readability rule**: At no point should HUD elements cover more than 15% of the screen. If future elements push past this, consolidate or defer to On Demand.

---

## HUD Elements

### 1. Player HP Bar (Must Show)

| Property | Value |
|----------|-------|
| **Zone** | Top bar, flush left |
| **Format** | Horizontal bar (128px wide, 12px tall). Green→yellow→red gradient based on HP %. Text overlay `"HP / MaxHP"` in white, 12px font. |
| **Data source** | `OnHpChanged(int currentHp, int maxHp)` |
| **States** | **Normal** — bar at current percentage, color = green-to-red. **Damaged** — flash red tint on bar, 0.15s. **Low health** (< 25%) — red + slow pulse (0.5s cycle). **Empty** — grey with `DEAD` text. |

### 2. XP Bar + Level Indicator (Must Show)

| Property | Value |
|----------|-------|
| **Zone** | Top bar, below HP bar (same left alignment, 128px wide, 6px tall) |
| **Format** | Thin fill bar coloured by current primary element. Level text `Lv.5` overlaid right of bar. No XP fraction text. |
| **Data source** | `OnXpChanged(int currentXp, int xpToNext)`, `LevelUpEvent` |
| **States** | **Normal** — fill advances. **Full** — brief golden pulse (0.3s) when XP cap reached, awaiting level-up. **Max level** — bar hidden, level text dimmed. |

### 3. Currency (Gold + Memory Shards) (Must Show)

| Property | Value |
|----------|-------|
| **Zone** | Top bar, flush right |
| **Format** | `★ 1250    ◆ 340` — icon + compact number. 12px font. Gold = coin/star icon, Shard = diamond icon. |
| **Data source** | `CurrencyChangedEvent(CurrencyType, int newBalance)` |
| **States** | **Normal** — static. **Zero** — text dimmed to 40% alpha. **Gained** — brief golden flash (0.2s) on the changed currency. |

### 4. Run Timer (Must Show)

| Property | Value |
|----------|-------|
| **Zone** | Top bar, between wave counter and currency (right-of-center) |
| **Format** | `12:34` — `MM:SS` text, monospace, 12px, light grey. |
| **Data source** | `RunElapsedTime(float seconds)` |
| **States** | **Running** — normal ticking. **Paused** (Time.timeScale = 0) — blinking colon. **Stopped** — greyed out post-run. |

### 5. Orbit Skill Icons (Must Show)

| Property | Value |
|----------|-------|
| **Zone** | Bottom bar, far left |
| **Format** | Horizontal row of up to 5 circular icons (28px). Element-coloured border. Tier indicated by star count (0-3 stars in top-right of icon). 4px spacing between icons. |
| **Data source** | `BuildState` (orbital skill list, levels) |
| **States** | **Normal** — full colour icon, element border, tier stars visible. **Empty slot** — 20% alpha ghost outline. |

### 6. Burst Skill Icons + Cooldown (Must Show)

| Property | Value |
|----------|-------|
| **Zone** | Bottom bar, center (slightly upward from orbit row) |
| **Format** | Up to 2 circular icons (36px — larger than orbits). Element-coloured border. Full colour when ready. On cooldown: radial fill overlay (clockwise sweep, 50% alpha grey) + countdown number `3.2s` centred on icon. |
| **Data source** | `BuildState` (burst skills), `CooldownTickEvent` or Time System |
| **States** | **Ready** — full icon, no overlay. **Cooldown** — radial sweep + countdown number. **Empty slot** — ghost outline only. |

### 7. Damage Numbers (Must Show)

| Property | Value |
|----------|-------|
| **Zone** | Transient — spawn at hit point, float upward + outward, fade over 0.8s |
| **Format** | Number text, 14-18px, coloured by element. Critical hits: 1.5x size, bold, brief screen-shake. |
| **Data source** | `DamageDealtEvent(int amount, ElementType element, bool isCritical, Vector3 worldPosition)` |
| **States** | **Normal** — float + fade. **Critical** — larger, brighter, incidental screen shake. **Zero/immune** — `IMMUNE` or `0` in grey. |

### 8. Wave Counter (Contextual)

| Property | Value |
|----------|-------|
| **Zone** | Top bar, center |
| **Format** | Text `Wave 3/8` — 14px, white, slightly larger than other top-bar text. Appears at wave start, fades to 40% alpha after 3s, remains visible but unobtrusive. New wave number pulses in. |
| **Data source** | `WaveStartedEvent(int waveNumber, int totalWaves)` |
| **States** | **Active** — `Wave 3/8` at full opacity, then fades to subtle. **Final wave** — `FINAL WAVE` in gold, stays visible. **Between waves** — dimmed. |

### 9. Boss HP Bar (Contextual)

| Property | Value |
|----------|-------|
| **Zone** | Top bar, below wave counter (center, wider bar — 200px) |
| **Format** | Horizontal bar with boss name `Aspect of Ember` on left, percentage text on right. Bar is wider and taller than player HP bar (8px tall). Enemy-element coloured fill. |
| **Data source** | `BossEncounterEvent(bool engaged, string bossName, int hp, int maxHp)` |
| **States** | **Engaged** — bar appears with slide-in animation. **Damaged** — flash white on hit. **Death** — bar empties, text `DEFEATED`, fades out. **Dormant** — hidden. |

### 10. Alert Banners (Contextual)

| Property | Value |
|----------|-------|
| **Zone** | Top-center, below boss HP bar area |
| **Format** | Centered banner text, 18-22px, auto-dismiss after 2-3s. Category-specific styling: **Zone intro** — element-colored text `Scorched Expanse`, 3s. **Boss warning** — red text `⚠ BOSS INCOMING`, 2s with screen shake. **Level-up** — gold text `LEVEL UP!` with brief particle burst, 1.5s. |
| **Data source** | `GameStateChangedEvent(GameState oldState, GameState newState)`, `LevelUpEvent` |
| **States** | **Entering** — slide-in or scale-up (0.2s). **Displayed** — hold at full opacity. **Exiting** — fade out. |

### 11. Lore Toast (Contextual)

| Property | Value |
|----------|-------|
| **Zone** | Mid-right edge (vertical toast, not intrusive) |
| **Format** | Compact toast: element-coloured icon + short text `Memory Fragment recovered (3/12)`. 11px, 30% alpha background pill. Auto-dismiss after 2s. |
| **Data source** | `LoreFragmentCollectedEvent(int fragmentId, string setName, int collected, int totalInSet)` |
| **States** | **Enter** — slide in from right (0.25s). **Displayed** — hold 2s. **Exit** — fade out. **Complete set** — gold outline + `Set complete!` briefly. |

### 12. Connection Status Banner (Contextual)

| Property | Value |
|----------|-------|
| **Zone** | Top-center, above all other banners |
| **Format** | Thin pill banner, 12px text. **Reconnecting** — yellow `⚠ Reconnecting...`. **Disconnected** — red `⚠ Connection lost — progress will be saved locally`. |
| **Data source** | `NetworkManager.OnStateChanged(ConnectionState)` |
| **States** | **Hidden** — connected. **Warning** — reconnecting (yellow, persistent). **Critical** — disconnected (red, persistent until restored). **Recovered** — `Connected` in green, auto-dismiss 1.5s. |

### 13. Enemy HP Bars — Elite/Boss (Contextual)

| Property | Value |
|----------|-------|
| **Zone** | Above enemy head (world-space) |
| **Format** | Thin bar (48px wide, 4px tall) above elite/boss enemies. Red fill. Only visible when enemy is on screen and has taken damage. |
| **Data source** | `DamageDealtEvent(EnemyId, int currentHp, int maxHp)` |
| **States** | **Untouched** — hidden. **Damaged** — shown above enemy. **Dying** — low HP red pulse. **Death** — bar shrinks away. |

### 14. Kill/Combo Counter (Contextual — Design Gap)

> **Note**: Not specified in any GDD. Included as a hook if desired — remove if scope is too wide for MVP.

| Property | Value |
|----------|-------|
| **Zone** | Right edge, mid-screen |
| **Format** | Compact vertical text: `42 Kills` in small grey text, or combo `x15` in orange when rapid kills occur. Appears after first kill, fades after 5s of no kills. |
| **Data source** | `EnemyKilledEvent(EnemyType)` |
| **States** | **Active** — kill count rises. **Combo** — larger orange text with brief pulse. **Idle** — fade out after delay. |

### 15. Low-Health Warning / Damage Vignette (Contextual)

| Property | Value |
|----------|-------|
| **Zone** | Screen edge (vignette overlay) |
| **Format** | Red-tinted radial vignette at screen edges. Intensity scales with damage taken (not a binary on/off). Soft blend, not hard border. |
| **Data source** | `OnHpChanged(int currentHp, int maxHp)` — intensity = `1 - (currentHp / maxHp)` |
| **States** | **Full HP** — invisible. **Low** — visible at edges. **Critical** (< 25%) — strong vignette with brief hard pulse on new damage. |

---

## Dynamic Behaviors

| State | What happens | Transitions |
|-------|-------------|-------------|
| **In-Run (default)** | All 7 Must Show elements visible. Contextual elements hidden. | — |
| **Wave transition** | Wave counter appears at top-center at full opacity, fades to 40% after 3s. New wave number pulses. | `WaveStartedEvent` → appear → 3s → fade |
| **Combat / taking damage** | Damage numbers float at hit point. Vignette intensity rises with missing HP. HP bar flashes red on each hit. | `DamageDealtEvent` → spawn numbers. `OnHpChanged` → vignette update + bar flash. |
| **Boss engagement** | Boss HP bar slides in below wave counter. Wave counter changes to `FINAL WAVE` (or stays dim). Boss warning banner (`⚠ BOSS INCOMING`) precedes by 2s. | `BossEncounterEvent` → bar enter (0.3s slide). Separate `GameStateChangedEvent` for warning. |
| **Level-up** | Gold banner `LEVEL UP!` at top-center, 1.5s. XP bar pulses golden. | `LevelUpEvent` → banner show → fade. XP bar pulse 0.3s. |
| **Pause** | HUD dims to 30% alpha behind pause overlay. Timer blinks. | `GameStateChangedEvent(InRun → Paused)` |
| **Run end** | Timer stops/stops blinking. All contextuals dismiss immediately. Victory or defeat overlay covers center. | `RunEndedEvent(RunResult)` |
| **Lore collection** | Toast slides in from right edge, holds 2s, fades. | `LoreFragmentCollectedEvent` → toast enter → 2s → fade out (0.5s). |
| **Connection loss** | Banner appears at top-center above all other elements. Persists until recovered. | `NetworkManager.OnStateChanged` → banner appears → persists → recovered → `Connected` flash → dismiss. |

### Notification priority

When multiple contextual notifications fire simultaneously, they are processed in this order. Lower-priority notifications wait until higher-priority ones dismiss, then display if still relevant.

| Priority | Notification | Behavior |
|----------|-------------|----------|
| 1 (highest) | **Connection status** | Appears immediately, persists until resolved. Preempts all others. |
| 2 | **Boss warning** | Appears immediately, 2s hold. Connection banner stays visible above it if active. |
| 3 | **Boss HP bar** | Slides in, persists for boss duration. |
| 4 | **Wave counter** | Appears at wave start, fades to dim. |
| 5 | **Level-up banner** | 1.5s hold, queues if boss warning is active. |
| 6 | **Zone intro** | 3s hold, lowest combat priority. |
| 7 (lowest) | **Lore toast** | 2s hold, queues behind all combat notifications. |

### Opacity rules

| Layer | Normal opacity | Paused opacity |
|-------|---------------|----------------|
| Top bar | 100% | 30% |
| Bottom skills | 100% | 30% |
| Damage numbers | 100% | 0% (hidden) |
| Contextual elements | 100% | 30% |
| Vignette | Variable (0-60%) | 10% |

---

## Platform & Input Variants

| Platform | Layout changes | Interaction |
|----------|---------------|-------------|
| **PC (Keyboard + Mouse)** | Full layout as specified. HUD is display-only — no clickable elements during combat (per P3 — no dead time means no UI navigation during action). All interactions happen via keyboard/gamepad. | KBM controls game actions (movement WASD, burst Q/E, dash Space). HUD is read-only. |
| **PC (Gamepad)** | Identical layout. HUD elements are read-only; no cursor focus required. | Left stick move, face buttons burst, triggers dash. HUD is read-only. |
| **Touch / Mobile** | Layout unchanged — same 1280x720 internal resolution. Safe zones: ensure top-bar avoids notch/cutout areas. If notch interferes, shift top bar down by 8px or move currency/timer to bottom-right. | HUD is read-only. Touch input maps to virtual stick (left side) and skill buttons (right side) — these are separate from HUD elements. |

**Safe zone policy**: All HUD elements sit within 10% of screen edge. On notched devices, top bar is padded down by the safe area inset via `Screen.safeArea`. The bottom skill zone is kept above the home indicator area.

---

## Accessibility

WCAG-AA baseline applied to all HUD elements.

| Requirement | Implementation |
|-------------|---------------|
| **Color not sole differentiator** | Element types have distinct icon shapes + element-specific border patterns in addition to colour. Damage numbers use both colour and position. Status changes use animation (pulse, slide) not just colour. |
| **Contrast ratio ≥ 4.5:1** | All text meets AA against their background. Top-bar text on 30% alpha background uses white text (contrast ~7:1 against dark game world). Banner text uses white on coloured pill. |
| **Minimum font size 11px** | Smallest text = lore toast at 11px, which is ~6pt at 1280px — borderline. If readability testing shows issues, increase to 12px. |
| **Vignette toggle** | Low-health vignette is optional — toggle in Settings > Accessibility > "Damage vignette". Default: on. |
| **Damage numbers** | Numeric feedback cannot be disabled entirely (core tactical info), but size and duration are configurable in Settings > Accessibility > "Damage text size" (Normal / Large). |
| **Flashing / motion reduction** | Alert banners and level-up effects use scale-up + fade, not hard flashes. Screen shake from critical hits is brief (0.15s). If "Reduce motion" OS setting detected, disable shake and use emphasis via glow only. |
| **Audio cues** | All contextual events (wave start, boss engagement, damage taken, lore collected) have paired audio cues. HUD is not the sole channel for critical information. |

---

## Open Questions

1. **Kill/combo counter** — not specified in any GDD. Included as a design gap placeholder. Include in MVP or defer to post-launch?
2. **Touch input layout** — touch virtual controls (left stick zone, right skill buttons) are separate from HUD. These need an input spec, not a HUD spec. Flag for the interaction-patterns doc.
3. **XP fraction text** — per current design, XP bar shows fill + level number only (no "250/1000"). Confirm this is sufficient for MVP or add fractional text.
4. **Damage numbers minimum font size** — 11px (~6pt at 1280px) is small. Acceptable for pixel art aesthetic? Or require 12px minimum.
5. **Lore toast position** — placed mid-right edge. Confirm this doesn't conflict with future HUD elements (e.g., quest tracker, event log).
6. **Enemy HP bars on mobile** — world-space bars above enemies may be very small on mobile screens. Consider always-on HP bar mode for touch? Same applies to PC at higher resolutions.
7. **Vignette intensity curve** — linear (`1 - hpRatio`) or exponential (barely visible until 50%, then ramps sharply)? Linear chosen for predictability — confirm before implementation.
