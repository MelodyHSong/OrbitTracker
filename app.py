# 🪐 OrbitTracker — Work Activity & Maintenance Tracking Workstation
# Author: MelodyHSong
# Language: Python
# File Name: app.py
# Description: Desktop Workstation with JSON database, auto-generated Queue Numbers,
#              pre-defined and dynamic custom columns, and service maintenance logs.

import sys
import os
import json
import time
import queue
import threading
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Enable Windows High-DPI Awareness for crisp rendering
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

# Import OrbitTracker Model & Dialogs
from database import DatabaseManager, WorkItem, ServiceNote
from dialogs import ItemDialog, ServiceNoteDialog, ColumnManagerDialog

# ==============================================================================
# 🪐 COSMIC COLOR PALETTE & THEME CONSTANTS
# ==============================================================================
BG_MAIN = "#0d1117"          # Deep space obsidian
BG_PANEL = "#161b22"         # Surface / card background
BG_SURFACE = "#21262d"       # Elevated widget background
BG_ACTIVE = "#30363d"        # Hover / selected item
BORDER_COLOR = "#30363d"     # Panel rim border
BORDER_ACTIVE = "#58a6ff"    # Focused active border

TEXT_PRIMARY = "#e2e8f0"     # Starlight white
TEXT_MUTED = "#8b949e"       # Dust gray
TEXT_DIM = "#586069"         # Nebula shadow

ACCENT_CYAN = "#58a6ff"      # Starlight cyan
ACCENT_GOLD = "#f2cc60"      # Celestial star gold
ACCENT_MINT = "#7ee787"      # Status ok / active green
ACCENT_CORAL = "#f85149"     # Alert / inactive red

FONT_HEADER = ("Segoe UI", 13, "bold")
FONT_SUBHEADER = ("Segoe UI", 9)
FONT_UI = ("Segoe UI", 9)
FONT_UI_BOLD = ("Segoe UI", 9, "bold")
FONT_CODE = ("Consolas", 9)
FONT_CODE_BOLD = ("Consolas", 9, "bold")
FONT_METRIC = ("Segoe UI", 18, "bold")
FONT_METRIC_LBL = ("Segoe UI", 8, "bold")


class OrbitTrackerApp:
    def __init__(self, root, initial_file=None):
        self.root = root
        self.root.title("🪐 OrbitTracker — Work Activity & Maintenance Workstation")
        self.root.geometry("1240x760")
        self.root.minsize(960, 600)
        self.root.configure(bg=BG_MAIN)

        # Asset & Path Resolution
        self.app_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        self.base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

        # State Variables
        self.config_path = os.path.join(self.base_dir, "config.json")
        self.config = self.load_config()
        self.background_queue = queue.Queue()
        self.autosave_timer = None
        self.selected_item_id = None
        self.sort_column = "queue_number"
        self.sort_desc = False

        # Determine Database File Path
        db_path = initial_file or self.config.get("database_path") or os.path.join(self.base_dir, "orbit_database.json")
        self.db = DatabaseManager(db_path)

        # Populate sample items if brand new empty database
        if len(self.db.items) == 0:
            self.seed_starter_data()

        # Set Window Icon
        self.set_app_icon()

        # Build UI Components
        self.build_ui()

        # Keyboard Shortcut Bindings
        self.bind_shortcuts()

        # Window Close Protocol
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)

        # Background Queue Poller
        self.root.after(100, self.process_queue)

        # Initial Refresh
        self.refresh_table()
        self.update_metrics_cards()
        self.log_message(f"OrbitTracker initialized. Database loaded: {os.path.basename(self.db.db_path)} ({len(self.db.items)} records)", level="SUCCESS")

    # ==========================================================================
    # CONFIGURATION & ASSETS
    # ==========================================================================
    def load_config(self):
        default_config = {
            "app_name": "OrbitTracker",
            "version": "1.0.0",
            "database_path": "orbit_database.json",
            "preferences": {
                "autosave_enabled": True,
                "autosave_interval_ms": 3000,
                "confirm_exit_on_unsaved": True
            }
        }
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[!] Warning: Could not parse config.json: {e}")
        return default_config

    def save_config(self):
        try:
            self.config["database_path"] = os.path.relpath(self.db.db_path, self.base_dir)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.log_message(f"Error saving config.json: {e}", level="ERROR")

    def set_app_icon(self):
        icon_candidates = [
            os.path.join(self.app_dir, "assets", "app_icon.ico"),
            os.path.join(self.base_dir, "assets", "app_icon.ico"),
        ]
        for icon_path in icon_candidates:
            if os.path.exists(icon_path):
                try:
                    self.root.iconbitmap(icon_path)
                    break
                except Exception:
                    pass

    def seed_starter_data(self):
        """Creates sample items when initializing OrbitTracker for the first time."""
        item1 = self.db.add_item(
            moc_number="MOC-3041",
            st_number="ST-94812",
            item_name="Centrifugal Booster Pump",
            make_and_model="Flowserve HPX-600",
            status="Active",
            department="Cryogenics & Propulsion",
            initial_note="Replaced high-pressure mechanical seal and verified casing alignment."
        )
        self.db.add_service_note(item1.id, "Lubricated bearings with synthetic Krytox grease; vibrations nominal.")

        item2 = self.db.add_item(
            moc_number="MOC-3048",
            st_number="ST-88104",
            item_name="Telemetry Transceiver Unit",
            make_and_model="L3Harris SpaceLink-9",
            status="Active",
            department="Avionics & Communications",
            initial_note="Bench-tested Ku-band frequency synthesizer; power output 42 dBm."
        )

        item3 = self.db.add_item(
            moc_number="MOC-2980",
            st_number="ST-77319",
            item_name="Hydraulic Actuator Solenoid",
            make_and_model="Parker Hannifin E-Series",
            status="Inactive",
            department="Hydraulics & Actuation",
            initial_note="Awaiting replacement spool assembly from vendor."
        )

        # Add a starter custom column
        self.db.add_custom_column("Facility Bay", default_val="Main Hangar")
        self.db.update_item(item1.id, custom_fields={self.db.custom_columns[0]["id"]: "Bay 4 West"})
        self.db.update_item(item2.id, custom_fields={self.db.custom_columns[0]["id"]: "Avionics Cleanroom"})
        self.db.update_item(item3.id, custom_fields={self.db.custom_columns[0]["id"]: "Storage Depot B"})

        self.db.save()

    # ==========================================================================
    # GUI ARCHITECTURE
    # ==========================================================================
    def build_ui(self):
        self.setup_ttk_styles()

        # 1. Header Bar
        self.build_header()

        # 2. Main Workspace Layout: Left Sidebar + Central Workstation + Right Inspector
        main_container = tk.Frame(self.root, bg=BG_MAIN)
        main_container.pack(fill="both", expand=True, padx=12, pady=(0, 4))

        # Left Sidebar (Controls, Metrics & Filters)
        self.build_sidebar(main_container)

        # Central Paned Container (Grid + Details Inspector)
        self.build_center_workstation(main_container)

        # 3. Bottom Collapsible Console & Status Bar
        self.build_bottom_panel()

    def setup_ttk_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Scrollbars
        style.configure(
            "Vertical.TScrollbar",
            background=BG_PANEL,
            troughcolor=BG_MAIN,
            bordercolor=BORDER_COLOR,
            arrowcolor=TEXT_MUTED
        )
        style.map("Vertical.TScrollbar", background=[("active", ACCENT_CYAN)])

        # Treeview (Data Grid)
        style.configure(
            "Treeview",
            background=BG_PANEL,
            foreground=TEXT_PRIMARY,
            fieldbackground=BG_PANEL,
            rowheight=28,
            font=FONT_UI,
            borderwidth=0
        )
        style.configure(
            "Treeview.Heading",
            background=BG_SURFACE,
            foreground=ACCENT_CYAN,
            relief="flat",
            font=FONT_UI_BOLD,
            padding=[8, 6]
        )
        style.map(
            "Treeview.Heading",
            background=[("active", BG_ACTIVE)],
            foreground=[("active", TEXT_PRIMARY)]
        )
        style.map(
            "Treeview",
            background=[("selected", BG_ACTIVE)],
            foreground=[("selected", ACCENT_CYAN)]
        )

        # Combobox
        style.configure(
            "TCombobox",
            background=BG_SURFACE,
            foreground=TEXT_PRIMARY,
            fieldbackground=BG_SURFACE,
            arrowcolor=TEXT_MUTED,
            bordercolor=BORDER_COLOR,
            darkcolor=BG_SURFACE,
            lightcolor=BG_SURFACE
        )
        style.map("TCombobox", fieldbackground=[("readonly", BG_SURFACE)], foreground=[("readonly", TEXT_PRIMARY)])

    # --------------------------------------------------------------------------
    # HEADER BAR
    # --------------------------------------------------------------------------
    def build_header(self):
        header = tk.Frame(self.root, bg=BG_PANEL, height=60, highlightthickness=1, highlightbackground=BORDER_COLOR)
        header.pack(fill="x", padx=12, pady=(8, 8))
        header.pack_propagate(False)

        # Left Branding
        brand_frame = tk.Frame(header, bg=BG_PANEL)
        brand_frame.pack(side="left", padx=14, pady=6)

        title_lbl = tk.Label(
            brand_frame,
            text="🪐 ORBIT TRACKER",
            font=FONT_HEADER,
            fg=TEXT_PRIMARY,
            bg=BG_PANEL
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = tk.Label(
            brand_frame,
            text="Work Activity & Maintenance Workstation • JSON Persistence",
            font=FONT_SUBHEADER,
            fg=TEXT_MUTED,
            bg=BG_PANEL
        )
        subtitle_lbl.pack(anchor="w")

        # Right Actions & Status Pill
        actions_frame = tk.Frame(header, bg=BG_PANEL)
        actions_frame.pack(side="right", padx=14, pady=8)

        self.status_pill = tk.Label(
            actions_frame,
            text="● SYSTEM READY",
            font=FONT_UI_BOLD,
            fg=ACCENT_MINT,
            bg=BG_SURFACE,
            padx=10,
            pady=4,
            relief="flat"
        )
        self.status_pill.pack(side="right", padx=(10, 0))

        btn_save = tk.Button(
            actions_frame,
            text="💾 Save DB",
            font=FONT_UI_BOLD,
            fg=TEXT_PRIMARY,
            bg=BG_SURFACE,
            activebackground=BG_ACTIVE,
            activeforeground=TEXT_PRIMARY,
            relief="flat",
            padx=12,
            pady=4,
            cursor="hand2",
            command=self.on_save_db
        )
        btn_save.pack(side="right", padx=4)

        btn_add_col = tk.Button(
            actions_frame,
            text="⚙️ Columns",
            font=FONT_UI,
            fg=TEXT_PRIMARY,
            bg=BG_SURFACE,
            activebackground=BG_ACTIVE,
            activeforeground=TEXT_PRIMARY,
            relief="flat",
            padx=10,
            pady=4,
            cursor="hand2",
            command=self.on_manage_columns
        )
        btn_add_col.pack(side="right", padx=4)

        btn_new_item = tk.Button(
            actions_frame,
            text="+ Add Work Item",
            font=FONT_UI_BOLD,
            fg=BG_MAIN,
            bg=ACCENT_CYAN,
            activebackground="#79c0ff",
            activeforeground=BG_MAIN,
            relief="flat",
            padx=14,
            pady=4,
            cursor="hand2",
            command=self.on_add_item
        )
        btn_new_item.pack(side="right", padx=4)

    # --------------------------------------------------------------------------
    # SIDEBAR
    # --------------------------------------------------------------------------
    def build_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg=BG_PANEL, width=250, highlightthickness=1, highlightbackground=BORDER_COLOR)
        sidebar.pack(side="left", fill="y", padx=(0, 8))
        sidebar.pack_propagate(False)

        # Top KPI Metrics Cards
        lbl_kpi = tk.Label(sidebar, text="DATABASE METRICS", font=FONT_METRIC_LBL, fg=ACCENT_GOLD, bg=BG_PANEL)
        lbl_kpi.pack(anchor="w", padx=14, pady=(12, 6))

        metrics_grid = tk.Frame(sidebar, bg=BG_PANEL)
        metrics_grid.pack(fill="x", padx=12, pady=(0, 10))

        # Card 1: Total Items
        c1 = tk.Frame(metrics_grid, bg=BG_SURFACE, highlightthickness=1, highlightbackground=BORDER_COLOR, padx=8, pady=6)
        c1.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        tk.Label(c1, text="TOTAL", font=FONT_METRIC_LBL, fg=TEXT_MUTED, bg=BG_SURFACE).pack(anchor="w")
        self.lbl_metric_total = tk.Label(c1, text="0", font=FONT_METRIC, fg=ACCENT_CYAN, bg=BG_SURFACE)
        self.lbl_metric_total.pack(anchor="w")

        # Card 2: Active
        c2 = tk.Frame(metrics_grid, bg=BG_SURFACE, highlightthickness=1, highlightbackground=BORDER_COLOR, padx=8, pady=6)
        c2.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        tk.Label(c2, text="ACTIVE", font=FONT_METRIC_LBL, fg=TEXT_MUTED, bg=BG_SURFACE).pack(anchor="w")
        self.lbl_metric_active = tk.Label(c2, text="0", font=FONT_METRIC, fg=ACCENT_MINT, bg=BG_SURFACE)
        self.lbl_metric_active.pack(anchor="w")

        # Card 3: Inactive
        c3 = tk.Frame(metrics_grid, bg=BG_SURFACE, highlightthickness=1, highlightbackground=BORDER_COLOR, padx=8, pady=6)
        c3.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)
        tk.Label(c3, text="INACTIVE", font=FONT_METRIC_LBL, fg=TEXT_MUTED, bg=BG_SURFACE).pack(anchor="w")
        self.lbl_metric_inactive = tk.Label(c3, text="0", font=FONT_METRIC, fg=ACCENT_CORAL, bg=BG_SURFACE)
        self.lbl_metric_inactive.pack(anchor="w")

        # Card 4: Service Notes
        c4 = tk.Frame(metrics_grid, bg=BG_SURFACE, highlightthickness=1, highlightbackground=BORDER_COLOR, padx=8, pady=6)
        c4.grid(row=1, column=1, sticky="nsew", padx=2, pady=2)
        tk.Label(c4, text="NOTES", font=FONT_METRIC_LBL, fg=TEXT_MUTED, bg=BG_SURFACE).pack(anchor="w")
        self.lbl_metric_notes = tk.Label(c4, text="0", font=FONT_METRIC, fg=ACCENT_GOLD, bg=BG_SURFACE)
        self.lbl_metric_notes.pack(anchor="w")

        metrics_grid.columnconfigure(0, weight=1)
        metrics_grid.columnconfigure(1, weight=1)

        # Primary Action Buttons
        lbl_actions = tk.Label(sidebar, text="ACTIONS & DATABASE", font=FONT_METRIC_LBL, fg=ACCENT_GOLD, bg=BG_PANEL)
        lbl_actions.pack(anchor="w", padx=14, pady=(8, 4))

        self.create_sidebar_btn(sidebar, "➕ New Item (Ctrl+N)", self.on_add_item, accent=ACCENT_CYAN, is_bold=True)
        self.create_sidebar_btn(sidebar, "⚙️ Manage Columns", self.on_manage_columns)
        self.create_sidebar_btn(sidebar, "💾 Save Database (Ctrl+S)", self.on_save_db)
        self.create_sidebar_btn(sidebar, "📂 Open Database... (Ctrl+O)", self.on_open_db)
        self.create_sidebar_btn(sidebar, "📄 New Database", self.on_new_db)
        self.create_sidebar_btn(sidebar, "📤 Export CSV (Ctrl+E)", self.on_export_csv)

        # Filters & Search Card
        lbl_filters = tk.Label(sidebar, text="FILTERS & SEARCH", font=FONT_METRIC_LBL, fg=ACCENT_GOLD, bg=BG_PANEL)
        lbl_filters.pack(anchor="w", padx=14, pady=(12, 4))

        filter_card = tk.Frame(sidebar, bg=BG_PANEL, padx=12)
        filter_card.pack(fill="x")

        # Live Search
        tk.Label(filter_card, text="Search All Fields:", font=FONT_UI, fg=TEXT_MUTED, bg=BG_PANEL).pack(anchor="w")
        search_box = tk.Frame(filter_card, bg=BG_SURFACE, highlightthickness=1, highlightbackground=BORDER_COLOR)
        search_box.pack(fill="x", pady=(2, 8))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self.on_filter_changed())
        self.entry_search = tk.Entry(
            search_box,
            textvariable=self.search_var,
            font=FONT_UI,
            bg=BG_SURFACE,
            fg=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY,
            relief="flat"
        )
        self.entry_search.pack(side="left", fill="x", expand=True, padx=6, ipady=3)

        btn_clear_search = tk.Button(
            search_box,
            text="✕",
            font=FONT_UI,
            fg=TEXT_MUTED,
            bg=BG_SURFACE,
            activebackground=BG_ACTIVE,
            relief="flat",
            padx=4,
            cursor="hand2",
            command=lambda: self.search_var.set("")
        )
        btn_clear_search.pack(side="right", padx=2)

        # Status Filter
        tk.Label(filter_card, text="Filter by Status:", font=FONT_UI, fg=TEXT_MUTED, bg=BG_PANEL).pack(anchor="w")
        self.filter_status_var = tk.StringVar(value="All")
        cb_status = ttk.Combobox(
            filter_card,
            textvariable=self.filter_status_var,
            values=["All", "Active", "Inactive"],
            state="readonly",
            font=FONT_UI
        )
        cb_status.pack(fill="x", pady=(2, 8))
        cb_status.bind("<<ComboboxSelected>>", lambda e: self.on_filter_changed())

        # Department Filter
        tk.Label(filter_card, text="Filter by Department:", font=FONT_UI, fg=TEXT_MUTED, bg=BG_PANEL).pack(anchor="w")
        self.filter_dept_var = tk.StringVar(value="All")
        self.cb_filter_dept = ttk.Combobox(
            filter_card,
            textvariable=self.filter_dept_var,
            values=["All"],
            state="readonly",
            font=FONT_UI
        )
        self.cb_filter_dept.pack(fill="x", pady=(2, 8))
        self.cb_filter_dept.bind("<<ComboboxSelected>>", lambda e: self.on_filter_changed())

        btn_reset_filters = tk.Button(
            filter_card,
            text="Reset Filters",
            font=FONT_UI,
            fg=TEXT_MUTED,
            bg=BG_SURFACE,
            activebackground=BG_ACTIVE,
            activeforeground=TEXT_PRIMARY,
            relief="flat",
            pady=3,
            cursor="hand2",
            command=self.on_reset_filters
        )
        btn_reset_filters.pack(fill="x", pady=(2, 4))

    def create_sidebar_btn(self, parent, text, command, accent=TEXT_PRIMARY, is_bold=False):
        btn = tk.Button(
            parent,
            text=text,
            font=FONT_UI_BOLD if is_bold else FONT_UI,
            fg=accent,
            bg=BG_SURFACE,
            activebackground=BG_ACTIVE,
            activeforeground=TEXT_PRIMARY,
            relief="flat",
            anchor="w",
            padx=12,
            pady=4,
            cursor="hand2",
            command=command
        )
        btn.pack(fill="x", padx=12, pady=2)
        return btn

    # --------------------------------------------------------------------------
    # CENTRAL WORKSTATION (GRID + DETAIL INSPECTOR)
    # --------------------------------------------------------------------------
    def build_center_workstation(self, parent):
        self.paned = tk.PanedWindow(parent, orient="horizontal", bg=BG_MAIN, sashwidth=4, sashrelief="flat")
        self.paned.pack(side="left", fill="both", expand=True)

        # 1. Left pane: Main Data Grid
        grid_frame = tk.Frame(self.paned, bg=BG_PANEL, highlightthickness=1, highlightbackground=BORDER_COLOR)
        self.paned.add(grid_frame, minsize=420, stretch="always")

        # Grid Header Bar
        grid_top = tk.Frame(grid_frame, bg=BG_SURFACE, height=36)
        grid_top.pack(fill="x")
        grid_top.pack_propagate(False)

        self.lbl_grid_title = tk.Label(grid_top, text="WORK ITEMS DATABASE", font=FONT_UI_BOLD, fg=TEXT_PRIMARY, bg=BG_SURFACE)
        self.lbl_grid_title.pack(side="left", padx=10, pady=8)

        self.lbl_grid_count = tk.Label(grid_top, text="Showing: 0 / 0 items", font=FONT_CODE, fg=TEXT_MUTED, bg=BG_SURFACE)
        self.lbl_grid_count.pack(side="right", padx=10, pady=8)

        # Treeview Container
        tree_container = tk.Frame(grid_frame, bg=BG_PANEL)
        tree_container.pack(fill="both", expand=True)

        self.tree_scroll_y = ttk.Scrollbar(tree_container, orient="vertical")
        self.tree_scroll_x = ttk.Scrollbar(tree_container, orient="horizontal")

        self.tree = ttk.Treeview(
            tree_container,
            selectmode="browse",
            yscrollcommand=self.tree_scroll_y.set,
            xscrollcommand=self.tree_scroll_x.set
        )

        self.tree_scroll_y.config(command=self.tree.yview)
        self.tree_scroll_x.config(command=self.tree.xview)

        self.tree_scroll_y.pack(side="right", fill="y")
        self.tree_scroll_x.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)

        # Configure Tree Tags for Row Coloring
        self.tree.tag_configure("active_row", foreground=TEXT_PRIMARY)
        self.tree.tag_configure("inactive_row", foreground=TEXT_MUTED)

        # Treeview Events
        self.tree.bind("<<TreeviewSelect>>", self.on_item_selected)
        self.tree.bind("<Double-1>", lambda e: self.on_edit_item())
        self.tree.bind("<Button-3>", self.show_context_menu)

        # Right-Click Context Menu
        self.build_context_menu()

        # 2. Right pane: Item Details & Service Log Timeline
        self.inspector_frame = tk.Frame(self.paned, bg=BG_PANEL, highlightthickness=1, highlightbackground=BORDER_COLOR)
        self.paned.add(self.inspector_frame, minsize=340, width=440, stretch="never")

        self.build_inspector_ui()

    # --------------------------------------------------------------------------
    # CONTEXT MENU
    # --------------------------------------------------------------------------
    def build_context_menu(self):
        self.ctx_menu = tk.Menu(self.root, tearoff=0, bg=BG_SURFACE, fg=TEXT_PRIMARY,
                                activebackground=ACCENT_CYAN, activeforeground=BG_MAIN, font=FONT_UI)
        self.ctx_menu.add_command(label="✏️ Edit Work Item...", command=self.on_edit_item)
        self.ctx_menu.add_command(label="📝 Add Service Note...", command=self.on_add_note_dialog)
        self.ctx_menu.add_command(label="🔄 Toggle Status (Active/Inactive)", command=self.on_toggle_status)
        self.ctx_menu.add_separator()
        self.ctx_menu.add_command(label="📋 Duplicate Item", command=self.on_duplicate_item)
        self.ctx_menu.add_command(label="🗑️ Delete Item", command=self.on_delete_item)

    def show_context_menu(self, event):
        item_row = self.tree.identify_row(event.y)
        if item_row:
            self.tree.selection_set(item_row)
            self.on_item_selected(None)
            self.ctx_menu.tk_popup(event.x_root, event.y_root)

    # --------------------------------------------------------------------------
    # INSPECTOR PANEL (SERVICE LOG TIMELINE)
    # --------------------------------------------------------------------------
    def build_inspector_ui(self):
        # Header banner
        insp_header = tk.Frame(self.inspector_frame, bg=BG_SURFACE, height=36)
        insp_header.pack(fill="x")
        insp_header.pack_propagate(False)

        lbl_insp_title = tk.Label(insp_header, text="ITEM & SERVICE INSPECTOR", font=FONT_UI_BOLD, fg=ACCENT_GOLD, bg=BG_SURFACE)
        lbl_insp_title.pack(side="left", padx=10, pady=8)

        self.lbl_insp_queue = tk.Label(insp_header, text="No Selection", font=FONT_CODE_BOLD, fg=TEXT_MUTED, bg=BG_SURFACE)
        self.lbl_insp_queue.pack(side="right", padx=10, pady=8)

        # Placeholder frame when no item is selected
        self.frame_no_selection = tk.Frame(self.inspector_frame, bg=BG_PANEL)
        self.frame_no_selection.pack(fill="both", expand=True, padx=20, pady=40)

        tk.Label(self.frame_no_selection, text="🪐", font=("Segoe UI", 36), fg=BORDER_ACTIVE, bg=BG_PANEL).pack(pady=(20, 10))
        tk.Label(self.frame_no_selection, text="No Item Selected", font=FONT_UI_BOLD, fg=TEXT_PRIMARY, bg=BG_PANEL).pack()
        tk.Label(
            self.frame_no_selection,
            text="Select an item from the workstation database\nto inspect equipment details, custom attributes,\nand view or append maintenance service notes.",
            font=FONT_UI,
            fg=TEXT_MUTED,
            bg=BG_PANEL,
            justify="center"
        ).pack(pady=8)

        # Active Inspector Content Frame
        self.frame_selection_content = tk.Frame(self.inspector_frame, bg=BG_PANEL)

        # 1. Item Details Card
        self.card_details = tk.Frame(self.frame_selection_content, bg=BG_SURFACE, highlightthickness=1, highlightbackground=BORDER_COLOR, padx=12, pady=10)
        self.card_details.pack(fill="x", padx=10, pady=(8, 4))

        # Title & Status row
        r_top = tk.Frame(self.card_details, bg=BG_SURFACE)
        r_top.pack(fill="x", pady=(0, 4))
        self.lbl_item_name = tk.Label(r_top, text="Item Name", font=FONT_UI_BOLD, fg=TEXT_PRIMARY, bg=BG_SURFACE, wraplength=260, justify="left")
        self.lbl_item_name.pack(side="left")

        self.lbl_item_status_pill = tk.Label(r_top, text="ACTIVE", font=FONT_CODE_BOLD, fg=ACCENT_MINT, bg=BG_ACTIVE, padx=6, pady=2)
        self.lbl_item_status_pill.pack(side="right")

        # Info Grid
        self.lbl_item_specs = tk.Label(self.card_details, text="", font=FONT_UI, fg=TEXT_MUTED, bg=BG_SURFACE, justify="left")
        self.lbl_item_specs.pack(anchor="w", pady=(2, 4))

        # Custom Fields block
        self.lbl_custom_specs = tk.Label(self.card_details, text="", font=FONT_CODE, fg=ACCENT_CYAN, bg=BG_SURFACE, justify="left")
        self.lbl_custom_specs.pack(anchor="w", pady=(2, 0))

        # Action bar for selected item
        action_bar = tk.Frame(self.card_details, bg=BG_SURFACE)
        action_bar.pack(fill="x", pady=(8, 0))

        btn_edit = tk.Button(
            action_bar, text="✏️ Edit", font=FONT_UI, fg=TEXT_PRIMARY, bg=BG_ACTIVE,
            activebackground=BORDER_COLOR, relief="flat", padx=8, pady=2, cursor="hand2", command=self.on_edit_item
        )
        btn_edit.pack(side="left", padx=(0, 4))

        btn_toggle = tk.Button(
            action_bar, text="🔄 Toggle Status", font=FONT_UI, fg=TEXT_PRIMARY, bg=BG_ACTIVE,
            activebackground=BORDER_COLOR, relief="flat", padx=8, pady=2, cursor="hand2", command=self.on_toggle_status
        )
        btn_toggle.pack(side="left", padx=4)

        btn_del = tk.Button(
            action_bar, text="🗑️ Delete", font=FONT_UI, fg=ACCENT_CORAL, bg=BG_ACTIVE,
            activebackground=BORDER_COLOR, relief="flat", padx=8, pady=2, cursor="hand2", command=self.on_delete_item
        )
        btn_del.pack(side="right")

        # 2. Service Log Timeline Section
        sec_log = tk.Frame(self.frame_selection_content, bg=BG_PANEL)
        sec_log.pack(fill="both", expand=True, padx=10, pady=(6, 8))

        log_top = tk.Frame(sec_log, bg=BG_PANEL)
        log_top.pack(fill="x", pady=(0, 4))

        self.lbl_log_count = tk.Label(log_top, text="SERVICE LOG (0 notes)", font=FONT_METRIC_LBL, fg=ACCENT_GOLD, bg=BG_PANEL)
        self.lbl_log_count.pack(side="left")

        btn_add_note = tk.Button(
            log_top, text="+ Add Note", font=FONT_UI_BOLD, fg=BG_MAIN, bg=ACCENT_GOLD,
            activebackground="#ffe58f", relief="flat", padx=8, pady=2, cursor="hand2", command=self.on_add_note_dialog
        )
        btn_add_note.pack(side="right")

        # Scrollable Canvas for Timeline Notes
        timeline_container = tk.Frame(sec_log, bg=BG_SURFACE, highlightthickness=1, highlightbackground=BORDER_COLOR)
        timeline_container.pack(fill="both", expand=True)

        self.timeline_canvas = tk.Canvas(timeline_container, bg=BG_PANEL, highlightthickness=0)
        self.timeline_scroll = ttk.Scrollbar(timeline_container, orient="vertical", command=self.timeline_canvas.yview)
        self.timeline_cards_frame = tk.Frame(self.timeline_canvas, bg=BG_PANEL)

        self.timeline_cards_frame.bind(
            "<Configure>",
            lambda e: self.timeline_canvas.configure(scrollregion=self.timeline_canvas.bbox("all"))
        )
        self.canvas_window_id = self.timeline_canvas.create_window((0, 0), window=self.timeline_cards_frame, anchor="nw")
        self.timeline_canvas.bind(
            "<Configure>",
            lambda e: self.timeline_canvas.itemconfig(self.canvas_window_id, width=e.width)
        )
        self.timeline_canvas.configure(yscrollcommand=self.timeline_scroll.set)

        self.timeline_canvas.pack(side="left", fill="both", expand=True)
        self.timeline_scroll.pack(side="right", fill="y")

        # Quick Inline Note Add Entry at bottom of inspector
        quick_add = tk.Frame(sec_log, bg=BG_PANEL)
        quick_add.pack(fill="x", pady=(6, 0))

        self.entry_quick_note = tk.Entry(
            quick_add, font=FONT_UI, bg=BG_SURFACE, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
            relief="flat", highlightthickness=1, highlightbackground=BORDER_COLOR
        )
        self.entry_quick_note.pack(side="left", fill="x", expand=True, padx=(0, 4), ipady=3)
        self.entry_quick_note.bind("<Return>", lambda e: self.on_quick_add_note())

        btn_quick_add = tk.Button(
            quick_add, text="Log Note", font=FONT_UI, fg=BG_MAIN, bg=ACCENT_CYAN,
            activebackground="#79c0ff", relief="flat", padx=10, pady=2, cursor="hand2", command=self.on_quick_add_note
        )
        btn_quick_add.pack(side="right")

    # --------------------------------------------------------------------------
    # BOTTOM CONSOLE & STATUS BAR
    # --------------------------------------------------------------------------
    def build_bottom_panel(self):
        bottom_container = tk.Frame(self.root, bg=BG_MAIN)
        bottom_container.pack(fill="x", side="bottom", padx=12, pady=(0, 6))

        # Activity Log Console (Collapsible)
        self.console_frame = tk.Frame(bottom_container, bg=BG_PANEL, height=100, highlightthickness=1, highlightbackground=BORDER_COLOR)
        self.console_frame.pack(fill="x", pady=(0, 4))
        self.console_frame.pack_propagate(False)

        console_header = tk.Frame(self.console_frame, bg=BG_SURFACE, height=24)
        console_header.pack(fill="x")
        console_header.pack_propagate(False)

        tk.Label(console_header, text="ACTIVITY CONSOLE", font=FONT_METRIC_LBL, fg=TEXT_MUTED, bg=BG_SURFACE).pack(side="left", padx=8)

        btn_clear = tk.Button(
            console_header, text="Clear", font=("Segoe UI", 7), fg=TEXT_MUTED, bg=BG_SURFACE,
            activebackground=BG_ACTIVE, relief="flat", padx=4, cursor="hand2", command=self.clear_logs
        )
        btn_clear.pack(side="right", padx=6)

        # Log Text Box
        self.log_text = tk.Text(
            self.console_frame, font=FONT_CODE, bg=BG_PANEL, fg=TEXT_PRIMARY,
            relief="flat", wrap="word", height=4
        )
        self.log_text.pack(fill="both", expand=True, padx=8, pady=2)
        self.log_text.tag_configure("INFO", foreground=ACCENT_CYAN)
        self.log_text.tag_configure("SUCCESS", foreground=ACCENT_MINT)
        self.log_text.tag_configure("WARNING", foreground=ACCENT_GOLD)
        self.log_text.tag_configure("ERROR", foreground=ACCENT_CORAL)
        self.log_text.tag_configure("DIM", foreground=TEXT_MUTED)

        # Bottom Status Bar
        statusbar = tk.Frame(bottom_container, bg=BG_PANEL, height=26, highlightthickness=1, highlightbackground=BORDER_COLOR)
        statusbar.pack(fill="x")
        statusbar.pack_propagate(False)

        self.lbl_status_db = tk.Label(statusbar, text="", font=FONT_CODE, fg=TEXT_MUTED, bg=BG_PANEL)
        self.lbl_status_db.pack(side="left", padx=10)

        self.lbl_status_dirty = tk.Label(statusbar, text="✓ Saved", font=FONT_CODE, fg=ACCENT_MINT, bg=BG_PANEL)
        self.lbl_status_dirty.pack(side="right", padx=10)

        self.lbl_status_stats = tk.Label(statusbar, text="", font=FONT_CODE, fg=TEXT_MUTED, bg=BG_PANEL)
        self.lbl_status_stats.pack(side="right", padx=10)

    # ==========================================================================
    # DATA GRID MANAGEMENT & REFRESH
    # ==========================================================================
    def configure_columns(self):
        """Configures the Treeview columns based on core fields + user dynamic custom columns."""
        core_cols = [
            ("queue_number", "Queue #", 80),
            ("moc_number", "MOC #", 95),
            ("st_number", "ST #", 90),
            ("item_name", "Item Name", 190),
            ("make_and_model", "Make & Model", 160),
            ("status", "Status", 75),
            ("department", "Department", 140),
            ("service_log", "Service Log", 100),
        ]

        custom_cols = []
        for c in self.db.custom_columns:
            custom_cols.append((c["id"], c["name"], 120))

        all_cols = core_cols + custom_cols
        col_ids = [c[0] for c in all_cols]

        self.tree.config(columns=col_ids, show="headings")

        for c_id, c_name, c_width in all_cols:
            header_text = c_name
            if c_id == self.sort_column:
                arrow = " ▲" if not self.sort_desc else " ▼"
                header_text += arrow

            self.tree.heading(
                c_id,
                text=header_text,
                command=lambda col=c_id: self.on_sort_column(col)
            )
            self.tree.column(c_id, width=c_width, minwidth=60, anchor="w")

        # Specific column alignments
        self.tree.column("queue_number", anchor="center")
        self.tree.column("status", anchor="center")
        self.tree.column("service_log", anchor="center")

    def refresh_table(self):
        """Refreshes the Treeview with current filters and columns."""
        self.configure_columns()

        # Preserve selection
        prev_selected = self.selected_item_id

        # Clear existing items
        for r in self.tree.get_children():
            self.tree.delete(r)

        query = self.search_var.get()
        status_filter = self.filter_status_var.get()
        dept_filter = self.filter_dept_var.get()

        filtered = self.db.filter_items(
            query=query,
            status_filter=status_filter,
            department_filter=dept_filter,
            sort_by=self.sort_column,
            sort_desc=self.sort_desc
        )

        for it in filtered:
            notes_count = len(it.service_log)
            notes_str = f"📝 {notes_count} note{'s' if notes_count != 1 else ''}"

            vals = [
                it.queue_number,
                it.moc_number,
                it.st_number,
                it.item_name,
                it.make_and_model,
                it.status,
                it.department,
                notes_str
            ]

            # Append custom column values
            for c in self.db.custom_columns:
                vals.append(it.custom_fields.get(c["id"], ""))

            tag = "active_row" if it.status == "Active" else "inactive_row"
            self.tree.insert("", "end", iid=it.id, values=vals, tags=(tag,))

        # Update Grid count label
        total_items = len(self.db.items)
        shown_items = len(filtered)
        self.lbl_grid_count.config(text=f"Showing: {shown_items} / {total_items} items")

        # Update Department combobox values
        known_depts = ["All"] + self.db.get_departments()
        self.cb_filter_dept.config(values=known_depts)

        # Restore selection if possible
        if prev_selected and self.tree.exists(prev_selected):
            self.tree.selection_set(prev_selected)
            self.tree.see(prev_selected)
        elif shown_items > 0 and not prev_selected:
            # Select first item
            first_id = self.tree.get_children()[0]
            self.tree.selection_set(first_id)

        self.on_item_selected(None)
        self.update_status_bar()

    def update_metrics_cards(self):
        m = self.db.get_metrics()
        self.lbl_metric_total.config(text=str(m["total_items"]))
        self.lbl_metric_active.config(text=str(m["active_items"]))
        self.lbl_metric_inactive.config(text=str(m["inactive_items"]))
        self.lbl_metric_notes.config(text=str(m["total_notes"]))

    def update_status_bar(self):
        rel_path = os.path.basename(self.db.db_path)
        self.lbl_status_db.config(text=f"Database: {rel_path}")

        m = self.db.get_metrics()
        self.lbl_status_stats.config(text=f"Records: {m['total_items']} | Active: {m['active_items']} | Inactive: {m['inactive_items']}")

        if self.db.is_dirty:
            self.lbl_status_dirty.config(text="● Unsaved Changes", fg=ACCENT_GOLD)
            self.set_status_pill("● MODIFIED", ACCENT_GOLD)
        else:
            self.lbl_status_dirty.config(text="✓ Saved", fg=ACCENT_MINT)
            self.set_status_pill("● SYSTEM READY", ACCENT_MINT)

    # --------------------------------------------------------------------------
    # SORTING & FILTERING
    # --------------------------------------------------------------------------
    def on_sort_column(self, col_id):
        if self.sort_column == col_id:
            self.sort_desc = not self.sort_desc
        else:
            self.sort_column = col_id
            self.sort_desc = False
        self.refresh_table()

    def on_filter_changed(self):
        self.refresh_table()

    def on_reset_filters(self):
        self.search_var.set("")
        self.filter_status_var.set("All")
        self.filter_dept_var.set("All")
        self.refresh_table()

    # ==========================================================================
    # SELECTION & INSPECTOR HANDLING
    # ==========================================================================
    def on_item_selected(self, event):
        sel = self.tree.selection()
        if not sel:
            self.selected_item_id = None
            self.frame_selection_content.pack_forget()
            self.frame_no_selection.pack(fill="both", expand=True, padx=20, pady=40)
            self.lbl_insp_queue.config(text="No Selection")
            return

        item_id = sel[0]
        self.selected_item_id = item_id
        item = self.db.get_item_by_id(item_id)
        if not item:
            return

        self.frame_no_selection.pack_forget()
        self.frame_selection_content.pack(fill="both", expand=True)

        self.lbl_insp_queue.config(text=item.queue_number)
        self.lbl_item_name.config(text=item.item_name)

        status_fg = ACCENT_MINT if item.status == "Active" else ACCENT_CORAL
        self.lbl_item_status_pill.config(text=item.status.upper(), fg=status_fg)

        specs_text = (
            f"MOC Number: {item.moc_number or '—'}\n"
            f"ST Number:  {item.st_number or '—'}\n"
            f"Make/Model: {item.make_and_model or '—'}\n"
            f"Department: {item.department or '—'}\n"
            f"Created:    {item.created_at}"
        )
        self.lbl_item_specs.config(text=specs_text)

        # Custom Fields text
        if self.db.custom_columns:
            c_lines = []
            for col in self.db.custom_columns:
                val = item.custom_fields.get(col["id"], "—")
                c_lines.append(f"{col['name']}: {val}")
            self.lbl_custom_specs.config(text="\n".join(c_lines))
        else:
            self.lbl_custom_specs.config(text="")

        # Refresh Timeline Cards
        self.refresh_timeline(item)

    def refresh_timeline(self, item):
        # Clear existing timeline cards
        for w in self.timeline_cards_frame.winfo_children():
            w.destroy()

        notes = item.service_log
        self.lbl_log_count.config(text=f"SERVICE LOG ({len(notes)} note{'s' if len(notes) != 1 else ''})")

        if not notes:
            lbl_empty = tk.Label(
                self.timeline_cards_frame,
                text="No maintenance notes logged yet.\nUse '+ Add Note' or quick log below.",
                font=FONT_UI,
                fg=TEXT_MUTED,
                bg=BG_PANEL,
                pady=20
            )
            lbl_empty.pack(fill="x")
            return

        # Display notes in reverse chronological order (newest first)
        for note in reversed(notes):
            self.create_timeline_card(item, note)

    def create_timeline_card(self, item, note):
        card = tk.Frame(
            self.timeline_cards_frame,
            bg=BG_SURFACE,
            highlightthickness=1,
            highlightbackground=BORDER_COLOR,
            padx=10,
            pady=8
        )
        card.pack(fill="x", pady=4, padx=2)

        # Header: Timestamp + Actions
        top = tk.Frame(card, bg=BG_SURFACE)
        top.pack(fill="x", pady=(0, 4))

        lbl_ts = tk.Label(top, text=f"🕒 {note.timestamp}", font=FONT_CODE_BOLD, fg=ACCENT_GOLD, bg=BG_SURFACE)
        lbl_ts.pack(side="left")

        btn_del_note = tk.Button(
            top, text="✕", font=("Segoe UI", 7), fg=TEXT_MUTED, bg=BG_SURFACE,
            activebackground=BG_ACTIVE, activeforeground=ACCENT_CORAL, relief="flat", padx=3, cursor="hand2",
            command=lambda n_id=note.id: self.on_delete_service_note(item.id, n_id)
        )
        btn_del_note.pack(side="right")

        # Note Content
        lbl_note = tk.Label(
            card,
            text=note.note,
            font=FONT_UI,
            fg=TEXT_PRIMARY,
            bg=BG_SURFACE,
            wraplength=360,
            justify="left"
        )
        lbl_note.pack(anchor="w")

    # ==========================================================================
    # ITEM ACTIONS (ADD, EDIT, DELETE, DUPLICATE)
    # ==========================================================================
    def on_add_item(self):
        dlg = ItemDialog(self.root, self.db)
        self.root.wait_window(dlg)
        if dlg.result:
            r = dlg.result
            item = self.db.add_item(
                moc_number=r["moc_number"],
                st_number=r["st_number"],
                item_name=r["item_name"],
                make_and_model=r["make_and_model"],
                status=r["status"],
                department=r["department"],
                custom_fields=r["custom_fields"],
                initial_note=r["initial_note"],
                queue_number=r["queue_number"]
            )
            self.log_message(f"Created work item [{item.queue_number}] {item.item_name}", level="SUCCESS")
            self.selected_item_id = item.id
            self.refresh_table()
            self.update_metrics_cards()
            self.trigger_autosave_if_enabled()

    def on_edit_item(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Select Item", "Please select an item to edit.", parent=self.root)
            return
        item_id = sel[0]
        item = self.db.get_item_by_id(item_id)
        if not item:
            return

        dlg = ItemDialog(self.root, self.db, item=item)
        self.root.wait_window(dlg)
        if dlg.result:
            r = dlg.result
            self.db.update_item(
                item_id=item_id,
                queue_number=r["queue_number"],
                moc_number=r["moc_number"],
                st_number=r["st_number"],
                item_name=r["item_name"],
                make_and_model=r["make_and_model"],
                status=r["status"],
                department=r["department"],
                custom_fields=r["custom_fields"]
            )
            self.log_message(f"Updated work item [{item.queue_number}] {item.item_name}", level="INFO")
            self.refresh_table()
            self.update_metrics_cards()
            self.trigger_autosave_if_enabled()

    def on_delete_item(self):
        sel = self.tree.selection()
        if not sel:
            return
        item_id = sel[0]
        item = self.db.get_item_by_id(item_id)
        if not item:
            return

        confirm = messagebox.askyesno(
            "Delete Item",
            f"Are you sure you want to delete item [{item.queue_number}] '{item.item_name}'?\nThis will remove the item and all its service notes.",
            parent=self.root
        )
        if confirm:
            self.db.delete_item(item_id)
            self.log_message(f"Deleted work item [{item.queue_number}]", level="WARNING")
            self.selected_item_id = None
            self.refresh_table()
            self.update_metrics_cards()
            self.trigger_autosave_if_enabled()

    def on_toggle_status(self):
        sel = self.tree.selection()
        if not sel:
            return
        item_id = sel[0]
        new_status = self.db.toggle_status(item_id)
        item = self.db.get_item_by_id(item_id)
        self.log_message(f"Toggled status for [{item.queue_number}] to {new_status}", level="INFO")
        self.refresh_table()
        self.update_metrics_cards()
        self.trigger_autosave_if_enabled()

    def on_duplicate_item(self):
        sel = self.tree.selection()
        if not sel:
            return
        item_id = sel[0]
        item = self.db.get_item_by_id(item_id)
        if not item:
            return

        new_item = self.db.add_item(
            moc_number=item.moc_number,
            st_number=item.st_number,
            item_name=f"{item.item_name} (Copy)",
            make_and_model=item.make_and_model,
            status=item.status,
            department=item.department,
            custom_fields=item.custom_fields,
            initial_note=f"Duplicated from {item.queue_number}"
        )
        self.log_message(f"Duplicated [{item.queue_number}] to new item [{new_item.queue_number}]", level="SUCCESS")
        self.selected_item_id = new_item.id
        self.refresh_table()
        self.update_metrics_cards()
        self.trigger_autosave_if_enabled()

    # ==========================================================================
    # SERVICE LOG ACTIONS
    # ==========================================================================
    def on_add_note_dialog(self):
        if not self.selected_item_id:
            messagebox.showinfo("Select Item", "Please select an item first.", parent=self.root)
            return
        item = self.db.get_item_by_id(self.selected_item_id)
        if not item:
            return

        dlg = ServiceNoteDialog(self.root, item)
        self.root.wait_window(dlg)
        if dlg.result:
            note = self.db.add_service_note(item.id, dlg.result["note"], dlg.result["timestamp"])
            self.log_message(f"Logged maintenance note for [{item.queue_number}]: {note.note[:30]}...", level="SUCCESS")
            self.refresh_table()
            self.update_metrics_cards()
            self.trigger_autosave_if_enabled()

    def on_quick_add_note(self):
        if not self.selected_item_id:
            return
        text = self.entry_quick_note.get().strip()
        if not text:
            return
        item = self.db.get_item_by_id(self.selected_item_id)
        if not item:
            return

        self.db.add_service_note(item.id, text)
        self.entry_quick_note.delete(0, "end")
        self.log_message(f"Quick note logged for [{item.queue_number}]", level="SUCCESS")
        self.refresh_table()
        self.update_metrics_cards()
        self.trigger_autosave_if_enabled()

    def on_delete_service_note(self, item_id, note_id):
        confirm = messagebox.askyesno("Delete Note", "Delete this service log note?", parent=self.root)
        if confirm:
            self.db.delete_service_note(item_id, note_id)
            self.log_message("Service note deleted.", level="INFO")
            self.refresh_table()
            self.update_metrics_cards()
            self.trigger_autosave_if_enabled()

    # ==========================================================================
    # CUSTOM COLUMNS MANAGEMENT
    # ==========================================================================
    def on_manage_columns(self):
        dlg = ColumnManagerDialog(self.root, self.db)
        self.root.wait_window(dlg)
        if dlg.result == "COLUMNS_CHANGED":
            self.log_message("Custom columns schema updated.", level="INFO")
            self.refresh_table()
            self.trigger_autosave_if_enabled()

    # ==========================================================================
    # DATABASE PERSISTENCE & FILE OPS
    # ==========================================================================
    def on_save_db(self):
        try:
            self.db.save()
            self.save_config()
            self.update_status_bar()
            self.log_message(f"Database saved to {os.path.basename(self.db.db_path)}", level="SUCCESS")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save database:\n{e}", parent=self.root)
            self.log_message(f"Error saving database: {e}", level="ERROR")

    def on_open_db(self):
        file_path = filedialog.askopenfilename(
            title="Open OrbitTracker Database",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                self.db.load(file_path)
                self.selected_item_id = None
                self.save_config()
                self.refresh_table()
                self.update_metrics_cards()
                self.log_message(f"Opened database: {file_path}", level="SUCCESS")
            except Exception as e:
                messagebox.showerror("Error Opening Database", f"Could not load database:\n{e}", parent=self.root)
                self.log_message(f"Failed to open {file_path}: {e}", level="ERROR")

    def on_new_db(self):
        if self.db.is_dirty:
            resp = messagebox.askyesnocancel("Unsaved Changes", "Current database has unsaved changes. Save before creating a new one?", parent=self.root)
            if resp is True:
                self.on_save_db()
            elif resp is None:
                return

        file_path = filedialog.asksaveasfilename(
            title="Create New OrbitTracker Database",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if file_path:
            self.db = DatabaseManager(file_path)
            self.selected_item_id = None
            self.save_config()
            self.refresh_table()
            self.update_metrics_cards()
            self.log_message(f"Initialized new database at: {file_path}", level="SUCCESS")

    def on_export_csv(self):
        file_path = filedialog.asksaveasfilename(
            title="Export Work Items to CSV",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                self.db.export_csv(file_path)
                messagebox.showinfo("Export Successful", f"Exported {len(self.db.items)} work items to:\n{file_path}", parent=self.root)
                self.log_message(f"Exported database to CSV: {file_path}", level="SUCCESS")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export CSV:\n{e}", parent=self.root)
                self.log_message(f"CSV export failed: {e}", level="ERROR")

    def trigger_autosave_if_enabled(self):
        if self.config.get("preferences", {}).get("autosave_enabled", True):
            if self.autosave_timer is not None:
                self.root.after_cancel(self.autosave_timer)
            interval = self.config.get("preferences", {}).get("autosave_interval_ms", 3000)
            self.autosave_timer = self.root.after(interval, self.perform_autosave)

    def perform_autosave(self):
        if self.db.is_dirty:
            try:
                self.db.save()
                self.update_status_bar()
                self.log_message("Database auto-saved.", level="INFO")
            except Exception as e:
                self.log_message(f"Autosave failed: {e}", level="ERROR")

    # ==========================================================================
    # LOGGING & QUEUE
    # ==========================================================================
    def log_message(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] ", "DIM")
        self.log_text.insert("end", f"[{level:<7}] ", level)
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")

    def clear_logs(self):
        self.log_text.delete("1.0", "end")
        self.log_message("Activity log cleared.", level="INFO")

    def set_status_pill(self, text, color):
        self.status_pill.config(text=text, fg=color)

    def process_queue(self):
        try:
            while not self.background_queue.empty():
                status, callback, data = self.background_queue.get_nowait()
                if status == "SUCCESS" and callback:
                    callback(data)
                elif status == "ERROR" and callback:
                    callback(data)
        except Exception:
            pass
        finally:
            self.root.after(100, self.process_queue)

    # ==========================================================================
    # KEYBOARD SHORTCUTS & WINDOW CLOSE
    # ==========================================================================
    def bind_shortcuts(self):
        self.root.bind("<Control-n>", lambda e: self.on_add_item())
        self.root.bind("<Control-s>", lambda e: self.on_save_db())
        self.root.bind("<Control-o>", lambda e: self.on_open_db())
        self.root.bind("<Control-e>", lambda e: self.on_export_csv())
        self.root.bind("<Control-f>", lambda e: self.entry_search.focus_set())
        self.root.bind("<F5>", lambda e: self.refresh_table())
        self.root.bind("<Delete>", lambda e: self.on_delete_item())

    def on_window_close(self):
        if self.db.is_dirty and self.config.get("preferences", {}).get("confirm_exit_on_unsaved", True):
            resp = messagebox.askyesnocancel("Unsaved Changes", "Database has unsaved changes. Save before exiting?", parent=self.root)
            if resp is True:
                self.on_save_db()
                self.root.destroy()
            elif resp is False:
                self.root.destroy()
        else:
            self.root.destroy()


def main():
    root = tk.Tk()
    initial_file = None
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        initial_file = sys.argv[1]

    app = OrbitTrackerApp(root, initial_file=initial_file)
    root.mainloop()


if __name__ == "__main__":
    main()
