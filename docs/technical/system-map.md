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
│   EventBus   InstancePool   LanguageManager                  │
│   GameManager   GameplayManager   LoadingManager             │
├──────────────────────────────────────────────────────────────┤
│                  Backend Abstraction Layer                     │
│   IBackendService (VContainer DI via BackendLifetimeScope)    │
│   ├── WebSocketSqlBackendService    ← PRIMARY — production   │
│   ├── OfflineBackendService         ← FALLBACK — dev/test    │
│   └── FirebaseBackendService        ← DEFERRED               │
│   BackendSettings.asset                                       │
│   BackendBootstrap                                            │
├──────────────────────────────────────────────────────────────┤
│                    Server Side (tiny-rift-server)              │
│   Node.js + Colyseus                                         │
│   WebSocket Gateway → Auth → Handlers → MySQL DB              │
│   Tables: users, profiles, currencies, leaderboards           │
└──────────────────────────────────────────────────────────────┘
```

## Template Systems (Already Built)

| Layer | System | Template Class(es) | Action |
|-------|--------|-------------------|--------|
| Presentation | UI Framework | UIElements, UIGameplay, UIMainMenu | Extend |
| Gameplay | Character | CharacterEntity, CharacterControllerComponent | Extend |
| Gameplay | Combat | CharacterAttackComponent, IDamageable | Extend |
| Gameplay | Skills | SkillData (SO), SkillDamageProvider | Extend |
| Gameplay | Enemies | MonsterEntity, MonsterHealth, MonsterMovement | Extend |
| Gameplay | Waves | Wave, GameplayManager | Configure |
| Gameplay | Buffs | CharacterBuffsComponent, ActiveBuff | Extend |
| Gameplay | Projectiles | MonsterDamageEntity, MonsterOrbitManager | Extend |
| Gameplay | Drops | DropEntity, DropPool | Configure |
| Gameplay | Movement | CharacterControllerComponent, AdvancedCharacterController2D | Configure |
| Systems | Save/Local | PlayerSave (partial), SecurePrefs | Extend |
| Systems | Event Bus | EventBus (typed events) | Extend |
| Systems | Pooling | MonsterPool, DropPool, DamagePopup | Configure |
| Systems | Localization | LanguageManager | Configure |
| Backend | DI Container | VContainer + BackendLifetimeScope | Extend |
| Backend | WebSocket SQL | WebSocketSqlBackendService (built in) | **Configure — primary** |
| Backend | Offline | OfflineBackendService (built in) | **Configure — fallback** |
| Backend | Firebase | FirebaseBackendService + 16 sync handlers | **DEFER** |

## M0 Backend Flow

```
┌───────────────────────────────────────────────────────┐
│                  Unity Game Client                      │
│                                                         │
│  BackendBootstrap                                       │
│    ├── Reads BackendSettings.asset                      │
│    ├── Registers IBackendService in VContainer          │
│    └── Starts connection (Online → WS, Offline → local) │
│                                                         │
│  On Startup:                                            │
│    LoginService.Login(username, password)                │
│      → WebSocket request to server                      │
│      → Server validates → returns user+token            │
│                                                         │
│  ProfileService.Load()                                   │
│      → Server returns profile data                      │
│                                                         │
│  CurrencyService.GetBalance()                            │
│      → Server returns authoritative currency            │
└──────────────────────┬────────────────────────────────┘
                       │ WebSocket
┌──────────────────────▼────────────────────────────────┐
│              tiny-rift-server (Node.js)                  │
│                                                         │
│  Colyseus WebSocket Gateway                             │
│  ├── Auth handler (login/register)                      │
│  ├── Profile handler (read/update)                      │
│  ├── Currency handler (add/spend — server-authoritative)│
│  └── Leaderboard handler (future)                       │
│                                                         │
│  MySQL Database                                         │
│  ├── users (auth, email, password_hash)                 │
│  ├── profiles (display_name, stats, wave records)       │
│  └── currencies (gold, gems, version for concurrency)   │
└───────────────────────────────────────────────────────┘
```

## Future Systems (Locked — in Assets/_TinyRift/Future/)

| System | When | Justification |
|--------|------|---------------|
| Firebase Auth + Firestore | Deferred | Not on primary path |
| Fusion 2 Multiplayer | Future | After core game loop ships |
| IAP / Battle Pass | Future | Post-launch monetization |
| Analytics | Future | When needed for live-ops |
