import pytest
import tkinter as tk
from editor.components.text_canvas import TextCanvas


@pytest.fixture
def root():
    root = tk.Tk()
    yield root
    root.destroy()


@pytest.fixture
def text_canvas(root):
    canvas = TextCanvas(root)
    return canvas


def create_key_event(char):
    """Helper function to create a key event with the given character."""
    event = type("Event", (), {})()
    event.char = char
    return event


def test_initial_state(text_canvas):
    """Test the initial state of the TextCanvas."""
    assert text_canvas.buffer == [[]]
    assert text_canvas.cursor_row == 0
    assert text_canvas.cursor_col == 0
    assert text_canvas.cursor_blink_delay == 600


def test_handle_keypress(text_canvas):
    """Test basic text input"""
    # Simulate typing 'hello'
    for char in "hello":
        event = create_key_event(char)
        text_canvas.handle_keypress(event)

    assert "".join(text_canvas.buffer[0]) == "hello"
    assert text_canvas.cursor_col == 5


def test_handle_enter(text_canvas):
    """Test pressing enter to create new line"""
    # First type some text
    for char in "test":
        event = create_key_event(char)
        text_canvas.handle_keypress(event)

    # Press enter
    text_canvas.handle_enter(None)

    assert len(text_canvas.buffer) == 2
    assert "".join(text_canvas.buffer[0]) == "test"
    assert text_canvas.buffer[1] == []


def test_handle_backspace(text_canvas):
    """Test backspace functionality"""
    # Type some text
    for char in "hello":
        event = create_key_event(char)
        text_canvas.handle_keypress(event)

    # Press backspace
    text_canvas.handle_backspace(None)

    assert "".join(text_canvas.buffer[0]) == "hell"
    assert text_canvas.cursor_col == 4


def test_cursor_movement(text_canvas):
    """Test cursor movement commands."""
    # Type "Hello\nWorld"
    for char in "Hello":
        text_canvas.handle_keypress(create_key_event(char))
    text_canvas.handle_enter(None)
    for char in "World":
        text_canvas.handle_keypress(create_key_event(char))

    # Test cursor movements
    text_canvas.move_cursor_up(None)
    assert text_canvas.cursor_row == 0
    assert text_canvas.cursor_col == 5

    text_canvas.move_cursor_left(None)
    assert text_canvas.cursor_row == 0
    assert text_canvas.cursor_col == 4

    text_canvas.move_cursor_right(None)
    assert text_canvas.cursor_row == 0
    assert text_canvas.cursor_col == 5

    text_canvas.move_cursor_down(None)
    assert text_canvas.cursor_row == 1
    assert text_canvas.cursor_col == 5


def test_multiline_backspace(text_canvas):
    """Test backspace at the beginning of a line."""
    # Create two lines and test merging them
    for char in "Hello":
        text_canvas.handle_keypress(create_key_event(char))
    text_canvas.handle_enter(None)
    for char in "World":
        text_canvas.handle_keypress(create_key_event(char))

    # Move to start of second line and backspace
    text_canvas.cursor_col = 0
    text_canvas.handle_backspace(None)

    assert "".join(text_canvas.buffer[0]) == "HelloWorld"
    assert text_canvas.cursor_row == 0
    assert text_canvas.cursor_col == 5


def test_cursor_bounds(text_canvas):
    """Test that cursor stays within valid bounds."""
    # Try moving up when at top
    text_canvas.move_cursor_up(None)
    assert text_canvas.cursor_row == 0

    # Try moving left when at start
    text_canvas.move_cursor_left(None)
    assert text_canvas.cursor_col == 0

    # Try moving right when at end of buffer
    text_canvas.move_cursor_right(None)
    assert text_canvas.cursor_col == 0

    # Try moving down when at bottom
    text_canvas.move_cursor_down(None)
    assert text_canvas.cursor_row == 0
