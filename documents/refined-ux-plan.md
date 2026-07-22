# Refined UX Improvement Plan: Purchase Order Importer (Workflow Accelerator)

## 🎯 Core Philosophy
This application is a **workflow accelerator**, not a full-scale ERP replacement. The goal is to maximize the speed of moving data from Excel to Odoo while minimizing "cognitive noise" and manual clicks. We prioritize **friction removal** over **feature richness**.

---

## 🚀 Prioritized Improvements

### ⚡ High Priority: The "Speed" Layer (Immediate Impact)
*These changes transform the app from a single-file utility into a high-throughput processor.*

1. **Batch Import Capability**
   - Add "Import All" and multi-select functionality in the Scan view.
   - **Goal:** Eliminate the repetitive 5-state loop for multiple files.
2. **Auto-Folder Monitoring (Watchdog)**
   - Replace the manual "Refresh" button with a real-time file system watcher.
   - **Goal:** UI updates instantly when files are dropped into the folder.
3. **"Next Pending File" Flow**
   - Add a "Next File" button in the Success view that jumps directly to the `ReadyView` of the next file in queue.
   - **Goal:** Create a "conveyor belt" experience for high-volume imports.
4. **File Preview (Ready State)**
   - Show row count and the primary Vendor name before the user confirms import.
   - **Goal:** Instant confirmation that the correct file is being processed.
5. **Drag and Drop Support**
   - Allow users to drag `.xlsx` files directly onto the app window to move them to the Incoming folder.
   - **Goal:** Remove the need to open Windows Explorer.
6. **Excel Template Download**
   - A one-click button to download the perfectly formatted template.
   - **Goal:** Reduce "format error" failures at the source.

### 🛠️ Medium Priority: The "Friction" Layer (Quality of Life)
*These features reduce the pain of errors and increase power-user efficiency.*

1. **Practical Error Recovery**
   - Add an "Open in Excel" button on the Failure view for the specific file that failed.
   - **Goal:** Immediate transition from "Error Detected" to "Error Fixing."
2. **Inline Validation Status**
   - Add small status icons (✅/⚠️) in the Scan view based on a quick background check of the file format.
   - **Goal:** Let users know which files are "safe" before they even select them.
3. **Fast-Track Import**
   - If a file is pre-validated as "Perfect," allow a "Quick Import" that skips the Ready view and goes straight to Progress.
   - **Goal:** Zero wasted clicks for clean data.
4. **Keyboard Shortcuts**
   - `Ctrl+R` (Refresh/Rescan), `Enter` (Confirm Import), `Esc` (Cancel/Back).
   - **Goal:** Enable "no-mouse" operation for experienced users.

---

## 🗑️ Excluded Features (Out of Scope)
*The following were identified in the initial plan but are rejected as "Enterprise Noise" that doesn't fit an accelerator tool.*

- **Undo Functionality:** Too risky/complex; users should manage PO deletions within Odoo.
- **Statistics Dashboard:** Not needed; users care about the *current* file, not a weekly trend.
- **Detailed Connection Diagnostics:** "Connection Failed" is sufficient; detailed latency/endpoint data is for IT, not the end-user.
- **Complex File Organization:** Current `Incoming` $\rightarrow$ `Processed` move is sufficient.
- **Progress Estimation:** Simulated progress is enough; precise timing adds complexity without value.

---

## 📅 Implementation Roadmap

### Phase 1: The Throughput Boost (1-2 Weeks)
- [ ] Batch Import Capability
- [ ] Auto-Folder Monitoring (Watchdog)
- [ ] "Next Pending File" Flow
- [ ] File Preview (Ready State)

### Phase 2: The Friction Reduction (1-2 Weeks)
- [ ] Drag and Drop Support
- [ ] Excel Template Download
- [ ] "Open in Excel" Error Recovery
- [ ] Inline Validation Status

### Phase 3: Power User Polish (1 Week)
- [ ] Fast-Track Import
- [ ] Keyboard Shortcuts
