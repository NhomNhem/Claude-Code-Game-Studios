# Systems Index: Tiny Rift Survivors

> **Status**: Draft
> **Created**: 2026-05-26
> **Last Updated**: 2026-05-26
> **Source Concept**: design/gdd/game-concept.md
> **Art Bible**: design/art/art-bible.md
> **Tier 1 Director Gates**: TD-SYSTEM-BOUNDARY (CONCERNS — accepted); PR-SCOPE (OPTIMISTIC — accepted); CD-SYSTEMS (CONCERNS — accepted as-is)

---

## Overview

Tiny Rift Survivors is a pixel-art bullet-heaven survivor-like with elemental rift lore, build-crafting via rune drafting, and persistent online economy. The core loop (move → auto-attack → aim bursts → level up → draft runes → discover synergies → defeat boss → earn currency + lore) requires ~35 systems for the 3-month MVP. Foundation and Core layers are largely template-provided or thin wrappers; the real design mass is in Feature (combat, drafting, progression) and Presentation (HUD, camp, draft UI). Art/editor work is the pacing bottleneck, not code.

> **PR-SCOPE note**: MVP timeline is optimistic but achievable. Cleanest cut under pressure: reduce rune skills from 6 → 3 (saves 10-14 days). UI canvases should be pre-prod'd early. Pixel art sourcing begins Day 1.

---

## Systems Enumeration

| # | System Name | Category | Priority | Status | Design Doc | Depends On |
|---|-------------|----------|----------|--------|------------|------------|
| 1 | Input System | Core | MVP | Designed | design/gdd/input-system.md | — |
| 2 | Game State Manager | Core | MVP | Needs Revision | design/gdd/game-state-manager.md | — |
| 3 | Time System | Core | MVP | Needs Revision | design/gdd/time-system.md | — |
| 4 | Network Manager | Core | MVP | Designed | design/gdd/network-manager.md | — |
| 5 | Event Bus (inferred) | Core | MVP | Needs Revision | design/gdd/event-bus.md | — |
| 6 | Skill Data System | Gameplay | MVP | Drafted | design/gdd/skill-data-system.md | — |
| 7 | Hit Detection | Core | MVP | Designed | design/gdd/hit-detection.md | — |
| 8 | Object Pooling (inferred) | Core | MVP | Drafted | design/gdd/object-pooling.md | — |
| 9 | Scene Manager | Core | MVP | In Review (Revised) | design/gdd/scene-manager.md | GState |
| 10 | Save/Profile Persistence | Persistence | MVP | In Review (Revised v4) | design/gdd/save-profile-persistence.md | SkillData, Network |
| 11 | Account/Profile System | Persistence | MVP | Designed | design/gdd/account-profile-system.md | Network, Save |
| 12 | Zone Definition System | Gameplay | MVP | Designed | design/gdd/zone-definition-system.md | Save |
| 13 | World State | Persistence | MVP | Designed | design/gdd/world-state.md | Save |
| 14 | Audio System | Audio | MVP | Designed | design/gdd/audio-system.md | GState, EventBus, ZoneDef, SkillData |
| 15 | VFX System | Gameplay | MVP | Designed | design/gdd/vfx-system.md | EventBus, ObjectPool |
| 16 | Currency System | Economy | MVP | Designed | design/gdd/currency-system.md | Save, Network |
| 17 | Lore Fragment System | Narrative | MVP | Designed | design/gdd/lore-fragment-system.md | Save |
| 18 | Status Effect System | Gameplay | MVP | Designed | design/gdd/status-effect-system.md | SkillData, TimeSystem |
| 19 | Damage & Health System | Gameplay | MVP | Designed | design/gdd/damage-health-system.md | SkillData, StatusFX, EventBus, TimeSys |
| 20 | Orbit Combat System | Gameplay | MVP | Designed | design/gdd/orbit-combat-system.md | DmgHealth, HitDetect, SkillData, ObjPool |
| 21 | Burst Skill System | Gameplay | MVP | Designed | design/gdd/burst-skill-system.md | DmgHealth, HitDetect, SkillData, ObjPool, TimeSys |
| 22 | Level-Up System | Progression | MVP | Designed | design/gdd/level-up-system.md | EventBus, Save |
| 23 | Rune Draft System | Progression | MVP | Designed | design/gdd/rune-draft-system.md | LevelUp, SkillData, BuildState |
| 24 | Enemy AI | Gameplay | MVP | Designed | design/gdd/enemy-ai-system.md | GState, HitDetect, ObjPool |
| 25 | Wave Spawning System | Gameplay | MVP | Designed | design/gdd/wave-spawning-system.md | ZoneDef, GState, ObjPool |
| 26 | Boss Encounter System | Gameplay | MVP | Designed | design/gdd/boss-encounter-system.md | EnemyAI, ZoneDef, StatusFX |
| 27 | Screen Shake & Feedback | Gameplay | MVP | Designed | design/gdd/screen-shake-system.md | EventBus, GState |
| 28 | Hero Camp Progression | Progression | MVP | Designed | design/gdd/hero-camp-progression.md | Save, Currency, WorldState |
| 29 | Build State | Gameplay | MVP | Designed | design/gdd/build-state.md | SkillData |
| 30 | HUD | UI | MVP | Designed | design/gdd/hud.md | DmgHealth, Currency, SkillData, Build, GState |
| 31 | Draft Panel UI | UI | MVP | Designed | design/gdd/draft-panel-ui.md | RuneDraft, SkillData |
| 32 | Camp Menu UI | UI | MVP | Designed | design/gdd/camp-menu-ui.md | CampProg, Codex, Currency |
| 33 | Codex UI | UI | MVP | Designed | design/gdd/codex-ui.md | Lore |
| 34 | SkillPresentationAdapter | Meta | MVP | Designed | design/gdd/skill-presentation-adapter.md | HitDetect, DmgHealth, SkillData, VFX, Audio |
| 35 | Loading/Transition System | UI | MVP | Designed | design/gdd/loading-transition-system.md | SceneMgr, GState |
| 36 | Run Completion | UI | MVP | Designed | design/gdd/run-completion-flow.md | Currency, Lore, CampProg, Build |
| 37 | Minimap | UI | Vertical Slice | Not Started | — | WorldState, GState, ZoneDef |
| 38 | Pause Menu | UI | Vertical Slice | Not Started | — | GState, Input |
| 39 | Hero/Zone Unlock | Progression | Vertical Slice | Not Started | — | CampProg, WorldState |
| 40 | Synergy System (inferred) | Gameplay | Alpha | Not Started | — | SkillData, StatusFX, Build |
| 41 | Server Economy Validation | Economy | Alpha | Not Started | — | Currency, Network |
| 42 | Tutorial/Onboarding | Meta | Alpha | Not Started | — | (nearly everything) |
| 43 | Fusion Co-op (inferred) | Gameplay | Full Vision | Not Started | — | Network, EnemyAI, Boss, Lobby |

---

## Categories

| Category | Description | Typical Systems |
|----------|-------------|-----------------|
| **Core** | Foundation infrastructure everything depends on | GState ✅, Event Bus ✅, Skill Data ✅, Input ✅, Time, Network, Hit Detection, Object Pool ✅, Scene Manager |
| **Gameplay** | The systems that make the game fun | Skill Data, Orbit/Burst Combat, DmgHealth, StatusFX, Enemy AI, Wave Spawn, Boss, Screen Shake, Build State, Zone Def, VFX, Synergy |
| **Progression** | How the player grows over time | Level-Up, Rune Draft, Camp Progression, Hero/Zone Unlock |
| **Economy** | Resource creation and consumption | Currency System, Server Economy Validation |
| **Persistence** | Save state and continuity | Save/Profile, Account/Profile, World State |
| **UI** | Player-facing information displays | HUD, Draft Panel, Camp Menu, Codex, Minimap, Pause, Loading, Run Completion |
| **Audio** | Sound and music | Audio System |
| **Narrative** | Story delivery | Lore Fragment System |
| **Meta** | Systems outside the core game loop | SkillPresentationAdapter, Tutorial/Onboarding |

---

## Priority Tiers

| Tier | Definition | Target Milestone | Design Urgency |
|------|------------|------------------|----------------|
| **MVP** | Required for the core loop to function. Without these, you can't test "is this fun?" | Month 3 | Design FIRST |

> **Creative Director Note (CD-SYSTEMS)**: Pillar 2 (Emergent Build-Crafting) is materially under-delivered in MVP — the Synergy System is deferred to Alpha, so the Rune Draft offers standalone picks only. Decision accepted: MVP validates the core loop (combat, draft, progression) without synergy reactions. Full synergy discovery lands in month 4-5. Pillar 1's "narrative power track" (mechanical reward for lore-correct picks) also deferred — MVP lore is passive text in the Codex. Both gaps are acknowledged and intentional scope decisions.
| **Vertical Slice** | Required for one complete, polished area. Demonstrates the full experience. | Month 5 | Design SECOND |
| **Alpha** | All features present in rough form. Complete mechanical scope, placeholder content OK. | Month 8 | Design THIRD |
| **Full Vision** | Polish, edge cases, nice-to-haves, and content-complete features. | 12+ months | Design as needed |

---

## Dependency Map

### Foundation Layer (zero dependencies)

1. **Input System** — `InputRouter` wrapping Unity Input System 1.19.0 with 3 action maps (Gameplay/Menu/Camp), GState-driven switching. Consumed by CharacterEntity (Move, UseSkill, UpdateDirectionalAim) and UI (InputSystemUIInputModule).
2. **Game State Manager** — Lightweight state machine (Menu/Playing/Paused/GameOver) publishing `OnStateChanged` events. No per-entity state — owned by owning systems. (TD-SYSTEM-BOUNDARY C4)
3. **Time System** — `TimeManager` wrapping Unity Time API with GState-aware time scale, run elapsed timer, cooldown registry, and hit-stop support. Consumed by all gameplay systems.
4. **Network Manager** — Wraps `IBackendService` with connection state machine (Disconnected/Connecting/Connected/Reconnecting), exponential backoff reconnect, heartbeat health check. Thin wrapper on template's backend service.
5. **Event Bus** — Publish/subscribe message bus. Decouples producers (Damage kills enemy) from consumers (Currency, XP, VFX, Audio, Screen Shake). (TD-SYSTEM-BOUNDARY C1)
6. **Skill Data System** — Static ScriptableObject config: skill id, element, cooldown, damage, rarity, icon, upgrade defs, VFX profile. Uses pure data references (IDs/keys/enums), never runtime types from higher layers. (TD-SYSTEM-BOUNDARY C3)
7. **Hit Detection** — Faction-aware hitbox/hurtbox registration (Player/Enemy/Neutral), wraps template's 3D trigger collision, publishes `HitEvent` to Event Bus. Per-target 0.3s cooldown. Additive layer over template — does not modify vendor code.

### Core Layer (depends on Foundation)

8. **Scene Manager** — Depends on: GState. Scene load/unload, additive scene support for camp → zone transitions.
9. **Save/Profile Persistence** — Depends on: SkillData, Network. Persists player profile, currency, unlocked skills, per-run state. Owns serialization of Build State (TD-SYSTEM-BOUNDARY C5). References SkillData by ID only.
10. **Account/Profile System** — Depends on: Network, Save. Login/registration, profile fetch/update via WebSocketSQL backend.
11. **Zone Definition System** — Depends on: Save. Wave composition configs, enemy spawn tables, boss data per zone. Loaded from ScriptableObjects.
12. **World State** — Depends on: Save. Which zones are restored/unlocked, camp growth level, persistent visual state. On zone completion, publishes restoration event to Event Bus → consumed by VFX System (art bible Section 7.6.1 zone restore sweep) and Post-Processing (Section 7.3.2 color grading shift).
13. **Audio System** — Depends on: GState. SFX playback, music crossfade, mixer bus management. Consumes audio events from Event Bus.
14. **VFX System** — Depends on: ObjectPool. Particle spawn/manage, elemental VFX library (art bible Section 8). Consumes VFX events from Event Bus.
15. **Currency System** — Depends on: Save, Network. Earn/spend with server-authoritative validation (deferred: full Server Economy Validation in Alpha). Consumes currency events from Event Bus.
16. **Lore Fragment System** — Depends on: Save. Fragment data storage, collection trigger (auto-collect on elite/boss kill), codex data provider.
17. **Object Pooling** — Depends on: (none built-in, consumed by many). `PoolManager` wrapping `UnityEngine.Pool.ObjectPool<T>` for projectiles, enemies, VFX, damage numbers. Prevents GC spikes. (TD-SYSTEM-BOUNDARY C2)
18. **Status Effect System** — Depends on: SkillData. Per-entity status tracking (frozen/burned/stunned), tick countdowns, stack management. Exposes `ApplyStatus(StatusType, EntityId)` and `GetActiveStatuses(EntityId)`. (TD-SYSTEM-BOUNDARY C6)

### Feature Layer (depends on Core)

19. **Damage & Health System** — Depends on: SkillData, StatusFX. HP management, damage calculation, invincibility frames, death detection. Applies status effects via `StatusFX.ApplyStatus()`. Publishes kill/death events to Event Bus.
20. **Orbit Combat System** — Depends on: DmgHealth, HitDetect, SkillData. Passive orbital auto-attack, targeting priority, orbit rotation speed. Uses ObjectPool for projectile pooling.
21. **Burst Skill System** — Depends on: DmgHealth, HitDetect, SkillData. Aimed skill execution, cooldown tracking, targeting (mouse/gamepad aim). Uses ObjectPool for skill-specific VFX.
22. **Level-Up System** — Depends on: Audio, VFX, Save. XP accumulation (consumes kill events from Event Bus), level thresholds, draft trigger.
23. **Rune Draft System** — Depends on: LevelUp, SkillData. 3-card draft generation, rarity weighting, synergy hints (future), selection handler.
24. **Enemy AI** — Depends on: GState, HitDetect, Input. Behavior patterns per enemy type (basic chase, elite pattern, boss phase tree), aggro range, detection glow (art bible Section 7.6.2).
25. **Wave Spawning System** — Depends on: ZoneDef, GState. Wave lifecycle (start, escalation, boss trigger), spawn positions, composition from ZoneDef config. Uses ObjectPool.
26. **Boss Encounter System** — Depends on: EnemyAI, ZoneDef, StatusFX. Phase transitions, telegraphs, arena gating, phase-change lighting (art bible Section 7.6.3).
27. **Screen Shake & Feedback** — Depends on: GState, DmgHealth. Shake profiles (art bible Section 6.5 table), damage vignette, low-health warning, hit-stop overlay. Consumes damage/kill events from Event Bus.
28. **Hero Camp Progression** — Depends on: Currency, Lore. Permanent upgrade tree, hero/zone unlock gates (handoff to Unlock system), currency sinks.
29. **Build State** — Depends on: SkillData, RuneDraft, GState. Per-run skill loadout, modifiers, synergy flags. Serialized by Save/Profile on checkpoint/run-end.

### Presentation Layer (depends on Feature)

30. **HUD** — Depends on: DmgHealth, Currency, SkillData, Build, GState. Health bar (runic inscription), skill slots with cooldown sweep, currency counters, kill/combo counter, boss health bar. Show/hide per GState.
31. **Draft Panel UI** — Depends on: RuneDraft, SkillData. 3-card parchment panel, hover glow (art bible Section 8.5.2), card pick-up animation (Section 8.5.3), shield-shaped card layout (Section 3.3).
32. **Camp Menu UI** — Depends on: CampProg, Codex, Currency. Start run button, lore codex access, currency display, upgrade panel (future tier).
33. **Codex UI** — Depends on: Lore. Fragment reading view, runic glyph → readable text toggle (art bible Section 6.2 rule 5).
34. **SkillPresentationAdapter** — Depends on: HitDetect, DmgHealth, SkillData, VFX, Audio. Maps skill data → animation timing + VFX sequence + hit-stop + audio feedback. Observes template events via bridge pattern — never modifies vendor code.
35. **Minimap** — Depends on: WorldState, GState, ZoneDef. Parchment disk (art bible Section 6.6), fog of war, player/entity markers. Vertical Slice.
36. **Pause Menu** — Depends on: GState, Input. Parchment panel, settings access, quit to camp. Vertical Slice.
37. **Loading/Transition System** — Depends on: SceneMgr, GState. Zone entry title card (art bible Section 6.3), ink-stamp/parchment-tear/rune-ignite transitions.
38. **Run Completion** — Depends on: Currency, Lore, CampProg, Build, EconValid. End-of-run summary screen, reward calculation, validation handoff to server economy, camp return flow.

### Polish Layer (depends on everything)

39. **Tutorial/Onboarding** — Depends on: (nearly everything). First-run flow, tooltip system, draft guidance, combat basics. Alpha.

---

## Recommended Design Order

Combining dependency sort + priority tier. Independent systems at the same layer can be designed in parallel.

| Order | System | Priority | Layer | Key Concerns | Est. Effort |
|-------|--------|----------|-------|--------------|-------------|
| 1 | Game State Manager | MVP | Foundation | C4: keep surface area narrow | S |
| 2 | Event Bus | MVP | Foundation | C1: define core message types first | S |
| 3 | Skill Data System | MVP | Foundation | C3: data-only contract, no runtime type refs | M |
| 4 | Object Pooling | MVP | Foundation | C2: generic pool for all spawnable entities | S |
| 5 | Input System | MVP | Foundation | Mostly Unity built-in; document actions | S |
| 6 | Time System | MVP | Foundation | Timer + cooldown foundation | S |
| 7 | Network Manager | MVP | Foundation | WebSocket lifecycle (config, not build) | S |
| 8 | Hit Detection | MVP | Foundation | Collider registration, hit event output | S |
| 9 | Save/Profile Persistence | MVP | Core | C5: define Build State serialization contract | M |
| 10 | Scene Manager | MVP | Core | Additive scene support | S |
| 11 | Currency System | MVP | Core | Server-authoritative hooks | M |
| 12 | Zone Definition System | MVP | Core | ScriptableObject-based wave configs | M |
| 13 | World State | MVP | Core | Zone restore state, persistence data | S |
| 14 | Audio System | MVP | Core | SFX playback, Event Bus consumer | S |
| 15 | VFX System | MVP | Core | Particle manager, elemental library | M |
| 16 | Status Effect System | MVP | Core | C6: define API contract with DmgHealth | M |
| 17 | Lore Fragment System | MVP | Core | Data storage, collection triggers | S |
| 18 | Account/Profile System | MVP | Core | Login/profile (mostly config) | S |
| 19 | Damage & Health System | MVP | Feature | HP, damage calc, i-frames, death | M |
| 20 | Orbit Combat System | MVP | Feature | Passive auto-attack, targeting | M |
| 21 | Burst Skill System | MVP | Feature | Aimed skill execution, cooldowns | M |
| 22 | Level-Up System | MVP | Feature | XP → level → draft trigger | S |
| 23 | Rune Draft System | MVP | Feature | 3-card choice, rarity weights | M |
| 24 | Build State | MVP | Feature | Per-run loadout, serialization handoff | S |
| 25 | Enemy AI | MVP | Feature | Behavior patterns per tier | M |
| 26 | Wave Spawning System | MVP | Feature | Wave lifecycle, composition, escalation | M |
| 27 | Boss Encounter System | MVP | Feature | Phases, telegraphs, arena gating | M |
| 28 | Screen Shake & Feedback | MVP | Feature | Event Bus consumer, shake profiles | S |
| 29 | Hero Camp Progression | MVP | Feature | Upgrade tree, currency sinks | M |
| 30 | HUD | MVP | Presentation | Layout per art bible Section 6.1 | M |
| 31 | Draft Panel UI | MVP | Presentation | Parchment/card layout per Section 3.3/8.5 | M |
| 32 | SkillPresentationAdapter | MVP | Presentation | Bridge pattern, Event Bus timing | L |
| 33 | Camp Menu UI (shell) | MVP | Presentation | Start run, codex, currency display | M |
| 34 | Codex UI | MVP | Presentation | Fragment display, rune↔text toggle | S |
| 35 | Loading/Transition System | MVP | Presentation | Zone entry card, scene transitions | S |
| 36 | Run Completion | MVP | Presentation | End-of-run summary, reward calc | M |

---

## Circular Dependencies

- **None found**. All dependency arrows point from higher-numbered layers to lower-numbered layers.

---

## High-Risk Systems

| System | Risk Type | Risk Description | Mitigation |
|--------|-----------|-----------------|------------|
| Skill Data System | Technical | C3: upgrade defs and VFX profiles must use pure data refs, not runtime types from higher layers. Violation would create inverted dependency (Foundation → Core). | GDD must explicitly document data-only contract. Review against C3 before implementation. |
| Event Bus | Technical | New system (C1). If message types aren't well-defined, the bus becomes a dumping ground for undocumented event strings, making debugging harder than direct calls. | Define core message type catalogue in GDD before L3 GDDs are written. |
| SkillPresentationAdapter | Technical | Uncoupled from template vendor code via bridge pattern. Timing must derive from SkillData + clip lengths, not FSM state reads. Failure = no animation feel at all. | Prototype in month 1 (concept risk item). Proof of concept with 1 skill before building 5-6. |
| Server Economy Validation | Scope | Full validation (time:dmg ratios, signed hashes) is Alpha tier. MVP uses trust-based currency with backend sync. Risk: exploit discovered before validation is built. | Acceptable for premium single-player game. Anti-cheat is a trust layer, not a gameplay requirement. |
| UI Panels | Scope | Editor/art bottleneck per PR-SCOPE. Draft Panel, Camp shell, HUD consume ~40-50% of MVP timeline. | Pre-prod UI canvases Day 1. Use placeholder sprites from template while pixel art is being created. |
| Unity 6000.3.11f1 | Technical | Post-cutoff engine. IL2CPP build validation, URP 17 render graph API changes, custom shader risk. | Weekly IL2CPP smoke test. Defer custom shaders to Vertical Slice. Rely on template's built-in URP pipeline. |
| Pillar 2 Delivery (Synergy) | Design | MVP has no Synergy System — Rune Draft offers standalone skills only. The game's namesake emergent discovery is absent until month 4-5. | Accepted scope decision (CD-SYSTEMS). Player-facing copy should manage expectations. 2-3 hard-coded pairs could be added for ~5-7% scope if P2 feel becomes critical. |
| Pillar 1 Narrative Track | Design | "Mechanical reward for lore-correct picks" is deferred. MVP lore is passive Codex text only. | Accepted scope decision. Codex UI quality (runic glyph, environmental memory ghosts) partially compensates. |

---

## Progress Tracker

| Metric | Count |
|--------|-------|
| Total systems identified | 42 |
| Design docs started | 12 |
| Design docs reviewed | 2 |
| Design docs approved | 1 |
| MVP systems designed | 35 / 35 |
| Vertical Slice systems designed | 0 / 3 |
| Alpha systems designed | 0 / 3 |
| Full Vision systems | 1 (Fusion Co-op) |

---

## Next Steps

- [x] Design MVP-tier systems in recommended design order (start with Game State Manager, Event Bus, Skill Data System)
- [ ] Pre-prod UI canvases for Draft Panel, Camp shell, and HUD while designing Foundation/Core GDDs
- [ ] Source/prototype pixel art for 1 hero, 1 basic enemy, 1 boss, and zone tiles
- [x] Run `/design-system game-state-manager` to author first Foundation GDD
- [ ] Run `/design-system event-bus` to define core message type catalogue before L3 GDDs
- [ ] Run `/design-system skill-data-system` to lock down data-only contract (blocks 8+ dependents)
- [ ] Run `/design-review` on each completed GDD
- [ ] Run `/gate-check pre-production` when all MVP GDDs are designed and reviewed
