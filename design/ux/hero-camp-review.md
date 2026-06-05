## UX Review: Hero Camp
**Date**: 2026-06-01
**Reviewer**: ux-review skill
**Document**: `design/ux/hero-camp.md`
**Platform Target**: PC (Keyboard/Mouse), Gamepad, Mobile (Touch)
**Accessibility Tier**: WCAG-AA (explicitly stated, no formal requirements doc exists yet)

### Completeness: 13/14 sections present
- [x] Document header — Status, Author present. Platform Target not in header header (covered in section body).
- [x] Purpose & Player Need — Clear player-perspective: "spend currency earned from runs to make the next run easier"
- [x] Player Context on Arrival — Four distinct arrival contexts with emotional states. Excellent.
- [x] Navigation Position — ASCII hierarchy diagram with return paths.
- [x] Entry & Exit Points — Full table with context carried across transitions.
- [x] Layout Specification — Zones defined, 16-component inventory table.
- [ ] States & Variants — Error state **MISSING**. Loading state **MISSING**.
- [x] Interaction Map — 11 interactions across all three platforms.
- [x] Data Requirements — 12 elements, all with system owners. No "UI" ownership.
- [x] Events Fired — 6 events. Missing: purchase failure / save failure events.
- [x] Transitions & Animations — 9 transitions with timing and notes.
- [x] Accessibility Requirements — Keyboard, gamepad, contrast ratios, color independence, motion sensitivity.
- [x] Localization Considerations — Risk/mitigation table per element. 40% expansion buffer.
- [x] Acceptance Criteria — 18 criteria (well above 5 minimum). Self-contained.

### Quality Issues: 5 found

1. **Missing Error State** [BLOCKING]
   - What's wrong: No error state is documented. The spec assumes all purchases succeed, all saves complete, all data loads. In reality: network failures, disk full, corrupted data, concurrent sync conflicts.
   - Where: States & Variants section.
   - Fix: Add error state(s): purchase failure (insufficient funds race, save failure), data load failure, sync conflict. Specify error toast content, retry behavior, fallback state.

2. **Missing Loading State** [BLOCKING]
   - What's wrong: No loading state while save data is being loaded from disk. The scene has a 0.5s fade-in but no indication that data is still being fetched.
   - Where: States & Variants section.
   - Fix: Add a "Loading Profile Data" state before Default (camp exploration). Show a brief spinner or pulsing campfire while IPersistStateService completes initial load. Document timeout behavior.

3. **Auto-dismiss toast not formalized as a state** [ADVISORY]
   - What's wrong: "New lore discovered" toast has timing in the transitions table (0.3s in, 2.5s hold, 0.3s out) but isn't listed as a state variant with its own behavior rules.
   - Where: States & Variants (missing entry), Transitions (timing present but no null context).

4. **Null/unavailable data not specified** [ADVISORY]
   - What's wrong: Data Requirements table doesn't specify fallback display when source data is unavailable (e.g., IPersistStateService returns null, ScriptableObject registry missing an entry).
   - Where: Data Requirements section.
   - Fix: Add a "Fallback / Null Display" column or note per row.

5. **No resolution/scaling criterion** [ADVISORY]
   - What's wrong: AC list doesn't include a resolution test (e.g., "UI renders correctly at 1920x1080, 1280x720, and 3840x2160"). The spec assumes a single layout.
   - Where: Acceptance Criteria.
   - Fix: Add criterion: "Camp Menu overlay renders correctly at minimum 1280x720 and maximum 3840x2160."

### GDD Alignment: ALIGNED
- `save-profile-persistence.md`: States "no direct UI; Camp Menu reads profile currency values" — addressed via currency bar.
- `scene-manager.md`: Scene-to-screen mapping (`_TinyRift/Scenes/HeroCamp`) — aligned.
- `camp-menu-ui.md`: No UI Requirements section, but GDD content matches overlay design.
- `hero-camp-progression.md`: No UI Requirements section; upgrade tree/costs aligned with spec.
- `currency-system.md`: "pure data-tracking layer with no UI of its own" — respected by the spec.
- No GDD UI requirement is missing from this spec. No unowned game state is displayed.

### Accessibility: COMPLIANT (with known gap)
- Target tier: WCAG-AA (per spec text; no `accessibility-requirements.md` exists yet)
- Keyboard navigation: fully specified (Tab cycle, Enter/EScape, WASD movement, no traps)
- Gamepad: fully specified (D-pad layout, A/B mapping, Start for pause)
- Contrast ratios: specified for all text layers (4.5:1 minimum, 7:1 for reader text)
- Color independence: affordability via button state, zone via brightness+border, badge via shape+position — good
- Motion sensitivity: <0.5s animations, no parallax, reduced-motion query honored — good
- **Gap**: No `accessibility-requirements.md` exists yet to formalize the baseline tier. The spec's self-declared WCAG-AA is reasonable.

### Pattern Library: INCONSISTENCIES FOUND
- `design/ux/interaction-patterns.md` does not exist yet — expected at this stage.
- All components listed as "New" pattern in the inventory — expected since no pattern library exists.
- Recommendation: After this review, create the pattern library as a consolidation step. The Camp Menu overlay (tab bar + scrollable list) and interact prompts will be foundational patterns.

### Verdict: APPROVED (after revision)

**Previously blocking issues — resolved in revision:**
- Error state added: 4 error variants (Purchase Error, Save Error, Data Load Error, Sync Conflict) with triggers, visual feedback, and timeout/retry behavior
- Loading state added: Loading Profile Data state with fallback display ("—"), timeout (5s), and transition to Data Load Error

**Previously advisory issues — resolved in revision:**
- Auto-dismiss toast timing formalized in transition table
- Null/unavailable data fallbacks added to all Data Requirements rows
- Resolution/scaling criterion added (1280×720, 1920×1080, 3840×2160)
- Purchase failure and data load failure ACs added (21 total criteria)
- Events Fired expanded: PurchaseFailed, ErrorEvent(SaveError), ErrorEvent(DataLoadError), DataChangedEvent
- Transition animations added: purchase error toast, save error indicator, data load error overlay, loading indicator

This spec is ready for handoff to implementation pipeline. Re-run `/ux-review` after any future revisions.
