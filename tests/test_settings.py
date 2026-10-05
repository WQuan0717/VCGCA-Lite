from src.utils.settings_manager import settings_manager
from src.core.gesture_controller import GestureController
from src.windows.settings_window import SettingsWindow


def test_reset_restores_original_defaults():
    settings_manager.reset_to_defaults()
    settings_manager.set("general", "copy_to_clipboard", True)
    settings_manager.set("gesture", "mappings", [])
    settings_manager.reset_to_defaults()
    assert settings_manager.get("general", "copy_to_clipboard") is False
    assert len(settings_manager.get("gesture", "mappings")) == 4


def test_getters_do_not_expose_mutable_settings():
    snapshot = settings_manager.get_all_settings()
    snapshot["general"]["auto_start"] = True
    section = settings_manager.get_section("gesture")
    section["mappings"].clear()
    mappings = settings_manager.get("gesture", "mappings")
    mappings.clear()
    assert settings_manager.get("general", "auto_start") is False
    assert len(settings_manager.get("gesture", "mappings")) == 4


def test_empty_mappings_stay_disabled_after_save_and_reload():
    settings_manager.set("gesture", "mappings", [])
    assert settings_manager.save_settings()
    settings_manager.load_settings()
    controller = GestureController()
    assert controller.mappings == []
    window = SettingsWindow()
    try:
        assert window.gesture_mapping_table.rowCount() == 0
        window.save_settings()
        assert settings_manager.get("gesture", "mappings") == []
    finally:
        window.close()
        window.deleteLater()


def test_restore_defaults_resets_all_general_controls():
    settings_manager.set("general", "copy_to_clipboard", True)
    settings_manager.set("general", "screenshot_path", "C:/custom-screenshots")
    settings_manager.set("general", "show_open_folder", False)
    window = SettingsWindow()
    try:
        window.restore_defaults()
        assert window.copy_to_clipboard_cb.isChecked() is False
        assert window.screenshot_path_edit.text() == ""
        assert window.show_open_folder_cb.isChecked() is True
    finally:
        window.close()
        window.deleteLater()


def test_non_object_json_falls_back_to_defaults(tmp_path, monkeypatch):
    config_file = tmp_path / "settings.json"
    config_file.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(settings_manager, "_config_file", str(config_file))
    settings_manager.load_settings()
    assert settings_manager.get("gesture", "prepare_time") == 1000


def test_failed_save_preserves_existing_file(tmp_path, monkeypatch):
    import importlib
    manager_module = importlib.import_module("src.utils.settings_manager")
    config_file = tmp_path / "settings.json"
    config_file.write_text('{"general": {"auto_start": false}}', encoding="utf-8")
    original = config_file.read_bytes()
    monkeypatch.setattr(settings_manager, "_config_file", str(config_file))

    def fail_replace(*args):
        raise OSError("disk write failed")

    monkeypatch.setattr(manager_module.os, "replace", fail_replace)
    assert settings_manager.save_settings() is False
    assert config_file.read_bytes() == original
    assert list(tmp_path.iterdir()) == [config_file]

