# Tiny Rift Survivors — Claude Code Game Studios

A Unity 6 survivor-like bullet heaven game built on the BulletHell Elemental Template (Bizachi).

## Technology Stack

- **Engine**: Unity 6000.3.11f1 (Unity 6)
- **Language**: C# (.NET Standard 2.1, IL2CPP)
- **Rendering**: URP 17.3 (2D Renderer)
- **Input**: Unity Input System 1.19.0
- **DI Framework**: VContainer (bundled)
- **Async**: UniTask (bundled)
- **Tweening**: LeanTween (bundled)
- **State Machines**: UnityHFSM (bundled)
- **Version Control**: Git with trunk-based development
- **Template**: BulletHell Elemental Template (Bizachi)

## Development Tracks

**Public Release Track** (ACTIVE) — stable, tested systems only.
**Full-Stack Lab Track** (LOCKED) — Firebase, Fusion 2, WebSocket/SQL, Battle Pass, IAP. Behind `#if LAB_TRACK`.

**CRITICAL**: The template already has ALL backend infrastructure built in (Firebase, WebSocket, Fusion 2, IAP, Battle Pass). These must be DISABLED for Public Release — not enabled later.

## Immutable Rules

1. NEVER modify `Assets/BulletHellTemplate/` vendor code
2. NEVER refactor template manager singletons
3. NEVER modify existing scenes or prefabs
4. NEVER enable backend services in Public Release builds
5. NEVER commit backend credentials
6. ALWAYS write custom code to `Assets/_TinyRift/`
7. ALWAYS keep Lab Track code in `Assets/_TinyRift/Lab/`
8. NEVER remove bundled libraries — just don't initialize unused ones

## Project Structure

```
/
├── CLAUDE.md                         # Master configuration
├── AGENTS.md                         # OpenCode agent configuration
├── .claude/                          # CCGS agent definitions, skills, hooks, rules
├── .opencode/                        # OpenCode configuration & OPS-X commands
├── .github/                          # GitHub templates, prompts, skills
├── Tiny-Rift-Survivors-GameClient/   # Unity project root
│   ├── Assets/
│   │   ├── BulletHellTemplate/       # VENDOR — never modify (~250+ scripts)
│   │   │   ├── Core/                 # Core gameplay, DataHandler, Systems
│   │   │   ├── Addons/               # DailyRewards, Inventory, Multiplayer
│   │   │   ├── Res/                  # Art, audio, prefabs, scenes, data
│   │   │   └── ThirdPartyResources/  # Colyseus, LeanTween, UniTask, VContainer, etc.
│   │   ├── Scenes/                   # User scenes (only SampleScene currently)
│   │   ├── Settings/                 # URP pipeline assets
│   │   ├── Firebase/                 # Firebase SDK (12.2.0)
│   │   ├── InputSystem_Actions.inputactions  # Player action map (8 actions)
│   │   └── _TinyRift/               # CUSTOM CODE DIR (not yet created)
│   │       └── Lab/                  # Lab Track code
│   └── ...
├── Tiny-Rift-Survivors-Docs/         # Astro/Starlight documentation site
├── design/                           # GDDs, narrative docs, balance data
├── docs/                             # Technical docs, architecture, roadmaps
│   ├── technical/                    # Template audit, system/backend maps
│   ├── product/                      # Product brief
│   └── roadmap/                      # Project roadmap
└── production/                       # Sprints, milestones, epics, stories
```

## Engine Version Reference

Unity 6000.3.11f1 — API reference: `docs/engine-reference/unity/`
LLM knowledge cutoff for Unity is ~2022 LTS. Always check engine reference docs
before suggesting Unity 6 API calls.

## Source Code Layout

Custom Unity code in `Tiny-Rift-Survivors-GameClient/Assets/_TinyRift/`.
Template vendor code in `Tiny-Rift-Survivors-GameClient/Assets/BulletHellTemplate/`.
Lab Track code in `Tiny-Rift-Survivors-GameClient/Assets/_TinyRift/Lab/`.

## Testing

Unity Test Framework (UTF, built-in) for unit and play mode tests.

## Collaboration Protocol

**User-driven collaboration, not autonomous execution.**
Every task follows: **Question -> Options -> Decision -> Draft -> Approval**

- Show drafts before writing
- Multi-file changes require approval
- No commits without instruction

## Current Stage

- **Stage**: Concept (production/stage.txt)
- **Review Mode**: full (production/review-mode.txt)
- **Template Audit**: docs/technical/template-audit.md
- **System Map**: docs/technical/system-map.md
- **Backend Map**: docs/technical/backend-map.md
- **Custom Code Dir**: `_TinyRift/` — not yet created

## Key Template Systems (Built In)

| System | Class | Customization |
|--------|-------|--------------|
| Game State | GameManager, GameplayManager, GameInstance | Configure |
| Character | CharacterEntity, CharacterControllerComponent | Extend |
| Combat | CharacterAttackComponent, IDamageable | Extend |
| Skills | SkillData (ScriptableObject), SkillDamageProvider | Extend |
| Enemies | MonsterEntity, MonsterHealth | Extend |
| Buffs | CharacterBuffsComponent, ActiveBuff | Extend |
| Waves | Wave, GameplayManager | Configure |
| Save/Load | PlayerSave (partial), SecurePrefs | Configure |
| Event Bus | EventBus (typed events) | Extend |
| Pooling | MonsterPool, DropPool, etc. | Configure |
| Localization | LanguageManager | Configure |
