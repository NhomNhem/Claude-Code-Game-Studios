# Active Session State

<!-- STATUS -->
- **Stage**: Production
- **Epic**: Orbit Combat (SYS-020) — passive orbital auto-attack system
- **Review Mode**: full
- **Last Updated**: 2026-06-05
- **Next Gate**: `/gate-check production-to-polish` — after all core mechanics implemented
<!-- /STATUS -->

<!-- QA-PLAN: 2026-06-02 | System: Sprint 1 | Plan written: production/qa/qa-plan-sprint-1-2026-06-02.md -->
<!-- QA-PLAN: 2026-06-03 | System: Sprint 2 | Plan written: production/qa/qa-plan-sprint-2-2026-06-03.md -->

## Current Focus

**Stage advanced: Pre-Production → Production** (gate check: CONCERNS verdict, accepted by user).

### Vertical Slice — Phase 4: Implement
- **Concept**: Tiny Rift Survivors
- **Validation**: "Does a player experience the Riftwalker fantasy of channeling elemental power to fight void-spawned enemies within 3 minutes — and can we build one complete loop in 5-7 days?"
- **Systems in scope**: Input (movement), Hit Detection, Object Pooling, Damage & Health, Orbit Combat (1 fire skill), Enemy AI (basic chase), Wave Spawning (timer), HUD (minimal), Scene Flow (Menu → Game → GameOver)
- **Art quality**: Placeholder (colored shapes)
- **Existing systems used**: GameState, EventBus, TimeSystem, SkillData
- **Start date**: 2026-06-02
**Pre-Production first iteration**: Accept all 6 ADRs, UX specs for key screens, build foundation artifacts.

### ADR Status — All 6 Accepted this session
- ADR-001: VContainer DI Architecture — **Accepted**
- ADR-002: Event Bus Contract — **Accepted**
- ADR-003: Input System Wrapper — **Accepted**
- ADR-004: Time System & Hit-Stop — **Accepted**
- ADR-005: Object Pooling Strategy — **Accepted**
- ADR-006: Save/Profile Serialization — **Accepted**

### UX Specs
- **Main Menu** — `design/ux/main-menu.md` (APPROVED via /ux-review)
- **Hero Camp** — `design/ux/hero-camp.md` (APPROVED after revision)
- **HUD** — `design/ux/hud.md` (APPROVED via /ux-review — 8 sections, Visual Budget + Notification Priority added per review)
- **Pause Menu** — `design/ux/pause-menu.md` (APPROVED via /ux-review — 4 issues fixed: Platform Target, error states, null handling, resolution criterion)

### Architecture & Engineering
- **Control Manifest** — `docs/architecture/control-manifest.md` created (63 Required patterns, 19 Forbidden approaches, 10 Guardrails from 6 ADRs)
- **ADR-001 updated**: `IProfileService → IPersistStateService` renamed, moved Core→Foundation, reconciled with ADR-006
- **Architecture doc updated**: ADR Audit now shows "6 ADRs Accepted" (was "No ADRs exist")

### Pre-Production → Production Gate
**Date**: 2026-06-01
**Verdict**: FAIL (8 blocking issues)
**Resolved this session**: 7 of 8
- ✅ ADR-001/ADR-006 naming conflict — Fixed
- ✅ Architecture doc stale — Fixed
- ✅ Pause menu UX spec — Written
- ✅ Control manifest — Written
- ✅ Epics created — 12 epics (Foundation: 5, Core: 7)
- ✅ Stories created — Foundation Infrastructure epic: 6 stories, all implemented & tested
- ✅ Sprint plan — Sprint 1 created & executed
**Remaining blockers**: TR registry, vertical slice

## Active Tasks
- [x] Accept all 6 ADRs (Proposed → Accepted)
- [x] HUD UX spec: Philosophy → IA → Layout → Elements → Dynamic Behaviors → Platform → Accessibility → Open Questions
- [x] /ux-review hud — NEEDS REVISION → 3 issues fixed → APPROVED
- [x] /gate-check pre-production-to-production — FAIL (8 blockers)
- [x] Fix ADR-001/ADR-006 naming conflict (IProfileService → IPersistStateService)
- [x] Fix architecture doc (ADR Audit: 6 ADRs Accepted)
- [x] Pause menu UX spec — all 14 sections written
- [x] Create control manifest — `docs/architecture/control-manifest.md`
- [x] /ux-review on pause-menu → APPROVED (4 issues fixed)
- [x] Create accessibility-requirements.md — `design/ux/accessibility-requirements.md` (Standard tier, WCAG-AA, 9 sections, committed)
- [x] IN-002 Skill Activation & Hold-to-Aim — Complete (all ACs verified, 7 tests)
## Session Extract — /story-done 2026-06-05
- Story: `production/epics/scene-management/stories/002-error-handling.md` — Error Handling & Safety (SM-002)
- Verdict: COMPLETE (code + tests already existed as part of SceneController implementation)
- Tech debt logged: None
- Next recommended: SM-004 Preloading & Edge Cases

## Session Extract — /story-done 2026-06-05
- Verdict: COMPLETE WITH NOTES
- Story: `production/epics/scene-management/stories/004-preloading-edge-cases.md` — Preloading & Edge Cases (SM-004)
- Tech debt logged: None
- Next recommended: Orbit Combat or Wave Spawning (vertical slice gaps)

## Session Extract — /create-epics 2026-06-05
- Epic: `production/epics/orbit-combat/EPIC.md` — Orbit Combat System
- Stories: 4 proposed (Orbit Ring Core, Hit Cooldown & Multiple Rings, Upgrades & Real-Time Changes, Orbit Lifecycle & Transitions)
- Next recommended: Run `/architecture-decision "Orbit Combat & Targeting Priority"` (ADR-008) then `/create-stories orbit-combat`

## Session Extract — /architecture-decision 2026-06-05
- ADR: ADR-008 Orbit Combat & Targeting Priority
- Status: Accepted
- Decision: Hybrid service + pooled component approach. Contact-based targeting via trigger colliders.
- Dependencies: ADR-001, ADR-002, ADR-004, ADR-005
- Engine risk: LOW (standard Unity patterns)
- Registry updated: 2 new entries (orbit_combat performance budget, orbit_projectile_positioning API decision)
- Next: /create-stories orbit-combat

## Session Extract — /create-stories 2026-06-05
- Epic: Orbit Combat (SYS-020)
- Stories: 4 written and Ready
  - ORBIT-001: Orbit Ring Core — Logic — ADR-008
  - ORBIT-002: Hit Cooldown & Multiple Rings — Logic — ADR-008
  - ORBIT-003: Upgrades & Real-Time Changes — Integration — ADR-008
  - ORBIT-004: Orbit Lifecycle & Transitions — Integration — ADR-008
- Next recommended: /story-readiness then /dev-story on ORBIT-001

- [ ] Create interaction-patterns.md
- [ ] Populate TR registry (`docs/architecture/tr-registry.yaml`)
- [x] Create epics + stories — 12 epics written (Foundation: 5, Core: 7), index updated
- [x] Create stories — Foundation Infrastructure: 6 stories written, implemented, 86 tests passing
- [x] Create sprint plan — Sprint 1 created & executed
- [ ] Build vertical slice (`/vertical-slice`)
- [x] Foundation Infrastructure epic: 6/6 stories Complete (all ACs verified)
- [x] Milestone review saved: `production/milestones/foundation-infrastructure-review.md`

## Known Technical Debt
- `FUSION_*` defines on Android/WebGL are stale (2.0.8 vs installed 2.1.1) — needs cleanup
- `FIREBASE` define still present on Standalone — needs removal
- Product Name `Tiny-Rift-Survivors-GameClient` and Company Name `DefaultCompany` — needs rename before EA
- `design/ux/interaction-patterns.md` not yet created
- Player journey map (`design/player-journey.md`) does not exist
- No architecture review report exists (must be in fresh session)
- Feature-layer ADRs (Damage, Orbit, Burst, Rune Draft, Enemy AI, Wave Spawning) not yet written

## Session Extract — /story-done 2026-06-02
- Verdict: COMPLETE
- Story: `production/epics/foundation-infrastructure/stories/002-event-bus-core.md` — Event Bus Core
- Tech debt logged: None
- Next recommended: FI-003 Time System Core

## Session Extract — /story-done 2026-06-02
- Verdict: COMPLETE WITH NOTES
- Story: `production/epics/foundation-infrastructure/stories/001-gstate-core-state-machine.md` — GState Core State Machine
- Tech debt logged: None
- Next recommended: FI-002 Event Bus Core

## Session Extract — /story-done 2026-06-02
- Verdict: COMPLETE WITH NOTES
- Story: `production/epics/foundation-infrastructure/stories/003-time-system-core.md` — Time System Core
- Tech debt logged: None
- Next recommended: SD-001 Skill Definition Schema or Sprint Close-Out

## Session Extract — /story-done 2026-06-02
- Verdict: COMPLETE WITH NOTES
- Story: `production/epics/foundation-infrastructure/stories/004-hit-stop.md` — Hit-Stop
- Tech debt logged: None
- Next recommended: SD-001 Skill Definition Schema or Sprint Close-Out

## Session Extract — /dev-story 2026-06-02
- Story: `production/epics/foundation-infrastructure/stories/001-gstate-core-state-machine.md` — GState Core State Machine
- Files changed: `Assets/_TinyRift/Runtime/GameState/GamePhase.cs`, `Assets/_TinyRift/Runtime/GameState/IGameStateManager.cs`, `Assets/_TinyRift/Runtime/GameState/GameStateManager.cs`
- Test written: `Assets/_TinyRift/Tests/EditMode/GameStateManager/GameStateManagerCoreTests.cs` (21 tests)
- Blockers: None
- Next: FI-002 Event Bus Core

## Session Extract — /dev-story 2026-06-02
- Story: `production/epics/foundation-infrastructure/stories/006-gstate-time-integration.md` — GState → Time System Integration
- Files changed: `Assets/_TinyRift/Runtime/Time/TimeManager.cs`
- Test written: `Assets/_TinyRift/Tests/EditMode/TimeSystem/TimeSystemGStateIntegrationTests.cs` (9 tests)
- Bug fix: EventBus namespace collision — used type alias `EventBusType = TinyRift.Runtime.EventBus.EventBus`
- Blockers: None
- Next: Milestone review / sprint close-out

## Session Extract — /milestone-review 2026-06-02
- Milestone: Foundation Infrastructure Epic
- Verdict: GO — 100% complete, 86 tests passing, 0 blockers
- Producer assessment: ON TRACK
- Review saved: `production/milestones/foundation-infrastructure-review.md`
- Next recommended: pre-load next epic or run architecture review

## Session Extract — /story-done 2026-06-02
- Verdict: COMPLETE WITH NOTES
- Story: `production/epics/input-system/stories/001-input-router-core.md` — InputRouter Core — Action Maps & Movement
- Tech debt logged: None
- Next recommended: IN-002 Skill Activation & Hold-to-Aim

## Session Extract — /dev-story 2026-06-02
- Story: `production/epics/input-system/stories/002-skill-activation.md` — Skill Activation & Hold-to-Aim
- Files changed: `Assets/_TinyRift/Runtime/Foundation/Input/IInputRouter.cs`, `Assets/_TinyRift/Runtime/Foundation/Input/InputRouter.cs`
- Test written: `Assets/_TinyRift/Tests/EditMode/Input/SkillActivationTests.cs` (7 tests)
- Blockers: None
- Next: /code-review then /story-done

## Session Extract — /story-done 2026-06-02
- Verdict: COMPLETE WITH NOTES
- Story: `production/epics/input-system/stories/002-skill-activation.md` — Skill Activation & Hold-to-Aim
- Tech debt logged: None
- Next recommended: IN-003 Pause Toggle & Menu Navigation

## Session Extract — /dev-story 2026-06-02
- Story: `production/epics/input-system/stories/003-pause-menu-nav.md` — Pause Toggle & Menu Navigation
- Files changed: `IInputRouter.cs`, `InputRouter.cs`, `InputRouterCoreTests.cs`, `SkillActivationTests.cs`
- Test written: `Assets/_TinyRift/Tests/EditMode/Input/PauseMenuNavTests.cs` (15 tests)
- Blockers: None
- Next: /code-review then /story-done

## Session Extract — /story-done 2026-06-02
- Verdict: COMPLETE WITH NOTES
- Story: `production/epics/input-system/stories/003-pause-menu-nav.md` — Pause Toggle & Menu Navigation
- Tech debt logged: None
- Next recommended: IN-004 Edge Cases — Device Disconnect, Rebinds
## Session Extract — /dev-story 2026-06-02
- Story: production/epics/input-system/stories/004-edge-cases.md — Edge Cases — Device Disconnect, Rebinds, State Safety
- Files changed: Assets/_TinyRift/Runtime/Foundation/Input/IInputRouter.cs, Assets/_TinyRift/Runtime/Foundation/Input/InputRouter.cs, Assets/_TinyRift/Tests/EditMode/Input/EdgeCaseTests.cs
- Test written: Assets/_TinyRift/Tests/EditMode/Input/EdgeCaseTests.cs
- Blockers: None
- Next: /code-review Assets/_TinyRift/Runtime/Foundation/Input/IInputRouter.cs Assets/_TinyRift/Runtime/Foundation/Input/InputRouter.cs Assets/_TinyRift/Tests/EditMode/Input/EdgeCaseTests.cs then /story-done production/epics/input-system/stories/004-edge-cases.md
## Session Extract — /story-done 2026-06-02
- Verdict: COMPLETE
- Story: production/epics/input-system/stories/004-edge-cases.md — Edge Cases — Device Disconnect, Rebinds, State Safety
- Tech debt logged: None
- Next recommended: PL-003 PoolManager Core
## Session Extract — /story-done 2026-06-02
- Verdict: COMPLETE WITH NOTES
- Story: production/epics/network-pooling/stories/003-poolmanager-core.md — PoolManager Core
- Tech debt logged: None
- Next recommended: Pool Growth, Safety & AOT Preservation (production/epics/network-pooling/stories/004-pool-growth-safety-aot.md)

## Session Extract — /story-done 2026-06-03
- Verdict: COMPLETE WITH NOTES
- Story: production/epics/network-pooling/stories/004-pool-growth-safety-aot.md — Pool Growth, Safety & AOT Preservation
- Tech debt logged: None
- Next recommended: Sprint close-out (all Must Have/Should Have stories complete)

## Session Extract — /story-done 2026-06-04
- Verdict: COMPLETE WITH NOTES
- Story: `production/epics/hit-detection/stories/001-hitbox-hurtbox-registration.md` — Hitbox/Hurtbox Registration & Faction System
- Tech debt logged: None
- Next recommended: HD-002 Hit Detection & Event Dispatch

## Session Extract — /story-done 2026-06-04
- Verdict: COMPLETE WITH NOTES
- Story: `production/epics/hit-detection/stories/002-hit-event-dispatch.md` — Hit Detection & Event Dispatch
- Tech debt logged: None
- Next recommended: HD-003 Per-Target Hit Cooldown (should-have, 2h) or SM-003 Activation & Completion Flow (must-have, 3h)

## Session Extract — /dev-story 2026-06-04
- Story: `production/epics/scene-management/stories/003-activation-completion-flow.md` — Activation & Completion Flow (SM-003)
- Files changed: SceneController.cs, SceneReadyToActivateEvent.cs, SceneLoadCompleteEvent.cs, ILoadingTransitionProvider.cs, BuiltInFadeController.cs
- Next: /code-review then /story-done

## Session Extract — /story-done 2026-06-04
- Verdict: COMPLETE WITH NOTES
- Story: `production/epics/scene-management/stories/003-activation-completion-flow.md` — Activation & Completion Flow (SM-003)
- Tech debt logged: None
- Next recommended: see Phase 8 below

## Session Extract — /dev-story 2026-06-04
- Story: `production/epics/hit-detection/stories/003-per-target-cooldown.md` — Per-Target Hit Cooldown (HD-003)
- Files changed: `Assets/_TinyRift/Runtime/Combat/HitCooldownTracker.cs`, `Assets/_TinyRift/Runtime/Combat/HitCooldownConfig.cs`, `Assets/_TinyRift/Runtime/Combat/HitResolver.cs`
- Test written: `Assets/_TinyRift/Tests/EditMode/Combat/TestHitCooldown.cs` (20 tests)
- Blockers: None
- Next: /code-review then /story-done

## Session Extract — /story-done 2026-06-04
- Verdict: COMPLETE WITH NOTES
- Story: `production/epics/hit-detection/stories/003-per-target-cooldown.md` — Per-Target Hit Cooldown (HD-003)
- Tech debt logged: None
- Next recommended: DH-001 Damage & Health Core

## Session Extract — /dev-story 2026-06-04
- Story: `production/epics/damage-health/stories/001-damage-health-core.md` — Damage & Health Core (DH-001)
- Files changed: `HitEvent.cs` (added DamageValue), `HitResolver.cs` (pass damage on publish), + 9 runtime files (DamageAppliedEvent, EntityDiedEvent, DamageArgs, DamageResult, IHealth, HealthComponent, HealthRegistry, IDamageApplicationService, DamageApplicationService), + 2 test files
- Test written: `Assets/_TinyRift/Tests/EditMode/Combat/HealthComponentTests.cs` (14 tests), `Assets/_TinyRift/Tests/EditMode/Combat/DamageApplicationServiceTests.cs` (6 tests)
- Blockers: None
- Next: `/code-review` then `/story-done`

## Session Extract — /architecture-review 2026-06-05
- Verdict: CONCERNS
- Requirements: 12 total — 12 covered, 0 partial, 0 gaps
- New TR-IDs registered: 10 (TR-enemyai-003 through TR-enemyai-012)
- GDD revision flags: None
- Top ADR gaps: Enemy AI State Machine Architecture (recommended but not blocking)
- Report: docs/architecture/architecture-review-enemy-ai-2026-06-05.md

## Session Extract — /architecture-decision 2026-06-05
- ADR: ADR-007 Enemy AI State Machine Architecture
- Status: Proposed
- Decision: Hybrid approach (MonoBehaviour per enemy + service coordination)
- Dependencies: ADR-001, ADR-002, ADR-004, ADR-005
- Registry updated: 2 new stances (enemy_ai_service_registration, enemy_static_registration)
- GDD updated: EnemyStateMachine → EnemyAIState, GameplayLifetimeScope → TinyRiftScope

## Session Extract — /dev-story 2026-06-05
- Story: `production/epics/enemy-ai/stories/001-basic-chase-ai.md` — Basic Chase AI (EA-001)
- Files changed:
  - `Assets/_TinyRift/Runtime/EnemyAI/EnemyAIState.cs` — created (enum)
  - `Assets/_TinyRift/Runtime/EnemyAI/EnemyAIConfig.cs` — created (ScriptableObject)
  - `Assets/_TinyRift/Runtime/EnemyAI/EnemyChaseAI.cs` — created (MonoBehaviour, state machine)
  - `Assets/_TinyRift/Runtime/_TinyRift.Runtime.asmdef` — modified (added Assembly-CSharp ref for MonsterMovementComponent)
- Test written: `Assets/_TinyRift/Tests/EditMode/EnemyAI/EnemyChaseAITests.cs` (20 test functions)
- Blockers: None
- Deviations: Uses MonsterMovementComponent directly (not CharacterAttackComponent — monsters use template contact damage, not player attack component). Story's design note updated to reflect template reality.
- Code review: APPROVED WITH SUGGESTIONS (user accepted suggestions as fine)
- Next: `/story-done`

## Session Extract — /story-done 2026-06-05
- Verdict: COMPLETE WITH NOTES
- Story: `production/epics/enemy-ai/stories/001-basic-chase-ai.md` — Basic Chase AI (EA-001)
- Tech debt logged: None
- Next recommended: SM-002 Error Handling & Safety or EA-002 Movement & Attack Integration

## Session Extract — /dev-story 2026-06-05
- Story: `production/epics/enemy-ai/stories/002-movement-and-attack.md` — Movement & Attack Integration (EA-002)
- Files changed:
  - `Assets/_TinyRift/Runtime/EnemyAI/EnemyChaseAI.cs` — modified (CharacterAttackComponent integration + death handling + StopAttack)
  - `Assets/_TinyRift/Runtime/EnemyAI/EnemyHurtbox.cs` — created (IHurtbox impl, registers with HitDetectionRegistry)
- Test written: `Assets/_TinyRift/Tests/PlayMode/EnemyAI/EnemyMovementAttackIntegrationTests.cs` (5 test functions)
- Blockers: None
- Code review: APPROVED WITH SUGGESTIONS
- Next: `/story-done`

## Session Extract — /story-done 2026-06-05
- Verdict: COMPLETE WITH NOTES
- Story: `production/epics/enemy-ai/stories/002-movement-and-attack.md` — Movement & Attack Integration (EA-002)
- Tech debt logged: None
- Next recommended: SM-002 Error Handling & Safety or Sprint Close-Out
