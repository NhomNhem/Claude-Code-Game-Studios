# Story Index — Tiny Rift Survivors

## Story Format

Each story file lives in `production/stories/` as `[epic-id]-NNN-[slug].md`.

```
FOUNDATION-001-001-init-docs.md     FOUNDATION-001-002-template-audit.md
BACKEND-001-001-remove-defines.md   CONCEPT-001-001-brainstorm.md
...
```

## Current Sprint Stories

None yet — project is in Concept phase.

## All Stories (Planned)

| ID | Epic | Story Name | Status | Priority |
|----|------|-----------|--------|----------|
| — | FOUNDATION-001 | Initialize project documentation | Completed | P0 |
| — | FOUNDATION-001 | Audit template systems | Completed | P0 |
| — | BACKEND-001 | Remove FIREBASE/FUSION2 defines for Public Release | Planned | P0 |
| — | CONCEPT-001 | Brainstorm game concept | Planned | P0 |
| — | CONCEPT-001 | Map systems & define customization scope | Planned | P0 |
| — | CONCEPT-002 | Create _TinyRift/ directory structure | Planned | P0 |
| — | CONCEPT-002 | Configure VContainer for custom systems | Planned | P0 |
| — | CONCEPT-003 | Author art bible | Planned | P0 |
| — | CONCEPT-003 | Generate asset specs | Planned | P0 |
| — | CORE-001 | Implement fire skill (extend SkillData) | Planned | P1 |
| — | CORE-001 | Implement ice skill (extend SkillData) | Planned | P1 |
| — | CORE-001 | Implement lightning skill (extend SkillData) | Planned | P1 |
| — | CORE-003 | Implement elemental synergy resolver | Planned | P1 |
| — | CORE-003 | Implement synergy procs & damage modifiers | Planned | P1 |
| — | CORE-002 | Implement 5 custom enemy types | Planned | P1 |
| — | CORE-002 | Configure wave progression data | Planned | P1 |
| — | PROG-001 | Design & implement meta-progression | Planned | P2 |
| — | PROG-002 | Extend PlayerSave for custom data | Planned | P2 |
| — | PROG-003 | Configure in-run shop | Planned | P2 |
| — | POLISH-001 | VFX pass (synergy effects, hits, FX) | Planned | P3 |
| — | POLISH-001 | Audio pass (SFX, music) | Planned | P3 |
| — | POLISH-002 | UI polish (menus, HUD, transitions) | Planned | P3 |
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
- **Ready for Review**: Implementation complete, awaiting review
- **Locked**: Lab Track — not for current sprint

## Story Lifecycle

1. Epic → `/create-stories` → story file with embedded TR-IDs
2. `/story-readiness` → validates story is ready
3. `/dev-story` → implements story
4. `/code-review` → reviews implementation
5. `/story-done` → marks complete, surfaces next story
