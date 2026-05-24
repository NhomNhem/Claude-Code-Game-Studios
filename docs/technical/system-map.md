# System Map — Tiny Rift Survivors

## Architecture Layers

```
┌──────────────────────────────────────────────────────────────┐
│                   Presentation Layer                          │
│   UIGameplay   UIMainMenu   Popups   HUD   DamageNumbers     │
│   UIElements (CharacterEntry, ShopEntry, etc.)               │
├──────────────────────────────────────────────────────────────┤
│                    Gameplay Layer                             │
│   CharacterEntity   MonsterEntity   Combat   Skills   Buffs  │
│   Projectiles   Waves   Drops   XP   Gold   Upgrades         │
│   Movement (2D)   Collision   Pooling   FSM Animation        │
├──────────────────────────────────────────────────────────────┤
│                    Systems Layer                              │
│   EventBus   InstancePool   LanguageManager   SaveSystem     │
│   GameManager   GameplayManager   LoadingManager             │
│   VContainer DI   BackendLifetimeScope                       │
├──────────────────────────────────────────────────────────────┤
│                  [Backend Layer — BUILT IN]                    │
│   DataHandler (IBackendService abstraction)                   │
│   ├── FirebaseBackendService                                  │
│   ├── WebSocketSqlBackendService                              │
│   └── OfflineBackendService (local fallback)                  │
│   AuthManager   IAPManager   MonetizationManager             │
│   BattlePassManager   Fusion 2   Colyseus                     │
└──────────────────────────────────────────────────────────────┘
```

## Template Systems (Already Built — No Custom Code Written Yet)

The BulletHell Elemental Template provides ALL of these systems out of the box.
Our job is to configure, extend, and customize — not build from scratch.

| System | Template Class(es) | Extends? |
|--------|-------------------|----------|
| Game State | GameManager, GameplayManager, GameInstance | Configure |
| Player Character | CharacterEntity, CharacterControllerComponent | Extend |
| Stats | CharacterStats, CharacterStatsComponent, CharacterStatsRuntime | Configure |
| Movement | CharacterControllerComponent, AdvancedCharacterController2D | Configure |
| Combat | CharacterAttackComponent, IDamageable, DamageEntity | Extend |
| Skills | SkillDamageProvider, SkillPerkDamageProvider, SkillData | Extend |
| Buffs | CharacterBuffsComponent, ActiveBuff, BuffCategory | Extend |
| Enemies | MonsterEntity, MonsterHealth, MonsterMovementComponent | Extend |
| Waves | Wave, WaveManager (via GameplayManager) | Configure |
| Projectiles | MonsterDamageEntity, MonsterOrbitManager | Extend |
| Drops | DropEntity, DropPool | Configure |
| XP/Leveling | CharacterStats (XP fields), DataHandler sync | Configure |
| Save/Load | PlayerSave partial classes + SecurePrefs | Configure |
| Shop | ShopItem ScriptableObject, ShopManager | Configure |
| Inventory | Inventory (Addon), InventorySave | Configure |
| Localization | LanguageManager + Components | Configure |
| Event Bus | EventBus (typed events) | Extend |
| Object Pooling | MonsterPool, DropPool, DamagePopup, SoundEffectsPool | Configure |
| UI Framework | UIElements prefab system, UIGameplay, UIMainMenu | Extend |
| Animation FSM | CharacterAnimationFSM, DirectionalAnimSet | Extend |
| Input | InputSystem_Actions.inputactions (8 actions) | Configure |
| DI Container | VContainer + BackendLifetimeScope | Extend |

## Backend Systems (Built In — Must Be DISABLED for Public Release)

| System | Template Class(es) | Status |
|--------|-------------------|--------|
| Firebase Auth | FirebaseAuthManager, AuthManager | Remove defines |
| Firebase Firestore | FirebaseManager + 16 sync handlers | Remove defines |
| Firebase Save | FirebaseSave | Remove defines |
| WebSocket/SQL | WebSocketSqlBackendService + 15 sync handlers | Remove defines |
| Fusion 2 Lobby | FusionLobbyManager, UILobby | Remove defines |
| Multiplayer | Fusion 2 (Addon) + Colyseus | Remove defines |
| IAP | IAPManager, MonetizationManager, Purchasing 4.14.2 | Remove defines |
| Battle Pass | BattlePassManager, BattlePassItem, UIBattlePass | Remove defines |
| Ranking | UIRankingMenu, FirebaseRankingHandler | Remove defines |

## Custom Systems to Build (in Assets/_TinyRift/)

| System | Description | Priority |
|--------|-------------|----------|
| Elemental Skill Synergies | Fire+Ice=Freeze, Fire+Lightning=Chain, Ice+Lightning=Shatter | P1 |
| Custom Skills | 3 signature skills with synergy-aware damage logic | P1 |
| Custom Enemies | 5+ enemy types with synergy-weakness system | P1 |
| Map Configs | Wave compositions, spawn patterns, difficulty curves | P1 |
| Meta-Progression | Between-run persistent upgrades (extends template save system) | P2 |
| Achievement System | Steam-based achievements | P2 |
