# ⭐ Changelog ⭐

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## ⭐ [1.0.3-dev] - 2026-09-14

### Added
- **Structured Maintenance Log System**: Replaced monolithic freeform service note strings with structured engineering fields:
  - `Problem *` (Required): Primary failure description, inspection need, or defect summary.
  - `Root Cause` (Optional): Mechanical, thermal, electrical, or operational failure cause.
  - `Action Taken` (Optional): Corrective maintenance action, adjustment, or replacement procedure performed.
  - `Parts/Materials Consumed` (Optional): Materials, spare parts, serial numbers, gaskets, fluids, or filters consumed.
- **Dedicated Quick Notes**: Lightweight operational notes and shift handoffs separate from diagnostic maintenance records, identified by a distinct purple pill badge (`⚡ Quick Note`).
- **Dual-Channel Timeline Filtering**: Real-time filter toolbar embedded directly above the service history cards (`All` | `🛠️ Maintenance` | `⚡ Quick Notes`).
- **Interactive Work Analytics & Graphing Dashboard (`WorkAnalyticsDialog`)**:
  - Full-featured visual dashboard accessible via top header button, sidebar action buttons, and keyboard shortcut <kbd>Ctrl</kbd>+<kbd>G</kbd>.
  - High-resolution native Tkinter vector canvas charting with custom dark cosmic aesthetics, dynamic value axis scaling, and grid guidelines.
  - **5 Analytical View Tabs**:
    1. *Activity Over Time*: Chronological monthly service logging volume and velocity.
    2. *Work by Department*: Comparative bar distribution of service operations across departments.
    3. *Equipment Service Intensity*: Work items ranked by cumulative maintenance interventions.
    4. *Root Cause Breakdown*: Pareto breakdown of recurring engineering failure modes.
    5. *Parts Consumed Log*: Inventory parts utilization frequency and consumption log.
  - Interactive mouse-hover tooltips displaying exact metric counts, department percentages, and part frequencies.
  - Tabular lower data inspection views for immediate numerical review.
  - Dynamic KPI metric cards (Total Items, Total Notes, Maintenance Logs, Quick Notes, Total Parts Consumed).
- **Expanded Multi-Field Search**: Real-time search engine now scans across all structured fields (`problem`, `root_cause`, `action_taken`, `parts_consumed`, `quick_note`).
- **Enhanced CSV Export**: Exports dedicated columns for `Problem`, `Root Cause`, `Action Taken`, `Parts Consumed`, and `Note Type` alongside synthesized summaries.
- **100% Non-Destructive Database Schema**:
  - Synthesized backward-compatible `note` property ensuring existing unit tests, third-party consumers, and legacy records remain 100% operational without data migration.
  - Transparent deserialization of legacy string-based service logs and graceful fallback rendering.
- **Automated UI & Visual Component Tests**: Added `tests/test_ui_components.py` testing timeline filtering, card rendering, and canvas chart drawing.

---

## ⭐ [1.0.2-dev] - 2026-09-08

### Added
- **Dynamic Highest Queue Numbering**: The auto-generated Queue number now dynamically and strictly follows the highest existing record in the database. Adding, editing, or deleting items recalculates the sequence automatically (`highest + 1`) to eliminate drift and stale counters.
- **Native Service Note Editing**: Direct in-place editing for maintenance log entries via new timeline edit buttons (`✏`) and double-click actions without needing to open the JSON file directly.
- **Database Note Update API**: Added `edit_note()` to `WorkItem` and `update_service_note()` to `DatabaseManager`.
- **Keyboard Shortcut**: Added <kbd>Ctrl</kbd>+<kbd>Enter</kbd> to quickly save or update service notes in `ServiceNoteDialog`.

### Fixed
- **Service Note Dialog Save Button Visibility**: Resolved an issue where Tkinter's packing order and default multi-line text widget height caused the bottom action bar (`Save Note` / `Cancel`) in `ServiceNoteDialog` to be unmapped and hidden off-screen.
- **Dialog Viewport Hardening**: Refactored `ItemDialog` and `ServiceNoteDialog` to guarantee bottom action bars remain firmly anchored and visible across all display resolutions.

---

## ⭐ [1.0.1-dev] - 2026-09-07

### Added
- **Database Initialization Prompt**: Modal startup dialog (`DatabaseInitDialog`) when the database file is not present, offering a direct choice to load sample demo records or initialize a clean, blank database.
- **Protected Database Deletion**: Dedicated `🗑️ Delete Database...` button with a secure confirmation dialog (`DeleteDatabaseDialog`) requiring the exact phrase `"DELETE DATABASE"` before deleting the file from disk.
- **Last Opened Database Memory**: Automatically tracks, stores, and opens the last active database across workstation sessions.

### Changed
- **Non-Intrusive Database Seeding**: Removed silent automatic sample item injection so empty databases remain clean unless the user explicitly chooses to load demo data.

---

## ⭐ [1.0.0] - 2026-09-06

### Added
- **Initial Release**: OrbitTracker Work Activity & Maintenance Tracking Workstation.
- **Cosmic Dark Theme**: High-contrast obsidian palette with starlight cyan and celestial gold accents.
- **Windows High-DPI Awareness**: Clean, crisp typography and geometry scaling on 1080p, 1440p, and 4K displays.
- **JSON-Backed Database**: Human-readable, portable persistence with atomic disk writes.
- **Auto-Generated Queue Numbers**: Sequential tracking (`Q-001`, `Q-002`, ...) with custom override support.
- **Pre-Defined & Custom Columns**: Core attributes (Queue, MOC, ST, Item, Make/Model, Status, Department) plus runtime-added dynamic fields.
- **Service Log Timeline**: Chronological maintenance note histories with inline logging, edit, and deletion capabilities.
- **Instant Search & Filtering**: Multi-field querying across item attributes and service notes, plus status and department filters.
- **Real-Time KPI Cards**: Live counters for total work items, active/inactive statuses, and maintenance logs.
- **CSV Data Export**: 1-click export of workstation records and service log summaries to CSV.
- **Automated Packaging Pipeline**: PyInstaller compilation, portable ZIP staging, and SHA-256 checksum generation.
