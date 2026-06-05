# Test Infrastructure

**Engine**: Unity 6000.3.11f1 (Unity 6 Update 3)
**Test Framework**: Unity Test Framework (NUnit-based)
**CI**: `.github/workflows/tests.yml`
**Setup date**: 2026-06-01

## Directory Layout

```
tests/
  unit/           # Auto-generated smoke seed docs
  integration/    # Smoke test docs
  smoke/          # Critical path test list for /smoke-check gate
  evidence/       # Screenshot logs and manual test sign-off records

Assets/_TinyRift/Tests/
  EditMode/       # Unit tests (pure logic — formulas, state machines, data validation)
  PlayMode/       # Integration tests (cross-system, save/load, physics, coroutines)
```

## Running Tests

Unity Test Framework runs via the Test Runner window:
Window → General → Test Runner

- **EditMode tests**: Run in the Test Runner without entering Play Mode
- **PlayMode tests**: Run in a simulated game scene

## Test Naming

- **Files**: `[System][Feature]Tests.cs` (e.g., `SaveProfileSerializationTests.cs`)
- **Methods**: `[Method]_[Scenario]_[Expected]` (e.g., `PersistStateAsync_MultipleRapidCalls_OneDiskWrite()`)
- **Namespace**: `Tests.[System]` (e.g., `Tests.SaveProfile`)

## Story Type → Test Evidence

| Story Type | Required Evidence | Location |
|---|---|---|
| Logic | Automated unit test — must pass | Assets/_TinyRift/Tests/EditMode/ |
| Integration | Integration test OR playtest doc | Assets/_TinyRift/Tests/PlayMode/ |
| Visual/Feel | Screenshot + lead sign-off | tests/evidence/ |
| UI | Manual walkthrough OR interaction test | tests/evidence/ |
| Config/Data | Smoke check pass | tests/smoke/ |

## CI

Tests run automatically on every push to `main` and on every pull request.
A failed test suite blocks merging.
