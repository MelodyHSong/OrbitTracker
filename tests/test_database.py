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

def test_structured_notes_and_analytics():
    temp_dir = tempfile.mkdtemp()
    db_file = os.path.join(temp_dir, "test_structured.json")

    try:
        db = DatabaseManager(db_file)

        # 1. Add item with structured initial note data
        item1 = db.add_item(
            moc_number="MOC-8800",
            st_number="ST-4401",
            item_name="Cryogenic Expansion Valve",
            make_and_model="Parker Hannifin Cryo-4",
            department="Cryogenics & Propulsion",
            initial_note_data={
                "problem": "Seal bypass during pressure cycle",
                "root_cause": "Thermal cycling fatigue on Teflon gasket",
                "action_taken": "Installed cryo-rated graphite seal assembly",
                "parts_consumed": "Gasket Pack #GRP-99",
                "note_type": "maintenance"
            }
        )
        assert len(item1.service_log) == 1
        n1 = item1.service_log[0]
        assert n1.note_type == "maintenance"
        assert n1.problem == "Seal bypass during pressure cycle"
        assert n1.root_cause == "Thermal cycling fatigue on Teflon gasket"
        assert n1.action_taken == "Installed cryo-rated graphite seal assembly"
        assert n1.parts_consumed == "Gasket Pack #GRP-99"
        assert "Problem:" in n1.note and "Action:" in n1.note

        # 2. Add quick note to item1
        qn = db.add_service_note(
            item1.id,
            note_type="quick",
            quick_note="Cryo specialist signed off inspection"
        )
        assert qn.note_type == "quick"
        assert qn.quick_note == "Cryo specialist signed off inspection"
        assert qn.note == "Cryo specialist signed off inspection"
        assert len(item1.service_log) == 2

        # 3. Add second item and add structured note
        item2 = db.add_item(
            moc_number="MOC-8801",
            st_number="ST-4402",
            item_name="Inertial Gyro Sensor",
            make_and_model="Honeywell HG-400",
            department="Avionics & Guidance"
        )
        n2 = db.add_service_note(
            item2.id,
            note_type="maintenance",
            problem="Drift detected on Z-axis accelerometer",
            root_cause="Vibration resonance",
            action_taken="Re-anchored mounting bracket with dampeners",
            parts_consumed="Silicone Damper Bushings"
        )
        assert n2.problem == "Drift detected on Z-axis accelerometer"
        assert n2.root_cause == "Vibration resonance"

        # 4. Save and reload to verify JSON serialization & deserialization
        db.save()
        db2 = DatabaseManager(db_file)
        r_item1 = db2.get_item_by_id(item1.id)
        assert len(r_item1.service_log) == 2
        assert r_item1.service_log[0].problem == "Seal bypass during pressure cycle"
        assert r_item1.service_log[0].parts_consumed == "Gasket Pack #GRP-99"
        assert r_item1.service_log[1].note_type == "quick"
        assert r_item1.service_log[1].quick_note == "Cryo specialist signed off inspection"

        # 5. Test Backward Compatibility: load legacy database with old schema
        legacy_file = os.path.join(temp_dir, "legacy_db.json")
        legacy_data = {
            "app_name": "OrbitTracker",
            "version": "1.0.0",
            "queue_prefix": "Q-",
            "next_queue_id": 2,
            "custom_columns": [],
            "items": [
                {
                    "id": "legacy-item-1",
                    "queue_number": "Q-001",
                    "moc_number": "MOC-OLD-1",
                    "st_number": "ST-OLD-1",
                    "item_name": "Old Solar Inverter",
                    "make_and_model": "Legacy Power Systems",
                    "status": "Active",
                    "department": "Power & Solar",
                    "custom_fields": {},
                    "service_log": [
                        {
                            "id": "old-note-1",
                            "timestamp": "2025-01-15 08:30:00",
                            "note": "Legacy maintenance note without structured fields."
                        }
                    ],
                    "created_at": "2025-01-15 08:00:00",
                    "updated_at": "2025-01-15 08:30:00"
                }
            ]
        }
        import json
        with open(legacy_file, "w", encoding="utf-8") as f:
            json.dump(legacy_data, f)

        db_legacy = DatabaseManager(legacy_file)
        assert len(db_legacy.items) == 1
        leg_it = db_legacy.items[0]
        assert len(leg_it.service_log) == 1
        leg_note = leg_it.service_log[0]
        assert leg_note.note == "Legacy maintenance note without structured fields."
        assert leg_note.problem == "Legacy maintenance note without structured fields."
        assert leg_note.note_type == "maintenance"

        # 6. Test Analytics calculation
        analytics = db2.get_work_analytics()
        assert analytics["total_items"] == 2
        assert analytics["total_notes"] == 3
        assert analytics["maintenance_notes_count"] == 2
        assert analytics["quick_notes_count"] == 1
        assert analytics["parts_consumed_count"] == 2
        assert len(analytics["timeline_monthly"]) >= 1
        assert len(analytics["dept_work"]) == 2
        assert len(analytics["parts_list"]) == 2

        print("[OK] Structured notes, backward compatibility & analytics tests passed.")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    test_database_lifecycle()
    test_structured_notes_and_analytics()

