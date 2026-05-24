# Active Session State

<!-- STATUS -->
- **Stage**: Concept
- **Epic**: BACKEND-001 — Backend Settings & DI Setup
- **Story**: None started
- **Sprint**: None
- **Review Mode**: full
- **Last Updated**: 2026-05-24
- **Next Gate**: Gate Check — Concept → Backend Ready
<!-- /STATUS -->

## Current Focus

Documentation initialized. Backend architecture settled: WebSocket + SQL is primary
production backend from day one. Offline is dev/fallback. Firebase deferred.

## Completed

- [x] Full GameClient audit (~250+ scripts, 8 scenes, backend layer, define symbols)
- [x] Template audit, system map, backend map, customization plan written
- [x] AGENTS.md, CLAUDE.md configured with two-track system
- [x] Product brief, roadmap, milestone plan created
- [x] Epic list, story index, QA strategy, release plan created
- [x] Backend decision: WebSocket + SQL primary, Offline fallback, Firebase deferred

## Active Tasks

None — backend decision documented. Awaiting implementation greenlight.

## Key Decisions

1. **Backend**: WebSocket + SQL is PRIMARY production backend (not Lab Track)
2. **Offline**: Dev/test/fallback only (built-in OfflineBackendService)
3. **Firebase**: Deferred indefinitely (remove FIREBASE define)
4. **Fusion 2**: Deferred (remove FUSION_* defines)
5. **IAP/BP**: Deferred (not in Public Release)
6. **M0 focus**: BackendSettings → BackendBootstrap → WebSocket config → Server → MySQL → E2E

## Next Steps (M0 Order)

1. Create `Assets/_TinyRift/` directory structure
2. Create `BackendSettings.asset` ScriptableObject
3. Create `BackendBootstrap.cs` (VContainer registration)
4. Configure `WebSocketSqlBackendService`
5. Create `tiny-rift-server` repo
6. Design MySQL schema
7. Build server auth handler
8. Build server profile handler
9. Build server currency handler
10. Unity ↔ WebSocket E2E: login → profile → currency
