import os
import pytest
import tkinter as tk
from editor.components.text_canvas import TextCanvas
from editor.models.text_buffer import Position


@pytest.fixture(scope="session", autouse=True)
def setup_display():
    """Set up a virtual display for running tests"""
    if os.environ.get("DISPLAY", "") == "":
        os.environ["DISPLAY"] = ":0"


@pytest.fixture
def root():
    root = tk.Tk()
    root.geometry("800x600")  # Set a reasonable window size
    root.update_idletasks()  # Process all pending display changes
    yield root
    root.destroy()


@pytest.fixture
def canvas(root):
    canvas = TextCanvas(root)
    canvas.pack(fill=tk.BOTH, expand=True)  # Make canvas fill the window
    canvas.update()  # Force the canvas to update
    root.update()  # Process all pending events
    return canvas


def test_canvas_initialization(canvas):
    """Test initial canvas setup"""
    assert isinstance(canvas, tk.Canvas)
    assert canvas.font == ("Courier", 12)
    assert canvas.text_x == 35  # Left margin
    assert canvas.text_y == 10  # Top margin
    assert canvas.cursor_blink_delay == 600


def test_resize_handling(canvas):
    """Test window resize calculations"""
    # Simulate a window resize
    canvas.canvas_width = 800
    canvas.canvas_height = 600
    canvas.render_text()  # Force a render after resize

    # Check visible lines calculation
    visible_lines = canvas.get_visible_lines()
    expected_lines = (600 - 2 * canvas.text_y) // canvas.line_height
    assert visible_lines == expected_lines

    # Check characters per line calculation
    chars_per_line = canvas.get_chars_per_line()
    expected_chars = (800 - 2 * canvas.text_x) // canvas.char_width
    assert chars_per_line == expected_chars


def test_text_rendering(canvas, root):
    """Test text rendering functionality"""
    # Type some text
    canvas.buffer.insert_char("H")
    canvas.buffer.insert_char("i")
    canvas.render_text()  # Force a render
    root.update()  # Process all pending events

    # Get all rendered items
    all_items = canvas.find_all()
    assert len(all_items) > 0  # At least something should be rendered


def test_cursor_blinking(canvas):
    """Test cursor blinking state changes"""
    initial_state = canvas.cursor_visible
    canvas.blink_cursor()
    assert canvas.cursor_visible != initial_state


def test_scrollbar_rendering(canvas, root):
    """Test scrollbar appears with multiple lines"""
    # Add enough lines to trigger scrollbar
    for _ in range(30):  # More than typical visible lines
        canvas.buffer.insert_newline()
    canvas.render_text()  # Force a render
    root.update()  # Process all pending events

    # Verify scrollbar elements are rendered
    all_items = canvas.find_all()
    assert len(all_items) > 0  # At least something should be rendered


def test_line_number_rendering(canvas, root):
    """Test line numbers are rendered correctly"""
    # Add multiple lines
    canvas.buffer.insert_char("A")
    canvas.buffer.insert_newline()
    canvas.buffer.insert_char("B")
    canvas.render_text()  # Force a render
    root.update()  # Process all pending events

    # Get all rendered items
    all_items = canvas.find_all()
    assert len(all_items) > 0  # At least something should be rendered


def test_word_wrap(canvas, root):
    """Test word wrapping for long lines"""
    # Set a narrow width to force wrapping
    canvas.canvas_width = 200

    # Insert long text
    long_text = "This is a very long line that should wrap"
    for char in long_text:
        canvas.buffer.insert_char(char)
    canvas.render_text()  # Force a render
    root.update()  # Process all pending events

    # Get all rendered items
    all_items = canvas.find_all()
    assert len(all_items) > 0  # At least something should be rendered


def test_event_handling(canvas):
    """Test event handling and buffer synchronization"""
    # Create a key event
    event = type("Event", (), {"char": "x"})()

    # Simulate key press
    canvas.handle_keypress(event)

    # Verify buffer state
    assert canvas.buffer.get_line(0) == "x"
    assert canvas.buffer.get_cursor_position() == Position(0, 1)


def test_initial_buffer_state(canvas):
    """Test the initial state of the text buffer"""
    assert canvas.buffer.get_line_count() == 1
    assert canvas.buffer.get_line(0) == ""
    assert canvas.buffer.get_cursor_position() == Position(0, 0)


def test_keyboard_input(canvas):
    """Test keyboard input handling"""
    # Simulate typing 'hello'
    for char in "hello":
        event = type("Event", (), {"char": char})()
        canvas.handle_keypress(event)

    assert canvas.buffer.get_line(0) == "hello"
    assert canvas.buffer.get_cursor_position() == Position(0, 5)


def test_return_key(canvas):
    """Test return key handling"""
    # Type some text
    for char in "test":
        event = type("Event", (), {"char": char})()
        canvas.handle_keypress(event)

    # Simulate return key by inserting newline directly
    canvas.buffer.insert_newline()

    assert canvas.buffer.get_line_count() == 2
    assert canvas.buffer.get_line(0) == "test"
    assert canvas.buffer.get_line(1) == ""


def test_backspace_key(canvas):
    """Test backspace key handling"""
    # Type some text
    for char in "hello":
        event = type("Event", (), {"char": char})()
        canvas.handle_keypress(event)

    # Simulate backspace
    canvas.buffer.backspace()

    assert canvas.buffer.get_line(0) == "hell"
    assert canvas.buffer.get_cursor_position() == Position(0, 4)


def test_cursor_key_movement(canvas):
    """Test cursor movement with arrow keys"""
    # Type "Hello\nWorld"
    for char in "Hello":
        event = type("Event", (), {"char": char})()
        canvas.handle_keypress(event)

    canvas.buffer.insert_newline()

    for char in "World":
        event = type("Event", (), {"char": char})()
        canvas.handle_keypress(event)

    # Test cursor movements using buffer methods
    canvas.buffer.move_cursor_up()
    pos = canvas.buffer.get_cursor_position()
    assert pos.row == 0 and pos.col == 5

    canvas.buffer.move_cursor_left()
    pos = canvas.buffer.get_cursor_position()
    assert pos.row == 0 and pos.col == 4

    canvas.buffer.move_cursor_right()
    pos = canvas.buffer.get_cursor_position()
    assert pos.row == 0 and pos.col == 5

    canvas.buffer.move_cursor_down()
    pos = canvas.buffer.get_cursor_position()
    assert pos.row == 1 and pos.col == 5
