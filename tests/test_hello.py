import os
import sys
from analysta import hello

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def test_hello_prints_greeting(capsys):
    hello()
    captured = capsys.readouterr()
    assert captured.out.strip() == "Hello, Analysta!"
