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
Stable, tested systems only. All backend services disabled.
Custom code lives in `Assets/_TinyRift/`.
**Current defines**: `UNITY_PIPELINE_URP` (remove `FIREBASE`/`FUSION2` from Player Settings)

### Track 2: Full-Stack Lab (PLANNED — LOCKED)
Experimental online systems. NOT enabled in any public build.
Backend services behind `#if LAB_TRACK` conditional compilation.

**Critical: Template ALREADY has backend infrastructure built in:**
- Firebase Auth + Firestore with full sync handlers (16 handlers)
- WebSocket/SQL backend with full sync handlers (15 handlers)
- Fusion 2 multiplayer (Addons/Multiplayer/)
- Colyseus multiplayer SDK
- Unity IAP + Battle Pass + Monetization
- OfflineBackendService for local-only fallback

**These must be DISABLED for Public Release builds**, not enabled later.

## Agent Rules

1. NEVER modify `Assets/BulletHellTemplate/` vendor code
2. NEVER refactor template manager singletons
3. NEVER modify existing scenes or prefabs
4. NEVER enable backend services in Public Release builds
5. NEVER change Unity project settings without explicit approval
6. Write ALL custom code to `Assets/_TinyRift/`
7. Lab Track code goes in `Assets/_TinyRift/Lab/`
8. Respect VContainer DI patterns already established by BackendLifetimeScope
9. Do NOT remove bundled third-party libraries — just don't initialize unused ones

## Current Scripting Defines

| Platform | Current | Public Release Target |
|----------|---------|----------------------|
| Standalone | `UNITY_PIPELINE_URP;FIREBASE` | `UNITY_PIPELINE_URP` |
| Android | `UNITY_PIPELINE_URP;FUSION_*` | `UNITY_PIPELINE_URP` |
| WebGL | `UNITY_PIPELINE_URP;FUSION_*` | `UNITY_PIPELINE_URP` |

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
