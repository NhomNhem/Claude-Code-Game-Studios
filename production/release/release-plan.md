# Release Plan — Tiny Rift Survivors

## Track 1: Public Release (PRIMARY)

### Pre-Release Tasks
- [ ] Remove `FIREBASE` from Standalone scripting define symbols
- [ ] Remove `FUSION_*` from Android/WebGL scripting define symbols
- [ ] Product Name: change from `Tiny-Rift-Survivors-GameClient` to `Tiny Rift Survivors`
- [ ] Company Name: change from `DefaultCompany` to actual studio name
- [ ] Bundle ID: change from `com.DefaultCompany...` to proper identifier
- [ ] Remove Unity splash screen if applicable
- [ ] Set proper icon
- [ ] Set bundle version to `1.0.0` for initial EA launch

### Early Access Release

**Target**: End of Phase 4 (Week 10)

**Platform**: Steam (PC)

**Distribution**: Premium purchase

**Build Config**:
- Scripting defines: `UNITY_PIPELINE_URP` only
- Scenes in build: Home, MapArena1, MapArena2, MapArena3, MapArena4
- Stripping Level: Medium (link.xml to keep gameplay assemblies)
- IL2CPP for Standalone

**Content**:
- Core survivor gameplay loop (extends template)
- 3 elemental skills (fire, ice, lightning)
- 3 elemental synergies (freeze, chain, shatter)
- 5 enemy types with distinct behaviors
- Wave progression (10+ waves)
- Skill upgrade paths
- Meta-progression unlocks
- In-run shop
- Basic achievements

**Release Checklist**:
- [ ] Smoke check: critical path passes
- [ ] All critical bugs fixed
- [ ] Performance: 60fps on target spec
- [ ] Balance: playtested and tuned
- [ ] Steam build configured and verified
- [ ] Store page created
- [ ] Legal review (privacy policy, EULA)
- [ ] Go/no-go producer sign-off

---

## Track 2: Full-Stack Lab (SECONDARY — LOCKED)

**Target**: Post-Public Release (Week 11+)

**Trigger**: Add `LAB_TRACK` to scripting define symbols

**Build Config**:
- Scripting defines: `UNITY_PIPELINE_URP;LAB_TRACK`
- All 8 scenes in build (including Login, PVP arenas)
- Firebase initialized via BackendLifetimeScope
- Fusion 2 initialized via FusionLobbyManager

**Additional Content**:
- Firebase Auth & Firestore (already built in template)
- Fusion 2 multiplayer (already built in template)
- WebSocket/SQL persistent state (already built in template)
- Battle Pass (already built in template)
- IAP cosmetics (already built in template)
- Leaderboards (already built in template)
- Analytics (already built in template)

---

## Branch Strategy

| Branch | Purpose | Deploy to |
|--------|---------|-----------|
| `main` | Public Release — production-ready | Steam (public) |
| `develop` | Active development — Public Track features | Internal |
| `lab/backend` | Lab Track backend configuration | Lab Track build |
| `lab/multiplayer` | Lab Track Fusion 2 tuning | Lab Track build |
| `hotfix/*` | Emergency fixes to main | Steam (hotfix) |

## Build Pipeline

```
main ──> Build-Public (defines: UNITY_PIPELINE_URP) ──> Steam
develop ──> Build-Dev (defines: UNITY_PIPELINE_URP) ──> Internal Test Build
lab/* ──> Build-Lab (defines: UNITY_PIPELINE_URP;LAB_TRACK) ──> Lab Track Test Build
```

## Versioning

Semantic: `MAJOR.MINOR.PATCH`

- EA.1, EA.2, ... Early Access releases
- 1.0.0 Full release
- 1.1.0 Feature updates
- 1.1.1 Hotfixes
