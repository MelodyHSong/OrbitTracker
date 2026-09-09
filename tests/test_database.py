import os
import sys
import tempfile
import shutil

# Ensure workspace root is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from database import DatabaseManager, WorkItem, ServiceNote

def test_database_lifecycle():
    temp_dir = tempfile.mkdtemp()
    db_file = os.path.join(temp_dir, "test_orbit.json")

    try:
        # 1. Initialize DB
        db = DatabaseManager(db_file)
        assert len(db.items) == 0
        assert db.peek_next_queue_number() == "Q-001"

        # 2. Add an item
        item1 = db.add_item(
            moc_number="MOC-1001",
            st_number="ST-8821",
            item_name="Hydro-Valve Controller",
            make_and_model="Parker Hannifin V-200",
            status="Active",
            department="Fluids & Hydraulics",
            initial_note="Installed initial pressure gasket"
        )
        assert item1.queue_number == "Q-001"
        assert len(item1.service_log) == 1
        assert item1.service_log[0].note == "Installed initial pressure gasket"
        assert db.peek_next_queue_number() == "Q-002"

        # 3. Add second item
        item2 = db.add_item(
            moc_number="MOC-1002",
            st_number="ST-9943",
            item_name="Primary Sensor Array",
            make_and_model="Honeywell MicroSens 4",
            status="Inactive",
            department="Avionics & Telemetry"
        )
        assert item2.queue_number == "Q-002"
        assert len(item2.service_log) == 0

        # 4. Add notes to item2
        note1 = db.add_service_note(item2.id, "Received from manufacturer, awaiting firmware flash.")
        note2 = db.add_service_note(item2.id, "Firmware updated to v2.4.1. Calibrated successfully.")
        assert len(item2.service_log) == 2

        # 4b. Test editing service notes
        success = db.update_service_note(item2.id, note1.id, "Received from vendor; firmware flash scheduled.", "2026-09-08 10:00:00")
        assert success is True
        assert item2.service_log[0].note == "Received from vendor; firmware flash scheduled."
        assert item2.service_log[0].timestamp == "2026-09-08 10:00:00"
        assert db.is_dirty is True

        # Test editing with nonexistent note or item ID
        assert db.update_service_note(item2.id, "nonexistent-id", "New text") is False
        assert db.update_service_note("nonexistent-item", note1.id, "New text") is False

        # 5. Add custom column
        col = db.add_custom_column("Facility Bay", default_val="Main Hangar")
        col_id = col["id"]
        assert item1.custom_fields[col_id] == "Main Hangar"
        assert item2.custom_fields[col_id] == "Main Hangar"

        # Update custom field for item 1
        db.update_item(item1.id, custom_fields={col_id: "Cryo Bay 3"})
        assert item1.custom_fields[col_id] == "Cryo Bay 3"

        # 6. Save and reload
        db.save()
        assert os.path.exists(db_file)

        db2 = DatabaseManager(db_file)
        assert len(db2.items) == 2
        assert db2.peek_next_queue_number() == "Q-003"
        assert len(db2.custom_columns) == 1
        reloaded_item1 = db2.get_item_by_id(item1.id)
        assert reloaded_item1.custom_fields[col_id] == "Cryo Bay 3"
        assert len(reloaded_item1.service_log) == 1

        # 7. Test filters
        active_items = db2.filter_items(status_filter="Active")
        assert len(active_items) == 1
        assert active_items[0].id == item1.id

        fluids_items = db2.filter_items(department_filter="Fluids & Hydraulics")
        assert len(fluids_items) == 1

        search_note = db2.filter_items(query="firmware")
        assert len(search_note) == 1
        assert search_note[0].id == item2.id

        # 8. Test metrics
        metrics = db2.get_metrics()
        assert metrics["total_items"] == 2
        assert metrics["active_items"] == 1
        assert metrics["inactive_items"] == 1
        assert metrics["total_notes"] == 3

        # 9. Test toggle status
        new_status = db2.toggle_status(item2.id)
        assert new_status == "Active"

        # 10. Test CSV export
        csv_file = os.path.join(temp_dir, "test_export.csv")
        db2.export_csv(csv_file)
        assert os.path.exists(csv_file)

        # 11. Test Queue number always follows the highest one
        # Currently items are Q-001 and Q-002, so next is Q-003
        assert db2.peek_next_queue_number() == "Q-003"
        item_high = db2.add_item(
            moc_number="MOC-1050",
            st_number="ST-5555",
            item_name="Deep Space Comm Array",
            make_and_model="General Dynamics DS-10",
            queue_number="Q-050"
        )
        assert item_high.queue_number == "Q-050"
        # Next should now follow highest (50 -> 51)
        assert db2.peek_next_queue_number() == "Q-051"

        # Update queue number of an item higher (50 -> 75)
        db2.update_item(item_high.id, queue_number="Q-075")
        assert db2.peek_next_queue_number() == "Q-076"

        # Delete highest item; next should drop back to Q-003
        db2.delete_item(item_high.id)
        assert db2.peek_next_queue_number() == "Q-003"

        print("[OK] Database tests passed.")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    test_database_lifecycle()
