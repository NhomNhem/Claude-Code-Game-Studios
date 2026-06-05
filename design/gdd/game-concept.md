# Game Concept: Tiny Rift Survivors

*Created: 2026-05-25*
*Status: Draft*

---

## Elevator Pitch

> A pixel-art bullet-heaven survivor-like where the player channels elemental rifts to fight waves of void-spawned enemies. Each rift reveals fragments of a shattered world's memory — the elements you wield tell the story of the civilization that fell using them. Online from day one with persistent server-authoritative economy.

---

## Core Identity

| Aspect | Detail |
| ---- | ---- |
| **Genre** | Top-down 2D bullet-heaven survivor-like, roguelite with persistent online progression |
| **Platform** | PC (Steam Early Access) |
| **Target Audience** | Explorer-primary, Achiever-secondary (see Player Profile below) |
| **Player Count** | Single-player (Fusion Shared Mode co-op deferred) |
| **Session Length** | 20-30 minutes per run |
| **Monetization** | Premium purchase only — no IAP, no ads |
| **Estimated Scope** | Large (6–8 months, solo with agent assistance) |
| **Comparable Titles** | Vampire Survivors (genre foundation), Hades (lore-through-combat + persistent camp), Astral Ascent (elemental build-crafting) |

---

## Core Fantasy

You are an explorer of a world that ended — a Riftwalker piecing together the memory of a fallen civilization through the elemental ruins it left behind. Every run is both a fight for survival and an archaeological expedition. The elements aren't just weapons; they're historical records of a catastrophe, and mastering them means understanding what was lost — and whether it was accident, sacrifice, or intention.

---

## Unique Hook

> "Like Vampire Survivors, AND ALSO the elements you fight with tell the story of the world that died using them — AND ALSO persistent online progression with server-authoritative economy."

The elements remember. Fire isn't just damage — it's the last passion of a burning age, sealed by a Fire Archmage who tried to contain the first Rift. Ice isn't just crowd control — it's frozen knowledge preserved by an Ice Queen in her crystalline archive. Lightning isn't just area damage — it's the final scream of broken technology, engineered by a brilliant mind to stabilize the unstable. Lore fragments from elites and bosses reveal this history — and the question that haunts every fragment: was the Rift catastrophe an accident, a sacrifice, or something someone intentionally caused?

---

## Player Experience Analysis (MDA Framework)

### Target Aesthetics

| Aesthetic | Priority | How We Deliver It |
| ---- | ---- | ---- |
| **Discovery** (exploration, secrets) | 1 | Lore fragments, hidden elemental synergies, world reactivity (color restoration) |
| **Narrative** (drama, story arc) | 2 | Hand-crafted lore fragments per element/zone/boss, Hero Camp as codex |
| **Fantasy** (make-believe, role-playing) | 3 | Riftwalker identity, channeling ancient elements, uncovering forbidden history |
| **Sensation** (sensory pleasure) | 4 | Elemental VFX (Fractured Memory + Elemental Alchemy), screen shake, hit feel via SkillPresentationAdapter |
| **Challenge** (obstacle course, mastery) | 5 | Wave density scaling, elite patterns, zone boss mechanics |
| **Expression** (self-expression, creativity) | 6 | Build-crafting through elemental rune drafting — each run's kit is unique |
| **Fellowship** (social connection) | 7 | Deferred — Fusion Shared Mode co-op if stable (future tier) |
| **Submission** (relaxation, comfort zone) | N/A | Not a target aesthetic — runs demand active engagement |

### Key Dynamics (Emergent Player Behaviors)

- **Players experiment with elemental combinations** to discover synergies (fire+ice=steam screen cover, lightning+water=chain stun)
- **Players optimize each run's build** around the first rare rune they find
- **Players share lore discoveries** ("did you find what the Ice Queen was preserving in zone 2?")
- **Players push deeper to see what the next zone remembers** — the world's story is the progression drive
- **Players theorycraft maximally broken synergy builds** between runs

### Core Mechanics (Systems We Build)

1. **Elemental Rune Drafting** — Level-up choices between 3 elemental rune upgrades. Each adds a modifier (new orbit, burst ability, passive buff) or unlocks a synergy.
2. **Orbit + Burst Combat** — Passive orbital auto-attacks + aimed burst skills on cooldown. Movement + positioning + timing.
3. **Lore Fragment Discovery** — Elite/boss kills auto-collect Memory Fragments readable in the Hero Camp codex (never mid-combat). Fragments track the world's history through named figures (Fire Archmage, Ice Queen, Lightning Engineer, Void-touched scholar) and physically restore color/saturation to the world. The central question: was the Rift catastrophe an accident, a sacrifice, or intention?
4. **Elemental Synergy System** — Real-time status tracking per enemy. Element A + Element B = compound effect. Resolved at hit time via custom IDamageProvider.
5. **Hero Camp Progression** — Persistent between-run hub with currency spends, hero unlocks, zone unlocks, and lore codex.

---

## Player Motivation Profile

### Primary Psychological Needs Served

| Need | How This Game Satisfies It | Strength |
| ---- | ---- | ---- |
| **Autonomy** (freedom, meaningful choice) | Draft decisions every level-up; player chooses their build trajectory. No two runs identical. | Core |
| **Competence** (mastery, skill growth) | Positioning, timing bursts, learning enemy patterns, optimizing synergy chains. Skill ceiling is real. | Core |
| **Relatedness** (connection, belonging) | Primarily single-player. Lore creates connection to the world and its history. Deferred: Fusion co-op may add fellowship. | Supporting |

### Player Type Appeal (Bartle Taxonomy)

- **[x] Achievers** (goal completion, collection, progression) — Hero Camp unlocks, currency earned per run, mastery across elements. Clear progression markers.
- **[x] Explorers** (discovery, understanding systems, finding secrets) — PRIMARY TYPE. Lore fragments, hidden synergies, elemental reaction discovery, world reactivity.
- **[ ] Socializers** (relationships, cooperation, community) — Deferred (Fusion co-op is cut tier).
- **[x] Competitors** (domination, PvP, leaderboards) — Weak secondary. Leaderboards may come post-EA. No PvP.

### Flow State Design

- **Onboarding curve**: First run: one orbit skill, one burst — learn movement + aiming. Second run: draft choice introduced. Third run: synergy discovery. Lore fragment on first elite kill.
- **Difficulty scaling**: Wave density + elite spawn rate increases with run time. Zone bosses add mechanical complexity (patterns, phases). Player power also scales via drafted runes.
- **Feedback clarity**: Elemental VFX colors = instant readability. Synergies burst with compound VFX. Lore fragments have a distinct visual drop effect.
- **Recovery from failure**: Death returns to Hero Camp with currency earned. Failed runs still yield partial progression. Lore fragments persist. "One more run" is immediate.

---

## Core Loop

### Moment-to-Moment (30 seconds)

Move with WASD → passive orbital rifts auto-attack nearby enemies → aim and release burst abilities on cooldown → dodge enemy patterns → feel elemental feedback (VFX, screen shake, damage numbers) → elite kills auto-collect lore fragments (read in Hero Camp, not mid-combat)

### Short-Term (5-15 minutes)

Clear wave → level up → draft 1 of 3 elemental rune upgrades → discover synergies as build takes shape → face elite/mini-boss → earn lore fragment → push deeper toward zone boss → decide whether to extend the run or prepare for the boss

### Session-Level (20-30 minutes)

Enter Rift (zone selection) → clear escalating waves → build elemental kit through draft choices → face elite encounters → reach zone boss → survive or die → return to Hero Camp with currency + lore → spend currency on upgrades → read new fragments in codex → next run

### Long-Term Progression

Every run earns currency and lore fragments → Hero Camp unlocks (new heroes, permanent upgrades, new rift zones) → elemental mastery grows across runs as synergies are discovered → persistent progress even on failed runs → the world map physically expands and recolors as zones are conquered

### Retention Hooks

- **Curiosity**: What lore does the next zone hold? What happens when I combine fire + lightning? What's behind that locked gate in the camp?
- **Investment**: Currency and lore persist across runs. The Hero Camp grows. Unlocked zones stay unlocked.
- **Mastery**: Synergy discovery is self-rewarding. Optimizing a build to its breaking point is the loop. Leaderboards (post-EA) add competitive drive.

---

## Game Pillars

### Pillar 1: Rifts Tell Stories
Every element, enemy, and arena remembers the world that was. Lore isn't a separate screen — it's in what you fight with and what you fight against.

*Design test*: Skills have two tracks — mechanical power (flat damage) and narrative power (zone bonus, synergy unlock, permanent Hero Camp upgrade). Picking the lore-correct skill feeds the narrative track, making it rewarding without punishing mechanical optimization.

### Pillar 2: Emergent Build-Crafting
Each run is a puzzle of elemental synergies. The fun is discovering combinations you didn't plan.

*Design test*: Choose synergy unlock over flat numerical upgrade, period.

### Pillar 3: Snappy 20–30 Minute Sessions
Always something meaningful to choose. No dead time. Runs are dense, readable, and respect the player's time.

*Design test*: When a lore text would take 30 seconds to read, we cut it to 10. When a boss fight could be 2 minutes or 5, we choose the tighter version.

### Pillar 4: World Reactivity
The world remembers what you've done. Conquered zones stay conquered. Color returns. The Hero Camp grows. The map evolves.

*Design test*: When a player completes a zone, the change should be visible on the map immediately, not just in a menu.

### Anti-Pillars
- **NOT procedurally-generated narrative**: All lore is hand-crafted. Story quality > story quantity.
- **NOT PvP**: This is a PvE narrative experience. If Fusion multiplayer comes, it's co-op.
- **NOT an endless treadmill**: Runs have defined endings. No "survive forever" mode.
- **NOT an inventory management sim**: No gear juggling, no stat shuffling. Equip runes, not items.
- **NOT a live-ops grind game**: Premium purchase. No daily quests, no FOMO timers.

**Tension resolution**: The context of the moment decides which pillar leads. Mid-combat → P3. Zone completion / elite reward → P1 + P4. Hero Camp → P1 + P2 + P4.

---

## Visual Identity Anchor

### Primary Direction: Fractured Memory (World Identity)
*Visual rule: "Everything is incomplete — beauty is in the fracture."*

- **Supporting principle 1: Color is memory**. The world starts in sepia/charcoal. As lore is uncovered, saturation bleeds back zone by zone.
- *Design test*: When designing a zone, ask — what color is this zone's memory? When the player completes it, what color returns?
- **Supporting principle 2: Every crack tells a story**. Jagged shards, broken geometry, energy seeping through fault lines. The world was shattered — the cracks are where the history leaks out.
- *Design test*: When placing environmental details, the default state is broken. Only player progress restores completeness.
- **Supporting principle 3: Monsters are corrupted memories**. Enemies are twisted remnants of the world that was — their design hints at what they used to be.
- *Design test*: Every enemy type has a visual clue to its pre-corruption identity (a broken tool, a faded uniform, a familiar shape distorted).

**Color philosophy**: Desaturated charcoal/sepia base. Each zone has a dominant memory color: amber (golden age), cyan (knowledge), viridian (life — corrupted), violet (void — consuming). Player skills use saturated elemental primaries as contrast. Lore fragment recovery triggers a local saturation bloom.

### Secondary Layer: Elemental Alchemy (Combat VFX)
*Visual rule: "Everything reacts."*

Element-specific silhouettes: fire = teardrop, ice = hexagon prism, lightning = zigzag arc. Synergies produce hybrid shapes. Combat reads at a glance through color-coded elemental language. Background stays dark so combat pops.

---

## Inspiration and References

| Reference | What We Take From It | What We Do Differently | Why It Matters |
| ---- | ---- | ---- | ---- |
| **Hades** | Lore-through-combat fragments, persistent camp progression, character unlocks | Our lore is about the WORLD, not characters. Hero Camp is a hub, not a relationship simulator. | Validates that narrative roguelite works commercially |
| **Vampire Survivors** | Wave-based survival, auto-attack foundation, 20-minute session structure | Player has agency through aimed bursts + draft choices. Not passive — active positioning and timing matter. | Proves the session length works for the genre |
| **Astral Ascent** | Elemental rune drafting, synergy discovery | Simpler element count (3 vs 8), faster onboarding, online persistence | Validates elemental build-crafting as a roguelite framework |
| **Dead Cells** | Persistent world unlocks, lore-through-environment | Story is in fragments, not environmental storytelling alone. Cleaner delivery. | Proves meta-progression + lore discovery loop |

---

## Target Player Profile

| Attribute | Detail |
| ---- | ---- |
| **Age range** | 18-35 |
| **Gaming experience** | Mid-core to hardcore — comfortable with action games and roguelite systems |
| **Time availability** | 20-30 minute sessions on weeknights, longer on weekends |
| **Platform preference** | PC (Steam) — plays with keyboard + mouse or controller |
| **Current games they play** | Hades, Dead Cells, Vampire Survivors, Slay the Spire, Astral Ascent |
| **What they're looking for** | A survivor-like with MEANING — where the combat serves a story, not just a score |
| **What would turn them away** | Repetitive runs with no narrative payoff, pay-to-win, excessive grind |

---

## Technical Considerations

| Consideration | Assessment |
| ---- | ---- |
| **Recommended Engine** | Unity 6000.3.11f1 (URP) — already configured, template provides full framework |
| **Key Technical Challenges** | Skill Presentation Adapter (animation feel without vendor code), Server-authoritative economy validation, Unity 6000.x post-cutoff API risk |
| **Art Style** | Pixel-art 2D with saturated elemental VFX overlay |
| **Art Pipeline Complexity** | Medium — custom pixel-art assets (characters, enemies, environments), particle VFX via template's pool system |
| **Audio Needs** | Moderate — combat SFX, elemental audio identity, minimal music |
| **Networking** | WebSocket + SQL (client-server for economy), Fusion Shared Mode (for deferred co-op) |
| **Content Volume** | MVP: 1 zone, 1 boss, 3-5 skills, 1 hero. Full vision: 5+ zones, 5+ bosses, 15+ skills, 5+ heroes |
| **Procedural Systems** | None in M0/M1. Wave composition is configured, not procedurally generated. Enemy spawn locations vary per session. |

---

## Risks and Open Questions

### Design Risks
- **Synergy balance is extremely hard**: Emergent combinations can produce degenerate builds. Need a strong balance feedback loop (automated testing, playtest data).
- **Lore may not land**: Writing quality is the hard part. Risk mitigated by: (a) named characters give players emotional anchors, (b) the unresolved dramatic question creates forward momentum, (c) fragments are auto-collected mid-run and read in Hero Camp — no cognitive load during combat.
- **20-minute sessions may feel too tight** with lore + build-crafting + combat: Tension resolution rule (P3 yields to P1/P2 at camp) mitigates this, but needs playtest validation.

### Technical Risks
- **Unity 6000.3.11f1 is post-cutoff**: IL2CPP build validation needed early. Custom shaders deferred to avoid URP 17 render graph API risk. Weekly IL2CPP smoke test recommended.
- **Server-authoritative economy**: Run-completion validation protocol needed (time:dmg ratios, signed telemetry hashes). Memory editing during runs is trivially possible in a PvE client.
- **SkillPresentationAdapter coupling risk**: Observing template events from outside vendor code — timing must derive from SkillData + clip lengths, not FSM state reads.

### Market Risks
- **Crowded genre**: Survivor-like space is saturated. Differentiation via narrative + online persistence + build-crafting is the moat. If execution doesn't deliver, the game is invisible.
- **Premium-only in a F2P-dominant genre**: Must communicate value clearly in store page and demo/trailer.

### Scope Risks
- **Backend timeline is the critical path**: If WebSocketSQL backend takes 4-6 weeks instead of 2-3, MVP timeline must extend. Front-load in month 1 to know by week 4. Template's `OfflineBackendService` is the fallback for local dev — no separate offline track needed.
- **Content volume (heroes, zones) is linear with time**: Can't accelerate — each hero/zone/boss is a fixed effort. Realistic count: 3 heroes, 3 zones for EA. Full 5-hero, 5-zone vision may be 12+ months.

### Open Questions
- Does the template's `WebSocketSqlBackendService` work with Docker stack out of the box, or does it need adaptation? — Answer by week 2.
- Can the `SkillPresentationAdapter` achieve satisfying feel without modifying the animation FSM? — Prototype in week 3.
- Do standalone skills provide enough depth for the first 10 runs without synergies? — Playtest at end of month 2.

---

## MVP Definition

**Core hypothesis**: Players find the elemental build-crafting + lore discovery loop engaging for 20-30 minute sessions across multiple runs.

**Required for MVP**:
1. 1 playable hero with orbit + burst combat
2. 1 Rift zone with wave progression and 1 boss/elite encounter
3. 5-6 standalone rune skills (fire, ice, lightning base set — no synergy system yet)
4. 1 Memory Fragment reward on boss kill (auto-collected, readable in Hero Camp)
5. Hero Camp shell (minimal functional UI: currency display, lore codex, start run)
6. WebSocketSQL backend: login, profile, currency E2E
7. SkillPresentationAdapter prototype (improved animation/VFX feel)
8. Steam Standalone build

**Explicitly NOT in MVP** (defer to post-MVP):
- Multiple heroes
- Multiple zones and bosses
- Full Hero Camp with upgrades
- Elemental synergy system (deferred to month 4-5)
- Fusion co-op
- Achievements
- Full VFX/audio polish

### Scope Tiers

| Tier | Content | Features | Timeline |
| ---- | ---- | ---- | ---- |
| **Tier 1 (MVP)** | 1 hero, 1 zone, 1 boss, 5-6 standalone skills | Online: login → profile → currency E2E. Hero Camp shell with lore codex. SkillPresentationAdapter prototype. Steam build. No synergies. | 3 months |
| **Tier 2 (Vertical Slice)** | 2 heroes, 2 zones, 2 bosses, 8 skills, 3+ synergies | Full Hero Camp functional. Synergy system introduced. Named Memory Fragments with first figure. Fusion Shared Mode smoke test. | 5 months |
| **Tier 3 (EA Launch)** | 3 heroes, 3 zones, 3 bosses, 12+ skills, 5+ synergies | Full lore system (named figures + open question), all named Memory Fragments, UI polish, VFX pass, balance tuning. Steam EA store page. | 8 months |
| **Tier 4 (Full Vision)** | 5+ heroes, 5+ zones, 5+ bosses, 15+ skills, full synergy matrix | All named figures resolved, dramatic question answered. Fusion co-op if stable, leaderboards, all content. | 12+ months |

**Offline dev mode**: Template's built-in `OfflineBackendService` handles local-only testing. No separate "offline track" — one codebase, one economy, toggle via BackendSettings.asset. This replaces the removed T0.5 approach (no migration risk, no dual-codebase).

---

## Next Steps

- [ ] Run `/design-review design/gdd/game-concept.md` to validate concept completeness
- [ ] Run `/art-bible` to create the visual identity specification from the Fractured Memory + Elemental Alchemy anchor
- [ ] Run `/map-systems` to decompose the concept into individual systems with dependency ordering
- [ ] Author per-system GDDs with `/design-system` (start with Combat, then Skills, then Progression)
- [ ] Plan the technical architecture with `/create-architecture`
- [ ] Record ADRs: SkillPresentationAdapter pattern, Run-completion validation protocol, Elemental synergy architecture
- [ ] Run `/architecture-review` for TR registry and Requirements Traceability Matrix
- [ ] Build MVP prototype to validate core loop (standalone skills, online auth, Hero Camp shell)

> **Director Gate Reviews**:
> - CD-PILLARS: CONCERNS (accepted — pillars sharpened per feedback)
> - AD-CONCEPT-VISUAL: CONCEPTS (user selected "Fractured Memory + Elemental Alchemy" pair)
> - TD-FEASIBILITY: VIABLE (2 medium concerns — economy validation, Unity 6 IL2CPP)
> - PR-SCOPE: OPTIMISTIC (accepted — timeline adjusted to 3 months MVP, 6-8 months EA)
