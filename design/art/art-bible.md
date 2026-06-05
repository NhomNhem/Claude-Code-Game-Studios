# Art Bible: Tiny Rift Survivors

*Created: 2026-05-25*
*Status: In Progress (Sections 1–9 — 9 complete)*

---

## Mood & Atmosphere

**Cross-state rule**: No two states share a lighting direction. The player always knows where they are by feel, even before reading UI.

### 1. Hero Camp — "Warm Hearth, Quiet Memory"
- **Emotion**: Safe haven, nostalgic comfort, quiet hope
- **Lighting**: Perpetual golden-hour warmth, low contrast, soft radial falloff from campfire. Implied time: early evening.
- **Descriptors**: intimate, still, amber-toned, layered-with-shadow, breathing
- **Energy**: Contemplative / restorative
- **Mood carrier**: Campfire embers drift upward carrying tiny light motes — each mote is a recovered memory fragment visible among the ambient particles

### 2. In-Run Combat — "Controlled Chaos in the Void"
- **Emotion**: Urgency, flow-state tension, strategic panic
- **Lighting**: Cool-black base (near-zero ambient), high contrast. Elemental VFX are the only light sources. No implied time of day — this is a non-place.
- **Descriptors**: electric, stark, volatile, dangerous, arctic-cold-with-hot-punches
- **Energy**: Frenetic
- **Mood carrier**: Elemental projectile trails against pure dark — teardrop fire arcs, hexagonal ice shrapnel with refraction glints, zigzag lightning with ghost echo

### 3. Boss Encounter — "The Storm Breaks"
- **Emotion**: Awe under pressure, dread alloyed with resolve
- **Lighting**: Dramatic chiaroscuro. Cool arena base, boss is the light source — warm threat glow shifting to saturated elemental color per phase. Pulsing with boss heartbeat.
- **Descriptors**: monumental, oppressive, thunderous, cinematic, volatile-sacred
- **Energy**: Frenetic with suspended beats (boss telegraphs create micro-pauses of held breath)
- **Mood carrier**: Boss aura pulse waves — at each phase transition, a colored shockwave of the boss's element ripples across the arena floor, briefly illuminating every enemy and projectile in silhouette

### 4. Victory / Zone Complete — "Color Returns to the World"
- **Emotion**: Triumph as revelation, earned warmth, bittersweet completion
- **Lighting**: Sepia-to-color bloom wave sweeps across the scene. Warm sunrise direction (implied dawn). Contrast blooms from flat to rich across 2 seconds.
- **Descriptors**: radiant, swelling, blooming, forgiving, expansive
- **Energy**: Euphoric release (measured, celebratory)
- **Mood carrier**: An ink-in-water color diffusion wave travels across the environment — the zone's true palette floods in from the player's position outward

### 5. Defeat / Death — "A Drift, Not a Crash"
- **Emotion**: Gentle melancholy, reflection, temporary setback
- **Lighting**: Soft desaturation to sepia-grey vignette. Radial darkening from edges inward. Implied dusk — last light leaving.
- **Descriptors**: hushed, fading, drifting, soft-edged, permeable
- **Energy**: Subsiding / contemplative
- **Mood carrier**: The last enemy that defeated the player lingers in full color for 1.5 seconds before it too desaturates — a Consequence Language moment

### 6. Menus / Draft Overlay — "The Strategist's Table"
- **Emotion**: Focused clarity, decisive calm, a protected moment
- **Lighting**: Warm parchment-gold glow behind the draft panel. Arena visible behind at 20% brightness with motion blur. High contrast on UI elements only.
- **Descriptors**: crisp, grounded, intentional, warm-lit, tactile
- **Energy**: Measured / decisive
- **Mood carrier**: Draft board with parchment texture and hand-inked rune icons. Each card glows with its elemental signature (ember-orange fire, glacial cyan ice, sharp amber-yellow lightning). Cards have slight paper-bob idle animation.

---
## Visual Identity Statement

**Visual Rule**: *Nothing is decorative — every pixel communicates either a fragment of memory, a readable combat choice, or a consequence of player action.*

### Supporting Principles

**Principle 1: Narrative Fragments** — Serves Pillar 1 (Rifts Tell Stories)
*Design test*: When a visual element is ambiguous between generic fantasy decoration and a fragment of the fallen world's story, choose the option that reveals a pre-corruption identity or memory. Cracked statues show what they depicted. Enemies hint at what they were before the void. Environments are ruins, not backdrops — every asset has a "before" story embedded in its design.

**Principle 2: Combat Readability First** — Serves Pillar 2 (Emergent Build-Crafting) + Pillar 3 (Snappy 20–30 Minute Sessions)
*Design test*: When visual flair competes with gameplay legibility, choose the option that makes threat zones, element types, cooldown states, and synergy indicators readable at a glance. Element silhouettes (teardrop fire, hexagon ice, zigzag lightning) and their hybrid synergy shapes must be distinguishable from any camera distance. Dark backgrounds exist to make combat VFX pop, not to hide information.

**Principle 3: Consequence Language** — Serves Pillar 4 (World Reactivity)
*Design test*: When designing any persistent visual element, build visible before/after states into the asset's language. Completed zones shift from sepia/charcoal toward saturated memory on both the map and the playable tile. The world visibly heals as the player's understanding grows — every player action must leave a visual mark.

---

## Shape Language

**Cross-shape rule**: No shape is arbitrary — every silhouette serves memory (what an entity was before the void), readability (can the player parse this at combat distance in under 0.5s), or consequence (what state of corruption or restoration is this asset in?).

### 1. Character Silhouette Philosophy — "Readability Through Broken Memory"

| Archetype | Silhouette Rule | Thumbnail Test | What It Communicates |
|-----------|-----------------|----------------|----------------------|
| **Player Hero (Riftwalker)** | Clean geometric arcs — intact circles, unbroken ovals, smooth curves. No jagged edges on the hero silhouette. | At thumbnail size, the hero reads as a complete, intentional shape against any background. | "I am whole. I am the restorer. I remember." — The hero is the only intact thing in a broken world. |
| **Basic Enemy (Void-Spawn)** | Broken circles — incomplete rings, arcs missing 30-60°, jagged inner edges where the circle was torn. Peripheral silhouette is a circle but the center is hollowed or fracturing. | Reads as "roughly round but wrong" — distinct from hero's clean curves at a glance. | "We used to be whole. Something tore us open." — The broken circle communicates loss before the player knows the lore. |
| **Elite Enemy** | Distorted polygons — the shape that was once a clean form (square, hexagon) now stretched, twisted, or asymmetrical. At least one axis that should be straight is bent. | Distinct from hero (curves) and basic enemy (broken circles) by being angular but wrong-angled. | "I was important. I was specific. Now I am twisted." — The non-Euclidean polygon hints at a pre-corruption identity (guardian, scholar, noble). |
| **Boss** | Massive incomplete geometric frame — a dominant silhouette (circle, hexagon, triangle) that is 70-90% complete, with the missing section revealing void energy inside. The missing arc is the boss's weak point or phase-change visual cue. | Largest silhouette on screen; only entity with void energy visible inside its own frame. | "I almost held together. I was the keeper of something. The void took most of me, but not all." — The near-complete shape reads as tragic power. |

**Pillar served**: Pillar 1 (Rifts Tell Stories) — enemy silhouettes encode pre-corruption identity before the player reads the lore. **Visual Identity Principle**: Narrative Fragments — every cracked circle or distorted polygon is a memory of a complete form.

**Pillar served**: Pillar 3 (Snappy 20-30 Minute Sessions) — silhouette archetypes are distinguishable at thumbnail distance, reducing cognitive load during dense combat.

### 2. Environment Geometry — "Angular Ruins Against Curved Void"

**Dominant geometry**: **Broken angular** (environment) against **organic curved** (void).

| Element | Shape Rule | Why |
|---------|-----------|-----|
| Architecture (ruins) | Sharp, fractured polygons — broken columns, shattered rectangular doorframes, cracked tile grids. Clean right angles but always interrupted by a jagged break. | The fallen civilization's architecture was orderly (right angles = intention, design). The void broke it. Angular geometry communicates "this was built, then destroyed." |
| Terrain / Ground | Organic flowing curves with hard geometric edges — the arena floor is a curved organic shape (void terrain) that meets shattered rectangular platforms (memory fragments of floors). | The void is shapeless (curves). Memory is structured (geometry). The tension between them is the game's central conflict visualized. |
| Void backdrop | Smooth organic curves, amoeba-like blobs, flowing tendril shapes with no hard edges. | The void is the absence of form. Hard edges require intention, memory, structure. The void has none. |
| Restored zones | Previously broken angles become clean right angles again. Fractured columns reassemble. Cracks fill with colored light (the zone's memory color). | Restoration reasserts structure. The geometric completeness is the visual reward — the player literally sees the world piece itself back together. |

**Pillar served**: Pillar 4 (World Reactivity) — environmental geometry has clear before/after states visible at zone level. **Visual Identity Principle**: Consequence Language — broken vs. clean angular geometry is the primary environmental state signal.

**Emotional communication**: The player's eye is always drawn to hard edges against the curved void. Hard edges = safe, structured, restored. Curves = void, danger, unreclaimed. This creates an instinctive "stay near the geometry" pull during combat.

### 3. UI Shape Grammar — "The Strategist's Table Vocabulary"

UI does **not** echo the angular-ruin environment. Instead, UI uses a **distinct diegetic language**: the Riftwalker's portable drafting table — parchment, ink, and hand-drawn runes.

| UI Element | Shape Rule | Rationale |
|------------|-----------|-----------|
| **Panel backgrounds** | Soft rounded rectangles with torn-parchment edge variation (subtle irregularity, not a perfect vector roundrect). | Warm, tactile, belonging to the hero (not the world). The rounded softness contrasts with the world's jagged broken angles — the drafting table is the hero's safe space. |
| **Rune cards (draft picks)** | Shield shape — rounded top, pointed bottom, like a medieval tournament shield. Each shield has a curved top arc (intact circle fragment) containing the element's shape icon. | The shield shape communicates "this is your protection" — it frames the choice as a defensive/offensive tool you carry into the void. The intact arc on top visually connects to the hero's clean-geometry silhouette. |
| **Buttons / interactive elements** | Circular with concentric ring indentation — like pressing a rune-stone. Active state: ring glows with element color. Hover: ring rotates slowly. | Circles in the UI belong to the hero (complete, intentional). Circles in the world belong to the void (broken). This creates a shape-ownership language: hero owns the circle, void corrupts the circle. |
| **Health / resource bars** | Horizontal runic inscription — a line of connected rune glyphs that fill left-to-right. Notched segments at critical thresholds. | A scroll being written, not a progress bar. The health bar is a narrative record of the run's history. |
| **Damage numbers** | No standard floating numbers — use inscribed rune-glyph numerals that pulse and fade. | Even damage feedback is in-world. Numbers are arcane runes counting the cost. |
| **Minimap** | Circular parchment disk with ink-stamped zone shapes. Unrestored areas are dashed outlines; restored areas are solid fills. | The minimap is an archaeological survey map — your cartographer's record of what has been reclaimed. |

**Pillar served**: Pillar 1 (Rifts Tell Stories) — every UI element is diegetically the hero's equipment, not a floating abstraction. **Visual Identity Principle**: Narrative Fragments — the parchment/shield/runic vocabulary makes the UI part of the story.

**Emotional communication**: The soft rounded UI against the jagged angular world creates a visual hug — the UI is safe, warm, yours. When you are in menus, you are protected. When you close the UI, you re-enter the broken world.

### 4. Hero Shapes vs. Supporting Shapes — "What Draws the Eye, What Recedes"

**Eye-drawing hierarchy** (highest to lowest visual priority):

| Priority | Entity | Shape Strategy | Why |
|----------|--------|----------------|-----|
| **1 (highest)** | Player Hero | Clean continuous arcs, glowing elemental orbit around the character. Hero is the only entity with a **full, unbroken outline** at all times. | Hero must be findable in any visual chaos. Complete silhouette = focal anchor. |
| **2** | Enemy projectiles / threat zones | High-saturation elemental shapes (teardrop/hex/zigzag) against the dark void. No desaturation. | Combat Readability First — threat shapes must pop before the player processes what the enemy IS. |
| **3** | Boss | Largest silhouette, void-glow from its incomplete frame. Boss is also a light source (per Mood). | Boss silhouette dominates because it's huge + luminous. Player can track boss position peripherally. |
| **4** | Elite enemies | Distorted polygon shape, slightly larger than basic enemies, with a void-aura outline (thin glow). | Elites are noticed by their wrongness — the distorted polygon catches the eye because it violates expectation of the enemy crowd's broken-circle shapes. |
| **5** | Basic enemies | Broken circles, small silhouette, no glow. Group in dense clusters. | Basic enemies recede individually but read as a threatening mass. Their collective silhouette is the threat, not individual shapes. |
| **6 (lowest)** | Environment / terrain | Dark greys and sepia tones, angular shapes that blend with the void edges. | The environment is the stage, not the performer. It exists to be navigated, not stared at. Restored zones gain saturated geometry that rises to priority 3-4. |

**Pillar served**: Pillar 3 (Snappy 20-30 Minute Sessions) — the eye-drawing hierarchy means a player can process a dense screen in under a second and know exactly where the hero is, what the threats are, and where the boss is.

**Visual Identity Principle**: Combat Readability First — the hierarchy exists so that combat information is parsed pre-cognitively.

### 5. Elemental Shape Vocabulary — "Read the Element by Its Silhouette"

Each element gets a **primary shape**, a **motion arc**, and a **synergy hybrid shape**. All shapes must be distinguishable when standing alone or in combination, at any camera distance, in under 0.5 seconds.

| Element | Primary Shape | Motion Arc | Synergy Hybrid | What It Communicates |
|---------|--------------|------------|----------------|---------------------|
| **Fire** | Teardrop — a circle pulling into a point. Wide base, sharp tip. | Parabolic arc (gravity-affected, drops toward target). Leaves fading ember-trail dots. | Fire+Ice = **Shatter-teardrop** — teardrop shape with hexagonal crack lines spreading from tip. | Passion, destruction, consumption. The teardrop shape implies something burning itself out. |
| **Ice** | Hexagon — six-sided prism with interior refraction lines. | Linear (no gravity, laser-straight). Leaves crystalline dust trail that lingers 0.5s. | Ice+Lightning = **Frost-arc** — hexagon with zigzag interior bolt, trailing frozen lightning. | Preservation, structure, stillness. The hexagon is the most stable geometric shape — ice is trying to hold things together. |
| **Lightning** | Zigzag — sharp angular line with 3-5 direction changes, a smaller fork at the terminus. | Instant teleport-step (no visible travel — appears at target point then chains). Ghost echo of the previous position lingers 0.3s. | Lightning+Fire = **Plasma-flare** — zigzag with teardrop nodes at each angle, trailing ember afterimages. | Speed, communication, the last scream of broken technology. The zigzag is electric signal breaking down. |
| **Void (enemy only)** | Incomplete circle — 60-80% of a circle with the missing gap oozing dark energy. | Slow pulsing expansion — the circle grows and contracts like a breathing wound. | N/A — void has no synergy with elements (it is the anti-element). | Absence, consumption, what remains when memory is erased. The incomplete circle is the void's mockery of wholeness. |

**Synergy combination rule**: When two elements combine on a target, the **smaller shape** embeds inside the **larger shape**. The dominant element (the one that was applied first or has higher tier) becomes the outer container. The secondary element becomes the interior pattern. At a glance, the player sees one shape with another shape's pattern inside — reading both elements simultaneously.

**Performance validation**: Each elemental shape occupies a minimum of 12x12 pixels at the game's camera distance. Shape edges use a contrasting 1-pixel outline in the element's complementary color (fire=amber, ice=cyan, lightning=gold) to ensure silhouette separation against the dark void.

**Pillar served**: Pillar 2 (Emergent Build-Crafting) — synergy hybrid shapes provide immediate visual feedback that your build is combining. **Visual Identity Principle**: Combat Readability First — element silhouettes are distinguishable in 0.5s at any distance because shape + motion arc + color form a unique signature per element.

### 6. Corruption vs. Restoration — "The Shape Language of Healing"

This is the game's primary visual state machine applied to every world-facing asset.

| State | Shape Language | Transition Signal |
|-------|---------------|-------------------|
| **Void-Corrupted** | Jagged breaks on all edges. Assets are 60-80% complete — something is visually missing. Missing sections show void energy (dark purple-black, slow-particled) inside the void. Colors desaturated to sepia/charcoal. | When the player enters a zone, void corruption is the default. Nothing to trigger — this is the "before" state. |
| **Partially Restored** | Previously jagged breaks now show glowing fracture lines (the zone's memory color). Asset is still broken but the breakage is **lit from within**. Missing sections now show colored light instead of void energy. | Triggered by lore fragment collection or elite kill. A wave of the zone's memory color ripples across that area's geometry — cracks fill with light over 1.5 seconds. |
| **Fully Restored** | Asset is 95-100% visually complete. The shape is whole. Color is fully saturated. No void energy visible. The asset casts a soft glow of its memory color onto nearby terrain. | Triggered by zone boss defeat. The zone's color saturation wave (from Mood: Victory) washes over everything — the geometry literally reassembles as the wave passes. Cracks seal, missing pieces reappear as translucent light-constructs (not solid — the memory is restored but the physical piece may be gone). |

**Corruption-to-restoration shape timeline** (applied uniformly to all environment assets):

```
Phase 1 (Enter zone):  Broken edges, jagged, void energy in gaps, desaturated
Phase 2 (Lore found):  Crack edges glow with color, void energy recedes, partial saturation
Phase 3 (Boss down):   Shape reassembles, light-construct fills missing pieces, full saturation, soft glow
```

**Transition rule**: No state transition is instant — each takes 1.5-2 seconds and follows a directional wave (from player position outward, or from the asset's base upward). The player watches the world heal.

**Pillar served**: Pillar 4 (World Reactivity) — the shape restoration timeline is the primary visual reward loop. **Visual Identity Principle**: Consequence Language — every player action has a visible shape consequence on the world geometry.

**Emotional communication**: The player learns to read broken shapes as "work to do" and complete shapes as "done." The act of watching a jagged crack fill with colored light and the missing piece reassemble as a ghost-construct is the game's core visual reward — you are literally restoring the world's shape memory.

---

## Color Palette & Material Values

### 1. Primary Palette Per Element

All values below assume sRGB working space and target medium-brightness monitors (~120 cd/m²). No color is purely decorative — each carries gameplay meaning.

| Element | Hue Range | Saturation Floor | Value Range | Purpose |
|---------|-----------|-----------------|-------------|---------|
| Fire (warm) | 0°–30° | 85% | 60–100% | Damage, aggression, danger approaching |
| Ice (cool) | 190°–220° | 80% | 50–95% | Control, slowing, defensive perimeter |
| Lightning (neutral-warm) | 40°–55° | 75% | 70–100% | Speed, precision, burst timing |
| Void (enemy) | 260°–300° | 20% max | 10–35% | Corruption, enemy presence, threat |
| Memory/restored | 30°–50° | 60–80% | 50–85% | Healing, progress, safe ground |
| Hero Camp | 25°–45° | 30–50% | 40–70% | Safety, rest, preparation — warmer and softer than combat zones |

**Colorblind reinforcement**: Each element's shape vocabulary (teardrop/hexagon/zigzag/incomplete circle) is the primary discriminator. Color occupies a secondary, reinforcing role. Fire always sits in the red-orange band, ice in blue-cyan, lightning in gold-yellow, void in deep purple — these occupy distinct hue regions even for most common color vision deficiencies.

**Hero Camp palette** deliberately shifts from the combat palette: amber and sepia dominate, saturation is capped at 50%, and contrast ratio between adjacent elements never exceeds 3:1. This creates a rest-state for the player's eye between combat encounters.

### 2. Saturation Hierarchy

Saturation is the primary cue for **importance-to-gameplay**. Higher saturation = higher mechanical significance.

| Layer | Saturation | Applies To |
|-------|-----------|------------|
| Elemental VFX | 100% | Projectiles, explosions, elemental trails — the only fully saturated pixels on screen |
| Boss aura | 90–100% | Boss elemental glow — signals active threat, also functions as arena lighting |
| Hero outline / aura | 70% | Player character rim light — always visible against any background |
| Restored zones | 60–80% | Cleared ground, repaired memory fragments — saturates as zone heals |
| Active enemies | 50–70% | Enemy sprites — enough saturation to read element type, not enough to distract from VFX |
| Void-corrupted terrain | 10–20% | Unrestored ground, corrupted walls — reads as "dead" or "sick" |
| Backdrop void | 0–5% | Far background — purely atmospheric, no gameplay information |

**Exception**: Boss fight arenas may invert this hierarchy — the boss aura becomes the dominant saturated element and the player's VFX reads against it at 80–90% saturation. This inversion signals "this is a special encounter" to the player.

### 3. Value / Lightness Rules

Value (lightness) controls **readability order** — the player's eye always goes to the brightest object first.

| Element | Value Range | Rationale |
|---------|-------------|-----------|
| Base void backdrop | 10–15% | Near black. Defines the "empty" state of the world. |
| Elemental light sources | 80–100% | Projectiles, explosions, impact flashes — maximum luminance for gameplay-critical events |
| Hero character | 60–70% (+ 90% rim) | Mid-bright base with a bright rim light separates hero from dark/void backgrounds |
| Readable dark (enemies) | 25–35% | Enemies are silhouetted against the void — enough value to read shape, not enough to be confused with terrain |
| Ruin stone (terrain) | 35–50% | Light enough to navigate by, dark enough to stay in the background |
| Restored memory objects | 60–80% | Brighter than terrain, dimmer than hero — draws attention but doesn't compete with player |
| UI elements | 70–90% | Always legible, uses parchment warmth to differentiate from gameplay elements |

**Value contrast rule**: No two gameplay-significant elements may share the same value range if they occupy the same screen region. Enemies (25–35%) and void terrain (10–20%) differ by at least 10 percentage points. Hero (60–70%) and restored zones (60–80%) overlap intentionally — this signals "this is yours now."

**Rim light rule**: Every gameplay-important entity (hero, enemies, interactable objects) gets a rim light at +30% value over its base. The rim light color always carries the element's hue. This ensures silhouettes read against both void and terrain backgrounds.

### 4. Material Feel Per Surface Type

| Surface | Albedo | Smoothness | Emission | Specular | Feel |
|---------|--------|-----------|----------|----------|------|
| Ruin stone | 0.25–0.40 | 0.05–0.10 | None | 0.02–0.05 | Rough, matte, porous — absorbs light, no reflection |
| Void surfaces | 0.05–0.12 | 0.70–0.85 | None | 0.40–0.60 | Smooth, semi-liquid, dark-glossy — reflects distant light in small specular flecks |
| Restored memory | 0.40–0.60 | 0.10–0.20 | 0.30–0.50 | 0.05–0.10 | Translucent, emissive, ghost-light — appears to glow from within, subtle pulse |
| Elemental effects | N/A (pure additive) | N/A | 1.0–2.0 | N/A | Pure light, no material surface — rendered as unlit additive particles or decals |
| UI parchment | 0.55–0.70 | 0.15–0.25 | None | 0.10–0.15 | Textured warm-grain, matte-absorbent with faint directional highlight |

**Void material note**: The dark-glossy void surface should show small specular flecks of the nearest elemental light source (e.g., a fire projectile reflected as a tiny orange dot on the void ground). This reinforces spatial awareness and makes the void feel like a physical substance rather than empty space.

**Restored memory emission**: Emission intensity pulses on a 3-second sinusoidal wave (±15% amplitude) to create a "breathing light" effect that distinguishes restored zones from static terrain. Pulse speed increases to 2-second cycles during enemy proximity (warning).

### 5. Contrast Budgeting

Every screen maintains exactly **5 contrast levels**, ordered by visual priority:

| Level | Description | Typical ΔE (approx) | Contains |
|-------|-------------|---------------------|----------|
| 1 (highest) | Elemental VFX vs. void backdrop | >60 | Projectiles, explosions, impact — the brightest, most saturated pixels against the darkest |
| 2 | Hero vs. background | 40–50 | Player character silhouette against void or terrain |
| 3 | Boss vs. arena | 30–40 | Boss shape against the arena floor — only in boss fights |
| 4 | Enemies vs. terrain | 20–30 | Enemy sprites readable against ruin stone or void ground |
| 5 (lowest) | Terrain vs. void | 10–15 | Ruin stone edges against void — enough to navigate, never enough to distract |

**Budgeting rule**: No more than 15% of screen pixels may occupy Level 1 at any time. No more than 30% may occupy Level 2. The remaining ~55%+ must be Levels 3–5. This prevents visual noise and ensures the player can always find the most important information.

**Violation**: Screen shake + boss phase transition may temporarily break these budgets (up to 25% Level 1 for 0.5 seconds max) — this reads as "intensity spike" rather than "broken visual design."

### 6. Dithering & Palette Restriction

**Palette model**: The game uses a **dynamic restricted palette** — 24 colors per zone in void state, expanding to 48 colors when fully restored.

- **Void state (0% restored)**: 24 colors — 4 per element (fire/ice/lightning/void), 4 for hero, 4 for terrain, 4 for UI, 4 for backdrop gradients. This enforces the "broken, limited" feeling of corrupted space.
- **Per memory fragment restored**: +2 colors unlocked (chosen from a zone-specific expansion palette). The palette expands in discrete steps, not smoothly.
- **Fully restored (100%)**: 48 colors — original 24 + 24 expansion colors. The final palette feels rich but never fully photorealistic.

**Dithering style**: Ordered Bayer dithering with a 4×4 pattern matrix. Applied to:
- All gradient transitions in the void backdrop (banding concealment)
- Re-entry transitions when moving between restored and void zones
- Edge blending between terrain and void (never between gameplay entities)

**Noise dithering**: Explicitly not used — ordered dithering preserves the pixel-art aesthetic and reads as "technical/retro" rather than "analog/film."

**Dithering rule**: Dithering is never applied to gameplay-critical elements (hero, enemies, VFX, UI). It is a background and terrain technique only. Applying dithering to a gameplay element would be a bug.

### 7. Colorblind Accessibility

The palette is designed to remain functional across the three most common color vision deficiencies (protanopia, deuteranopia, tritanopia):

1. **Shape as primary discriminator**: Every element type has a unique shape language (fire=teardrop, ice=hexagon, lightning=zigzag, void=incomplete circle) — color is always redundant with shape.
2. **Hue separation**: Fire (0–30°), ice (190–220°), lightning (40–55°), void (260–300°) — these occupy hue regions that remain distinct even when red-green channels collapse.
3. **Luminance separation**: Elemental VFX (80–100% value) vs. enemies (25–35%) vs. void (10–15%) — tritanopia-safe luminance hierarchy.
4. **Saturation as intensity cue**: All elements are consistently high-saturation in VFX state, low-saturation in idle/ambient state — saturation change signals "this element is active."

### 8. Performance Constraints

- All palettes must work on medium-brightness monitors (~120 cd/m²). No reliance on OLED infinite contrast for readability.
- Maximum 48 colors on screen at any time (24 in void zones) — this bound ensures URP pixel-art batch rendering stays efficient.
- Emission values capped at 2.0 to avoid bloom artifacts on mid-range GPUs.
- No more than 3 unique particle systems with additive blending visible simultaneously — enforced by limiting elemental VFX to one dominant element per combat encounter plus hero effects.
- Rim lights are implemented as a single-pass sprite outline shader (not a full-screen post-process) to maintain 60 FPS.

---

## Character & Prop Design Guidelines

### 1. Hero Design Rules — "Intact Silhouettes in a Broken World"

**Canvas & scale**: Heroes are rendered at **48×48 px** on a 64×64 px canvas (allows 8 px padding on all sides for weapon swing, VFX overlap, and shadow). Final in-world rendering is 32–36 px tall (accounting for 4–6 px of cinematic ground-shadow padding below the feet).

**Proportion rules**:
| Measure | Rule | Why |
|---------|------|-----|
| Head-to-body | 1:3 (head = 12 px, body + legs = 36 px) | Readable facial element spot at 1:3; keeps hero distinct from enemies (1:2.5) and environment tiles |
| Limb width | 4–5 px thick (upper arm/thigh), 3–4 px (forearm/shin) | Thick enough to read limb pose at thumbnail; thin enough to avoid chunky teddy-bear proportions |
| Hand size | 3×3 px closed fist, 4×4 px open palm with weapon | Hands are the smallest readable detail — below 3 px they become noise |
| Eye size | 2×2 px iris + 1 px highlight | Single pixel of eye white + 2 px colored iris + 1 px white highlight = readable gaze direction at 48 px |

**Silhouette distinctiveness** — each hero must be identifiable at 24×24 px (thumbnail):
| Hero | Silhouette Key | Thumbnail Identifier | What Cannot Be Changed |
|------|----------------|---------------------|----------------------|
| Fire Archmage | Wide triangular robe base, narrow shoulders, tall pointed hood/cowl. Weapon: staff (tall, top-heavy). | "Tall triangle with a point above" — a candle shape | Cowl height-to-width ratio, staff length ≥ body height |
| Ice Queen | A-line dress/tunic that flares from waist, broad shoulders, crown/tiara spikes. Weapon: orb (held at chest height, spherical). | "Wide at shoulders and hem, narrow waist — an hourglass with a crown" | Crown spike count (3 minimum), hem width ≥ shoulder width |
| Lightning Engineer | Narrow rectangle body, mechanical backpack (square protrusion above shoulders), asymm tool belt. Weapon: gauntlet (arm extended forward, fist). | "A rectangle with a box on its back and one arm extended" — a question-mark profile | Backpack height ≥ head height, extended arm always visible from both left/right |
| Void Scholar | Hooded cloak that drags on ground, hunched shoulder line (one shoulder higher). Weapon: tome (held open in both hands at chest). | "A bell silhouette with irregular top — hunched cloak, book at chest" | Cloak ground-drag (2 px extra width at base), tome opens forward not sideways |

**Base pose**: Standing idle — weight on back foot, front foot slightly forward, torso rotated 3/4 to camera. This is the hero's default narrative pose: ready but not aggressive, a restorer surveying their work.

**Combat stance**: Each hero has a distinct readiness pose that activates when enemies are within aggro range:
- Fire Archmage: staff held diagonally across body, flame already glowing in the crystal
- Ice Queen: orb raised to eye level, off-hand extended palm-forward (warding gesture)
- Lightning Engineer: gauntlet fist at shoulder height, legs bent wider than idle, backpack vents crackle
- Void Scholar: tome open, pages flipping automatically, one hand tracing a rune in the air

**Animation budget per hero**:
| Action | Frames | Directional? | Notes |
|--------|--------|-------------|-------|
| Idle (breathing) | 4 | No (single south-facing) | 2-frame subtle breath cycle + 2-frame ambient elemental flicker on weapon |
| Idle (ambient element) | 3 | No (overlay) | Particle spawn frame, sustain frame, fade frame — loops over base idle |
| Walk | 6 | 4-directional (N/S/E/W) | 3 frames per step, 2 steps per cycle. Diagonal = blended from cardinal |
| Dash | 3 | 4-directional | Wind-up, dash (stretch frame), recovery. The dash frame is a 1.2x horizontal stretch of the combat silhouette |
| Attack (basic) | 5 | 4-directional | Wind-up, strike 1, strike 2, hit-hold, recovery. Frame 3 (hit-hold) has a 2-frame freeze (hit-stop) |
| Skill cast | 8 | 4-directional | Wind-up (3f), channel glow (2f), release (2f), recovery (1f) |
| Hit reaction | 3 | No (face-attacker) | Impact (lean back), stagger (arms fling), recover (return to combat stance) |
| Death | 6 | No | Collapse (kneel - 2f), fall (tilt - 2f), dissolve to light motes (2f — hero never leaves a corpse) |
| Zone restore (emote) | 5 | No | Kneel-touch-ground, glow rises from hand, stand-and-look (unique per hero — see below) |
| Victory cheer | 8 | No | Unique per hero, 8 frames, plays once then returns to idle |

**Zone restore emote** — unique per hero animation that plays when a zone boss is defeated:
- Fire Archmage: plants staff in ground, fire ring expands from staff base outward
- Ice Queen: releases orb which rises above her head, then shatters into healing frost across the zone
- Lightning Engineer: slams gauntlet fist into ground, lightning grid spreads in all directions
- Void Scholar: closes tome, touches the ground with both hands, the book glows and the zone color floods from the contact point

**Elemental signature on model** — how each hero's element manifests on their body (not just VFX):
| Hero | Passive Element Signal | Active Element Signal |
|------|----------------------|----------------------|
| Fire Archmage | Ember-orange glow in the staff crystal. Small ember particles drift from the cowl's edge. | Staff crystal becomes fully lit (100% value). Rune lines on the robing glow orange in sequence from feet to hands. |
| Ice Queen | Orb contains a slow-turning snowflake. Breath is visible as frost (2×2 px overlay). | Orb emits a cold-cyan glow that illuminates her face from below. Frost crust forms on her shoulders and crown edges. |
| Lightning Engineer | Backpack vents emit a faint amber glow. Gauntlet fingers have micro-sparks between them. | Gauntlet arcs electricity to the ground (visible 1-pixel zigzag to feet). Backpack vents flash in rhythm with heart-rate during combat. |
| Void Scholar | Tome pages are edged in dark-purple glow. One eye has a small purple pupil (void corruption visible). | Tome runes lift off the page and orbit the scholar. The scholar's shadow becomes irregular and moves independently. |

**Clothing/armor philosophy**: Heroes wear functional remnants, not fantasy armor. Every garment piece is a memory of what a riftwalker needed to survive:
- All clothing has visible repairs — stitches, patches, replaced straps. These are the hero's history.
- No symmetrical armor — a pauldron on one side suggests that side is the "void-facing" side (the direction they brace against)
- Fabrics have weight in animation — heavy cloak swish, robe drag, leather crease. No floaty capes that ignore gravity.
- Metal is limited to 3 pieces max per hero (weapon tip, one buckle, one pauldron/greave). Most of the hero is cloth, leather, and binding.
- Color palette per hero: 60% base tone (element's secondary hue at 40% sat), 25% accent (element's primary at 70% sat), 10% dark trim (leather/binding at 20% value), 5% emissive (element's 100% sat glow point).

### 2. Enemy Design Rules — "What the Void Left Behind"

**Void-spawn template** — all void enemies share these visual traits:
1. **Broken silhouette**: Every void enemy has at least one edge that is jagged, torn, or incomplete. No smooth outlines.
2. **Void core**: A dark purple-black center (260°–300° hue, 10–15% value, 20% max saturation) visible through a gap in their form. This is the "hole where the soul was."
3. **Rim glow**: Thin (1 px) rim in the enemy's elemental affinity color — this is the "pre-corruption memory" clinging to the edge.
4. **Chitin-like surface**: Dark gloss (smoothness 0.6–0.7) with subtle specular flecks in the element's hue. The void preserved the surface but hollowed the content.
5. **Drift idle**: All void enemies have a 1–2 px floating bob on a 2–3 second sine wave. They do not stand still — they are unsettled, restless, falling.

**Tier differentiation**:
| Tier | Pixel Height | Frame Budget | Silhouette Rule | Death Animation |
|------|-------------|-------------|-----------------|-----------------|
| Basic | 24–28 px | 3–4 frames per action | Broken circle — one type of break (top missing, or left arc gone). Always a single "color" of void. | "Pop" — void core collapses inward, the chitin shell shatters into 3–4 jagged shards that fade after 0.5s. No lingering. |
| Elite | 32–36 px | 5–6 frames per action | Distorted polygon — 2+ types of distortion. Has a distinct pre-corruption accessory (half a helm, a tattered robe fragment, a broken weapon). | "Crack and release" — the chitin cracks along structural lines, memory-colored light bleeds from the cracks (not void energy), then a 0.5s dissolve to motes. Leaves no corpse but leaves a lore fragment drop. |
| Boss | 48–64 px | 8–12 frames per action | Incomplete geometric frame (70–90% complete). Missing section reveals giant void core. Has 3 distinct phase-change visual states. | "Two-stage collapse" — Phase 1 death: the boss frame cracks, memory light floods from the void core, boss staggers. Phase 2: the frame completes itself (the missing arc fills with light), boss dissolves upward into light motes with a zone-color wave. |

**Pre-corruption identity clues** — every enemy hints at what it was before the void:
- A basic void-spawn carrying a broken circle on its chest was once a **commoner** — the circle was a locket, a coin, a simple emblem
- A void-spawn with a partial crown/tiara was once **nobility or governance**
- A void-spawn with broken geometric weapon or armor piece was once a **guardian/soldier**
- A void-spawn with tattered book/page fragments was once a **scholar or scribe**
- A void-spawn with a cracked bell or horn was once a **town crier or messenger**
- A void-spawn with a broken tool (hammer, sickle, spindle) was once an **artisan or laborer**

These clues must be readable at 24 px height — this means exaggerated proportions (the broken crown is 6 px wide on a 24 px sprite, the book fragment is 8×6 px). Subtlety kills readability at this scale.

**Elemental affinity variation**: A void-spawn's element appears as:
1. **Rim glow color**: The 1-px outline shifts from default void-purple to the element's hue at 70% saturation
2. **Core particles**: Small (1–2 px) particles of the element's color drift from the void core gap
3. **Attack VFX**: The enemy's attack projectiles use the element's shape vocabulary (fire=teardrop, ice=hexagon, lightning=zigzag) but at 50% saturation and with void-purple undertones — corrupted elements
4. **Death effect**: On death, the core explosion has a 0.2s flash of the element's color before the void shatters

**Death animation principles** (Consequence Language applied to enemies):
| Tier | Death Sequence | Duration | Player Feedback |
|------|---------------|----------|-----------------|
| Basic | Void core collapses → shell shatters → shards fade | 0.5s | Brief — you killed something small. Moves on. |
| Elite | Crack lines appear (0.3s) → memory light bleeds from cracks (0.3s) → light expands, shell dissolves upward (0.5s) | 1.1s | Satisfying — you freed something significant. Lore fragment confirms it. |
| Boss | Phase 1 collapse (0.5s) → pause (0.3s) → frame completes with light (0.5s) → dissolve upward with zone color wave (0.7s) | 2.0s | Triumphant — you fully restored a keeper of memory. Zone-wide visual reward. |

**Rule**: No enemy leaves a corpse. Basic enemies shatter into shards. Elites and bosses dissolve into light motes (restored memory returning to the world). The void does not leave bodies — it leaves absence.

### 3. Prop & Environmental Object Rules — "Nothing Is Decorative"

**Interactable vs. decorative**: There are no decorative props. Every placed object belongs to one of these categories:

| Category | Example | Player Interaction | Visual Distinctiveness |
|----------|---------|-------------------|------------------------|
| Lore fragment | Cracked tablet, glowing page fragment | Walk-over collect | Soft golden-white glow (2 px), floating bob, 1.2x scale pulse every 2s |
| Zone memory core | Restored statue head, complete glyph stone | Click/approach to activate "zone restore" | Zone-color strong glow (4 px), slow rotation, humming particle stream upward |
| Currency drop | Memory shard (crystallized light) | Walk-over collect | Small (8×8 px), element-colored, ground-hugging (no floating bob), 0.5s fade |
| Health pickup | Restored campfire fragment | Walk-over collect | Warm amber glow, 1 px heart-shaped flame, soft upward particle |
| Skill draft altar | Draft table with rune cards visible | Approach to open UI | Parchment + wooden table shape, warm glow, distinct from all void geometry |
| Trap / hazard zone | Void geyser, corrupted crystal spike | Avoid or destroy | Element-colored danger rim, pulsing (1s cycle), 15% larger than safe variant |
| Breakable obstacle | Cracked wall, void-choked door | Attack to destroy | Visible crack pattern (converging on a strike point), void-seepage from cracks |
| Environmental memory | Phantom figure, ghost-animal | Visual only (ambient) | 40% alpha, desaturated, repeats a 3–4 frame loop of a mundane action (a phantom blacksmith hammering, a ghost-child running) |

**Lore fragment prop design**:
- Size: 16×16 px (large enough to read as an object, small enough to not clutter)
- Shape: Always rectilinear or tablet-like — a tile fragment, a page, a broken tool head
- Palette: 6 colors max — 2 whites (base + highlight), 2 zone-memory colors (base + glow), 1 void-purple remnant (a corner of corruption), 1 gold-white (collect highlight)
- Glow animation: Soft sinusoidal pulse (1.5s period), expands 1 px at peak
- On collect: The fragment releases a zone-color ripple (12×12 px ring expanding outward over 0.5s), then the fragment sprite becomes 40% alpha and desaturates over 1s before fading — the fragment remains visible as a "collected" ghost for 1s as a reward

**Restored object vs. corrupted object variant rules**:
| Aspect | Corrupted | Restored |
|--------|-----------|----------|
| Palette | Sepia/charcoal + void purple (max 8 colors) | Full zone memory palette (12–16 colors) |
| Glow | None (surface is matte-dead) | Soft emission at 0.3–0.5 intensity |
| Completeness | 60–80% visible; missing chunks show void energy | 95–100% visible; missing chunks are light-construct filled |
| Interactability | Destroy/kill/avoid | Inspect/touch/activate |
| Edge quality | Jagged, torn, broken edges | Clean or glowing-fracture edges (crack lines filled with light) |
| Shadow | No shadow (void objects cast nothing) | Soft 2-px drop shadow (reasserted in the world) |

**Collectible / currency item design**:
- **Memory shards** (primary currency): 8×8 px crystallized light polygons (hexagonal or diamond-shaped). Shards match the zone's memory color but desaturated to 50%. On collect, they spiral to the UI shard counter (0.3s travel) and leave a 2-px sparkle trail.
- **Void fragments** (secondary / enemy-drop currency): 6×6 px jagged dark-purple shards with a 1-px rim glow. On collect, they dissolve and a dark pulse travels to the counter.
- **Rift essence** (rare currency): 12×12 px glowing orb with the element's shape inside (a teardrop in amber, a hexagon in cyan, a zigzag in gold). Slow float (2px bob), trailing 1-px elemental particles. On collect, a 0.5s element-colored explosion animation.

### 4. Sizing & Scaling — "Readability at Every Distance"

**Hero dimensions**:
- Canvas: 64×64 px (8 px padding per side for weapon/VFX overlap)
- Sprite render: 48×48 px (feet to top of head)
- In-world height: 32–36 px (accounts for 4–6 px ground shadow + 4 px cinematic padding at top)
- Screen height percentage: **4–6%** of a 1080p screen — hero occupies roughly 35–50 px on a typical 1080p display at default camera distance
- Camera distance: Fixed orthographic size such that the hero is ~40 px tall on a 1080p display. This is the default "combat readability" distance.

**Enemy size relative to hero**:
| Enemy Tier | Relative Height | Absolute Height (px on screen) | Count per Screen |
|------------|----------------|-------------------------------|------------------|
| Basic | 60–80% of hero | 24–32 px | 30–60 (dense swarm) |
| Elite | 90–110% of hero | 36–44 px | 3–8 (mixed with basic) |
| Boss | 130–180% of hero | 52–72 px | 1 at a time |

**Prop pixel budgets**:
| Prop Type | Max Size | Palette Max |
|-----------|----------|-------------|
| Lore fragment | 16×16 px | 6 colors |
| Memory shard (currency) | 8×8 px | 4 colors |
| Void fragment (currency) | 6×6 px | 3 colors |
| Rift essence (rare currency) | 12×12 px | 5 colors + 1 emission |
| Breakable obstacle | 24×32 px | 10 colors |
| Zone memory core | 28×28 px | 8 colors + emission |
| Draft altar (merchant) | 32×40 px | 14 colors + UI parchment |
| Trap/hazard | 20×20 px (base) + 8 px glow | 6 colors + element glow |
| Environmental memory (ghost) | 24×28 px | 6 colors (40% alpha) |

**Screen percentage constraints**:
| Entity | % of Screen Height | Purpose |
|--------|-------------------|---------|
| Hero | 4–6% | Primary focal point, always visible |
| Basic enemies | 2.5–4% | Readable as individuals in swarms |
| Elites | 4.5–5.5% | Larger and distinct from the swarm |
| Boss | 6.5–9% | Dominant screen presence, cannot be missed |
| Projectiles | 1–3% | Minimum 6×6 px to be read at peripheral vision |
| UI (outermost panels) | 5–8% from edge | Always in peripheral, never over gameplay |
| Ground shadow (all entities) | 2–4 px below feet | Grounds the entity in the world |

**Scaling rule**: No dynamic scaling. Camera zooms are discrete (boss zoom = 1.2x, no smooth zoom). This preserves pixel alignment and prevents texture shimmering.

### 5. Animation Principles — "Weight, Memory, and Impact"

**Frame count conventions per action type**:
| Action Class | Frame Count | Description |
|-------------|-------------|-------------|
| Idle loop | 2–4 frames | Subtle movement — breathing, ambient float, micro-shift of weight |
| Ambient element loop | 2–3 frames (overlay on idle) | Weapon element emission flicker, particle spawn-sustain-fade |
| Movement (walk/float) | 6 frames per direction | 3 frames per step, 2 steps per cycle. First frame is reset of cycle. |
| Quick action (dash, dodge) | 3 frames | Wind-up, action, recovery. Dash action frame is a 1.2x stretch. |
| Standard attack | 4–5 frames | Wind-up, contact, hold, recovery. Contact frame held for hit-stop. |
| Heavy/skill attack | 7–8 frames | Extended wind-up (2–3f), channel (1–2f), release (2f), recovery (1f) |
| Hit reaction | 3 frames | Impact, stagger, recover. Always faces attacker on impact. |
| Death (basic enemy) | 3–4 frames | Core collapse, shatter, fade. No recover. |
| Death (elite enemy) | 5–6 frames | Crack, light bleed, dissolve upward, fade. |
| Death (boss) | 8–12 frames | Phase 1 collapse, pause, frame-complete light, dissolve upward. |
| Death (hero) | 6 frames | Kneel, fall, dissolve to light motes. |
| Object interaction | 4–5 frames | Reach, touch, glow response, withdraw. |
| Zone restore emote | 5 frames | Unique per hero — see Section 5.1. |
| Victory cheer | 8 frames | Unique per hero, played once, hero returns to idle. |

**Hit-stop / freeze-frame rules**:
| Event | Hit-Stop Duration | Applies To |
|-------|-------------------|------------|
| Basic attack connects | 2 frames (33ms at 60fps) | Player character only — enemy continues at full speed (player gets micro-pause to confirm hit) |
| Skill/ability connects | 4–6 frames (67–100ms) | Player + the hit enemy both freeze. Nearby enemies continue. Creates a "punch" feel. |
| Enemy hit by player | 2 frames | Enemy freezes. Player does not. Makes the player feel faster than enemies. |
| Player hit by enemy | 0 frames (no hit-stop) | Being hit never pauses the player — loss of control is not fun (per Pillar 3: snappy sessions) |
| Boss phase transition | 12 frames (200ms) | Full screen freeze. Boss is struck by a memory-light beam. All particles pause. Then boss explodes into new phase animation. |
| Enemy death (basic) | 0 frames | No freeze — keep combat flowing |
| Enemy death (elite) | 3 frames | Brief pause on the crack moment — acknowledges the kill without stopping play |
| Enemy death (boss) | 8 frames | Full stop on the frame-complete light moment. All enemies pause. A "breather" reward. |

**Hit-stop visual effect**: During hit-stop frames, the frozen character gets a 1-px overlay of their element's color at 20% opacity + a 0.5-px white "impact flash" at the contact point that fades over the freeze duration. This gives the freeze visual meaning ("something important just happened") rather than looking like a lag spike.

**Idle animation complexity**:
| Entity Type | Idle Complexity | Detail |
|-------------|-----------------|--------|
| Hero (camp) | High — 6–8 frame total (4 base + 4 ambient) | Full breath cycle, weapon element idle, head turning every 5s to survey surroundings |
| Hero (combat) | Medium — 4 frame total (2 base + 2 ambient) | Alert stance, weapon at ready, micro-weight shifts. No head turning (locked on combat) |
| Basic enemy | Low — 2–3 frame total | The "void drift" — 1–2 px sine float, occasional (random every 3–5s) 2-frame twitch. Minimal — these are hollow shells. |
| Elite enemy | Medium — 4–5 frame total | Void drift + pre-corruption accessorized item animation (tattered cape flap, broken weapon sway). More movement = more alive = more threatening. |
| Boss | High — 6–8 frame total | Slow breathing (frame 1–4 inhale, 5–6 hold, 7–8 exhale), particle emission from void core, phase-change color pulse on idle loop. Boss feels alive and dangerous even when not attacking. |
| Lore fragment | Low — 2 frames | Soft float bob + 2-frame glow pulse |
| Environmental memory | Low — 3–4 frame loop | Phantom action loop (hammering, walking, waving). Repeats with 2–4s gap. |

**Transition animations** — corruption ↔ restoration:
| Transition | Direction | Duration | Visual Sequence |
|------------|-----------|----------|-----------------|
| Corruption → Partial Restore | Zone-event triggered | 1.5s | Void energy recedes from cracks (0.5s) → crack edges glow with zone-memory color (0.5s) → light spreads 30% across the asset surface (0.5s). The asset still has its jagged edges but is now "lit from within." |
| Partial → Full Restore | Zone-boss-defeat triggered | 2.0s | Glow intensifies from 0.3 to 0.8 emission (0.5s) → jagged missing chunk fills with light-construct geometry from edges inward (0.8s) → light pulse travels from base to top (0.5s) → steady-state restored glow (0.2s). |
| Restore → Re-corruption | Player-leaves-zone (runtime reset) | 1.0s | Light construct fades (0.3s) → glow dims (0.3s) → void purple seeps in from cracks (0.4s). Asset returns to corrupted state. This transition is a visual "reset" — it should feel like the void reclaiming its territory as you leave. |

**Transition wave rule**: All zone-wide transitions (partial restore, full restore, re-corruption) travel as a wave across the arena, originating from the trigger source (player position for partial, boss death location for full, zone edge for re-corruption). The wave front is 16 px wide and takes 0.5s to traverse the full zone. This gives the player a clear spatial cause-and-effect read.

### 6. Design Constraints — "Working Within the Walls"

**Max palette colors per character**:
| Entity Class | Max Colors | Break-down |
|-------------|-----------|------------|
| Hero (idle) | 14 | 6 body/clothing + 3 skin/hair + 2 weapon + 2 element idle glow + 1 rim light |
| Hero (combat glow) | 16 | 14 idle + 2 additional element-active glow colors |
| Basic enemy | 8 | 4 chitin/body + 2 void core + 1 rim glow + 1 element affinity |
| Elite enemy | 12 | 6 chitin/body + 2 void core + 1 rim glow + 2 pre-corruption accessory + 1 element affinity |
| Boss | 20 | 10 body/frame + 3 void core (gradated) + 2 rim glow + 3 element affinity + 2 phase-specific |
| Lore fragment | 6 | 2 base + 2 memory color + 1 void remnant + 1 gold highlight |
| Currency shard | 4 | 2 base + 1 emission + 1 highlight |
| Hazard prop | 8 | 4 base + 2 element glow + 1 warning marker + 1 void rim |
| Obstacle | 10 | 6 structure + 2 void corruption + 2 crack glow |

**Max pixels per character** (sprite canvas size):
| Entity Class | Canvas (px) | Render Area (px) |
|-------------|-------------|-------------------|
| Hero | 64×64 | 48×48 (8 px padding for weapons/VFX) |
| Basic enemy | 40×40 | 32×32 |
| Elite enemy | 48×48 | 36×36 (with 6 px padding per side) |
| Boss | 80×80 | 64×64 (8 px padding — bosses also have an extended glow overlay at +4 px outside canvas) |
| Lore fragment | 24×24 | 16×16 |
| Currency / collectible | 16×16 | 8×8 (with 4 px padding) |
| Obstacle / hazard | 40×40 | 32×32 |

**Readability at medium camera distance** (default combat zoom):
| Readability Requirement | Minimum Size | Test |
|------------------------|-------------|------|
| Hero identifiable by silhouette | 24×24 px | At 66% scale (mid-zoom-out), hero still reads as distinct from all enemy types |
| Element type on projectile | 8×8 px | The shape vocabulary (teardrop/hex/zigzag) must be recognizable at 8×8 px |
| Enemy tier identification | 20×20 px | The difference between basic (broken circle) and elite (distorted polygon) must be parsable |
| Lore fragment visible | 10×10 px | The glow (not the object shape) must catch the player's eye at any camera distance |
| Threat zone / hazard area | 16×16 px | The element-colored pulsing rim must be visible in peripheral vision |
| Currency on ground | 6×6 px | Smallest readable element — relies on color contrast against void/terrain background |

**All characters must work against both background types**:
| Background Type | Hero | Enemy | VFX | Prop |
|----------------|------|-------|-----|------|
| Void-dark (10–15% value) | Hero rim light (+30% value) + element glow ensure contrast | Enemy rim glow (1 px) + chitin specular flecks separate from void | 100% saturated elemental shapes pop against pure dark | Lore fragment gold-white glow (60% value) readable |
| Restored-bright (40–70% value) | Hero element glow shifts to 80% value (brighter than background) | Enemy void core (10–15% value) provides silhouette contrast — enemies are always darker than restored terrain | Shapes keep 100% saturation but reduce emission to 0.8 to avoid bloom-washout against bright bg | Props keep 50% sat but add 2-px dark drop shadow for ground separation |
| Mixed (partial restore, 25–50% value) | Hero is always +20% value over any background tile | Enemies are always -15% value below any background tile | Shapes are always the highest saturation element on screen | Props always have both glow AND drop shadow to work in mixed lighting |

**Contrast floor rule**: No character may drop below a 3:1 contrast ratio against its background at any pixel. Tested against the three worst-case backgrounds: pure void (10% value), fully restored terrain (70% value), and mid-restore stone (35% value). Any character failing this test gets a rim light adjustment (width or value increase) until the test passes.

---

## UI & HUD Design Philosophy

*The Strategist's Table is not a computer interface — it is a war table strewn with parchment, etched runes, and hand-carved tokens. Every element the player touches should feel like it was pulled from a satchel, not a dropdown.*

### 6.1 Screen Real Estate — HUD Layout

The HUD is framed as a **parchment border overlay** on the Strategist's Table, occupying the outermost 8–12% of the screen. All gameplay occupies the inner clear zone.

**Layout zones (1280×720 reference, safe-zone-tested for 16:9, 16:10, and 21:9):**

| Zone | Position | Size | Contents |
|------|----------|------|----------|
| Health & Shield | Top-left, inset 8 px from edge | 200×24 px active area | Health bar (runic inscription), shield bar (glow overlay), class-specific resource bar |
| Skill slots | Bottom-center, floating above parchment border | 5 slots × 48×48 px each, 6 px gap | Active skills (cooldown sweep overlay), ultimate slot (larger at 56×56 px, centered) |
| Currency counters | Top-right, stacked vertically | 120×18 px per counter | Rift Shards (gold), Void Essence (purple), zone-specific currency |
| Minimap | Top-right corner, nested into parchment corner | 120×120 px circular disk | See Section 6.6 |
| Buff/debuff indicators | Below health bar, horizontal flow | 24×24 px per icon, max 8 visible | Duration sweep ring, stack count (6-pt pixel label, bottom-right) |
| Kill / combo counter | Right edge, mid-height, vertical | 36×18 px text area | Combo multiplier, kill streak timer bar alongside |
| Danger warning / boss health bar | Top-center, below zone title area | 300×20 px | Boss name (left-aligned), health bar (runic inscription, full width), elemental affinity icon (right) |
| Zone title card | Top-center, above boss bar | Full-width overlay, 48 px tall | Zone name, difficulty tier badge, fades after 3 s |
| Notification / toast | Center-right, vertical stack | 200×36 px per toast | Quest updates, achievement unlocks, lore fragment discoveries — scrolls in from right edge |

**Safe zones — no UI may overlap:**
- **Center 50% × 50% kill box** (640×360 px at 1280×720): Pure gameplay area. No persistent UI element may intrude. Transient elements (draft pick cards, boss warnings) may enter from edges but must retract within 2 s.
- **Bottom 30 px action bar buffer**: Reserved for critical touch-friendly area on mobile/touch inputs.
- **±8 px from screen center**: No element may pin to the exact center point. The player's aim/position indicator is the only occupant.

During draft screen open (HUD dims to 20% brightness), the draft panel occupies the **center 70% × 60%** with the arena visible behind at 20% brightness + 8-directional motion blur. Draft panel opacity: 90% parchment fill, 10% arena bleed-through. The parchment border at screen edges remains at full 100% brightness — the player must never lose their frame of reference.

### 6.2 Typography

The Strategist's Table uses two pixel fonts: one **runic display face** for titles, zone announcements, and draft-card names, and one **readable body face** for numbers, labels, and tooltips.

**Font selection criteria:**
- Display font: Minimum 5×7 px character block, monospaced, terminal-stroke letters with angular cuts (ink-stamped, not printed). Must support uppercase A–Z, digits 0–9, and common punctuation (.,!?:;-). At least 3 distinct ligature pairs (TH, ST, ER) for runic feel.
- Body font: Minimum 5×5 px character block (with 1 px descender for g/j/p/q/y), sans-serif, pixel-optimized for 1280×720 readability. Must support full ASCII Latin-1 set plus accented chars (à, é, í, ó, ú, ü, ñ) — minimum 128 glyphs to cover Western European languages.

**No CJK / Cyrillic support in v1.** Character set is ASCII + Latin-1 supplement. Localization for East European languages uses Latin-1, for CJK requires a separate font swap.

**Font size hierarchy:**

| Context | Display or Body | Size (px) | Line height | Notes |
|---------|----------------|-----------|-------------|-------|
| Zone title card | Display (runic) | 14 pt (28×14 px canvas) | 14 px | Upper-case only, letter-spacing +2 px |
| Boss name | Display (runic) | 10 pt (20×10 px canvas) | 10 px | Upper-case, glow behind text |
| Draft card item name | Display (runic) | 8 pt (16×8 px) | 8 px | Single line, centered |
| HUD label text | Body | 7 pt (7×7 px) | 7 px | Health "HP", currency "SHARDS", skill keybinds |
| HUD value counters | Body | 7 pt (7×7 px) | 7 px | Numbers only, monospaced digit width |
| Damage numbers | Display (runic numerals) | 10 pt pulsing → 6 pt fade | 10 px | Rune-glyph digits, shrink as they float up |
| Tooltip / description | Body | 6 pt (6×6 px) | 8 px | Tooltip box max width 240 px, word-wrapped |
| Settings / menu items | Body | 8 pt (8×8 px) | 10 px | Menu options, slider labels |
| Button labels | Display (runic) | 7 pt (14×7 px) | 7 px | Short labels only (1–3 words max) |

**Text contrast minimums:**
- All readable text: minimum **4.5:1** against its background (WCAG AA).
- Runic display text (shorter, larger): minimum **3:1** against its background.
- Damage numbers: always rendered in 100% saturated element color against void background — no contrast ratio requirement (temporary, animated, unread).
- Text on parchment background: dark ink (#2B1D0F) on parchment (#D4C4A8) = 6.3:1 — passes easily.
- Text on void-dark panel: gold ink (#E8C84A) on dark panel (#1A1423) = 7.1:1 — passes.

**Rune vs. readable text rules:**
1. Zone titles, boss names, and item names = runic display (atmosphere).
2. All gameplay-critical information (health value, currency count, timer, cooldown seconds) = body font, readable (function over atmosphere).
3. Damage numbers = runic-glyph numerals only (no letters needed, pure visual feedback).
4. Tutorial / first-time tooltips = body font always. New players must not struggle to parse essential instructions.
5. Lore fragments: discovered fragments display rune-glyph on the fragment card, with a "translate" button that renders the readable body text on the same card. This gives atmosphere without gating comprehension.

### 6.3 Screen Flow & Transition Treatment

Every transition on the Strategist's Table is an **ink-stamp, parchment-tear, or rune-ignite** event. No fades-to-black — the table is always present.

**Zone entry transition:**
1. Arena dims to 30% over 0.3 s.
2. Zone title card stamps in from the top edge (ink-stamp squish animation: overshoot width to 110%, compress to 90%, settle at 100% over 0.5 s).
3. Title holds for 2 s, then the parchment edge ignites with the zone's element color (0.8 s particle ash trail as the card burns away).
4. Arena brightness restores to 100% over 0.3 s.
5. Total duration: 3.1 s. Player can move/dodge during the burn-away phase (frames 2.0–3.1).

**Boss warning treatment:**
1. Screen rim pulses with boss element color (3 pulses over 1.5 s, 20 px vignette width).
2. Boss icon appears center-top (64×64 px, element-rimmed), slams down with screen shake (2 px, 3 oscillations, 0.3 s).
3. Runic boss name text stamp-in below icon (identical to zone card animation, but faster: 0.3 s squish).
4. Warning persists until boss is engaged (first damage dealt), then transitions to the persistent boss health bar.
5. If player leaves boss arena: warning re-triggers on re-entry after 10 s cooldown.

**Victory screen overlay:**
1. 0.5 s hold on final frame (kill cam freeze).
2. Gold-ink bloom from center, expanding to fill screen (0.8 s).
3. Runic "VICTORY" text stamps in (1.2 s squish animation, two words staggered: VICTOR at 0 s, Y at 0.15 s).
4. Reward cards slide up from bottom (parchment rectangles, staggered by 0.1 s each, up to 5 cards).
5. "Return to Camp" button (circular rune-stamp, bottom-right) appears after all cards have settled + 0.5 s delay.
6. No manual dismiss required — "Return to Camp" is active, or auto-return after 15 s idle.

**Defeat screen overlay:**
1. 1.0 s hold on death moment (hard freeze, no input accepted).
2. Void-dark vignette creeps inward from edges over 1.5 s, settling at center-80% coverage (20% arena still visible, dimmed to 10%).
3. Parchment tears diagonally from top-left (2D paper-tear shader, 0.8 s) revealing a void-black panel beneath.
4. Runic "FALLEN" text appears on the void panel, with a flicker animation (ink not fully dry — 2 s of random alpha flicker at 8 Hz).
5. Stats summary card slides up (runic labels, body-font values).
6. Two buttons: "Try Again" (circular rune-stamp, golden) and "Return to Camp" (rectangular parchment-tab, neutral). Both enabled after 2 s from card arrival.
7. Total unskippable sequence: 4.3 s before player can act.

**Pause menu:**
- Trigger: circular rune-stamp button (top-right, 32×32 px, always visible) or Escape key.
- Open: arena dims to 20% + motion blur, parchment panel slides down from top edge covering upper 60% of screen. Panel has torn-paper bottom edge.
- Items: Resume (rune-stamp, center), Settings (parchment tab, right), Quit to Camp (parchment tab, far-right, red ink).
- Close: panel slides back up, arena brightness restores over 0.25 s.
- No background parallax or animation during pause — the arena is frozen.

**Settings / options style:**
- Full-screen parchment sheet (not a panel), with a curled-corner page-turn animation to enter.
- Settings categories as bookmark tabs on the left edge.
- Sliders: horizontal runic inscription that fills with element-colored ink as value increases.
- Toggles: circular seal stamp, filled = on, empty = off.
- Dropdowns: accordion parchment fold (unfolds downward, each option is a paper slip).
- Back button: curled-corner page-turn reverse to exit settings.

### 6.4 Icon Design Guidelines

All icons are **pixel art rendered on a parchment or rune-stone canvas**. No photorealistic or vector icons.

**Skill icon standards:**
- Canvas: 24×24 px active area + 2 px padding = 28×28 px total texture.
- Palette limit: **8 colors per icon** (1 transparent, 1 parchment-background tint, 6 subject colors).
- The subject (weapon, elemental shape, body part) must occupy at least 50% of the active area.
- Background: solid parchment-tint (never transparent — each icon is a painted tile on the Strategist's Table).
- Readability rule: at 24×24 px on a 1280×720 display, the core shape must be identifiable in 0.2 s glance test. If a designer cannot name the icon in 0.2 s at actual scale, the icon needs simplification.
- Cooldown overlay: dark sweep (from transparent toward #0F0A12 at 70% opacity), chasing the 12-o'clock position clockwise. No alpha gradient noise — solid sweep edge.
- Ultimate icon: 28×28 px active area + 2 px padding = 32×32 px total. Gold-ink border (1 px) around the parchment canvas.

**Element icon standards (consistent shapes across all systems):**

| Element | Icon Shape | Canvas | Key Feature |
|---------|-----------|--------|-------------|
| Fire | Teardrop with 2 inner highlights | 16×16 px | Bottom-left pixel always lit (ember core) |
| Ice | Hexagon, faceted (3 inner triangles) | 16×16 px | Top-center pixel always white (frost point) |
| Lightning | Zigzag bolt with 2 branches | 16×16 px | Bottom-right pixel always yellow-white (strike tip) |
| Void | Distorted circle, 2 inward spikes | 16×16 px | Center 2×2 px pure black (#000000) |
| Arcane | Five-pointed star, open center | 16×16 px | Center pixel purple-white glow |
| Earth | Irregular polygon, 6 sides | 16×16 px | Lower-right corner brown-dark (soil weight) |
| Wind | 3 stacked horizontal curves (wave) | 16×16 px | Top curve always lighter than bottom (wind gradient) |
| Holy | Upright teardrop + crossbar | 16×16 px | Center crossbar extends 2 px past teardrop edges |

Element icons are used as **affixes on skill cards** (corner badge, 12×12 px), **buff/debuff indicators** (16×16 px), and **zone affinity markers** (on minimap, 8×8 px). At scaled-down sizes, only the shape silhouette and the key feature pixel are required.

**Buff/debuff icon principles:**
- Canvas: 16×16 px (compact) or 24×24 px (extended tooltip).
- Single subject + element badge (top-left, 6×6 px element icon).
- Duration indicator: 1-px ring around the icon clockwise from 12-o'clock, 50% opacity white, swept off as time elapses.
- Stack count: 6-pt bold number, bottom-right, white, 1-px black drop shadow.
- Debuffs get a red-tint overlay on the parchment background (multiply blend, 30% opacity red).
- Buffs get a gold-tint overlay (additive blend, 20% opacity gold).

**Lore fragment icon:**
- Canvas: 12×12 px.
- Shape: torn-parchment rectangle, 1-px glow (gold-white) outlining the torn edge.
- Corner curl at top-right (3 px triangle fold, darker parchment color).
- On the fragment face: a single rune glyph (the fragment's identifier), 5×7 px.
- When collected: glow intensifies (2 px, pulsing at 1 Hz) for 3 s, then returns to normal.

**Collectible icon (generic):**
- Canvas: 8×8 px.
- Shape: small diamond or circle (whichever fits the collectible type).
- Minimum 1 px of element-rim glow for visibility against any background.

### 6.5 Animation & Feedback on UI

Every UI interaction gets a **parchment-physical feel**: paper squish, ink spread, stamp impact. No digital-smooth transitions.

**Button press animation:**
1. Idle: parchment texture, raised (1-px bottom/right drop shadow at #2B1D0F, 60% opacity).
2. Hover: scale to 105%, drop shadow extends to 2 px, element-color rim glow (1 px perimeter).
3. Press: scale to 90%, drop shadow reduces to 0 px (pressed into table), brightness dips 10% for 0.08 s.
4. Release: overshoot to 105% for 0.05 s, settle to 100% at 0.1 s. Total press-release: 0.23 s.
5. Disabled: 50% opacity, no hover state, cross-hatch overlay (2-px diagonal lines, 20% opacity).

**Card draft pick-up animation:**
1. Cards sit on table: slight rotation variance (±3°), slight y-offset variance (±2 px), stacked with 1-px drop shadow.
2. Hover on card: card rises 4 px (y offset), drop shadow extends to 4 px, rotation straightens to 0°, element glow appears behind card.
3. Pick up card: card scales to 110%, y rises 8 px, then shrinks to 0% over 0.2 s with a slight arc (ease-out quad). Simultaneously, the chosen card's element-color particle burst (8 particles, 12 px travel, 0.3 s fade).
4. Non-chosen cards: shuffle sideways (0.15 s), then slide off to left/right edges (0.3 s, ease-in).
5. Total pick-up animation: 0.5 s until new card set enters.

**Health bar decrease/increase animation:**
- Decrease: bar depletes from right to left in two layers. **Foreground** (current HP) depletes immediately (0.1 s). **Background** (delayed HP, shown as a darker desaturated bar) ticks down to match over 0.5 s — gives the player a clear "damage taken" visual buffer.
- Increase: bar fills left-to-right, single layer, 0.3 s with a brief 105% overshoot at 0.25 s, then settle.
- At zero HP: bar cracks (2-px jagged line through the inscription, white, fades in over 0.3 s), then screen transitions to defeat sequence.
- Critical HP (< 25%): bar pulses (80% → 100% fill oscillation, 1 Hz, sine wave), and the bar's runic inscription glows red.

**Currency collect → counter animation:**
1. Currency orb touches player: 4-particle burst (element-colored, 8 px travel, 0.2 s).
2. After 0.1 s delay, the currency counter number does a **count-up animation**: old number slides up and out, new number slides in from below (0.15 s each digit).
3. If 3+ orbs collected within 1 s, the counter skips the individual animations and shows a single "+X" pop-up (6 pt, centered above counter, gold ink, fades over 0.5 s) — then jumps to the new total.

**Screen shake:**
- Shake profiles (defined by amplitude in px, frequency in Hz, duration in s):

| Trigger | Amplitude | Frequency | Duration | Falloff |
|---------|-----------|-----------|----------|---------|
| Boss roar entrance | 4 px | 12 Hz | 0.4 s | None (hard stop) |
| Boss stomp attack | 3 px | 8 Hz | 0.3 s | Linear to 0 at 0.3 s |
| Player hit (heavy) | 2 px | 15 Hz | 0.15 s | Exponential to 0 at 0.15 s |
| Explosion (any) | 2 px | 10 Hz | 0.2 s | Linear to 0 at 0.2 s |
| Zone clear / victory | 1 px | 6 Hz | 0.5 s | Linear to 0 at 0.5 s |

- Shake applies to the **entire canvas**, not individual elements. The parchment HUD border shakes with the arena (the Strategist's Table rattles).
- No shake during menus, settings, or pause.
- Shake priority: if a new shake triggers while one is active, the higher amplitude wins; on tie, the new one replaces.

**Damage vignette / low-health warning:**
- On taking damage: red vignette (circular gradient from edges, 30% opacity at edges → 0% at center-30%) flashes for 0.15 s.
- Below 25% HP: persistent red vignette at 10% opacity edges → 0% at center-50%. Pulses at 0.5 Hz (10% → 15% → 10%) to maintain urgency without obscuring gameplay.
- Below 10% HP: vignette intensity increases to 20% → 30% → 20% pulse, plus the screen border gains a jagged "cracked parchment" overlay (1-px white lines, randomized crack pattern, refreshed every 0.5 s).
- All vignette opacities are additive — damage flash adds on top of low-health persistent vignette.

**Notification / toast style:**
- Toast slides in from the right edge, 8 px from top of action area.
- Background: parchment rectangle with a torn-right-edge (entry edge), 3-px drop shadow.
- Icon (12×12 px, left-aligned) + title text (7 pt body, bold) + optional subtitle (6 pt body, 50% opacity).
- Entry: slide in over 0.3 s (ease-out cubic).
- Hold: 3 s for normal toasts, 5 s for achievement/unlock toasts.
- Exit: slide out over 0.2 s (ease-in cubic), or stack if multiple toasts are queued (stack up to 3, then overflow queue).
- Interaction: clicking or tapping a toast dismisses it immediately with a crumble animation (0.15 s, paper fold into center).
- Maximum visible toasts: 3. Queue beyond 3 is held and released oldest-first as space opens.

### 6.6 Minimap / Zone Map Treatment

The minimap is framed as a **hand-drawn parchment map** pinned to the corner of the Strategist's Table. The player is a moving ink-wash stamp; discovered areas light up like wet ink revealing hidden text.

**Visual style:**
- Canvas: 120×120 px circular disk, bounded by a 2-px gold-ink ring.
- Background: parchment texture (#C4B49A at center, darkening to #8B7D65 at edge — burnt map edge effect).
- Map lines: 1-px dark-ink lines (#3D2B1A at 80% opacity), hand-drawn quality (slight sine-wave wobble, amplitude 0.5 px at 0.5 Hz).
- Restored areas: warm gold wash (#D4A84B at 25% opacity fill, additive blend — wet ink reveal effect).
- Void/unexplored: dark sepia (#2A1F15 at 90% opacity, subtractive blend — unlit part of the map).
- Fog of war / void concealment: scrolling noise texture (2 px cells, 50% opacity #1A130D, scrolls at 0.25 px/s inward-toward-center) over unexplored areas.

**What is shown:**
| Element | Visual | Size on map | Notes |
|---------|--------|-------------|-------|
| Player position | White-gold ink-wash stamp, 3-pt circle | 4×4 px | 1-px pulsing ring (1 Hz) around stamp |
| Enemy positions (non-boss) | Red specks, 1×1 px | 1×1 px | Only visible when enemy is within player's detection radius (16 map-px = ~80 game-px) |
| Boss location | Element-colored skull rune | 5×5 px | Always visible once boss arena is entered |
| Restored areas | Warm gold wash fill | Variable | Smooth polygon fill, updates every 1 s |
| Rift fragments / collectibles | Gold-white diamond, pulsing | 2×2 px | Only if player has the "riftsense" ability |
| Zone boundary | Dark-ink dashed line, 1 px | Perimeter | Only visible when player is within 20 map-px of boundary |
| Player facing direction | Small triangle on stamp edge | 2-px base, 3-px height | Rotates with player facing, white fill |
| Danger indicators (incoming boss AoE) | Red expanding ring | Variable | 0.5-px ring, expands at same rate as in-game AoE, fades 0.3 s after mechanic resolves |

**Update rate:**
- Player position: every frame (60 fps).
- Enemy positions: every 3 frames (20 Hz).
- Restored area reveal: every 5 frames (12 Hz).
- Collectible visibility: every 10 frames (6 Hz) — less critical, lower priority.
- Boss position: every frame once engaged.

**Performance constraint**: The minimap must render within **0.2 ms** per frame total (including texture updates and blit to screen). If the reveal texture update exceeds budget, fall back to updating every 10 frames (6 Hz) for the wash fill layer.

### 6.7 Accessibility

The Strategist's Table must be usable by players with visual, motor, or hearing disabilities. These requirements are non-negotiable for release.

**Minimum readable text size:**
- Body font: never below **6 pt** (6×6 px character block on a 1280×720 canvas at 100% UI scale).
- At 1280×720, 6 pt = 1/120th of screen width per character. This is the floor. No essential text may be rendered below this size.
- Damage numbers (non-essential, animated) are exempt.
- Runic display text: never below **7 pt** (14×7 px canvas).

**UI scaling option:**
- Three settings: **100%** (default), **125%**, **150%**.
- Scaling method: uniform integer upscale (2× nearest-neighbor for 125% and 150%) — no bilinear blur.
- At 125%: 1280×720 renders as 1600×900 internal resolution for UI layer. HUD elements scale uniformly.
- At 150%: 1280×720 renders as 1920×1080 internal for UI layer. At this scale, the draft card panel uses scrollable parchment (scrolling with mouse wheel or touch drag) because cards no longer fit within the viewport.
- Scaling applies to the **entire UI layer** only. The game layer (arena) remains at native resolution. This preserves 60 FPS during draft screen.
- Settings menu must preview the scaling change immediately (apply on slider release, no restart required).

**Colorblind-safe icon indicators:**
- All element icons are **shape-distinct** (see Section 6.4 icon table) — no element is identified by color alone.
- Buff/debuff type (beneficial vs. harmful) is indicated by **icon border shape**: circular for beneficial, hexagonal for harmful. Red tint is supplementary, not primary.
- Danger indicators (AoE telegraphs, boss warnings) use **pulsing shape + animation** in addition to color. A red-only indicator would fail this requirement.
- Rarity tiers on items/cards use **shape borders** (square = common, pentagon = uncommon, hexagon = rare, octagon = legendary) in addition to color.
- Player/enemy/ally differentiation: player icon has pulsing ring, enemy has jagged outline, ally has smooth double outline.

**Audio cues for UI interactions:**
Every interaction type must produce at least one distinct audio cue:

| Interaction | Audio cue | Notes |
|-------------|-----------|-------|
| Button press | Single parchment crinkle + wood tap | Pitch varies by button size (small = higher pitch) |
| Card draft — hover | Paper rustle (0.2 s) | Volume: 30% of master |
| Card draft — pick up | Runic chime + paper slide | Element-colored chime (different root note per element) |
| Health bar — damage | Low thud (drum skin) | Volume proportional to damage % of max HP |
| Health bar — below 25% | Continuous low heartbeat loop | 80 bpm, fades in over 0.5 s, fades out over 1 s when HP > 25% |
| Currency collect | Short coin chime | Pitch increases by +2 semitones per 10 consecutive collects (diminishing returns) |
| Level up / upgrade available | Rising arpeggio (3 notes, 0.5 s) | Major chord, instrument = celeste |
| Zone entry | Low horn blast (1 s) | Zone element's associated instrument |
| Boss spawn | Brass hit + low rumble | 0.5 s attack, 2 s decay rumble |
| Victory | Fanfare (4 notes, 1.5 s) | Major, full chord, trumpets |
| Defeat | Single cello note (2 s, slow attack) | Minor, lowest octave, with reverb tail |
| Pause open | Ink-pot lid clink (0.1 s) | High-pitched, short |
| Pause close | Ink-pot lid clink (0.1 s) — same sample | Distinct enough to associate both actions |
| Settings slider change | Wooden click (0.05 s) | Tick per discrete step |
| Notification toast | Paper slide (0.15 s) | Same as card hover but shorter |
| Tooltip open | Paper lift (0.1 s) | Quiet, at 20% of master |
| UI navigation (keyboard) | Focus tick (0.05 s) | Percussive, panned center |
| Error (can't afford, can't equip) | Low buzz (0.15 s) | Dissonant, 70% volume |

All audio cues must have a **mute toggle** separate from master volume. The UI audio mixer group is its own bus (called "Interface") with independent volume control in the Settings menu. Cue duration is capped at 2 s — no looping UI sounds except the low-health heartbeat.

---

## Lighting & Post-Processing

**Governing Principle**: Every lighting decision serves either readability (Combat Readability First) or mood (Narrative Fragments). No light exists for "realism" — this is a pixel-art void, not a photographic scene. Light sources are either game-mechanical (elemental VFX, detection ranges) or narrative (campfire = safety, memory fragments = recovered lore).

**Renderer Constraint**: All lights are **URP 2D Lights** using the 2D Renderer. No 3D lights are permitted. Light falloff and intensity curves are hand-authored to respect pixel boundaries — no sub-pixel smoothness that breaks the pixel-art aesthetic.

---

### 7.1 URP 2D Lighting Model

#### 7.1.1 Light Types Used

| Light Type | Purpose | URP Parameter Configuration |
|------------|---------|------------------------------|
| **2D Global Light** | Base ambient per game state | `Light Type = Global`, `Color = per-state ramp`, `Intensity = 0.1–0.8` |
| **2D Point Light** | Elemental VFX, campfire, lore fragments | `Light Type = Point`, `Falloff = Custom Curve (pixel-stepped)`, `Intensity = 0.3–2.0` |
| **2D Freeform Light** | Boss silhouette glow, zone restore sweeps | `Light Type = Freeform`, `Shape = per-boss silhouette`, `Softness = 2 px` |

**Visual Identity Principle**: Combat Readability First — point lights tie directly to elemental type; players learn which light color corresponds to which damage type before reading tooltips.

#### 7.1.2 Light Budget Per Screen

| Metric | Value | Rationale |
|--------|-------|-----------|
| Max real-time 2D lights per frame | 8 | 4×2 pixel overhead per light; 8 = sweet spot between visual density and 60 FPS on low-end mobile |
| Max lights affecting single sprite | 4 | URP 2D Renderer shader configuration; beyond 4 = visual noise on pixel-art surfaces |
| Light fallback behavior | Nearest wins | If >8 lights visible, only nearest 8 render; remainder contribute only to ambient color |
| Volumetric lights | None | Not compatible with pixel-art aesthetic; light "volume" implied by particle density, not volumetric rendering |

**Mood connection**: Combat state relies on this budget — elemental VFX are the *only* light sources against the near-zero ambient. This constraint enforces the "Controlled Chaos in the Void" mood (Section 2.2).

#### 7.1.3 Light Falloff Curves

All 2D point lights use **pixel-stepped custom falloff curves**, not URP's default smooth falloff. The falloff must step in whole-pixel increments to preserve the pixel-art aesthetic.

**Curve definition** (intensity vs. pixel radius):
- Radius 0 px: 100% intensity
- Radius 8 px: 75% intensity (step, not gradient)
- Radius 16 px: 50% intensity
- Radius 24 px: 25% intensity
- Radius 32 px: 0% intensity

**Exemption**: Lore fragments and campfire use a softer (but still stepped) 6-step curve to communicate warmth without breaking pixel boundaries.

**Visual Identity Principle**: Narrative Fragments — the campfire's warmer, gentler falloff curve is a subtle visual signal that this space is different from the void. Players feel "home" before they consciously analyze the light shape.

#### 7.1.4 Light Cookies & Masks

All lights use **hand-drawn pixel-art cookies** (mask textures) to avoid the "perfect circle" artificiality of default URP lights.

| Light Source | Cookie Resolution | Cookie Pattern |
|--------------|-------------------|----------------|
| Campfire (Hero Camp) | 32×32 | Irregular blob with 4–6 uneven "lobes" simulating flame shape; 2 px soft edge (pixel-stepped) |
| Elemental VFX (Fire) | 16×16 | Teardrop shape, matching projectile silhouette (see Section 3) |
| Elemental VFX (Ice) | 16×16 | Hexagon shape, matching ice projectile |
| Elemental VFX (Lightning) | 16×16 | Zigzag shape, 3 px width, matching lightning |
| Lore Fragment | 24×24 | Perfect octagon (rarity signal, see Section 6.5) with 1 px border pulse |
| Boss Freeform Light | 64×64 | Boss silhouette mask; inner 50% is full intensity, outer edge has 3 px stepped falloff |

**Cookie rendering**: Use URP 2D Light's `Cookie` parameter with `Filter Mode = Point (no filter)`. No bilinear filtering on light cookies — ever.

#### 7.1.5 Shadow Casting

URP 2D shadow casting is **disabled by default** and only enabled for specific layers with strict constraints.

| Layer | Shadow Casting | Why |
|-------|----------------|-----|
| Player (Hero) | **Enabled** | Rim light readability; shadow grounds the hero on the arena floor |
| Enemies (Basic/Elite) | **Enabled** | Same grounding effect; shadow size communicates hitbox area |
| Environment (Ruins) | **Enabled** | Consequence Language — restored ruins have crisp shadows; corrupted ones have no shadows |
| Boss | **Enabled (Dynamic)** | Shadow pulses in sync with boss heartbeat; shadow lengthens during phase transitions |
| Projectiles / VFX | **Disabled** | Too many, too fast — visual noise and performance cost |
| UI Layer | **Disabled** | UI reads as floating overlay; no grounding needed |

**Shadow configuration**:
- `Shadow Intensity = 0.3` (softer than photographic shadows)
- `Shadow Resolution = 128 px` (low-res = pixel-art compatible)
- `Shadow Softness = 2 px` (stepped, not gradient)
- `Shadow Distance = 8 px` (short — implies overhead light direction, not sun)

**Mood connection**: Hero Camp has longer, softer shadows (16 px distance) to communicate golden hour (Section 2.1). Combat has short, sharp shadows (8 px) because the only light sources are nearby elemental VFX (Section 2.2).

---

### 7.2 Lighting Per Game State

Every game state has a dedicated light configuration that directly implements the mood from Section 2.

#### State Transition Crossfade

All lighting changes between states use **1.0 s linear crossfade** unless specified. Crossfade applies to:
- 2D Global Light color + intensity
- Vignette intensity
- Color grading parameters
- Bloom threshold + intensity

**Exception**: Boss phase-change light shifts are **instantaneous** (0.0 s) for shock value, then fade to new values over 0.5 s.

#### 7.2.1 Hero Camp State (Section 2.1)

**Mood target**: "Warm Hearth, Quiet Memory" — golden hour, low contrast, intimate

| Light Component | Configuration |
|-----------------|---------------|
| 2D Global Light | Hue 30° (warm amber), Saturation 0.2, Value 0.4, Intensity 0.3 |
| Campfire Point Light | Hue 20° (orange), Intensity 0.6, Radius 128 px, Cookie = campfire blob (32×32) |
| Secondary Point Lights (3 total) | Hue 35° (gold), Intensity 0.2 each, placed at tent, workbench, and lore pedestal |
| Shadow Distance | 16 px (longer = golden hour implication) |
| Shadow Intensity | 0.2 (softer = calm) |

**Visual Identity Principle**: Narrative Fragments — the campfire is the warm center; every other light in the camp orbits it. This is the visual metaphor of "home" that the player is restoring across the rifts.

#### 7.2.2 In-Run Combat State (Section 2.2)

**Mood target**: "Controlled Chaos in the Void" — near-zero ambient, VFX-only light sources

| Light Component | Configuration |
|-----------------|---------------|
| 2D Global Light | Hue 240° (cool blue-black), Saturation 0.1, Value 0.12, Intensity 0.15 |
| Hero Rim Light | *Material-based*, not scene light — hero sprite uses emission 0.4 at all times (see Section 4.4) |
| Elemental VFX Lights | 2D Point Lights spawned per projectile; Fire = hue 20°, Ice = hue 200°, Lightning = hue 50° |
| Shadow Distance | 8 px (short = nearby light sources only) |
| Shadow Intensity | 0.3 (sharper = tension) |

**Visual Identity Principle**: Combat Readability First — the near-zero ambient ensures elemental VFX pop at maximum contrast. Players can count projectiles in their peripheral vision because each one carries its own light.

#### 7.2.3 Boss Encounter State (Section 2.3)

**Mood target**: "The Storm Breaks" — chiaroscuro, boss is primary light source

| Light Component | Configuration |
|-----------------|---------------|
| 2D Global Light | Hue 220° (cold), Saturation 0.15, Value 0.1, Intensity 0.1 |
| Boss Freeform Light | Shape matches boss silhouette; color = boss element hue; intensity **pulsing 0.4–0.8** synced to boss heartbeat |
| Boss Phase Shift | Global Light hue shifts instantaneously on phase change; e.g., fire boss phase 2 shifts from hue 20° → hue 0° (redder, angrier) |
| Shadow Distance | 12 px (variable during pulse) |
| Shadow Intensity | 0.4 (deepest shadows = oppressive mood) |

**Visual Identity Principle**: Consequence Language — the boss's light pulse is not decorative; it communicates attack cooldown. Players learn that peak intensity = telegraph end → imminent attack.

#### 7.2.4 Victory / Zone Complete (Section 2.4)

**Mood target**: "Color Returns to the World" — sepia → color bloom wave

| Light Component | Configuration |
|-----------------|---------------|
| 2D Global Light (Start) | Hue 35° (sepia), Saturation 0.1, Value 0.3, Intensity 0.2 |
| 2D Global Light (End, 2.0 s) | Hue 45° (sunrise), Saturation 0.3, Value 0.6, Intensity 0.8 |
| Color Sweep Cookie | 2D Global Light uses scrolling cookie (128×16) that moves across screen L→R over 2.0 s |
| Shadow Distance | Ramps from 0 px → 12 px during sweep (world "gains form" as it restores) |

**Visual Identity Principle**: Consequence Language — this is the *signature* restoration visual. The light sweep is identical to the one used for memory fragment collection, but on a zone scale. Players understand "I just healed this place" before any UI appears.

#### 7.2.5 Defeat / Death (Section 2.5)

**Mood target**: "A Drift, Not a Crash" — sepia-grey, radial darkening

| Light Component | Configuration |
|-----------------|---------------|
| 2D Global Light | Hue 40° (sepia-grey), Saturation 0.05, Value 0.25, Intensity 0.2 |
| Vignette Intensity | Ramps from 0.0 → 0.8 over 1.5 s; radial darkening from edges inward |
| Shadow Distance | 0 px (world loses definition) |
| Shadow Intensity | 0.0 |

**Narrative touch**: The killing enemy remains at full color + full lighting for 1.5 s after everything else desaturates. This is a Consequence Language moment (Section 2.5) — the player sees *what* defeated them, not just a generic game over.

#### 7.2.6 Menus / Draft Overlay (Section 2.6)

**Mood target**: "The Strategist's Table" — parchment glow, arena dimmed

| Light Component | Configuration |
|-----------------|---------------|
| 2D Global Light (Arena) | Hue 240°, Saturation 0.1, Value 0.08, Intensity 0.1 (20% of combat brightness) |
| UI Panel Point Light | Hue 45° (parchment), Intensity 0.4, placed *behind* draft panel (only affects UI layer) |
| Card Element Lights | Each draft card has tiny 2D point light (radius 32 px) matching element hue; only activates on hover |
| Motion Blur | Arena background uses 8-directional blur (see Section 7.3.7); UI layer is sharp |

**Visual Identity Principle**: Combat Readability First — the arena is intentionally dimmed and blurred during draft so the player's focus is on the card choice. The motion blur implies "the world is still turning but you have a protected moment to decide."

---

### 7.3 Post-Processing Stack (URP Volumes)

**Stack Constraint**: Only URP Volume overrides explicitly listed here are permitted. No default post-processing. All volumes use **weight 0.0–1.0** per state with smooth crossfade.

#### 7.3.1 Volume Setup

| Volume Layer | Purpose | Update Frequency |
|--------------|---------|------------------|
| Default Volume | Base values for all states | Never (only as fallback) |
| Camp Volume | Hero Camp overrides | Enter/exit only |
| Combat Volume | In-run base overrides | Enter/exit only |
| Boss Volume | Boss encounter overrides | Per phase |
| Victory Volume | Victory sequence overrides | One-shot during sequence |
| Defeat Volume | Defeat sequence overrides | One-shot during sequence |
| Draft Volume | Draft overlay overrides | Toggle with draft UI |

#### 7.3.2 Color Grading (Split-Toning)

Color grading directly implements the mood palette from Section 2. All values use **ACES color space** (see Section 7.3.4).

| State | Shadows (Split-Toning) | Midtones (Gamma) | Highlights (Split-Toning) |
|-------|------------------------|------------------|---------------------------|
| Hero Camp | Hue 30° (warm amber) | Gamma +0.1 | Hue 50° (bright amber) |
| Combat | Hue 240° (cool blue) | Gamma -0.1 | (No highlights — VFX only) |
| Boss | Hue 220° (cold) | Gamma -0.2 | Hue = boss element |
| Victory | Hue 35° (sepia → 45°) | Gamma ramps -0.1 → +0.2 | Hue 55° (sunrise) |
| Defeat | Hue 40° (sepia-grey) | Gamma -0.3 | (No highlights) |
| Draft | Hue 35° (parchment) | Gamma 0.0 | Hue 45° (warm paper) |

**Visual Identity Principle**: Narrative Fragments — split-toning creates color harmony without visual noise. Hero Camp feels warm because *shadows* are warm, not because everything is orange. This is subtle but emotionally effective.

#### 7.3.3 Bloom

Bloom is **only for elemental VFX and high-emission surfaces**. Use bloom threshold to exclude the void, base sprites, and low-emission UI.

**Core settings**:
- `Bloom Threshold = 0.8` (only emission > 0.8 blooms; see Section 4.4 material values)
- `Bloom Filtering = Point` (no smooth blur; pixel-art compatible)
- `Bloom Resolution = Half` (performance; 2× blur downscale)

**Per-state intensity**:

| State | Bloom Intensity | Why |
|-------|-----------------|-----|
| Hero Camp | 0.3 | Campfire embers get gentle bloom; not overwhelming |
| Combat | 0.8 | Elemental VFX pop against void; this is the primary visual "punch" |
| Boss | 1.0 | Boss aura + phase-change shocks bloom strongly; oppressive mood |
| Victory | 1.2 | Maximum bloom during color sweep; feels like dawn breaking |
| Defeat | 0.1 | Almost no bloom; fading, lifeless feel |
| Draft | 0.2 | Card hover elements get subtle bloom; arena VFX bloom reduced |

**Critical constraint**: `Bloom Intensity must never exceed 2.0`. This is a performance guardrail and a visual one — excessive bloom washes out the pixel-art detail that makes the game readable.

#### 7.3.4 Tonemapping & Color Space

**Tonemapper**: **ACES** (Academy Color Encoding System)
- `Tonemapping Mode = ACES`
- `Color Space = Linear`

**Why ACES**:
1. Consistent color across PC, WebGL, and mobile
2. Better highlight handling for elemental VFX
3. Industry standard for URP 2D pixel-art games targeting premium platforms

**Exemption**: WebGL builds may fall back to `Neutral` tonemapping if ACES causes shader compilation issues on low-end GPUs.

#### 7.3.5 Anti-Aliasing (None)

**AA Mode**: Disabled completely.

Rationale: This is pixel-art. Anti-aliasing (FXAA, SMAA, TAA) blurs pixel edges and destroys the intentional visual style.

**Replacement for AA**:
- Use **URP Pixel Perfect Camera** (see Section 7.4) with integer scaling
- All sprite `Filter Mode = Point (no filter)`
- All sprite `Wrap Mode = Clamp`
- No sub-pixel movement on gameplay sprites (pixel snapping enabled)

**Exception**: UI text may use SDF (Signed Distance Field) rendering for sharp text at different scales. Gameplay sprites never use SDF.

#### 7.3.6 Vignette

Vignette intensity is the primary mood carrier for "contained" vs "expansive" feelings.

| State | Vignette Intensity | Vignette Radius | Mood Effect |
|-------|---------------------|-----------------|-------------|
| Hero Camp | 0.0 | 1.0 | No vignette = open, safe, home |
| Combat | 0.2 | 0.8 | Subtle edge darkening = contained danger |
| Boss | 0.4 | 0.6 | Stronger vignette = oppressive, claustrophobic |
| Victory | 0.0 → 0.1 ramp | 1.0 → 0.9 | Fades in slightly; world expands but focus stays on player |
| Defeat | 0.0 → 0.8 ramp | 1.0 → 0.3 | World closes in; tunnel vision on the killing enemy |
| Draft | 0.3 | 0.7 | Draws focus to center (draft panel location) |

**Vignette shape**: Circular, not rounded-corner box. Center always at screen center (not camera position).

#### 7.3.7 Depth of Field & Motion Blur

| Effect | Usage |
|--------|-------|
| **Depth of Field** | **Never enabled** — this is a 2D game; blurring pixel art destroys readability |
| **Motion Blur** | **Only during Draft overlay** — 8-directional blur on arena background layer only |

**Draft motion blur configuration**:
- Affects only `Arena` layer (UI layer excluded)
- `Blur Type = Directional (8-way)`
- `Blur Intensity = 0.3`
- `Blur Radius = 4 px` (stepped, not smooth)
- Automatically disabled when draft UI closes

**Why only during Draft**: The blur communicates "the arena is still running, but you're in a protected decision space." It's a Consequence Language technique — the world doesn't stop, but it *does* let you breathe.

#### 7.3.8 Post-Processing Performance Budget

| Post Effect | Target GPU Cost (ms) | Render Scale |
|-------------|----------------------|--------------|
| Color Grading | < 0.3 ms | Full-res |
| Bloom | < 0.8 ms | Half-res |
| Vignette | < 0.2 ms | Full-res (combined with color grading) |
| Motion Blur (Draft only) | < 0.6 ms | Half-res |
| **Total** | **< 2.0 ms** | |

**Optimization rule**: Color grading and vignette are always combined into a single blit pass by URP when both are enabled. Verify this in Frame Debugger — 2 separate passes = bug, fix it.

---

### 7.4 Pixel Perfect Camera Settings

**Camera Component**: URP `Pixel Perfect Camera` (built-in, not custom)

All settings enforce integer scaling to preserve pixel-art sharpness across all resolutions.

#### 7.4.1 Core Settings

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Reference Resolution X | 1280 | 16:9 base; 1280×720 = most common integer-scale denominator |
| Reference Resolution Y | 720 | Matches X; 720p is the render "floor" |
| Upscale Mode | `Window Dependent` | Integer scale only; no fractional scaling ever |
| Pixel Snapping (Gameplay) | Enabled | No sub-pixel movement on game layer; preserves 1px grid |
| Pixel Snapping (UI) | Disabled | UI may use SDF text and smooth scrolling; gameplay grid remains intact |
| Run In Edit Mode | Enabled | Preview pixel-perfect behavior in Scene view |

#### 7.4.2 Resolution Scaling Table

| Display Resolution | Internal Render Resolution | Scale Factor |
|--------------------|---------------------------|--------------|
| 1280×720 (720p) | 1280×720 | 1× (native) |
| 1920×1080 (1080p) | 1280×720 → upscale 1.5× nearest | 1.5× (UI layer renders at 1920×1080) |
| 2560×1440 (1440p) | 1280×720 → upscale 2× nearest | 2× (integer, perfect) |
| 3840×2160 (4K) | 1280×720 → upscale 3× nearest | 3× (integer, perfect) |

**Critical**: The *gameplay layer* always renders at 1280×720 and upscales with nearest-neighbor. The *UI layer* renders at native display resolution when UI scaling is set to 125% or 150% (see Section 6.6). This keeps text sharp while preserving pixel-art integrity for gameplay.

#### 7.4.3 Pixel Perfect + Post-Processing Interaction

**Problem**: URP Pixel Perfect Camera and post-processing can conflict if not ordered correctly.

**Solution (required setup)**:
1. Pixel Perfect Camera runs **before** post-processing in the render pipeline
2. Post-processing runs at **native display resolution** (after upscale)
3. Exception: Bloom runs at **half internal resolution** (640×360) and is upscaled

**Render order (per frame)**:
```
1. Gameplay renders at 1280×720 (pixel perfect)
2. UI renders at native resolution (if scaling enabled)
3. Pixel Perfect Camera upscales gameplay to display resolution
4. Post-processing (color grading, vignette) runs at display res
5. Bloom runs at half-res and composites
6. Final blit to screen
```

**Visual Identity Principle**: Combat Readability First — this order ensures gameplay pixels remain perfectly sharp while post-processing adds mood *without* blurring edges. If you see blurred gameplay pixels in a build, the render order is wrong — fix it.

---

### 7.5 Light Budget & Performance Targets

All values are **measured targets** for 60 FPS on minimum spec hardware.

#### 7.5.1 Light Budget

| Metric | Target Value | Measurement Method |
|--------|--------------|--------------------|
| Max 2D Point Lights per frame | 8 | Frame Debugger → 2D Renderer → Lights count |
| Max lights affecting 1 sprite | 4 | Frame Debugger → Per-sprite light list |
| Light culling threshold | Distance > screen edge + 32 px | Custom culling; lights off-screen get culled |
| Light intensity minimum for render | 0.1 | Lights below this contribute only to ambient, don't render |

#### 7.5.2 Post-Processing Budget

| Metric | Target Value | Notes |
|--------|--------------|-------|
| Full-screen blit passes per frame | 2 max | 1 = color+vignette combined, 2 = bloom if active |
| Bloom render scale | 0.5× (half-res) | Non-negotiable for mobile performance |
| Post-processing total GPU time | < 2.0 ms | Measure in Unity Profiler → GPU → Render.PostProcessing |
| Render target memory | < 16 MB | 1280×720 × 4 buffers (color, depth, bloom, temp) |

#### 7.5.3 Platform-Specific Adjustments

| Platform | Light Budget | Post Quality | Rationale |
|----------|--------------|--------------|-----------|
| High-end PC (GTX 1660+) | 12 lights | Full bloom + AA (text only) | Premium experience |
| Mid-range PC / Console | 8 lights | Full bloom | Target spec |
| Low-end mobile (Android 10+) | 6 lights | Bloom intensity capped at 0.5 | Battery + thermal |
| WebGL (desktop) | 8 lights | Full bloom | Browser texture limits |
| WebGL (mobile) | 6 lights | Bloom disabled | Performance + overheating |

**Fallback chain (implemented in code)**:
1. If > budget lights visible → cull furthest lights to ambient
2. If GPU time > 2.5 ms → disable bloom
3. If GPU time > 3.0 ms → disable all post except color grading
4. If still over budget → force 1× render scale (no upscaling)

---

### 7.6 Special Lighting Techniques

These techniques implement Consequence Language (Visual Identity Principle 3) — every light communicates a state change.

#### 7.6.1 Zone Restore Light Sweep

When a zone completes restoration (Victory state), a warm light sweep passes across the entire environment.

**Implementation**:
- 2D Global Light with a **scrolling cookie** (128×16 texture)
- Cookie is a **linear gradient pixel-stepped into 4 bands** (0%, 33%, 66%, 100% intensity)
- Cookie scrolls from left to right across the screen over **2.0 s**
- At the same time, global light hue shifts from 35° (sepia) → 45° (sunrise)

**Visual Identity Principle**: Consequence Language — this is identical to the light sweep that plays when collecting a single memory fragment, but on a zone scale. Players learn: "sweep = something was restored."

#### 7.6.2 Enemy Detection Glow (Angry Glow)

When the player enters an enemy's detection range, the enemy's rim light intensifies.

**Implementation**:
- Not a scene light — uses **sprite emission channel** (see Section 4.4)
- Normal enemy emission: 0.1 (almost off)
- Detection-range emission: **ramps to 0.6 over 0.3 s**
- Emission color = enemy's corruption hue (Section 4.3)
- Emission pulse frequency: 2 Hz when in detection range

**UDK reference**: This is the classic "angry glow" from Unreal Tournament — players learn to watch for the glow before the enemy even moves.

**Visual Identity Principle**: Combat Readability First — the glow is a *pre-attack* cue. Players with fast reaction times can dodge before the enemy fires. This rewards skill and awareness.

#### 7.6.3 Boss Phase Change Light Shift

When a boss transitions between phases, the entire arena's light color shifts instantaneously.

**Implementation**:
- 2D Global Light hue changes **instantly (0.0 s)** on phase change
- Example (fire boss):
  - Phase 1: Hue 20° (orange)
  - Phase 2: Hue 0° (red) — instant shift
  - Phase 3: Hue 350° (deep red) — instant shift
- After instant shift, global light intensity pulses **0.4→0.8→0.4** over 0.5 s

**Visual Identity Principle**: Consequence Language — the shift is a clear state boundary. Players know: "color changed = boss behavior changed." No ambiguity.

#### 7.6.4 Lore Fragment Glow

Lore fragments (collectible memory pieces) have a dedicated light that follows them.

**Implementation**:
- 2D Point Light, radius 64 px
- Intensity: **pulsing 0.4–0.7** at 1 Hz
- Hue = fragment's memory color (each zone has unique memory hue)
- Cookie = octagon shape (24×24) — matches rarity icon shape (Section 6.5)
- Light follows fragment at 0.1 s smooth damp (not pixel-snapped for floaty feel)

**Visual Identity Principle**: Narrative Fragments — the octagon cookie communicates "this is valuable/rare" before the player reads the UI. The floaty follow (not pixel-snapped) makes the fragment feel "alive" — a piece of memory drifting in the void.

---

**Section 7 Acceptance Criteria** (for implementation):
1. All 6 game states have distinct lighting profiles measurable in Frame Debugger
2. No more than 8 real-time 2D lights visible in any combat scenario
3. Post-processing total GPU time < 2.0 ms on target spec (measured in Profiler)
4. All light cookies use Point filtering; no bilinear blur on light shapes
5. Pixel Perfect Camera integer scaling verified at 1440p and 4K resolutions
6. Zone restore sweep, detection glow, and phase shift all functional in test scene

---

## VFX & Particle Systems

**Core Philosophy**: Every particle effect is a gameplay signal. No decorative particles. If a VFX does not communicate range, element, impact, state change, or consequence, it does not exist. In combat — where Section 2 defines near-zero ambient light — VFX are the only visual language the player has to read the fight. A player should be able to identify element, damage type, and hit outcome from particle shape alone, without reading health bars.

**Visual Identity Principle**: Combat Readability First — VFX are the player's primary信息来源 in void-lit combat. Ambiguity is a design failure.

### 8.1 Elemental VFX Library

Every elemental VFX follows the **shape language** established in Section 3 (fire = teardrop, ice = hexagon, lightning = zigzag). Each element gets three VFX tiers: projectile trail, impact, and status overlay.

#### 8.1.1 Fire

**Projectile trail**:
- 6 ember dots emitted per frame along projectile trajectory
- Each ember: 4×4 px teardrop (Section 3 shape), color `#FF4400` to `#FFAA00` over lifetime
- Lifetime: 0.3 s. Fade: sharp drop at end (no soft tail).
- Renderer mode: Additive. No light attached (budget reserved for impact).
- Tint follows projectile velocity vector — embers stretch 1.5× in direction of travel

**Impact**:
- Teardrop burst at hit point: 8 particles, each 8×8 px
- Direction: radial outward from center, random angle ±30° of surface normal
- Lifetime: 0.2 s. Initial speed: 120 px/s.
- On impact: emit one 2D Point Light (radius 48 px, intensity 1.5, hue 20°) for 0.1 s
- Followed by 4 secondary embers that arc downward (gravity 60 px/s²) over 0.4 s

**Explosion** (area-of-effect skills):
- Expanding ring: starts at 8×8 px, expands to 48×48 px over 0.15 s
- 16 particles burst from ring edge: 6×6 px teardrops, radial outward
- Ring texture: soft circular gradient with hard outer edge
- Flash: full-screen white overlay at 15% opacity for 1 frame (linked to hit-stop window, Section 5 hit-stop rules)

**Visual Identity Principle**: Elemental Shapes — fire is always teardrop, never round or square. Players recognize fire before they see the color.

#### 8.1.2 Ice

**Projectile trail**:
- 4 crystal dust particles per frame along trajectory
- Each crystal: 3×3 px hexagon (Section 3 shape), color `#88FFFF` to `#FFFFFF` over lifetime
- Lifetime: 0.5 s (lingers — ice stays in the air longer than fire)
- Fade: linear. Particles slow to 0 speed over lifetime (suspended dust feel).
- Renderer mode: Additive. No light.
- Particles linger at projectile path waypoints — trail builds up over time as a visible "path" the projectile traveled

**Impact**:
- Hexagonal shatter: 6 fragments, each 6×4 px shard of broken hexagon
- Direction: along hexagon's 6 natural bisectors (0°, 60°, 120°, 180°, 240°, 300°)
- Lifetime: 0.35 s. Speed: 80 px/s with 30 px/s² deceleration.
- Each fragment has a refractive white core line (1 px) — simulates ice catching light
- No point light (ice is cold — no glow)

**Freeze status** (enemy frozen):
- Frost crust overlay: renders on top of enemy sprite at 40% alpha
- Overlay texture: hexagonal crack pattern (tileable, 64×64)
- Overlay pulses: alpha cycles 40% → 55% → 40% at 1 Hz while frozen
- Edges of overlay have 4 icicle shards (8×2 px) that grow from sprite bounds outward by 4 px over 0.5 s then hold
- Overlay uses **sprite emissive channel** (Section 4.4), emission level 0.3

**Visual Identity Principle**: Elemental Shapes — ice is always hexagonal. The shatter pattern communicates "ice broke" without the player reading a debuff icon.

#### 8.1.3 Lightning

**Projectile trail** (teleport-step):
- Ghost echo: projectile teleports in 4-px steps at 60 Hz (appears as instant movement)
- Echo: a faded copy of the projectile sprite at 25% alpha remains at each step position
- Echo lifetime: 0.3 s. Fade: exponential drop.
- Maximum 3 echoes visible simultaneously
- Between echoes: 1-px-thin zigzag line (Section 3 zigzag, 60° angle turns) connecting positions
- Zigzag line lifetime: 0.15 s

**Impact**:
- Zigzag spread: 3–5 branches (random, weighted toward 4)
- Each branch: 2-px-thick zigzag line, length 24–48 px, random from impact point
- Branch lifetime: 0.2 s. Flash at branch tip on extension.
- 1 frame: white line overlay at full alpha, then fades to element color (`#AA88FF`) over remaining lifetime
- No point light (branches are self-illuminating via Additive renderer)

**Stun status** (enemy stunned):
- Electric cage overlay: renders on top of enemy sprite at 35% alpha
- Cage texture: 2-px-thick zigzag lines forming a loose ring around the enemy
- Cage rotates at 180°/s — creates visual motion even though enemy is frozen
- Spark particles: 2 per second, 2×2 px, spawn at cage edges, arc 8 px outward, 0.15 s lifetime
- Overlay uses sprite emissive channel, emission level 0.5

**Visual Identity Principle**: Elemental Shapes — lightning is always zigzag, never a straight line or arc. Even the stun cage is a series of angled turns.

#### 8.1.4 Void (Enemy)

**Projectile** (dark orb):
- 8×8 px orb with visible incomplete-circle trail — a circle missing a 90° wedge
- Trail: 4 ghost orbs at 30% alpha, each rotated by wedge position (+0°, +90°, +180°, +270° showing the gap in different places)
- Trail lifetime: 0.4 s. No fade — hard cutoff.
- Orb color: `#440033` (deep purple-black) with 1-px `#880066` rim
- Renderer mode: Additive. Attached 2D Point Light: radius 32 px, intensity 0.3, hue 300°

**Impact**:
- Void tear: expanding and contracting ring — starts at 4×4 px, expands to 32×32 px over 0.2 s, then contracts back to 0 over 0.15 s
- Ring texture: jagged edge (noise-displaced circle), color `#660044` to `#000000`
- 4 secondary particles: 3×3 px purple-black dots that spiral inward toward tear center, not outward
- No sound-linked flash (void impacts are quiet — Section 8.3 sound design reference)

**Corruption status** (zone corruption):
- Void seepage: dark purple vignette creeps in from screen edges when player is in corrupted zone
- Vignette: radial gradient (edge 60% opacity → center 0% opacity), hue 290°
- Seepage pulse: opacity cycles 30% → 60% → 30% at 0.5 Hz (slow, ominous)
- At maximum corruption: thin branching lines (1 px, 30% opacity) crawl from edges toward center like cracks
- Lines advance at 8 px/s, 3–5 lines visible at any time
- Overlay renders **above** gameplay layer but **below** UI layer (Section 6 UI rendering order)

**Visual Identity Principle**: Negative Space — void effects are defined by what's *missing* (incomplete circle, shrinking tear, edges closing in). The only element that pulls inward instead of exploding outward.

#### 8.1.5 Zone Memory Restoration

**Restoration particles** (zone-colored rising motes):
- Each mote: 2×2 px soft dot, zone's memory hue (unique per zone)
- Emission: 12 motes per second from each restored object
- Trajectory: float upward at 30 px/s with 4-px horizontal sine-wave wobble (±2 px amplitude, 2 Hz)
- Lifetime: 2.0 s. Fade-in: 0.3 s. Fade-out: 0.5 s at end.
- Motes rise to 64 px above object, then dissolve
- Light: no per-mote light (too many). One 2D Point Light per restoration zone, radius 80 px, intensity 0.8, motes' hue

**Visual Identity Principle**: Narrative Fragments — the rising motes echo the campfire memory motes from Section 1. Players subconsciously connect "motes rising = memory recovered."

#### 8.1.6 Synergy Hybrid VFX

When two elements combine (via hero skill synergy), the resulting VFX merges both shape languages:

| Synergy | Hybrid VFX | Duration | Unique Trait |
|---------|-----------|----------|--------------|
| Fire + Ice | Shatter-teardrop with hexagonal crack lines | 0.3 s | Teardrop splits along hexagon grid lines, 12 fragments total |
| Fire + Lightning | Zigzag fire streak with ember branch ends | 0.25 s | Each zigzag turn spawns a teardrop ember that arcs off independently |
| Ice + Lightning | Hexagonal electric burst with frozen branch pattern | 0.3 s | Zigzag branches freeze mid-extension, 6 branches locked at hexagon edges |
| Fire + Ice + Lightning | Elemental vortex: rotating ring (teardrop/hexagon/zigzag segments) | 0.5 s | 24 particles in ring, 8 per element, ring pulses 32→48→32 px radius |

**Implementation**:
- Hybrid VFX always uses both element colors at 100% saturation
- Hybrid VFX uses a separate 2D Point Light: intensity 2.0, radius 64 px, color transitions between both element hues at 5 Hz
- Hybrid VFX counts as ONE particle system toward the 3-system limit (Section 4)

**Visual Identity Principle**: Shape Language — synergy communicates *combination*. Players learn: "two shapes at once = two elements working together."

### 8.2 Hit Effects & Impact VFX

#### 8.2.1 Player Hits Enemy

**Contact flash**:
- 1 frame only (16.67 ms at 60 fps)
- 12×12 px circle, pure white, 50% opacity
- Position: exact hit point
- Renderer mode: Additive
- No scaling or movement — exact 1-frame hard flash

**Knockback dust**:
- 3 particles emitted in arc opposite to knockback direction
- Each particle: 4×4 px soft circle, color `#CCCCCC` at 40% alpha
- Trajectory: 45° cone opposite knockback vector, speed 40–60 px/s
- Lifetime: 0.2 s. Gravity: 80 px/s² downward
- Only emitted if knockback distance > 0 (contact-only hits skip dust)

**Visual Identity Principle**: Combat Readability First — the 1-frame white flash is the universal "hit confirmed" signal. The player does not need to see a damage number to know the attack landed.

#### 8.2.2 Enemy Hits Player

**Contact flash**:
- 1 frame only
- 12×12 px circle, red (`#FF0000`), 50% opacity
- Position: player center, not hit point (readability — player always sees it)
- Renderer mode: Additive

**Screen shake** (linked to Section 7.4 screen shake system):
- Magnitude: 2 px
- Frequency: 15 Hz
- Duration: 0.15 s
- Waveform: sine decay (prefer natural settle over mechanical stop)

**Visual Identity Principle**: Player Empathy — the red flash is a universal "you got hit" cue, paired with camera shake. The screen moves for you because you cannot move. The framestop + flash makes every hit feel consequential even at low health.

#### 8.2.3 Critical Hit

**Larger contact flash**:
- 2 frames (33.33 ms)
- 20×20 px circle, element color at 100% saturation, 60% opacity
- Outer ring: 28×28 px, 30% opacity, expands to 36×36 px over 2 frames then dissolves

**Sound-linked pulse ring**:
- Expanding ring from hit point, 2 px thick, element color
- Starts at 16×16 px, expands to 64×64 px over 0.3 s
- Ring expansion speed linked to hit SFX attack transient (programmer: sync to audio timeline)
- Fade: sharp at end — ring holds full opacity for 80% of lifetime then drops to 0 in final 20%

**Visual Identity Principle**: Weight & Consequence — crits are bigger, longer, and louder. The expanded flash + ring pulse tells the player "this one mattered" before the damage number arrives.

#### 8.2.4 Hit-Stop Visual

During hit-stop freeze frames (Section 5 hit-stop rules: 2 frames basic, 4–6 frames skills):

**Element overlay**:
- Full-screen overlay at hit point region (48×48 px area centered on hit), element color at 20% opacity
- Overlay locks to hit point position — does not move during freeze
- Overlay uses **Additive** renderer mode

**White impact flash**:
- 0.5 px border around overlay region, pure white
- Appears on first freeze frame only, then fades over remaining freeze frames
- Purpose: gives the freeze a "snapshot" feel — the frame is frozen mid-brightest-moment

**Visual Identity Principle**: Weight & Consequence — hit-stop without visual feedback would feel like a lag spike. The element overlay + flash communicates "time stopped because this mattered."

### 8.3 Collection VFX

#### 8.3.1 Lore Fragment Collect

**Zone-color ripple**:
- Expanding ring: 12×12 px → 24×24 px over 0.5 s
- Color: zone's memory hue (Section 7.6.4 lore fragment glow)
- Ring thickness: 2 px at start, thinning to 0.5 px at end
- Renderer mode: Additive
- Only one ripple per collect (no multiple rings)

**Fragment ghost**:
- Faded copy of the lore fragment sprite
- Alpha: 40% at collect moment, fades to 0% over 1.0 s
- Position: drifts upward 16 px over lifetime (gentle float)
- Rotation: no rotation — ghost stays oriented to original sprite

**Visual Identity Principle**: Narrative Fragments — the ghost makes the fragment feel like it was "a memory" that lingers a moment before fully dissolving into the player.

#### 8.3.2 Memory Shard Collect

**Spiral to counter**:
- Shard sprite shrinks (12×12 → 4×4) and spirals toward the memory counter UI position (Section 6.5 top bar)
- Spiral: 3 full rotations over 0.3 s, radius decreases 20→0 px
- Path: arcs toward counter with slight curve, not straight line

**Sparkle trail**:
- 4 particles per shard, 2×2 px, zone memory hue
- Emitted along spiral path, trail behind shard
- Lifetime: 0.2 s. Speed follows shard speed.

**Visual Identity Principle**: Collection Satisfaction — the spiral-to-counter animation mimics a coin-magnet in action games. The sparkle trail communicates "this was valuable" as it leaves the play field.

#### 8.3.3 Rift Essence Collect

**Element-colored explosion**:
- 8 particles burst from essence position
- Each particle: 4×4 px soft circle, hero's element color (100% saturation)
- Radial burst: random direction, speed 80–120 px/s
- Lifetime: 0.5 s. Gravity: 40 px/s² (particles arc down after burst)

**Point light flash** (if 3-light budget permits):
- 2D Point Light: radius 32 px, intensity 1.0, element hue, 0.15 s duration

**Visual Identity Principle**: Elemental Shapes — essence is the player's resource, so its VFX uses the player's element. The burst communicates "this is now yours."

#### 8.3.4 Health Pickup Collect

**Warm amber pulse**:
- Expanding ring: 8×8 → 20×20 px over 0.3 s
- Color: `#FF8800` at 50% → 0% opacity
- Two pulses staggered: second pulse starts at 0.15 s

**Heart-shaped burst**:
- 4 particles: 4×4 px, `#FF4444`, arranged in heart silhouette at pickup point
- Particles expand outward 12 px over 0.2 s then dissolve
- One particle per heart quadrant (top-left, top-right, bottom-left, bottom-right)

**Visual Identity Principle**: Player Empathy — health pickups use warm, inviting colors (amber, soft red) that contrast with combat's cool-black void. The heart shape is universally readable.

### 8.4 Restoration VFX

#### 8.4.1 Single Fragment Restore (Partial Zone Heal)

**Light fills crack from one side**:
- Crack (on environment sprite) fills with warm light from one edge toward the other
- Light fill: pixel-stepped 4-band gradient (0%, 33%, 66%, 100%), zone memory hue
- Fill direction: left-to-right (matches light sweep direction in Section 7.6.1)
- Duration: 1.5 s
- Implementation: shader parameter `_FillAmount` animates 0→1 on the crack overlay material (Section 7.6.1 cookie uses same 4-band gradient)

**Wave**:
- Radial wave emanates from fragment position
- Wave: 1-px-thick ring, zone memory color, 30% opacity
- Expands from 8 px to 48 px radius over 1.5 s
- Wave is subtle — lower opacity than combat VFX. Restoration is calm.

**Visual Identity Principle**: Consequence Language — the fill direction matches the zone restore sweep (Section 7.6.1). Players learn: "light fill from left = something was repaired."

#### 8.4.2 Zone Boss Defeat (Full Restore)

**Saturation wave**:
- Wave travels from boss death position across entire screen
- Zone's true color palette floods in — desaturated void environment saturates to 100% over 2 s
- Implementation: post-process saturation parameter animated 0% → 100% via Timeline (not code — use Timeline for precise duration control)

**Ghost-construct pieces assemble**:
- 6–8 ghostly construct pieces (buildings, objects from the zone's memory) appear at 20% alpha
- Pieces fly in from off-screen edges, each on a 0.5 s delayed start
- Each piece slides to its final position over 1.0 s with smooth damp (not linear — overshoot by 4 px then settle)
- Once assembled, pieces fade up to 60% alpha over 0.3 s (they do not go to 100% — ghost remains ghostly)
- Pieces are silhouettes in zone memory hue, no detail — this is a *hint* of what the zone was

**Visual Identity Principle**: Narrative Fragments — the ghost constructs are the most explicit memory VFX. Players see what *was* here, even if only as a silhouette. The 2 s restore sequence is the game's emotional payoff moment.

#### 8.4.3 Hero's Zone Restore Emote

Each hero performs a unique emote on zone full restore (see Section 5.1 characteristics):

| Hero | Emote VFX | Duration | Particle Behavior |
|------|-----------|----------|-------------------|
| Pyra | Flame pillar rises behind, 64 px tall | 1.5 s | 12 embers spiral up pillar, 4/frame, 0.8 s lifetime |
| Glaci | Ice crystal forms at hero feet, 16×16 px, then shatters | 1.2 s | Shatter: 8 hexagonal fragments, radial, 0.4 s lifetime |
| Volt | Electric arc circles hero 3 times at 32 px radius | 1.0 s | Arc: 2-px zigzag line, 3 branches, 0.3 s each rotation |

**Implementation**: Emote VFX spawns on player character object and follows hero position during animation. Emote cancels on player movement input (hero can cancel the flourish to keep playing).

**Visual Identity Principle**: Character Identity — each hero's restoration VFX uses their element in a *personal* way, not a generic burst. This reinforces hero identity (Section 5.1) every time a zone is restored.

### 8.5 UI VFX

Section 6 established frame timing and animation curves. These VFX are the particle / shader components that accompany those animations.

#### 8.5.1 Button Press Ripple

- Expanding ring from press point: starts at 4×4 px, expands to button width over 0.23 s
- Ring thickness: 2 px, thinning to 0 px at end
- Color: parchment gold (Section 4.2 UI palette, gold `#D4A843`) at 60% → 0% opacity
- Ring conforms to button shape (rounded rectangle mask, not a perfect circle)
- Implementation: `RectMask2D` on ring material, UV offset animated

#### 8.5.2 Card Hover Glow

- Element-colored glow behind draft card, renders below card sprite
- Glow: 48×48 px soft radial gradient, element color at 30% opacity
- Glow fades in over 0.1 s on hover start, fades out over 0.15 s on hover end
- Glow follows card position with 0.05 s smooth damp (slight float)
- No additional particles — glow is a single sprite

#### 8.5.3 Card Pick-Up Particle Burst

- 8 particles burst from card center on pick-up
- Each particle: 4×4 px soft circle, card's element color
- Radial burst: random direction, speed 60–100 px/s
- Lifetime: 0.3 s. Fade: linear.
- No light (UI layer has no real-time lights — Section 7.1)

#### 8.5.4 Menu Transition VFX

Three transition types, matching Section 6.6 menu flow:

**Ink-stamp squash**:
- Current panel shrinks vertically (scale Y 1.0 → 0.0) over 0.15 s
- At squash midpoint, 2 particles (6×6 px, ink-black `#1A1A1A`) appear at menu title position
- Particles expand to 12×12 px and fade over 0.1 s

**Parchment-tear shader**:
- Transition between menu panels uses a shader-based tear
- Shader parameter `_TearPosition` scrolls left-to-right across screen over 0.3 s
- Left of tear: new panel visible. Right of tear: old panel.
- Tear edge: 4-px band of procedural noise (1-px texels, 50% white, 50% transparent)
- Implementation: custom `ParchmentTear` shader, URP-compatible, `Queue=Transparent`

**Rune-ignite**:
- Panel's decorative rune elements (Section 6.4) ignite one at a time on entry
- Each rune: emission ramps 0.0 → 1.0 over 0.15 s, stagger 0.05 s per rune
- 1 spark particle per rune (2×2 px, gold) emits at ignition moment, arcs 8 px upward, 0.2 s lifetime

**Visual Identity Principle**: Material Authenticity — every UI transition communicates "this is a physical object" (paper, ink, parchment). No digital-style fades or slides.

#### 8.5.5 Notification Toast Entry

**Paper slide**:
- Toast slides in from screen top on a parchment-gold trail
- Trail: 4 ghost copies of toast at 20% alpha, spaced 4 px apart behind toast
- Slide curve: ease-out (0.3 s) for entry, ease-in (0.2 s) for exit

**Dust puff**:
- 4 particles (3×3 px, `#E8D5A3` at 30% opacity) puff from toast center on entry
- Particles expand 8 px outward over 0.2 s, fade to 0%
- One-time emission (no looping — toast sits quietly once on screen)

**Visual Identity Principle**: Material Authenticity — the dust puff and paper slide make notifications feel like a physical note being placed on a desk, not a digital popup.

### 8.6 Particle Budgets & Performance

All particle systems must operate within URP's 2D renderer constraints. These budgets are hard limits — performance testing must verify compliance on minimum-spec devices.

#### 8.6.1 Global Limits

| Metric | Limit | Notes |
|--------|-------|-------|
| Max simultaneous particles | 200 | All systems combined — measure in worst-case combat (boss + 6 enemies + player skills) |
| Max active particle systems | 12 | Includes trails, continuous emissions, and one-shot impacts |
| Max particle lifetime | 3.0 s | Hard cap — any system with Lifetime > 3 s must use a looping system with cull |
| Max 3D mesh particles | 0 | 2D only — no mesh particles in URP 2D Renderer |
| Custom vertex streams | Not used | Default particle renderer only |

#### 8.6.2 Per-System Limits

| VFX | Max Particles | Max Systems Active | Notes |
|-----|-------------|-------------------|-------|
| Fire projectile trail | 60 | 3 | 6/frame × 0.3 s = ~18 per trail, 3 simultaneous trails |
| Fire impact / explosion | 24 | 3 | 16 burst + 8 embers |
| Ice projectile trail | 40 | 3 | 4/frame × 0.5 s lingering = ~20 per trail |
| Ice impact / shatter | 8 | 3 | 6 fragments + 2 reserve |
| Lightning ghost echo | 20 | 2 | 3 echoes × ~6 lines |
| Lightning impact | 8 | 3 | 5 branches + 3 reserve |
| Void projectile trail | 10 | 4 | 4 ghosts + orb per projectile |
| Void impact | 8 | 3 | 4 secondary + 4 reserve |
| Zone restoration motes | 60 | 1 | 12/s × 2 s lifetime = ~24 active, budget allows 60 for dense zones |
| Hit effects (all types) | 12 | 3 | Flash + dust + ring per impact |
| Collection VFX | 20 | 3 | Ripple + ghost + spiral per collect |
| UI VFX | 16 | 2 | Glow + burst + sparks per transition |

**Total worst-case calculation**: Fire (60+24) + Ice (40+8) + Lightning (20+8) + Void (10+8) + Motes (60) + Hit (12) + Collect (20) + UI (16) = **286 peak**. Systems that exceed the 200 global limit must cull lowest-priority particles first:
1. Priority 1 (must render): Hit effects, player impact VFX
2. Priority 2 (render if budget available): Elemental trails, enemy impact VFX
3. Priority 3 (cull first): Collection VFX sparkles, zone restoration motes beyond 40

**Implementation**: Particle system script checks `ParticleSystem.particleCount` before emitting. If global count > 180, skip Priority 3 emissions. If > 195, skip Priority 2 also.

#### 8.6.3 Texture Atlasing

- All particle textures on a single atlas: max 2048×2048 px
- Atlas includes: teardrop (32×32), hexagon (32×32), zigzag line (64×16), soft circle (16×16), ring (64×64), hex crack (64×64), electric cage (64×64), void orb (32×32), void jagged-ring (64×64), mote (8×8), rune-spark (16×16), gold-ring (32×32)
- Atlas format: RGBA Compressed (ASTC 6×6 for mobile, DXT5 for desktop)
- All particle materials reference the atlas with `_MainTex` set via material property block (no material instances)
- UV rect per particle type: defined in `ParticleAtlas.asset` ScriptableObject — programmatically set via `TextureSheetAnimation` module

#### 8.6.4 Overdraw Management

In URP 2D, transparent particles render front-to-back. Overdraw is the primary performance risk.

**Rules**:
- No more than **3 layers** of transparent particles in any screen region
- All additive particles render in a single draw call layer (sorted by material, not distance)
- Distance sorting disabled for additive particles (they sort by queue, not Z)
- Non-additive particles (e.g., UI dust puff at 30% opacity) use `Queue=Transparent+1` to separate from additive layer

**Per-scene validation**:
- Frame Debugger: verify `DrawMesh` calls for particles ≤ 12 per frame
- RenderDoc: capture a 3-second combat sequence, verify no pixel shaded more than 3 times by particle draws
- Profiler: `Gfx.WaitForPresent` time from particles must not exceed 1.0 ms on target spec

**Visual Identity Principle**: Performance Is Polish — overdraw management is not an optimization task, it is a design constraint. VFX artists must design within 3 layers. If a VFX needs a fourth layer, the design brief is wrong, not the renderer.

---

**Section 8 Acceptance Criteria** (for implementation):
1. Every VFX in Section 8.1–8.5 is implemented in a test scene with documented parameters
2. No VFX uses purely decorative particles — each maps to a gameplay signal identifiable in Frame Debugger
3. Global particle count never exceeds 200 in any combat scenario (verified in Profiler)
4. No single particle system exceeds its per-system budget from Section 8.6.2
5. All particle textures on a single atlas (max 2048×2048) verified in Asset Auditor
6. Overdraw ≤ 3 layers in any screen region (verified in RenderDoc capture)
7. Particle GPU time < 1.0 ms on target spec (measured in Profiler)
8. Priority culling system (Section 8.6.2) functional: culls lowest-priority VFX when approaching budget limits
9. Hybrid synergy VFX (Section 8.1.6) all implemented and verified

---

## Technical Art Pipeline & Asset Management

**Status**: Draft
**Scope**: Naming conventions, pipeline steps, folder structure, import settings, atlas rules, animation workflow, shader management, and version control for all art assets.
**Audience**: Technical artists, programmers, and artists producing assets for production.

This section defines the production pipeline that every art asset follows from creation tool to in-game rendering. A new artist joining the project should be able to read this section and produce a file that passes automated review.

---

### 9.1 Naming Conventions

All file and asset names use **`snake_case`**. Only lowercase letters, digits, and underscores. No spaces, no hyphens, no uppercase.

#### 9.1.1 Sprites (individual frames)

```
{type}_{entity}_{variant}_{state}_{frameNumber}.png
```

| Component | Values | Examples |
|-----------|--------|----------|
| `type` | `hero`, `enemy`, `prop`, `ui`, `vfx`, `env` | `hero`, `enemy`, `ui` |
| `entity` | `pyra`, `glaci`, `volt`, `voidspawn`, `frostmimic`, `riftfragment` | `pyra`, `voidspawn` |
| `variant` | Element or zone or skin name — `fire`, `ice`, `lightning`, `void`, `ruin_a`, `basic` | `fire`, `ruin_a` |
| `state` | Animation state — `idle`, `walk`, `attack01`, `hit`, `death`, `restore` | `idle`, `attack01` |
| `frameNumber` | Zero-padded 3-digit frame index | `000`, `001`, `042` |

**Examples**:
- `hero_pyra_fire_idle_000.png` — Pyra's fire-element idle frame 0
- `enemy_voidspawn_basic_walk_005.png` — Basic void-spawn walk frame 5
- `prop_riftfragment_void_idle_000.png` — Rift fragment idle
- `vfx_fire_teardrop_particle_000.png` — Fire teardrop particle texture
- `env_tile_ruin_a_floor_000.png` — Ruin zone floor tile
- `ui_icon_health_rune_000.png` — Health rune icon

**Corrupted vs. restored variants**: Use `corrupted` or `restored` as the variant on environment/prop sprites. Both variants share the same frame count and layout, enabling sprite-swap during zone restoration (Section 3.2).

#### 9.1.2 Textures (materials, particles, shader inputs)

```
t_{purpose}_{variant}_{size}.png
```

| Component | Examples |
|-----------|----------|
| `purpose` | `particle_teardrop`, `particle_hex`, `noise_cloud`, `gradient_circle`, `light_glow`, `mask_circle` |
| `variant` | `fire`, `ice`, `white`, `default` |
| `size` | Width in pixels — `16`, `32`, `64`, `128`, `256` |

**Examples**:
- `t_particle_teardrop_32.png` — 32×32 teardrop particle texture
- `t_noise_cloud_64.png` — 64×64 noise cloud for shader effects
- `t_light_glow_128.png` — 128×128 radial glow for 2D lights

#### 9.1.3 Materials

```
m_{surface}_{variant}.mat
```

| Component | Examples |
|-----------|----------|
| `surface` | `ruin_stone`, `hero_pyra`, `enemy_voidspawn`, `ui_parchment`, `vfx_fire`, `vfx_ice` |
| `variant` | `corrupted`, `restored`, `default` (omit for single-variant) |

**Examples**:
- `m_ruin_stone_corrupted.mat` — Corrupted stone material
- `m_hero_pyra.mat` — Pyra's sprite material (unlit sprite)
- `m_vfx_fire_additive.mat` — Fire VFX with additive blend
- `m_ui_parchment_panel.mat` — Parchment panel material (custom shader)

#### 9.1.4 Shaders

```
sh_{effect}.shader
```

And companion files:
- `sh_{effect}.shadergraph` — Shader Graph variant (URP)
- `sh_{effect}_VARIANT_NAME.shadervariants` — Variant collection

**Examples**:
- `sh_parchment_tear.shader` — Parchment-tear transition shader
- `sh_emission_overlay.shader` — Elemental emission overlay
- `sh_corruption_overlay.shader` — Void corruption overlay
- `sh_rim_light.shader` — Rim lighting for heroes and elites

#### 9.1.5 VFX Prefabs

```
vfx_{element}_{action}.prefab
```

| Component | Examples |
|-----------|----------|
| `element` | `fire`, `ice`, `lightning`, `void`, `restore`, `synergy_fire_ice`, `synergy_ice_lightning`, `synergy_lightning_fire` |
| `action` | `explosion`, `hit`, `trail`, `aura`, `projectile`, `restore_wave`, `death`, `spawn` |

**Examples**:
- `vfx_fire_explosion.prefab` — Fire explosion on enemy hit
- `vfx_ice_projectile.prefab` — Ice projectile traveling VFX
- `vfx_synergy_fire_ice_shatter.prefab` — Fire+Ice shatter hybrid (Section 8.1.6)
- `vfx_restore_zone_wave.prefab` — Zone restoration color wave (Section 4 mood state)

#### 9.1.6 Animation Controllers

```
ac_{entity}_{type}.controller
```

| Component | Examples |
|----------|----------|
| `entity` | `hero`, `enemy_basic`, `enemy_elite`, `boss`, `prop` |
| `type` | `combat`, `idle`, `fx`, `ui` |

**Examples**:
- `ac_hero_combat.controller` — Hero shared combat state machine
- `ac_enemy_basic.controller` — Basic enemy state machine
- `ac_boss_voidtitan.controller` — Boss-specific controller

#### 9.1.7 Sprite Atlases

```
sa_{zone_or_type}.spriteatlas
```

**Examples**:
- `sa_characters.spriteatlas` — All heroes + NPCs
- `sa_enemies_basic.spriteatlas` — Basic enemies
- `sa_env_ruins.spriteatlas` — Ruin zone environment tiles
- `sa_ui.spriteatlas` — All UI elements
- `sa_vfx.spriteatlas` — Particle textures and VFX sprites

#### 9.1.8 Source Art Files

```
{entity}_{variant}.aseprite
```

**Examples**:
- `pyra_fire.aseprite` — Pyra's fire-element sprite sheet source
- `glaci_ice.aseprite` — Glaci's ice-element sprite sheet source
- `voidspawn_basic.aseprite` — Basic void-spawn source
- `ruin_tileset.aseprite` — Environment tileset source

---

### 9.2 File Formats & Import Settings

#### 9.2.1 Source Formats

| Asset Type | Source Format | Delivery Format | Notes |
|-----------|---------------|-----------------|-------|
| Character sprites | `.aseprite` | `.png` (individual frames) | Aseprite native if available; PNG export for non-Aseprite artists |
| Environment tiles | `.aseprite` or `.png` | `.png` | Single tiles or tile strips |
| UI elements | `.aseprite` or `.png` | `.png` | SVG source → rasterize at 1×, 2×, 3× |
| Particle textures | `.aseprite` or `.png` | `.png` | Power-of-two dimensions required |
| Materials | — | `.mat` | Created in Unity, not from DCC |
| Shaders | `.shader` + `.shadergraph` | `.shader` | Shader Graph → code conversion is manual; keep both |
| 3D scenes / references | `.psd`, `.tga` | — | Reference only — not imported into Unity |
| Animation | `.aseprite` tags → `.png` frames | `.png` + `.anim` | One PNG per layer per animation state |

#### 9.2.2 Sprite Import Settings (Unity)

All pixel-art sprites must use these settings. Do not deviate without written approval from the technical lead.

| Setting | Value | Rationale |
|---------|-------|-----------|
| Texture Type | `Sprite (2D and UI)` | Standard for 2D pixel art |
| Sprite Mode | `Multiple` | Each frame is a separate sprite in the same texture |
| Pixels Per Unit | `16` | 1 tile = 16 px (Section 4.1 reference resolution) |
| Mesh Type | `Full Rect` | Tight mesh causes sorting artifacts with pixel art; Full Rect guarantees correct per-pixel alignment |
| Filter Mode | `Point (no filter)` | Nearest-neighbor — no blur on pixel art |
| Compression | `None` | Pixel art textures must be lossless |
| Compression (mobile atlas) | `ASTC 6×6` | Applied at build time to atlas textures only — never to individual source sprites |
| Max Size | See table below | Per asset type budget |
| Format | `RGBA 32 Bit` | Full color fidelity for pixel art |
| Alpha Source | `Input Texture Alpha` | Alpha comes from file, not grayscale |
| Read/Write | `Disabled` | Enable only for runtime texture manipulation (rare) |
| Mip Maps | `Disabled` | 2D pixel art does not use mip maps (PPU is constant) |
| Wrap Mode | `Clamp` | Prevents edge bleeding at atlas borders |

**Max Size by asset type:**

| Asset Type | Max Size | Exception |
|-----------|----------|-----------|
| Character sprites | 512×512 | Boss sprites: 1024×1024 |
| Enemy sprites | 256×256 | Elite enemies: 512×512 |
| Environment tiles | 256×256 | Tile sheets: 2048×2048 |
| UI elements | 256×256 | Full-screen overlays: 1024×512 |
| Particle textures | 64×64 | Background VFX: 128×128 |
| All atlas textures | Per atlas budget (Section 9.5.4) | — |

#### 9.2.3 Pivot Points

| Sprite Category | Pivot | Why |
|----------------|-------|-----|
| Characters (heroes, enemies, NPCs) | `Bottom-center` (0.5, 0) | Ground alignment — character feet touch the tile grid |
| Projectiles | `Center` (0.5, 0.5) | Rotation origin is the projectile center |
| VFX particles | `Center` (0.5, 0.5) | Particles scale and rotate from center |
| Environment tiles | `Bottom-center` (0.5, 0) | Tile grid alignment — snap to tile Y=0 |
| UI elements | `Top-left` (0, 1) | Standard screen-space coordinate origin |
| Icon glyphs | `Center` (0.5, 0.5) | Centered in the icon frame |

**Implementation**: Apply pivot points in the Sprite Editor window when slicing sprites. Store per-sprite overrides in `.asset` files, not in the texture meta file (to avoid merge conflicts).

#### 9.2.4 Sprite Slicing (Sprite Editor)

- Use **Grid by Cell Count** for sprite sheets with uniform frame sizes.
- Use **Automatic Slicing** only for irregular VFX textures (single-frame particles, noise textures).
- Name slices according to Section 9.1 naming convention.
- Set pivot per slice using the category rules above (Section 9.2.3).
- After slicing, verify each sprite's `Pixels Per Unit = 16` in the Inspector (this is the global default, but slicing can override per-sprite).

---

### 9.3 Folder Structure

All custom art assets live under `Assets/_TinyRift/Art/`. **No art assets outside this path.** The template's built-in art (Assets/BulletHellTemplate/) is never modified (per Agent Rule 1).

```
Assets/_TinyRift/Art/
├── Characters/
│   ├── Pyra/                # Section 5 hero roster — Pyra (fire)
│   │   ├── Sprites/         # .png frame exports
│   │   ├── Animations/      # Clip + controller overrides
│   │   └── Source/          # .aseprite files
│   ├── Glaci/               # Glaci (ice)
│   ├── Volt/                # Volt (lightning)
│   └── NPCs/                # Friendly NPCs (camp vendors, lore givers)
│
├── Enemies/
│   ├── Basic/               # Void-spawn, elemental mimics (basic tier)
│   │   ├── Sprites/
│   │   ├── Animations/
│   │   └── Source/
│   ├── Elite/               # Elemental mimics (elite tier)
│   │   ├── Sprites/
│   │   ├── Animations/
│   │   └── Source/
│   └── Boss/                # Zone bosses, void titans
│       ├── Sprites/
│       ├── Animations/
│       └── Source/
│
├── Environment/
│   ├── Zones/               # Per-zone environment art
│   │   ├── Ruins/           # Ruin zone tileset
│   │   ├── Voidheart/       # Voidheart zone tileset
│   │   └── Shared/          # Common tiles (floor, wall, edge)
│   └── Terrain/             # Terrain tiles, ground sheets
│
├── Props/
│   ├── RiftFragments/       # Collectible lore fragments (Section 5.5)
│   ├── Obstacles/           # Destructible cover, void cysts
│   └── Decorations/         # Non-interactive world dressing
│
├── UI/
│   ├── HUD/                 # Health bar, minimap, skill icons
│   ├── Icons/               # Element icons, synergy icons, status icons
│   ├── Cards/               # Draft card backgrounds, rare frames
│   ├── Panels/              # Parchment backgrounds, inventory panels
│   ├── Fonts/               # Rune glyph sprites (not TTF font files — Section 6.2)
│   └── Effects/             # UI-specific VFX (selection glow, card flip)
│
├── VFX/
│   ├── Elements/            # Particle textures per element
│   │   ├── Fire/            # teardrop, ember, smoke
│   │   ├── Ice/             # hexagon, crystal, frost
│   │   ├── Lightning/       # zigzag, arc, spark
│   │   └── Void/            # tendril, pulse, corruption
│   ├── HitEffects/          # Impact sparks, shatter debris, status VFX
│   └── Environment/         # Ambient dust, waterfall mist, zone-specific VFX
│
├── Materials/               # All .mat files (flat, no subfolders)
├── Shaders/                 # All custom shaders + Shader Graph files
│   └── Fallbacks/           # Fallback shaders for unsupported platforms
│
├── Atlases/                 # Sprite Atlas assets
├── Animation/               # Shared animation clips + base controllers
└── Reference/               # Concept art, moodboards, style guides (excluded from build)
```

**Important**: The `Reference/` folder must be excluded from game builds. Add this in Project Settings → Editor → Asset Serialization (exclude via folder-based build stripping) or via a custom script `Assets/_TinyRift/Editor/ExcludeReferenceFromBuild.cs`.

---

### 9.4 Sprite Pipeline: Aseprite → Unity

#### 9.4.1 Layer Export Rules

| Aseprite Layer | Unity Sprite | Notes |
|---------------|-------------|-------|
| `body` (merged) | Character sprite (main) | All body sub-layers merged into one layer before export |
| `element_effect` | Separate overlay sprite | Used for elemental glow, rune pulse — applied as a second sprite in Unity (additive blend material) |
| `weapon` | Merged into body or separate | If the weapon animates independently, export as a separate sprite; otherwise merge into body |
| `shadow` | Separate sprite | Ground shadow — rendered below character with `Sorting Order -1` |
| `voice` (reference only) | Not exported | Animation notes, dialog cues — strip from final export |

**Export workflow** for each animation state:
1. Aseprite frame tags define each animation state (idle, walk, attack01, hit, death).
2. Per animation state, export each relevant layer as individual frame PNGs.
3. Naming: `{entity}_{variant}_{state}_{frameNumber}.png` (Section 9.1.1).
4. Import into Unity and slice using Grid by Cell Count in Sprite Editor.
5. Create Animation clip from sliced sprites (drag frames into Timeline at 1:1 frame mapping).

#### 9.4.2 Individual Frames vs. Sprite Sheet

**Use individual frame PNGs, not sprite sheets.**

Rationale (URP 2D specific):
- URP 2D's `SpriteRenderer` can swap individual sprites without loading a full sheet
- Individual frames enable per-frame pivot overrides (important for animation precision)
- Per-frame compression control (exempt action frames from atlas compression)
- Simpler diff in version control (changing one frame touches one file, not the whole sheet)

Exception: **Background / ambient VFX textures** that never animate per-frame can stay as sprite sheets or single-frame textures.

#### 9.4.3 Aseprite Frame Tag to Unity Animation Mapping

| Aseprite Tag | Unity Animation Clip | Events |
|-------------|---------------------|--------|
| `idle` | `{entity}_idle.anim` | None |
| `walk` | `{entity}_walk.anim` | Footstep sound at mid-stride frames |
| `attack01` | `{entity}_attack01.anim` | Hit frame event (frame where damage is dealt); VFX spawn event |
| `attack02` | `{entity}_attack02.anim` | Same as above |
| `hit` | `{entity}_hit.anim` | Damage flash event; screen shake trigger |
| `death` | `{entity}_death.anim` | VFX spawn; despawn event at animation end |
| `restore` | `{entity}_restore.anim` | Color bloom event; sound effect |
| `spawn` | `{entity}_spawn.anim` | VFX spawn at entry; sound effect |

#### 9.4.4 Reference Image Handling

- Reference images (concept art, mood boards, style guides) go in `Art/Reference/`.
- Do NOT import reference images into Unity scenes. They stay outside the game build.
- Use `.jpg` for large reference images (photographs, environment concepts).
- Use `.png` for pixel-art reference (character concepts, color studies).
- Add `Art/Reference/**` to the exclusion list in build settings (Section 9.3).

---

### 9.5 Atlas Packing Rules

#### 9.5.1 What Goes in Each Atlas

| Atlas Asset | Contents | Max Size | Includes |
|------------|----------|----------|----------|
| `sa_characters.spriteatlas` | All hero sprites (Pyra, Glaci, Volt + future) + NPCs | 1024×1024 | All animation frames per hero |
| `sa_enemies_basic.spriteatlas` | Basic enemy sprites | 1024×1024 | Void-spawn, elemental mimics (basic) |
| `sa_enemies_elite.spriteatlas` | Elite enemy sprites | 1024×1024 | Elite elemental mimics |
| `sa_enemies_boss.spriteatlas` | Boss sprites | 2048×2048 | One boss per zone — separated for size |
| `sa_env_ruins.spriteatlas` | Ruin zone tile set | 2048×2048 | All tiles + corrupted/restored variants |
| `sa_env_voidheart.spriteatlas` | Voidheart zone tile set | 2048×2048 | All tiles + variants |
| `sa_env_shared.spriteatlas` | Shared environment tiles | 2048×2048 | Generic floor, wall, edge tiles |
| `sa_ui.spriteatlas` | All UI/HUD elements | 512×512 | Panels, icons, rune glyphs, card frames |
| `sa_vfx.spriteatlas` | All VFX particle textures | 2048×2048 | Elemental particle textures, hit spark textures |

#### 9.5.2 Sprite Atlas vs. Manual Atlas

**Use Unity's Sprite Atlas** (`Window → 2D → Sprite Atlas`) for all atlases. Do NOT create manual atlases (single large PNG imported as one sprite) — Unity's Sprite Atlas manages padding, bleeding, and variant swapping automatically.

| Feature | Unity Sprite Atlas | Manual Atlas |
|---------|-------------------|-------------|
| Automatic padding | Yes (configurable) | Manual |
| Variant swapping (Section 5.5) | Yes (change source texture, atlas rebuilds) | Manual reimport |
| Build-time compression | Yes (per-platform override) | Manual per-texture |
| Per-sprite pivot | Preserved from source | Lost — single pivot per atlas |
| Sorting layers | Per-sprite, preserved | Per-texture only |

Manual atlases are **only** acceptable for:
- Very large single textures (noise textures, gradient ramps) that aren't multiple sprites
- Runtime-generated textures (render targets, camera captures)

#### 9.5.3 Packing Tag Naming

Packing tags must match the Atlas asset naming without the `sa_` prefix:

| Atlas Asset | Packing Tag |
|------------|------------|
| `sa_characters.spriteatlas` | `characters` |
| `sa_enemies_basic.spriteatlas` | `enemies_basic` |
| `sa_env_ruins.spriteatlas` | `env_ruins` |
| `sa_ui.spriteatlas` | `ui` |
| `sa_vfx.spriteatlas` | `vfx` |

Set `Sprite → Packing Tag` in the Inspector for every sprite that belongs in an atlas. If a sprite has no packing tag, it will not be included in any atlas and will render as a separate draw call.

#### 9.3.4 Atlas Max Sizes (repeated from 9.5.1 for reference)

| Platform | Character Atlas | Environment Atlas | UI Atlas | VFX Atlas |
|----------|----------------|-------------------|----------|-----------|
| Standalone (PC/Mac/Linux) | 2048×2048 | 2048×2048 | 1024×1024 | 2048×2048 |
| Mobile (Android/iOS) | 1024×1024 | 2048×2048 | 512×512 | 1024×1024 |

Mobile variants use the same source sprites but are repacked at build time via platform-specific Sprite Atlas overrides.

#### 9.5.4 Variant Handling

**Corrupted and restored variants** of the same asset (Section 3.2, Section 5.5) go in the **same Sprite Atlas**. Unity's Sprite Atlas supports variant swapping by replacing the source texture — the atlas rebuilds automatically and all `SpriteRenderer` references remain valid.

Rule: If an asset exists in both `corrupted` and `restored` states, both variants must:
- Have identical sprite counts and frame sizes (same grid slice)
- Use the same packing tag
- Live in the same subfolder (e.g., `env_tile_ruin_a_corrupted_000.png` and `env_tile_ruin_a_restored_000.png`)

This guarantees that the runtime zone-restoration script can swap sprites one-to-one without re-slicing.

#### 9.5.5 Atlas Padding & Bleed

| Setting | Value | Why |
|---------|-------|-----|
| Padding | `4 pixels` | Prevents edge bleeding with Point filtering |
| Bleed | `Enabled` | Expands edge pixels into padding — prevents transparent borders on rotated sprites |
| Tags are packed into atlas based on | `Packing Tag` | Using the tag names from Section 9.5.3 |

---

### 9.6 Animation Pipeline

#### 9.6.1 From Aseprite Frame Tags to Unity Animation Clips

1. **Author in Aseprite**: Create frame tags for each animation state (Section 9.4.3). Tag names must match animation state names.
2. **Export frames**: Individual PNGs per state per layer (Section 9.4.2).
3. **Import to Unity**: Drop into `Art/Characters/{entity}/Sprites/` (or matching folder per Section 9.3).
4. **Slice in Sprite Editor**: Grid by Cell Count, set pivot (Section 9.2.3), name slices.
5. **Create Animation clip**: Select all frames for a state, drag into empty Animation clip window. Unity creates the keyframes at 1 frame per sprite.
6. **Set sample rate**: Animation clips use the Aseprite source frame rate (typically 12 fps for pixel-art characters). Use `Animation → Sample Rate` = 12. Do not use 30 or 60 fps for pixel-art animations — each sprite is one frame.
7. **Add events**: Hit frames, sound cues, VFX spawns (Section 9.6.5).

**Per-hero animation budget** (from Section 5.2.1):

| State | Frames | FPS | Duration |
|-------|--------|-----|----------|
| Idle | 4 | 12 | 0.33 s |
| Walk | 6 | 12 | 0.50 s |
| Attack 01 | 4 | 12 | 0.33 s |
| Attack 02 | 4 | 12 | 0.33 s |
| Hit/Stagger | 2 | 12 | 0.17 s |
| Death | 6 | 12 | 0.50 s |
| Spawn | 4 | 12 | 0.33 s |
| Channel | 4 | 12 | 0.33 s (hold last frame for longer channeling) |
| **Total per hero** | **34 frames** | — | — |

#### 9.6.2 Animation Controller Structure

```
ac_hero_combat.controller
├── Base Layer (Any State → Idle default)
│   ├── Idle        ←→ Walk (blend tree, no transition)
│   ├── Idle        → Attack01 (has exit time, can interrupt)
│   │               → Attack02 (has exit time, random selection)
│   ├── Any State   → Hit (immediate interrupt, priority 2)
│   ├── Any State   → Death (immediate interrupt, priority 3)
│   └── Walk        → Idle (has exit time)
│
├── Layer 1: Element Overlay (Additive, weight = 1)
│   └── One active state per element — blends over base animation
│       (fire glow, ice crystal overlay, lightning arc overlay)
│
└── Layer 2: Weapon FX (Additive, weight = 1)
    └── Attack frames trigger element-specific weapon trail on this layer
```

**Layer rules**:
- Base layer: movement and combat. Transitions use `Has Exit Time = true` except for Hit and Death (immediate).
- Element Overlay (Layer 1): Additive blending. Weight = 1. Contains one animation per element (fire overlay, ice overlay, lightning overlay). This layer is toggled on/off by gameplay code when the hero's element changes.
- Weapon FX (Layer 2): Additive blending. Weight = 1. Triggered by animation events on attack frames. Contains weapon-trail VFX sprites that render on top of the character.

**Controller per entity type**:
- `ac_hero_combat.controller` — All heroes share this controller. Per-hero sprite sets are assigned via the Animator's `Avatar Mask` and override controllers (Section 9.6.3).
- `ac_enemy_basic.controller` — All basic enemies share this controller (same states, different animation clips).
- `ac_enemy_elite.controller` — Elite enemies add a `Telegraph` state and `Rage` state.
- `ac_boss_{name}.controller` — Unique per boss. Bosses have unique state machines.

#### 9.6.3 Override Controllers for Hero Skins/Variants

Hero skins and elemental variants use **Animator Override Controllers**:

1. Base controller: `ac_hero_combat.controller` contains the state machine.
2. Per-hero override: `ac_hero_{name}.overrideController` maps `ac_hero_combat`'s animation clips to the hero's specific sprites.
3. Per-element override: `ac_hero_{name}_{element}.overrideController` — each hero has one per element. Changes only the `Element Overlay` layer's clips.

**Folder convention**: Override controllers live in `Art/Characters/{name}/Animations/`.

#### 9.6.4 Animation Events

| Event Name | Float Parameter | Trigger Timing | Consumer |
|-----------|----------------|----------------|----------|
| `OnHitFrame` | Damage multiplier (float) | Frame where damage is dealt | Combat system (damage calculation) |
| `OnSound` | Sound clip index (int) | Per animation sound cue | Audio manager |
| `OnVFXSpawn` | VFX prefab index (int) | Spawn VFX at character position | VFX manager |
| `OnFootstep` | Terrain type (int) | Walk cycle mid-stride | Audio manager (footstep sound) |
| `OnProjectileSpawn` | Projectile ID (int) | Frame where projectile is launched | Combat system (projectile creation) |
| `OnStateEnd` | 0 | Last frame of state | State machine (transition trigger) |

**Implementation**: Events are added to Animation clips via the Animation window's event line. All event functions are defined on `AnimEventReceiver.cs` component (attached to the same GameObject as the Animator).

---

### 9.7 Shader Management

#### 9.7.1 Shader Types

| Shader | File | Type | Purpose | Fallback |
|--------|------|------|---------|----------|
| Unlit Sprite | Built-in (URP) | Built-in | Default material for all pixel-art sprites | — (always available) |
| Parchment-Tear | `sh_parchment_tear.shader` | Custom | Parchment paper edge, torn-panel transition (Section 6 UI) | `Sprites/Default` |
| Emission Overlay | `sh_emission_overlay.shader` | Custom | Elemental glow overlay on characters and VFX | `Sprites/Default` |
| Corruption Overlay | `sh_corruption_overlay.shader` | Custom | Void corruption effect on enemies and environment | `Sprites/Default` |
| Rim Light | `sh_rim_light.shader` | Custom | Rim lighting for hero silhouettes (Section 3.4 priority 1) | `Sprites/Default` |
| Zone Restoration | `sh_zone_restore.shader` | Custom | Ink-in-water color bloom wave (Section 4 mood state) | `Sprites/Default` |

#### 9.7.2 Custom Shader Parameters

Each custom shader must expose a documented set of parameters with sensible defaults. Example for `sh_corruption_overlay.shader`:

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `_MainTex` | Texture2D | None | — | Base sprite texture |
| _CorruptionStrength | Float | 0.0 | 0.0 – 1.0 | Blend weight: 0 = no corruption, 1 = fully corrupted |
| _CorruptionColor | Color | #1A0F2E | — | Void tint color |
| _EdgeDarkenAmount | Float | 0.5 | 0.0 – 1.0 | Darkness multiplier at corrupted region edges |
| _PulseSpeed | Float | 0.0 | 0.0 – 5.0 | Corruption pulse animation speed (0 = static) |

All custom shaders must expose a `_MainTex` and accept the standard Unity sprite texture input format for URP compatibility.

#### 9.7.3 Shader Variant Collection

URP builds shader variants at build time for every combination of `Shader Features`. To prevent variant explosion:

1. Create a **Shader Variant Collection** asset per custom shader: `sh_{effect}_variants.shadervariants`.
2. Manually list only the variant combinations that are actually used in materials.
3. Add the variant collection to the project's `Graphics Settings → Shader Stripping → Always Included Shaders`.
4. Define a `CUSTOM_VARIANTS` keyword scope. If a material uses an unlisted variant, it will render as the fallback shader — log a warning at build time.

This prevents the build from compiling thousands of unused variants from the URP library.

#### 9.7.4 Fallback Shaders

Each custom shader has a fallback shader defined in its `#pragma` section:

```hlsl
#pragma surface surf Standard vertex:vert addshadow
// At the shader file bottom:
Fallback "Sprites/Default"
```

The fallback shader (`Sprites/Default`) is the built-in URP unlit sprite shader. It will not produce the custom effect, but the asset will render visibly. This is acceptable — the effect is a visual enhancement, not a gameplay requirement.

**Platform fallback rules**:
- If a platform does not support the custom shader (e.g., WebGL 2.0 with limited `_CameraSortingLayerTexture` support), it silently falls back to `Sprites/Default`.
- All materials using custom shaders must still visually function (correct sorting, correct pivot, correct sprite) under the fallback. The only loss is the visual effect itself.
- Test every custom shader with its fallback active before shipping.

---

### 9.8 Version Control for Binary Assets

#### 9.8.1 Git LFS

All binary art assets must be tracked by Git LFS. Configured in `.gitattributes` at the repository root.

```
# Art binary files — Git LFS
*.png     filter=lfs diff=lfs merge=lfs -text
*.aseprite filter=lfs diff=lfs merge=lfs -text
*.psb     filter=lfs diff=lfs merge=lfs -text
*.tga     filter=lfs diff=lfs merge=lfs -text
*.psd     filter=lfs diff=lfs merge=lfs -text
*.jpg     filter=lfs diff=lfs merge=lfs -text
*.jpeg    filter=lfs diff=lfs merge=lfs -text
*.tiff    filter=lfs diff=lfs merge=lfs -text
*.bmp     filter=lfs diff=lfs merge=lfs -text
*.gif     filter=lfs diff=lfs merge=lfs -text

# Audio (future use — Section 9.9 placeholder)
*.wav     filter=lfs diff=lfs merge=lfs -text
*.ogg     filter=lfs diff=lfs merge=lfs -text
*.mp3     filter=lfs diff=lfs merge=lfs -text

# No LFS needed for:
# .mat, .shader, .shadergraph, .anim, .controller, .overrideController, .spriteatlas
# These are text-based or YAML-serialized and diff-friendly
```

#### 9.8.2 Unity Meta Files

**Unity `.meta` files MUST be committed.** This is non-negotiable.

- Each `.png` file has a corresponding `.png.meta` that stores import settings (pivot, PPU, compression, packing tag).
- If `.meta` files are missing, Unity re-imports with default settings — breaking every pivot, every slice, every atlas packing tag.
- Validation: `git status` should show zero untracked `.meta` files. Run `git clean -nd` periodically to check for orphaned assets.

#### 9.8.3 Asset Serialization

Set `Edit → Project Settings → Editor → Asset Serialization → Mode` to **`Force Text`**.

With `Force Text`:
- Scenes (`.unity`), prefabs (`.prefab`), presets (`.preset`) are serialized as YAML text.
- Diffs are readable in pull requests.
- Merge conflicts are resolvable.
- Without it, scenes and prefabs are binary `.unity` files that are unmergeable.

This is a one-time project setting, not per-developer.

#### 9.8.4 Art Review Checklist (Pre-Commit)

Before committing art assets, verify:

- [ ] Sprites follow naming convention (Section 9.1) — validated by `Assets/_TinyRift/Editor/AssetNamingValidator.cs`
- [ ] Sprite import settings match Section 9.2 (PPU=16, Point filtering, Full Rect, Compression=None)
- [ ] Pivot points are correct per asset type (Section 9.2.3)
- [ ] Packing tag is set matching Section 9.5.3
- [ ] `.png.meta` file is committed alongside the PNG
- [ ] Source `.aseprite` file is committed (in `Source/` subfolder)
- [ ] Animation clips reference the correct sprites (no missing sprite warnings)
- [ ] No `.jpg` or lossy formats for pixel-art sprites (reference images only)
- [ ] No file is larger than 5 MB (exception: boss sprites up to 10 MB, reference images up to 15 MB)
- [ ] Reference images are in `Art/Reference/`, not in a game-imported folder
- [ ] Materials using custom shaders also list the fallback (Section 9.7.4)

---

### 9.9 Future Pipeline Considerations

This section captures pipeline decisions deferred to later phases:

| Topic | Status | Target Phase | Notes |
|-------|--------|-------------|-------|
| Audio asset pipeline | Deferred | Polish | Naming: `sfx_{context}_{variant}.wav`, `mus_{zone}_{mood}.ogg` |
| Localized UI asset workflow | Deferred | Localization | Rune glyphs are language-agnostic (Section 6.2); text-free icons are preferred |
| Mobile-specific LOD system | Deferred | Mobile optimization | Reduce sprite atlas sizes for 1 GB RAM devices (Section 9.5.4) |
| Automated import validation | Deferred | Production | Editor script in `Assets/_TinyRift/Editor/` validates naming, settings, and atlas tags on import |
| CI/CD build verification | Deferred | Release | GitHub Actions workflow checks all art assets against Section 9 conventions |
| Addressable asset system | Deferred | Post-launch | If asset count exceeds 2000 sprites, migrate to Addressables for memory management |

---

**Section 9 Acceptance Criteria** (for implementation):
1. Naming validator script (`AssetNamingValidator.cs`) exists and passes on all current art assets
2. A new artist can produce a character sprite, import it, and see it render correctly by following Section 9.2–9.4
3. All sprites are assigned to correct atlases per Section 9.5 — verified by a packing-tag audit
4. Animation controllers follow the structure from Section 9.6.2 — verified by code review
5. All custom shaders in `Art/Shaders/` expose documented parameters and have fallback shaders set
6. `.gitattributes` includes LFS patterns from Section 9.8.1 — verified by repo config
7. `Asset Serialization = Force Text` is set on the Unity project — verified in Project Settings
8. No `.meta` file is missing for any art asset — verified by a CI check
9. Reference folder is excluded from all build targets — verified by test build
10. Art asset folder structure matches Section 9.3 — verified by folder audit
