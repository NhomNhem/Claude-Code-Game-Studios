# Milestone Plan — Tiny Rift Survivors

## M0: Backend Foundation (Weeks 1-2)
**Gate**: Concept → Backend Ready

**Deliverables**:
- [ ] `BackendSettings.asset` — online/offline/mock toggle
- [ ] `BackendBootstrap.cs` — VContainer registration + startup sequence
- [ ] `WebSocketSqlBackendService` configured and connected
- [ ] `tiny-rift-server` repo created with Node.js + Colyseus
- [ ] MySQL schema (users, profiles, currencies, leaderboards)
- [ ] Server: login/register handler
- [ ] Server: profile read/update handler
- [ ] Server: server-authoritative currency handler
- [ ] Unity ↔ WebSocket end-to-end flow: login → profile → currency
- [ ] `FIREBASE` and `FUSION_*` defines removed from Player Settings
- [ ] `Assets/_TinyRift/` directory structure created
- [ ] Game concept document and GDDs for core systems

**Exit Criteria**:
- Login → Profile → Currency round-trip works end-to-end
- Offline fallback works (no server required)
- No Firebase/Fusion code initialized at startup
- Gate check passes

---

## M1: Core Content (Weeks 3-6)
**Gate**: Backend Ready → Content Complete

**Deliverables**:
- [ ] 3 elemental skills implemented (fire, ice, lightning)
- [ ] Elemental synergy system (freeze, chain, shatter)
- [ ] 5 enemy types with distinct behaviors
- [ ] Wave progression system
- [ ] Skill upgrade paths
- [ ] Damage numbers & basic VFX
- [ ] HUD shows server-authoritative currency
- [ ] UX specs for HUD and menus

**Exit Criteria**:
- All core systems unit tested
- Playable run from start to wave 10
- Currency displayed from server
- No critical bugs

---

## M2: Progression (Weeks 7-8)
**Gate**: Content Complete → Feature Complete

**Deliverables**:
- [ ] Meta-progression system (between-run upgrades)
- [ ] Persistent save/load synced to backend
- [ ] In-run shop
- [ ] Achievement system (Steam)
- [ ] Menus (main, pause, game over, upgrades)

**Exit Criteria**:
- Full run loop: menu → play → die/win → meta-upgrade → replay
- Progress persists across sessions (server-side)
- All progression systems tested

---

## M3: Polish & Early Access (Weeks 9-10)
**Gate**: Feature Complete → Ship

**Deliverables**:
- [ ] Balance tuning complete
- [ ] Full VFX pass
- [ ] SFX and music integration
- [ ] UI polish complete
- [ ] Performance: 60fps on target spec
- [ ] Product renamed from template defaults
- [ ] Steam integration complete
- [ ] QA pass — all critical bugs fixed

**Exit Criteria**:
- Smoke check passes
- Release checklist complete
- Build verified on Steam
- Go/no-go decision: GREEN
- Early Access launch

---

## Future Milestones (Post-EA)
- Firebase integration (deferred)
- Fusion 2 multiplayer
- IAP / Battle Pass
- Platform expansions (console, mobile)
