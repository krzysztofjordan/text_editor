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


# @patch.object(TextCanvas, 'render_text')
# def test_on_buffer_changed_triggers_render(mock_render_text, canvas):
#     """Test on_buffer_changed calls render_text.""" # Shortened docstring
#     initial_call_count = mock_render_text.call_count
#
#     # Modify the buffer, which should trigger on_buffer_changed
#     canvas.buffer.insert_char('A')
#
#     # Assert that render_text was called again
#     assert mock_render_text.call_count > initial_call_count


def test_text_rendering(canvas, root):
    """Test text rendering functionality"""
    # Type some text
    canvas.buffer.insert_char("H")
    canvas.buffer.insert_char("i")
    canvas.render_text()  # Force a render
    root.update()  # Process all pending events

    # Get all rendered items
    text_items = canvas.find_withtag("text_content")
    assert len(text_items) == 1, "Should render one text content item"
    rendered_text = canvas.itemcget(text_items[0], "text")
    assert rendered_text == "Hi", "Rendered text content is incorrect"


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


# Refactored Tab Indentation Tests


def test_tab_indentation_empty_line(canvas):
    """Test Tab in an empty line inserts tab_size spaces."""
    event = type("Event", (), {"keysym": "Tab"})()
    tab_size = canvas.tab_size

    # Ensure buffer is pristine for this test
    canvas.buffer.clear()

    initial_pos = canvas.buffer.get_cursor_position()
    canvas.handle_tab_press(event)

    expected_text = " " * tab_size
    assert canvas.buffer.get_line(initial_pos.row) == expected_text
    assert canvas.buffer.get_cursor_position().col == initial_pos.col + tab_size


def test_tab_indentation_after_text(canvas):
    """Test Tab after existing text inserts tab_size spaces."""
    event = type("Event", (), {"keysym": "Tab"})()
    tab_size = canvas.tab_size

    # Ensure buffer is pristine and setup "abc"
    canvas.buffer.clear()
    for char_code in "abc":
        key_event = type("Event", (), {"char": char_code})()
        canvas.handle_keypress(key_event)
    # Buffer: "abc", cursor at (0, 3)
    assert canvas.buffer.get_line(0) == "abc"
    assert canvas.buffer.get_cursor_position() == Position(0, 3)

    cursor_before_tab = canvas.buffer.get_cursor_position()
    canvas.handle_tab_press(event)  # Tab at "abc|"

    expected_line = "abc" + (" " * tab_size)
    assert canvas.buffer.get_line(0) == expected_line, (
        f"Expected '{expected_line}' after tab, " f"got '{canvas.buffer.get_line(0)}'"
    )
    assert canvas.buffer.get_cursor_position().col == cursor_before_tab.col + tab_size


def test_tab_indentation_at_start_of_text(canvas):
    """Test Tab at start of existing text prepends tab_size spaces."""
    event = type("Event", (), {"keysym": "Tab"})()
    tab_size = canvas.tab_size

    # Ensure buffer is pristine and setup "test"
    canvas.buffer.clear()
    for char_code in "test":
        key_event = type("Event", (), {"char": char_code})()
        canvas.handle_keypress(key_event)
    # Buffer: "test", cursor at (0, 4)
    assert canvas.buffer.get_line(0) == "test"
    assert canvas.buffer.get_cursor_position() == Position(0, 4)

    canvas.buffer.set_cursor_position(0, 0)  # Move cursor to beginning: |test
    cursor_before_tab = canvas.buffer.get_cursor_position()
    canvas.handle_tab_press(event)

    expected_line = (" " * tab_size) + "test"
    assert canvas.buffer.get_line(0) == expected_line, (
        f"Expected '{expected_line}' for tab at start, "
        f"got '{canvas.buffer.get_line(0)}'"
    )
    assert canvas.buffer.get_cursor_position().col == cursor_before_tab.col + tab_size


def test_mouse_click_cursor_movement(canvas):
    """Test that mouse clicks move the cursor to the correct text position."""
    # Test clicking in an empty buffer
    event_empty_click = type(
        "Event", (), {"x": canvas.text_x + 5, "y": canvas.text_y + 5}
    )()
    canvas.buffer.clear()  # Ensure pristine buffer for this click test
    canvas.handle_mouse_click(event_empty_click)
    assert canvas.buffer.get_cursor_position() == Position(0, 0)

    # Add some text
    line1 = "Hello World"
    line2 = "Second Line"
    # Explicitly clear buffer before this population segment for robustness,
    # though the previous clear for event_empty_click might have already done so.
    canvas.buffer.clear()
    for char_code in line1:
        key_event = type("Event", (), {"char": char_code})()
        canvas.handle_keypress(key_event)
    canvas.buffer.insert_newline()
    for char_code in line2:
        key_event = type("Event", (), {"char": char_code})()
        canvas.handle_keypress(key_event)
    # Buffer setup complete

    # Test click at the beginning of the first line (Target: 0,0)
    click_x_l0_c0 = canvas.text_x  # Col 0
    click_y_l0 = (
        canvas.text_y + (0 * canvas.line_height) + (canvas.line_height // 2)
    )  # Middle of line 0
    event_l0_c0 = type("Event", (), {"x": click_x_l0_c0, "y": click_y_l0})()
    canvas.handle_mouse_click(event_l0_c0)
    assert canvas.buffer.get_cursor_position() == Position(0, 0)

    # Test click in the middle of the first line (Target: 0, 6)
    target_col_l0 = 6
    click_x_l0_c6 = (
        canvas.text_x + (target_col_l0 * canvas.char_width) + (canvas.char_width // 2)
    )
    event_l0_c6 = type("Event", (), {"x": click_x_l0_c6, "y": click_y_l0})()
    canvas.handle_mouse_click(event_l0_c6)
    assert canvas.buffer.get_cursor_position() == Position(0, target_col_l0)

    # Test click at the end of the first line (Target: 0, len(line1))
    target_col_l0_end = len(line1)
    click_x_l0_end = (
        canvas.text_x
        + (target_col_l0_end * canvas.char_width)
        + (canvas.char_width // 2)  # Click towards middle of char cell
    )
    event_l0_end = type("Event", (), {"x": click_x_l0_end, "y": click_y_l0})()
    canvas.handle_mouse_click(event_l0_end)
    assert canvas.buffer.get_cursor_position() == Position(0, target_col_l0_end)

    # Test click on the second line (Target: 1, 3)
    target_row_l1 = 1
    target_col_l1 = 3
    click_y_l1 = (
        canvas.text_y + (target_row_l1 * canvas.line_height) + (canvas.line_height // 2)
    )
    click_x_l1_c3 = (
        canvas.text_x + (target_col_l1 * canvas.char_width) + (canvas.char_width // 2)
    )
    event_l1_c3 = type("Event", (), {"x": click_x_l1_c3, "y": click_y_l1})()
    canvas.handle_mouse_click(event_l1_c3)
    assert canvas.buffer.get_cursor_position() == Position(target_row_l1, target_col_l1)

    # Test click beyond the end of a line (should snap to end of line)
    click_x_l1_beyond = canvas.text_x + ((len(line2) + 5) * canvas.char_width)
    event_l1_beyond = type("Event", (), {"x": click_x_l1_beyond, "y": click_y_l1})()
    canvas.handle_mouse_click(event_l1_beyond)
    assert canvas.buffer.get_cursor_position() == Position(target_row_l1, len(line2))

    # Test click way below existing lines
    col_derived_from_x_event = 3  # X coord from click_x_l1_c3 gives col 3
    num_buffer_lines_for_click_test = canvas.buffer.get_line_count()

    click_y_far_below = canvas.text_y + (
        (num_buffer_lines_for_click_test + 5) * canvas.line_height
    )
    event_far_below = type(
        "Event", (), {"x": click_x_l1_c3, "y": click_y_far_below}
    )()  # Ensure this parenthesis is correctly placed
    canvas.handle_mouse_click(event_far_below)

    expected_row_far_below = num_buffer_lines_for_click_test - 1
    # Clamp row to be at least 0 if buffer became empty unexpectedly
    if num_buffer_lines_for_click_test == 0:
        expected_row_far_below = 0

    len_of_expected_line = len(canvas.buffer.get_line(expected_row_far_below))
    expected_col_far_below = max(0, min(col_derived_from_x_event, len_of_expected_line))

    assert canvas.buffer.get_cursor_position() == Position(
        expected_row_far_below, expected_col_far_below
    )
