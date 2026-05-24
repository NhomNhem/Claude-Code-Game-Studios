# Project Roadmap — Tiny Rift Survivors

## Roadmap Context

The BulletHell Elemental Template provides a complete game framework including
the `IBackendService` abstraction. We configure `WebSocketSqlBackendService` as
primary and build the server-side infrastructure alongside the game client.

```
M0: Backend ──> M1: Core ──> M2: Progression ──> M3: Polish ──> Future
  WebSocket/SQL    Elemental Skills    Meta-progression    Balance          Firebase
  Node.js Server   Custom Enemies     Achievements        VFX/Audio        Fusion 2
  MySQL Schema     Synergy System     Save/Load           Steam EA Launch  IAP/BP
  Login/Currency   Waves/Upgrades     Shop                Bug Fixing
```

## M0 — Backend Foundation (Weeks 1-2)
- [ ] Create `Assets/_TinyRift/` directory structure
- [ ] `BackendSettings.asset` ScriptableObject
- [ ] `BackendBootstrap.cs` — VContainer registration for IBackendService
- [ ] Configure `WebSocketSqlBackendService` connection settings
- [ ] Remove `FIREBASE` and `FUSION_*` defines from Player Settings
- [ ] Create `tiny-rift-server` repo (Node.js + Colyseus)
- [ ] MySQL schema design (users, profiles, currencies, leaderboards)
- [ ] Server auth handler (login/register)
- [ ] Server profile handler (read/update)
- [ ] Server currency handler (server-authoritative add/spend)
- [ ] Unity ↔ WebSocket end-to-end: login → profile → currency round-trip
- [ ] GDDs for core gameplay systems
- [ ] Art bible & visual identity

## M1 — Core Content (Weeks 3-6)
- [ ] 3 signature skills (fire, ice, lightning)
- [ ] Elemental synergy system (freeze, chain, shatter)
- [ ] 5 enemy types with distinct behaviors
- [ ] Wave progression system (configure Wave/GameplayManager)
- [ ] Skill upgrade paths (configure SkillPerkData)
- [ ] Damage numbers & basic VFX
- [ ] HUD integration with server currency

## M2 — Progression (Weeks 7-8)
- [ ] Meta-progression system (between-run upgrades)
- [ ] Persistent save/load via backend sync
- [ ] In-run shop (configure ShopItem data)
- [ ] Achievement system
- [ ] Menus (main, pause, game over, upgrades)

## M3 — Polish & Early Access (Weeks 9-10)
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
- [ ] Fusion 2 multiplayer
- [ ] IAP / Battle Pass
- [ ] Leaderboards
- [ ] Analytics & live-ops tools
