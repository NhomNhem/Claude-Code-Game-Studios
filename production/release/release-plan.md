# Release Plan — Tiny Rift Survivors

## Release Strategy

WebSocket + SQL online backend from day one. Premium purchase on Steam.
No Firebase, no Fusion 2, no IAP in Public Release builds.

## Pre-Release Tasks

- [ ] Remove `FIREBASE` from Standalone scripting define symbols
- [ ] Remove `FUSION_*` from Android/WebGL scripting define symbols
- [ ] Product Name: `Tiny-Rift-Survivors-GameClient` → `Tiny Rift Survivors`
- [ ] Company Name: `DefaultCompany` → actual studio name
- [ ] Bundle ID: `com.DefaultCompany...` → `com.[studio].tinyrift`
- [ ] Set proper icon
- [ ] Bundle version: `1.0.0` for EA launch
- [ ] Server infrastructure: production WebSocket endpoint deployed
- [ ] Server monitoring and logging configured

## Early Access Release (M3)

**Target**: End of Phase M3 (Week 10)

**Platform**: Steam (PC)

**Distribution**: Premium purchase

**Build Config**:
- Scripting defines: `UNITY_PIPELINE_URP` only
- Backend: `WebSocketSqlBackendService` (production endpoint)
- Fallback: `OfflineBackendService` (graceful degradation)
- Scenes in build: Login, Home, MapArena1-4 (remove PVP scenes)
- Stripping Level: Medium + link.xml for gameplay assemblies
- IL2CPP for Standalone

**Content**:
- Online login with username/email + password
- Server-authoritative currency (gold + gems)
- Player profile with stats
- Core survivor gameplay loop
- 3 elemental skills + 3 synergies
- 5 enemy types
- Wave progression (10+ waves)
- Skill upgrade paths
- Meta-progression unlocks
- In-run shop
- Basic Steam achievements

**Release Checklist**:
- [ ] Smoke check: critical path passes
- [ ] E2E backend test: login → play → earn currency → persist → reload
- [ ] All critical bugs fixed
- [ ] Performance: 60fps on target spec
- [ ] Balance: playtested and tuned
- [ ] Server: production-ready (monitoring, scaling, backup)
- [ ] Steam build configured and verified
- [ ] Store page created
- [ ] Legal review (privacy policy, EULA, ToS)
- [ ] Go/no-go producer sign-off

## Backend Deployment

| Environment | URL | Database | Purpose |
|-------------|-----|----------|---------|
| Local | `ws://localhost:8080` | Local MySQL | Dev |
| Staging | `ws://staging.tinyrift.com:8080` | Staging DB | QA/Test |
| Production | `ws://api.tinyrift.com:8080` | Production DB | Live |

## Branch Strategy

| Branch | Purpose | Deploy to |
|--------|---------|-----------|
| `main` | Public Release — production-ready | Steam (public), Production server |
| `develop` | Active development | Internal, Staging server |
| `hotfix/*` | Emergency fixes | Steam (hotfix), Production server |

## Build Pipeline

```
main ──> Build-Public (UNITY_PIPELINE_URP) ──> Steam
develop ──> Build-Dev (UNITY_PIPELINE_URP) ──> Internal Test
```

Server deploys independently via CI/CD on the `tiny-rift-server` repo.

## Versioning

Semantic: `MAJOR.MINOR.PATCH`

- Client + Server versions must be compatible within a release
- Breaking protocol changes increment MAJOR
- EA.1, EA.2, ... Early Access releases
- 1.0.0 Full release
