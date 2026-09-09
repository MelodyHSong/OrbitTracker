# ⭐ Changelog ⭐

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
