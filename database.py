# 🪐 OrbitTracker — Database & Persistence Layer
# Author: MelodyHSong
# File Name: database.py
# Description: JSON-backed database manager with auto-generated Queue Numbers,
#              dynamic custom columns, service log tracking, device type and category workflows,
#              work status (Done, Working, Stuck, Idle), and multi-period analytics.

import os
import json
import uuid
from datetime import datetime
from collections import defaultdict


class ServiceNote:
    """Represents a single maintenance record or quick note for a tracked item."""
    def __init__(
        self,
        note: str = "",
        timestamp: str = None,
        note_id: str = None,
        note_type: str = "maintenance",
        problem: str = "",
        root_cause: str = "",
        action_taken: str = "",
        parts_consumed: str = "",
        quick_note: str = "",
        work_status: str = "Done",
        severity: str = "Routine",
        service_type: str = "Corrective Repair",
        technician: str = ""
    ):
        self.id = note_id or str(uuid.uuid4())[:8]
        self.timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.note_type = "quick" if str(note_type).strip().lower() == "quick" else "maintenance"
        self.problem = str(problem or "").strip()
        self.root_cause = str(root_cause or "").strip()
        self.action_taken = str(action_taken or "").strip()
        self.parts_consumed = str(parts_consumed or "").strip()
        self.quick_note = str(quick_note or "").strip()

        # Operational Work State: Done, Working, Stuck, Idle (or Observation for quick notes)
        if self.note_type == "quick":
            self.work_status = "Observation"
            self.severity = ""
            self.service_type = "Observation"
        else:
            ws = str(work_status or "Done").strip().capitalize()
            if ws not in ("Done", "Working", "Stuck", "Idle"):
                ws = "Done"
            self.work_status = ws
            self.severity = str(severity or "Routine").strip()
            self.service_type = str(service_type or "Corrective Repair").strip()

        self.technician = str(technician or "").strip()

        # Backward compatibility & display string synthesis
        if self.note_type == "quick":
            if not self.quick_note and note:
                self.quick_note = str(note).strip()
            self.note = self.quick_note
        else:
            if not self.problem and note:
                self.problem = str(note).strip()

            # Synthesize human-readable string representation for self.note
            if not self.root_cause and not self.action_taken and not self.parts_consumed:
                self.note = self.problem or str(note or "").strip()
            else:
                parts = []
                if self.problem:
                    parts.append(f"Problem: {self.problem}")
                if self.root_cause:
                    parts.append(f"Root Cause: {self.root_cause}")
                if self.action_taken:
                    parts.append(f"Action: {self.action_taken}")
                if self.parts_consumed:
                    parts.append(f"Parts: {self.parts_consumed}")
                self.note = " | ".join(parts) if parts else str(note or "").strip()

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "note_type": self.note_type,
            "work_status": self.work_status,
            "severity": self.severity,
            "service_type": self.service_type,
            "technician": self.technician,
            "problem": self.problem,
            "root_cause": self.root_cause,
            "action_taken": self.action_taken,
            "parts_consumed": self.parts_consumed,
            "quick_note": self.quick_note,
            "note": self.note
        }

    @classmethod
    def from_dict(cls, data):
        raw_note = data.get("note", "")
        work_status = data.get("work_status", "Done")
        severity = data.get("severity", "Routine")
        service_type = data.get("service_type", "Corrective Repair")
        technician = data.get("technician", "")

        # If explicitly marked as quick note or has quick_note without problem
        if data.get("note_type") == "quick" or ("quick_note" in data and not data.get("problem")):
            return cls(
                note=raw_note,
                timestamp=data.get("timestamp"),
                note_id=data.get("id"),
                note_type="quick",
                quick_note=data.get("quick_note", raw_note),
                work_status=work_status,
                severity=severity,
                service_type=service_type,
                technician=technician
            )

        # If structured fields exist
        if "problem" in data or "action_taken" in data or "root_cause" in data or "parts_consumed" in data:
            return cls(
                note=raw_note,
                timestamp=data.get("timestamp"),
                note_id=data.get("id"),
                note_type=data.get("note_type", "maintenance"),
                problem=data.get("problem", raw_note),
                root_cause=data.get("root_cause", ""),
                action_taken=data.get("action_taken", ""),
                parts_consumed=data.get("parts_consumed", ""),
                quick_note=data.get("quick_note", ""),
                work_status=work_status,
                severity=severity,
                service_type=service_type,
                technician=technician
            )

        # Legacy database entry (only 'note' key exists):
        return cls(
            note=raw_note,
            timestamp=data.get("timestamp"),
            note_id=data.get("id"),
            note_type="maintenance",
            problem=raw_note,
            work_status=work_status,
            severity=severity,
            service_type=service_type,
            technician=technician
        )


class WorkItem:
    """Represents an equipment, tool, or work activity item tracked in OrbitTracker."""
    def __init__(
        self,
        queue_number: str = "",
        moc_number: str = "",
        st_number: str = "",
        item_name: str = "",
        make_and_model: str = "",
        status: str = "Active",
        department: str = "",
        category: str = "General",
        device_type: str = "Unspecified",
        custom_fields: dict = None,
        service_log: list = None,
        item_id: str = None,
        created_at: str = None,
        updated_at: str = None
    ):
        self.id = item_id or str(uuid.uuid4())
        self.queue_number = queue_number
        self.moc_number = str(moc_number).strip()
        self.st_number = str(st_number).strip()
        self.item_name = str(item_name).strip()
        self.make_and_model = str(make_and_model).strip()
        self.status = "Active" if str(status).strip().lower() in ("active", "true", "1") else "Inactive"
        self.department = str(department).strip()
        self.category = str(category or "").strip()
        self.device_type = str(device_type or "").strip()
        self.custom_fields = dict(custom_fields) if custom_fields else {}
        self.service_log = [
            note if isinstance(note, ServiceNote) else ServiceNote.from_dict(note)
            for note in (service_log or [])
        ]
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.created_at = created_at or now_str
        self.updated_at = updated_at or now_str

    def get_work_status(self) -> str:
        """Returns the item's current operational state (Done, Working, Stuck, Idle) based on the latest maintenance note."""
        for note in reversed(self.service_log):
            if getattr(note, "note_type", "maintenance") == "quick":
                continue
            ws = getattr(note, "work_status", None)
            if ws in ("Done", "Working", "Stuck", "Idle"):
                return ws
        return "Idle" if self.status == "Inactive" else "Done"

    def to_dict(self):
        return {
            "id": self.id,
            "queue_number": self.queue_number,
            "moc_number": self.moc_number,
            "st_number": self.st_number,
            "item_name": self.item_name,
            "make_and_model": self.make_and_model,
            "status": self.status,
            "department": self.department,
            "category": self.category,
            "device_type": self.device_type,
            "custom_fields": self.custom_fields,
            "service_log": [n.to_dict() for n in self.service_log],
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            queue_number=data.get("queue_number", ""),
            moc_number=data.get("moc_number", ""),
            st_number=data.get("st_number", ""),
            item_name=data.get("item_name", ""),
            make_and_model=data.get("make_and_model", ""),
            status=data.get("status", "Active"),
            department=data.get("department", ""),
            category=data.get("category", ""),
            device_type=data.get("device_type", ""),
            custom_fields=data.get("custom_fields", {}),
            service_log=data.get("service_log", []),
            item_id=data.get("id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )

    def add_note(
        self,
        note_text: str = "",
        timestamp: str = None,
        note_type: str = "maintenance",
        problem: str = "",
        root_cause: str = "",
        action_taken: str = "",
        parts_consumed: str = "",
        quick_note: str = "",
        work_status: str = "Done",
        severity: str = "Routine",
        service_type: str = "Corrective Repair",
        technician: str = ""
    ) -> ServiceNote:
        """Adds a service note (either structured maintenance record or quick note)."""
        if isinstance(note_text, dict):
            note = ServiceNote.from_dict(note_text)
        elif note_type == "quick":
            q_txt = quick_note or note_text
            note = ServiceNote(
                note=q_txt,
                timestamp=timestamp,
                note_type="quick",
                quick_note=q_txt,
                work_status=work_status,
                severity=severity,
                service_type=service_type,
                technician=technician
            )
        else:
            note = ServiceNote(
                note=note_text,
                timestamp=timestamp,
                note_type=note_type,
                problem=problem or note_text,
                root_cause=root_cause,
                action_taken=action_taken,
                parts_consumed=parts_consumed,
                work_status=work_status,
                severity=severity,
                service_type=service_type,
                technician=technician
            )
        self.service_log.append(note)
        self.touch()
        return note

    def delete_note(self, note_id: str) -> bool:
        before_len = len(self.service_log)
        self.service_log = [n for n in self.service_log if n.id != note_id]
        if len(self.service_log) < before_len:
            self.touch()
            return True
        return False

    def edit_note(
        self,
        note_id: str,
        note_text: str = None,
        timestamp: str = None,
        note_type: str = None,
        problem: str = None,
        root_cause: str = None,
        action_taken: str = None,
        parts_consumed: str = None,
        quick_note: str = None,
        work_status: str = None,
        severity: str = None,
        service_type: str = None,
        technician: str = None
    ) -> bool:
        """Edits an existing maintenance note or quick note in the service log."""
        for note in self.service_log:
            if note.id == note_id:
                if timestamp:
                    note.timestamp = timestamp
                if note_type is not None:
                    note.note_type = note_type
                if work_status is not None:
                    ws = str(work_status).strip().capitalize()
                    note.work_status = ws if ws in ("Done", "Working", "Stuck", "Idle") else "Done"
                if severity is not None:
                    note.severity = str(severity).strip()
                if service_type is not None:
                    note.service_type = str(service_type).strip()
                if technician is not None:
                    note.technician = str(technician).strip()
                if quick_note is not None:
                    note.quick_note = str(quick_note).strip()
                if problem is not None:
                    note.problem = str(problem).strip()
                if root_cause is not None:
                    note.root_cause = str(root_cause).strip()
                if action_taken is not None:
                    note.action_taken = str(action_taken).strip()
                if parts_consumed is not None:
                    note.parts_consumed = str(parts_consumed).strip()

                if note.note_type == "quick":
                    if note_text is not None and not quick_note:
                        note.quick_note = str(note_text).strip()
                    note.note = note.quick_note
                else:
                    if note_text is not None and problem is None:
                        note.problem = str(note_text).strip()
                    if not note.root_cause and not note.action_taken and not note.parts_consumed:
                        note.note = note.problem or (note_text or note.note)
                    else:
                        parts = []
                        if note.problem:
                            parts.append(f"Problem: {note.problem}")
                        if note.root_cause:
                            parts.append(f"Root Cause: {note.root_cause}")
                        if note.action_taken:
                            parts.append(f"Action: {note.action_taken}")
                        if note.parts_consumed:
                            parts.append(f"Parts: {note.parts_consumed}")
                        note.note = " | ".join(parts) if parts else (note_text or note.note)

                self.touch()
                return True
        return False

    def touch(self):
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class DatabaseManager:
    """Manages reading, writing, querying, and updating the OrbitTracker JSON database."""

    DEFAULT_DB_NAME = "orbit_database.json"

    DEFAULT_CATEGORIES = []
    DEFAULT_DEVICE_TYPES = []

    WORK_STATUSES = ["Done", "Working", "Stuck", "Idle"]

    def __init__(self, db_path: str = None):
        self.db_path = os.path.abspath(db_path or self.DEFAULT_DB_NAME)
        self.app_name = "OrbitTracker"
        self.version = "1.1.0-dev"
        self.queue_prefix = "Q-"
        self.next_queue_id = 1
        self.custom_columns = []  # List of {"id": str, "name": str, "default_val": str}
        self.categories = []      # User-defined / discovered categories
        self.device_types = []    # User-defined / discovered device types
        self.technicians = []     # User-defined / discovered technicians
        self.task_presets = []    # User-defined task presets
        self.items = []           # List of WorkItem instances
        self.is_dirty = False
        self.last_saved = None

        self.load()

    def create_default_schema(self):
        """Initializes empty database schema with zero preset categories, device types, or tasks."""
        self.queue_prefix = "Q-"
        self.next_queue_id = 1
        self.custom_columns = []
        self.categories = []
        self.device_types = []
        self.technicians = []
        self.task_presets = []
        self.items = []
        self.is_dirty = False

    def migrate_schema(self) -> bool:
        """
        Safely and non-destructively migrates legacy databases:
        1. Detects any custom column named 'Device Type' (or variations: 'device_type', 'device', 'equipment type')
           and migrates custom_fields values to item.device_type, then removes the custom column definition.
        2. Detects any custom column named 'Category' (or variations: 'item category', 'work category')
           and migrates custom_fields values to item.category, then removes the custom column definition.
        3. Ensures all items have valid category and device_type attributes without forced placeholders.
        Returns True if any migration modifications were made.
        """
        migrated = False

        device_type_patterns = {
            "device type", "devicetype", "device_type", "device-type",
            "device", "equipment type", "equipmenttype", "asset type", "unit type"
        }
        category_patterns = {
            "category", "categories", "item category", "work category",
            "equipment category", "classification"
        }

        dev_col_ids = []
        cat_col_ids = []
        remaining_custom_cols = []

        for col in self.custom_columns:
            name_clean = col.get("name", "").strip().lower().replace("_", " ").replace("-", " ")
            if name_clean in device_type_patterns:
                dev_col_ids.append((col["id"], col.get("default_val", "")))
            elif name_clean in category_patterns:
                cat_col_ids.append((col["id"], col.get("default_val", "")))
            else:
                remaining_custom_cols.append(col)

        if dev_col_ids or cat_col_ids:
            migrated = True
            self.custom_columns = remaining_custom_cols

        for item in self.items:
            for col_id, def_val in dev_col_ids:
                if col_id in item.custom_fields:
                    val = item.custom_fields.pop(col_id, "")
                    if (not getattr(item, "device_type", None) or item.device_type in ("", "Unspecified")) and val:
                        item.device_type = str(val).strip()
                        migrated = True

            for col_id, def_val in cat_col_ids:
                if col_id in item.custom_fields:
                    val = item.custom_fields.pop(col_id, "")
                    if (not getattr(item, "category", None) or item.category in ("", "General")) and val:
                        item.category = str(val).strip()
                        migrated = True

            if not hasattr(item, "device_type") or item.device_type is None:
                item.device_type = ""
            if not hasattr(item, "category") or item.category is None:
                item.category = ""

        if migrated:
            self.is_dirty = True
            if os.path.exists(self.db_path):
                try:
                    backup_path = self.db_path + ".pre_migration_backup"
                    if not os.path.exists(backup_path):
                        import shutil
                        shutil.copy2(self.db_path, backup_path)
                except Exception:
                    pass
            self.save()

        return migrated

    def load(self, path: str = None):
        """Loads database from JSON file. If not found, initializes a fresh database."""
        if path:
            self.db_path = os.path.abspath(path)

        if not os.path.exists(self.db_path):
            self.create_default_schema()
            # Save default starter database
            self.save()
            return

        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.app_name = data.get("app_name", "OrbitTracker")
            self.version = data.get("version", "1.1.0-dev")
            self.queue_prefix = data.get("queue_prefix", "Q-")
            self.next_queue_id = int(data.get("next_queue_id", 1))
            self.custom_columns = data.get("custom_columns", [])
            self.categories = data.get("categories", [])
            self.device_types = data.get("device_types", [])
            self.technicians = data.get("technicians", [])
            self.task_presets = data.get("task_presets", [])

            items_raw = data.get("items", [])
            self.items = [WorkItem.from_dict(it) for it in items_raw]
            self.update_next_queue_id_from_items()

            # Execute non-destructive automated schema migration
            self.migrate_schema()

            self.is_dirty = False
            self.last_saved = datetime.now()
        except Exception as e:
            raise RuntimeError(f"Failed to load database from {self.db_path}: {e}")

    def save(self, path: str = None):
        """Saves current database to JSON file atomically."""
        target_path = os.path.abspath(path or self.db_path)
        dir_name = os.path.dirname(target_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

        data = {
            "app_name": self.app_name,
            "version": self.version,
            "last_modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "queue_prefix": self.queue_prefix,
            "next_queue_id": self.get_next_queue_id(),
            "custom_columns": self.custom_columns,
            "categories": getattr(self, "categories", []),
            "device_types": getattr(self, "device_types", []),
            "technicians": getattr(self, "technicians", []),
            "task_presets": getattr(self, "task_presets", []),
            "items": [it.to_dict() for it in self.items]
        }

        # Write to temporary file first, then atomically replace
        temp_path = target_path + ".tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        os.replace(temp_path, target_path)

        self.db_path = target_path
        self.is_dirty = False
        self.last_saved = datetime.now()

    # ==========================================================================
    # QUEUE NUMBER GENERATION (Always next following highest one)
    # ==========================================================================
    def get_highest_queue_id(self) -> int:
        """Finds the maximum integer queue number suffix among all existing items."""
        max_id = 0
        for it in self.items:
            q = (it.queue_number or "").strip()
            if q.startswith(self.queue_prefix):
                suffix = q[len(self.queue_prefix):]
                if suffix.isdigit():
                    val = int(suffix)
                    if val > max_id:
                        max_id = val
        return max_id

    def get_next_queue_id(self) -> int:
        """Returns the next sequential integer ID following the highest existing item."""
        return self.get_highest_queue_id() + 1

    def generate_next_queue_number(self) -> str:
        """Returns the next sequential queue number that follows the highest existing one."""
        next_id = self.get_next_queue_id()
        self.next_queue_id = next_id + 1
        return f"{self.queue_prefix}{next_id:03d}"

    def peek_next_queue_number(self) -> str:
        """Previews the next sequential queue number following the highest existing one."""
        return f"{self.queue_prefix}{self.get_next_queue_id():03d}"

    def update_next_queue_id_from_items(self):
        """Ensures next_queue_id is always the next ID following the highest existing queue number."""
        self.next_queue_id = self.get_next_queue_id()

    # ==========================================================================
    # ITEM CRUD
    # ==========================================================================
    def add_item(
        self,
        moc_number: str,
        st_number: str,
        item_name: str,
        make_and_model: str,
        status: str = "Active",
        department: str = "",
        category: str = "General",
        device_type: str = "Unspecified",
        custom_fields: dict = None,
        initial_note: str = None,
        queue_number: str = None,
        initial_note_data: dict = None
    ) -> WorkItem:
        """Adds a new work item with auto-generated queue number and optional initial service note."""
        if not queue_number:
            queue_number = self.generate_next_queue_number()
        else:
            queue_number = queue_number.strip()

        fields = {}
        for col in self.custom_columns:
            col_id = col["id"]
            fields[col_id] = col.get("default_val", "")
        if custom_fields:
            fields.update(custom_fields)

        item = WorkItem(
            queue_number=queue_number,
            moc_number=moc_number,
            st_number=st_number,
            item_name=item_name,
            make_and_model=make_and_model,
            status=status,
            department=department,
            category=category,
            device_type=device_type,
            custom_fields=fields
        )

        if initial_note_data:
            item.add_note(
                note_text=initial_note_data.get("note", ""),
                timestamp=initial_note_data.get("timestamp"),
                note_type=initial_note_data.get("note_type", "maintenance"),
                problem=initial_note_data.get("problem", ""),
                root_cause=initial_note_data.get("root_cause", ""),
                action_taken=initial_note_data.get("action_taken", ""),
                parts_consumed=initial_note_data.get("parts_consumed", ""),
                quick_note=initial_note_data.get("quick_note", ""),
                work_status=initial_note_data.get("work_status", "Done"),
                severity=initial_note_data.get("severity", "Routine"),
                service_type=initial_note_data.get("service_type", "Corrective Repair"),
                technician=initial_note_data.get("technician", "")
            )
        elif initial_note and str(initial_note).strip():
            item.add_note(initial_note)

        self.items.append(item)
        self.update_next_queue_id_from_items()
        self.is_dirty = True
        return item

    def update_item(
        self,
        item_id: str,
        moc_number: str = None,
        st_number: str = None,
        item_name: str = None,
        make_and_model: str = None,
        status: str = None,
        department: str = None,
        category: str = None,
        device_type: str = None,
        custom_fields: dict = None,
        queue_number: str = None
    ) -> WorkItem:
        """Updates attributes of an existing item."""
        item = self.get_item_by_id(item_id)
        if not item:
            raise KeyError(f"Item not found: {item_id}")

        if queue_number is not None:
            item.queue_number = queue_number.strip()
            self.update_next_queue_id_from_items()
        if moc_number is not None:
            item.moc_number = moc_number.strip()
        if st_number is not None:
            item.st_number = st_number.strip()
        if item_name is not None:
            item.item_name = item_name.strip()
        if make_and_model is not None:
            item.make_and_model = make_and_model.strip()
        if status is not None:
            item.status = "Active" if str(status).strip().lower() in ("active", "true", "1") else "Inactive"
        if department is not None:
            item.department = department.strip()
        if category is not None:
            item.category = str(category).strip() or "General"
        if device_type is not None:
            item.device_type = str(device_type).strip() or "Unspecified"
        if custom_fields is not None:
            item.custom_fields.update(custom_fields)

        item.touch()
        self.is_dirty = True
        return item

    def delete_item(self, item_id: str) -> bool:
        """Removes an item from the database."""
        before = len(self.items)
        self.items = [it for it in self.items if it.id != item_id]
        if len(self.items) < before:
            self.update_next_queue_id_from_items()
            self.is_dirty = True
            return True
        return False

    def get_item_by_id(self, item_id: str) -> WorkItem:
        """Finds item by unique ID."""
        for it in self.items:
            if it.id == item_id:
                return it
        return None

    def toggle_status(self, item_id: str) -> str:
        """Toggles status between Active and Inactive."""
        item = self.get_item_by_id(item_id)
        if item:
            item.status = "Inactive" if item.status == "Active" else "Active"
            item.touch()
            self.is_dirty = True
            return item.status
        return None

    # ==========================================================================
    # SERVICE LOG OPERATIONS
    # ==========================================================================
    def add_service_note(
        self,
        item_id: str,
        note_text: str = "",
        timestamp: str = None,
        note_type: str = "maintenance",
        problem: str = "",
        root_cause: str = "",
        action_taken: str = "",
        parts_consumed: str = "",
        quick_note: str = "",
        work_status: str = "Done",
        severity: str = "Routine",
        service_type: str = "Corrective Repair",
        technician: str = ""
    ) -> ServiceNote:
        """Adds a maintenance note or quick note to an item's service log."""
        item = self.get_item_by_id(item_id)
        if not item:
            raise KeyError(f"Item not found: {item_id}")
        note = item.add_note(
            note_text=note_text,
            timestamp=timestamp,
            note_type=note_type,
            problem=problem,
            root_cause=root_cause,
            action_taken=action_taken,
            parts_consumed=parts_consumed,
            quick_note=quick_note,
            work_status=work_status,
            severity=severity,
            service_type=service_type,
            technician=technician
        )
        self.is_dirty = True
        return note

    def delete_service_note(self, item_id: str, note_id: str) -> bool:
        """Deletes a maintenance note from an item's service log."""
        item = self.get_item_by_id(item_id)
        if not item:
            return False
        res = item.delete_note(note_id)
        if res:
            self.is_dirty = True
        return res

    def update_service_note(
        self,
        item_id: str,
        note_id: str,
        note_text: str = None,
        timestamp: str = None,
        note_type: str = None,
        problem: str = None,
        root_cause: str = None,
        action_taken: str = None,
        parts_consumed: str = None,
        quick_note: str = None,
        work_status: str = None,
        severity: str = None,
        service_type: str = None,
        technician: str = None
    ) -> bool:
        """Updates an existing maintenance note or quick note in an item's service log."""
        item = self.get_item_by_id(item_id)
        if not item:
            return False
        res = item.edit_note(
            note_id=note_id,
            note_text=note_text,
            timestamp=timestamp,
            note_type=note_type,
            problem=problem,
            root_cause=root_cause,
            action_taken=action_taken,
            parts_consumed=parts_consumed,
            quick_note=quick_note,
            work_status=work_status,
            severity=severity,
            service_type=service_type,
            technician=technician
        )
        if res:
            self.is_dirty = True
        return res

    # ==========================================================================
    # DYNAMIC CUSTOM COLUMNS
    # ==========================================================================
    def add_custom_column(self, name: str, default_val: str = "") -> dict:
        """Adds a new user-defined column. Automatically populates all existing items."""
        name = name.strip()
        if not name:
            raise ValueError("Column name cannot be empty")

        for col in self.custom_columns:
            if col["name"].lower() == name.lower():
                raise ValueError(f"Column '{name}' already exists.")

        col_id = "col_" + str(uuid.uuid4())[:8]
        col_def = {
            "id": col_id,
            "name": name,
            "default_val": default_val
        }
        self.custom_columns.append(col_def)

        for it in self.items:
            if col_id not in it.custom_fields:
                it.custom_fields[col_id] = default_val

        self.is_dirty = True
        return col_def

    def remove_custom_column(self, col_id: str) -> bool:
        """Removes a custom column definition and deletes its field from all items."""
        before = len(self.custom_columns)
        self.custom_columns = [c for c in self.custom_columns if c["id"] != col_id]
        if len(self.custom_columns) < before:
            for it in self.items:
                it.custom_fields.pop(col_id, None)
            self.is_dirty = True
            return True
        return False

    def rename_custom_column(self, col_id: str, new_name: str) -> bool:
        """Renames a custom column display label."""
        new_name = new_name.strip()
        if not new_name:
            raise ValueError("Column name cannot be empty")
        for col in self.custom_columns:
            if col["id"] == col_id:
                col["name"] = new_name
                self.is_dirty = True
                return True
        return False

    # ==========================================================================
    # QUERYING, SEARCHING & FILTERING
    # ==========================================================================
    def get_departments(self) -> list:
        """Returns sorted list of unique department names currently in use."""
        depts = {it.department for it in self.items if it.department}
        return sorted(list(depts))

    def get_categories(self) -> list:
        """Returns sorted list of unique categories in the database or saved by the user."""
        cats = set()
        for c in getattr(self, "categories", []):
            if c and c.strip():
                cats.add(c.strip())
        for it in self.items:
            c = getattr(it, "category", "")
            if c and c.strip():
                cats.add(c.strip())
        return sorted(list(cats))

    def get_device_types(self) -> list:
        """Returns sorted list of unique device types in the database or saved by the user."""
        types = set()
        for d in getattr(self, "device_types", []):
            if d and d.strip():
                types.add(d.strip())
        for it in self.items:
            dt = getattr(it, "device_type", "")
            if dt and dt.strip():
                types.add(dt.strip())
        return sorted(list(types))

    def get_technicians(self) -> list:
        """Returns sorted list of unique technicians recorded across all items, service notes, and presets."""
        techs = set()
        for t in getattr(self, "technicians", []):
            if t and t.strip():
                techs.add(t.strip())
        for it in self.items:
            for note in it.service_log:
                t = getattr(note, "technician", None)
                if t and t.strip():
                    techs.add(t.strip())
        return sorted(list(techs))

    def add_category(self, cat: str):
        if cat and cat.strip() and cat.strip() not in self.categories:
            self.categories.append(cat.strip())
            self.is_dirty = True

    def add_device_type(self, dtype: str):
        if dtype and dtype.strip() and dtype.strip() not in self.device_types:
            self.device_types.append(dtype.strip())
            self.is_dirty = True

    def add_technician(self, tech: str):
        if tech and tech.strip() and tech.strip() not in self.technicians:
            self.technicians.append(tech.strip())
            self.is_dirty = True

    def get_task_presets(self) -> list:
        """Returns list of user-defined task presets."""
        return getattr(self, "task_presets", [])

    def add_task_preset(self, preset: dict):
        if preset and preset.get("title"):
            if not hasattr(self, "task_presets") or not isinstance(self.task_presets, list):
                self.task_presets = []
            self.task_presets.append(preset)
            self.is_dirty = True

    def delete_task_preset(self, title: str) -> bool:
        if hasattr(self, "task_presets"):
            before = len(self.task_presets)
            self.task_presets = [p for p in self.task_presets if p.get("title") != title]
            if len(self.task_presets) < before:
                self.is_dirty = True
                return True
        return False

    def filter_items(
        self,
        query: str = "",
        status_filter: str = "All",
        department_filter: str = "All",
        device_type_filter: str = "All",
        category_filter: str = "All",
        work_status_filter: str = "All",
        sort_by: str = "queue_number",
        sort_desc: bool = False
    ) -> list:
        """Filters and sorts items based on search query, status, department, device type, and category."""
        results = []
        q_clean = query.strip().lower()

        for it in self.items:
            # 1. Status Filter
            if status_filter != "All" and it.status != status_filter:
                continue

            # 2. Department Filter
            if department_filter != "All" and it.department != department_filter:
                continue

            # 3. Device Type Filter
            if device_type_filter != "All" and getattr(it, "device_type", "") != device_type_filter:
                continue

            # 4. Category Filter
            if category_filter != "All" and getattr(it, "category", "") != category_filter:
                continue

            # 5. Work Status Filter (Done, Working, Stuck, Idle)
            if work_status_filter != "All" and it.get_work_status() != work_status_filter:
                continue

            # 6. Query Text Search across all core, custom, and note attributes
            if q_clean:
                fields_to_check = [
                    it.queue_number,
                    it.moc_number,
                    it.st_number,
                    it.item_name,
                    it.make_and_model,
                    getattr(it, "device_type", ""),
                    getattr(it, "category", ""),
                    it.status,
                    it.get_work_status(),
                    it.department
                ]
                for val in it.custom_fields.values():
                    fields_to_check.append(str(val))
                for n in it.service_log:
                    fields_to_check.extend([
                        n.note,
                        n.problem,
                        n.root_cause,
                        n.action_taken,
                        n.parts_consumed,
                        n.quick_note,
                        getattr(n, "work_status", ""),
                        getattr(n, "severity", ""),
                        getattr(n, "service_type", ""),
                        getattr(n, "technician", "")
                    ])

                matched = any(q_clean in str(val).lower() for val in fields_to_check)
                if not matched:
                    continue

            results.append(it)

        # 7. Sorting
        def sort_key(item: WorkItem):
            if sort_by == "queue_number":
                q = item.queue_number
                if q.startswith(self.queue_prefix):
                    s = q[len(self.queue_prefix):]
                    if s.isdigit():
                        return (0, int(s))
                return (1, q.lower())
            elif sort_by == "moc_number":
                return item.moc_number.lower()
            elif sort_by == "st_number":
                return item.st_number.lower()
            elif sort_by == "item_name":
                return item.item_name.lower()
            elif sort_by == "make_and_model":
                return item.make_and_model.lower()
            elif sort_by == "device_type":
                return getattr(item, "device_type", "").lower()
            elif sort_by == "category":
                return getattr(item, "category", "").lower()
            elif sort_by == "status":
                return item.status.lower()
            elif sort_by == "work_status":
                return item.get_work_status().lower()
            elif sort_by == "department":
                return item.department.lower()
            elif sort_by == "service_log":
                return len(item.service_log)
            elif sort_by.startswith("col_"):
                return str(item.custom_fields.get(sort_by, "")).lower()
            elif sort_by == "created_at":
                return item.created_at
            elif sort_by == "updated_at":
                return item.updated_at
            return item.queue_number.lower()

        results.sort(key=sort_key, reverse=sort_desc)
        return results

    def get_metrics(self) -> dict:
        """Returns database KPI statistics including work status counts (Done, Working, Stuck, Idle)."""
        total = len(self.items)
        active = sum(1 for it in self.items if it.status == "Active")
        inactive = total - active
        total_notes = sum(len(it.service_log) for it in self.items)
        total_maint = sum(sum(1 for n in it.service_log if n.note_type != "quick") for it in self.items)
        total_quick = sum(sum(1 for n in it.service_log if n.note_type == "quick") for it in self.items)

        working_cnt = sum(1 for it in self.items if it.get_work_status() == "Working")
        stuck_cnt = sum(1 for it in self.items if it.get_work_status() == "Stuck")
        done_cnt = sum(1 for it in self.items if it.get_work_status() == "Done")
        idle_cnt = sum(1 for it in self.items if it.get_work_status() == "Idle")

        return {
            "total_items": total,
            "active_items": active,
            "inactive_items": inactive,
            "total_notes": total_notes,
            "total_maintenance_notes": total_maint,
            "total_quick_notes": total_quick,
            "working_count": working_cnt,
            "stuck_count": stuck_cnt,
            "done_count": done_cnt,
            "idle_count": idle_cnt
        }

    def get_work_analytics(
        self,
        period: str = "monthly",
        filter_device_type: str = "All",
        filter_category: str = "All",
        filter_dept: str = "All",
        filter_status: str = "All"
    ) -> dict:
        """
        Calculates multi-dimensional work analytics across daily, weekly, monthly, quarterly, and yearly timelines.
        Includes device types, categories, problems, parts, and work states (Done, Working, Stuck, Idle).
        """
        period_norm = str(period or "monthly").lower().strip()
        if period_norm not in ("daily", "weekly", "monthly", "quarterly", "yearly"):
            period_norm = "monthly"

        # 1. Filter Items
        filtered_items = []
        for it in self.items:
            if filter_device_type != "All" and getattr(it, "device_type", "") != filter_device_type:
                continue
            if filter_category != "All" and getattr(it, "category", "") != filter_category:
                continue
            if filter_dept != "All" and it.department != filter_dept:
                continue
            if filter_status != "All" and it.get_work_status() != filter_status and it.status != filter_status:
                continue
            filtered_items.append(it)

        total_items = len(filtered_items)
        active_items = sum(1 for it in filtered_items if it.status == "Active")
        inactive_items = total_items - active_items

        all_notes = []
        for it in filtered_items:
            for n in it.service_log:
                all_notes.append((it, n))

        total_notes = len(all_notes)
        maint_notes_count = sum(1 for _, n in all_notes if n.note_type != "quick")
        quick_notes_count = sum(1 for _, n in all_notes if n.note_type == "quick")
        parts_consumed_count = sum(1 for _, n in all_notes if n.parts_consumed)

        # Work status counts across items
        item_working = sum(1 for it in filtered_items if it.get_work_status() == "Working")
        item_stuck = sum(1 for it in filtered_items if it.get_work_status() == "Stuck")
        item_done = sum(1 for it in filtered_items if it.get_work_status() == "Done")
        item_idle = sum(1 for it in filtered_items if it.get_work_status() == "Idle")

        # 2. Multi-Period Timeline Aggregation (Daily, Weekly, Monthly, Quarterly, Yearly)
        def get_bucket_key(ts: str, mode: str) -> str:
            if not ts or len(ts) < 4:
                return "Unknown"
            year = ts[:4]
            if mode == "daily":
                return ts[:10] if len(ts) >= 10 else year
            elif mode == "weekly":
                if len(ts) >= 10:
                    try:
                        dt = datetime.strptime(ts[:10], "%Y-%m-%d")
                        iso_y, iso_w, _ = dt.isocalendar()
                        return f"{iso_y}-W{iso_w:02d}"
                    except Exception:
                        pass
                return ts[:7] + " W"
            elif mode == "quarterly":
                try:
                    month = int(ts[5:7]) if len(ts) >= 7 else 1
                    q = (month - 1) // 3 + 1
                    return f"{year}-Q{q}"
                except Exception:
                    return f"{year}-Q1"
            elif mode == "yearly":
                return year
            else:  # monthly
                return ts[:7] if len(ts) >= 7 else year

        timeline_data = defaultdict(lambda: {
            "maintenance": 0,
            "quick": 0,
            "total": 0,
            "done": 0,
            "working": 0,
            "stuck": 0,
            "idle": 0,
            "parts": 0,
            "device_types": defaultdict(int),
            "problems": defaultdict(int)
        })

        timeline_monthly = defaultdict(lambda: {"maintenance": 0, "quick": 0, "total": 0})

        for it, n in all_notes:
            b_key = get_bucket_key(n.timestamp, period_norm)
            mo_key = get_bucket_key(n.timestamp, "monthly")

            # Update chosen period bucket
            entry = timeline_data[b_key]
            if n.note_type == "quick":
                entry["quick"] += 1
            else:
                entry["maintenance"] += 1
                ws = getattr(n, "work_status", "Done")
                if ws == "Working":
                    entry["working"] += 1
                elif ws == "Stuck":
                    entry["stuck"] += 1
                elif ws == "Idle":
                    entry["idle"] += 1
                else:
                    entry["done"] += 1
            entry["total"] += 1

            if n.parts_consumed:
                entry["parts"] += 1

            dtype = getattr(it, "device_type", "Unspecified")
            entry["device_types"][dtype] += 1

            if n.problem:
                entry["problems"][n.problem] += 1

            # Update backward-compatible monthly map
            if n.note_type == "quick":
                timeline_monthly[mo_key]["quick"] += 1
            else:
                timeline_monthly[mo_key]["maintenance"] += 1
            timeline_monthly[mo_key]["total"] += 1

        sorted_timeline = sorted(timeline_data.items(), key=lambda x: x[0])
        sorted_monthly = sorted(timeline_monthly.items(), key=lambda x: x[0])

        # 3. Device Type Intelligence
        dev_work = defaultdict(lambda: {
            "items": 0,
            "maintenance": 0,
            "quick": 0,
            "total": 0,
            "done": 0,
            "working": 0,
            "stuck": 0,
            "idle": 0,
            "parts": 0,
            "problems": defaultdict(int)
        })
        for it in filtered_items:
            dtype = getattr(it, "device_type", "Unspecified") or "Unspecified"
            dev_work[dtype]["items"] += 1
            ws_item = it.get_work_status()
            if ws_item == "Working":
                dev_work[dtype]["working"] += 1
            elif ws_item == "Stuck":
                dev_work[dtype]["stuck"] += 1
            elif ws_item == "Idle":
                dev_work[dtype]["idle"] += 1
            else:
                dev_work[dtype]["done"] += 1

            for n in it.service_log:
                if n.note_type == "quick":
                    dev_work[dtype]["quick"] += 1
                else:
                    dev_work[dtype]["maintenance"] += 1
                dev_work[dtype]["total"] += 1
                if n.parts_consumed:
                    dev_work[dtype]["parts"] += 1
                if n.problem:
                    dev_work[dtype]["problems"][n.problem] += 1

        sorted_dev_work = sorted(dev_work.items(), key=lambda x: x[1]["total"], reverse=True)

        # 4. Category Intelligence
        cat_work = defaultdict(lambda: {
            "items": 0,
            "maintenance": 0,
            "quick": 0,
            "total": 0,
            "parts": 0
        })
        for it in filtered_items:
            cat = getattr(it, "category", "General") or "General"
            cat_work[cat]["items"] += 1
            for n in it.service_log:
                if n.note_type == "quick":
                    cat_work[cat]["quick"] += 1
                else:
                    cat_work[cat]["maintenance"] += 1
                cat_work[cat]["total"] += 1
                if n.parts_consumed:
                    cat_work[cat]["parts"] += 1

        sorted_cat_work = sorted(cat_work.items(), key=lambda x: x[1]["total"], reverse=True)

        # 5. Work by Department
        dept_work = defaultdict(lambda: {
            "maintenance": 0,
            "quick": 0,
            "total": 0,
            "items": 0,
            "working": 0,
            "stuck": 0,
            "done": 0,
            "idle": 0
        })
        for it in filtered_items:
            d = it.department or "Unassigned"
            dept_work[d]["items"] += 1
            ws = it.get_work_status()
            if ws == "Working":
                dept_work[d]["working"] += 1
            elif ws == "Stuck":
                dept_work[d]["stuck"] += 1
            elif ws == "Idle":
                dept_work[d]["idle"] += 1
            else:
                dept_work[d]["done"] += 1

            for n in it.service_log:
                if n.note_type == "quick":
                    dept_work[d]["quick"] += 1
                else:
                    dept_work[d]["maintenance"] += 1
                dept_work[d]["total"] += 1

        sorted_dept_work = sorted(
            dept_work.items(),
            key=lambda x: x[1]["total"],
            reverse=True
        )

        # 6. Equipment Service Intensity (Top Serviced Items)
        item_intensity = []
        for it in filtered_items:
            m_cnt = sum(1 for n in it.service_log if n.note_type != "quick")
            q_cnt = sum(1 for n in it.service_log if n.note_type == "quick")
            p_cnt = sum(1 for n in it.service_log if n.parts_consumed)
            item_intensity.append({
                "id": it.id,
                "queue_number": it.queue_number,
                "item_name": it.item_name,
                "device_type": getattr(it, "device_type", "Unspecified"),
                "category": getattr(it, "category", "General"),
                "department": it.department,
                "status": it.status,
                "work_status": it.get_work_status(),
                "total_notes": len(it.service_log),
                "maintenance_notes": m_cnt,
                "quick_notes": q_cnt,
                "parts_actions": p_cnt
            })
        item_intensity.sort(key=lambda x: x["total_notes"], reverse=True)

        # 7. Problem / Diagnostic Breakdown
        problems_map = defaultdict(lambda: {"count": 0, "device_types": set(), "latest": ""})
        for it, n in all_notes:
            if n.problem:
                p_clean = n.problem.strip().title()
                problems_map[p_clean]["count"] += 1
                problems_map[p_clean]["device_types"].add(getattr(it, "device_type", "Unspecified"))
                if not problems_map[p_clean]["latest"] or n.timestamp > problems_map[p_clean]["latest"]:
                    problems_map[p_clean]["latest"] = n.timestamp

        sorted_problems = sorted(
            [(p, d["count"], sorted(list(d["device_types"])), d["latest"]) for p, d in problems_map.items()],
            key=lambda x: x[1],
            reverse=True
        )

        # 8. Root Cause Frequencies
        root_causes = defaultdict(int)
        for _, n in all_notes:
            rc = n.root_cause.strip()
            if rc:
                root_causes[rc.title()] += 1
        sorted_root_causes = sorted(root_causes.items(), key=lambda x: x[1], reverse=True)

        # 9. Parts Consumed Breakdown & Frequency
        parts_list = []
        parts_freq = defaultdict(lambda: {"count": 0, "device_types": set()})
        for it, n in all_notes:
            if n.parts_consumed:
                p_text = n.parts_consumed.strip()
                dtype = getattr(it, "device_type", "Unspecified")
                parts_list.append({
                    "queue_number": it.queue_number,
                    "item_name": it.item_name,
                    "device_type": dtype,
                    "category": getattr(it, "category", "General"),
                    "parts": p_text,
                    "timestamp": n.timestamp,
                    "problem": n.problem,
                    "work_status": getattr(n, "work_status", "Done")
                })
                parts_freq[p_text]["count"] += 1
                parts_freq[p_text]["device_types"].add(dtype)

        sorted_parts_freq = sorted(
            [(p, d["count"], sorted(list(d["device_types"]))) for p, d in parts_freq.items()],
            key=lambda x: x[1],
            reverse=True
        )

        return {
            "period": period_norm,
            "total_items": total_items,
            "active_items": active_items,
            "inactive_items": inactive_items,
            "item_working": item_working,
            "item_stuck": item_stuck,
            "item_done": item_done,
            "item_idle": item_idle,
            "total_notes": total_notes,
            "maintenance_notes_count": maint_notes_count,
            "quick_notes_count": quick_notes_count,
            "parts_consumed_count": parts_consumed_count,
            "timeline": sorted_timeline,
            "timeline_monthly": sorted_monthly,  # Backward compatibility
            "device_type_work": sorted_dev_work,
            "category_work": sorted_cat_work,
            "dept_work": sorted_dept_work,
            "item_intensity": item_intensity,
            "problems_analysis": sorted_problems,
            "root_causes": sorted_root_causes,
            "parts_list": parts_list,
            "parts_frequency": sorted_parts_freq,
            "work_status_summary": {
                "Done": item_done,
                "Working": item_working,
                "Stuck": item_stuck,
                "Idle": item_idle
            }
        }

    # ==========================================================================
    # CSV EXPORT
    # ==========================================================================
    def export_csv(self, file_path: str):
        """Exports the entire database or items to a CSV file."""
        import csv

        headers = [
            "Queue Number",
            "MOC Number",
            "ST Number",
            "Item Name",
            "Make and Model",
            "Device Type",
            "Category",
            "Status",
            "Current State",
            "Department",
            "Total Notes",
            "Maintenance Notes",
            "Quick Notes",
            "Latest Problem",
            "Latest Action",
            "Latest Parts Consumed",
            "Latest State"
        ]
        custom_cols = self.custom_columns
        for c in custom_cols:
            headers.append(c["name"])
        headers.extend(["Created At", "Updated At", "All Service Notes"])

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

            for it in self.items:
                m_notes = [n for n in it.service_log if n.note_type != "quick"]
                q_notes = [n for n in it.service_log if n.note_type == "quick"]
                latest_m = m_notes[-1] if m_notes else None
                latest_note = it.service_log[-1] if it.service_log else None

                all_notes_str = " | ".join(
                    f"[{n.timestamp} - {n.note_type.upper()} | {getattr(n, 'work_status', 'Done')} | {getattr(n, 'severity', 'Routine')}] {n.note}"
                    for n in it.service_log
                )
                row = [
                    it.queue_number,
                    it.moc_number,
                    it.st_number,
                    it.item_name,
                    it.make_and_model,
                    getattr(it, "device_type", "Unspecified"),
                    getattr(it, "category", "General"),
                    it.status,
                    it.get_work_status(),
                    it.department,
                    len(it.service_log),
                    len(m_notes),
                    len(q_notes),
                    latest_m.problem if latest_m else (latest_note.note if latest_note else ""),
                    latest_m.action_taken if latest_m else "",
                    latest_m.parts_consumed if latest_m else "",
                    getattr(latest_note, "work_status", "Done") if latest_note else it.get_work_status()
                ]
                for c in custom_cols:
                    row.append(it.custom_fields.get(c["id"], ""))
                row.extend([it.created_at, it.updated_at, all_notes_str])
                writer.writerow(row)
