# Epic List — Tiny Rift Survivors

## Template Context

The BulletHell Elemental Template provides ~250+ scripts including a complete game
framework (movement, combat, skills, enemies, waves, save/load, pooling, VContainer DI,
EventBus, localization, shop, inventory, online backends). Our epics focus on:

1. **Configuring/Extending** existing template systems
2. **Adding** custom content (skills, enemies, synergies)
3. **Disabling** built-in backend services for Public Release

## Epic Index

| ID | Epic | Phase | Priority | Status |
|----|------|-------|----------|--------|
| FOUNDATION-001 | Project Initialization | Foundation | P0 | Active |
| CONCEPT-001 | Game Concept & Design | Foundation | P0 | Planned |
| CONCEPT-002 | Engine Configuration & Audit | Foundation | P0 | Planned |
| CONCEPT-003 | Art & Visual Identity | Foundation | P0 | Planned |
| CORE-001 | Elemental Skill System | Core Content | P1 | Planned |
| CORE-002 | Custom Enemies & Waves | Core Content | P1 | Planned |
| CORE-003 | Synergy System | Core Content | P1 | Planned |
| PROG-001 | Meta-Progression | Progression | P2 | Planned |
| PROG-002 | Save System Extension | Progression | P2 | Planned |
| PROG-003 | Shop & Upgrades | Progression | P2 | Planned |
| POLISH-001 | VFX & Audio | Polish/Release | P3 | Planned |
| POLISH-002 | UI/UX Polish | Polish/Release | P3 | Planned |
| POLISH-003 | Balance & Tuning | Polish/Release | P3 | Planned |
| POLISH-004 | Performance & Optimization | Polish/Release | P3 | Planned |
| RELEASE-001 | Product Identity & Steam Setup | Release | P0 | Planned |
| RELEASE-002 | QA & Bug Fixing | Release | P0 | Planned |
| RELEASE-003 | Early Access Launch | Release | P0 | Planned |
| BACKEND-001 | Backend Disablement | Foundation | P0 | Planned |
| LAB-001 | Firebase Configuration | Lab Track | P4 | Locked |
| LAB-002 | Fusion 2 Multiplayer | Lab Track | P4 | Locked |
| LAB-003 | IAP & Battle Pass | Lab Track | P4 | Locked |
| LAB-004 | WebSocket/SQL Backend | Lab Track | P4 | Locked |

## Active Epic

### FOUNDATION-001: Project Initialization
- **Scope**: Create project documentation, production tracking, workflow rules
- **Status**: Active
- **Stories**: None yet
- **Dependencies**: None
- **ADRs**: None yet
- **Deliverables**: Template audit ✓, system map ✓, backend map ✓, customization plan ✓

## Priority Definitions
- **P0**: Blocking — must complete before moving to next phase
- **P1**: Core — essential for MVP
- **P2**: Important — enhances core experience
- **P3**: Polish — quality and refinement
- **P4**: Lab Track — locked until Public Release ships

## Epic Details

### BACKEND-001: Backend Disablement (NEW — P0)
Template ships with FIREBASE on Standalone and FUSION2 on Android/WebGL.
These must be removed from Public Release build configs.
- Remove `FIREBASE` from Standalone defines
- Remove `FUSION_*` from Android/WebGL defines
- Verify no backend initialization in built player
- Decision: keep `OfflineBackendService` or disable entirely

### CORE-001: Elemental Skill System
- Extend `SkillData` ScriptableObject for custom skills
- Implement 3 signature skills: fire (AoE burn), ice (slow/freeze), lightning (chain)
- Hook into existing `SkillDamageProvider` / `SkillPerkDamageProvider`
- Skill upgrade paths via `SkillPerkData`

### CORE-003: Synergy System (NEW)
- Elemental combinations: Fire+Ice=Freeze, Fire+Lightning=Chain, Ice+Lightning=Shatter
- Skill activation checks concurrent active elements
- Damage modifiers based on active synergies
- Visual feedback for synergy procs

### RELEASE-001: Product Identity & Steam Setup
- Rename Product Name from `Tiny-Rift-Survivors-GameClient`
- Set Company Name from `DefaultCompany`
- Set proper bundle identifier
- Steamworks SDK integration
- Steam build configuration
