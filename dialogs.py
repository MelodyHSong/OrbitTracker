# 🪐 OrbitTracker — Modal Dialogs
# Author: MelodyHSong
# File Name: dialogs.py
# Description: Cosmic dark themed modal dialogs for Adding/Editing Work Items,
#              overhauled Service Maintenance Logs (Done, Working, Stuck, Idle, Presets),
#              Custom Columns, and Multi-Period Work Analytics Dashboard.

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Theme Constants matching OrbitTracker aesthetic
BG_MAIN = "#0d1117"
BG_PANEL = "#161b22"
BG_SURFACE = "#21262d"
BG_ACTIVE = "#30363d"
BORDER_COLOR = "#30363d"
BORDER_ACTIVE = "#58a6ff"

TEXT_PRIMARY = "#e2e8f0"
TEXT_MUTED = "#8b949e"
TEXT_DIM = "#586069"

ACCENT_CYAN = "#58a6ff"
ACCENT_GOLD = "#f2cc60"
ACCENT_MINT = "#7ee787"
ACCENT_CORAL = "#f85149"

COLOR_WORKING = "#58a6ff"
COLOR_STUCK = "#f85149"
COLOR_DONE = "#7ee787"
COLOR_IDLE = "#f2cc60"

FONT_TITLE = ("Segoe UI", 12, "bold")
FONT_LABEL = ("Segoe UI", 9, "bold")
FONT_UI = ("Segoe UI", 9)
FONT_CODE = ("Consolas", 9)
FONT_CODE_BOLD = ("Consolas", 9, "bold")


def center_window_on_parent(window, parent, width=540, height=620):
    """Centers a modal window relative to its parent window."""
    parent.update_idletasks()
    p_x = parent.winfo_rootx()
    p_y = parent.winfo_rooty()
    p_w = parent.winfo_width()
    p_h = parent.winfo_height()

    pos_x = max(50, p_x + (p_w - width) // 2)
    pos_y = max(50, p_y + (p_h - height) // 2)

    window.geometry(f"{width}x{height}+{pos_x}+{pos_y}")


class BaseDialog(tk.Toplevel):
    """Base modal window with cosmic styling and focus grab."""
    def __init__(self, parent, title="OrbitTracker"):
        super().__init__(parent)
        self.parent = parent
        self.title(title)
        self.configure(bg=BG_MAIN)
        self.resizable(True, True)
        self.transient(parent)
        self.result = None

        # Bind Esc to close
        self.bind("<Escape>", lambda e: self.destroy())


class ItemDialog(BaseDialog):
    """Modal dialog for Adding a new Work Item or Editing an existing Work Item."""
    def __init__(self, parent, db, item=None, existing_depts=None):
        super().__init__(parent, title="Edit Work Item" if item else "Add New Work Item")
        self.db = db
        self.item = item
        self.existing_depts = existing_depts or db.get_departments()

        # Determine dimensions based on custom columns
        custom_count = len(db.custom_columns)
        base_h = 660 if item else 780
        target_h = min(860, base_h + custom_count * 38)
        center_window_on_parent(self, parent, width=620, height=target_h)

        self.custom_entries = {}
        self.build_ui()
        self.grab_set()
        self.focus_first_input()

    def build_ui(self):
        # Header banner
        header = tk.Frame(self, bg=BG_PANEL, height=52, highlightthickness=1, highlightbackground=BORDER_COLOR)
        header.pack(fill="x", padx=12, pady=(12, 8))
        header.pack_propagate(False)

        title_text = "🪐 EDIT WORK ITEM" if self.item else "🪐 ADD NEW WORK ITEM"
        lbl_title = tk.Label(header, text=title_text, font=FONT_TITLE, fg=ACCENT_CYAN, bg=BG_PANEL)
        lbl_title.pack(side="left", padx=14, pady=10)

        badge_txt = f"ID: {self.item.queue_number}" if self.item else f"Next: {self.db.peek_next_queue_number()}"
        lbl_badge = tk.Label(header, text=badge_txt, font=FONT_CODE, fg=ACCENT_GOLD, bg=BG_SURFACE, padx=8, pady=3)
        lbl_badge.pack(side="right", padx=14, pady=10)

        # Bottom Button Bar
        btn_bar = tk.Frame(self, bg=BG_PANEL, height=52, highlightthickness=1, highlightbackground=BORDER_COLOR)
        btn_bar.pack(side="bottom", fill="x", padx=12, pady=(4, 12))
        btn_bar.pack_propagate(False)

        btn_cancel = tk.Button(
            btn_bar,
            text="Cancel",
            font=FONT_UI,
            fg=TEXT_PRIMARY,
            bg=BG_SURFACE,
            activebackground=BG_ACTIVE,
            activeforeground=TEXT_PRIMARY,
            relief="flat",
            padx=14,
            pady=4,
            cursor="hand2",
            command=self.destroy
        )
        btn_cancel.pack(side="right", padx=10, pady=10)

        save_txt = "Save Changes" if self.item else "+ Add Work Item"
        btn_save = tk.Button(
            btn_bar,
            text=save_txt,
            font=("Segoe UI", 9, "bold"),
            fg=BG_MAIN,
            bg=ACCENT_CYAN,
            activebackground="#79c0ff",
            activeforeground=BG_MAIN,
            relief="flat",
            padx=16,
            pady=4,
            cursor="hand2",
            command=self.on_save
        )
        btn_save.pack(side="right", padx=4, pady=10)

        # Scrollable form container
        scroll_container = tk.Frame(self, bg=BG_MAIN)
        scroll_container.pack(side="top", fill="both", expand=True, padx=14, pady=4)

        canvas = tk.Canvas(scroll_container, bg=BG_MAIN, highlightthickness=0)
        v_scroll = ttk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)
        form_frame = tk.Frame(canvas, bg=BG_MAIN)

        form_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=form_frame, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width))

        canvas.configure(yscrollcommand=v_scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")

        # Row 1: Queue Number & Operational Status
        r1 = tk.Frame(form_frame, bg=BG_MAIN)
        r1.pack(fill="x", pady=4)

        f_q = tk.Frame(r1, bg=BG_MAIN)
        f_q.pack(side="left", fill="x", expand=True, padx=(0, 6))
        tk.Label(f_q, text="Queue Number (Auto-Generated)", font=FONT_LABEL, fg=TEXT_MUTED, bg=BG_MAIN).pack(anchor="w")
        self.entry_queue = tk.Entry(f_q, font=FONT_UI, bg=BG_SURFACE, fg=ACCENT_GOLD, insertbackground=TEXT_PRIMARY,
                                    relief="flat", highlightthickness=1, highlightbackground=BORDER_COLOR)
        self.entry_queue.pack(fill="x", pady=2, ipady=4)
        init_q = self.item.queue_number if self.item else self.db.peek_next_queue_number()
        self.entry_queue.insert(0, init_q)

        f_st = tk.Frame(r1, bg=BG_MAIN, width=160)
        f_st.pack(side="right", fill="x", padx=(6, 0))
        tk.Label(f_st, text="Record Status", font=FONT_LABEL, fg=TEXT_MUTED, bg=BG_MAIN).pack(anchor="w")
        self.status_var = tk.StringVar(value=self.item.status if self.item else "Active")
        self.cb_status = ttk.Combobox(f_st, textvariable=self.status_var, values=["Active", "Inactive"], state="readonly", font=FONT_UI)
        self.cb_status.pack(fill="x", pady=2, ipady=3)

        # Row 2: MOC Number & ST Number
        r2 = tk.Frame(form_frame, bg=BG_MAIN)
        r2.pack(fill="x", pady=4)

        f_moc = tk.Frame(r2, bg=BG_MAIN)
        f_moc.pack(side="left", fill="x", expand=True, padx=(0, 6))
        tk.Label(f_moc, text="MOC Number (Management of Change / Ticket)", font=FONT_LABEL, fg=TEXT_MUTED, bg=BG_MAIN).pack(anchor="w")
        self.entry_moc = tk.Entry(f_moc, font=FONT_UI, bg=BG_SURFACE, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                                  relief="flat", highlightthickness=1, highlightbackground=BORDER_COLOR)
        self.entry_moc.pack(fill="x", pady=2, ipady=4)
        if self.item:
            self.entry_moc.insert(0, self.item.moc_number)

        f_st_num = tk.Frame(r2, bg=BG_MAIN)
        f_st_num.pack(side="right", fill="x", expand=True, padx=(6, 0))
        tk.Label(f_st_num, text="ST Number (Service Tag #)", font=FONT_LABEL, fg=TEXT_MUTED, bg=BG_MAIN).pack(anchor="w")
        self.entry_st = tk.Entry(f_st_num, font=FONT_UI, bg=BG_SURFACE, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                                 relief="flat", highlightthickness=1, highlightbackground=BORDER_COLOR)
        self.entry_st.pack(fill="x", pady=2, ipady=4)
        if self.item:
            self.entry_st.insert(0, self.item.st_number)

        # Row 3: Item Name (Required)
        r3 = tk.Frame(form_frame, bg=BG_MAIN)
        r3.pack(fill="x", pady=4)
        tk.Label(r3, text="Item Name *", font=FONT_LABEL, fg=TEXT_MUTED, bg=BG_MAIN).pack(anchor="w")
        self.entry_name = tk.Entry(r3, font=FONT_UI, bg=BG_SURFACE, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                                   relief="flat", highlightthickness=1, highlightbackground=BORDER_COLOR)
        self.entry_name.pack(fill="x", pady=2, ipady=4)
        if self.item:
            self.entry_name.insert(0, self.item.item_name)

        # Row 4: Make and Model
        r4 = tk.Frame(form_frame, bg=BG_MAIN)
        r4.pack(fill="x", pady=4)
        tk.Label(r4, text="Make and Model", font=FONT_LABEL, fg=TEXT_MUTED, bg=BG_MAIN).pack(anchor="w")
        self.entry_model = tk.Entry(r4, font=FONT_UI, bg=BG_SURFACE, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                                    relief="flat", highlightthickness=1, highlightbackground=BORDER_COLOR)
        self.entry_model.pack(fill="x", pady=2, ipady=4)
        if self.item:
            self.entry_model.insert(0, self.item.make_and_model)

        # Row 5: Device Type & Category Dropdowns
        r5 = tk.Frame(form_frame, bg=BG_MAIN)
        r5.pack(fill="x", pady=4)

        f_dev = tk.Frame(r5, bg=BG_MAIN)
        f_dev.pack(side="left", fill="x", expand=True, padx=(0, 6))
        tk.Label(f_dev, text="Device Type (Equipment Line)", font=FONT_LABEL, fg=ACCENT_CYAN, bg=BG_MAIN).pack(anchor="w")
        self.device_type_var = tk.StringVar(value=getattr(self.item, "device_type", "") if self.item else "")
        self.cb_device_type = ttk.Combobox(f_dev, textvariable=self.device_type_var, values=self.db.get_device_types(), font=FONT_UI)
        self.cb_device_type.pack(fill="x", pady=2, ipady=3)

        f_cat = tk.Frame(r5, bg=BG_MAIN)
        f_cat.pack(side="right", fill="x", expand=True, padx=(6, 0))
        tk.Label(f_cat, text="Category (Discipline / Domain)", font=FONT_LABEL, fg=ACCENT_GOLD, bg=BG_MAIN).pack(anchor="w")
        self.category_var = tk.StringVar(value=getattr(self.item, "category", "") if self.item else "")
        self.cb_category = ttk.Combobox(f_cat, textvariable=self.category_var, values=self.db.get_categories(), font=FONT_UI)
        self.cb_category.pack(fill="x", pady=2, ipady=3)

        # Row 6: Department
        r6 = tk.Frame(form_frame, bg=BG_MAIN)
        r6.pack(fill="x", pady=4)
        tk.Label(r6, text="Department / Location", font=FONT_LABEL, fg=TEXT_MUTED, bg=BG_MAIN).pack(anchor="w")
        self.dept_var = tk.StringVar(value=self.item.department if self.item else "")
        self.cb_dept = ttk.Combobox(r6, textvariable=self.dept_var, values=self.existing_depts, font=FONT_UI)
        self.cb_dept.pack(fill="x", pady=2, ipady=3)

        # Row 7: Dynamic Custom Columns (if any defined)
        if self.db.custom_columns:
            sep_frame = tk.Frame(form_frame, bg=BG_MAIN)
            sep_frame.pack(fill="x", pady=(10, 4))
            tk.Label(sep_frame, text="CUSTOM ATTRIBUTES", font=FONT_LABEL, fg=TEXT_MUTED, bg=BG_MAIN).pack(anchor="w")

            for col in self.db.custom_columns:
                col_id = col["id"]
                col_name = col["name"]
                def_val = col.get("default_val", "")

                c_row = tk.Frame(form_frame, bg=BG_MAIN)
                c_row.pack(fill="x", pady=3)
                tk.Label(c_row, text=col_name, font=FONT_LABEL, fg=TEXT_MUTED, bg=BG_MAIN).pack(anchor="w")
                c_entry = tk.Entry(c_row, font=FONT_UI, bg=BG_SURFACE, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                                   relief="flat", highlightthickness=1, highlightbackground=BORDER_COLOR)
                c_entry.pack(fill="x", pady=2, ipady=4)

                val = ""
                if self.item:
                    val = self.item.custom_fields.get(col_id, def_val)
                else:
                    val = def_val
                c_entry.insert(0, val)
                self.custom_entries[col_id] = c_entry

        # Row 8: Initial Maintenance / Service Log (shown when creating new item)
        if not self.item:
            box_note = tk.Frame(form_frame, bg=BG_PANEL, highlightthickness=1, highlightbackground=BORDER_COLOR, padx=10, pady=8)
            box_note.pack(fill="x", pady=(10, 4))

            tk.Label(
                box_note,
                text="INITIAL MAINTENANCE LOG (OPTIONAL INTAKE RECORD)",
                font=FONT_LABEL,
                fg=ACCENT_CYAN,
                bg=BG_PANEL
            ).pack(anchor="w", pady=(0, 2))

            # Operational Work State & Severity Row
            st_row = tk.Frame(box_note, bg=BG_PANEL)
            st_row.pack(fill="x", pady=(2, 6))

            f_ws = tk.Frame(st_row, bg=BG_PANEL)
            f_ws.pack(side="left", fill="x", expand=True, padx=(0, 4))
            tk.Label(f_ws, text="Work State", font=FONT_LABEL, fg=ACCENT_GOLD, bg=BG_PANEL).pack(anchor="w")
            self.init_work_status_var = tk.StringVar(value="Done")
            cb_ws = ttk.Combobox(f_ws, textvariable=self.init_work_status_var, values=["Done", "Working", "Stuck", "Idle"], state="readonly", font=FONT_UI)
            cb_ws.pack(fill="x", pady=2, ipady=2)

            f_sev = tk.Frame(st_row, bg=BG_PANEL)
            f_sev.pack(side="left", fill="x", expand=True, padx=4)
            tk.Label(f_sev, text="Severity", font=FONT_LABEL, fg=TEXT_MUTED, bg=BG_PANEL).pack(anchor="w")
            self.init_sev_var = tk.StringVar(value="Routine")
            cb_sev = ttk.Combobox(f_sev, textvariable=self.init_sev_var, values=["Routine", "Medium", "High", "Critical"], state="readonly", font=FONT_UI)
            cb_sev.pack(fill="x", pady=2, ipady=2)

            f_tech = tk.Frame(st_row, bg=BG_PANEL)
            f_tech.pack(side="right", fill="x", expand=True, padx=(4, 0))
            tk.Label(f_tech, text="Technician", font=FONT_LABEL, fg=TEXT_MUTED, bg=BG_PANEL).pack(anchor="w")
            self.entry_init_tech = ttk.Combobox(f_tech, values=self.db.get_technicians(), font=FONT_UI)
            self.entry_init_tech.pack(fill="x", pady=2, ipady=3)

            # Problem
            tk.Label(box_note, text="Problem / Malfunction *", font=FONT_LABEL, fg=TEXT_MUTED, bg=BG_PANEL).pack(anchor="w")
            self.entry_init_problem = tk.Entry(box_note, font=FONT_UI, bg=BG_SURFACE, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                                               relief="flat", highlightthickness=1, highlightbackground=BORDER_COLOR)
            self.entry_init_problem.pack(fill="x", pady=2, ipady=3)

            # Root Cause
            tk.Label(box_note, text="Root Cause", font=FONT_LABEL, fg=TEXT_MUTED, bg=BG_PANEL).pack(anchor="w", pady=(3, 0))
            self.entry_init_root = tk.Entry(box_note, font=FONT_UI, bg=BG_SURFACE, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                                            relief="flat", highlightthickness=1, highlightbackground=BORDER_COLOR)
            self.entry_init_root.pack(fill="x", pady=2, ipady=3)

            # Action Taken
            tk.Label(box_note, text="Action Taken", font=FONT_LABEL, fg=TEXT_MUTED, bg=BG_PANEL).pack(anchor="w", pady=(3, 0))
            self.entry_init_action = tk.Entry(box_note, font=FONT_UI, bg=BG_SURFACE, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                                              relief="flat", highlightthickness=1, highlightbackground=BORDER_COLOR)
            self.entry_init_action.pack(fill="x", pady=2, ipady=3)

            # Parts Consumed
            tk.Label(box_note, text="Parts / Materials Consumed", font=FONT_LABEL, fg=TEXT_MUTED, bg=BG_PANEL).pack(anchor="w", pady=(3, 0))
            self.entry_init_parts = tk.Entry(box_note, font=FONT_UI, bg=BG_SURFACE, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                                             relief="flat", highlightthickness=1, highlightbackground=BORDER_COLOR)
            self.entry_init_parts.pack(fill="x", pady=2, ipady=3)

    def focus_first_input(self):
        self.entry_name.focus_set()

    def on_save(self):
        item_name = self.entry_name.get().strip()
        if not item_name:
            messagebox.showwarning("Required Field", "Please enter an Item Name.", parent=self)
            self.entry_name.focus_set()
            return

        queue_num = self.entry_queue.get().strip()
        moc_num = self.entry_moc.get().strip()
        st_num = self.entry_st.get().strip()
        make_model = self.entry_model.get().strip()
        status = self.status_var.get().strip()
        dept = self.dept_var.get().strip()
        device_type = self.device_type_var.get().strip()
        category = self.category_var.get().strip()

        if device_type:
            self.db.add_device_type(device_type)
        if category:
            self.db.add_category(category)

        custom_vals = {}
        for col_id, ent in self.custom_entries.items():
            custom_vals[col_id] = ent.get().strip()

        initial_note_data = None
        if not self.item and hasattr(self, "entry_init_problem"):
            prob = self.entry_init_problem.get().strip()
            root = self.entry_init_root.get().strip()
            act = self.entry_init_action.get().strip()
            parts = self.entry_init_parts.get().strip()
            tech = self.entry_init_tech.get().strip() if hasattr(self, "entry_init_tech") else ""
            if tech:
                self.db.add_technician(tech)
            w_state = self.init_work_status_var.get().strip() or "Done"
            sev = self.init_sev_var.get().strip() or "Routine"

            if (root or act or parts or tech) and not prob:
                messagebox.showwarning("Problem Required", "Please specify the Problem for the initial service note.", parent=self)
                self.entry_init_problem.focus_set()
                return

            if prob:
                initial_note_data = {
                    "note_type": "maintenance",
                    "problem": prob,
                    "root_cause": root,
                    "action_taken": act,
                    "parts_consumed": parts,
                    "technician": tech,
                    "work_status": w_state,
                    "severity": sev
                }

        self.result = {
            "queue_number": queue_num,
            "moc_number": moc_num,
            "st_number": st_num,
            "item_name": item_name,
            "make_and_model": make_model,
            "status": status,
            "department": dept,
            "device_type": device_type,
            "category": category,
            "custom_fields": custom_vals,
            "initial_note_data": initial_note_data,
            "initial_note": initial_note_data["problem"] if initial_note_data else ""
        }
        self.destroy()


class ServiceNoteDialog(BaseDialog):
    """Overhauled modal dialog for structured maintenance logging with Work States (Done, Working, Stuck, Idle), presets, and observation notes."""
    def __init__(self, parent, item, note=None, db=None):
        self.item = item
        self.note = note
        self.db = db or getattr(parent, "db", None)
        self.is_quick = (note and getattr(note, "note_type", "maintenance") == "quick")
        
        title = "Edit Quick Note" if self.is_quick else ("Edit Maintenance Log" if note else "Service Log Entry")
        super().__init__(parent, title=title)

        target_h = 440 if self.is_quick else 690
        center_window_on_parent(self, parent, width=640, height=target_h)
        self.build_ui()
        self.grab_set()

    def build_ui(self):
        # Header banner
        header = tk.Frame(self, bg=BG_PANEL, height=52, highlightthickness=1, highlightbackground=BORDER_COLOR)
        header.pack(side="top", fill="x", padx=12, pady=(12, 6))
        header.pack_propagate(False)

        if self.is_quick:
            title = "🔭 EDIT OBSERVATION NOTE"
            color = "#f0883e"
        elif self.note:
            title = "🛠️ EDIT MAINTENANCE LOG"
            color = ACCENT_GOLD
        else:
            title = "🛠️ ADD MAINTENANCE LOG"
            color = ACCENT_CYAN

        self.lbl_title = tk.Label(header, text=title, font=FONT_TITLE, fg=color, bg=BG_PANEL)
        self.lbl_title.pack(side="left", padx=14, pady=10)

        item_tag = f"[{self.item.queue_number}] {self.item.item_name[:24]}"
        lbl_badge = tk.Label(header, text=item_tag, font=FONT_CODE, fg=TEXT_MUTED, bg=BG_SURFACE, padx=8, pady=3)
        lbl_badge.pack(side="right", padx=14, pady=10)

        # Bottom Button Bar
        btn_bar = tk.Frame(self, bg=BG_PANEL, height=50, highlightthickness=1, highlightbackground=BORDER_COLOR)
        btn_bar.pack(side="bottom", fill="x", padx=12, pady=(4, 12))
        btn_bar.pack_propagate(False)

        btn_cancel = tk.Button(
            btn_bar, text="Cancel", font=FONT_UI, fg=TEXT_PRIMARY, bg=BG_SURFACE,
            activebackground=BG_ACTIVE, relief="flat", padx=14, pady=4, cursor="hand2", command=self.destroy
        )
        btn_cancel.pack(side="right", padx=10, pady=8)

        save_btn_text = "Update Note" if self.note else "Save Record"
        btn_save = tk.Button(
            btn_bar, text=save_btn_text, font=("Segoe UI", 9, "bold"), fg=BG_MAIN, bg=ACCENT_CYAN,
            activebackground="#79c0ff", relief="flat", padx=18, pady=4, cursor="hand2", command=self.on_save
        )
        btn_save.pack(side="right", padx=4, pady=8)

        # Form Container
        form = tk.Frame(self, bg=BG_MAIN)
        form.pack(side="top", fill="both", expand=True, padx=14, pady=4)

        # Top Control Strip: Note Type Switcher (Left) + Timestamp (Right)
        ctrl_strip = tk.Frame(form, bg=BG_MAIN)
        ctrl_strip.pack(fill="x", pady=(0, 6))

        f_mode = tk.Frame(ctrl_strip, bg=BG_MAIN)
        f_mode.pack(side="left")
        tk.Label(f_mode, text="Note Type:", font=FONT_LABEL, fg=TEXT_MUTED, bg=BG_MAIN).pack(anchor="w")

        self.note_type_var = tk.StringVar(value="quick" if self.is_quick else "maintenance")
        mode_btn_frame = tk.Frame(f_mode, bg=BG_SURFACE, highlightthickness=1, highlightbackground=BORDER_COLOR)
        mode_btn_frame.pack(anchor="w", pady=(2, 0))

        self.btn_mode_maint = tk.Radiobutton(
            mode_btn_frame,
            text="🛠️ Maintenance Record",
            value="maintenance",
            variable=self.note_type_var,
            font=("Segoe UI", 8, "bold"),
            fg=TEXT_PRIMARY,
            bg=BG_SURFACE,
            selectcolor=BG_ACTIVE,
            activebackground=BG_ACTIVE,
            activeforeground=ACCENT_CYAN,
            indicatoron=False,
            padx=12,
            pady=3,
            cursor="hand2",
            command=self.on_mode_switched
        )
        self.btn_mode_maint.pack(side="left")

        self.btn_mode_quick = tk.Radiobutton(
            mode_btn_frame,
            text="🔭 Observation Note",
            value="quick",
            variable=self.note_type_var,
            font=("Segoe UI", 8, "bold"),
            fg=TEXT_PRIMARY,
            bg=BG_SURFACE,
            selectcolor=BG_ACTIVE,
            activebackground=BG_ACTIVE,
            activeforeground="#f0883e",
            indicatoron=False,
            padx=12,
            pady=3,
            cursor="hand2",
            command=self.on_mode_switched
        )
        self.btn_mode_quick.pack(side="left")

        # Timestamp
        f_ts = tk.Frame(ctrl_strip, bg=BG_MAIN)
        f_ts.pack(side="right", anchor="ne")
        tk.Label(f_ts, text="Timestamp", font=FONT_LABEL, fg=TEXT_MUTED, bg=BG_MAIN).pack(anchor="e")
        now_str = self.note.timestamp if self.note else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.entry_ts = tk.Entry(f_ts, font=FONT_CODE, bg=BG_SURFACE, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                                 width=20, relief="flat", highlightthickness=1, highlightbackground=BORDER_COLOR)
        self.entry_ts.pack(anchor="e", pady=(2, 0), ipady=2)
        self.entry_ts.insert(0, now_str)

        # Container 1: Quick Observation Note
        self.quick_container = tk.Frame(form, bg=BG_MAIN)

        lbl_obs = tk.Label(
            self.quick_container,
            text="🔭 OBSERVATION NOTE • Logged without work status override (Done, Working, Stuck, Idle)",
            font=("Segoe UI", 8, "bold"),
            fg="#f0883e",
            bg="#2d2218",
            padx=10,
            pady=4,
            highlightthickness=1,
            highlightbackground="#d97706"
        )
        lbl_obs.pack(anchor="w", fill="x", pady=(2, 8))

        tk.Label(self.quick_container, text="Observation Note Content *", font=FONT_LABEL, fg=TEXT_PRIMARY, bg=BG_MAIN).pack(anchor="w", pady=(2, 0))
        self.txt_quick = tk.Text(self.quick_container, font=FONT_UI, bg=BG_SURFACE, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                                 relief="flat", highlightthickness=1, highlightbackground=BORDER_COLOR, wrap="word", height=8)
        self.txt_quick.pack(fill="both", expand=True, pady=4)
        if self.note:
            self.txt_quick.insert("1.0", self.note.quick_note or self.note.note)
        self.txt_quick.bind("<Control-Return>", lambda e: (self.on_save(), "break"))

        # Container 2: Structured Maintenance Record
        self.maint_container = tk.Frame(form, bg=BG_MAIN)

        # Work State Selector
        f_state = tk.Frame(self.maint_container, bg=BG_MAIN)
        f_state.pack(fill="x", pady=(0, 6))
        tk.Label(f_state, text="Work State (Kanban Status):", font=FONT_LABEL, fg=ACCENT_GOLD, bg=BG_MAIN).pack(anchor="w")

        init_ws = getattr(self.note, "work_status", "Done") if self.note else "Done"
        if init_ws == "Observation":
            init_ws = "Done"
        self.work_status_var = tk.StringVar(value=init_ws)
        state_btn_frame = tk.Frame(f_state, bg=BG_SURFACE, highlightthickness=1, highlightbackground=BORDER_COLOR)
        state_btn_frame.pack(anchor="w", pady=(2, 0))

        self.state_buttons = {}
        states = [("Done", COLOR_DONE), ("Working", COLOR_WORKING), ("Stuck", COLOR_STUCK), ("Idle", COLOR_IDLE)]
        for s_name, s_color in states:
            b = tk.Radiobutton(
                state_btn_frame,
                text=s_name,
                value=s_name,
                variable=self.work_status_var,
                font=("Segoe UI", 8, "bold"),
                fg=TEXT_PRIMARY,
                bg=BG_SURFACE,
                selectcolor=BG_ACTIVE,
                activebackground=BG_ACTIVE,
                activeforeground=s_color,
                indicatoron=False,
                padx=12,
                pady=2,
                cursor="hand2"
            )
            b.pack(side="left")
            self.state_buttons[s_name] = b

        # Metadata Row 1: Severity, Service Type, Presets
        meta_strip1 = tk.Frame(self.maint_container, bg=BG_MAIN)
        meta_strip1.pack(fill="x", pady=(2, 6))

        f_sev = tk.Frame(meta_strip1, bg=BG_MAIN)
        f_sev.pack(side="left", fill="x", expand=True, padx=(0, 6))
        tk.Label(f_sev, text="Severity", font=FONT_LABEL, fg=TEXT_MUTED, bg=BG_MAIN).pack(anchor="w")
        self.sev_var = tk.StringVar(value=getattr(self.note, "severity", "Routine") if self.note else "Routine")
        cb_sev = ttk.Combobox(f_sev, textvariable=self.sev_var, values=["Routine", "Medium", "High", "Critical"], state="readonly", font=FONT_UI)
        cb_sev.pack(fill="x", pady=2, ipady=2)

        f_stype = tk.Frame(meta_strip1, bg=BG_MAIN)
        f_stype.pack(side="left", fill="x", expand=True, padx=6)
        tk.Label(f_stype, text="Service Type", font=FONT_LABEL, fg=TEXT_MUTED, bg=BG_MAIN).pack(anchor="w")
        self.stype_var = tk.StringVar(value=getattr(self.note, "service_type", "Corrective Repair") if self.note else "Corrective Repair")
        cb_stype = ttk.Combobox(
            f_stype,
            textvariable=self.stype_var,
            values=["Corrective Repair", "Preventative Maintenance (PM)", "Inspection & Testing", "Calibration", "Overhaul", "Firmware Update"],
            state="readonly",
            font=FONT_UI
        )
        cb_stype.pack(fill="x", pady=2, ipady=2)

        f_presets = tk.Frame(meta_strip1, bg=BG_MAIN)
        f_presets.pack(side="right", padx=(6, 0))
        tk.Label(f_presets, text="Quick Fill", font=FONT_LABEL, fg=TEXT_MUTED, bg=BG_MAIN).pack(anchor="e")
        btn_presets = tk.Menubutton(
            f_presets,
            text="⚡ Task Presets ▾",
            font=("Segoe UI", 8, "bold"),
            fg=BG_MAIN,
            bg=ACCENT_GOLD,
            activebackground="#ffe58f",
            relief="flat",
            padx=10,
            pady=3,
            cursor="hand2"
        )
        btn_presets.pack(anchor="e", pady=2)
        self.preset_menu = tk.Menu(btn_presets, tearoff=0, bg=BG_SURFACE, fg=TEXT_PRIMARY, font=FONT_UI)
        btn_presets["menu"] = self.preset_menu
        self.build_preset_menu(self.preset_menu)

        # Metadata Row 2: Technician / Operator
        meta_strip2 = tk.Frame(self.maint_container, bg=BG_MAIN)
        meta_strip2.pack(fill="x", pady=(0, 6))

        tk.Label(meta_strip2, text="Technician / Operator", font=FONT_LABEL, fg=TEXT_MUTED, bg=BG_MAIN).pack(anchor="w")
        tech_values = self.db.get_technicians() if (self.db and hasattr(self.db, "get_technicians")) else []
        self.entry_tech = ttk.Combobox(meta_strip2, values=tech_values, font=FONT_UI)
        self.entry_tech.pack(fill="x", pady=2, ipady=2)
        if self.note:
            self.entry_tech.set(getattr(self.note, "technician", ""))

        # Problem Description (Required)
        f_prob = tk.Frame(self.maint_container, bg=BG_MAIN)
        f_prob.pack(fill="x", pady=(2, 4))
        tk.Label(f_prob, text="Problem / Malfunction Description *", font=FONT_LABEL, fg=ACCENT_GOLD, bg=BG_MAIN).pack(anchor="w")
        self.txt_problem = tk.Text(f_prob, font=FONT_UI, bg=BG_SURFACE, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                                   relief="flat", highlightthickness=1, highlightbackground=BORDER_COLOR, wrap="word", height=2)
        self.txt_problem.pack(fill="x", pady=2)
        if self.note:
            self.txt_problem.insert("1.0", self.note.problem or self.note.note)
        self.txt_problem.bind("<Control-Return>", lambda e: (self.on_save(), "break"))

        # Root Cause Analysis (Optional)
        f_root = tk.Frame(self.maint_container, bg=BG_MAIN)
        f_root.pack(fill="x", pady=(2, 4))
        tk.Label(f_root, text="Root Cause Analysis (Optional)", font=FONT_LABEL, fg=TEXT_MUTED, bg=BG_MAIN).pack(anchor="w")
        self.txt_root = tk.Text(f_root, font=FONT_UI, bg=BG_SURFACE, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                                relief="flat", highlightthickness=1, highlightbackground=BORDER_COLOR, wrap="word", height=2)
        self.txt_root.pack(fill="x", pady=2)
        if self.note:
            self.txt_root.insert("1.0", self.note.root_cause)
        self.txt_root.bind("<Control-Return>", lambda e: (self.on_save(), "break"))

        # Action Taken (Optional)
        f_act = tk.Frame(self.maint_container, bg=BG_MAIN)
        f_act.pack(fill="x", pady=(2, 4))
        tk.Label(f_act, text="Action Taken / Maintenance Performed (Optional)", font=FONT_LABEL, fg=TEXT_MUTED, bg=BG_MAIN).pack(anchor="w")
        self.txt_action = tk.Text(f_act, font=FONT_UI, bg=BG_SURFACE, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                                  relief="flat", highlightthickness=1, highlightbackground=BORDER_COLOR, wrap="word", height=2)
        self.txt_action.pack(fill="x", pady=2)
        if self.note:
            self.txt_action.insert("1.0", self.note.action_taken)
        self.txt_action.bind("<Control-Return>", lambda e: (self.on_save(), "break"))

        # Parts Consumed (Optional)
        f_parts = tk.Frame(self.maint_container, bg=BG_MAIN)
        f_parts.pack(fill="x", pady=(2, 4))
        tk.Label(f_parts, text="Parts / Materials Consumed (Optional)", font=FONT_LABEL, fg=TEXT_MUTED, bg=BG_MAIN).pack(anchor="w")
        self.entry_parts = tk.Entry(f_parts, font=FONT_UI, bg=BG_SURFACE, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                                    relief="flat", highlightthickness=1, highlightbackground=BORDER_COLOR)
        self.entry_parts.pack(fill="x", pady=2, ipady=3)
        if self.note:
            self.entry_parts.insert(0, self.note.parts_consumed)
        self.entry_parts.bind("<Control-Return>", lambda e: (self.on_save(), "break"))

        # Pack active container
        if self.note_type_var.get() == "quick":
            self.quick_container.pack(fill="both", expand=True)
            self.txt_quick.focus_set()
        else:
            self.maint_container.pack(fill="both", expand=True)
            self.txt_problem.focus_set()

    def on_mode_switched(self):
        mode = self.note_type_var.get()
        if mode == "quick":
            self.maint_container.pack_forget()
            self.quick_container.pack(fill="both", expand=True)
            self.lbl_title.config(text="🔭 OBSERVATION NOTE", fg="#f0883e")
            self.geometry("640x440")
            self.txt_quick.focus_set()
        else:
            self.quick_container.pack_forget()
            self.maint_container.pack(fill="both", expand=True)
            self.lbl_title.config(text="🛠️ MAINTENANCE LOG", fg=ACCENT_CYAN)
            self.geometry("640x700")
            self.txt_problem.focus_set()

    def build_preset_menu(self, menu):
        menu.delete(0, "end")
        presets = self.db.get_task_presets() if (self.db and hasattr(self.db, "get_task_presets")) else []
        if not presets:
            menu.add_command(label="(No Presets Saved)", state="disabled")
        else:
            for p in presets:
                title = p.get("title", "Untitled Preset")
                prob = p.get("problem", "")
                root = p.get("root_cause", "")
                act = p.get("action_taken", "")
                parts = p.get("parts_consumed", "")
                stype = p.get("service_type", "Corrective Repair")
                state = p.get("work_status", "Done")
                sev = p.get("severity", "Routine")
                menu.add_command(
                    label=f"⚡ {title}",
                    command=lambda prb=prob, rt=root, a=act, prts=parts, st=stype, ws=state, sv=sev: self.apply_preset(prb, rt, a, prts, st, ws, sv)
                )

        menu.add_separator()
        menu.add_command(label="💾 Save Current Form as Preset...", command=self.on_save_as_preset)
        if presets:
            menu.add_command(label="🗑️ Delete a Preset...", command=self.on_delete_preset_dialog)

    def on_save_as_preset(self):
        from tkinter import simpledialog
        title = simpledialog.askstring("Save Task Preset", "Enter a title for this task preset:", parent=self)
        if not title or not title.strip():
            return
        preset = {
            "title": title.strip(),
            "problem": self.txt_problem.get("1.0", "end-1c").strip(),
            "root_cause": self.txt_root.get("1.0", "end-1c").strip(),
            "action_taken": self.txt_action.get("1.0", "end-1c").strip(),
            "parts_consumed": self.entry_parts.get().strip(),
            "service_type": self.stype_var.get().strip(),
            "work_status": self.work_status_var.get().strip(),
            "severity": self.sev_var.get().strip()
        }
        if self.db and hasattr(self.db, "add_task_preset"):
            self.db.add_task_preset(preset)
            self.db.save()
        if hasattr(self, "preset_menu"):
            self.build_preset_menu(self.preset_menu)
        messagebox.showinfo("Preset Saved", f"Task preset '{title.strip()}' has been saved to the database!", parent=self)

    def on_delete_preset_dialog(self):
        presets = self.db.get_task_presets() if (self.db and hasattr(self.db, "get_task_presets")) else []
        if not presets:
            return
        del_win = tk.Toplevel(self)
        del_win.title("Delete Task Preset")
        del_win.configure(bg=BG_PANEL)
        del_win.geometry("340x220")
        del_win.transient(self)
        del_win.grab_set()

        tk.Label(del_win, text="Select preset to delete:", font=FONT_LABEL, fg=TEXT_PRIMARY, bg=BG_PANEL).pack(padx=14, pady=(12, 6), anchor="w")
        lb = tk.Listbox(del_win, bg=BG_SURFACE, fg=TEXT_PRIMARY, selectbackground=BG_ACTIVE, relief="flat", font=FONT_UI)
        lb.pack(fill="both", expand=True, padx=14, pady=4)
        for p in presets:
            lb.insert("end", p.get("title", ""))

        def do_delete():
            sel = lb.curselection()
            if not sel:
                return
            t = lb.get(sel[0])
            if self.db and hasattr(self.db, "delete_task_preset"):
                self.db.delete_task_preset(t)
                self.db.save()
            if hasattr(self, "preset_menu"):
                self.build_preset_menu(self.preset_menu)
            del_win.destroy()

        btn_row = tk.Frame(del_win, bg=BG_PANEL)
        btn_row.pack(fill="x", padx=14, pady=8)
        tk.Button(btn_row, text="Delete", font=FONT_UI_BOLD, fg=BG_MAIN, bg=ACCENT_CORAL, relief="flat", padx=10, command=do_delete).pack(side="right")
        tk.Button(btn_row, text="Cancel", font=FONT_UI, fg=TEXT_PRIMARY, bg=BG_SURFACE, relief="flat", padx=8, command=del_win.destroy).pack(side="right", padx=6)

    def apply_preset(self, problem, root_cause, action, parts, service_type, work_status, severity):
        self.txt_problem.delete("1.0", "end")
        self.txt_problem.insert("1.0", problem)
        self.txt_root.delete("1.0", "end")
        self.txt_root.insert("1.0", root_cause)
        self.txt_action.delete("1.0", "end")
        self.txt_action.insert("1.0", action)
        self.entry_parts.delete(0, "end")
        self.entry_parts.insert(0, parts)
        self.stype_var.set(service_type)
        self.work_status_var.set(work_status)
        self.sev_var.set(severity)

    def on_save(self):
        ts = self.entry_ts.get().strip() or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        mode = self.note_type_var.get()

        if mode == "quick":
            text = self.txt_quick.get("1.0", "end-1c").strip()
            if not text:
                messagebox.showwarning("Empty Note", "Please enter observation note text.", parent=self)
                self.txt_quick.focus_set()
                return
            self.result = {
                "note_type": "quick",
                "quick_note": text,
                "note": text,
                "work_status": "Observation",
                "timestamp": ts
            }
        else:
            w_state = self.work_status_var.get().strip() or "Done"
            problem = self.txt_problem.get("1.0", "end-1c").strip()
            if not problem:
                messagebox.showwarning("Required Field", "Please enter the Problem description (Required*).", parent=self)
                self.txt_problem.focus_set()
                return

            root_cause = self.txt_root.get("1.0", "end-1c").strip()
            action_taken = self.txt_action.get("1.0", "end-1c").strip()
            parts_consumed = self.entry_parts.get().strip()
            technician = self.entry_tech.get().strip() if hasattr(self, "entry_tech") else ""
            if technician and self.db and hasattr(self.db, "add_technician"):
                self.db.add_technician(technician)
            severity = self.sev_var.get().strip() or "Routine"
            service_type = self.stype_var.get().strip() or "Corrective Repair"

            self.result = {
                "note_type": "maintenance",
                "problem": problem,
                "root_cause": root_cause,
                "action_taken": action_taken,
                "parts_consumed": parts_consumed,
                "work_status": w_state,
                "severity": severity,
                "service_type": service_type,
                "technician": technician,
                "timestamp": ts
            }

        self.destroy()


class ColumnManagerDialog(BaseDialog):
    """Modal dialog to view, add, and remove dynamic custom columns."""
    def __init__(self, parent, db):
        super().__init__(parent, title="Manage Custom Columns")
        self.db = db
        center_window_on_parent(self, parent, width=540, height=480)
        self.build_ui()
        self.grab_set()

    def build_ui(self):
        header = tk.Frame(self, bg=BG_PANEL, height=52, highlightthickness=1, highlightbackground=BORDER_COLOR)
        header.pack(fill="x", padx=12, pady=(12, 8))
        header.pack_propagate(False)

        lbl_title = tk.Label(header, text="⚙️ CUSTOM DATABASE COLUMNS", font=FONT_TITLE, fg=ACCENT_CYAN, bg=BG_PANEL)
        lbl_title.pack(side="left", padx=14, pady=10)

        content = tk.Frame(self, bg=BG_MAIN)
        content.pack(fill="both", expand=True, padx=14, pady=4)

        lbl_info = tk.Label(
            content,
            text="Core columns (Queue #, MOC #, ST #, Item Name, Make/Model, Device Type, Category, Status, Department, Service Log) are permanently maintained. Below are user-added custom columns:",
            font=FONT_UI,
            fg=TEXT_MUTED,
            bg=BG_MAIN,
            wraplength=490,
            justify="left"
        )
        lbl_info.pack(anchor="w", pady=(0, 8))

        tree_frame = tk.Frame(content, bg=BG_SURFACE, highlightthickness=1, highlightbackground=BORDER_COLOR)
        tree_frame.pack(fill="both", expand=True, pady=(0, 8))

        cols = ("name", "id", "default")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=5)
        self.tree.heading("name", text="Column Display Name")
        self.tree.heading("id", text="Schema ID")
        self.tree.heading("default", text="Default Value")
        self.tree.column("name", width=180)
        self.tree.column("id", width=120)
        self.tree.column("default", width=150)
        self.tree.pack(fill="both", expand=True)

        self.refresh_list()

        card_add = tk.Frame(content, bg=BG_PANEL, highlightthickness=1, highlightbackground=BORDER_COLOR, padx=10, pady=8)
        card_add.pack(fill="x", pady=4)

        tk.Label(card_add, text="Add New Custom Column", font=FONT_LABEL, fg=ACCENT_GOLD, bg=BG_PANEL).pack(anchor="w", pady=(0, 4))

        inp_row = tk.Frame(card_add, bg=BG_PANEL)
        inp_row.pack(fill="x")

        f1 = tk.Frame(inp_row, bg=BG_PANEL)
        f1.pack(side="left", fill="x", expand=True, padx=(0, 6))
        tk.Label(f1, text="Column Name", font=FONT_UI, fg=TEXT_MUTED, bg=BG_PANEL).pack(anchor="w")
        self.entry_new_col = tk.Entry(f1, font=FONT_UI, bg=BG_SURFACE, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                                      relief="flat", highlightthickness=1, highlightbackground=BORDER_COLOR)
        self.entry_new_col.pack(fill="x", pady=2, ipady=3)

        f2 = tk.Frame(inp_row, bg=BG_PANEL)
        f2.pack(side="left", fill="x", expand=True, padx=(0, 6))
        tk.Label(f2, text="Default Value (Optional)", font=FONT_UI, fg=TEXT_MUTED, bg=BG_PANEL).pack(anchor="w")
        self.entry_def_val = tk.Entry(f2, font=FONT_UI, bg=BG_SURFACE, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                                      relief="flat", highlightthickness=1, highlightbackground=BORDER_COLOR)
        self.entry_def_val.pack(fill="x", pady=2, ipady=3)

        btn_add = tk.Button(
            inp_row, text="+ Add Column", font=("Segoe UI", 9, "bold"), fg=BG_MAIN, bg=ACCENT_MINT,
            activebackground="#a6f3b0", relief="flat", padx=10, pady=3, cursor="hand2", command=self.on_add_column
        )
        btn_add.pack(side="right", pady=(18, 0))

        btn_bar = tk.Frame(self, bg=BG_PANEL, height=50, highlightthickness=1, highlightbackground=BORDER_COLOR)
        btn_bar.pack(side="bottom", fill="x", padx=12, pady=(4, 12))
        btn_bar.pack_propagate(False)

        btn_close = tk.Button(
            btn_bar, text="Close", font=FONT_UI, fg=TEXT_PRIMARY, bg=BG_SURFACE,
            activebackground=BG_ACTIVE, relief="flat", padx=14, pady=4, cursor="hand2", command=self.destroy
        )
        btn_close.pack(side="right", padx=10, pady=10)

        btn_del = tk.Button(
            btn_bar, text="🗑️ Delete Column", font=FONT_UI, fg=ACCENT_CORAL, bg=BG_SURFACE,
            activebackground=BG_ACTIVE, relief="flat", padx=12, pady=4, cursor="hand2", command=self.on_delete_column
        )
        btn_del.pack(side="left", padx=10, pady=10)

    def refresh_list(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        for col in self.db.custom_columns:
            self.tree.insert("", "end", iid=col["id"], values=(col["name"], col["id"], col.get("default_val", "")))

    def on_add_column(self):
        name = self.entry_new_col.get().strip()
        def_val = self.entry_def_val.get().strip()
        if not name:
            messagebox.showwarning("Validation Error", "Please enter a column name.", parent=self)
            return
        try:
            self.db.add_custom_column(name, default_val=def_val)
            self.entry_new_col.delete(0, "end")
            self.entry_def_val.delete(0, "end")
            self.refresh_list()
        except ValueError as e:
            messagebox.showerror("Error", str(e), parent=self)

    def on_delete_column(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Select Column", "Please select a custom column to delete.", parent=self)
            return
        col_id = sel[0]
        col_name = self.tree.item(col_id)["values"][0]
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete column '{col_name}'?\nThis will remove its data from all items.", parent=self):
            self.db.remove_custom_column(col_id)
            self.refresh_list()


class DatabaseInitDialog(BaseDialog):
    """Modal dialog prompting user to initialize empty database or load demo data."""
    def __init__(self, parent, db_path="orbit_database.json"):
        super().__init__(parent, title="Initialize OrbitTracker Database")
        self.db_path = db_path
        self.result = "empty"
        center_window_on_parent(self, parent, width=560, height=360)
        self.build_ui()
        self.grab_set()

    def build_ui(self):
        header = tk.Frame(self, bg=BG_PANEL, height=52, highlightthickness=1, highlightbackground=BORDER_COLOR)
        header.pack(fill="x", padx=12, pady=(12, 8))
        header.pack_propagate(False)

        lbl_title = tk.Label(header, text="🪐 WELCOME TO ORBIT TRACKER", font=FONT_TITLE, fg=ACCENT_CYAN, bg=BG_PANEL)
        lbl_title.pack(side="left", padx=14, pady=10)

        msg_frame = tk.Frame(self, bg=BG_MAIN)
        msg_frame.pack(fill="x", padx=16, pady=4)

        lbl_info = tk.Label(
            msg_frame,
            text="No existing OrbitTracker database was found at the designated path:",
            font=FONT_UI,
            fg=TEXT_PRIMARY,
            bg=BG_MAIN,
            wraplength=500,
            justify="left"
        )
        lbl_info.pack(anchor="w", pady=(0, 2))

        lbl_path = tk.Label(
            msg_frame,
            text=f"📁 {self.db_path}",
            font=FONT_CODE,
            fg=ACCENT_GOLD,
            bg=BG_SURFACE,
            padx=8,
            pady=4,
            anchor="w"
        )
        lbl_path.pack(fill="x", pady=(4, 6))

        lbl_question = tk.Label(
            msg_frame,
            text="Would you like to populate sample equipment data to explore OrbitTracker, or start with a fresh empty database?",
            font=FONT_UI,
            fg=TEXT_MUTED,
            bg=BG_MAIN,
            wraplength=500,
            justify="left"
        )
        lbl_question.pack(anchor="w", pady=(0, 4))

        choices_frame = tk.Frame(self, bg=BG_MAIN)
        choices_frame.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        card_demo = tk.Frame(choices_frame, bg=BG_PANEL, highlightthickness=1, highlightbackground=BORDER_COLOR)
        card_demo.pack(fill="x", pady=(0, 8))

        btn_demo = tk.Button(
            card_demo,
            text="🪐  Load Demo Database",
            font=("Segoe UI", 10, "bold"),
            fg=BG_MAIN,
            bg=ACCENT_CYAN,
            activebackground="#79c0ff",
            relief="flat",
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.on_load_demo
        )
        btn_demo.pack(side="left", padx=12, pady=10)

        lbl_demo_desc = tk.Label(
            card_demo,
            text="Loads sample equipment units, device types, maintenance logs, and custom columns.",
            font=FONT_UI,
            fg=TEXT_MUTED,
            bg=BG_PANEL,
            wraplength=300,
            justify="left"
        )
        lbl_demo_desc.pack(side="left", padx=(0, 10), pady=10)

        card_empty = tk.Frame(choices_frame, bg=BG_PANEL, highlightthickness=1, highlightbackground=BORDER_COLOR)
        card_empty.pack(fill="x")

        btn_empty = tk.Button(
            card_empty,
            text="✨  Create Empty Database",
            font=("Segoe UI", 10, "bold"),
            fg=TEXT_PRIMARY,
            bg=BG_SURFACE,
            activebackground=BG_ACTIVE,
            relief="flat",
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.on_create_empty
        )
        btn_empty.pack(side="left", padx=12, pady=10)

        lbl_empty_desc = tk.Label(
            card_empty,
            text="Creates a clean, blank database ready for your operational equipment.",
            font=FONT_UI,
            fg=TEXT_MUTED,
            bg=BG_PANEL,
            wraplength=300,
            justify="left"
        )
        lbl_empty_desc.pack(side="left", padx=(0, 10), pady=10)

        self.bind("<Return>", lambda e: self.on_load_demo())
        btn_demo.focus_set()

    def on_load_demo(self):
        self.result = "demo"
        self.destroy()

    def on_create_empty(self):
        self.result = "empty"
        self.destroy()


class DeleteDatabaseDialog(BaseDialog):
    """Modal dialog requiring the user to type 'DELETE DATABASE' to confirm deletion."""
    def __init__(self, parent, db_path="orbit_database.json"):
        super().__init__(parent, title="Confirm Database Deletion")
        self.db_path = db_path
        self.result = False
        center_window_on_parent(self, parent, width=540, height=360)
        self.build_ui()
        self.grab_set()

    def build_ui(self):
        header = tk.Frame(self, bg=BG_PANEL, height=52, highlightthickness=1, highlightbackground=BORDER_COLOR)
        header.pack(fill="x", padx=12, pady=(12, 8))
        header.pack_propagate(False)

        lbl_title = tk.Label(header, text="⚠️ DELETE DATABASE", font=FONT_TITLE, fg=ACCENT_CORAL, bg=BG_PANEL)
        lbl_title.pack(side="left", padx=14, pady=10)

        lbl_badge = tk.Label(header, text="DANGER", font=FONT_CODE, fg=BG_MAIN, bg=ACCENT_CORAL, padx=8, pady=3)
        lbl_badge.pack(side="right", padx=14, pady=10)

        body = tk.Frame(self, bg=BG_MAIN)
        body.pack(fill="both", expand=True, padx=16, pady=(4, 8))

        lbl_warn = tk.Label(
            body,
            text="Warning: You are about to permanently delete this database file from disk:",
            font=FONT_LABEL,
            fg=TEXT_PRIMARY,
            bg=BG_MAIN,
            wraplength=500,
            justify="left"
        )
        lbl_warn.pack(anchor="w", pady=(0, 4))

        lbl_path = tk.Label(
            body,
            text=f"📁 {self.db_path}",
            font=FONT_CODE,
            fg=ACCENT_GOLD,
            bg=BG_SURFACE,
            padx=8,
            pady=4,
            anchor="w"
        )
        lbl_path.pack(fill="x", pady=(0, 6))

        lbl_info = tk.Label(
            body,
            text="All work items, service logs, and custom columns in this file will be permanently erased.\n\nTo confirm, type \"DELETE DATABASE\" below:",
            font=FONT_UI,
            fg=TEXT_MUTED,
            bg=BG_MAIN,
            wraplength=500,
            justify="left"
        )
        lbl_info.pack(anchor="w", pady=(0, 6))

        self.entry_confirm = tk.Entry(
            body,
            font=("Consolas", 10, "bold"),
            bg=BG_SURFACE,
            fg=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY,
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER_COLOR
        )
        self.entry_confirm.pack(fill="x", ipady=5, pady=(2, 8))
        self.entry_confirm.focus_set()
        self.entry_confirm.bind("<KeyRelease>", self.check_input)

        btn_bar = tk.Frame(self, bg=BG_PANEL, height=52, highlightthickness=1, highlightbackground=BORDER_COLOR)
        btn_bar.pack(side="bottom", fill="x", padx=12, pady=(4, 12))
        btn_bar.pack_propagate(False)

        btn_cancel = tk.Button(
            btn_bar,
            text="Cancel",
            font=FONT_UI,
            fg=TEXT_MUTED,
            bg=BG_SURFACE,
            activebackground=BG_ACTIVE,
            activeforeground=TEXT_PRIMARY,
            relief="flat",
            padx=16,
            pady=4,
            cursor="hand2",
            command=self.destroy
        )
        btn_cancel.pack(side="right", padx=(6, 12), pady=10)

        self.btn_delete = tk.Button(
            btn_bar,
            text="🗑️ Permanently Delete Database",
            font=("Segoe UI", 9, "bold"),
            fg=TEXT_DIM,
            bg=BG_SURFACE,
            activebackground=ACCENT_CORAL,
            activeforeground=BG_MAIN,
            relief="flat",
            padx=16,
            pady=4,
            state="disabled",
            command=self.on_confirm_delete
        )
        self.btn_delete.pack(side="right", padx=6, pady=10)

    def check_input(self, event=None):
        val = self.entry_confirm.get().strip()
        if val == "DELETE DATABASE":
            self.btn_delete.configure(state="normal", fg=BG_MAIN, bg=ACCENT_CORAL, cursor="hand2")
            if event and event.keysym in ("Return", "KP_Enter"):
                self.on_confirm_delete()
        else:
            self.btn_delete.configure(state="disabled", fg=TEXT_DIM, bg=BG_SURFACE, cursor="arrow")

    def on_confirm_delete(self):
        if self.entry_confirm.get().strip() == "DELETE DATABASE":
            self.result = True
            self.destroy()


class WorkAnalyticsDialog(BaseDialog):
    """Overhauled visual analytics dashboard with multi-period trends, device types, problems, parts, and work states."""
    def __init__(self, parent, db):
        super().__init__(parent, title="OrbitTracker — Work Performance & Analytics")
        self.db = db
        self.current_tab = "temporal"
        self.selected_period = "monthly"
        self.filter_device_type = "All"
        self.filter_category = "All"
        self.filter_status = "All"
        self.chart_items = []

        center_window_on_parent(self, parent, width=1080, height=740)
        self.minsize(980, 680)
        self.resizable(True, True)
        self.build_ui()
        self.grab_set()

    def build_ui(self):
        # 1. Header banner
        header = tk.Frame(self, bg=BG_PANEL, height=54, highlightthickness=1, highlightbackground=BORDER_COLOR)
        header.pack(fill="x", padx=12, pady=(10, 4))
        header.pack_propagate(False)

        lbl_title = tk.Label(header, text="📊 WORK PERFORMANCE & MAINTENANCE ANALYTICS", font=FONT_TITLE, fg=ACCENT_CYAN, bg=BG_PANEL)
        lbl_title.pack(side="left", padx=14, pady=10)

        lbl_badge = tk.Label(header, text="METRICS ENGINE v1.1.0", font=FONT_CODE, fg=ACCENT_GOLD, bg=BG_SURFACE, padx=8, pady=3)
        lbl_badge.pack(side="right", padx=14, pady=10)

        # 2. Top KPI Summary Banner (Including Done, Working, Stuck, Idle)
        self.kpi_frame = tk.Frame(self, bg=BG_MAIN)
        self.kpi_frame.pack(fill="x", padx=12, pady=(0, 4))
        self.build_kpi_cards()

        # 3. Time Interval & Global Filter Bar
        ctrl_bar = tk.Frame(self, bg=BG_PANEL, height=44, highlightthickness=1, highlightbackground=BORDER_COLOR)
        ctrl_bar.pack(fill="x", padx=12, pady=(0, 4))
        ctrl_bar.pack_propagate(False)

        # Left: Time Interval Selector
        lbl_p = tk.Label(ctrl_bar, text="PERIOD:", font=("Segoe UI", 8, "bold"), fg=TEXT_MUTED, bg=BG_PANEL)
        lbl_p.pack(side="left", padx=(10, 4))

        self.period_buttons = {}
        periods = [("daily", "📅 Daily"), ("weekly", "📆 Weekly"), ("monthly", "🗓️ Monthly"), ("quarterly", "📊 Quarterly"), ("yearly", "📈 Yearly")]
        for p_id, p_label in periods:
            b = tk.Button(
                ctrl_bar,
                text=p_label,
                font=("Segoe UI", 8, "bold" if p_id == self.selected_period else "normal"),
                fg=ACCENT_CYAN if p_id == self.selected_period else TEXT_MUTED,
                bg=BG_ACTIVE if p_id == self.selected_period else BG_SURFACE,
                activebackground=BG_ACTIVE,
                relief="flat",
                padx=8,
                pady=2,
                cursor="hand2",
                command=lambda pid=p_id: self.set_period(pid)
            )
            b.pack(side="left", padx=2, pady=6)
            self.period_buttons[p_id] = b

        # Right: Filters for Device Type, Category, and Work State
        f_box = tk.Frame(ctrl_bar, bg=BG_PANEL)
        f_box.pack(side="right", padx=8, pady=4)

        tk.Label(f_box, text="Device:", font=("Segoe UI", 8), fg=TEXT_MUTED, bg=BG_PANEL).pack(side="left", padx=(4, 2))
        self.cb_filter_dev = ttk.Combobox(f_box, values=["All"] + self.db.get_device_types(), state="readonly", width=14, font=("Segoe UI", 8))
        self.cb_filter_dev.set(self.filter_device_type)
        self.cb_filter_dev.pack(side="left", padx=(0, 6))
        self.cb_filter_dev.bind("<<ComboboxSelected>>", lambda e: self.on_filter_changed())

        tk.Label(f_box, text="Category:", font=("Segoe UI", 8), fg=TEXT_MUTED, bg=BG_PANEL).pack(side="left", padx=(2, 2))
        self.cb_filter_cat = ttk.Combobox(f_box, values=["All"] + self.db.get_categories(), state="readonly", width=14, font=("Segoe UI", 8))
        self.cb_filter_cat.set(self.filter_category)
        self.cb_filter_cat.pack(side="left", padx=(0, 6))
        self.cb_filter_cat.bind("<<ComboboxSelected>>", lambda e: self.on_filter_changed())

        tk.Label(f_box, text="State:", font=("Segoe UI", 8), fg=TEXT_MUTED, bg=BG_PANEL).pack(side="left", padx=(2, 2))
        self.cb_filter_state = ttk.Combobox(f_box, values=["All", "Working", "Stuck", "Done", "Idle"], state="readonly", width=9, font=("Segoe UI", 8))
        self.cb_filter_state.set(self.filter_status)
        self.cb_filter_state.pack(side="left")
        self.cb_filter_state.bind("<<ComboboxSelected>>", lambda e: self.on_filter_changed())

        # 4. Tab Selector Bar
        tab_bar = tk.Frame(self, bg=BG_PANEL, height=36, highlightthickness=1, highlightbackground=BORDER_COLOR)
        tab_bar.pack(fill="x", padx=12, pady=(0, 4))
        tab_bar.pack_propagate(False)

        self.tab_buttons = {}
        tabs = [
            ("temporal", "📈 Trends"),
            ("device_types", "📟 Device Types"),
            ("problems", "🔍 Diagnostics"),
            ("parts", "📦 Parts"),
            ("department", "🏢 Departments"),
            ("intensity", "🛠️ Intensity"),
            ("root_causes", "🔬 Root Causes")
        ]

        for tab_id, tab_label in tabs:
            btn = tk.Button(
                tab_bar,
                text=tab_label,
                font=FONT_LABEL,
                fg=TEXT_MUTED,
                bg=BG_PANEL,
                activebackground=BG_ACTIVE,
                activeforeground=TEXT_PRIMARY,
                relief="flat",
                padx=8,
                pady=3,
                cursor="hand2",
                command=lambda tid=tab_id: self.switch_tab(tid)
            )
            btn.pack(side="left", padx=2, pady=2)
            self.tab_buttons[tab_id] = btn

        # 5. Main Chart Canvas Area
        canvas_container = tk.Frame(self, bg=BG_PANEL, highlightthickness=1, highlightbackground=BORDER_COLOR)
        canvas_container.pack(fill="both", expand=True, padx=12, pady=(0, 4))

        self.canvas = tk.Canvas(canvas_container, bg=BG_PANEL, highlightthickness=0, height=290)
        self.canvas.pack(fill="both", expand=True, padx=6, pady=6)
        self.canvas.bind("<Configure>", lambda e: self.draw_chart())
        self.canvas.bind("<Motion>", self.on_canvas_motion)
        self.canvas.bind("<Leave>", self.on_canvas_leave)

        # 6. Lower Data Table Section
        self.table_frame = tk.Frame(self, bg=BG_PANEL, height=130, highlightthickness=1, highlightbackground=BORDER_COLOR)
        self.table_frame.pack(fill="x", padx=12, pady=(0, 4))
        self.table_frame.pack_propagate(False)
        self.build_table_view()

        # 7. Bottom Status & Close Action Bar
        btn_bar = tk.Frame(self, bg=BG_PANEL, height=40, highlightthickness=1, highlightbackground=BORDER_COLOR)
        btn_bar.pack(side="bottom", fill="x", padx=12, pady=(0, 8))
        btn_bar.pack_propagate(False)

        self.lbl_status = tk.Label(btn_bar, text="", font=FONT_UI, fg=TEXT_MUTED, bg=BG_PANEL)
        self.lbl_status.pack(side="left", padx=12, pady=6)

        btn_close = tk.Button(
            btn_bar, text="Close", font=FONT_UI, fg=TEXT_PRIMARY, bg=BG_SURFACE,
            activebackground=BG_ACTIVE, relief="flat", padx=16, pady=3, cursor="hand2", command=self.destroy
        )
        btn_close.pack(side="right", padx=10, pady=5)

        btn_refresh = tk.Button(
            btn_bar, text="🔄 Refresh Analytics", font=FONT_UI, fg=BG_MAIN, bg=ACCENT_CYAN,
            activebackground="#79c0ff", relief="flat", padx=14, pady=3, cursor="hand2", command=self.refresh_all
        )
        btn_refresh.pack(side="right", padx=4, pady=5)

        self.switch_tab("temporal")

    def build_kpi_cards(self):
        for w in self.kpi_frame.winfo_children():
            w.destroy()

        analytics = self.get_current_analytics()

        kpis = [
            ("TOTAL WORK ITEMS", str(analytics["total_items"]), ACCENT_CYAN),
            ("WORKING", str(analytics["item_working"]), COLOR_WORKING),
            ("STUCK", str(analytics["item_stuck"]), COLOR_STUCK),
            ("DONE", str(analytics["item_done"]), COLOR_DONE),
            ("IDLE", str(analytics["item_idle"]), COLOR_IDLE),
            ("MAINTENANCE LOGS", str(analytics["maintenance_notes_count"]), ACCENT_MINT),
            ("PARTS CONSUMED", str(analytics["parts_consumed_count"]), ACCENT_GOLD)
        ]

        for i in range(len(kpis)):
            self.kpi_frame.columnconfigure(i, weight=1)

        for col_idx, (title, val, color) in enumerate(kpis):
            card = tk.Frame(self.kpi_frame, bg=BG_SURFACE, highlightthickness=1, highlightbackground=BORDER_COLOR, padx=8, pady=4)
            card.grid(row=0, column=col_idx, sticky="nsew", padx=2, pady=2)
            tk.Label(card, text=title, font=("Segoe UI", 7, "bold"), fg=TEXT_MUTED, bg=BG_SURFACE).pack(anchor="w")
            tk.Label(card, text=val, font=("Segoe UI", 13, "bold"), fg=color, bg=BG_SURFACE).pack(anchor="w")

    def build_table_view(self):
        for w in self.table_frame.winfo_children():
            w.destroy()

        tree_frame = tk.Frame(self.table_frame, bg=BG_PANEL)
        tree_frame.pack(fill="both", expand=True, padx=4, pady=4)

        scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
        self.tree = ttk.Treeview(tree_frame, show="headings", height=4, yscrollcommand=scroll_y.set)
        scroll_y.config(command=self.tree.yview)

        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

    def get_current_analytics(self):
        return self.db.get_work_analytics(
            period=self.selected_period,
            filter_device_type=self.filter_device_type,
            filter_category=self.filter_category,
            filter_status=self.filter_status
        )

    def set_period(self, period_id):
        self.selected_period = period_id
        for pid, btn in self.period_buttons.items():
            if pid == period_id:
                btn.config(bg=BG_ACTIVE, fg=ACCENT_CYAN, font=("Segoe UI", 8, "bold"))
            else:
                btn.config(bg=BG_SURFACE, fg=TEXT_MUTED, font=("Segoe UI", 8))
        self.refresh_all()

    def on_filter_changed(self):
        self.filter_device_type = self.cb_filter_dev.get()
        self.filter_category = self.cb_filter_cat.get()
        self.filter_status = self.cb_filter_state.get()
        self.refresh_all()

    def switch_tab(self, tab_id):
        # Support alias for backward compatibility with 'activity'
        if tab_id == "activity":
            tab_id = "temporal"
        self.current_tab = tab_id
        for tid, btn in self.tab_buttons.items():
            if tid == tab_id:
                btn.config(bg=BG_ACTIVE, fg=ACCENT_CYAN, font=("Segoe UI", 9, "bold"))
            else:
                btn.config(bg=BG_PANEL, fg=TEXT_MUTED, font=FONT_LABEL)

        self.draw_chart()
        self.populate_table()

    def refresh_all(self):
        self.build_kpi_cards()
        self.draw_chart()
        self.populate_table()

    # ==========================================================================
    # CHART RENDERING (Native Tkinter Canvas Vector Graphics)
    # ==========================================================================
    def draw_chart(self):
        self.canvas.delete("all")
        self.chart_items = []

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 50:
            w = max(self.canvas.winfo_reqwidth(), 900)
        if h < 50:
            h = max(self.canvas.winfo_reqheight(), 290)

        analytics = self.get_current_analytics()

        if self.current_tab in ("temporal", "activity"):
            self.render_temporal_chart(analytics, w, h)
        elif self.current_tab == "device_types":
            self.render_device_types_chart(analytics, w, h)
        elif self.current_tab == "problems":
            self.render_problems_chart(analytics, w, h)
        elif self.current_tab == "parts":
            self.render_parts_chart(analytics, w, h)
        elif self.current_tab == "department":
            self.render_department_chart(analytics, w, h)
        elif self.current_tab == "intensity":
            self.render_intensity_chart(analytics, w, h)
        elif self.current_tab == "root_causes":
            self.render_root_causes_chart(analytics, w, h)

    def render_temporal_chart(self, analytics, w, h):
        timeline = analytics["timeline"]
        if not timeline:
            self.draw_empty_state("No service activity recorded for the selected period & filters.")
            return

        period_title = self.selected_period.capitalize()
        self.lbl_status.config(text=f"Showing {period_title} maintenance volume across {len(timeline)} timeline intervals.")

        padding_left = 60
        padding_right = 30
        padding_top = 40
        padding_bottom = 50

        chart_w = w - padding_left - padding_right
        chart_h = h - padding_top - padding_bottom

        max_val = max(entry[1]["total"] for entry in timeline)
        if max_val == 0:
            max_val = 1
        ceiling = max_val + (1 if max_val < 5 else max_val // 4 + 1)

        # Draw Grid Lines
        steps = 4
        for i in range(steps + 1):
            val = int(ceiling * (i / steps))
            y = padding_top + chart_h - (chart_h * (i / steps))
            self.canvas.create_line(padding_left, y, w - padding_right, y, fill="#21262d", dash=(2, 4))
            self.canvas.create_text(padding_left - 8, y, text=str(val), fill=TEXT_MUTED, font=("Segoe UI", 8), anchor="e")

        self.canvas.create_line(padding_left, padding_top, padding_left, h - padding_bottom, fill=BORDER_COLOR)
        self.canvas.create_line(padding_left, h - padding_bottom, w - padding_right, h - padding_bottom, fill=BORDER_COLOR)

        slot_w = chart_w / len(timeline)
        bar_w = min(42, slot_w * 0.65)

        for idx, (b_key, counts) in enumerate(timeline):
            center_x = padding_left + slot_w * idx + slot_w / 2
            x1 = center_x - bar_w / 2
            x2 = center_x + bar_w / 2

            m_cnt = counts["maintenance"]
            q_cnt = counts["quick"]
            tot = counts["total"]

            m_h = (chart_h * (m_cnt / ceiling)) if ceiling else 0
            q_h = (chart_h * (q_cnt / ceiling)) if ceiling else 0

            y_base = h - padding_bottom
            y_m = y_base - m_h
            y_top = y_m - q_h

            if m_cnt > 0:
                self.canvas.create_rectangle(x1, y_m, x2, y_base, fill=ACCENT_MINT, outline="#a6f3b0", width=1)
                tip = f"📅 {b_key}\n🛠️ Maintenance: {m_cnt}\nDone: {counts['done']} | Working: {counts['working']} | Stuck: {counts['stuck']}"
                self.chart_items.append((x1, y_m, x2, y_base, tip))

            if q_cnt > 0:
                self.canvas.create_rectangle(x1, y_top, x2, y_m, fill="#f0883e", outline="#ffa756", width=1)
                self.chart_items.append((x1, y_top, x2, y_m, f"📅 {b_key}\n⚡ Observation Notes: {q_cnt}"))

            if tot > 0:
                self.canvas.create_text(center_x, y_top - 8, text=str(tot), fill=TEXT_PRIMARY, font=("Segoe UI", 8, "bold"))

            # Format X-axis label
            lbl_text = b_key
            if len(timeline) > 12:
                lbl_text = b_key[-5:] if len(b_key) >= 5 else b_key
            self.canvas.create_text(center_x, h - padding_bottom + 14, text=lbl_text, fill=TEXT_MUTED, font=("Segoe UI", 7))

        self.draw_legend([
            ("🛠️ Maintenance Logs", ACCENT_MINT),
            ("⚡ Quick Notes (Observation)", "#f0883e")
        ], w, 14)

    def render_device_types_chart(self, analytics, w, h):
        dev_data = analytics["device_type_work"]
        if not dev_data:
            self.draw_empty_state("No device type records available.")
            return

        self.lbl_status.config(text=f"Showing work distribution across {len(dev_data)} equipment device types.")

        padding_left = 180
        padding_right = 60
        padding_top = 36
        padding_bottom = 30

        chart_w = w - padding_left - padding_right
        chart_h = h - padding_top - padding_bottom

        top_devs = dev_data[:8]
        max_val = max(d[1]["total"] for d in top_devs)
        if max_val == 0:
            max_val = 1
        ceiling = max_val + 1

        slot_h = min(42, chart_h / len(top_devs))
        bar_h = slot_h * 0.6

        for idx, (dtype, counts) in enumerate(top_devs):
            y_center = padding_top + slot_h * idx + slot_h / 2
            y1 = y_center - bar_h / 2
            y2 = y_center + bar_h / 2

            disp_name = (dtype[:22] + "...") if len(dtype) > 24 else dtype
            self.canvas.create_text(padding_left - 10, y_center, text=disp_name, fill=TEXT_PRIMARY, font=("Segoe UI", 8, "bold"), anchor="e")

            bw = chart_w * (counts["total"] / ceiling)
            x_end = padding_left + bw

            self.canvas.create_rectangle(padding_left, y1, x_end, y2, fill=ACCENT_CYAN, outline="#79c0ff")
            tip = f"📟 Device Type: {dtype}\nUnits: {counts['items']}\nTotal Events: {counts['total']}\nWorking: {counts['working']} | Stuck: {counts['stuck']} | Done: {counts['done']}\nParts Replaced: {counts['parts']}"
            self.chart_items.append((padding_left, y1, x_end, y2, tip))

            txt = f"{counts['total']} events ({counts['items']} units)"
            if counts["stuck"] > 0:
                txt += f" • ⚠️ {counts['stuck']} Stuck"
            self.canvas.create_text(x_end + 8, y_center, text=txt, fill=ACCENT_GOLD, font=("Segoe UI", 8), anchor="w")

        self.canvas.create_line(padding_left, padding_top - 10, padding_left, padding_top + slot_h * len(top_devs), fill=BORDER_COLOR)

        self.draw_legend([("Work Events per Device Type", ACCENT_CYAN)], w - 240, 14)

    def render_problems_chart(self, analytics, w, h):
        problems = analytics["problems_analysis"]
        if not problems:
            self.draw_empty_state("No diagnostic problem records recorded yet.")
            return

        self.lbl_status.config(text=f"Showing top recurring equipment failure modes and diagnostic problem reports.")

        padding_left = 220
        padding_right = 60
        padding_top = 36
        padding_bottom = 30

        chart_w = w - padding_left - padding_right
        chart_h = h - padding_top - padding_bottom

        top_probs = problems[:8]
        max_val = max(p[1] for p in top_probs)
        ceiling = max_val + 1

        slot_h = min(42, chart_h / len(top_probs))
        bar_h = slot_h * 0.6

        for idx, (p_name, count, dtypes, latest) in enumerate(top_probs):
            y_center = padding_top + slot_h * idx + slot_h / 2
            y1 = y_center - bar_h / 2
            y2 = y_center + bar_h / 2

            disp_name = (p_name[:26] + "...") if len(p_name) > 28 else p_name
            self.canvas.create_text(padding_left - 10, y_center, text=disp_name, fill=TEXT_PRIMARY, font=("Segoe UI", 8, "bold"), anchor="e")

            bw = chart_w * (count / ceiling)
            x_end = padding_left + bw

            self.canvas.create_rectangle(padding_left, y1, x_end, y2, fill=ACCENT_CORAL, outline="#ff7b72")
            tip = f"🔍 Malfunction: {p_name}\nOccurrences: {count}\nAffected Device Types: {', '.join(dtypes) or 'None'}\nLatest: {latest or 'Unknown'}"
            self.chart_items.append((padding_left, y1, x_end, y2, tip))

            txt = f"{count} case{'s' if count != 1 else ''} • {', '.join(dtypes[:2])}"
            self.canvas.create_text(x_end + 8, y_center, text=txt, fill=ACCENT_GOLD, font=("Segoe UI", 8), anchor="w")

        self.canvas.create_line(padding_left, padding_top - 10, padding_left, padding_top + slot_h * len(top_probs), fill=BORDER_COLOR)

        self.draw_legend([("Malfunction Occurrences", ACCENT_CORAL)], w - 220, 14)

    def render_parts_chart(self, analytics, w, h):
        parts_list = analytics["parts_list"]
        if not parts_list:
            self.draw_empty_state("No parts or materials consumed logged yet.")
            return

        self.lbl_status.config(text=f"Showing {len(parts_list)} recorded parts and materials replacement jobs.")

        padding_left = 60
        padding_right = 40
        padding_top = 40
        padding_bottom = 40

        chart_w = w - padding_left - padding_right
        chart_h = h - padding_top - padding_bottom

        tot_notes = analytics["total_notes"]
        parts_cnt = analytics["parts_consumed_count"]
        no_parts_cnt = tot_notes - parts_cnt

        center_x = padding_left + 130
        center_y = padding_top + chart_h / 2
        radius = min(85, chart_h / 2 - 10)

        p_angle = (parts_cnt / tot_notes * 360) if tot_notes else 0
        np_angle = 360 - p_angle

        self.canvas.create_arc(
            center_x - radius, center_y - radius, center_x + radius, center_y + radius,
            start=0, extent=p_angle, fill=ACCENT_GOLD, outline="#ffe58f"
        )
        self.canvas.create_arc(
            center_x - radius, center_y - radius, center_x + radius, center_y + radius,
            start=p_angle, extent=np_angle, fill=BG_SURFACE, outline=BORDER_COLOR
        )

        hole_r = radius * 0.55
        self.canvas.create_oval(
            center_x - hole_r, center_y - hole_r, center_x + hole_r, center_y + hole_r,
            fill=BG_PANEL, outline=BORDER_COLOR
        )
        pct = (parts_cnt / tot_notes * 100) if tot_notes else 0
        self.canvas.create_text(center_x, center_y - 6, text=f"{pct:.0f}%", fill=ACCENT_GOLD, font=("Segoe UI", 12, "bold"))
        self.canvas.create_text(center_x, center_y + 10, text="PARTS RATIO", fill=TEXT_MUTED, font=("Segoe UI", 6, "bold"))

        info_x = center_x + radius + 40
        self.canvas.create_text(info_x, center_y - 50, text="PARTS & CONSUMABLES LOGISTICS", font=("Segoe UI", 10, "bold"), fill=ACCENT_CYAN, anchor="w")
        self.canvas.create_text(info_x, center_y - 25, text=f"• Maintenance Events with Parts: {parts_cnt}", font=FONT_UI, fill=TEXT_PRIMARY, anchor="w")
        self.canvas.create_text(info_x, center_y - 2, text=f"• Routine Service / Inspections: {no_parts_cnt}", font=FONT_UI, fill=TEXT_MUTED, anchor="w")
        self.canvas.create_text(info_x, center_y + 20, text=f"• Total Logged Events: {tot_notes}", font=FONT_UI, fill=TEXT_PRIMARY, anchor="w")

        top_p = analytics["parts_frequency"][:3]
        top_str = ", ".join(f"{p[0]} (x{p[1]})" for p in top_p) if top_p else "None"
        self.canvas.create_text(info_x, center_y + 44, text=f"• Top Consumed: {top_str}", font=("Segoe UI", 8, "italic"), fill=ACCENT_GOLD, anchor="w")

    def render_department_chart(self, analytics, w, h):
        dept_data = analytics["dept_work"]
        if not dept_data:
            self.draw_empty_state("No department work logged yet.")
            return

        self.lbl_status.config(text=f"Showing work actions performed across {len(dept_data)} departments.")

        padding_left = 180
        padding_right = 60
        padding_top = 36
        padding_bottom = 30

        chart_w = w - padding_left - padding_right
        chart_h = h - padding_top - padding_bottom

        max_val = max(d[1]["total"] for d in dept_data)
        if max_val == 0:
            max_val = 1
        ceiling = max_val + 1

        top_depts = dept_data[:8]
        slot_h = min(42, chart_h / len(top_depts))
        bar_h = slot_h * 0.6

        for idx, (dept_name, counts) in enumerate(top_depts):
            y_center = padding_top + slot_h * idx + slot_h / 2
            y1 = y_center - bar_h / 2
            y2 = y_center + bar_h / 2

            m_cnt = counts["maintenance"]
            q_cnt = counts["quick"]
            tot = counts["total"]

            w_m = (chart_w * (m_cnt / ceiling)) if ceiling else 0
            w_q = (chart_w * (q_cnt / ceiling)) if ceiling else 0

            disp_name = (dept_name[:22] + "...") if len(dept_name) > 24 else dept_name
            self.canvas.create_text(padding_left - 10, y_center, text=disp_name, fill=TEXT_PRIMARY, font=("Segoe UI", 8, "bold"), anchor="e")

            x_start = padding_left
            x_m = x_start + w_m
            x_end = x_m + w_q

            if m_cnt > 0:
                self.canvas.create_rectangle(x_start, y1, x_m, y2, fill=ACCENT_CYAN, outline="#79c0ff")
                self.chart_items.append((x_start, y1, x_m, y2, f"🏢 {dept_name}\n🛠️ Maintenance: {m_cnt}"))

            if q_cnt > 0:
                self.canvas.create_rectangle(x_m, y1, x_end, y2, fill="#f0883e", outline="#ffa756")
                self.chart_items.append((x_m, y1, x_end, y2, f"🏢 {dept_name}\n⚡ Quick Notes (Observation): {q_cnt}"))

            self.canvas.create_text(x_end + 8, y_center, text=f"{tot} logs ({counts['items']} units)", fill=ACCENT_GOLD, font=("Segoe UI", 8), anchor="w")

        self.canvas.create_line(padding_left, padding_top - 10, padding_left, padding_top + slot_h * len(top_depts), fill=BORDER_COLOR)

        self.draw_legend([
            ("🛠️ Maintenance", ACCENT_CYAN),
            ("⚡ Quick Notes (Observation)", "#f0883e")
        ], y=14)

    def render_intensity_chart(self, analytics, w, h):
        items = analytics["item_intensity"]
        top_items = [it for it in items if it["total_notes"] > 0][:8]
        if not top_items:
            self.draw_empty_state("No maintenance logs recorded for equipment yet.")
            return

        self.lbl_status.config(text=f"Showing top {len(top_items)} equipment units by maintenance frequency.")

        padding_left = 200
        padding_right = 60
        padding_top = 36
        padding_bottom = 30

        chart_w = w - padding_left - padding_right
        chart_h = h - padding_top - padding_bottom

        max_val = max(it["total_notes"] for it in top_items)
        ceiling = max_val + 1

        slot_h = min(42, chart_h / len(top_items))
        bar_h = slot_h * 0.6

        for idx, it in enumerate(top_items):
            y_center = padding_top + slot_h * idx + slot_h / 2
            y1 = y_center - bar_h / 2
            y2 = y_center + bar_h / 2

            tag = f"[{it['queue_number']}] {it['item_name'][:16]} ({it['device_type'][:10]})"
            self.canvas.create_text(padding_left - 10, y_center, text=tag, fill=TEXT_PRIMARY, font=("Segoe UI", 8, "bold"), anchor="e")

            bw = chart_w * (it["total_notes"] / ceiling)
            x_end = padding_left + bw

            fill_c = ACCENT_GOLD if it["parts_actions"] > 0 else ACCENT_CYAN
            self.canvas.create_rectangle(padding_left, y1, x_end, y2, fill=fill_c, outline="#ffe58f" if fill_c == ACCENT_GOLD else "#79c0ff")

            tip = f"🪐 {it['queue_number']} — {it['item_name']}\nDevice: {it['device_type']} | Category: {it['category']}\nState: {it['work_status']}\nTotal Events: {it['total_notes']} | Parts: {it['parts_actions']}"
            self.chart_items.append((padding_left, y1, x_end, y2, tip))

            txt = f"{it['total_notes']} events • State: {it['work_status']}"
            self.canvas.create_text(x_end + 8, y_center, text=txt, fill=TEXT_MUTED, font=("Segoe UI", 8), anchor="w")

        self.canvas.create_line(padding_left, padding_top - 10, padding_left, padding_top + slot_h * len(top_items), fill=BORDER_COLOR)

        self.draw_legend([
            ("Parts Consumed", ACCENT_GOLD),
            ("Standard Service", ACCENT_CYAN)
        ], w - 220, 14)

    def render_root_causes_chart(self, analytics, w, h):
        rc_data = analytics["root_causes"]
        if not rc_data:
            self.draw_empty_state("No root cause analyses recorded yet.")
            return

        self.lbl_status.config(text=f"Showing top {len(rc_data)} identified root causes.")

        padding_left = 220
        padding_right = 60
        padding_top = 36
        padding_bottom = 30

        chart_w = w - padding_left - padding_right
        chart_h = h - padding_top - padding_bottom

        max_val = max(c[1] for c in rc_data)
        ceiling = max_val + 1

        top_rc = rc_data[:8]
        slot_h = min(42, chart_h / len(top_rc))
        bar_h = slot_h * 0.6

        for idx, (rc_name, count) in enumerate(top_rc):
            y_center = padding_top + slot_h * idx + slot_h / 2
            y1 = y_center - bar_h / 2
            y2 = y_center + bar_h / 2

            disp_name = (rc_name[:28] + "...") if len(rc_name) > 30 else rc_name
            self.canvas.create_text(padding_left - 10, y_center, text=disp_name, fill=TEXT_PRIMARY, font=("Segoe UI", 8, "bold"), anchor="e")

            bw = chart_w * (count / ceiling)
            x_end = padding_left + bw

            self.canvas.create_rectangle(padding_left, y1, x_end, y2, fill=ACCENT_CORAL, outline="#ff7b72")
            self.chart_items.append((padding_left, y1, x_end, y2, f"🔬 Root Cause:\n{rc_name}\nOccurrences: {count}"))

            self.canvas.create_text(x_end + 8, y_center, text=f"{count} case{'s' if count != 1 else ''}", fill=ACCENT_CORAL, font=("Segoe UI", 8), anchor="w")

        self.canvas.create_line(padding_left, padding_top - 10, padding_left, padding_top + slot_h * len(top_rc), fill=BORDER_COLOR)

    def draw_empty_state(self, message):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        self.canvas.create_text(w / 2, h / 2 - 10, text="🪐 NO DATA AVAILABLE", font=("Segoe UI", 11, "bold"), fill=TEXT_MUTED)
        self.canvas.create_text(w / 2, h / 2 + 14, text=message, font=FONT_UI, fill=TEXT_DIM, justify="center")

    def draw_legend(self, items, x=None, y=14):
        # Calculate dynamic item widths so text never overlaps or clips
        item_widths = [int(len(label) * 7.5 + 28) for label, _ in items]
        total_w = sum(item_widths) + (len(items) - 1) * 16

        canvas_w = self.canvas.winfo_width()
        if canvas_w < 100:
            canvas_w = 900

        # Anchor nicely from the right edge with 24px margin
        start_x = max(180, canvas_w - total_w - 24)
        curr_x = start_x

        for idx, (label, color) in enumerate(items):
            self.canvas.create_rectangle(curr_x, y, curr_x + 12, y + 12, fill=color, outline="")
            self.canvas.create_text(curr_x + 18, y + 6, text=label, fill=TEXT_MUTED, font=("Segoe UI", 8), anchor="w")
            curr_x += item_widths[idx] + 16

    # ==========================================================================
    # INTERACTIVE HOVER TOOLTIPS
    # ==========================================================================
    def on_canvas_motion(self, event):
        self.canvas.delete("tooltip")
        mx, my = event.x, event.y

        for x1, y1, x2, y2, text in self.chart_items:
            if x1 <= mx <= x2 and y1 <= my <= y2:
                tt_x = min(mx + 12, self.canvas.winfo_width() - 190)
                tt_y = max(my - 50, 10)

                lines = text.split("\n")
                box_h = 16 * len(lines) + 12
                box_w = max(len(l) for l in lines) * 7 + 16

                self.canvas.create_rectangle(tt_x, tt_y, tt_x + box_w, tt_y + box_h, fill="#0d1117", outline=BORDER_ACTIVE, width=1, tags="tooltip")
                for i, line in enumerate(lines):
                    self.canvas.create_text(tt_x + 8, tt_y + 8 + i * 16, text=line, font=("Segoe UI", 8), fill=TEXT_PRIMARY, anchor="nw", tags="tooltip")
                break

    def on_canvas_leave(self, event):
        self.canvas.delete("tooltip")

    # ==========================================================================
    # LOWER DATA TABLE POPULATION
    # ==========================================================================
    def populate_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        analytics = self.get_current_analytics()

        if self.current_tab in ("temporal", "activity"):
            self.tree["columns"] = ("period", "total", "maintenance", "quick", "working", "stuck", "done", "parts")
            self.tree.heading("period", text="Period Interval")
            self.tree.heading("total", text="Total Events")
            self.tree.heading("maintenance", text="Maint Records")
            self.tree.heading("quick", text="Quick Notes")
            self.tree.heading("working", text="Working")
            self.tree.heading("stuck", text="Stuck")
            self.tree.heading("done", text="Done")
            self.tree.heading("parts", text="Parts Jobs")

            self.tree.column("period", width=130)
            self.tree.column("total", width=90)
            self.tree.column("maintenance", width=100)
            self.tree.column("quick", width=90)
            self.tree.column("working", width=75)
            self.tree.column("stuck", width=75)
            self.tree.column("done", width=75)
            self.tree.column("parts", width=85)

            for b_key, counts in reversed(analytics["timeline"]):
                self.tree.insert("", "end", values=(
                    b_key, counts["total"], counts["maintenance"], counts["quick"],
                    counts["working"], counts["stuck"], counts["done"], counts["parts"]
                ))

        elif self.current_tab == "device_types":
            self.tree["columns"] = ("dtype", "items", "total", "working", "stuck", "done", "parts")
            self.tree.heading("dtype", text="Device Type")
            self.tree.heading("items", text="Units Tracked")
            self.tree.heading("total", text="Total Work Events")
            self.tree.heading("working", text="Working")
            self.tree.heading("stuck", text="Stuck")
            self.tree.heading("done", text="Done")
            self.tree.heading("parts", text="Parts Replaced")

            self.tree.column("dtype", width=220)
            self.tree.column("items", width=110)
            self.tree.column("total", width=130)
            self.tree.column("working", width=80)
            self.tree.column("stuck", width=80)
            self.tree.column("done", width=80)
            self.tree.column("parts", width=110)

            for dtype, counts in analytics["device_type_work"]:
                self.tree.insert("", "end", values=(
                    dtype, counts["items"], counts["total"],
                    counts["working"], counts["stuck"], counts["done"], counts["parts"]
                ))

        elif self.current_tab == "problems":
            self.tree["columns"] = ("prob", "occurrences", "devices", "latest")
            self.tree.heading("prob", text="Diagnostic Malfunction / Problem")
            self.tree.heading("occurrences", text="Occurrences")
            self.tree.heading("devices", text="Affected Device Types")
            self.tree.heading("latest", text="Latest Incident")

            self.tree.column("prob", width=340)
            self.tree.column("occurrences", width=100)
            self.tree.column("devices", width=240)
            self.tree.column("latest", width=140)

            for p_name, count, dtypes, latest in analytics["problems_analysis"]:
                self.tree.insert("", "end", values=(p_name, count, ", ".join(dtypes), latest))

        elif self.current_tab == "parts":
            self.tree["columns"] = ("timestamp", "queue", "item", "dtype", "parts", "state")
            self.tree.heading("timestamp", text="Date & Time")
            self.tree.heading("queue", text="Queue #")
            self.tree.heading("item", text="Equipment")
            self.tree.heading("dtype", text="Device Type")
            self.tree.heading("parts", text="Parts Consumed")
            self.tree.heading("state", text="Work State")

            self.tree.column("timestamp", width=130)
            self.tree.column("queue", width=80)
            self.tree.column("item", width=180)
            self.tree.column("dtype", width=130)
            self.tree.column("parts", width=240)
            self.tree.column("state", width=80)

            for p in reversed(analytics["parts_list"]):
                self.tree.insert("", "end", values=(
                    p["timestamp"], p["queue_number"], p["item_name"],
                    p["device_type"], p["parts"], p.get("work_status", "Done")
                ))

        elif self.current_tab == "department":
            self.tree["columns"] = ("dept", "items", "total_logs", "working", "stuck", "done", "idle")
            self.tree.heading("dept", text="Department")
            self.tree.heading("items", text="Units Tracked")
            self.tree.heading("total_logs", text="Total Work Events")
            self.tree.heading("working", text="Working")
            self.tree.heading("stuck", text="Stuck")
            self.tree.heading("done", text="Done")
            self.tree.heading("idle", text="Idle")

            self.tree.column("dept", width=200)
            self.tree.column("items", width=100)
            self.tree.column("total_logs", width=120)
            self.tree.column("working", width=80)
            self.tree.column("stuck", width=80)
            self.tree.column("done", width=80)
            self.tree.column("idle", width=80)

            for dept_name, counts in analytics["dept_work"]:
                self.tree.insert("", "end", values=(
                    dept_name, counts["items"], counts["total"],
                    counts["working"], counts["stuck"], counts["done"], counts["idle"]
                ))

        elif self.current_tab == "intensity":
            self.tree["columns"] = ("queue", "name", "dtype", "category", "dept", "state", "notes")
            self.tree.heading("queue", text="Queue #")
            self.tree.heading("name", text="Item Name")
            self.tree.heading("dtype", text="Device Type")
            self.tree.heading("category", text="Category")
            self.tree.heading("dept", text="Department")
            self.tree.heading("state", text="Work State")
            self.tree.heading("notes", text="Total Events")

            self.tree.column("queue", width=80)
            self.tree.column("name", width=170)
            self.tree.column("dtype", width=120)
            self.tree.column("category", width=120)
            self.tree.column("dept", width=140)
            self.tree.column("state", width=80)
            self.tree.column("notes", width=90)

            for it in analytics["item_intensity"]:
                self.tree.insert("", "end", values=(
                    it["queue_number"], it["item_name"], it["device_type"],
                    it["category"], it["department"], it["work_status"], it["total_notes"]
                ))

        elif self.current_tab == "root_causes":
            self.tree["columns"] = ("root_cause", "frequency", "pct")
            self.tree.heading("root_cause", text="Identified Root Cause")
            self.tree.heading("frequency", text="Occurrences")
            self.tree.heading("pct", text="Share of Diagnosed Issues")

            self.tree.column("root_cause", width=420)
            self.tree.column("frequency", width=140)
            self.tree.column("pct", width=180)

            tot_rc = sum(c[1] for c in analytics["root_causes"])
            for rc, count in analytics["root_causes"]:
                pct = f"{(count / tot_rc * 100):.1f}%" if tot_rc else "0%"
                self.tree.insert("", "end", values=(rc, count, pct))
