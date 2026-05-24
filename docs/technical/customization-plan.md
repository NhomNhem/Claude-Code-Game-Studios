# Customization Plan — Tiny Rift Survivors

## Fundamental Approach

The BulletHell Elemental Template provides a **complete game framework** with ~250+ scripts
including a full backend abstraction layer (`IBackendService`). We are:

1. **Configuring** template systems for our needs
2. **Extending** with custom content (skills, enemies, synergies)
3. **Configuring** `WebSocketSqlBackendService` as primary production backend
4. **Building** the Node.js/Colyseus/MySQL server (`tiny-rift-server`)
5. **Deferring** Firebase, Fusion 2, IAP, Battle Pass

## Directory Structure

```
Assets/
├── BulletHellTemplate/                # VENDOR — never modify
└── _TinyRift/                         # ALL custom code (create on first use)
    ├── Scripts/
    │   ├── Backend/                   # M0 — backend bootstrap + services
    │   │   ├── BackendSettings.asset  # ScriptableObject toggle
    │   │   ├── BackendBootstrap.cs    # VContainer registration
    │   │   ├── LoginService.cs
    │   │   ├── ProfileService.cs
    │   │   ├── CurrencyService.cs
    │   │   └── WebSocketConfig.cs
    │   ├── Skills/                    # Custom skill definitions + synergy system
    │   ├── Enemies/                   # Custom enemy configurations
    │   ├── Config/                    # ScriptableObject configs
    │   ├── UI/                        # Custom UI extensions
    │   └── Systems/                   # Custom game systems
    ├── Art/
    ├── Audio/
    ├── Prefabs/
    └── Future/                        # Firebase, Fusion, IAP, BP (locked)
```

## Backend Configuration Plan

### WebSocketSqlBackendService (Template Built-In)
The template's `WebSocketSqlBackendService` already provides:
- WebSocket connection management
- Message serialization/deserialization
- Sync handlers for auth, profile, progress, purchases, rewards, etc.

**Our task**: Configure the existing service for our server, not rebuild it.

### Extending the Template's Backend
```csharp
// BackendBootstrap.cs — in _TinyRift/Scripts/Backend/
// Registered in VContainer alongside or extending BackendLifetimeScope

var settings = Resources.Load<BackendSettings>("BackendSettings");

switch (settings.backendMode)
{
    case BackendMode.Online:
        // Configure WebSocketSqlBackendService with server URL
        container.Register<IWebSocketConfig>(new WebSocketConfig { url = settings.serverUrl });
        container.Register<IBackendService, WebSocketSqlBackendService>();
        break;
    case BackendMode.Offline:
        container.Register<IBackendService, OfflineBackendService>();
        break;
}
```

## Implementation Order

### M0 — Backend Foundation (NOW)
| # | Task | Where |
|---|------|-------|
| 1 | Create `Assets/_TinyRift/` directory structure | Unity |
| 2 | Create `BackendSettings.asset` ScriptableObject | Unity |
| 3 | Create `BackendBootstrap.cs` (VContainer registration) | Unity |
| 4 | Configure `WebSocketSqlBackendService` connection | Unity |
| 5 | Create `tiny-rift-server` repo (Node.js + Colyseus) | Server |
| 6 | MySQL schema (users, profiles, currencies) | Server |
| 7 | Login handler (server-side auth) | Server |
| 8 | Profile handler (server-side read/write) | Server |
| 9 | Currency handler (server-authoritative) | Server |
| 10 | Login → Profile → Currency end-to-end test | Both |

### M1 — Core Gameplay (after M0)
- Elemental skills, enemies, waves
- Extend template gameplay systems
- Basic HUD integration with backend currency

### M2 — Progression
- Meta-progression, save/load, achievements
- Shop (in-run + persistent)

### M3 — Polish & Release
- Balance, VFX, audio, performance
- Steam integration
- Early Access

## Forbidden

1. NEVER modify `Assets/BulletHellTemplate/` vendor code
2. NEVER refactor template manager singletons
3. NEVER modify existing scenes or prefabs
4. NEVER enable Firebase or Fusion 2 in builds
5. NEVER remove bundled third-party libraries
6. NEVER add `FIREBASE` or `FUSION_*` defines back to Player Settings
