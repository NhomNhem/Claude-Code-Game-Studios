# Customization Plan — Tiny Rift Survivors

## Fundamental Approach

The BulletHell Elemental Template provides a **complete game framework** with ~250+ scripts.
We are **extending and configuring**, not building from scratch. Most systems already exist
in the template — our job is to add content, tune configurations, and disable unneeded backend features.

## Directory Structure

```
Assets/
├── BulletHellTemplate/           # VENDOR — never modify
│   ├── Core/                     # All template systems (~250+ files)
│   ├── Addons/                   # DailyRewards, Inventory, Multiplayer, PCDesktop, RewardPopup
│   ├── Res/                      # Art, audio, VFX, prefabs, scenes
│   └── ThirdPartyResources/      # Colyseus, LeanTween, UniTask, VContainer, UnityHFSM, UIEffect
│
└── _TinyRift/                    # ALL custom code (does not exist yet — create on first use)
    ├── Scripts/
    │   ├── Skills/               # Custom skill definitions + synergy system
    │   ├── Enemies/              # Custom enemy configurations + behaviors
    │   ├── Config/               # ScriptableObject configs (wave presets, balance data)
    │   ├── UI/                   # Custom UI extensions (HUD overrides, new menus)
    │   └── Systems/              # Custom game systems (meta-progression, achievements)
    ├── Art/                      # Custom sprites, textures, animations
    ├── Audio/                    # Custom SFX, music
    ├── Prefabs/                  # Custom prefabs
    └── Scenes/                   # Custom scenes if needed
```

## Forbidden

1. NEVER modify any file under `Assets/BulletHellTemplate/`
2. NEVER refactor template manager singletons (GameManager, GameplayManager, etc.)
3. NEVER modify existing scenes under `BulletHellTemplate/Res/Scenes/`
4. NEVER modify existing prefabs under `BulletHellTemplate/`
5. NEVER remove bundled third-party libraries (Colyseus, etc. — just don't call them)
6. NEVER rename/restructure template folders
7. NEVER add `LAB_TRACK` define to Public Release builds

## Backend Disablement Plan

### Immediate (Concept Phase)
- Document current define symbols (FIREBASE on Standalone, FUSION on Android/WebGL)
- Decision required: remove backend defines from Public Release build config

### Implementation Plan
```csharp
// Option A: Remove defines entirely (cleanest for Public Release)
// Project Settings > Player > Standalone > Scripting Define Symbols: UNITY_PIPELINE_URP
//
// Option B: Add LAB_TRACK guard (keeps both tracks)
// Project Settings > Player > Standalone > Scripting Define Symbols: UNITY_PIPELINE_URP
// Lab Track builds add LAB_TRACK
```

## Implementation Strategy (Template Systems)

### Configure (tuning data, no code changes)
- Wave configurations → `Wave.cs`, wave data files
- Character stats → `CharacterData` ScriptableObject
- Skill parameters → `SkillData` ScriptableObject
- Shop items → `ShopItem` ScriptableObject
- Drop tables → Drop configuration data
- XP curves → Leveling data in DataHandler

### Extend (new subclasses, interface implementations)
- Custom skills → New `SkillData` + damage provider implementations
- Custom enemies → New `MonsterEntity` configurations
- UI screens → New screen scripts in `_TinyRift/Scripts/UI/`
- Elemental synergies → New system in `_TinyRift/Scripts/Systems/`

### Create (new systems, not in template)
- Meta-progression (between-run persistent upgrades)
- Achievement system
- Steam integration
- Custom elemental synergy resolver

## Build Pipeline

Three build configurations:
1. **Public Release** — defines: `UNITY_PIPELINE_URP` (no backend)
2. **Lab Track Dev** — defines: `UNITY_PIPELINE_URP;LAB_TRACK`
3. **Editor** — defines: as configured; careful of `FIREBASE`/`FUSION` activation

## Custom Code Design Principles

1. **Use VContainer** — template already uses it; register new systems in existing scope
2. **Use EventBus** — template has typed events; prefer event-driven decoupling
3. **Use ScriptableObjects** — template patterns use SOs for all configurable data
4. **Work WITH template patterns** — singletons, component-based entities, FSM animations
5. **No DOTS/ECS** — template is pure MonoBehaviour; maintain consistency
6. **UGUI only** — no UI Toolkit
