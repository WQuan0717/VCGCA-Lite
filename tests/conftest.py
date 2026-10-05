"""Keep tests away from the user's settings, desktop actions and camera."""
import os
import tempfile
from copy import deepcopy

import pytest


_test_home = tempfile.TemporaryDirectory(prefix="vcgca-tests-")
os.environ["USERPROFILE"] = _test_home.name
os.environ["HOME"] = _test_home.name
os.environ["QT_QPA_PLATFORM"] = "offscreen"


@pytest.fixture(scope="session")
def qapp():
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app
    app.processEvents()


@pytest.fixture(autouse=True)
def isolated_settings(qapp):
    from src.utils.settings_manager import settings_manager
    original_defaults = deepcopy(settings_manager._defaults)
    settings_manager._settings = deepcopy(original_defaults)
    yield settings_manager
    settings_manager._defaults = original_defaults
    settings_manager._settings = deepcopy(original_defaults)

