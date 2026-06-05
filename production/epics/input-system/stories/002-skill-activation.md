# Story 002: Skill Activation & Hold-to-Aim

- **Epic**: Input System
- **System**: Input System
- **Type**: Logic
- **Priority**: P0
- **Estimate**: 3h
- **Status**: Complete
- **Last Updated**: 2026-06-02

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-input-005` | Skill slot 1 forward-aim calls UseSkill(1, Vector2.zero) | ✅ ADR-003 |
| `TR-input-006` | Hold skill slot 2 directed-aim calls UseSkill(2, lastAimDir) on release | ✅ ADR-003 |
| `TR-input-015` | Directed-aim hold interrupted by forward-aim works | ✅ ADR-003 |
| `TR-input-014` | Skill slot out of range no-ops | ✅ ADR-003 |

## ADR Guidance

**ADR-003 (Input System & InputRouter Wrapper Pattern):**
- Skill actions are declared in the Gameplay action map: UseSkill1–4
- Forward-aim skills fire instantly on press (`UseSkill(slotIndex, Vector2.zero)`)
- Directed-aim skills: on press begin piping `GetAimInput()` into `UpdateDirectionalAim()` each frame while held; on release call `UseSkill(slotIndex, lastAimDir)`
- Hold-to-aim state is tracked per slot in InputRouter
- Slot out-of-range guarded by `characterEntity.GetSkillCount()` before routing
- Hold-to-aim state flushed on map disable (per TR-input-010, covered in Story 003)
- Register as interface singleton in TinyRiftScope (per ADR-001)

## Description

Implement skill activation routing in InputRouter: forward-aim (instant press-to-cast) and directed-aim (hold-to-aim then release-to-cast). Track per-slot hold state so `UpdateDirectionalAim()` pipes continuously while held. Guard skill slot indices against `characterEntity.GetSkillCount()` — out-of-range slots silently no-op. Ensure a directed-aim hold doesn't block firing a forward-aim skill in another slot.

## Design

### Per-Slot Hold State

```csharp
public class InputRouter : IInputRouter
{
    private readonly int[] _skillSlots = { 0, 1, 2, 3 }; // 1-based indexing
    private readonly HashSet<int> _heldSlots = new();
    private readonly Dictionary<int, Vector2> _lastAimDirs = new();

    private void OnSkillPressed(int slotIndex)
    {
        if (slotIndex >= _characterEntity.GetSkillCount())
            return; // TR-input-014: out of range no-op

        if (IsDirectedAimSkill(slotIndex))
        {
            // Begin tracking hold
            _heldSlots.Add(slotIndex);
            _lastAimDirs[slotIndex] = GetAimInput();
        }
        else
        {
            // Forward-aim: fire instantly (TR-input-005)
            _characterEntity.UseSkill(slotIndex, Vector2.zero);
        }
    }

    private void OnSkillReleased(int slotIndex)
    {
        if (slotIndex >= _characterEntity.GetSkillCount())
            return;

        if (_heldSlots.Remove(slotIndex))
        {
            // Directed-aim: cast on release with last known direction (TR-input-006)
            Vector2 lastDir = _lastAimDirs.GetValueOrDefault(slotIndex, Vector2.zero);
            _characterEntity.UseSkill(slotIndex, lastDir);
            _lastAimDirs.Remove(slotIndex);
        }
    }

    public void Update()
    {
        // Update aim direction for all held directed-aim slots
        Vector2 aimDir = GetAimInput();
        foreach (int slot in _heldSlots)
        {
            _lastAimDirs[slot] = aimDir;
            _characterEntity.UpdateDirectionalAim(aimDir);
        }
    }
}
```

### Directed-Aim + Forward-Aim Interruption (TR-input-015)

When a directed-aim skill is held in slot 2 and the player presses skill slot 1 (forward-aim):
- `OnSkillPressed(1)` fires independently — slot 1 is not in `_heldSlots`, so it routes as forward-aim instantly
- Slot 2's hold state remains intact — its aim direction continues to update
- This works naturally because each slot tracks its state independently in `_heldSlots`

```csharp
// Forward-aim in slot 1 doesn't affect held state of slot 2
// No special handling needed — per-slot tracking ensures isolation
```

### Skill Type Determination

The skill type (forward-aim vs directed-aim) can be determined by:
1. An `ISkillDataProvider` interface that InputRouter queries, OR
2. A simple configuration array passed to InputRouter

Recommendation: use approach 1 once `ISkillDataProvider` exists. For initial implementation, use a hardcoded config array `_skillAimTypes[slotIndex]` that maps each slot to ForwardAim or DirectedAim, replaceable later when the skill data system is integrated.

```csharp
private enum SkillAimType { ForwardAim, DirectedAim }
private readonly SkillAimType[] _skillAimTypes = new SkillAimType[4];
```

## Acceptance Criteria

1. **Forward-aim press**: Pressing skill slot 1 (forward-aim) calls `characterEntity.UseSkill(1, Vector2.zero)` exactly once.
2. **Directed-aim hold then release**: Holding skill slot 2 (directed-aim) for 400ms then releasing calls `characterEntity.UseSkill(2, lastAimDir)` exactly once with the last known aim direction.
3. **Directed-aim continuous update**: While slot 2 is held, `characterEntity.UpdateDirectionalAim()` is called each frame with the current aim direction.
4. **Forward-aim during directed-aim hold**: While slot 2 is held, pressing slot 1 (forward-aim) fires `UseSkill(1, Vector2.zero)` normally — slot 2's hold state is not affected.
5. **Out-of-range slot**: Pressing skill slot 5 (when only 4 slots exist) calls no method on CharacterEntity.
6. **Out-of-range release**: Releasing skill slot 5 similarly no-ops.
7. **Multiple held slots**: Holding slot 2 and slot 3 simultaneously updates both aim directions each frame and releases both correctly.

## QA Test Cases

- **AC1 (Forward-aim press)**: Mock CharacterEntity. Press skill slot 1. Verify UseSkill(1, Vector2.zero) called exactly once.
- **AC2 (Directed-aim hold+release)**: Hold slot 2 for 5 frames, release. Verify UseSkill(2, lastAimDir) called exactly once with non-zero direction.
- **AC3 (Continuous update during hold)**: Hold slot 2 for 3 frames. Verify UpdateDirectionalAim() called each frame.
- **AC4 (Forward-aim during hold)**: Hold slot 2, press slot 1. Verify UseSkill(1, Vector2.zero) called. Verify slot 2 held state intact.
- **AC5 (Out-of-range press)**: Press skill slot 5 (4 slots exist). Verify no CharacterEntity method called.
- **AC6 (Out-of-range release)**: Release skill slot 5. Verify no CharacterEntity method called.
- **AC7 (Multi-hold)**: Hold slots 2 and 3 for 3 frames, release. Verify both UpdateDirectionalAim called each frame. Verify both UseSkill called on release.

**Edge cases**: Zero-duration hold (press+release same frame), device switch mid-hold.

## Test Evidence Path

- `Assets/_TinyRift/Tests/EditMode/Input/SkillActivationTests.cs`
- Mock CharacterEntity to verify UseSkill calls with correct slot index and direction
- Verify UpdateDirectionalAim is called every frame during hold
- Verify out-of-range slots never reach CharacterEntity
- Verify forward-aim fires correctly during directed-aim hold

## Dependencies

- **Depends on**: Story 001 (InputRouter Core — action maps, movement, aim)
- **Unlocks**: Story 003 (Pause Toggle & Menu Navigation), Story 004 (Edge Cases)

## Risks

- **LOW**: Skill type (forward vs directed) may be determined by skill data system not yet built. Mitigation: use config array as placeholder; swap for ISkillDataProvider integration later.
- **LOW**: Hold-to-aim state could leak if Update() stops being called. Mitigation: hold state is per-frame updated and map disable cleans it up (Story 003).
