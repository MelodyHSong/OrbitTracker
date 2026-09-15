# 🪐 OrbitTracker — Database & Persistence Layer
# Author: MelodyHSong
# File Name: database.py
# Description: JSON-backed database manager with auto-generated Queue Numbers,
#              dynamic custom columns, service log tracking, and search/filtering.

import os
import json
import uuid
from datetime import datetime


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
        quick_note: str = ""
    ):
        self.id = note_id or str(uuid.uuid4())[:8]
        self.timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.note_type = "quick" if str(note_type).strip().lower() == "quick" else "maintenance"
        self.problem = str(problem or "").strip()
        self.root_cause = str(root_cause or "").strip()
        self.action_taken = str(action_taken or "").strip()
        self.parts_consumed = str(parts_consumed or "").strip()
        self.quick_note = str(quick_note or "").strip()

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
        # If explicitly marked as quick note or has quick_note without problem
        if data.get("note_type") == "quick" or ("quick_note" in data and not data.get("problem")):
            return cls(
                note=raw_note,
                timestamp=data.get("timestamp"),
                note_id=data.get("id"),
                note_type="quick",
                quick_note=data.get("quick_note", raw_note)
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
                quick_note=data.get("quick_note", "")
            )

        # Legacy database entry (only 'note' key exists):
        return cls(
            note=raw_note,
            timestamp=data.get("timestamp"),
            note_id=data.get("id"),
            note_type="maintenance",
            problem=raw_note
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
        self.custom_fields = dict(custom_fields) if custom_fields else {}
        self.service_log = [
            note if isinstance(note, ServiceNote) else ServiceNote.from_dict(note)
            for note in (service_log or [])
        ]
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.created_at = created_at or now_str
        self.updated_at = updated_at or now_str

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
        quick_note: str = ""
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
                quick_note=q_txt
            )
        else:
            note = ServiceNote(
                note=note_text,
                timestamp=timestamp,
                note_type=note_type,
                problem=problem or note_text,
                root_cause=root_cause,
                action_taken=action_taken,
                parts_consumed=parts_consumed
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
        quick_note: str = None
    ) -> bool:
        """Edits an existing maintenance note or quick note in the service log."""
        for note in self.service_log:
            if note.id == note_id:
                if timestamp:
                    note.timestamp = timestamp
                if note_type is not None:
                    note.note_type = note_type
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

    def __init__(self, db_path: str = None):
        self.db_path = os.path.abspath(db_path or self.DEFAULT_DB_NAME)
        self.app_name = "OrbitTracker"
        self.version = "1.0.3-dev"
        self.queue_prefix = "Q-"
        self.next_queue_id = 1
        self.custom_columns = []  # List of {"id": str, "name": str, "default_val": str}
        self.items = []           # List of WorkItem instances
        self.is_dirty = False
        self.last_saved = None

        self.load()

    def create_default_schema(self):
        """Initializes empty database schema."""
        self.queue_prefix = "Q-"
        self.next_queue_id = 1
        self.custom_columns = []
        self.items = []
        self.is_dirty = False

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
            self.version = data.get("version", "1.0.3-dev")
            self.queue_prefix = data.get("queue_prefix", "Q-")
            self.next_queue_id = int(data.get("next_queue_id", 1))
            self.custom_columns = data.get("custom_columns", [])

            items_raw = data.get("items", [])
            self.items = [WorkItem.from_dict(it) for it in items_raw]
            self.update_next_queue_id_from_items()
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

        # Initialize any custom fields with default values
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
                quick_note=initial_note_data.get("quick_note", "")
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
        quick_note: str = ""
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
            quick_note=quick_note
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
        quick_note: str = None
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
            quick_note=quick_note
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

        # Check for duplicate names
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

        # Propagate default to all existing items
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

    def filter_items(
        self,
        query: str = "",
        status_filter: str = "All",
        department_filter: str = "All",
        sort_by: str = "queue_number",
        sort_desc: bool = False
    ) -> list:
        """Filters and sorts items based on search query, status, and department."""
        results = []
        q_clean = query.strip().lower()

        for it in self.items:
            # 1. Status Filter
            if status_filter != "All" and it.status != status_filter:
                continue

            # 2. Department Filter
            if department_filter != "All" and it.department != department_filter:
                continue

            # 3. Query Text Search
            if q_clean:
                # Check standard fields
                fields_to_check = [
                    it.queue_number,
                    it.moc_number,
                    it.st_number,
                    it.item_name,
                    it.make_and_model,
                    it.status,
                    it.department
                ]
                # Check custom fields
                for val in it.custom_fields.values():
                    fields_to_check.append(str(val))
                # Check notes
                for n in it.service_log:
                    fields_to_check.extend([
                        n.note,
                        n.problem,
                        n.root_cause,
                        n.action_taken,
                        n.parts_consumed,
                        n.quick_note
                    ])

                matched = any(q_clean in str(val).lower() for val in fields_to_check)
                if not matched:
                    continue

            results.append(it)

        # 4. Sorting
        def sort_key(item: WorkItem):
            if sort_by == "queue_number":
                # Try natural sorting for Q-xxx
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
            elif sort_by == "status":
                return item.status.lower()
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
        """Returns database KPI statistics."""
        total = len(self.items)
        active = sum(1 for it in self.items if it.status == "Active")
        inactive = total - active
        total_notes = sum(len(it.service_log) for it in self.items)
        total_maint = sum(sum(1 for n in it.service_log if n.note_type != "quick") for it in self.items)
        total_quick = sum(sum(1 for n in it.service_log if n.note_type == "quick") for it in self.items)
        return {
            "total_items": total,
            "active_items": active,
            "inactive_items": inactive,
            "total_notes": total_notes,
            "total_maintenance_notes": total_maint,
            "total_quick_notes": total_quick
        }

    def get_work_analytics(self) -> dict:
        """Calculates comprehensive work performance and maintenance statistics across all work items."""
        from collections import defaultdict

        total_items = len(self.items)
        active_items = sum(1 for it in self.items if it.status == "Active")
        inactive_items = total_items - active_items

        all_notes = []
        for it in self.items:
            for n in it.service_log:
                all_notes.append((it, n))

        total_notes = len(all_notes)
        maint_notes_count = sum(1 for _, n in all_notes if n.note_type != "quick")
        quick_notes_count = sum(1 for _, n in all_notes if n.note_type == "quick")
        parts_consumed_count = sum(1 for _, n in all_notes if n.parts_consumed)

        # 1. Timeline Activity by Month (e.g. '2026-09')
        timeline_monthly = defaultdict(lambda: {"maintenance": 0, "quick": 0, "total": 0})
        for _, n in all_notes:
            month_key = n.timestamp[:7] if len(n.timestamp) >= 7 else "Unknown"
            if n.note_type == "quick":
                timeline_monthly[month_key]["quick"] += 1
            else:
                timeline_monthly[month_key]["maintenance"] += 1
            timeline_monthly[month_key]["total"] += 1
        sorted_timeline = sorted(timeline_monthly.items(), key=lambda x: x[0])

        # 2. Work by Department
        dept_work = defaultdict(lambda: {"maintenance": 0, "quick": 0, "items": 0})
        for it in self.items:
            d = it.department or "Unassigned"
            dept_work[d]["items"] += 1
            for n in it.service_log:
                if n.note_type == "quick":
                    dept_work[d]["quick"] += 1
                else:
                    dept_work[d]["maintenance"] += 1
        sorted_dept_work = sorted(
            dept_work.items(),
            key=lambda x: (x[1]["maintenance"] + x[1]["quick"]),
            reverse=True
        )

        # 3. Equipment Service Intensity (Top Serviced Items)
        item_intensity = []
        for it in self.items:
            m_cnt = sum(1 for n in it.service_log if n.note_type != "quick")
            q_cnt = sum(1 for n in it.service_log if n.note_type == "quick")
            p_cnt = sum(1 for n in it.service_log if n.parts_consumed)
            item_intensity.append({
                "id": it.id,
                "queue_number": it.queue_number,
                "item_name": it.item_name,
                "department": it.department,
                "status": it.status,
                "total_notes": len(it.service_log),
                "maintenance_notes": m_cnt,
                "quick_notes": q_cnt,
                "parts_actions": p_cnt
            })
        item_intensity.sort(key=lambda x: x["total_notes"], reverse=True)

        # 4. Root Cause Frequencies
        root_causes = defaultdict(int)
        for _, n in all_notes:
            rc = n.root_cause.strip()
            if rc:
                root_causes[rc.title()] += 1
        sorted_root_causes = sorted(root_causes.items(), key=lambda x: x[1], reverse=True)

        # 5. Parts Consumed Breakdown
        parts_list = []
        for it, n in all_notes:
            if n.parts_consumed:
                parts_list.append({
                    "queue_number": it.queue_number,
                    "item_name": it.item_name,
                    "parts": n.parts_consumed,
                    "timestamp": n.timestamp
                })

        return {
            "total_items": total_items,
            "active_items": active_items,
            "inactive_items": inactive_items,
            "total_notes": total_notes,
            "maintenance_notes_count": maint_notes_count,
            "quick_notes_count": quick_notes_count,
            "parts_consumed_count": parts_consumed_count,
            "timeline_monthly": sorted_timeline,
            "dept_work": sorted_dept_work,
            "item_intensity": item_intensity,
            "root_causes": sorted_root_causes,
            "parts_list": parts_list
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
            "Status",
            "Department",
            "Total Notes",
            "Maintenance Notes",
            "Quick Notes",
            "Latest Problem",
            "Latest Action",
            "Latest Parts Consumed"
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

                all_notes_str = " | ".join(
                    f"[{n.timestamp} - {n.note_type.upper()}] {n.note}" for n in it.service_log
                )
                row = [
                    it.queue_number,
                    it.moc_number,
                    it.st_number,
                    it.item_name,
                    it.make_and_model,
                    it.status,
                    it.department,
                    len(it.service_log),
                    len(m_notes),
                    len(q_notes),
                    latest_m.problem if latest_m else (it.service_log[-1].note if it.service_log else ""),
                    latest_m.action_taken if latest_m else "",
                    latest_m.parts_consumed if latest_m else ""
                ]
                for c in custom_cols:
                    row.append(it.custom_fields.get(c["id"], ""))
                row.extend([it.created_at, it.updated_at, all_notes_str])
                writer.writerow(row)
