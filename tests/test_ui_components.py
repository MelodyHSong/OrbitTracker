import os
import sys
import tempfile
import shutil
import tkinter as tk

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import OrbitTrackerApp
from database import DatabaseManager
from dialogs import WorkAnalyticsDialog, ServiceNoteDialog, ItemDialog

def test_ui_and_dialogs():
    temp_dir = tempfile.mkdtemp()
    test_db_path = os.path.join(temp_dir, "test_ui_db.json")
    # Pre-initialize and save database so prompt_database_init modal is not triggered
    init_db = DatabaseManager(test_db_path)
    init_db.save()

    root = tk.Tk()
    root.withdraw()  # Hide main window for headless automated testing

    try:
        # Initialize app with fresh test database
        app = OrbitTrackerApp(root, initial_file=test_db_path)
        root.update()

        # 1. Add item with structured initial maintenance note
        item = app.db.add_item(
            moc_number="MOC-TEST-1",
            st_number="ST-TEST-1",
            item_name="Hydraulic Servo Actuator",
            make_and_model="Moog Series 30",
            department="Hydraulics & Actuation",
            initial_note_data={
                "problem": "Actuator piston seal degraded under 3000 PSI",
                "root_cause": "Fluid thermal expansion past 85C",
                "action_taken": "Replaced Viton seal pack with fluorosilicone",
                "parts_consumed": "Seal Kit #MOOG-VK-1",
                "note_type": "maintenance"
            }
        )
        app.selected_item_id = item.id
        app.refresh_table()
        app.update_metrics_cards()
        root.update()

        assert len(item.service_log) == 1
        assert item.service_log[0].problem == "Actuator piston seal degraded under 3000 PSI"
        assert item.service_log[0].parts_consumed == "Seal Kit #MOOG-VK-1"

        # 2. Add quick note via inline entry
        app.entry_quick_note.insert(0, "Carrier delivered replacement solenoid valve.")
        app.on_quick_add_note()
        root.update()

        assert len(item.service_log) == 2
        assert item.service_log[1].note_type == "quick"
        assert item.service_log[1].quick_note == "Carrier delivered replacement solenoid valve."

        # 3. Test timeline filters
        app.set_timeline_filter("quick")
        root.update()
        cards = app.timeline_cards_frame.winfo_children()
        assert len(cards) == 1  # only quick note

        app.set_timeline_filter("maintenance")
        root.update()
        cards = app.timeline_cards_frame.winfo_children()
        assert len(cards) == 1  # only maintenance note

        app.set_timeline_filter("all")
        root.update()
        cards = app.timeline_cards_frame.winfo_children()
        assert len(cards) == 2  # both notes

        # 4. Test WorkAnalyticsDialog rendering and all tab switches
        analytics_dlg = WorkAnalyticsDialog(root, app.db)
        root.update()

        tabs = ["activity", "department", "intensity", "root_causes", "parts"]
        for t in tabs:
            analytics_dlg.switch_tab(t)
            root.update()
            # Verify canvas has drawn items
            assert len(analytics_dlg.canvas.find_all()) > 0
            print(f"[OK] Analytics chart '{t}' rendered successfully.")

        # Test hover tooltip simulation on canvas
        if analytics_dlg.chart_items:
            x1, y1, x2, y2, tip = analytics_dlg.chart_items[0]
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            event = type("Event", (), {"x": mid_x, "y": mid_y})()
            analytics_dlg.on_canvas_motion(event)
            root.update()
            assert len(analytics_dlg.canvas.find_withtag("tooltip")) > 0
            analytics_dlg.on_canvas_leave(event)
            root.update()
            assert len(analytics_dlg.canvas.find_withtag("tooltip")) == 0
            print("[OK] Canvas interactive tooltips tested.")

        analytics_dlg.destroy()
        root.update()

        # 5. Test Backward Compatibility: Load the project's actual orbit_database.json
        real_db_path = os.path.join(BASE_DIR, "orbit_database.json")
        if os.path.exists(real_db_path):
            real_db = DatabaseManager(real_db_path)
            assert len(real_db.items) > 0
            # Test that all service logs load with .note, .note_type, and .problem
            for it in real_db.items:
                for n in it.service_log:
                    assert n.note != ""
                    assert n.problem != ""
                    assert n.note_type in ("maintenance", "quick")
            print(f"[OK] Real database '{real_db_path}' backward compatibility confirmed ({len(real_db.items)} items).")

        print("[OK] All UI component tests passed successfully!")
    finally:
        try:
            root.destroy()
        except Exception:
            pass
        shutil.rmtree(temp_dir, ignore_errors=True)
        test_cfg = os.path.join(BASE_DIR, "tests", "config.json")
        if os.path.exists(test_cfg):
            try:
                os.remove(test_cfg)
            except Exception:
                pass

if __name__ == "__main__":
    test_ui_and_dialogs()
