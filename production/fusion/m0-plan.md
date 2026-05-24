# M0 Fusion Plan — Tiny Rift Survivors

## Goal

Fusion SDK install + one smoke-test COOP session in-editor.
Prove Fusion pipeline works end-to-end before any gameplay implementation.

## Key Finding: SDK Not Installed

Fusion SDK 2.0.8 is **not installed**. The template has extensive `#if FUSION2`
code (~2000+ lines across 8 files) but all of it compiles out on Standalone
(the development platform) because Standalone defines do not include `FUSION2`.

## Scope In

1. Install Fusion SDK 2.0.8 (exact version the template targets)
2. Add `FUSION2;FUSION_2;FUSION_2_0` to Standalone Scripting Define Symbols
3. Create Fusion AppId in Photon dashboard, configure in Unity
4. Create `FusionSmokeTest` scene or test flow:
   - Start `NetworkRunner` in `GameMode.Shared`
   - Runner creates a room
   - Load MapArena1 via `NetworkRunner.LoadScene()`
   - Spawn `GameplaySync` prefab
   - Verify `MatchStarted = true`, connection state = `Connected`
5. Cleanup: proper Fusion shutdown on disconnect

## Scope Out

- Colyseus/Fusion integration (separate concern)
- Full COOP gameplay (skills, enemies, drops — M1+)
- PVP modes (Arena, TDM, Battle Royale)
- Lobby UI (UILobby.cs — bypass for M0)
- Host migration
- Bot queue / matchmaking
- Steamworks

## Data Boundary

```
WebSocketSQL (Colyseus):  Auth, Profile, Economy, Inventory, Rewards, Friends, Mail, Leaderboards
Fusion (M0):              One NetworkRunner, one room, one map load, one GameplaySync spawn

No cross-contamination. Fusion touches gameplay session only.
```

## Risks

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Fusion SDK version mismatch with template (needs 2.0.8) | Medium | Pin exact 2.0.8 |
| #if FUSION2 code has bitrot since last compiled | Low | Clean pattern — just needs compilation |
| Shared Mode requires Photon Cloud (no LAN) | High | Document this — devs need internet |
| IL2CPP stripping may kill Fusion assemblies | Medium | Add Fusion assemblies to link.xml |

## Story

**Title**: `BACKEND-007-fusion-sdk-install-and-smoke-test`

**AC**:
1. `FUSION2` define added to Standalone, project compiles without errors
2. Fusion SDK 2.0.8 installed, AppId configured
3. NetworkRunner starts in Shared Mode, creates room
4. MapArena1 loads via Fusion scene manager
5. GameplaySync spawns, MatchStarted = true
6. Disconnect triggers clean runner shutdown

**Evidence**:
- Screenshot: console `Connected to Fusion session [room]`
- Screenshot: scene hierarchy with GameplaySync spawned
- Log capture: `Start → OnConnectedToServer → OnPlayerJoined → SceneLoadDone`
- Photon dashboard showing 1 active session
