# Technical Preferences

<!-- Populated by /setup-engine (2026-05-25). Updated as decisions are made. -->
<!-- All agents reference this file for project-specific standards and conventions. -->

## Engine & Language

- **Engine**: Unity 6000.3.11f1 (Unity 6 Update 3)
- **Language**: C# (.NET Standard 2.1, IL2CPP)
- **Rendering**: URP 17.3 (2D Renderer)
- **Physics**: Built-in 2D Physics (Box2D)

## Input & Platform

<!-- Written by /setup-engine. Read by /ux-design, /ux-review, /test-setup, /team-ui, and /dev-story -->
<!-- to scope interaction specs, test helpers, and implementation to the correct input methods. -->

- **Target Platforms**: PC, Mobile
- **Input Methods**: Keyboard/Mouse, Gamepad, Touch
- **Primary Input**: Keyboard/Mouse (PC), Touch (Mobile)
- **Gamepad Support**: Full
- **Touch Support**: Full
- **Platform Notes**: URP 2D Renderer scales well on mobile. UI must support both mouse and touch interactions. No hover-only interactions (mobile compatibility). Input System 1.19.0 with action maps per platform.

## Naming Conventions

- **Classes**: PascalCase (e.g., `PlayerController`)
- **Public fields/properties**: PascalCase (e.g., `MoveSpeed`)
- **Private fields**: _camelCase (e.g., `_moveSpeed`)
- **Methods**: PascalCase (e.g., `TakeDamage()`)
- **Files**: PascalCase matching class (e.g., `PlayerController.cs`)
- **Prefabs/Scenes**: PascalCase matching root MonoBehaviour (e.g., `PlayerController.prefab`)
- **Constants**: PascalCase (e.g., `MaxHealth`) or UPPER_SNAKE_CASE for bitflags (e.g., `FLAG_INVULNERABLE`)

## Performance Budgets

- **Target Framerate**: 60 FPS (PC), 30 FPS (mobile minimum)
- **Frame Budget**: 16.6ms (PC), 33.3ms (mobile)
- **Draw Calls**: < 300 (mobile), < 500 (PC)
- **Memory Ceiling**: 512 MB (mobile), 2 GB (PC)
- **VFX**: Particle system pooling, object pooling via MonsterPool/DropPool (template built-in)

## Testing

- **Framework**: Unity Test Framework (NUnit-based)
- **Minimum Coverage**: Balance formulas, gameplay systems, networking (if applicable)
- **Required Tests**: Core loop validation, upgrade/stat calculations, damage formulas, save/load integrity
- **Test Location**: `Assets/_TinyRift/Tests/` (EditMode for logic, PlayMode for integration)

## Forbidden Patterns

<!-- Add patterns that should never appear in this project's codebase -->
- [None configured yet — add as architectural decisions are made]

## Allowed Libraries / Addons

<!-- Add approved third-party dependencies here -->
- [None configured yet — add as dependencies are approved]

## Architecture Decisions Log

<!-- Quick reference linking to full ADRs in docs/architecture/ -->
- [No ADRs yet — use /architecture-decision to create one]

## Engine Specialists

<!-- Written by /setup-engine when engine is configured. -->
<!-- Read by /code-review, /architecture-decision, /architecture-review, and team skills -->
<!-- to know which specialist to spawn for engine-specific validation. -->

- **Primary**: unity-specialist
- **Language/Code Specialist**: unity-specialist (C# review — primary covers it)
- **Shader Specialist**: unity-shader-specialist (Shader Graph, HLSL, URP/HDRP materials)
- **UI Specialist**: unity-ui-specialist (UI Toolkit UXML/USS, UGUI Canvas, runtime UI)
- **Additional Specialists**: unity-dots-specialist (ECS, Jobs system, Burst compiler), unity-addressables-specialist (asset loading, memory management, content catalogs)
- **Routing Notes**: Invoke primary for architecture and general C# code review. Invoke DOTS specialist for any ECS/Jobs/Burst code. Invoke shader specialist for rendering and visual effects. Invoke UI specialist for all interface implementation. Invoke Addressables specialist for asset management systems.

### File Extension Routing

| File Extension / Type | Specialist to Spawn |
|-----------------------|---------------------|
| Game code (.cs files) | unity-specialist |
| Shader / material files (.shader, .shadergraph, .mat) | unity-shader-specialist |
| UI / screen files (.uxml, .uss, Canvas prefabs) | unity-ui-specialist |
| Scene / prefab / level files (.unity, .prefab) | unity-specialist |
| Native extension / plugin files (.dll, native plugins) | unity-specialist |
| General architecture review | unity-specialist |
