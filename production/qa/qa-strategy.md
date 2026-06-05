# QA Strategy — Tiny Rift Survivors

## Testing Philosophy

Verification-driven development: tests before implementation for gameplay systems,
evidence-based validation for UI and content. Backend testing is paramount.
Fusion Shared Mode validated via smoke test before any multiplayer gameplay code.

## Test Framework

- **Unity Test Framework** (UTF, built-in)
- **Play Mode** tests for integration/regression
- **Edit Mode** tests for isolated unit tests
- **Manual testing** for UI, flow, animation feel, and Fusion networking
- **Server-side testing** via Node.js test runner
- **Fusion Shared Mode**: smoke test via editor + Photon Cloud (no automated framework yet)

## Test Categories

### Unit Tests (Edit Mode)
- Balance formulas (damage, XP curves, scaling)
- Skill calculations (cooldown, duration, modifiers)
- Enemy stat calculations
- Wave progression math
- Currency operations (add, spend, validate)
- BackendSettings.asset deserialization
- SkillPresentationAdapter parameter validation

### Integration Tests (Play Mode)
- Skill → enemy damage flow
- XP pickup → level-up → stat change
- Wave start → enemy spawn → wave complete
- Shop purchase → stat modification
- **WebSocket connection lifecycle** (connect → auth → heartbeat → reconnect)
- **Login → Profile → Currency round-trip**
- **Fusion Shared Mode smoke test**: NetworkRunner.Start(GameMode.Shared) → Connected → room create → map load → spawn
- **Fusion disconnect/cleanup**: runner shutdown, no dangling objects

### Server Tests
- Auth endpoint: valid login, invalid login, duplicate register
- Profile endpoint: read owned, read foreign, update validation
- Currency endpoint: add authorized, spend authorized, spend insufficient, concurrency conflict

### Manual Testing
- UI navigation flows
- Visual polish
- Audio integration
- Performance profiling
- Offline mode fallback behavior
- Network disconnect/reconnect handling
- **Animation feel**: Skill casting responsiveness, hit-stop timing, VFX alignment
- **Fusion Shared Mode**: 2 editor instances in same room, latency observation, authority transfer

## QA Gates

| Phase | Gate | Requirements |
|-------|------|-------------|
| M0 | Backend Ready | Login→Profile→Currency E2E passes, Offline fallback works |
| M0.5 | Pipe Ready | Fusion Shared Mode smoke test passes, SkillPresentationAdapter prototype compiles |
| M1 | Content Complete | All systems tested, playable run, no critical bugs |
| M2 | Feature Complete | Full run loop, backend sync verified |
| M3 | Ship | Smoke check pass, all critical bugs fixed, performance OK |

## Backend QA Focus
- Connection resilience: reconnect, timeout, invalid URL
- Auth security: SQL injection, token expiry, replay attacks
- Currency integrity: double-spend prevention, sync conflict resolution
- Offline fallback: seamless mode switching, no data loss

## Fusion QA Focus
- **Connection lifecycle**: Start → Connected → RoomJoined → SceneLoaded
- **Authority transfer**: disconnect host while peer playing, verify migration
- **Networked objects**: spawn/despawn sync, no orphan references
- **Disconnect resilience**: reconnect handling if Photon Cloud drops
- **No regression**: Fusion session does not affect WebSocketSQL auth/profile/economy

## Bug Tracking

Bugs filed as markdown in `production/qa/bugs/` using the bug report template.
Severity: Critical / Major / Minor / Cosmetic.
Priority: P0 (blocker) / P1 (must fix before launch) / P2 (nice to have) / P3 (defer).

## Regression Strategy

- Every bug fix includes a regression test
- Critical path (menu → play → wave → upgrade → replay) tested before each release
- Backend changes trigger full E2E test suite
- Every currency mutation has a server-side unit test
- Fusion Shared Mode changes: offline gameplay must never regress (Fusion code is `#if FUSION2`-gated)

## QA Cadence

- **Daily**: Unit tests on any code change
- **Sprint-end**: Full play mode test suite + manual test pass
- **Milestone-end**: Smoke check + soak test
- **Pre-release**: Full regression + performance profile + release checklist
