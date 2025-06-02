import pytest
import tkinter as tk
from editor.main import SimpleTextEditor
from editor.components.text_canvas import TextCanvas


@pytest.fixture
def editor():
    editor = SimpleTextEditor()
    yield editor
    editor.destroy()


def test_editor_initialization(editor):
    """Test if the editor window initializes correctly"""
    assert isinstance(editor, tk.Tk)
    assert editor.title() == "Simple Text Editor"

    # Check if text canvas was created
    assert hasattr(editor, "text_canvas")
    assert isinstance(editor.text_canvas, TextCanvas)

    # Update geometry to ensure it's set
    editor.geometry("600x400")
    editor.update()
    geometry = editor.geometry()
    width, height = map(int, geometry.split("+")[0].split("x"))
    assert width == 600
    assert height == 400
