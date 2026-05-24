# Story Index — Tiny Rift Survivors

## Story Format

Each story file lives in `production/stories/` as `[epic-id]-NNN-[slug].md`.

```
BACKEND-001-001-settings-asset.md    BACKEND-002-001-websocket-config.md
BACKEND-003-001-server-scaffold.md   BACKEND-004-001-mysql-schema.md
...
```

## Current Sprint Stories

None yet — project is in Concept phase.

## All Stories (Planned)

### M0: Backend Foundation

| ID | Epic | Story Name | Status | Priority |
|----|------|-----------|--------|----------|
| — | BACKEND-001 | Create BackendSettings.asset ScriptableObject | Planned | P0 |
| — | BACKEND-001 | Create BackendBootstrap.cs (VContainer registration) | Planned | P0 |
| — | BACKEND-001 | Configure WebSocketSqlBackendService connection | Planned | P0 |
| — | BACKEND-002 | Implement WebSocketConfig with URL/reconnect/timeout | Planned | P0 |
| — | BACKEND-002 | Implement message handler routing | Planned | P0 |
| — | BACKEND-003 | Scaffold tiny-rift-server (Node.js + Colyseus) | Planned | P0 |
| — | BACKEND-003 | Implement server auth handler (register/login) | Planned | P0 |
| — | BACKEND-004 | Design and create MySQL schema | Planned | P0 |
| — | BACKEND-004 | Implement database connection pool | Planned | P0 |
| — | BACKEND-005 | Implement Unity LoginService | Planned | P0 |
| — | BACKEND-005 | Implement Unity ProfileService | Planned | P0 |
| — | BACKEND-005 | End-to-end: login → profile load | Planned | P0 |
| — | BACKEND-006 | Implement server-authoritative currency | Planned | P0 |
| — | BACKEND-006 | Implement Unity CurrencyService | Planned | P0 |
| — | BACKEND-006 | End-to-end: login → profile → currency round-trip | Planned | P0 |
| — | FOUNDATION-001 | Initialize project documentation | Completed | P0 |
| — | FOUNDATION-001 | Audit template systems | Completed | P0 |
| — | FOUNDATION-001 | Remove FIREBASE/FUSION defines | Planned | P0 |
| — | FOUNDATION-001 | Create _TinyRift/ directory structure | Planned | P0 |
| — | CONCEPT-001 | Brainstorm game concept | Planned | P0 |
| — | CONCEPT-001 | Map systems & define customization scope | Planned | P0 |
| — | CONCEPT-002 | Author art bible | Planned | P0 |

### M1: Core Content

| ID | Epic | Story Name | Status | Priority |
|----|------|-----------|--------|----------|
| — | CORE-001 | Implement fire skill (extend SkillData) | Planned | P1 |
| — | CORE-001 | Implement ice skill (extend SkillData) | Planned | P1 |
| — | CORE-001 | Implement lightning skill (extend SkillData) | Planned | P1 |
| — | CORE-003 | Implement elemental synergy resolver | Planned | P1 |
| — | CORE-003 | Implement synergy procs & damage modifiers | Planned | P1 |
| — | CORE-002 | Implement 5 custom enemy types | Planned | P1 |
| — | CORE-002 | Configure wave progression data | Planned | P1 |

### M2: Progression

| ID | Epic | Story Name | Status | Priority |
|----|------|-----------|--------|----------|
| — | PROG-001 | Design & implement meta-progression | Planned | P2 |
| — | PROG-002 | Implement save/load with backend sync | Planned | P2 |
| — | PROG-003 | Configure and wire in-run shop | Planned | P2 |

### M3: Polish & Release

| ID | Epic | Story Name | Status | Priority |
|----|------|-----------|--------|----------|
| — | POLISH-001 | VFX pass | Planned | P3 |
| — | POLISH-001 | Audio pass | Planned | P3 |
| — | POLISH-002 | UI polish | Planned | P3 |
| — | POLISH-003 | Balance tuning & playtesting | Planned | P3 |
| — | POLISH-004 | Performance optimization | Planned | P3 |
| — | RELEASE-001 | Product rename & bundle ID | Planned | P0 |
| — | RELEASE-001 | Steamworks SDK integration | Planned | P0 |
| — | RELEASE-002 | QA testing pass | Planned | P0 |
| — | RELEASE-003 | Early Access launch | Planned | P0 |

## Status Definitions
- **Completed**: Done
- **In Progress**: Actively being worked on
- **Planned**: Identified but not started
- **Blocked**: Cannot proceed due to dependency
- **Locked**: Future extension — not for current milestones
