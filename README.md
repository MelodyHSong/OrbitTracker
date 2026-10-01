# 🪐 OrbitTracker 🪐

> "Work Activity & Maintenance Tracking Workstation with JSON Database Persistence."

**OrbitTracker** is a modern Windows desktop workstation designed to log, inspect, and organize equipment maintenance, work orders, and day-to-day operations. Built with a signature Cosmic Dark UI theme, it pairs lightweight standard JSON persistence with high-performance querying, auto-generated Queue Numbers, pre-defined workflow columns, dynamic runtime-added columns, and a chronological Service Log timeline.

---

## ✨ Features

- **📂 JSON-Backed Database**: Human-readable, portable, atomic writes that protect against data corruption.
- **🔢 Auto-Generated Queue Numbers**: Dynamic sequential tracking (`Q-001`, `Q-002`, ...) that always follows the highest existing queue number in the database, automatically recalculating when items are added, modified, or deleted.
- **📋 Pre-Defined Core Columns & Workflow**:
  - **Queue Number**: Automatic sequence identifier following the highest record.
  - **MOC Number**: Management of Change / Work Order tracking identifier.
  - **ST Number**: Service Tag identifier.
  - **Item Name**: Name and description of the equipment or workpiece.
  - **Make and Model**: Hardware manufacturer and model.
  - **Device Type**: Equipment type classification (*Booster Pump*, *Transceiver*, *Actuator Solenoid*, *Power Inverter*, *Sensor*, etc.).
  - **Category**: Engineering discipline dropdown (*Mechanical & Structural*, *Electrical & Avionics*, *Cryogenics & Propulsion*, *Hydraulics & Pneumatics*, *Thermal & Environmental*, *Optics & Payloads*, *Sensors & Telemetry*).
  - **Status & Operational State**: Live state tracking (**Done**, **Working**, **Stuck**, **Idle**) with colored badges and status toggling (`Active` / `Inactive`).
  - **Department**: Assigned department with autocomplete suggestions from existing records.
  - **Service Log**: Chronological maintenance history timeline for each item.
- **🛡️ Non-Breaking Schema Auto-Migration**: Automatically migrates databases with custom columns named "Device Type" or "Category" into core fields with automated safety backups (`.pre_migration_backup`).
- **⚙️ Dynamic Custom Columns**: Add new user-defined fields (e.g. *Facility Bay*, *Serial Number*, *Calibration Standard*, *Priority*) at runtime. All items instantly inherit the schema.
- **🛠️ Overhauled Maintenance Diagnostics & Task Presets**:
  - **Structured Maintenance Logs**: Comprehensive engineering log entries with dedicated fields:
    - `Problem *` (Required): Core fault, failure mode, or inspection reason.
    - `Root Cause` (Optional): Underlying mechanical, electrical, or procedural cause.
    - `Action Taken` (Optional): Remediation steps, repairs, or procedures performed.
    - `Parts/Materials Consumed` (Optional): Replacement parts, serials, gaskets, lubricants, and materials used.
    - `Work State`: Select **Done**, **Working**, **Stuck**, or **Idle** state for immediate operational awareness.
    - `Severity & Service Type`: Classify severity (*Routine*, *Medium*, *High*, *Critical*) and service category (*Corrective Repair*, *Preventative Maintenance*, *Calibration*, *Inspection & Testing*, *Overhaul*).
    - `Technician Attribution`: Capture operator or technician handling the job.
  - **⚡ Quick Task Presets**: One-click menu templates in `ServiceNoteDialog` for instant auto-filling of common operational tasks.
  - **Dedicated Quick Notes**: Lightweight operational memos and shift handoffs visually distinguished with a celestial `⚡ Quick Note` badge.
  - **Faceted Timeline Navigation**: Filter notes instantly between `All`, `🛠️ Maintenance`, `⚡ Quick Notes`, `🔄 Working`, `⚠️ Stuck`, and `✅ Done`.
  - **Native In-App Note Editing**: Edit existing notes directly via timeline edit buttons (`✏`) or double-clicking any note card.
  - Quick inline logging directly from the inspector panel without modal dialogs.
  - Timestamped notes with full edit and delete capabilities.
- **📊 Interactive Multi-Period Work Analytics Dashboard**:
  - Dedicated multi-tab vector canvas visualization modal accessible via header button, sidebar, or `Ctrl + G`.
  - **Multi-Period Aggregation**: Switch instantly between **Daily**, **Weekly**, **Monthly**, **Quarterly**, and **Yearly** analysis timeframes.
  - **7 Interactive Analytical Views**:
    - **Temporal Trends**: Volume trends and velocity curves across the chosen timeframe.
    - **Device Types & Categories**: Distribution across hardware types and engineering categories.
    - **Problems & Diagnostics**: Frequency analysis of root causes, error codes, and failure descriptions.
    - **Parts Consumed Log**: Comprehensive parts utilization registry and consumption counts.
    - **Work by Department**: Comparative workload distributions across engineering units.
    - **Equipment Service Intensity**: High-maintenance equipment Pareto ranking.
    - **Root Cause Breakdown**: Fault mode distribution and wear patterns.
  - **Interactive Features**: Dynamic tooltips on hover, real-time KPI metrics, global filter controls (Device Type, Category, Work State), and lower data grid breakdowns.
- **🔍 Instant Multi-Field Search & Filter**:
  - Live search across all core attributes, custom fields, and maintenance note content (including problem, root cause, action taken, and parts consumed).
  - Segmented work state & status filtering (`All`, `Working`, `Stuck`, `Done`, `Idle`, `Active`, `Inactive`).
  - Dropdown filter by Device Type, Category, and Department.
- **📊 Real-Time Metrics & KPI Status Matrix**:
  - Total Work Items count.
  - Real-time **Working**, **Stuck**, **Done**, and **Idle** counters.
  - Total service maintenance notes logged.
- **🌱 Smart Database Initialization**: Missing or fresh database paths prompt users with a choice to load demo equipment data or start with a clean empty database.
- **🛡️ Protected Database Deletion**: Permanent file deletion requires typing `"DELETE DATABASE"` in a confirmation modal to safeguard against accidental data loss.
- **🔄 Workspace State Persistence**: Automatically remembers and reopens the last opened database on launch.
- **📤 Export Capabilities**: 1-click export to standard CSV format including Category, Device Type, Current State, custom columns, and structured service history columns.
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
  "version": "1.1.0-dev",
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
      "category": "Cryogenics & Propulsion",
      "device_type": "Booster Pump",
      "custom_fields": {
        "col_a81f3": "Bay 4 West"
      },
      "service_log": [
        {
          "id": "4b219cf0",
          "timestamp": "2026-09-14 14:15:00",
          "note_type": "maintenance",
          "work_status": "Done",
          "severity": "Routine",
          "service_type": "Corrective Repair",
          "technician": "M. Song",
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
