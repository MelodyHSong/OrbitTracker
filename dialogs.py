# 🪐 OrbitTracker — Modal Dialogs
# Author: MelodyHSong
# File Name: dialogs.py
# Description: Cosmic dark themed modal dialogs for Adding/Editing Work Items,
#              adding Service Log notes, and managing custom columns.

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

FONT_TITLE = ("Segoe UI", 12, "bold")
FONT_LABEL = ("Segoe UI", 9, "bold")
FONT_UI = ("Segoe UI", 9)
FONT_CODE = ("Consolas", 9)


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

        # Determine dimensions based on number of custom columns
        custom_count = len(db.custom_columns)
        base_h = 600 if item else 720
        target_h = min(820, base_h + custom_count * 38)
        center_window_on_parent(self, parent, width=580, height=target_h)

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

        # Bottom Button Bar (Packed at bottom before scrollable container)
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

        # Scrollable form container for small displays / many custom columns
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

        # Row 1: Queue Number & Status
        r1 = tk.Frame(form_frame, bg=BG_MAIN)
        r1.pack(fill="x", pady=4)

        # Queue Number (Auto generated, user can edit)
        f_q = tk.Frame(r1, bg=BG_MAIN)
        f_q.pack(side="left", fill="x", expand=True, padx=(0, 6))
        tk.Label(f_q, text="Queue Number (Auto-Generated)", font=FONT_LABEL, fg=TEXT_MUTED, bg=BG_MAIN).pack(anchor="w")
        self.entry_queue = tk.Entry(f_q, font=FONT_UI, bg=BG_SURFACE, fg=ACCENT_GOLD, insertbackground=TEXT_PRIMARY,
                                    relief="flat", highlightthickness=1, highlightbackground=BORDER_COLOR)
        self.entry_queue.pack(fill="x", pady=2, ipady=4)
        init_q = self.item.queue_number if self.item else self.db.peek_next_queue_number()
        self.entry_queue.insert(0, init_q)

        # Status
        f_st = tk.Frame(r1, bg=BG_MAIN, width=150)
        f_st.pack(side="right", fill="x", padx=(6, 0))
        tk.Label(f_st, text="Status", font=FONT_LABEL, fg=TEXT_MUTED, bg=BG_MAIN).pack(anchor="w")
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

        # Row 5: Department
        r5 = tk.Frame(form_frame, bg=BG_MAIN)
        r5.pack(fill="x", pady=4)
        tk.Label(r5, text="Department", font=FONT_LABEL, fg=TEXT_MUTED, bg=BG_MAIN).pack(anchor="w")
        self.dept_var = tk.StringVar(value=self.item.department if self.item else "")
        self.cb_dept = ttk.Combobox(r5, textvariable=self.dept_var, values=self.existing_depts, font=FONT_UI)
        self.cb_dept.pack(fill="x", pady=2, ipady=3)

        # Row 6: Dynamic Custom Columns (if any defined)
        if self.db.custom_columns:
            sep_frame = tk.Frame(form_frame, bg=BG_MAIN)
            sep_frame.pack(fill="x", pady=(10, 4))
            tk.Label(sep_frame, text="CUSTOM USER ATTRIBUTES", font=FONT_LABEL, fg=ACCENT_GOLD, bg=BG_MAIN).pack(anchor="w")

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

        # Row 7: Initial Service Log Note (shown when creating new item)
        if not self.item:
            box_note = tk.Frame(form_frame, bg=BG_PANEL, highlightthickness=1, highlightbackground=BORDER_COLOR, padx=10, pady=8)
            box_note.pack(fill="x", pady=(10, 4))

            tk.Label(
                box_note,
                text="INITIAL MAINTENANCE / SERVICE LOG (OPTIONAL)",
                font=FONT_LABEL,
                fg=ACCENT_CYAN,
                bg=BG_PANEL
            ).pack(anchor="w", pady=(0, 2))

            tk.Label(
                box_note,
                text="If logging initial work upon item intake, specify the fields below:",
                font=("Segoe UI", 8),
                fg=TEXT_MUTED,
                bg=BG_PANEL
            ).pack(anchor="w", pady=(0, 6))

            # Problem
            tk.Label(box_note, text="Problem / Malfunction *", font=FONT_LABEL, fg=TEXT_MUTED, bg=BG_PANEL).pack(anchor="w")
            self.entry_init_problem = tk.Entry(box_note, font=FONT_UI, bg=BG_SURFACE, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                                               relief="flat", highlightthickness=1, highlightbackground=BORDER_COLOR)
            self.entry_init_problem.pack(fill="x", pady=2, ipady=3)

            # Root Cause
            tk.Label(box_note, text="Root Cause", font=FONT_LABEL, fg=TEXT_MUTED, bg=BG_PANEL).pack(anchor="w", pady=(4, 0))
            self.entry_init_root = tk.Entry(box_note, font=FONT_UI, bg=BG_SURFACE, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                                            relief="flat", highlightthickness=1, highlightbackground=BORDER_COLOR)
            self.entry_init_root.pack(fill="x", pady=2, ipady=3)

            # Action Taken
            tk.Label(box_note, text="Action Taken", font=FONT_LABEL, fg=TEXT_MUTED, bg=BG_PANEL).pack(anchor="w", pady=(4, 0))
            self.entry_init_action = tk.Entry(box_note, font=FONT_UI, bg=BG_SURFACE, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                                              relief="flat", highlightthickness=1, highlightbackground=BORDER_COLOR)
            self.entry_init_action.pack(fill="x", pady=2, ipady=3)

            # Parts Consumed
            tk.Label(box_note, text="Parts / Materials Consumed", font=FONT_LABEL, fg=TEXT_MUTED, bg=BG_PANEL).pack(anchor="w", pady=(4, 0))
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

        # Collect custom fields
        custom_vals = {}
        for col_id, ent in self.custom_entries.items():
            custom_vals[col_id] = ent.get().strip()

        initial_note_data = None
        if not self.item and hasattr(self, "entry_init_problem"):
            prob = self.entry_init_problem.get().strip()
            root = self.entry_init_root.get().strip()
            act = self.entry_init_action.get().strip()
            parts = self.entry_init_parts.get().strip()

            # If any maintenance field is entered, Problem is required
            if (root or act or parts) and not prob:
                messagebox.showwarning("Problem Required", "Please specify the Problem for the initial service note.", parent=self)
                self.entry_init_problem.focus_set()
                return

            if prob:
                initial_note_data = {
                    "note_type": "maintenance",
                    "problem": prob,
                    "root_cause": root,
                    "action_taken": act,
                    "parts_consumed": parts
                }

        self.result = {
            "queue_number": queue_num,
            "moc_number": moc_num,
            "st_number": st_num,
            "item_name": item_name,
            "make_and_model": make_model,
            "status": status,
            "department": dept,
            "custom_fields": custom_vals,
            "initial_note_data": initial_note_data,
            "initial_note": initial_note_data["problem"] if initial_note_data else ""
        }
        self.destroy()


class ServiceNoteDialog(BaseDialog):
    """Modal dialog for adding or editing a structured maintenance record or quick note."""
    def __init__(self, parent, item, note=None):
        is_quick = note and note.note_type == "quick"
        title = "Edit Quick Note" if is_quick else ("Edit Maintenance Log" if note else "Add Maintenance Log")
        super().__init__(parent, title=title)
        self.item = item
        self.note = note
        self.is_quick = is_quick

        target_h = 360 if self.is_quick else 560
        center_window_on_parent(self, parent, width=560, height=target_h)
        self.build_ui()
        self.grab_set()

    def build_ui(self):
        # Header banner
        header = tk.Frame(self, bg=BG_PANEL, height=52, highlightthickness=1, highlightbackground=BORDER_COLOR)
        header.pack(side="top", fill="x", padx=12, pady=(12, 8))
        header.pack_propagate(False)

        if self.is_quick:
            title = "⚡ EDIT QUICK NOTE"
            color = "#bc8cff"
        elif self.note:
            title = "🛠️ EDIT MAINTENANCE LOG"
            color = ACCENT_GOLD
        else:
            title = "🛠️ ADD MAINTENANCE LOG"
            color = ACCENT_CYAN

        lbl_title = tk.Label(header, text=title, font=FONT_TITLE, fg=color, bg=BG_PANEL)
        lbl_title.pack(side="left", padx=14, pady=10)

        item_tag = f"[{self.item.queue_number}] {self.item.item_name[:22]}"
        lbl_badge = tk.Label(header, text=item_tag, font=FONT_CODE, fg=TEXT_MUTED, bg=BG_SURFACE, padx=8, pady=3)
        lbl_badge.pack(side="right", padx=14, pady=10)

        # Button Bar
        btn_bar = tk.Frame(self, bg=BG_PANEL, height=50, highlightthickness=1, highlightbackground=BORDER_COLOR)
        btn_bar.pack(side="bottom", fill="x", padx=12, pady=(4, 12))
        btn_bar.pack_propagate(False)

        btn_cancel = tk.Button(
            btn_bar, text="Cancel", font=FONT_UI, fg=TEXT_PRIMARY, bg=BG_SURFACE,
            activebackground=BG_ACTIVE, relief="flat", padx=12, pady=4, cursor="hand2", command=self.destroy
        )
        btn_cancel.pack(side="right", padx=10, pady=8)

        save_btn_text = "Update Note" if self.note else "Save Record"
        btn_save = tk.Button(
            btn_bar, text=save_btn_text, font=("Segoe UI", 9, "bold"), fg=BG_MAIN, bg=ACCENT_CYAN,
            activebackground="#79c0ff", relief="flat", padx=16, pady=4, cursor="hand2", command=self.on_save
        )
        btn_save.pack(side="right", padx=4, pady=8)

        # Form
        form = tk.Frame(self, bg=BG_MAIN)
        form.pack(side="top", fill="both", expand=True, padx=14, pady=4)

        # Timestamp row
        ts_frame = tk.Frame(form, bg=BG_MAIN)
        ts_frame.pack(fill="x", pady=(0, 6))
        tk.Label(ts_frame, text="Timestamp", font=FONT_LABEL, fg=TEXT_MUTED, bg=BG_MAIN).pack(side="left")

        now_str = self.note.timestamp if self.note else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.entry_ts = tk.Entry(ts_frame, font=FONT_CODE, bg=BG_SURFACE, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                                 width=22, relief="flat", highlightthickness=1, highlightbackground=BORDER_COLOR)
        self.entry_ts.pack(side="right", ipady=3)
        self.entry_ts.insert(0, now_str)

        if self.is_quick:
            # Quick Note Editor
            tk.Label(form, text="Quick Note Content *", font=FONT_LABEL, fg=TEXT_MUTED, bg=BG_MAIN).pack(anchor="w")
            self.txt_quick = tk.Text(form, font=FONT_UI, bg=BG_SURFACE, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                                     relief="flat", highlightthickness=1, highlightbackground=BORDER_COLOR, wrap="word", height=6)
            self.txt_quick.pack(fill="both", expand=True, pady=4)
            if self.note:
                self.txt_quick.insert("1.0", self.note.quick_note or self.note.note)
            self.txt_quick.focus_set()
            self.txt_quick.bind("<Control-Return>", lambda e: (self.on_save(), "break"))
        else:
            # Field 1: Problem (Required)
            f_prob = tk.Frame(form, bg=BG_MAIN)
            f_prob.pack(fill="x", pady=(0, 4))
            tk.Label(f_prob, text="Problem / Malfunction Description *", font=FONT_LABEL, fg=ACCENT_GOLD, bg=BG_MAIN).pack(anchor="w")
            self.txt_problem = tk.Text(f_prob, font=FONT_UI, bg=BG_SURFACE, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                                       relief="flat", highlightthickness=1, highlightbackground=BORDER_COLOR, wrap="word", height=3)
            self.txt_problem.pack(fill="x", pady=2)
            if self.note:
                self.txt_problem.insert("1.0", self.note.problem or self.note.note)
            self.txt_problem.focus_set()
            self.txt_problem.bind("<Control-Return>", lambda e: (self.on_save(), "break"))

            # Field 2: Root Cause (Optional)
            f_root = tk.Frame(form, bg=BG_MAIN)
            f_root.pack(fill="x", pady=(2, 4))
            tk.Label(f_root, text="Root Cause Analysis (Optional)", font=FONT_LABEL, fg=TEXT_MUTED, bg=BG_MAIN).pack(anchor="w")
            self.txt_root = tk.Text(f_root, font=FONT_UI, bg=BG_SURFACE, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                                    relief="flat", highlightthickness=1, highlightbackground=BORDER_COLOR, wrap="word", height=2)
            self.txt_root.pack(fill="x", pady=2)
            if self.note:
                self.txt_root.insert("1.0", self.note.root_cause)
            self.txt_root.bind("<Control-Return>", lambda e: (self.on_save(), "break"))

            # Field 3: Action Taken (Optional)
            f_act = tk.Frame(form, bg=BG_MAIN)
            f_act.pack(fill="x", pady=(2, 4))
            tk.Label(f_act, text="Action Taken / Maintenance Performed (Optional)", font=FONT_LABEL, fg=TEXT_MUTED, bg=BG_MAIN).pack(anchor="w")
            self.txt_action = tk.Text(f_act, font=FONT_UI, bg=BG_SURFACE, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                                      relief="flat", highlightthickness=1, highlightbackground=BORDER_COLOR, wrap="word", height=3)
            self.txt_action.pack(fill="x", pady=2)
            if self.note:
                self.txt_action.insert("1.0", self.note.action_taken)
            self.txt_action.bind("<Control-Return>", lambda e: (self.on_save(), "break"))

            # Field 4: Parts Consumed (Optional)
            f_parts = tk.Frame(form, bg=BG_MAIN)
            f_parts.pack(fill="x", pady=(2, 4))
            tk.Label(f_parts, text="Parts / Materials Consumed (Optional)", font=FONT_LABEL, fg=TEXT_MUTED, bg=BG_MAIN).pack(anchor="w")
            self.entry_parts = tk.Entry(f_parts, font=FONT_UI, bg=BG_SURFACE, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                                        relief="flat", highlightthickness=1, highlightbackground=BORDER_COLOR)
            self.entry_parts.pack(fill="x", pady=2, ipady=3)
            if self.note:
                self.entry_parts.insert(0, self.note.parts_consumed)
            self.entry_parts.bind("<Control-Return>", lambda e: (self.on_save(), "break"))

    def on_save(self):
        ts = self.entry_ts.get().strip() or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if self.is_quick:
            text = self.txt_quick.get("1.0", "end-1c").strip()
            if not text:
                messagebox.showwarning("Empty Note", "Please enter quick note text.", parent=self)
                self.txt_quick.focus_set()
                return
            self.result = {
                "note_type": "quick",
                "quick_note": text,
                "note": text,
                "timestamp": ts
            }
        else:
            problem = self.txt_problem.get("1.0", "end-1c").strip()
            if not problem:
                messagebox.showwarning("Required Field", "Please enter the Problem description (Required*).", parent=self)
                self.txt_problem.focus_set()
                return

            root_cause = self.txt_root.get("1.0", "end-1c").strip()
            action_taken = self.txt_action.get("1.0", "end-1c").strip()
            parts_consumed = self.entry_parts.get().strip()

            self.result = {
                "note_type": "maintenance",
                "problem": problem,
                "root_cause": root_cause,
                "action_taken": action_taken,
                "parts_consumed": parts_consumed,
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
        # Header banner
        header = tk.Frame(self, bg=BG_PANEL, height=52, highlightthickness=1, highlightbackground=BORDER_COLOR)
        header.pack(fill="x", padx=12, pady=(12, 8))
        header.pack_propagate(False)

        lbl_title = tk.Label(header, text="⚙️ CUSTOM DATABASE COLUMNS", font=FONT_TITLE, fg=ACCENT_CYAN, bg=BG_PANEL)
        lbl_title.pack(side="left", padx=14, pady=10)

        # Content
        content = tk.Frame(self, bg=BG_MAIN)
        content.pack(fill="both", expand=True, padx=14, pady=4)

        # Explanatory note
        lbl_info = tk.Label(
            content,
            text="Pre-defined core columns (Queue #, MOC #, ST #, Item Name, Make/Model, Status, Department, Service Log) are permanently maintained. Below are user-added custom columns:",
            font=FONT_UI,
            fg=TEXT_MUTED,
            bg=BG_MAIN,
            wraplength=490,
            justify="left"
        )
        lbl_info.pack(anchor="w", pady=(0, 8))

        # List of existing custom columns
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

        # Add New Column Card
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

        # Bottom Button Bar
        btn_bar = tk.Frame(self, bg=BG_PANEL, height=50, highlightthickness=1, highlightbackground=BORDER_COLOR)
        btn_bar.pack(side="bottom", fill="x", padx=12, pady=(4, 12))
        btn_bar.pack_propagate(False)

        btn_del = tk.Button(
            btn_bar, text="Delete Selected Column", font=FONT_UI, fg=ACCENT_CORAL, bg=BG_SURFACE,
            activebackground=BG_ACTIVE, relief="flat", padx=12, pady=4, cursor="hand2", command=self.on_delete_column
        )
        btn_del.pack(side="left", padx=10, pady=8)

        btn_close = tk.Button(
            btn_bar, text="Done", font=("Segoe UI", 9, "bold"), fg=BG_MAIN, bg=ACCENT_CYAN,
            activebackground="#79c0ff", relief="flat", padx=16, pady=4, cursor="hand2", command=self.destroy
        )
        btn_close.pack(side="right", padx=10, pady=8)

    def refresh_list(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for col in self.db.custom_columns:
            self.tree.insert("", "end", iid=col["id"], values=(col["name"], col["id"], col.get("default_val", "")))

    def on_add_column(self):
        name = self.entry_new_col.get().strip()
        if not name:
            messagebox.showwarning("Required", "Please enter a column name.", parent=self)
            self.entry_new_col.focus_set()
            return
        def_val = self.entry_def_val.get().strip()
        try:
            self.db.add_custom_column(name, default_val=def_val)
            self.entry_new_col.delete(0, "end")
            self.entry_def_val.delete(0, "end")
            self.refresh_list()
            self.result = "COLUMNS_CHANGED"
        except ValueError as e:
            messagebox.showerror("Error", str(e), parent=self)

    def on_delete_column(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Selection Required", "Select a column from the list to remove.", parent=self)
            return
        col_id = sel[0]
        # Find column name
        col_name = col_id
        for c in self.db.custom_columns:
            if c["id"] == col_id:
                col_name = c["name"]
                break

        conf = messagebox.askyesno(
            "Confirm Column Removal",
            f"Are you sure you want to delete the custom column '{col_name}'?\nThis will remove its data from all items.",
            parent=self
        )
        if conf:
            self.db.remove_custom_column(col_id)
            self.refresh_list()
            self.result = "COLUMNS_CHANGED"


class DatabaseInitDialog(BaseDialog):
    """Modal dialog asking whether to create an empty database or load demo data."""
    def __init__(self, parent, db_path="orbit_database.json"):
        super().__init__(parent, title="OrbitTracker — Database Setup")
        self.db_path = db_path
        self.result = "empty"
        center_window_on_parent(self, parent, width=540, height=370)
        self.build_ui()
        self.grab_set()

    def build_ui(self):
        # Header banner
        header = tk.Frame(self, bg=BG_PANEL, height=52, highlightthickness=1, highlightbackground=BORDER_COLOR)
        header.pack(fill="x", padx=12, pady=(12, 8))
        header.pack_propagate(False)

        lbl_title = tk.Label(header, text="🪐 DATABASE INITIALIZATION", font=FONT_TITLE, fg=ACCENT_CYAN, bg=BG_PANEL)
        lbl_title.pack(side="left", padx=14, pady=10)

        lbl_badge = tk.Label(header, text="NEW SETUP", font=FONT_CODE, fg=ACCENT_GOLD, bg=BG_SURFACE, padx=8, pady=3)
        lbl_badge.pack(side="right", padx=14, pady=10)

        # Message container
        msg_frame = tk.Frame(self, bg=BG_MAIN)
        msg_frame.pack(fill="x", padx=16, pady=(6, 12))

        lbl_prompt = tk.Label(
            msg_frame,
            text="Default database was not found at:",
            font=FONT_LABEL,
            fg=TEXT_PRIMARY,
            bg=BG_MAIN
        )
        lbl_prompt.pack(anchor="w")

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
            text="Would you like to populate sample data to explore OrbitTracker, or start with a fresh empty database?",
            font=FONT_UI,
            fg=TEXT_MUTED,
            bg=BG_MAIN,
            wraplength=500,
            justify="left"
        )
        lbl_question.pack(anchor="w", pady=(0, 4))

        # Choices container
        choices_frame = tk.Frame(self, bg=BG_MAIN)
        choices_frame.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        # Option 1: Load Demo
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
            text="Loads 3 sample equipment records, service logs, and custom columns.",
            font=FONT_UI,
            fg=TEXT_MUTED,
            bg=BG_PANEL,
            wraplength=300,
            justify="left"
        )
        lbl_demo_desc.pack(side="left", padx=(0, 10), pady=10)

        # Option 2: Create Empty Database
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
            text="Creates a clean, blank database ready for your own work orders.",
            font=FONT_UI,
            fg=TEXT_MUTED,
            bg=BG_PANEL,
            wraplength=300,
            justify="left"
        )
        lbl_empty_desc.pack(side="left", padx=(0, 10), pady=10)

        # Default keyboard shortcuts
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
        # Header banner
        header = tk.Frame(self, bg=BG_PANEL, height=52, highlightthickness=1, highlightbackground=BORDER_COLOR)
        header.pack(fill="x", padx=12, pady=(12, 8))
        header.pack_propagate(False)

        lbl_title = tk.Label(header, text="⚠️ DELETE DATABASE", font=FONT_TITLE, fg=ACCENT_CORAL, bg=BG_PANEL)
        lbl_title.pack(side="left", padx=14, pady=10)

        lbl_badge = tk.Label(header, text="DANGER", font=FONT_CODE, fg=BG_MAIN, bg=ACCENT_CORAL, padx=8, pady=3)
        lbl_badge.pack(side="right", padx=14, pady=10)

        # Warning container
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
            text="All work items, service logs, and custom columns in this file will be permanently erased. This action cannot be undone.\n\nTo confirm, type \"DELETE DATABASE\" below:",
            font=FONT_UI,
            fg=TEXT_MUTED,
            bg=BG_MAIN,
            wraplength=500,
            justify="left"
        )
        lbl_info.pack(anchor="w", pady=(0, 6))

        # Entry box
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

        # Listen for keystrokes to dynamically enable/disable the button
        self.entry_confirm.bind("<KeyRelease>", self.check_input)

        # Button Bar
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
            self.btn_delete.configure(
                state="normal",
                fg=BG_MAIN,
                bg=ACCENT_CORAL,
                cursor="hand2"
            )
            if event and event.keysym in ("Return", "KP_Enter"):
                self.on_confirm_delete()
        else:
            self.btn_delete.configure(
                state="disabled",
                fg=TEXT_DIM,
                bg=BG_SURFACE,
                cursor="arrow"
            )

    def on_confirm_delete(self):
        if self.entry_confirm.get().strip() == "DELETE DATABASE":
            self.result = True
            self.destroy()


class WorkAnalyticsDialog(BaseDialog):
    """Interactive visual analytics dashboard and graphing engine for work performed on work items."""
    def __init__(self, parent, db):
        super().__init__(parent, title="OrbitTracker — Work Performance & Analytics")
        self.db = db
        self.current_tab = "activity"  # "activity", "department", "intensity", "root_causes", "parts"
        self.chart_items = []          # Store bar bounding boxes for interactive hover: (x1, y1, x2, y2, tooltip_text)

        center_window_on_parent(self, parent, width=880, height=700)
        self.build_ui()
        self.grab_set()

    def build_ui(self):
        # 1. Header banner
        header = tk.Frame(self, bg=BG_PANEL, height=54, highlightthickness=1, highlightbackground=BORDER_COLOR)
        header.pack(fill="x", padx=12, pady=(12, 6))
        header.pack_propagate(False)

        lbl_title = tk.Label(header, text="📊 WORK PERFORMANCE & MAINTENANCE ANALYTICS", font=FONT_TITLE, fg=ACCENT_CYAN, bg=BG_PANEL)
        lbl_title.pack(side="left", padx=14, pady=10)

        lbl_badge = tk.Label(header, text="ANALYTICS ENGINE", font=FONT_CODE, fg=ACCENT_GOLD, bg=BG_SURFACE, padx=8, pady=3)
        lbl_badge.pack(side="right", padx=14, pady=10)

        # 2. KPI Summary Banner
        self.kpi_frame = tk.Frame(self, bg=BG_MAIN)
        self.kpi_frame.pack(fill="x", padx=12, pady=(0, 6))
        self.build_kpi_cards()

        # 3. Tab Selector Buttons
        tab_bar = tk.Frame(self, bg=BG_PANEL, height=40, highlightthickness=1, highlightbackground=BORDER_COLOR)
        tab_bar.pack(fill="x", padx=12, pady=(0, 6))
        tab_bar.pack_propagate(False)

        self.tab_buttons = {}
        tabs = [
            ("activity", "📈 Activity Over Time"),
            ("department", "🏢 Work by Department"),
            ("intensity", "🛠️ Equipment Intensity"),
            ("root_causes", "🔍 Root Cause Breakdown"),
            ("parts", "📦 Parts Consumed Log")
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
                padx=12,
                pady=6,
                cursor="hand2",
                command=lambda tid=tab_id: self.switch_tab(tid)
            )
            btn.pack(side="left", padx=2, pady=2)
            self.tab_buttons[tab_id] = btn

        # 4. Main Chart Canvas Area
        canvas_container = tk.Frame(self, bg=BG_PANEL, highlightthickness=1, highlightbackground=BORDER_COLOR)
        canvas_container.pack(fill="both", expand=True, padx=12, pady=(0, 6))

        self.canvas = tk.Canvas(canvas_container, bg=BG_PANEL, highlightthickness=0, height=310)
        self.canvas.pack(fill="both", expand=True, padx=8, pady=8)
        self.canvas.bind("<Configure>", lambda e: self.draw_chart())
        self.canvas.bind("<Motion>", self.on_canvas_motion)
        self.canvas.bind("<Leave>", self.on_canvas_leave)

        # 5. Lower Data Table / Legend Section
        self.table_frame = tk.Frame(self, bg=BG_PANEL, height=130, highlightthickness=1, highlightbackground=BORDER_COLOR)
        self.table_frame.pack(fill="x", padx=12, pady=(0, 6))
        self.table_frame.pack_propagate(False)

        self.build_table_view()

        # 6. Bottom Action Bar
        btn_bar = tk.Frame(self, bg=BG_PANEL, height=44, highlightthickness=1, highlightbackground=BORDER_COLOR)
        btn_bar.pack(side="bottom", fill="x", padx=12, pady=(0, 10))
        btn_bar.pack_propagate(False)

        self.lbl_status = tk.Label(btn_bar, text="", font=FONT_UI, fg=TEXT_MUTED, bg=BG_PANEL)
        self.lbl_status.pack(side="left", padx=12, pady=8)

        btn_close = tk.Button(
            btn_bar, text="Close", font=FONT_UI, fg=TEXT_PRIMARY, bg=BG_SURFACE,
            activebackground=BG_ACTIVE, relief="flat", padx=16, pady=4, cursor="hand2", command=self.destroy
        )
        btn_close.pack(side="right", padx=10, pady=6)

        btn_refresh = tk.Button(
            btn_bar, text="🔄 Refresh Analytics", font=FONT_UI, fg=BG_MAIN, bg=ACCENT_CYAN,
            activebackground="#79c0ff", relief="flat", padx=14, pady=4, cursor="hand2", command=self.refresh_all
        )
        btn_refresh.pack(side="right", padx=4, pady=6)

        self.switch_tab("activity")

    def build_kpi_cards(self):
        for w in self.kpi_frame.winfo_children():
            w.destroy()

        analytics = self.db.get_work_analytics()

        kpis = [
            ("TOTAL WORK ITEMS", str(analytics["total_items"]), ACCENT_CYAN),
            ("MAINTENANCE LOGS", str(analytics["maintenance_notes_count"]), ACCENT_MINT),
            ("QUICK NOTES", str(analytics["quick_notes_count"]), "#bc8cff"),
            ("PARTS CONSUMED", str(analytics["parts_consumed_count"]), ACCENT_GOLD),
            ("TOTAL WORK EVENTS", str(analytics["total_notes"]), TEXT_PRIMARY)
        ]

        self.kpi_frame.columnconfigure(0, weight=1)
        self.kpi_frame.columnconfigure(1, weight=1)
        self.kpi_frame.columnconfigure(2, weight=1)
        self.kpi_frame.columnconfigure(3, weight=1)
        self.kpi_frame.columnconfigure(4, weight=1)

        for col_idx, (title, val, color) in enumerate(kpis):
            card = tk.Frame(self.kpi_frame, bg=BG_SURFACE, highlightthickness=1, highlightbackground=BORDER_COLOR, padx=10, pady=6)
            card.grid(row=0, column=col_idx, sticky="nsew", padx=2, pady=2)

            tk.Label(card, text=title, font=("Segoe UI", 7, "bold"), fg=TEXT_MUTED, bg=BG_SURFACE).pack(anchor="w")
            tk.Label(card, text=val, font=("Segoe UI", 14, "bold"), fg=color, bg=BG_SURFACE).pack(anchor="w")

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

    def switch_tab(self, tab_id):
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
            w = max(self.canvas.winfo_reqwidth(), 800)
        if h < 50:
            h = max(self.canvas.winfo_reqheight(), 300)

        analytics = self.db.get_work_analytics()

        if self.current_tab == "activity":
            self.render_activity_chart(analytics, w, h)
        elif self.current_tab == "department":
            self.render_department_chart(analytics, w, h)
        elif self.current_tab == "intensity":
            self.render_intensity_chart(analytics, w, h)
        elif self.current_tab == "root_causes":
            self.render_root_causes_chart(analytics, w, h)
        elif self.current_tab == "parts":
            self.render_parts_chart(analytics, w, h)

    def render_activity_chart(self, analytics, w, h):
        monthly = analytics["timeline_monthly"]
        if not monthly:
            self.draw_empty_state("No service activity recorded yet.")
            return

        self.lbl_status.config(text=f"Showing monthly service volume across {len(monthly)} month periods.")

        padding_left = 60
        padding_right = 30
        padding_top = 40
        padding_bottom = 50

        chart_w = w - padding_left - padding_right
        chart_h = h - padding_top - padding_bottom

        max_val = max(m[1]["total"] for m in monthly)
        if max_val == 0:
            max_val = 1
        # Round up ceiling
        ceiling = max_val + (1 if max_val < 5 else max_val // 4 + 1)

        # Draw Y-Axis Grid lines
        steps = 4
        for i in range(steps + 1):
            val = int(ceiling * (i / steps))
            y = padding_top + chart_h - (chart_h * (i / steps))
            self.canvas.create_line(padding_left, y, w - padding_right, y, fill="#21262d", dash=(2, 4))
            self.canvas.create_text(padding_left - 8, y, text=str(val), fill=TEXT_MUTED, font=("Segoe UI", 8), anchor="e")

        # X and Y main axes
        self.canvas.create_line(padding_left, padding_top, padding_left, h - padding_bottom, fill=BORDER_COLOR)
        self.canvas.create_line(padding_left, h - padding_bottom, w - padding_right, h - padding_bottom, fill=BORDER_COLOR)

        # Draw Bars
        slot_w = chart_w / len(monthly)
        bar_w = min(46, slot_w * 0.65)

        for idx, (month, counts) in enumerate(monthly):
            center_x = padding_left + slot_w * idx + slot_w / 2
            x1 = center_x - bar_w / 2
            x2 = center_x + bar_w / 2

            m_cnt = counts["maintenance"]
            q_cnt = counts["quick"]
            tot = counts["total"]

            # Stacked bars: Maintenance on bottom, Quick notes on top
            m_h = (chart_h * (m_cnt / ceiling)) if ceiling else 0
            q_h = (chart_h * (q_cnt / ceiling)) if ceiling else 0

            y_base = h - padding_bottom
            y_m = y_base - m_h
            y_top = y_m - q_h

            if m_cnt > 0:
                rect_m = self.canvas.create_rectangle(x1, y_m, x2, y_base, fill=ACCENT_MINT, outline="#a6f3b0", width=1)
                self.chart_items.append((x1, y_m, x2, y_base, f"📅 {month}\n🛠️ Maintenance: {m_cnt} logs"))

            if q_cnt > 0:
                rect_q = self.canvas.create_rectangle(x1, y_top, x2, y_m, fill="#bc8cff", outline="#d2a8ff", width=1)
                self.chart_items.append((x1, y_top, x2, y_m, f"📅 {month}\n⚡ Quick Notes: {q_cnt} notes"))

            # Total label on top of bar
            if tot > 0:
                self.canvas.create_text(center_x, y_top - 8, text=str(tot), fill=TEXT_PRIMARY, font=("Segoe UI", 8, "bold"))

            # X-axis label
            self.canvas.create_text(center_x, h - padding_bottom + 14, text=month, fill=TEXT_MUTED, font=("Segoe UI", 8))

        # Legend
        self.draw_legend([
            ("🛠️ Maintenance Logs", ACCENT_MINT),
            ("⚡ Quick Notes", "#bc8cff")
        ], w - 220, 16)

    def render_department_chart(self, analytics, w, h):
        dept_data = analytics["dept_work"]
        if not dept_data:
            self.draw_empty_state("No department work logged yet.")
            return

        self.lbl_status.config(text=f"Showing work actions performed across {len(dept_data)} departments.")

        padding_left = 170
        padding_right = 60
        padding_top = 36
        padding_bottom = 30

        chart_w = w - padding_left - padding_right
        chart_h = h - padding_top - padding_bottom

        max_val = max(d[1]["maintenance"] + d[1]["quick"] for d in dept_data)
        if max_val == 0:
            max_val = 1
        ceiling = max_val + 1

        slot_h = min(45, chart_h / len(dept_data))
        bar_h = slot_h * 0.6

        for idx, (dept_name, counts) in enumerate(dept_data[:8]):
            y_center = padding_top + slot_h * idx + slot_h / 2
            y1 = y_center - bar_h / 2
            y2 = y_center + bar_h / 2

            m_cnt = counts["maintenance"]
            q_cnt = counts["quick"]
            tot = m_cnt + q_cnt

            w_m = (chart_w * (m_cnt / ceiling)) if ceiling else 0
            w_q = (chart_w * (q_cnt / ceiling)) if ceiling else 0

            # Y-axis label
            disp_name = (dept_name[:20] + "...") if len(dept_name) > 22 else dept_name
            self.canvas.create_text(padding_left - 10, y_center, text=disp_name, fill=TEXT_PRIMARY, font=("Segoe UI", 8, "bold"), anchor="e")

            # Horizontal Stacked Bars
            x_start = padding_left
            x_m = x_start + w_m
            x_end = x_m + w_q

            if m_cnt > 0:
                self.canvas.create_rectangle(x_start, y1, x_m, y2, fill=ACCENT_CYAN, outline="#79c0ff")
                self.chart_items.append((x_start, y1, x_m, y2, f"🏢 {dept_name}\n🛠️ Maintenance: {m_cnt}"))

            if q_cnt > 0:
                self.canvas.create_rectangle(x_m, y1, x_end, y2, fill="#bc8cff", outline="#d2a8ff")
                self.chart_items.append((x_m, y1, x_end, y2, f"🏢 {dept_name}\n⚡ Quick Notes: {q_cnt}"))

            # Value label at end
            self.canvas.create_text(x_end + 8, y_center, text=f"{tot} logs ({counts['items']} units)", fill=ACCENT_GOLD, font=("Segoe UI", 8), anchor="w")

        # Vertical axis line
        self.canvas.create_line(padding_left, padding_top - 10, padding_left, padding_top + slot_h * min(8, len(dept_data)), fill=BORDER_COLOR)

        # Legend
        self.draw_legend([
            ("🛠️ Maintenance", ACCENT_CYAN),
            ("⚡ Quick Notes", "#bc8cff")
        ], w - 210, 14)

    def render_intensity_chart(self, analytics, w, h):
        items = analytics["item_intensity"]
        top_items = [it for it in items if it["total_notes"] > 0][:8]
        if not top_items:
            self.draw_empty_state("No maintenance logs recorded for equipment yet.")
            return

        self.lbl_status.config(text=f"Showing top {len(top_items)} equipment units by maintenance frequency.")

        padding_left = 180
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

            tag = f"[{it['queue_number']}] {it['item_name'][:18]}"
            self.canvas.create_text(padding_left - 10, y_center, text=tag, fill=TEXT_PRIMARY, font=("Segoe UI", 8, "bold"), anchor="e")

            bw = chart_w * (it["total_notes"] / ceiling)
            x_end = padding_left + bw

            # Color bar: Gold if parts replaced, Cyan otherwise
            fill_c = ACCENT_GOLD if it["parts_actions"] > 0 else ACCENT_CYAN
            self.canvas.create_rectangle(padding_left, y1, x_end, y2, fill=fill_c, outline="#79c0ff" if fill_c == ACCENT_CYAN else "#ffe58f")

            tip = f"🪐 {it['queue_number']} — {it['item_name']}\n🛠️ Maint: {it['maintenance_notes']} | ⚡ Quick: {it['quick_notes']}\n📦 Parts Consumed: {it['parts_actions']} jobs"
            self.chart_items.append((padding_left, y1, x_end, y2, tip))

            txt = f"{it['total_notes']} events" + (f" ({it['parts_actions']} parts)" if it["parts_actions"] else "")
            self.canvas.create_text(x_end + 8, y_center, text=txt, fill=TEXT_MUTED, font=("Segoe UI", 8), anchor="w")

        self.canvas.create_line(padding_left, padding_top - 10, padding_left, padding_top + slot_h * len(top_items), fill=BORDER_COLOR)

        self.draw_legend([
            ("Parts Consumed", ACCENT_GOLD),
            ("Standard Service", ACCENT_CYAN)
        ], w - 220, 14)

    def render_root_causes_chart(self, analytics, w, h):
        rc_data = analytics["root_causes"]
        if not rc_data:
            self.draw_empty_state("No root cause analyses recorded yet.\nFill out 'Root Cause' when logging maintenance.")
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
            self.chart_items.append((padding_left, y1, x_end, y2, f"🔍 Root Cause:\n{rc_name}\nOccurrences: {count}"))

            self.canvas.create_text(x_end + 8, y_center, text=f"{count} case{'s' if count != 1 else ''}", fill=ACCENT_CORAL, font=("Segoe UI", 8), anchor="w")

        self.canvas.create_line(padding_left, padding_top - 10, padding_left, padding_top + slot_h * len(top_rc), fill=BORDER_COLOR)

    def render_parts_chart(self, analytics, w, h):
        parts_list = analytics["parts_list"]
        if not parts_list:
            self.draw_empty_state("No parts or materials consumed logged yet.\nRecord parts when logging maintenance notes.")
            return

        self.lbl_status.config(text=f"Showing {len(parts_list)} recorded parts and materials replacement jobs.")

        padding_left = 60
        padding_right = 40
        padding_top = 40
        padding_bottom = 40

        chart_w = w - padding_left - padding_right
        chart_h = h - padding_top - padding_bottom

        # Doughnut / summary distribution
        tot_notes = analytics["total_notes"]
        parts_cnt = analytics["parts_consumed_count"]
        no_parts_cnt = tot_notes - parts_cnt

        center_x = padding_left + 140
        center_y = padding_top + chart_h / 2
        radius = min(90, chart_h / 2 - 10)

        p_angle = (parts_cnt / tot_notes * 360) if tot_notes else 0
        np_angle = 360 - p_angle

        # Draw Pie slices
        self.canvas.create_arc(
            center_x - radius, center_y - radius, center_x + radius, center_y + radius,
            start=0, extent=p_angle, fill=ACCENT_GOLD, outline="#ffe58f"
        )
        self.canvas.create_arc(
            center_x - radius, center_y - radius, center_x + radius, center_y + radius,
            start=p_angle, extent=np_angle, fill=BG_SURFACE, outline=BORDER_COLOR
        )

        # Center hole (doughnut effect)
        hole_r = radius * 0.55
        self.canvas.create_oval(
            center_x - hole_r, center_y - hole_r, center_x + hole_r, center_y + hole_r,
            fill=BG_PANEL, outline=BORDER_COLOR
        )
        pct = (parts_cnt / tot_notes * 100) if tot_notes else 0
        self.canvas.create_text(center_x, center_y - 6, text=f"{pct:.0f}%", fill=ACCENT_GOLD, font=("Segoe UI", 12, "bold"))
        self.canvas.create_text(center_x, center_y + 10, text="PARTS RATIO", fill=TEXT_MUTED, font=("Segoe UI", 6, "bold"))

        # Right Summary Info
        info_x = center_x + radius + 40
        self.canvas.create_text(info_x, center_y - 45, text="PARTS CONSUMPTION METRICS", font=("Segoe UI", 10, "bold"), fill=ACCENT_CYAN, anchor="w")
        self.canvas.create_text(info_x, center_y - 20, text=f"• Maintenance Events with Parts: {parts_cnt}", font=FONT_UI, fill=TEXT_PRIMARY, anchor="w")
        self.canvas.create_text(info_x, center_y + 2, text=f"• Routine Service / Inspections: {no_parts_cnt}", font=FONT_UI, fill=TEXT_MUTED, anchor="w")
        self.canvas.create_text(info_x, center_y + 24, text=f"• Total Service Events: {tot_notes}", font=FONT_UI, fill=TEXT_PRIMARY, anchor="w")
        self.canvas.create_text(info_x, center_y + 46, text=f"• Detailed parts log listed in the table below.", font=("Segoe UI", 8, "italic"), fill=ACCENT_GOLD, anchor="w")

    def draw_empty_state(self, message):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        self.canvas.create_text(w / 2, h / 2 - 10, text="🪐 NO DATA AVAILABLE", font=("Segoe UI", 11, "bold"), fill=TEXT_MUTED)
        self.canvas.create_text(w / 2, h / 2 + 14, text=message, font=FONT_UI, fill=TEXT_DIM, justify="center")

    def draw_legend(self, items, x, y):
        curr_x = x
        for label, color in items:
            self.canvas.create_rectangle(curr_x, y, curr_x + 12, y + 12, fill=color, outline="")
            self.canvas.create_text(curr_x + 18, y + 6, text=label, fill=TEXT_MUTED, font=("Segoe UI", 8), anchor="w")
            curr_x += 105

    # ==========================================================================
    # INTERACTIVE HOVER TOOLTIPS
    # ==========================================================================
    def on_canvas_motion(self, event):
        self.canvas.delete("tooltip")
        mx, my = event.x, event.y

        for x1, y1, x2, y2, text in self.chart_items:
            if x1 <= mx <= x2 and y1 <= my <= y2:
                # Draw tooltip box
                tt_x = min(mx + 12, self.canvas.winfo_width() - 170)
                tt_y = max(my - 45, 10)

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

        analytics = self.db.get_work_analytics()

        if self.current_tab == "activity":
            self.tree["columns"] = ("month", "total", "maintenance", "quick", "ratio")
            self.tree.heading("month", text="Month")
            self.tree.heading("total", text="Total Events")
            self.tree.heading("maintenance", text="Maintenance Records")
            self.tree.heading("quick", text="Quick Notes")
            self.tree.heading("ratio", text="Maint %")
            self.tree.column("month", width=120)
            self.tree.column("total", width=110)
            self.tree.column("maintenance", width=160)
            self.tree.column("quick", width=130)
            self.tree.column("ratio", width=100)

            for month, counts in reversed(analytics["timeline_monthly"]):
                tot = counts["total"]
                m = counts["maintenance"]
                q = counts["quick"]
                pct = f"{(m / tot * 100):.0f}%" if tot else "0%"
                self.tree.insert("", "end", values=(month, tot, m, q, pct))

        elif self.current_tab == "department":
            self.tree["columns"] = ("dept", "items", "total_logs", "maint_logs", "quick_notes")
            self.tree.heading("dept", text="Department")
            self.tree.heading("items", text="Units Tracked")
            self.tree.heading("total_logs", text="Total Work Events")
            self.tree.heading("maint_logs", text="Maintenance Logs")
            self.tree.heading("quick_notes", text="Quick Notes")
            self.tree.column("dept", width=220)
            self.tree.column("items", width=110)
            self.tree.column("total_logs", width=130)
            self.tree.column("maint_logs", width=140)
            self.tree.column("quick_notes", width=120)

            for dept_name, counts in analytics["dept_work"]:
                tot = counts["maintenance"] + counts["quick"]
                self.tree.insert("", "end", values=(dept_name, counts["items"], tot, counts["maintenance"], counts["quick"]))

        elif self.current_tab == "intensity":
            self.tree["columns"] = ("queue", "name", "dept", "status", "notes", "maint", "parts")
            self.tree.heading("queue", text="Queue #")
            self.tree.heading("name", text="Item Name")
            self.tree.heading("dept", text="Department")
            self.tree.heading("status", text="Status")
            self.tree.heading("notes", text="Total Events")
            self.tree.heading("maint", text="Maintenance")
            self.tree.heading("parts", text="Parts Jobs")
            self.tree.column("queue", width=85)
            self.tree.column("name", width=200)
            self.tree.column("dept", width=160)
            self.tree.column("status", width=80)
            self.tree.column("notes", width=95)
            self.tree.column("maint", width=95)
            self.tree.column("parts", width=95)

            for it in analytics["item_intensity"]:
                self.tree.insert("", "end", values=(
                    it["queue_number"], it["item_name"], it["department"], it["status"],
                    it["total_notes"], it["maintenance_notes"], it["parts_actions"]
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

        elif self.current_tab == "parts":
            self.tree["columns"] = ("timestamp", "queue", "item", "parts")
            self.tree.heading("timestamp", text="Date & Time")
            self.tree.heading("queue", text="Queue #")
            self.tree.heading("item", text="Equipment")
            self.tree.heading("parts", text="Parts & Materials Consumed")
            self.tree.column("timestamp", width=140)
            self.tree.column("queue", width=90)
            self.tree.column("item", width=200)
            self.tree.column("parts", width=340)

            for p in reversed(analytics["parts_list"]):
                self.tree.insert("", "end", values=(p["timestamp"], p["queue_number"], p["item_name"], p["parts"]))


