# Sprint 1 — 2026-06-02 to 2026-06-09

> **Review mode**: full

## Sprint Goal
Implement core infrastructure (Game State Machine, Event Bus, Time System) so that all downstream systems have a foundation to build on.

## Capacity
- Total days: 5 (working)
- Buffer (20%): 1 day reserved
- Available: 4 days (24h)

## Tasks

### Must Have (Critical Path)
| ID | Story | Est. Days | Dependencies | Acceptance Criteria |
|----|-------|-----------|-------------|-------------------|
| FI-001 | GState Core State Machine | 1.5 | None | 21 ACs — Edit Mode testable. State transitions, thread safety, null-safe defaults, Pause/InRun/Camp/HeroCamp |
| FI-002 | Event Bus Core | 1.5 | None | Type-filtered pub/sub, warm/cold start, depth limit (17), unsubscription safety, struct-as-event support |
| FI-003 | Time System Core | 1.0 | FI-001 (pause/resume via GState) | Custom time scales, pause freeze, hit-stop isolation, `_prePauseTimeScale` preservation |

### Should Have
| ID | Story | Est. Days | Dependencies | Acceptance Criteria |
|----|-------|-----------|-------------|-------------------|
| FI-004 | Hit-Stop | 0.5 | FI-003 (Time System) | Duration scale (0.25×), overlap behavior, pause-immune, no GC per trigger |
| SD-001 | Skill Definition Schema | 0.5 | None | ScriptableObject schema, required fields, element type, tier range, AC list |

## Producer Gate Advisories (accepted)
- **Milestone alignment**: M0 Backend Foundation goal is login/currency flow. Sprint 1 builds game-side infrastructure only. Milestone re-scoping deferred — will reconcile before M0 deadline.
- **FI-003 design approach**: Dependency on GState for pause/resume. If event-driven integration required, FI-005 (GState→EB) may need to be pulled in. Approach to be clarified before FI-003 implementation begins.
- **First-sprint risk**: Template compatibility (VContainer, Unity 6), Input System 1.19.0 unknowns, solo velocity baseline unestablished. 0.5d buffer absorbed into general 20% reserve.
- **FI-004 estimate**: 0.5d is optimistic (Unity tween recovery, input gating, screen flash). Flagged as likely spillover.

## Risks
| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| R01: Template compatibility unknown | Medium | High — VContainer registration, existing manager singletons | All 21 GState ACs are Edit Mode — catch early. No template vendor code modified. |
| R02: First sprint velocity baseline | High | Medium — no historical data | Conservative estimates; 20% buffer; first sprint is discovery |
| R03: FI-003 integration dependency gap | Medium | Medium — direct coupling vs event-driven unresolved | Clarify before FI-003 implementation. May need to pull FI-005 into Must Have. |
| R04: Unity 6000 IL2CPP generics (Event Bus) | Medium | High — `System.Action<T>` in AOT | Event Bus designed with explicit type registration, no runtime type baking |

## Dependencies on External Factors
- Unity 6000.3.11f1 project must build without Firebase/Fusion defines
- Template's existing `GameManager` singleton must coexist with VContainer-registered GState
- No server or backend dependency for Sprint 1

## Definition of Done
- [ ] All Must Have tasks completed
- [ ] All stories pass acceptance criteria
- [ ] QA plan exists (`production/qa/qa-plan-sprint-1.md`)
- [ ] All Logic/Integration stories have passing unit/integration tests
- [ ] Smoke check passed
- [ ] No S1 or S2 bugs in delivered features
- [ ] Design documents updated for any deviations
- [ ] Code reviewed and merged
