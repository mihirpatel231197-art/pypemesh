# UX Principles

**Version:** 0.1
**Status:** Non-negotiable design law

> The user said: *"capacity of all possible software but everything must be easy to use."*
> That's the hardest UX problem in engineering software. This doc is how we solve it.

## The core tension

- Caesar II is powerful because it's dense. It's dense because it's powerful.
- Fisher-Price UIs hide power. Power UIs scare new users.
- **Most tools pick a side. We don't get to.**

## The resolution: progressive disclosure with full power always accessible

Every screen has three layers:

1. **Default layer** — what a new engineer sees. Shows only what's needed for 80% of workflows.
2. **Advanced layer** — revealed by keyboard shortcut, right-click, or "Advanced" toggle. Full Caesar-level control.
3. **Expert layer** — spreadsheet mode, raw model JSON, solver flags. Always one keystroke away.

No layer *hides* capability. All layers *prioritize* capability.

---

## The 12 laws

### 1. **Time-to-first-model: 10 minutes**

A new engineer with Caesar II background builds a 10-node model, runs analysis,
reads results — in under 10 minutes, first session. If not, we've failed.

**Measurement:** usability test with 5 engineers, first session, recorded.

### 2. **Infinite undo. No exceptions.**

Every action is undoable. Including: solver run, delete node, batch import,
material change, code switch. Crash recovery restores undo stack.

**Why:** Caesar II's biggest complaint is losing undo on exit. This is trivially
solvable with immer/immutable patches. We solve it.

### 3. **No modal dialogs for normal work**

Adding a pipe segment? Inline editor in the 3D view, not a popup.
Editing properties? Side panel, not a dialog. Changing material? Dropdown, not a wizard.

Modals are reserved for *destructive* confirmation and *large* flows (import wizard, report customization).

### 4. **Keyboard-first**

Every action has a shortcut. Shortcut reference accessible via `?` key always.
Command palette (Cmd/Ctrl-K) lists every command, searchable.

**Reference:** AutoCAD + VS Code models. Not Microsoft Office.

### 5. **Two input modes, always synchronized**

- **Graphical**: point, click, drag in 3D.
- **Spreadsheet**: tabular editor, Caesar-style rows.

Edit in one → the other updates instantly. Toggle with `Tab`. Power users stay
in spreadsheet. Beginners stay graphical. Nobody is forced either way.

### 6. **Progressive disclosure of physics**

Default UI shows: node ID, type, properties, stress ratio. Done.

Advanced-mode reveals: SIF values, flexibility factors, element stiffness
contribution, mass matrix entry, modal participation factor. Everything.

The physics is never hidden, just not *shown by default*.

### 7. **Instant feedback, always**

- Click a node → properties update <50ms
- Drag to route a pipe → preview follows cursor, no lag
- Change material → stress re-checked (if last solve exists) <200ms
- Type in spreadsheet cell → validation inline, no delayed error modal

If something takes >200ms, show a spinner. >2s, show progress. >10s, show cancel.

### 8. **Errors teach, not punish**

Bad: `ERROR: invalid SIF`.
Good: `Elbow E30 has SIF=1.82 but 3D radius=0.8D, below B31J minimum (1.0D). Possible causes: 1) wrong radius, 2) custom SIF needed. Click for help.`

Every error references: the node, the rule, the cause, the fix, a help link.

### 9. **Defaults that work**

New project → B31.3 preselected (most common). Material A106-B preselected.
Temperature 20°C. Pressure 0. Units mm/N/bar/C.

Changing default = one click. Requiring user to set defaults = failure.

### 10. **Never lose work**

- Autosave every 30s
- Local-first storage (IndexedDB) even for cloud projects
- Offline mode works for everything except cloud collab
- Tab close warning if unsaved (but autosave runs anyway)
- Browser crash? Reopen → right back where you were.

### 11. **Show your work**

Every result traceable to inputs. Click a stress value → shows:
- Which code equation produced it
- Which loads contributed (percentage breakdown)
- Which SIF applied
- Which allowable compared against
- "Open in spreadsheet" drill-down

Commercial tools black-box this. We don't.

### 12. **Ruthless performance**

- 60fps 3D viewport on 2000 nodes
- Keystroke → visible update <50ms
- First paint <2s
- Solver on 500-node static model <5s
- Report generation <3s

A slow UI punishes every keystroke. Performance is a feature — measured, regressed on, CI-gated.

---

## Anti-patterns (things we will never do)

- ❌ "Welcome to the new version" modal
- ❌ Tutorials that block the UI
- ❌ "Are you sure?" for reversible actions
- ❌ Magic auto-fix that changes user data silently
- ❌ Features behind 3+ clicks with no shortcut
- ❌ Input fields without units visible
- ❌ Tooltip-only help (no deep link)
- ❌ Red numbers without context (*why* is 94% bad?)
- ❌ Progress bars that lie
- ❌ Telemetry we don't disclose

---

## Visual design notes (for phase B)

- Typography: system stack (SF Pro / Segoe UI / Inter) — legible at small sizes
- Density: closer to AutoCAD/VS Code than Figma/Notion. Engineers process dense info.
- Color: reserve red for failed code check. Orange for warning. Green for pass. Blue for info. Don't use color as the only channel (accessibility).
- Units: always displayed next to values. Never implicit.
- Precision: 4 sig figs in UI by default, user-configurable to 2-6.

## Onboarding (phase B.1)

- No forced tutorial.
- Template projects in "New" dialog: "Simple thermal loop", "Pump discharge", "Relief header".
- Inline hints only for first-time actions, dismissible forever.
- Help sidebar with searchable docs, always one shortcut away.

## How we enforce this

- Every PR that touches UI is reviewed against this doc.
- Every quarter: 5-user usability test recorded.
- Every release: time-to-first-model measured and tracked.
- This doc is versioned. Changes to principles require explicit decision.
