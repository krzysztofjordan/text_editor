import pytest
import tkinter as tk
from simple_text_editor import SimpleTextEditor


@pytest.fixture
def editor():
    app = SimpleTextEditor()
    yield app
    app.destroy()


def test_editor_initial_title(editor):
    assert editor.title() == "Simple Text Editor"


def test_text_widget_exists(editor):
    assert isinstance(editor.text_widget, tk.Text)


def test_cursor_movement(editor):
    editor.text_widget.insert('1.0', 'Hello\nWorld')
    editor.text_widget.mark_set('insert', '2.0')
    # Move cursor up
    editor.move_cursor_up(None)
    assert editor.text_widget.index('insert') == '1.0'
    # Move cursor down
    editor.move_cursor_down(None)
    assert editor.text_widget.index('insert') == '2.0'
    # Move cursor left
    editor.move_cursor_left(None)
    assert editor.text_widget.index('insert') == '1.5'
    # Move cursor right
    editor.move_cursor_right(None)
    assert editor.text_widget.index('insert') == '2.0'
