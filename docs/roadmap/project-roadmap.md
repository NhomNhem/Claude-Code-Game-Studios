# Project Roadmap — Tiny Rift Survivors

## Roadmap Context

The BulletHell Elemental Template already provides a complete game framework.
Our task is primarily **content creation, configuration, and extension** rather than
building systems from scratch. This changes the roadmap from "build systems" to
"configure template + add custom content."

```
Phase 1: Foundation ──> Phase 2: Core Content ──> Phase 3: Progression ──> Phase 4: Polish ──> Phase 5: Lab
  Docs / Setup           Elemental Skills          Meta-progression        Balance                Backend
  Audit template         Custom enemies            Achievements            VFX/Audio              Enable template's
  Configure existing     Synergy system            Extend save system      Steam integration      built-in services
```

## Phase 1: Foundation (Weeks 1-2)
- [x] Setup engine & project docs
- [x] Audit template systems (complete: 250+ scripts inventoried)
- [ ] Game concept document (brainstorm)
- [ ] Art bible & visual identity
- [ ] Create `Assets/_TinyRift/` directory structure
- [ ] GDDs for custom systems (elemental skills, synergies, enemies)
- [ ] Backend disablement plan (remove FIREBASE/FUSION defines)
- [ ] Project architecture blueprint + ADRs

## Phase 2: Core Content (Weeks 3-6)
- [ ] 3 signature skills (fire, ice, lightning) — extend SkillData
- [ ] Elemental synergy system (vaporize, plasma, shatter)
- [ ] 5 enemy types with distinct behaviors — configure MonsterEntity
- [ ] Wave progression tuning — configure Wave/GameplayManager
- [ ] Skill upgrade paths — configure SkillPerkData
- [ ] Damage numbers & basic VFX — configure existing systems

## Phase 3: Progression (Weeks 7-8)
- [ ] Meta-progression system (between-run persistent upgrades)
- [ ] Extend PlayerSave for new progression data
- [ ] In-run shop configuration — configure ShopItem data
- [ ] Achievement system
- [ ] Menus (main, pause, game over, upgrades)

## Phase 4: Polish & Release (Weeks 9-10)
- [ ] Balance tuning & playtesting
- [ ] Full VFX pass (elemental reactions, hits, explosions)
- [ ] SFX & music integration
- [ ] UI polish (menus, HUD, transitions)
- [ ] Performance optimization (URP, object pooling)
- [ ] Bug fixing & QA pass
- [ ] Steam integration
- [ ] Rename product/company/bundle from template defaults
- [ ] Early Access release

## Phase 5: Full-Stack Lab Track (Weeks 11+)
- [ ] Add `LAB_TRACK` define
- [ ] Configure Firebase Auth + Firestore (already built in template)
- [ ] Configure Fusion 2 multiplayer (already built in template)
- [ ] Configure IAP (already built in template)
- [ ] Configure Battle Pass (already built in template)
- [ ] Configure WebSocket/SQL backend (already built in template)
- [ ] Configure Ranking/Leaderboards (already built in template)
- [ ] Lab Track build
