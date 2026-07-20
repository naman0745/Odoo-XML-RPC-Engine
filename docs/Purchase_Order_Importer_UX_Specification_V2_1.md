# UX / Product Design Specification
## Purchase Order Importer
### Desktop Application - Python / PySide6

**Version 2.1 - 2026-07-20**

A complete interface architecture for importing Purchase Orders from Excel into Odoo ERP.
Prepared as an implementation-ready specification for frontend engineering.
Backend treated as a stable black box; this document defines the GUI layer only.

---

## Contents

- [Section 0 - Revision Summary](#section-0---revision-summary)
- [Section 1 - Design Philosophy](#1-design-philosophy)
- [Section 2 - User Journey](#2-user-journey)
- [Section 3 - Window Layout](#3-window-layout)
- [Section 4 - Information Hierarchy](#4-information-hierarchy)
- [Section 5 - Screen Wireframes](#5-screen-wireframes)
- [Section 6 - Component Specification](#6-component-specification)
- [Section 7 - Import Progress Experience](#7-import-progress-experience)
- [Section 8 - Success Experience](#8-success-experience)
- [Section 9 - Failure Experience](#9-failure-experience)
- [Section 10 - Visual Style System](#10-visual-style-system)
- [Section 11 - Accessibility](#11-accessibility)
- [Section 12 - Future Scalability](#12-future-scalability)

---

## Section 0 - Revision Summary

### V2.1 - Changes from V2 (2026-07-20)

Version 2.1 incorporates the final review changes required before frontend implementation. The design philosophy, folder-based workflow, single-window structure, information hierarchy, workflow checklist, visual language, accessibility guidance, typography, layout, and Incoming/Processed Orders workflow remain unchanged from Version 2 except where explicitly noted below.

#### What changed and why

**0.1 - Automatic workspace creation**
The application no longer blocks first launch with mandatory folder setup. On startup, it creates a default workspace under `Documents/Purchase Order Importer/` whenever the workspace does not already exist. Users can open the application and begin using it immediately.

**0.2 - Self-healing default folders**
The default workspace folders are recreated automatically whenever possible. If `Incoming Orders`, `Processed Orders`, `Logs`, or `Config` is deleted, the application recreates the missing folder on launch or scan instead of presenting a blocking error.

**0.3 - Optional custom folders**
Users may still choose custom Incoming and Processed folder locations for shared folders, network drives, or alternate local paths. Custom paths are optional and remembered between sessions. The default workspace remains available as the fallback.

**0.4 - Empty state clarified**
When no workbooks are waiting in the Incoming Orders folder, the Folder Scan View shows a calm empty state with `Open Incoming Folder` and `Refresh` actions. The empty state is informational and never asks users to configure folders before they can use the application.

**0.5 - Atomic result model**
The UI now represents only the two outcomes the backend can produce: `Purchase Order Created` and `Purchase Order Not Created`. The success and failure surfaces no longer describe unsupported intermediate result states.

**0.6 - Unsupported actions removed**
Actions that depend on backend capabilities not currently available have been removed from the active interface contract. The result screen and progress screen now expose only actions the backend can reliably support.

**0.7 - Technical details simplified**
The technical details disclosure remains available for IT staff, but the UI-level detail is limited to error code, import stage, timestamp, and an `Open Log File` action. Full diagnostic output remains in the log file.

**0.8 - Connection status model corrected**
The connection indicator reflects discrete backend checks, not continuous polling. It updates on application startup, immediately before an import, and after connection-related failures.

**0.9 - Last scan time added**
The Folder Scan View displays the timestamp of the most recent successful folder scan beside the pending order count, giving users confidence that the displayed queue is current.

#### Sections updated in V2.1

| Section | Change |
|---|---|
| 0 | Revision summary updated |
| 1.3 | Out-of-scope guidance aligned with current backend capabilities |
| 2.1 | Automatic workspace creation added; blocking setup removed |
| 2.2 | Empty state and folder recovery behavior clarified |
| 3.1 | Footer and connection indicator model updated |
| 4.1 | Last-scan timestamp added to launch hierarchy |
| 5.1 | Folder Scan wireframe includes last-scan line |
| 5.3 | Progress wireframe aligned to current backend-supported actions |
| 5.4 | Success wireframe uses a single next action |
| 5.5/5.6 | Failure wireframes simplify technical detail display |
| 6.2 | Pending Order List includes last-scan display |
| 6.7 | Result Panel aligned to atomic backend outcomes |
| 6.8 | Technical Details Disclosure scoped to error code, stage, timestamp, and log link |
| 6.10 | Dialog guidance updated |
| 8 | Success Experience aligned to atomic backend behavior |
| 9.3 | Connection category updated to checked-not-polled model |
| 12.2 | Settings describes optional custom-folder configuration |

---

## §1 — Design Philosophy

The interface exists to make a technical process feel effortless for non-technical staff — and effortlessly diagnosable for IT when something goes wrong.

### §1.1 — Core Principles

- **One task, one screen.** The application does exactly one thing: import a Purchase Order file. There is no dashboard to navigate, no sidebar of unrelated modules. The main window IS the product. This reduces cognitive load to near zero — a new hire can use it correctly on day one without training.

- **The GUI narrates, it never decides.** Because all business logic lives in the Import Controller, the interface's only job is to faithfully represent what the backend is doing and what it returned. This shapes every decision in the document: no client-side validation messaging, no "smart" pre-checks, no interpretation of data — only honest presentation of controller state.

- **Calm technology.** Business operations software is used under time pressure, often by people who are not comfortable with computers. The interface should never introduce anxiety through color, motion, or ambiguity. Status is always unambiguous; errors are never cryptic by default.

- **Progressive disclosure.** Simple summary first, technical detail available on demand. A staff member sees "Import failed — vendor 'ACME Corp' could not be matched." An IT technician can expand the same result to see the error code, the stage at which it failed, and a link to the log file. Same screen, two audiences, no mode switching.

- **Predictable, not clever.** No hidden gestures, no auto-advancing screens, no surprise dialogs. Every state transition is triggered by an explicit user action or a clearly communicated backend event. Trust is built through consistency, not delight.

- **Native desktop conventions.** This is a Windows desktop tool used daily. It should feel instantly familiar — standard title bar, standard folder dialogs, standard keyboard shortcuts — rather than reinventing platform conventions.

- **Represent only what exists.** The GUI does not design affordances for backend capabilities that do not currently exist. If a feature is absent from the backend, its button is absent from the interface.

### §1.2 — Reference Points

The visual and interaction language draws from four products, each contributing a specific lesson:

| Product | Lesson borrowed |
|---|---|
| **Windows File Explorer** | Folder-centric mental model; path display; native dialogs |
| **Visual Studio Code** | Calm, dark-accented status indicators; progressive detail in output panels |
| **Notion / Linear** | Clean card components; generous whitespace; readable data density |
| **macOS Finder / Activity Monitor** | Confidence through live status — counts, timestamps, scan feedback |

### §1.3 — What This Design Deliberately Avoids

- Dashboards, widgets, or panels that exist only to look sophisticated.
- Multi-step setup wizards before first use. The application is ready to use immediately on first launch.
- Color used decoratively — every color on screen carries meaning.
- Motion for its own sake — animation is used only to communicate state change, never as flourish.
- Affordances for backend capabilities that do not currently exist.
- Representing states the backend cannot produce (unsupported intermediate result — removed in v2.1).
- Exposing implementation detail in the primary UI; diagnostic internals belong in the log file.

---

## §2 — User Journey

The complete journey from launch to a successful import, with the underlying intent of each step.

### §2.1 — Primary Flow

1. **Launch** — On first launch, the application automatically creates the default workspace folder structure under `Documents/Purchase Order Importer/` if it does not already exist. No setup prompt, no wizard, no blocking configuration step. The app opens directly into the Folder Scan View, which displays the pending order list (or empty state) immediately.

2. **Automatic workspace** — The four required folders are created silently at startup if missing:
   ```
   Documents/
   └── Purchase Order Importer/
       ├── Incoming Orders/     ← scanned for pending workbooks
       ├── Processed Orders/    ← destination for completed imports
       ├── Logs/                ← rotating import log files
       └── Config/              ← persisted settings (custom paths etc.)
   ```
   If a folder is deleted between sessions, the application recreates it on next launch rather than presenting an error. The workspace is self-healing.

3. **Folder scan** — The application scans the Incoming Orders folder on launch and displays the results as a list of pending order cards. The scan timestamp and pending count are displayed above the list. A `Refresh` button triggers a manual re-scan at any time.

4. **Select order** — The user selects a pending order from the list. The card highlights and the primary action button becomes enabled. If exactly one workbook is present it is pre-selected automatically.

5. **Start import** ? The user clicks "Import Purchase Order." The content area transitions to the Progress state. Once started, the import runs until the backend returns a success or failure result.

6. **Progress** — The six named pipeline stages are shown as a live checklist (§7). Each transitions from pending → active → complete as the backend reports progress.

7. **Result (success)** — The Success panel shows the PO ID and row count. The imported workbook is moved automatically to Processed Orders. A quiet confirmation line ("✓ Workbook moved to Processed Orders") appears beneath the row count. The single next-step action is "Import Next Order."

8. **Result (failure)** — The Failure panel shows the plain-language error. The workbook is NOT moved — it remains in Incoming Orders for correction. The user can click "Try Again" to re-run, or "Back to Order List" to return to the queue.

### §2.2 — Secondary / Edge Paths

- **Incoming folder is empty:** The uniform empty state is shown — no pending orders message, folder path, `Open Incoming Folder` button, and `Refresh` button. This is the same state shown on first launch and on any subsequent launch with no workbooks. There is no separate "first-launch" experience.

- **Default folder deleted between sessions:** The application recreates the missing folder automatically at next launch. A brief, non-blocking notice ("Incoming Orders folder was recreated") may appear in the footer status strip. This applies only to the default workspace folders; custom locations that go missing present an error (see §9.3).

- **Custom folder configured:** Users with a custom incoming/processed location configured in Settings see their custom path scanned instead of the default. The behaviour is identical.

- **Duplicate filename in Processed folder:** The incoming file is renamed with a timestamp suffix before moving (e.g. `PO_DRInternational_2026-07-20_143205.xlsx`). A toast notification informs the user. No blocking dialog is shown.

- **Connection check fails before import:** Connection status is checked immediately before the import begins. If the connection cannot be established, the import does not start and a Failure panel is shown immediately (no progress checklist) with the connection failure category.

- **Network drops mid-import:** Treated as a Failure result returned by the backend — same Failure panel pattern with the "connection" category. No distinction is made in the UI between "failed before start" and "failed mid-pipeline."

### §2.3 — Journey Map Summary

| Step | User action | Application response |
|---|---|---|
| Launch | (none) | Workspace created if needed; folder scanned; Folder Scan View shown |
| Select order | Click on card | Card highlighted; Import button enabled |
| Start import | Click Import | Progress state shown; connection checked; pipeline begins |
| Import succeeds | (none) | Success panel; workbook moved; Import Next Order available |
| Import fails | (none) | Failure panel; workbook stays in Incoming; Try Again / Back to List |
| Retry | Click Try Again | Re-runs import on same file |
| Back to list | Click Back to Order List | Returns to Folder Scan View; failed file still visible |
| Next order | Click Import Next Order | Returns to Folder Scan View; completed file gone |

---

## §3 — Window Layout

A single-window application, fixed conceptual structure, resizable within sane bounds. No tabs, no multi-window juggling — everything the user needs is always visible.

### §3.1 — Structural Regions

#### Title Bar (native OS chrome)
Standard Windows title bar showing "Purchase Order Importer." No custom chrome — a custom title bar adds engineering cost and risk for zero UX benefit in an internal business tool. Native chrome is instantly familiar and free.

#### Header Band
A slim, fixed band beneath the title bar. Contains:
- Application name / logo mark (small, left-aligned).
- Connection status indicator (right-aligned) — a small dot + label. Shows the result of the most recent connection check, NOT a live polling feed. Checks occur: (1) at application start, (2) immediately before each import, (3) after a connection-related failure. The indicator uses three states: `● Connected`, `○ Not Connected`, `⚠ Check failed`.
- A gear icon (far right) that opens the optional Folder Configuration panel.

#### Primary Content Area
The single largest region of the window. This area is a state machine with exactly **five** mutually exclusive states:

| State | When shown |
|---|---|
| **Folder Scan state** | Launch, after import, after returning from result |
| **Ready state** | Order card selected, awaiting user action |
| **Progress state** | Import pipeline running |
| **Success state** | Pipeline completed, PO created |
| **Failure state** | Pipeline aborted, no PO created |

Each state replaces the previous in place — no navigation, no new window. This reinforces that the entire task is one continuous operation, not a wizard.

#### Footer / Status Strip
A thin strip anchored to the bottom of the window. Shows, left to right:
- App version (e.g. `v2.1.0`)
- Last import timestamp, when available (e.g. `Last import: today at 4:12 PM`)
- `Configure Folders` — opens the optional Folder Configuration panel
- `View Log File` — opens the current day's log file in the default text editor

Anything that would intimidate a non-technical user lives here — present but never foregrounded.

### §3.2 — Why This Structure

- **Single content region:** Business users under time pressure should never have to ask "where do I click next?" A morphing single region guarantees the next action is always in the same visual location.
- **Header as trust signal:** Connection status is surfaced persistently so IT can preempt a whole class of support tickets. The checked-not-polled model avoids misleading users about the indicator's freshness — if it reads "Connected" it means "connected as of last check", which is clearly different from a continuous green light.
- **Footer as escape hatch for complexity:** Raw logs, version numbers, and diagnostic links are demoted to the footer — present but never competing with the primary task.

### §3.3 — Recommended Window Sizing

| Property | Value |
|---|---|
| Default size | 760 × 560 px |
| Minimum size | 640 × 480 px |
| Maximum | Resizable; content column max-width 640 px |
| Resizing behaviour | Window resizes freely; content region centers within; pending order list gains scroll if needed |

---

## §4 — Information Hierarchy

What the eye should land on, in order, at each stage of the journey. This governs type scale, color weight, and spatial priority throughout the visual design.

### §4.1 — On Launch (Folder Scan State)

1. **The pending orders list** — vertical stack of order cards, centered in the content area. If a single workbook is pending, it is pre-selected and the eye moves immediately to the action button.
2. **Scan metadata line** — `3 pending orders · Last scanned: today at 4:58 PM` — small, above the list, confirming the list is fresh.
3. **Connection status in the header** — quietly present; it escalates (amber/red) only when the connection is unavailable.

### §4.2 — After Order Selection

1. **The selected order card** — filename is the largest, boldest text on screen at this moment; selection border makes the chosen item unambiguous.
2. **"Import Purchase Order" button** — high contrast, unmistakably the next step.
3. **"← Back to order list" link** — present but visually quiet.

### §4.3 — During Progress

1. **The currently active step** — highlighted, animated spinner.
2. **Completed steps** — calm checkmark, lower-contrast color so the eye is not drawn back.
3. **Pending steps** — muted/greyed, present for context but not competing.

### §4.4 — On Success

1. **Unambiguous success signal** — green check + "Purchase Order Created" headline, large and immediate.
2. **The PO ID** — the single most important output of the entire application; shown in a visually distinct card at maximum contrast.
3. **Row summary** — e.g. "12 of 12 rows imported successfully" — secondary confirmation.
4. **Move confirmation** — "✓ Workbook moved to Processed Orders" — quiet secondary line.
5. **"Import Next Order" button** — the one clear next action.

### §4.5 — On Failure

1. **Unambiguous failure signal** — amber warning icon + plain-language headline.
2. **The actionable detail** — e.g. "Row 7: Vendor 'ACME Corp' not found in Odoo" — largest supporting text.
3. **Row summary** — e.g. "9 of 12 rows validated · 0 rows imported" — counts without blame.
4. **Inline notice** — "ⓘ Workbook remains in Incoming Orders — correct and retry."
5. **"▸ View Technical Details" disclosure** — low-contrast, collapsed by default.
6. **"Try Again" / "Back to Order List" buttons** — clear, no dead-ends.

---

## §5 — Screen Wireframes

ASCII wireframes of every primary state at the recommended default window size of 760 × 560 px. Proportions are schematic; exact measurements are defined in §6 and §10.

### §5.1 — Folder Scan State (Orders Pending)

```
┌──────────────────────────────────────────────────────────────────┐
│  Purchase Order Importer                          ─  □  ✕        │  ← native title bar
├──────────────────────────────────────────────────────────────────┤
│  ◆ PO Importer                        ● Connected to Odoo  ⚙     │  ← header band
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  3 pending orders · Last scanned: today at 4:58 PM  [⟳ Refresh]  │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  📄  PO_DRInternational_July.xlsx          248 KB  Jul 20  │  │  ← selected
│  └────────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  📄  PO_ACME_Q3.xlsx                        91 KB  Jul 19  │  │
│  └────────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  📄  PO_SupplierX_Reorder.xlsx              37 KB  Jul 18  │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                    │
│                ┌──────────────────────────────┐                   │
│                │   Import Purchase Order       │                   │
│                └──────────────────────────────┘                   │
│                                                                    │
├──────────────────────────────────────────────────────────────────┤
│  v2.1.0   Last import: today at 4:12 PM   Configure Folders  View Log │
└──────────────────────────────────────────────────────────────────┘
```

### §5.2 — Folder Scan State (Empty)

```
┌──────────────────────────────────────────────────────────────────┐
│  Purchase Order Importer                          ─  □  ✕        │
├──────────────────────────────────────────────────────────────────┤
│  ◆ PO Importer                        ● Connected to Odoo  ⚙     │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  0 pending orders · Last scanned: today at 4:58 PM  [⟳ Refresh]  │
│                                                                    │
│                                                                    │
│                         📂                                         │
│               No pending purchase orders found.                    │
│                                                                    │
│        Add Excel workbooks to the Incoming Orders folder           │
│        to begin.                                                   │
│                                                                    │
│        D:\Documents\Purchase Order Importer\Incoming Orders        │
│                                                                    │
│         ┌────────────────────────┐  ┌─────────┐                   │
│         │  Open Incoming Folder  │  │ Refresh │                   │
│         └────────────────────────┘  └─────────┘                   │
│                                                                    │
├──────────────────────────────────────────────────────────────────┤
│  v2.1.0                             Configure Folders   View Log  │
└──────────────────────────────────────────────────────────────────┘
```

### §5.3 — Ready State — Order Selected

```
┌──────────────────────────────────────────────────────────────────┐
│  Purchase Order Importer                          ─  □  ✕        │
├──────────────────────────────────────────────────────────────────┤
│  ◆ PO Importer                        ● Connected to Odoo  ⚙     │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│   ┌────────────────────────────────────────────────────────────┐  │
│   │  📄  PO_DRInternational_July.xlsx                           │  │
│   │       248 KB · Modified 20 Jul · D:\...\Incoming Orders     │  │
│   └────────────────────────────────────────────────────────────┘  │
│                                                                    │
│                ┌──────────────────────────────┐                   │
│                │   Import Purchase Order       │                   │
│                └──────────────────────────────┘                   │
│                                                                    │
│                 ← Back to order list                              │
│                                                                    │
├──────────────────────────────────────────────────────────────────┤
│  v2.1.0                             Configure Folders   View Log  │
└──────────────────────────────────────────────────────────────────┘
```

### §5.4 — Progress State

```
┌──────────────────────────────────────────────────────────────────┐
│  Purchase Order Importer                          ─  □  ✕        │
├──────────────────────────────────────────────────────────────────┤
│  ◆ PO Importer                        ● Connected to Odoo  ⚙     │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  PO_DRInternational_July.xlsx                                      │
│                                                                    │
│  ✓  Reading workbook                                               │
│  ✓  Validating columns                                             │
│  ✓  Validating rows                                                │
│  ✓  Resolving vendor                                               │
│  ◌  Resolving products  ···                          ← active     │
│  ○  Creating purchase order                          ← pending    │
│                                                                    │
│  ════════════════════════════════░░░░░░░░░░░░  (4 of 6)           │
│                                                                    │
│                                                                    │
├──────────────────────────────────────────────────────────────────┤
│  v2.1.0                             Configure Folders   View Log  │
└──────────────────────────────────────────────────────────────────┘
```

> **Note:** The Progress state contains status information only. It does not introduce action controls that the backend cannot support.

### §5.5 — Success State

```
┌──────────────────────────────────────────────────────────────────┐
│  Purchase Order Importer                          ─  □  ✕        │
├──────────────────────────────────────────────────────────────────┤
│  ◆ PO Importer                        ● Connected to Odoo  ⚙     │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│                           ✓                                        │
│                  Purchase Order Created                            │
│                                                                    │
│                   ┌───────────────────┐                           │
│                   │      PO00847      │                           │
│                   └───────────────────┘                           │
│                                                                    │
│              12 of 12 rows imported successfully                   │
│              ✓  Workbook moved to Processed Orders                 │
│                                                                    │
│              ┌──────────────────────┐                             │
│              │   Import Next Order  │                             │
│              └──────────────────────┘                             │
│                                                                    │
├──────────────────────────────────────────────────────────────────┤
│  v2.1.0   Last import: today at 4:12 PM   Configure Folders  View Log │
└──────────────────────────────────────────────────────────────────┘
```

> **Note:** The Success state exposes one next-step action only.

### §5.6 — Failure State (Collapsed Technical Detail)

```
┌──────────────────────────────────────────────────────────────────┐
│  Purchase Order Importer                          ─  □  ✕        │
├──────────────────────────────────────────────────────────────────┤
│  ◆ PO Importer                        ● Connected to Odoo  ⚙     │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│                            ⚠                                       │
│                   Import Could Not Finish                          │
│                                                                    │
│  Row 7: Vendor "ACME Corp" could not be matched to a vendor        │
│  in Odoo. No purchase order was created.                           │
│                                                                    │
│  9 of 12 rows validated · 0 rows imported                          │
│                                                                    │
│  ⓘ Workbook remains in Incoming Orders — correct and retry.        │
│                                                                    │
│  ▸ View Technical Details                                          │
│                                                                    │
│    ┌───────────────┐  ┌──────────────────────┐                    │
│    │  Try Again    │  │  Back to Order List   │                    │
│    └───────────────┘  └──────────────────────┘                    │
│                                                                    │
├──────────────────────────────────────────────────────────────────┤
│  v2.1.0                             Configure Folders   View Log  │
└──────────────────────────────────────────────────────────────────┘
```

### §5.7 — Failure State (Expanded Technical Detail)

```
│  ▾ View Technical Details                                          │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  Error Code:    VENDOR_NOT_FOUND                             │ │
│  │  Import Stage:  Resolving vendor                             │ │
│  │  Timestamp:     2026-07-20 16:12:34                          │ │
│  │                                                              │ │
│  │  → Open full log file                                        │ │
│  └──────────────────────────────────────────────────────────────┘ │
```

The technical details panel shows **only**:
- **Error Code** — a stable, readable identifier (e.g. `VENDOR_NOT_FOUND`, `PRODUCT_AMBIGUOUS`, `ODOO_CONNECTION_ERROR`)
- **Import Stage** — the named pipeline step at which the error occurred
- **Timestamp** — date and time of the failed import
- **Link to log file** — opens the current log file in the default text editor

Implementation-specific diagnostics **belong in the log file, not in this panel.**

---

## §6 — Component Specification

Every reusable UI element, its states, and the reasoning behind its design. This section is written as a direct input to frontend implementation — each component maps to a PySide6 widget or widget composition.

### §6.1 — Buttons

All buttons: 8 px vertical / 20 px horizontal padding, 6 px corner radius, 14 px medium-weight label, 150 ms ease-out transition on hover/press.

| Variant | Background | Label | Use |
|---|---|---|---|
| Primary | Accent blue `#2563EB` | White | Main action (Import, Import Next Order, Try Again) |
| Secondary | White | Slate 700 | Supporting action (Back to Order List, Refresh) |
| Ghost/link | Transparent | Accent blue | Low-emphasis navigation (← Back to order list, Open Incoming Folder) |
| Destructive | Red `#DC2626` | White | Not used in v2.1 (no destructive actions in scope) |

Disabled state: 40% opacity, `not-allowed` cursor. Button label never changes to a loading spinner — the button becomes disabled and the progress state takes over the content area.

### §6.2 — Pending Order List

**Purpose:** Display the contents of the Incoming Orders folder as a scannable, selectable list.

**States:**

| State | Display |
|---|---|
| Pending orders present | Scrollable list of Order Cards; count + last-scan timestamp above |
| Empty (folder empty) | Empty state illustration + message + Open Incoming Folder + Refresh |
| Refreshing | Spinner in count badge + "Scanning…" text; list updates in place on completion |

**Scan metadata line** (appears above the list in all non-empty states):
```
3 pending orders · Last scanned: today at 4:58 PM   [⟳ Refresh]
```
- Count is bold; timestamp is muted; Refresh is a Ghost button.
- On first launch with no prior scan: `Scanning…` until the first scan completes, then switches to the count + timestamp format.

**Layout:** Single column, max content width 640 px, vertically scrollable if the list overflows the content area.

### §6.3 — Order Card

A single-row card within the Pending Order List.

**Contents:** File-type icon (left, 24 px) · Filename (bold, 14 px, truncated with ellipsis if needed; full name shown in a tooltip on hover) · Metadata line (size · modified date · folder path — 12 px, muted Slate 500).

**States:**

| State | Visual |
|---|---|
| Default | White background, 1 px border-grey border, 8 px corner radius, 16 px padding, 1 px drop shadow |
| Hover | Border: Slate 600 |
| Selected | Border: 2 px accent blue `#2563EB`; background: `#EBF2FF` (~5% accent tint) |

**Interaction:** The entire card is the click target. No separate checkbox or remove icon — workbooks are managed through the file system, not the GUI. The selected card is carried into the Ready state as the focal element.

### §6.4 — Status Badges

Small pill-shaped labels that communicate a single discrete state at a glance. Used in the header connection indicator and potentially in future features.

| Badge | Color | Text |
|---|---|---|
| Connected | Green `#16A34A` dot + label | `Connected to Odoo` |
| Not Connected | Amber `#D97706` dot + label | `Not Connected` |
| Check failed | Red `#DC2626` dot + label | `Connection check failed` |

Badge reflects the result of the most recent of the three defined connection checks. It is not a live indicator.

### §6.5 — Workflow Checklist (Progress)

A vertical list of the six fixed backend stages, each row:

```
[icon]  [label]                             [trailing detail — optional]
  ✓     Reading workbook
  ✓     Validating columns
  ✓     Validating rows
  ✓     Resolving vendor
  ◌     Resolving products  ···             ← active: spinner + pulse
  ○     Creating purchase order             ← pending: muted
```

**Icon set:**
- `○` — pending (Slate 400)
- `◌` + spinner animation — active (Accent blue)
- `✓` — complete (Green)
- `✗` — failed (Red/Amber — marks the step where the error occurred)

**Design rationale:** Named steps are used rather than a percentage bar as the primary element because: (a) business users trust concrete named progress over abstract numbers, (b) the failing step is immediately identified by name, reducing the diagnostic burden on both staff and IT. "Resolving vendor" is concrete and reassuring. A spinner is not.

**No extra action control is rendered in this state.** The progress surface only represents backend-reported status.

### §6.6 — Progress Bar (supplementary)

A slim (4 px) linear bar beneath the checklist, filled in accent blue, showing step completion (n of 6 steps). Supplementary to the checklist — it communicates overall progress at a glance but is not the primary element.

### §6.7 — Result Panel

Shared structural component for both Success and Failure. Differs only in color, icon, and copy.

```
[status icon, centered, 48 px]
[headline, centered, 20 px bold]
[key data block — PO ID card (success) or primary error line (failure)]
[summary line — row counts, 13 px muted]
[secondary note — move confirmation (success) or "remains in Incoming" (failure)]
[optional: expandable technical detail — failure only]
[action button row — right-aligned or centered]
```

**Success variant:**
- Icon: green check
- Headline: "Purchase Order Created"
- Key data block: PO ID in a distinct card (14 px monospace, clipcopy icon on hover)
- Summary: "12 of 12 rows imported successfully"
- Secondary: "✓ Workbook moved to Processed Orders" (green, 13 px)
- Actions: `Import Next Order` (Primary button)

**Failure variant:**
- Icon: amber warning
- Headline: "Import Could Not Finish"
- Key data block: primary error line (plain-language, 14 px)
- Summary: "9 of 12 rows validated · 0 rows imported" (muted)
- Secondary: "ⓘ Workbook remains in Incoming Orders — correct and retry." (Slate 500, 13 px)
- Actions: `Try Again` (Primary) + `Back to Order List` (Secondary)

**No additional result variant is rendered.** The backend is atomic. A PO either exists or it does not.

### §6.8 — Technical Details Disclosure

A collapsed-by-default expander (`▸` → `▾` chevron + "View Technical Details"), 13 px muted-navy text, no border, no box — visually quiet.

When expanded, shows a bordered box containing only:
1. **Error Code** — a stable, human-readable identifier. Must be defined in the backend error taxonomy. E.g.: `VENDOR_NOT_FOUND`, `PRODUCT_AMBIGUOUS`, `HEADER_MISSING`, `ODOO_CONNECTION_ERROR`.
2. **Import Stage** — the pipeline step name exactly as shown in the checklist.
3. **Timestamp** — ISO-format date and time of the failed import.
4. **→ Open full log file** — ghost link that opens the log file in the default system text editor.

**What is explicitly excluded from this panel:**
- Implementation-specific module names, filenames, or source positions
- Low-level backend fault strings or diagnostic dumps
- Internal exception class names
- Odoo model names or field identifiers

These details belong in the log file. The disclosure panel is for triage, not debugging.

A `📋 Copy` icon button appears in the top-right of the disclosure box to copy the four fields as formatted text to the clipboard for paste into an IT support ticket.

### §6.9 — Notifications / Toasts

Used sparingly — only for background / non-blocking events that do not require user acknowledgement:
- "Workbook renamed to `PO_ACME_2026-07-20_143205.xlsx` (duplicate name in Processed folder)"
- "Incoming Orders folder was recreated (it had been deleted)"

Toast: bottom-right corner, 320 px wide, 4 second auto-dismiss, Slate 800 background, white text, 8 px corner radius. Dismissable by click.

### §6.10 — Dialogs (Modal)

No modal dialogs are used in v2.1. If a future feature requires a modal, it should follow the same design system (8 px radius, Slate 800 overlay at 40% opacity, same button specification as ?6.1).

### §6.11 — Tooltips

11 px, dark background, appear after 500 ms hover delay. Used for:
- Full filename on truncated order card labels
- Folder path details in the scan metadata line
- Timestamp detail (e.g. "Checked on 2026-07-20 at 16:58:02") on hover over the connection status badge

### §6.12 — Empty States

Two empty states exist in v2.1:

**1. Folder empty (primary — shown on first launch and any time Incoming Orders contains no workbooks):**
- Folder icon (40 px, Slate 400)
- "No pending purchase orders found." (16 px, Slate 700)
- "Add Excel workbooks to the Incoming Orders folder to begin." (14 px, Slate 500)
- Folder path label (12 px, monospace, Slate 400)
- `Open Incoming Folder` (Secondary button) + `Refresh` (Ghost button)

Copy is instructional, never apologetic. There is no "first-launch" variant — a first launch with no workbooks shows exactly this state. No configuration prompt appears.

**2. Custom folder missing (shown when a user-configured custom path no longer exists):**
- Warning icon (40 px, Amber)
- "Configured folder not found." (16 px, Slate 700)
- Path that could not be found (12 px, monospace, Slate 400)
- `Use Default Folder` (Primary) + `Configure Folders` (Secondary)

The default workspace is never "missing" — it is recreated automatically. Only custom paths can trigger this error.

### §6.13 — Loading / Busy States

| Context | Treatment |
|---|---|
| Folder scan on launch | "Scanning…" in the scan metadata line; list area blank until complete |
| Manual refresh | Spinner in count badge; existing cards remain visible |
| Import pipeline | Progress state takes full control of the content area |
| Connection check (at start) | Connection badge briefly shows `⟳ Checking…` then resolves |

No full-screen loading overlays are used. The content area is never replaced with a blank spinner.

### §6.14 — Folder Configuration Panel

An optional panel accessible from the gear icon in the header band and the `Configure Folders` link in the footer. Not a blocking first-launch step.

**Contents:**
- **Incoming Orders Folder** — current path (editable) + `Browse…` button + `Reset to Default` link
- **Processed Orders Folder** — current path (editable) + `Browse…` button + `Reset to Default` link
- Validation: both paths must be valid, accessible directories before Save is enabled
- `Save` (Primary) + `Cancel` (Secondary)

**Behaviour:**
- Settings are persisted between sessions in `Documents/Purchase Order Importer/Config/settings.json`
- Changing the Incoming Orders path triggers an immediate re-scan
- If neither path has been customised, the panel shows the default paths (greyed out) and makes clear that defaults are already in use

---

## §7 — Import Progress Experience

### §7.1 — The Decision: Checklist, Not Spinner Alone

A bare spinner ("Importing…") is rejected outright. It tells the user nothing about what is happening, how long it will take, or where a failure occurred. Under time pressure, silence is anxiety.

A pure percentage progress bar is also rejected as the primary element. The import pipeline has a fixed, small number of discrete stages — percentages imply a granularity that does not exist.

### §7.2 — The Chosen Pattern: Named Checklist + Supplementary Bar

The primary progress experience is a vertical checklist mirroring the six backend stages exactly as they are defined — no labels invented by the GUI:

1. Reading workbook
2. Validating columns
3. Validating rows
4. Resolving vendor
5. Resolving products
6. Creating purchase order

Each step transitions `pending → active → complete` as the backend reports progress. A thin supplementary bar below the checklist shows overall step completion (n of 6). The filename being imported is shown above the checklist throughout.

### §7.3 — Why This Builds Trust

- **Specificity over abstraction:** "Resolving vendor" is concrete and reassuring. If the user knows that "ACME Corp" is the vendor on this PO, they understand exactly what is happening.
- **Failure locality:** If the import fails, the checklist visually freezes with the failing step marked `✗`. The user can see at a glance where the process stopped — before even reading the error message.
- **No false precision:** Steps complete discretely; there is no attempt to interpolate progress within a step.

### §7.4 — Timing and Motion

| Transition | Duration | Easing |
|---|---|---|
| Step pending → active | 150 ms | `ease-out` |
| Step active → complete | 200 ms | `ease-in-out` |
| Checklist → Result panel | 300 ms | Fade cross-dissolve |
| Result panel entrance | 250 ms | Slide up 8 px + fade in |

All transitions respect the OS "Reduce Motion" setting (§11.6).

### §7.5 — What Happens If a Step Takes a Long Time

If a single stage (e.g. resolving many products against Odoo) runs long, the active step's spinner continues without modification. After approximately 15 seconds on the same step, small trailing dots (`···`) appear beside the label — a subtle "still working" signal without a timer or percentage, which would introduce false precision.

---

## §8 — Success Experience

### §8.1 — Design Intent

Success should feel like **closure, not celebration.** This is a back-office tool used dozens of times a day. A success state that demands attention or plays a sound would become irritating within a week. The goal is: unambiguous confirmation, fast access to the PO ID, and a clear path to the next task.

### §8.2 — Information Shown, in Priority Order

1. **Status confirmation** — green check icon + "Purchase Order Created" headline. Unambiguous, glanceable in under a second.
2. **The PO ID/reference** — the single most important output of the entire application. Shown in a visually distinct card at maximum contrast. A clip-copy icon appears on hover.
3. **Row summary** — "12 of 12 rows imported successfully." Smaller, muted text. Confirms completeness without demanding attention.
4. **Move confirmation** — "✓ Workbook moved to Processed Orders." Quiet but explicit — the user knows the file is archived and will not reappear in the pending list.
5. **Next action** — `Import Next Order` (Primary button). This returns to the Folder Scan View with a refreshed list; the completed workbook is no longer shown, providing implicit confirmation of the move.

### 8.3 - Atomic Success Model

The backend either creates a purchase order or it does not. When the Success Experience is shown, all rows were imported and a PO exists in Odoo. If any error occurs, the result is always Failure. The UI must not introduce any additional completion category beyond the two backend outcomes.

### §8.4 — After Success

The window does not auto-reset and does not auto-close. The result stays visible until the user acts. When "Import Next Order" is clicked, the content area transitions to the Folder Scan View; the completed workbook no longer appears there, confirming the move.

---

## §9 — Failure Experience

### §9.1 — Design Intent

Failure is the moment this application is most likely to generate a support ticket or a frustrated phone call. The failure experience must simultaneously serve two audiences: a non-technical staff member who needs a plain-language explanation they can act on, and an IT technician who needs a quickly accessible trail of diagnostic information.

### §9.2 — The Two-Layer Model

Every failure is presented in two layers, and the interface never merges them:

- **Layer 1 — Plain language (always visible):** A single sentence written for someone with no technical knowledge. It names what went wrong in business terms, not system terms. Example: `Vendor "ACME Corp" could not be matched to a vendor in Odoo.`

- **Layer 2 ? Technical detail (collapsed by default):** Error code, import stage, timestamp, and a link to the log file. This is the IT-facing surface. It is always available but never foregrounded. Implementation internals belong in the log file, not in this layer.

### §9.3 — Failure Severity Categories

| Category | Icon | Plain-language pattern | Example |
|---|---|---|---|
| Data validation | ⚠ amber | "Row N could not be processed — [reason]." | "Row 7: Vendor 'ACME Corp' not found in Odoo." |
| Ambiguous match | ⚠ amber | "Multiple matches found for [item] — import stopped." | "Multiple vendors match 'ACME Corp' — please clarify." |
| File / header | ⚠ amber | "The workbook is missing a required column — [column name]." | "Required column 'Vendor Code' not found." |
| Connection | 🔴 red | "The application could not connect to Odoo." | Additional note: the connection status badge updates to reflect the check failure. |

**Connection failures:** The connection status badge in the header updates immediately to reflect the failure result (the check was triggered immediately before this import). The badge does not continue to "Connected" — it now correctly reflects the most recent check result.

### §9.4 — Multi-Row Failures

If more than one row failed validation, the plain-language layer summarises rather than listing everything:

> "3 rows could not be processed: rows 7, 12, and 14. Check the Technical Details or log file for the full list."

The log file always contains the complete per-row detail.

### §9.5 — What the User Can Do From Here

- **Try Again** — Re-runs the import on the same file without any re-selection. Available when the error is likely correctable (data issues) or transient (connection).
- **Back to Order List** — Returns to the Folder Scan View. The failed workbook remains in Incoming Orders and continues to appear in the pending list.
- **View Technical Details** — Expands the disclosure panel (§6.8).
- **View Log File** — Available in the footer at all times; opens the log directly.

### §9.6 — Tone of Copy

Failure copy never uses blame language ("You entered an invalid vendor") — it is always framed around the system's limitation ("could not be matched") or an actionable discrepancy ("not found in Odoo"). The goal is: inform, then point toward resolution.

---

## §10 — Visual Style System

### §10.1 — Color Palette

Color is used exclusively to carry meaning (status, hierarchy) — never for decoration. The palette is deliberately minimal.

| Token | Hex | Role |
|---|---|---|
| `accent-blue` | `#2563EB` | Primary action, selection state, active step, focus rings |
| `success-green` | `#16A34A` | Success state, move confirmation, completed step icons |
| `warning-amber` | `#D97706` | Failure state, warning badge, ambiguous-match category |
| `error-red` | `#DC2626` | Connection failure, critical errors |
| `navy` | `#1E293B` | Primary text, headings |
| `slate-700` | `#334155` | Secondary text |
| `slate-500` | `#64748B` | Muted / supporting text, metadata lines |
| `slate-400` | `#94A3B8` | Placeholder text, disabled icons |
| `border-grey` | `#E2E8F0` | Card borders, section dividers |
| `background` | `#F8FAFC` | Window background |
| `surface` | `#FFFFFF` | Cards, panels |

No gradient, no secondary accent hue, no decorative illustration color. This restraint is what separates calm business software from consumer applications.

### §10.2 — Typography

All type: Inter (Google Fonts). Fallback: system-ui, sans-serif.

| Role | Size | Weight | Color |
|---|---|---|---|
| Window title (header band) | 15 px | 600 | Navy |
| Section heading | 20 px | 700 | Navy |
| Primary label / filename | 14 px | 600 | Navy |
| Body / step label | 14 px | 400 | Slate 700 |
| Metadata / secondary | 13 px | 400 | Slate 500 |
| Caption / badge | 12 px | 500 | Contextual |
| PO ID (monospace) | 14 px | 600 | Navy |

### §10.3 — Spacing System

8 px base unit throughout — every margin, padding, and gap is a multiple of 8 (8 / 16 / 24 / 32 / 40 / 48 px). This produces a visually consistent rhythm without per-element decisions.

### §10.4 — Corner Radius

- 6 px on all interactive elements (buttons, inputs, badges)
- 8 px on cards and containers
- 4 px on small badges and tags

Never fully rounded (pill) on content containers — reserved for badges only.

### §10.5 — Elevation & Shadows

One shadow level only: `0 1px 3px rgba(0,0,0,0.08)` — barely perceptible, reinforces card containment without visual noise. Used on: Order Cards, Result Panels, folder configuration panel. Not used on the header band or footer (they use border lines instead).

### §10.6 — Iconography

A single consistent icon set throughout: **Phosphor Icons** (recommended) or **Lucide** — both open-source, consistent stroke weight, available as SVG. All icons used as 20 × 20 px or 24 × 24 px SVG, never raster PNG.

### §10.7 — Layout Grid

Single-column content, centered within the window, max content width ~640 px. Content does not break into a multi-column layout at any window width — horizontal resizing simply adds equal whitespace to both margins.

---

## §11 — Accessibility

This is internal business software with a mandatory-use population — accessibility here is not a nice-to-have but a baseline obligation. A staff member with motor, visual, or cognitive differences must be able to use this tool without accommodation.

### §11.1 — Keyboard Navigation

- Full tab-order support through every interactive element in logical reading order (order list → selected card → Import button → footer links → header gear icon).
- `Enter`/`Space` activates the focused button or selects the focused order card.
- `Escape` collapses the technical details disclosure.
- `↑` / `↓` arrow keys navigate between order cards when the list is focused.
- The technical details expander is fully keyboard-operable (`Enter` toggles expand/collapse).
- **`Ctrl+R`** — triggers a manual folder re-scan from the Folder Scan View (replaces the `Ctrl+O` file-browse shortcut from V1, which no longer applies).

### §11.2 — Focus Indicators

Every focusable element shows a clearly visible focus ring: 2 px solid `accent-blue`, offset 2 px from the element boundary. This ring is never suppressed in mouse-interaction contexts — it is always rendered.

### §11.3 — Color Contrast

- All body text on background: ≥ 7:1 (AAA)
- All interactive element labels on their backgrounds: ≥ 4.5:1 (AA)
- Status badge text on badge backgrounds: ≥ 4.5:1
- Muted text (Slate 500 on white): 4.6:1 — just above AA threshold; not used for actionable elements

### §11.4 — Screen Reader Support

- All status icons (checklist step icons, result icon, connection badge dot) have accessible labels (e.g. `aria-label="Step complete"`, `aria-label="Step failed"`).
- The progress checklist uses `aria-live="polite"` for step transitions so a screen reader announces each completion without interrupting.
- The result panel headline uses `aria-live="assertive"` — it is the most important state change in the application and warrants immediate announcement.
- The technical details disclosure uses `aria-expanded` and `aria-controls` attributes.
- The order count + last-scan line uses `aria-label` combining both pieces of information.

### §11.5 — High-DPI & Screen Scaling

- All icons and graphics as SVG — crisp at any DPI.
- All spacing and type sizes in DPI-independent logical units (Qt's device-independent pixels).
- Layout tested to remain legible and non-overlapping at minimum window size (640 × 480) at 150% scaling.

### §11.6 — Motion Sensitivity

All transitions respect the OS-level "Reduce Motion" setting where PySide6/Qt exposes it. If reduced motion is active: transitions become instant cuts rather than fades/slides; the checklist step spinner is replaced by a static active indicator.

---

## §12 — Future Scalability

The v2.1 layout is deliberately minimal, but every structural decision below reserves space and precedent for the features most likely to be added subsequently. None of these are in scope; they are captured here so that layout decisions made today do not foreclose them.

### §12.1 — Import History

The footer already contains a `View Log File` link. A future "Import History" entry point can be added here as a second link, pointing to a searchable history panel. The single content region state machine can add a "History" state without structural changes.

### §12.2 — Settings (Custom Folder Configuration — In Scope for v2.1)

The gear icon in the header band opens the Folder Configuration panel (§6.14). This is the natural home for all future settings additions. The header icon cluster is designed to hold 2–4 icons without rebalancing the layout. Future settings candidates:
- Odoo connection parameters (server URL, database, credentials)
- Notification preferences
- Log retention policy

Custom folder paths are persisted in `Documents/Purchase Order Importer/Config/settings.json`. The default workspace is always available as a fallback if custom paths are deleted or become inaccessible.

### §12.3 — Saved Connections / Multiple Odoo Servers

The connection status badge in the header is already a distinct, tappable region. Evolving it from a status indicator to a server-selector (for multi-server environments) requires no structural layout change.

### §12.4 — User Profiles

If multi-user identity becomes relevant (e.g. showing who ran which import in history), a small avatar or initials badge can be placed in the header band immediately to the left of the connection badge without rebalancing the layout.

### 12.5 - Why the Architecture Supports This

- **Single content region as a state machine:** New states (History List, Settings Panel) can be added to the same region without introducing navigation chrome.
- **Header band as an extensible icon rail:** Already holds one icon (gear); built from the start to hold up to four.
- **Footer as the technical/secondary layer:** Establishes precedent that low-priority, IT-oriented, or power-user affordances live here.
- **Component-based specification:** Every component in Section 6 (cards, badges, buttons, disclosures) is generic and reusable. A History feature reuses Order Cards with a processed-status badge; it does not require new components.

---

*End of Specification — Version 2.1*

*This document defines UI/UX architecture only. No implementation code, business logic, or backend behaviour is specified here beyond what is necessary to define the interface contract.*
