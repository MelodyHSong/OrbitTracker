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
        base_h = 600 if item else 660
        target_h = min(780, base_h + custom_count * 38)
        center_window_on_parent(self, parent, width=560, height=target_h)

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

        # Scrollable form container for small displays / many custom columns
        canvas = tk.Canvas(self, bg=BG_MAIN, highlightthickness=0)
        v_scroll = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        form_frame = tk.Frame(canvas, bg=BG_MAIN)

        form_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=form_frame, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width))

        canvas.configure(yscrollcommand=v_scroll.set)
        canvas.pack(side="top", fill="both", expand=True, padx=14, pady=4)
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
            r_note = tk.Frame(form_frame, bg=BG_MAIN)
            r_note.pack(fill="x", pady=(8, 4))
            tk.Label(r_note, text="Initial Service / Maintenance Note (Optional)", font=FONT_LABEL, fg=ACCENT_CYAN, bg=BG_MAIN).pack(anchor="w")
            self.txt_initial_note = tk.Text(r_note, font=FONT_UI, bg=BG_SURFACE, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                                            height=3, relief="flat", highlightthickness=1, highlightbackground=BORDER_COLOR, wrap="word")
            self.txt_initial_note.pack(fill="x", pady=2)

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

        initial_note = ""
        if hasattr(self, "txt_initial_note"):
            initial_note = self.txt_initial_note.get("1.0", "end-1c").strip()

        self.result = {
            "queue_number": queue_num,
            "moc_number": moc_num,
            "st_number": st_num,
            "item_name": item_name,
            "make_and_model": make_model,
            "status": status,
            "department": dept,
            "custom_fields": custom_vals,
            "initial_note": initial_note
        }
        self.destroy()


class ServiceNoteDialog(BaseDialog):
    """Modal dialog for adding a new maintenance/service note to an item."""
    def __init__(self, parent, item, note=None):
        super().__init__(parent, title="Edit Service Note" if note else "Add Service / Maintenance Note")
        self.item = item
        self.note = note
        center_window_on_parent(self, parent, width=500, height=360)
        self.build_ui()
        self.grab_set()

    def build_ui(self):
        # Header banner
        header = tk.Frame(self, bg=BG_PANEL, height=50, highlightthickness=1, highlightbackground=BORDER_COLOR)
        header.pack(fill="x", padx=12, pady=(12, 8))
        header.pack_propagate(False)

        title = "✏️ EDIT SERVICE NOTE" if self.note else "📝 ADD SERVICE NOTE"
        lbl_title = tk.Label(header, text=title, font=FONT_TITLE, fg=ACCENT_GOLD, bg=BG_PANEL)
        lbl_title.pack(side="left", padx=14, pady=10)

        item_tag = f"[{self.item.queue_number}] {self.item.item_name[:22]}"
        lbl_badge = tk.Label(header, text=item_tag, font=FONT_CODE, fg=TEXT_MUTED, bg=BG_SURFACE, padx=8, pady=3)
        lbl_badge.pack(side="right", padx=14, pady=10)

        # Form
        form = tk.Frame(self, bg=BG_MAIN)
        form.pack(fill="both", expand=True, padx=14, pady=4)

        # Timestamp row
        ts_frame = tk.Frame(form, bg=BG_MAIN)
        ts_frame.pack(fill="x", pady=(0, 6))
        tk.Label(ts_frame, text="Timestamp", font=FONT_LABEL, fg=TEXT_MUTED, bg=BG_MAIN).pack(side="left")

        now_str = self.note.timestamp if self.note else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.entry_ts = tk.Entry(ts_frame, font=FONT_CODE, bg=BG_SURFACE, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                                 width=22, relief="flat", highlightthickness=1, highlightbackground=BORDER_COLOR)
        self.entry_ts.pack(side="right", ipady=3)
        self.entry_ts.insert(0, now_str)

        # Note Text
        tk.Label(form, text="Maintenance Performed / Notes *", font=FONT_LABEL, fg=TEXT_MUTED, bg=BG_MAIN).pack(anchor="w")
        self.txt_note = tk.Text(form, font=FONT_UI, bg=BG_SURFACE, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                                relief="flat", highlightthickness=1, highlightbackground=BORDER_COLOR, wrap="word")
        self.txt_note.pack(fill="both", expand=True, pady=4)
        if self.note:
            self.txt_note.insert("1.0", self.note.note)
        self.txt_note.focus_set()

        # Button Bar
        btn_bar = tk.Frame(self, bg=BG_PANEL, height=50, highlightthickness=1, highlightbackground=BORDER_COLOR)
        btn_bar.pack(side="bottom", fill="x", padx=12, pady=(4, 12))
        btn_bar.pack_propagate(False)

        btn_cancel = tk.Button(
            btn_bar, text="Cancel", font=FONT_UI, fg=TEXT_PRIMARY, bg=BG_SURFACE,
            activebackground=BG_ACTIVE, relief="flat", padx=12, pady=4, cursor="hand2", command=self.destroy
        )
        btn_cancel.pack(side="right", padx=10, pady=8)

        btn_save = tk.Button(
            btn_bar, text="Save Note", font=("Segoe UI", 9, "bold"), fg=BG_MAIN, bg=ACCENT_GOLD,
            activebackground="#ffe58f", relief="flat", padx=14, pady=4, cursor="hand2", command=self.on_save
        )
        btn_save.pack(side="right", padx=4, pady=8)

    def on_save(self):
        text = self.txt_note.get("1.0", "end-1c").strip()
        if not text:
            messagebox.showwarning("Empty Note", "Please enter maintenance notes.", parent=self)
            self.txt_note.focus_set()
            return
        ts = self.entry_ts.get().strip() or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.result = {"note": text, "timestamp": ts}
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


