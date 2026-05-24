# Backend Map — Tiny Rift Survivors

## CRITICAL: Backend Is BUILT IN, Not Planned

Unlike a typical project where backend services would be added later, the
BulletHell Elemental Template already ships with a full backend layer:

- Firebase Auth + Firestore (12.2.0)
- WebSocket/SQL backend with full sync handlers
- Fusion 2 multiplayer (Addons/Multiplayer/)
- Colyseus multiplayer SDK (bundled)
- Unity IAP (Purchasing 4.14.2)
- Battle Pass system
- Ranking/leaderboard system
- GM/admin panel

**The task is not "enable these later" — it's "disable these NOW for Public Release."**

## Current Scripting Define Symbols

| Platform | Symbols | Backend Status |
|----------|---------|---------------|
| Standalone | `UNITY_PIPELINE_URP;FIREBASE` | **Firebase active** — must strip for Release |
| Android | `UNITY_PIPELINE_URP;FUSION_*` | **Fusion 2 active** — must strip for Release |
| WebGL | `UNITY_PIPELINE_URP;FUSION_*` | **Fusion 2 active** — must strip for Release |

## Public Release Track — Backend Removal Strategy

### Step 1: Remove Define Symbols
Remove backend defines from Public Release build config:
```
Public Release: UNITY_PIPELINE_URP (ONLY)
Lab Track:     UNITY_PIPELINE_URP;LAB_TRACK
```

### Step 2: Asset Stripping
Use Unity's Managed Stripping Level + Linker to strip unused backend code:
- Already set to "Minimal" — increase to "Low" or "Medium"
- Create a `link.xml` that explicitly keeps gameplay assemblies only

### Step 3: Scene Management
Current build includes 8 scenes — Public Release needs a subset:
- Remove Login scene (no auth needed for offline game)
- Remove PVPArena scenes (no multiplayer)
- Keep: Home, MapArena1-4

## Full-Stack Lab Track

### Enablement Method
```csharp
// LAB_TRACK defined in Player Settings > Scripting Define Symbols
// Controls whether backend services initialize
#if LAB_TRACK
    // Full backend initialization
#endif
```

### Backend Architecture (Already Built in Template)

```
BackendLifetimeScope (VContainer)
  ├── IBackendService (interface)
  │   ├── FirebaseBackendService     [FIREBASE define]
  │   ├── WebSocketSqlBackendService [WEBSOCKET define]
  │   └── OfflineBackendService      [Always available — local fallback]
  │
  ├── Sync Handlers (per service)
  │   ├── ProgressHandler
  │   ├── CharacterHandler
  │   ├── PurchasesHandler
  │   ├── RewardsHandler
  │   ├── ProfileHandler
  │   ├── ExpHandler
  │   ├── FriendsHandler
  │   ├── MailHandler
  │   ├── PresenceHandler
  │   └── RankingHandler
  │
  └── Auth
      ├── FirebaseAuthHandler
      └── AuthManager (token management)
```

## Data Flow

```
Public Release Build:
  GameClient ──> Template Systems ──> Local Save (PlayerPrefs + Binary)

Lab Track Build:
  GameClient ──> Template Systems ──> OfflineBackendService (local)
                                   ──> FirebaseBackendService (cloud sync)
                                   ──> WebSocketSqlBackendService (persistent)
                                   ──> Fusion 2 (real-time multiplayer)
```

## Security Boundaries

- Firebase native plugins (DLLs) exist in `Assets/Plugins/` — harmless unless initialized
- Firebase config files (`google-services.json`, `GoogleService-Info.plist`) apparently NOT present yet
- All backend code is in template vendor tree — we don't remove it, we just prevent its initialization
- The `OfflineBackendService` is safe for Public Release (local-only persistence)
