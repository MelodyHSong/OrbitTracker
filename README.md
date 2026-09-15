# 🪐 OrbitTracker 🪐

> "Work Activity & Maintenance Tracking Workstation with JSON Database Persistence."

**OrbitTracker** is a modern Windows desktop workstation designed to log, inspect, and organize equipment maintenance, work orders, and day-to-day operations. Built with a signature Cosmic Dark UI theme, it pairs lightweight standard JSON persistence with high-performance querying, auto-generated Queue Numbers, pre-defined workflow columns, dynamic runtime-added columns, and a chronological Service Log timeline.

---

## ✨ Features

- **📂 JSON-Backed Database**: Human-readable, portable, atomic writes that protect against data corruption.
- **🔢 Auto-Generated Queue Numbers**: Dynamic sequential tracking (`Q-001`, `Q-002`, ...) that always follows the highest existing queue number in the database, automatically recalculating when items are added, modified, or deleted.
- **📋 Pre-Defined Core Columns**:
  - **Queue Number**: Automatic sequence identifier following the highest record.
  - **MOC Number**: Management of Change / Work Order tracking identifier.
  - **ST Number**: Service Tag identifier.
  - **Item Name**: Name and description of the equipment or workpiece.
  - **Make and Model**: Hardware manufacturer and model.
  - **Status**: Visual status toggling (`Active` / `Inactive`) with colored badges.
  - **Department**: Assigned department with autocomplete suggestions from existing records.
  - **Service Log**: Chronological maintenance history timeline for each item.
- **⚙️ Dynamic Custom Columns**: Add new user-defined fields (e.g. *Facility Bay*, *Serial Number*, *Assigned Technician*, *Priority*) at runtime. All items instantly inherit the schema.
- **🛠️ Structured Service Note Diagnostics & Quick Notes**:
  - **Structured Maintenance Logs**: Comprehensive engineering log entries with dedicated fields:
    - `Problem *` (Required): Core fault, failure mode, or inspection reason.
    - `Root Cause` (Optional): Underlying mechanical, electrical, or procedural cause.
    - `Action Taken` (Optional): Remediation steps, repairs, or procedures performed.
    - `Parts/Materials Consumed` (Optional): Replacement parts, serials, gaskets, lubricants, and materials used.
  - **Dedicated Quick Notes**: Lightweight operational memos and shift handoffs visually distinguished with a dedicated `⚡ Quick Note` badge.
  - **Dual-Channel Timeline Filtering**: Filter notes instantly between `All`, `🛠️ Maintenance`, and `⚡ Quick Notes`.
  - **Native In-App Note Editing**: Edit existing notes directly via timeline edit buttons (`✏`) or double-clicking any note card.
  - Quick inline logging directly from the inspector panel without modal dialogs.
  - Timestamped notes with full edit and delete capabilities.
- **📊 Interactive Work Performance & Analytics Dashboard**:
  - Dedicated multi-tab vector canvas visualization modal accessible via header button, sidebar, or `Ctrl + G`.
  - **5 Interactive Analytical Views**:
    - **Activity Over Time**: Monthly service volume trends and activity velocity.
    - **Work by Department**: Comparative workload distributions across engineering units.
    - **Equipment Service Intensity**: High-maintenance equipment ranking and service frequency.
    - **Root Cause Breakdown**: Pareto distribution of failure modes and root causes.
    - **Parts Consumed Inventory**: Comprehensive parts utilization registry and consumption frequencies.
  - **Interactive Features**: Dynamic tooltips on hover, real-time KPI metrics, and lower data grid breakdowns.
- **🔍 Instant Multi-Field Search & Filter**:
  - Live search across all core attributes, custom fields, and maintenance note content (including problem, root cause, action taken, and parts consumed).
  - Segmented status filtering (`All`, `Active`, `Inactive`).
  - Dropdown filter by Department.
- **📊 Real-Time Metrics & KPI Cards**:
  - Total Work Items count.
  - Active vs. Inactive status counters.
  - Total service maintenance notes logged.
- **🌱 Smart Database Initialization**: Missing or fresh database paths prompt users with a choice to load demo equipment data or start with a clean empty database.
- **🛡️ Protected Database Deletion**: Permanent file deletion requires typing `"DELETE DATABASE"` in a confirmation modal to safeguard against accidental data loss.
- **🔄 Workspace State Persistence**: Automatically remembers and reopens the last opened database on launch.
- **📤 Export Capabilities**: 1-click export to standard CSV format including custom columns and structured service history columns (Problem, Root Cause, Action Taken, Parts Consumed, Note Type).
- **🎨 Cosmic Dark Workstation Aesthetic**: High-DPI scaling, custom Tkinter and TTK clam theme, custom multi-resolution icon (`.ico`), and activity console.

---

## 🚀 Quick Start

### Launching OrbitTracker
Run the smart Windows launcher batch file:
```cmd
run.bat
```
Or launch directly with Python:
```cmd
python app.py
```

### Dependencies
OrbitTracker uses Python's standard library (`tkinter`, `json`, `threading`, `queue`, `os`, `sys`).
- Optional for icon synthesis: `pillow` (already installed)
- Optional for `.exe` compilation: `pyinstaller`

---

## 🗃️ Database JSON Structure

Databases are saved by default to `orbit_database.json` in the application directory:

```json
{
  "app_name": "OrbitTracker",
  "version": "1.0.3-dev",
  "last_modified": "2026-09-14 20:30:00",
  "queue_prefix": "Q-",
  "next_queue_id": 4,
  "custom_columns": [
    {
      "id": "col_a81f3",
      "name": "Facility Bay",
      "default_val": "Main Hangar"
    }
  ],
  "items": [
    {
      "id": "c7104bfa-9f42-4f18-a6d1-f20cb058e578",
      "queue_number": "Q-001",
      "moc_number": "MOC-3041",
      "st_number": "ST-94812",
      "item_name": "Centrifugal Booster Pump",
      "make_and_model": "Flowserve HPX-600",
      "status": "Active",
      "department": "Cryogenics & Propulsion",
      "custom_fields": {
        "col_a81f3": "Bay 4 West"
      },
      "service_log": [
        {
          "id": "4b219cf0",
          "timestamp": "2026-09-14 14:15:00",
          "note_type": "maintenance",
          "problem": "Seal leakage detected during high-pressure run",
          "root_cause": "Thermal cycling degraded elastomer O-ring",
          "action_taken": "Replaced mechanical seal assembly and re-torqued casing bolts",
          "parts_consumed": "Seal Kit #SK-401, Viton O-Ring #OR-88"
        }
      ],
      "created_at": "2026-09-14 14:00:00",
      "updated_at": "2026-09-14 14:15:00"
    }
  ]
}
```

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
| :--- | :--- |
| `Ctrl + N` | Add New Work Item |
| `Ctrl + S` | Save Current Database |
| `Ctrl + O` | Open Existing Database File |
| `Ctrl + E` | Export Records to CSV |
| `Ctrl + F` | Focus Live Search Box |
| `Ctrl + G` | Open Work Performance Graphs & Analytics Dashboard |
| `Ctrl + Enter` | Save or Update Note in Service Note Dialog |
| `F5` | Refresh Workstation Grid & Statistics |
| `Delete` | Delete Currently Selected Item |

---

## 📦 Building Standalone Executable

To compile a standalone Windows `.exe`:
```cmd
build.bat
```
The compiled executable will be placed in `dist/orbittracker.exe`.
