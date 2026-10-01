# ⭐ Changelog ⭐

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## ⭐ [1.1.0-dev] - 2026-09-30

### Added
- **Movable & Resizable UI Data Grid Columns**:
  - Implemented drag-and-drop column reordering on Treeview headers with automatic persistence of `column_order` in `config.json`.
  - Configured resizable columns (`stretch=False`) that preserve custom widths across table refreshes and persist in `config.json`.
- **Orange Observation Classification for Quick Notes**:
  - Converted quick notes to dedicated observation logs tagged with a vibrant orange `🔭 OBSERVATION` pill badge (`#f0883e`).
  - Removed Done/Idle/Working status overrides from notes, ensuring quick observations never overwrite the operational Kanban state of equipment.
- **Empty Baseline Presets for Categories, Device Types & Tasks**:
  - Initialized databases with empty preset categories, device types, technicians, and tasks so users start with a clean slate and build their own operational library.
  - Added user-customizable task preset saving (`💾 Save Current Form as Preset...`) and preset deletion in `ServiceNoteDialog`.
- **Dynamic Technician Autocomplete Dropdowns**:
  - Automatically registers newly typed technicians and populates dropdowns across `ItemDialog` and `ServiceNoteDialog` for future use.
- **Interactive Note Type Mode Switcher**:
  - Added an in-dialog toggle (`🛠️ Maintenance Record` vs `🔭 Observation Note`) in `ServiceNoteDialog` for seamless switching between structured maintenance forms and quick notes.
- **Cosmic Motto**:
  - Added witty branding quote under the Orbit Tracker header logo: *"Always document your journey, traveller!"*.

### Fixed
- **Analytics Dialog Glitches**:
  - Corrected canvas legend overlap in `WorkAnalyticsDialog` by dynamically computing character widths and spacing.
  - Eliminated horizontal tab-bar overflow by resizing window default to 1080x740 with responsive layout.
- **Service Note Dialog Rendering**:
  - Fixed an `AttributeError` on `self.db` in `ServiceNoteDialog` that prevented the lower half of the maintenance form from rendering.
- **Preset Deletion UI Font Reference**:
  - Fixed an undefined `FONT_UI_BOLD` constant reference on the task preset deletion button in `ServiceNoteDialog`.

---

## ⭐ [1.0.3-dev] - 2026-09-30

### Added
- **Category & Device Type First-Class Workflows**:
  - Integrated `device_type` and `category` as core equipment attributes across the schema, Item creation dialog (`ItemDialog`), central data grid, sorting engine, and details inspector.
  - Pre-populated Category dropdown with standard aerospace and industrial engineering domains plus auto-discovery of existing categories.
  - Multi-field sidebar filters for **Device Type**, **Category**, and **Work State**.
- **Non-Breaking Database Schema Auto-Migration**:
  - Automated detection and non-destructive migration of legacy custom columns matching "Device Type" or "Category" (`DatabaseManager.migrate_schema()`).
  - Historical custom field values safely copied to core attributes without data loss.
  - Safe retirement of legacy custom column definitions to prevent duplicate columns in the workstation grid.
  - Automatic pre-migration backup creation (`.pre_migration_backup`).
- **Operational Work States (Done, Working, Stuck, Idle)**:
  - Added dedicated operational state tracking at the service note and equipment level.
  - Prominent color-coded work state pill badges in the details inspector (`DONE`, `WORKING`, `STUCK`, `IDLE`).
  - Grid row styling accents for items in `Stuck` (coral) and `Working` (cyan) states.
  - Sidebar KPI status matrix with live counters for **Total**, **Working**, **Stuck**, **Done**, **Idle**, and **Notes**.
- **Overhauled Maintenance Diagnostics & Task Presets**:
  - Structured maintenance logs with dedicated engineering fields: `Problem *`, `Root Cause`, `Action Taken`, and `Parts/Materials Consumed`.
  - **⚡ Task Presets Menu**: One-click quick-fill templates in `ServiceNoteDialog` for routine maintenance (PM Pressure Seal, Bearing Lubrication Flush, Sensor Recalibration, RF Link Check, Actuator Solenoid Jammed, Intake Functional Pass).
  - Severity classification (`Routine`, `Medium`, `High`, `Critical`), Service Type categorizing, and Technician attribution.
  - Faceted timeline filtering supporting `All`, `🛠️ Maintenance`, `⚡ Quick Notes`, `🔄 Working`, `⚠️ Stuck`, and `✅ Done`.
- **Multi-Period Work Analytics Engine (`WorkAnalyticsDialog`)**:
  - Added interactive period switcher supporting **Daily**, **Weekly**, **Monthly**, **Quarterly**, and **Yearly** analysis intervals.
  - **7 Analytical View Tabs**:
    1. *Temporal Trends*: Dynamic volume trends and velocity curves across the chosen timeframe.
    2. *Device Types & Categories*: Distribution across hardware archetypes and engineering categories.
    3. *Problems & Diagnostics*: Frequency analysis of recurring failure modes and diagnostics.
    4. *Parts Consumed Log*: Parts utilization registry with consumable counts.
    5. *Work by Department*: Comparative workload distributions across engineering units.
    6. *Equipment Service Intensity*: High-maintenance equipment Pareto ranking.
    7. *Root Cause Breakdown*: Fault mode distribution and wear patterns.
  - Global filter controls by Device Type, Category, and Work State.
  - Interactive mouse-hover tooltips and lower data inspection tables.
- **Enhanced CSV Export**: Outputs dedicated columns for `Device Type`, `Category`, `Current State`, `Problem`, `Root Cause`, `Action Taken`, `Parts Consumed`, and `Note Type`.
- **Comprehensive Test Coverage**: Extended `tests/test_database.py` and `tests/test_ui_components.py` testing migration, work states, multi-period analytics intervals, and sidebar filtering.

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
