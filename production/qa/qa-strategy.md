# QA Strategy — Tiny Rift Survivors

## Testing Philosophy

Verification-driven development: tests before implementation for gameplay systems,
evidence-based validation for UI and content.

## Test Framework

- **Unity Test Framework** (UTF, built-in)
- **Play Mode** tests for integration/regression
- **Edit Mode** tests for isolated unit tests
- **Manual testing** for UI, flow, and feel

## Test Categories

### Unit Tests (Edit Mode)
- Balance formulas (damage, XP curves, scaling)
- Skill calculations (cooldown, duration, modifiers)
- Enemy stat calculations
- Wave progression math
- Save/load serialization

### Integration Tests (Play Mode)
- Skill → enemy damage flow
- XP pickup → level-up → stat change
- Wave start → enemy spawn → wave complete
- Shop purchase → stat modification

### Manual Testing
- UI navigation flows
- Visual polish
- Audio integration
- Performance profiling
- Feel and game juice

## QA Gates

| Phase | Gate | Requirements |
|-------|------|-------------|
| Foundation | Gate → Systems Design | Prototype plays, no crashes |
| Core Content | Gate → Pre-Production | All systems unit tested, vertical slice playable |
| Progression | Gate → Production | Full run loop, save/load verified |
| Release | Gate → Launch | Smoke check pass, no critical bugs, performance OK |

## Bug Tracking

Bugs filed as markdown in `production/qa/bugs/` using the bug report template.
Severity: Critical / Major / Minor / Cosmetic.
Priority: P0 (blocker) / P1 (must fix before launch) / P2 (nice to have) / P3 (defer).

## Regression Strategy

- Every bug fix includes a regression test
- Critical path (menu → play → wave → upgrade → replay) tested before each release
- Balance changes trigger formula test suite

## QA Cadence

- **Daily**: Unit tests on any code change
- **Sprint-end**: Full play mode test suite + manual test pass
- **Milestone-end**: Smoke check + soak test
- **Pre-release**: Full regression + performance profile + release checklist
