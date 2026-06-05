# Epic: Save & Profile

> **Layer**: Core
> **Systems**: Save/Profile Persistence, Account/Profile System
> **GDDs**: `design/gdd/save-profile-persistence.md`, `design/gdd/account-profile-system.md`
> **Architecture Modules**: Save/Profile, Account/Profile
> **Status**: Ready
> **Stories**: Not yet created — run `/create-stories save-profile`

## Overview

Manages all persistent game data and player identity. Save/Profile Persistence provides JSON-serialized save/load via Newtonsoft.Json with atomic write pattern (temp file → rename), single-file consolidation (`persistent.json`), versioned schema migration, dirty-flag+debounce write coalescing, and field-type-specific conflict resolution strategies. Account/Profile System manages login/registration via WebSocket backend, session token storage, and profile hydration after authentication. ProfileSyncService orchestrates sync between local save and backend.

## Governing ADRs

| ADR | Decision Summary | Engine Risk |
|-----|-----------------|-------------|
| ADR-001: VContainer DI Architecture | Both register as interface singletons in TinyRiftScope | LOW |
| ADR-006: Save/Profile Serialization | JSON via Newtonsoft.Json with atomic writes. PersistentSaveData consolidation. ProfileSyncService as intermediate sync orchestrator. | MEDIUM — AOT preservation for [JsonProperty]-annotated types |

## GDD Requirements

| TR-ID | Requirement | ADR Coverage |
|-------|-------------|--------------|
| _(placeholder)_ | JSON serialization via Newtonsoft.Json | ADR-006 ✅ |
| _(placeholder)_ | Atomic write pattern (temp file → rename) | ADR-006 ✅ |
| _(placeholder)_ | Single persistent.json with versioned schema migration | ADR-006 ✅ |
| _(placeholder)_ | ProfileSyncService for backend sync orchestration | ADR-006 ✅ |
| _(placeholder)_ | Login/registration via WebSocket backend | ❌ No ADR |
| _(placeholder)_ | Session token storage for credential-free reconnection | ❌ No ADR |

## Definition of Done

This epic is complete when:
- All stories are implemented, reviewed, and closed via `/story-done`
- All acceptance criteria from both GDDs are verified
- All Logic and Integration stories have passing test files in `tests/`
- IL2CPP build serializes and deserializes PersistentSaveData without field drop

## Stories

| # | Story | Type | Status | ADR |
|---|-------|------|--------|-----|
| 001 | Core Persistence Layer | Logic | Ready | ADR-006 |
| 002 | Version Migration & Corruption Recovery | Logic | Ready | ADR-006 |
| 003 | Fault Tolerance — IOException, Network Disconnect, Synclog | Logic | Ready | ADR-006 |
| 004 | Conflict Resolution — Scalar, List, Quarantine | Integration | Ready | ADR-006 |
| 005 | Concurrency & Throttling — Debounce, Coalescing | Logic | Ready | ADR-006 |
| 006 | Orphan Recovery & Build State | Logic | Ready | ADR-006 |
| 007 | Pre-Save Validation | Logic | Ready | ADR-006 |
| 008 | Account/Profile System | Integration | Ready | ADR-001 |

## Next Step

Run `/dev-story` on a save & profile story to begin implementation.
