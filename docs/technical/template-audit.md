# Template Audit — BulletHell Elemental Template

Audit date: 2026-05-24
Audited version: BulletHell Elemental Template (Bizachi)
Unity version: 6000.3.11f1 (Unity 6)

## Source Structure

```
Assets/BulletHellTemplate/
├── Core/                         # Core gameplay framework (~250+ files)
│   ├── 2D/                       # 2D pathfinding
│   ├── Backend/                  # Firebase auth/manager, web request utils
│   ├── DataHandler/              # FULL backend sync layer (VContainer DI)
│   │   ├── Backend/              # FirebaseBackendService, WebSocketSqlBackendService, OfflineBackendService
│   │   ├── DataExport/           # Exporter tools (editor)
│   │   ├── DTOs/                 # Friends, Mail, MapEvent, Presence DTOs
│   │   ├── Local/                # PlayerSave (partial classes), SecurePrefs
│   │   └── Sync/                 # FirebaseSync (16 handlers), OfflineSync (7), WebsocketSync (15)
│   ├── Editor/                   # Custom editors for managers, scriptables, data
│   ├── Gameplay/                 # Character, Battle, Skills, Stats, Models
│   │   ├── Character/            # BaseCharacterEntity, CharacterEntity, CharacterController...
│   │   ├── Battle/               # MonsterEntity, MonsterSkill, MonsterHealth
│   │   ├── Skills/               # ActiveBuff, BuffCategory, SkillDamageProvider
│   │   └── Stat/                 # StatType enum
│   ├── LanguageManager/          # Localization system (Text, Audio, Fonts)
│   ├── LocalSave/                # PlayerPrefsDebugger
│   ├── MainMenu/Lobby/           # FusionLobbyManager, UILobby, room/network utils
│   ├── Misc/                     # Animations, spritesheet renderer, UI effects
│   ├── Scriptables/              # ScriptableObjects: CharacterData, SkillData, ShopItem, IAPItem...
│   ├── Skill/                    # SkillSettings
│   ├── Systems/                  # EventBus, InstancePool, FSM, FriendList, Mailbox, GMPanel
│   └── UIElements/               # UI entry prefab scripts (CharacterEntry, ShopEntry...)
├── Addons/
│   ├── DailyRewards/             # Daily login + new account reward system
│   ├── Inventory/                # Persistent inventory + item slots
│   ├── Multiplayer/              # Fusion 2 PVP/Arena/BattleRoyale scripts
│   ├── PCDesktop/                # PC input & skill controllers
│   └── RewardPopup/              # Reward presentation popup system
├── Res/                          # Art, audio, VFX, prefabs, scenes, game data
├── Packages/                     # Builtin.unitypackage
└── ThirdPartyResources/          # Colyseus, LeanTween, UniTask, VContainer, UnityHFSM, UIEffect
```

## Key Architecture Findings

### Already Active Backend Systems
The template ships with a FULL backend layer already wired — this changes the strategy from "build later" to "disable for Public Release":

| System | Status | Where |
|--------|--------|-------|
| Firebase Auth | Built-in | `Core/Backend/FirebaseAuthManager.cs` |
| Firebase Firestore | Built-in | `Core/Backend/FirebaseManager.cs` + 16 sync handlers |
| WebSocket/SQL Backend | Built-in | `Core/DataHandler/Backend/WebSocketSqlBackendService.cs` + 15 sync handlers |
| Offline Backend (fallback) | Built-in | `Core/DataHandler/Backend/OfflineBackendService.cs` |
| Backend DI (VContainer) | Built-in | `Core/DataHandler/BackendLifetimeScope.cs` |
| Fusion 2 Multiplayer | Built-in (Addon) | `Addons/Multiplayer/` + `Core/MainMenu/Lobby/` |
| Unity IAP | Built-in | `Core/IAPManager.cs`, `Core/MonetizationManager.cs` |
| Battle Pass | Built-in | `Core/BattlePassManager.cs`, `Core/BattlePassItem.cs` |
| Auth System | Built-in | `Core/AuthManager.cs` |

### Scripting Define Symbols
| Platform | Symbols | Implication |
|----------|---------|-------------|
| Standalone | `UNITY_PIPELINE_URP; FIREBASE` | Firebase is enabled in standalone — must be stripped for Public Release |
| Android | `UNITY_PIPELINE_URP; FUSION_*` | Fusion 2 is enabled — must be stripped for Public Release |
| WebGL | `UNITY_PIPELINE_URP; FUSION_*` | Fusion 2 enabled — must be stripped for Public Release |

**Critical**: The `FIREBASE` define is set on Standalone and `FUSION2` on Android/WebGL. We need to decide whether to remove these from Public Release build configs.

### Third-Party Libraries (Bundled)
| Library | Purpose | Notes |
|---------|---------|-------|
| VContainer | Dependency Injection | Used by BackendLifetimeScope |
| Colyseus | Multiplayer SDK | Additional networking alongside Fusion 2 |
| UniTask | Async/await | C# async patterns without coroutines |
| LeanTween | Tweening/animation | Lightweight animation |
| UnityHFSM | State machines | Hierarchical finite state machine |
| UIEffect | UI effects (outline, shadow, etc.) | UGUI extensions |

### Existing Systems (Already Built In)
- **Movement**: `CharacterControllerComponent`, `AdvancedCharacterController2D`
- **Combat**: `CharacterAttackComponent`, `DamageEntity`, `IDamageable`, `MonsterHealth`
- **Skills**: `SkillDamageProvider`, `SkillPerkDamageProvider`, `ActiveBuff`
- **Projectiles**: `MonsterDamageEntity`, `MonsterOrbitManager`
- **Wave system**: `Wave.cs`, `WaveManager` (part of GameplayManager)
- **XP/Leveling**: `CharacterStats`, `CharacterStatsRuntime`, XP system in DataHandler
- **Buff system**: `CharacterBuffsComponent`, `BuffCategory`
- **Save system**: PlayerSave (partial classes across multiple files)
- **EventBus**: Typed event system (PlayerEvents, EnemyEvents, GameplayEvents, etc.)
- **Object Pooling**: `MonsterPool`, `DropPool`, `DamagePopup`, `SoundEffectsPool`
- **Localization**: `LanguageManager` with Text/Audio/Font switching
- **FSM Animation**: `CharacterAnimationFSM` with directional sets

## Scenes (8 in Build)

| Index | Scene | Purpose |
|-------|-------|---------|
| 0 | Login | Authentication screen |
| 1 | Home | Main menu hub |
| 2 | MapArena1 | Gameplay arena 1 |
| 3 | MapArena2 | Gameplay arena 2 |
| 4 | MapArena3 | Gameplay arena 3 |
| 5 | MapArena4 | Gameplay arena 4 |
| 6 | PVPArenaBR | Battle Royale arena |
| 7 | PVPArena2 | PVP arena 2 |

## Input System

Action asset: `Assets/InputSystem_Actions.inputactions`
One action map "Player" with 8 actions: Move, Look, Attack, Interact, Jump, Sprint, Previous, Next
Bindings for Keyboard+Mouse and Gamepad. Active Input Handler: Input System Package.

## Project Settings

| Setting | Value |
|---------|-------|
| Product Name | `Tiny-Rift-Survivors-GameClient` (needs rename) |
| Company Name | `DefaultCompany` (needs rename) |
| Bundle Version | `0.0.2` |
| Standalone Identifier | `com.DefaultCompany.Tiny-Rift-Survivors-GameClient` |
| Color Space | Linear |
| Scripting Backend | IL2CPP |
| API Compatibility | .NET Standard 2.1 |

## Key Directives

1. **Never** modify `Assets/BulletHellTemplate/` vendor code
2. **Never** refactor manager singletons (GameManager, GameplayManager, etc.)
3. **Never** modify existing scenes or prefabs
4. **Never** remove bundled third-party libraries from template's ThirdPartyResources
5. **Beware**: Backend services are wired via VContainer — avoid triggering them in builds
6. `Assets/_TinyRift/` does **not exist yet** — must be created as custom code directory
