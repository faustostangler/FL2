import re

from infrastructure.config.config import Config
from infrastructure.logging.context_tracker import ContextTracker


def sample_function():
    tracker = ContextTracker(Config().paths.root_dir)
    return tracker.get_import_path()


def test_get_import_path_contains_function_name():
    path = sample_function()
    assert re.search(r"test_get_import_path_contains_function_name$", path)
