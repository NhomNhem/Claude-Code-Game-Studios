# Tiny Rift Survivors — OpenCode Agents & Configuration

This file defines the agent configuration for OpenCode sessions.
When working on this project, agents follow the two-track system below.

## Engine Configuration

- **Engine**: Unity 6000.3.11f1 (Unity 6)
- **Language**: C#
- **Rendering**: URP 17.3
- **Template**: BulletHell Elemental Template (Bizachi)
- **Input**: Unity Input System 1.19.0
- **DI Framework**: VContainer (bundled in template)
- **Async**: UniTask (bundled in template)

## Development Tracks

### Track 1: Public Release (ACTIVE — PRIMARY)
Online-enabled via WebSocket + SQL backend. Server-authoritative economy.
- Backend: WebSocket + SQL (primary), Offline (dev/fallback)
- Auth: WebSocket-based login, email/username + password
- Multiplayer: None yet (deferred)
- Monetization: Premium purchase only (no IAP)
- No Firebase, no Fusion 2
- Custom code in `Assets/_TinyRift/`
- **Defines**: `UNITY_PIPELINE_URP;BACKEND_ONLINE` (remove `FIREBASE`/`FUSION2`)

### Track 2: Future Extensions (PLANNED — LOCKED)
Experimental systems, not in any public build yet.
- Firebase (deferred, not part of primary path)
- Fusion 2 multiplayer (future)
- IAP / Battle Pass (future)

## Critical: Template Already Has Backend Infrastructure

The template ships with **all three backends built in** via `IBackendService`:
- `WebSocketSqlBackendService` — **USE THIS** (primary production)
- `OfflineBackendService` — **USE THIS** (dev/test/fallback)
- `FirebaseBackendService` — DEFER (not part of primary path)

We configure and extend existing services, not build from scratch.
Remove `FIREBASE` define from Player Settings to prevent Firebase init.

## Agent Rules

1. NEVER modify `Assets/BulletHellTemplate/` vendor code
2. NEVER refactor template manager singletons
3. NEVER modify existing scenes or prefabs
4. NEVER enable Firebase or Fusion 2 in Public Release builds
5. NEVER change Unity project settings without explicit approval
6. Write ALL custom code to `Assets/_TinyRift/`
7. Future-extension code (Firebase, Fusion, IAP, BP) goes in `Assets/_TinyRift/Future/`
8. Respect VContainer DI patterns established by BackendLifetimeScope
9. Do NOT remove bundled third-party libraries — just don't initialize unused ones

## Current Scripting Defines (Target)

| Platform | Current | Target |
|----------|---------|--------|
| Standalone | `UNITY_PIPELINE_URP;FIREBASE` | `UNITY_PIPELINE_URP` |
| Android | `UNITY_PIPELINE_URP;FUSION_*` | `UNITY_PIPELINE_URP` |
| WebGL | `UNITY_PIPELINE_URP;FUSION_*` | `UNITY_PIPELINE_URP` |

Dev builds may add `BACKEND_ONLINE` or use Offline mode per BackendSettings.asset.

## M0 Backend Priorities

1. `BackendSettings.asset` (ScriptableObject — toggle online/offline/mock)
2. `BackendBootstrap` (VContainer registration, startup init sequence)
3. WebSocketSQL setup — configure `WebSocketSqlBackendService`
4. Node.js/Colyseus server (GitHub: `tiny-rift-server`)
5. MySQL schema (users, profiles, currency, leaderboards)
6. Unity client → WebSocketSQL connection (login round-trip)
7. Login → Profile → Currency end-to-end flow

## Session Workflow

1. Read `docs/technical/customization-plan.md` before starting new work
2. Read `production/session-state/active.md` for current state
3. Check `production/epics/epic-list.md` for active epic
4. Follow CCGS skills workflow for design → architecture → implementation

## Status Reference

- **Stage**: Concept
- **Review Mode**: full
- **Engine**: Unity 6000.3.11f1
- **Template**: BulletHell Elemental Template
- **Custom Code Dir**: `Assets/_TinyRift/` (not yet created)
