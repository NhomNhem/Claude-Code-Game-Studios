# Tiny Rift Survivors — Claude Code Game Studios

A Unity 6 survivor-like bullet heaven game built on the BulletHell Elemental Template (Bizachi),
with a WebSocket + SQL online backend from day one.

## Technology Stack

- **Engine**: Unity 6000.3.11f1 (Unity 6)
- **Language**: C# (.NET Standard 2.1, IL2CPP)
- **Rendering**: URP 17.3 (2D Renderer)
- **Input**: Unity Input System 1.19.0
- **DI Framework**: VContainer (bundled)
- **Async**: UniTask (bundled)
- **Tweening**: LeanTween (bundled)
- **State Machines**: UnityHFSM (bundled)
- **Backend**: WebSocket + SQL (primary), Offline (dev/fallback)
- **Server**: Node.js + Colyseus
- **Database**: MySQL
- **Template**: BulletHell Elemental Template (Bizachi)

## Development Tracks

**Track 1: Public Release** (ACTIVE) — online via WebSocket + SQL. Server-authoritative economy.
No Firebase, no Fusion 2, no IAP. Defines: `UNITY_PIPELINE_URP`.

**Track 2: Future Extensions** (LOCKED) — Firebase, Fusion 2 multiplayer, IAP, Battle Pass.

**CRITICAL**: The template already has all three backends built in (`IBackendService`).
We use `WebSocketSqlBackendService` as primary, `OfflineBackendService` for dev/fallback,
and defer `FirebaseBackendService`. Remove `FIREBASE` from Player Settings defines.

## Immutable Rules

1. NEVER modify `Assets/BulletHellTemplate/` vendor code
2. NEVER refactor template manager singletons
3. NEVER modify existing scenes or prefabs
4. NEVER enable Firebase or Fusion 2 in Public Release builds
5. NEVER commit backend credentials
6. ALWAYS write custom code to `Assets/_TinyRift/`
7. Future-extension code (Firebase, Fusion, IAP, BP) → `Assets/_TinyRift/Future/`
8. NEVER remove bundled libraries — just don't initialize unused ones

## Project Structure

```
/
├── CLAUDE.md / AGENTS.md              # Configurations
├── Tiny-Rift-Survivors-GameClient/    # Unity project root
│   ├── Assets/
│   │   ├── BulletHellTemplate/        # VENDOR — never modify
│   │   ├── _TinyRift/                 # Custom code
│   │   │   └── Future/                # Firebase, Fusion, IAP, BP (locked)
│   │   └── ...
│   └── ...
├── tiny-rift-server/                  # Node.js + Colyseus server (separate repo)
├── design/                            # GDDs, narrative docs, balance data
├── docs/                              # Technical docs, architecture, roadmaps
└── production/                        # Sprints, milestones, epics, stories
```

## M0 Backend Priorities

1. `BackendSettings.asset` — ScriptableObject (online/offline/mock toggle)
2. `BackendBootstrap` — VContainer registration, startup init
3. WebSocketSQL configuration — extend `WebSocketSqlBackendService`
4. Node.js/Colyseus server (`tiny-rift-server` repo)
5. MySQL schema (users, profiles, currency, leaderboards)
6. Unity ↔ WebSocketSQL connection
7. Login → Profile → Currency end-to-end flow

## Key Template Systems (Built In)

| System | Class | Customization |
|--------|-------|--------------|
| Game State | GameManager, GameplayManager, GameInstance | Configure |
| Character | CharacterEntity, CharacterControllerComponent | Extend |
| Combat | CharacterAttackComponent, IDamageable | Extend |
| Skills | SkillData (ScriptableObject), SkillDamageProvider | Extend |
| Enemies | MonsterEntity, MonsterHealth | Extend |
| Save/Load | PlayerSave (partial), SecurePrefs | Extend |
| Event Bus | EventBus (typed events) | Extend |
| Pooling | MonsterPool, DropPool, etc. | Configure |
| Localization | LanguageManager | Configure |
| Backend DI | BackendLifetimeScope, IBackendService | Extend — primary path |
| WebSocket SQL | WebSocketSqlBackendService (built in template) | Configure |
| Offline | OfflineBackendService (built in template) | Configure |

## Engine Version Reference

@docs/engine-reference/unity/VERSION.md

## Current Stage

- **Stage**: Concept (production/stage.txt)
- **Review Mode**: full (production/review-mode.txt)
- **Backend**: WebSocket + SQL (primary), Offline (fallback), Firebase (deferred)
- **Custom Code Dir**: `Assets/_TinyRift/` — not yet created
