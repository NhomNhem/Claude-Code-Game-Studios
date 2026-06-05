# Project Roadmap — Tiny Rift Survivors

## Roadmap Context

The BulletHell Elemental Template provides a complete game framework including
the `IBackendService` abstraction. We configure `WebSocketSqlBackendService` as
primary and build the server-side infrastructure alongside the game client.

```
M0: Backend ──> M0.5: Pipe ──> M1: Core ──> M2: Progression ──> M3: Polish ──> Future
  WebSocket/SQL    Fusion Smoke     Elemental Skills    Meta-progression    Balance         Firebase
  Node.js Server   Test + Anim      Custom Enemies      Achievements        VFX/Audio       Host Mode
  MySQL Schema     Feel Setup       Synergy System      Save/Load           Steam EA Launch IAP/BP
  Login/Currency                     Waves/Upgrades     Shop                Bug Fixing
```

## M0 — Backend Foundation (Completed)

- [x] Full GameClient audit (~250+ scripts, 8 scenes, backend layer, define symbols)
- [x] Template audit, system map, backend map, customization plan
- [x] AGENTS.md, CLAUDE.md, two-track system configured
- [x] Product brief, roadmap, milestone plan
- [x] Epic list, story index, QA strategy, release plan
- [x] Backend decision: WebSocket + SQL primary
- [x] Docker WebSocketSQL stack running (MySQL, Redis, phpMyAdmin, GameServer)
- [x] REST /auth/register verified via curl
- [x] Unity login with backend-created account
- [x] Unity reaches WebSocketSQL, PresenceRoom joins, game playable
- [x] Fusion SDK 2.1.1 RC 2054 imported and configured
- [x] Engine setup verified (Unity 6000.3.11f1 — ref docs, tech prefs, agent config)

## M0 — Remaining

- [ ] Create `Assets/_TinyRift/` directory structure
- [ ] `BackendSettings.asset` ScriptableObject
- [ ] `BackendBootstrap.cs` — VContainer registration for IBackendService
- [ ] Configure `WebSocketSqlBackendService` connection settings
- [ ] Remove `FIREBASE` and stale `FUSION_*` defines from Player Settings
- [ ] Create `tiny-rift-server` repo (Node.js + Colyseus)
- [ ] MySQL schema design (users, profiles, currencies, leaderboards)
- [ ] Server auth handler (login/register)
- [ ] Server profile handler (read/update)
- [ ] Server currency handler (server-authoritative add/spend)
- [ ] Unity ↔ WebSocket end-to-end: login → profile → currency round-trip
- [ ] GDDs for core gameplay systems
- [ ] Art bible & visual identity

## M0.5 — Pipe & Feel (Weeks 2-3)

- [ ] Fusion Shared Mode smoke test (NetworkRunner → room → map → spawn)
- [ ] Skill Presentation Adapter — prototype animation feel bridge
- [ ] Character/monster movement feel profile tuning (ScriptableObject, no vendor code)
- [ ] Documentation: architecture decisions for Fusion Shared Mode baseline

## M1 — Core Content (Weeks 4-7)

- [ ] 3 signature skills (fire, ice, lightning) — feel-tuned via adapter
- [ ] Elemental synergy system (freeze, chain, shatter)
- [ ] 5 enemy types with distinct behaviors
- [ ] Wave progression system (configure Wave/GameplayManager)
- [ ] Skill upgrade paths (configure SkillPerkData)
- [ ] Damage numbers & basic VFX
- [ ] HUD integration with server currency

## M2 — Progression (Weeks 8-9)

- [ ] Meta-progression system (between-run upgrades)
- [ ] Persistent save/load via backend sync
- [ ] In-run shop (configure ShopItem data)
- [ ] Achievement system
- [ ] Menus (main, pause, game over, upgrades)

## M3 — Polish & Early Access (Weeks 10-11)

- [ ] Balance tuning & playtesting
- [ ] Full VFX pass (elemental reactions, hits, explosions)
- [ ] SFX & music integration
- [ ] UI polish
- [ ] Performance optimization (URP, object pooling)
- [ ] Product rename (from template defaults)
- [ ] Steam integration
- [ ] QA pass → smoke check → release checklist
- [ ] Early Access launch

## Future (Post-EA)

- [ ] Firebase (deferred, not on primary path)
- [ ] Fusion 2 Host Mode lab (if Shared Mode insufficient for PvP)
- [ ] IAP / Battle Pass
- [ ] Leaderboards
- [ ] Analytics & live-ops tools
