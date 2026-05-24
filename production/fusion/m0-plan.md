# M0 Fusion Plan — Tiny Rift Survivors

## Status ✅ — Fusion SDK Installed (2026-05-25)

**Version**: 2.1.1 Release-Candidate 2054 (build 2026-05-20)
**Location**: `Assets/Photon/Fusion/`
**AppId**: `46fda6fe-9b0f-4071-8233-26da07ea1144` (PhotonAppSettings.asset)
**Standalone defines**: Auto-configured by Fusion SDK on import:
  `UNITY_PIPELINE_URP;FUSION_WEAVER;FUSION2;FUSION_2;FUSION_2_1;FUSION_2_1_1;FUSION_2_OR_NEWER;FUSION_2_0_OR_NEWER;FUSION_2_1_OR_NEWER;FUSION_LOGLEVEL_INFO`

**Template code activation**: `#if FUSION2` (234+ blocks) will now compile on Standalone.
  `FUSION_NETWORK` (SoundEffectsPool, DropPool — 13 blocks) is a **separate template define**,
  not a Fusion SDK define. Not needed for M0.

**TODO**: Open Unity Editor, verify compile completes without errors.

## Goal

Fusion SDK install + one smoke-test COOP session in-editor.
Prove Fusion pipeline works end-to-end before any gameplay implementation.

## Scope In

1. [✅] Install Fusion SDK 2.1.1
2. [✅] Configure AppId in PhotonAppSettings.asset
3. [✅] Add FUSION2 define to Standalone (auto-done by SDK)
4. [⬜] Open Unity Editor, verify project compiles
5. [⬜] Create FusionSmokeTest scene or test flow:
   - Start NetworkRunner in GameMode.Shared
   - Runner creates a room
   - Load MapArena1 via NetworkRunner.LoadScene()
   - Spawn GameplaySync prefab
   - Verify MatchStarted = true, connection state = Connected
6. [⬜] Cleanup: proper Fusion shutdown on disconnect

## Scope Out

- Colyseus/Fusion integration (separate concern)
- Full COOP gameplay (skills, enemies, drops — M1+)
- PVP modes (Arena, TDM, Battle Royale)
- Lobby UI (UILobby.cs — bypass for M0)
- Host migration
- Bot queue / matchmaking
- Steamworks
- FUSION_NETWORK define (SoundEffectsPool / DropPool networking — optional)

## Risks

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Shared Mode requires Photon Cloud (no LAN) | High | Devs need internet to test |
| #if FUSION2 code bitrot since template was created | Low | Conditional pattern is clean |
| FUSION_NETWORK define missing (SoundEffectsPool, DropPool) | None | These have `#else` fallbacks that work fine without the define |
| IL2CPP stripping may kill Fusion assemblies | Medium | Add Fusion assemblies to link.xml when building for release |

## Story

**Title**: `BACKEND-007-fusion-sdk-install-and-smoke-test`

**AC**:
1. FUSION2 define added to Standalone, project compiles without errors
2. Fusion SDK 2.1.1 installed, AppId configured
3. NetworkRunner starts in Shared Mode, creates room
4. MapArena1 loads via Fusion scene manager
5. GameplaySync spawns, MatchStarted = true
6. Disconnect triggers clean runner shutdown

**Evidence**:
- Screenshot: console `Connected to Fusion session [room]`
- Screenshot: scene hierarchy with GameplaySync spawned
- Log capture: Start → OnConnectedToServer → OnPlayerJoined → SceneLoadDone
- Photon dashboard showing 1 active session
