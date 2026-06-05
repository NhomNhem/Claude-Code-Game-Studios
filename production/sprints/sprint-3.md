# Sprint 3 — 2026-06-04 to 2026-06-10

> **Review mode**: full

## Sprint Goal
Build core combat loop foundations — Hit Detection, Scene Management, and Damage & Health

## Capacity
- Total days: 5
- Buffer (20%): 1 day reserved
- Available: 4 days (32h)

## Tasks

### Must Have (Critical Path) — 13h
| ID | Task | Est. | Dependencies |
|----|------|------|-------------|
| HD-001 | Hitbox/Hurtbox Registration & Faction System | 3h | None |
| HD-002 | Hit Detection & Event Dispatch | 3h | HD-001 |
| SM-001 | Scene Load/Unload Core | 4h | None |
| SM-003 | Activation & Completion Flow | 3h | SM-001 |

### Should Have — 14h
| ID | Task | Est. | Dependencies |
|----|------|------|-------------|
| EPICS-DH | Create Damage & Health epic + stories | 2h | None (on-demand, parallel HD-001) |
| EPICS-EA | Create Enemy AI epic + stories | 2h | None (on-demand) |
| HD-003 | Per-Target Hit Cooldown | 2h | HD-002 |
| SM-002 | Error Handling & Safety | 3h | SM-001 |
| DH-001 | Damage & Health core | 4h | HD-002 + EPICS-DH |
| EA-001 | Enemy AI (basic chase) | 3h | EPICS-EA |

### Nice to Have — 2h
| ID | Task | Est. | Dependencies |
|----|------|------|-------------|
| SM-004 | Preloading & Edge Cases | 2h | SM-003 |

### Deferred to Sprint 4
| Task | Reason |
|------|--------|
| OC-001 Basic Orbit Combat (1 fire skill) | Needs HD + DH + EA complete — too sequential |
| WS-001 Wave Spawning | Needs EA first — enemies need to exist |
| HUD Health/Combat display | Needs DH first — no health data to display |

## Risks
| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| R01: DH-001 has dual-dep on EPICS-DH + HD-002 | Medium | Medium | EPICS-DH is on-demand parallel; epic files now created in-progress |
| R02: Scene Management async edge cases (Unity) | Medium | Medium | SM-002/SM-004 are Should Have/Nice to Have — safe to defer |
| R03: Hit Detection depends on Unity trigger colliders w/ template | Low | Medium | Template has OnTriggerEnter — HD wraps, doesn't replace |
| R04: EA-001 blocked if EPICS-EA not done | Low | Medium | EPICS-EA is 2h Should Have — done early in sprint |
| R05: DH-001 + EA-001 both Should Have (14h) may overrun | Medium | Medium | Drop EA-001 if capacity runs short; DH-001 has priority |

## Definition of Done
- [ ] All Must Have tasks completed
- [ ] All tasks pass acceptance criteria
- [ ] QA plan exists (`production/qa/qa-plan-sprint-3.md`)
- [ ] All Logic/Integration stories have passing unit/integration tests
- [ ] Smoke check passed
- [ ] No S1 or S2 bugs in delivered features
- [ ] Design documents updated for any deviations
- [ ] Code reviewed and merged
