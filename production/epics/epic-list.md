# Epic List — Tiny Rift Survivors

## Template Context

The BulletHell Elemental Template provides ~250+ scripts including a full game
framework and backend abstraction (`IBackendService`). Our M0 focus is the
WebSocket + SQL backend as primary production path.

Active backend: `WebSocketSqlBackendService`
Fallback: `OfflineBackendService`
Deferred: `FirebaseBackendService`

## Epic Index

| ID | Epic | Phase | Priority | Status |
|----|------|-------|----------|--------|
| BACKEND-001 | Backend Settings & DI Setup | M0 | P0 | Active |
| BACKEND-002 | WebSocket SQL Service | M0 | P0 | Planned |
| BACKEND-003 | Server Infrastructure (Node.js) | M0 | P0 | Planned |
| BACKEND-004 | MySQL Schema & Data Layer | M0 | P0 | Planned |
| BACKEND-005 | Auth & Profile Flow | M0 | P0 | Planned |
| BACKEND-006 | Currency System | M0 | P0 | Planned |
| FOUNDATION-001 | Project Initialization | M0 | P0 | Active |
| CONCEPT-001 | Game Concept & Design | M0 | P0 | Planned |
| CONCEPT-002 | Art & Visual Identity | M0 | P0 | Planned |
| CORE-001 | Elemental Skill System | M1 | P1 | Planned |
| CORE-002 | Custom Enemies & Waves | M1 | P1 | Planned |
| CORE-003 | Synergy System | M1 | P1 | Planned |
| PROG-001 | Meta-Progression | M2 | P2 | Planned |
| PROG-002 | Save System & Backend Sync | M2 | P2 | Planned |
| PROG-003 | Shop & Upgrades | M2 | P2 | Planned |
| POLISH-001 | VFX & Audio | M3 | P3 | Planned |
| POLISH-002 | UI/UX Polish | M3 | P3 | Planned |
| POLISH-003 | Balance & Tuning | M3 | P3 | Planned |
| POLISH-004 | Performance | M3 | P3 | Planned |
| RELEASE-001 | Product Identity & Steam | M3 | P0 | Planned |
| RELEASE-002 | QA & Release | M3 | P0 | Planned |

## Active Epics

### BACKEND-001: Backend Settings & DI Setup
- **Scope**: BackendSettings.asset ScriptableObject, BackendBootstrap.cs, VContainer registration
- **Dependencies**: None
- **Status**: Active
- **Key Files**: `_TinyRift/Scripts/Backend/BackendSettings.asset`, `BackendBootstrap.cs`

### FOUNDATION-001: Project Initialization
- **Scope**: Documentation, directory structure, template audit
- **Status**: Active (90% complete)
- **Deliverables**: Template audit ✓, system map ✓, backend map ✓, customization plan ✓

## Epic Details

### BACKEND-002: WebSocket SQL Service
- Configure `WebSocketSqlBackendService` (built in template)
- WebSocketConfig with server URL, reconnect, timeout settings
- Message handler routing (login, profile, currency messages)
- Connection lifecycle: connect → auth → heartbeat → reconnect

### BACKEND-003: Server Infrastructure
- GitHub repo: `tiny-rift-server`
- Node.js + TypeScript + Colyseus
- Dev config, prod config, PM2/process manager setup
- Dockerfile for containerized deployment

### BACKEND-004: MySQL Schema
- Tables: users, profiles, currencies, leaderboard_entries
- Index strategy, migration plan
- Connection pooling configuration

### BACKEND-005: Auth & Profile Flow
- Unity: LoginService (username/email + password)
- Server: register, login, token management
- Unity: ProfileService (display_name, stats)
- End-to-end: Login → Profile load → display in Home scene

### BACKEND-006: Currency System
- Server-authoritative gold and gems
- Unity: CurrencyService (get balance, add, spend)
- Server: all currency mutations validated server-side
- Optimistic concurrency control (version field)

## Priority Definitions
- **P0**: M0 — must ship backend foundation
- **P1**: M1 — core gameplay content
- **P2**: M2 — progression systems
- **P3**: M3 — polish and release
