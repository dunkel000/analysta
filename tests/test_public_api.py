import importlib.util
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import analysta


def test_version_matches_about():
    spec = importlib.util.spec_from_file_location("about", "src/analysta/__about__.py")
    about = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(about)
    assert analysta.__version__ == about.__version__


def test_all_exports():
    expected = {"Delta", "hello", "trim_whitespace", "find_duplicates"}
    assert set(analysta.__all__) == expected
    for name in expected:
        assert hasattr(analysta, name)
