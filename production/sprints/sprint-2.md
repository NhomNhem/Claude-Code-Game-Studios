# Sprint 2 — 2026-06-03 to 2026-06-10

> **Review mode**: full

## Sprint Goal
Build production Input System and Object Pooling modules.

## Capacity
- Total days: 5
- Buffer (20%): 1 day reserved
- Available: 4 days (24h)

## Tasks

### Must Have (Critical Path) — 10h
| ID | Task | Est. | Dependencies |
|----|------|------|-------------|
| IN-001 | InputRouter Core — Action Maps & Movement | 0.5d (4h) | GState + EventBus (Sprint 1) |
| IN-002 | Skill Activation & Hold-to-Aim | 0.5d (4h) | IN-001 |
| IN-003 | Pause Toggle & Menu Navigation | 0.25d (2h) | IN-001, IN-002 |

### Should Have — 12h
| ID | Task | Est. | Dependencies |
|----|------|------|-------------|
| PL-003 | PoolManager Core (ObjectPool<T> wrapper, IPoolable) | 0.5d (4h) | None (standalone) |
| PL-004 | Pool Growth, Safety & AOT Preservation | 0.4d (3h) | PL-003 |
| IN-004 | Edge Cases — Device Disconnect, Rebinds | 0.6d (5h) | IN-002, IN-003 |

### Nice to Have — 3h
| ID | Task | Est. | Dependencies |
|----|------|------|-------------|
| HD-001 | Hitbox/Hurtbox Registration & Faction System | 0.4d (3h) | None (standalone) |

### Deferred to Sprint 3
| Task | Reason |
|------|--------|
| VS-INT Vertical Slice Integration | Integration deserves focused sprint, not rushed |

## Risks
| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| R01: Input System 1.19.0 post-cutoff | Medium | High | ACs are Edit Mode testable; catch early |
| R02: Must Have is sequential (IN-001→002→003) | Low | Medium | Only 10h — 14h buffer absorbs any slip |
| R03: IL2CPP AOT for ObjectPool<T> generics | Medium | High | PL-004 explicitly covers link.xml preservation |
| R04: Solo dev — no parallel execution on sequential chain | Medium | Medium | PL-003/PL-004 are standalone and can run alongside if context-switching is acceptable |

## Definition of Done
- [ ] All Must Have tasks completed
- [ ] All tasks pass acceptance criteria
- [ ] QA plan exists (`production/qa/qa-plan-sprint-2.md`)
- [ ] All Logic/Integration stories have passing unit/integration tests
- [ ] Smoke check passed
- [ ] No S1 or S2 bugs in delivered features
- [ ] Design documents updated for any deviations
- [ ] Code reviewed and merged
