"""Tests for the TextBuffer class"""

import pytest
from editor.models.text_buffer import TextBuffer, Position

# Rope is not directly used in tests, but is a dependency of TextBuffer
from editor.models.rope import Rope


class MockObserver:
    def __init__(self):
        self.change_count = 0

    def on_buffer_changed(self):
        self.change_count += 1


@pytest.fixture
def buffer():
    return TextBuffer()


@pytest.fixture
def observed_buffer():
    buffer = TextBuffer()
    observer = MockObserver()
    buffer.add_observer(observer)
    return buffer, observer


def test_initial_state():
    """Test TextBuffer initialization."""
    buf = TextBuffer()
    assert buf.get_all_text() == ""
    assert buf.get_line_count() == 1
    assert buf.get_line(0) == ""
    assert buf.get_cursor_position() == Position(0, 0)


def test_insert_char(observed_buffer):
    """Test inserting characters"""
    buffer, observer = observed_buffer

    # Insert single character
    buffer.insert_char("a")
    assert buffer.get_line(0) == "a"
    assert buffer.get_cursor_position() == Position(0, 1)
    assert observer.change_count == 1

    # Insert multiple characters
    for char in "bcde":
        buffer.insert_char(char)
    assert buffer.get_line(0) == "abcde"
    assert buffer.get_cursor_position() == Position(0, 5)
    assert observer.change_count == 5


def test_insert_newline(observed_buffer):
    """Test line splitting with enter key"""
    buffer, observer = observed_buffer

    # Type some text and split it
    for char in "Hello World":
        buffer.insert_char(char)

    # Move cursor to middle and press enter
    buffer.cursor.col = 6
    buffer.insert_newline()

    assert buffer.get_line_count() == 2
    assert buffer.get_line(0) == "Hello "
    assert buffer.get_line(1) == "World"
    assert buffer.get_cursor_position() == Position(1, 0)


def test_backspace(observed_buffer):
    """Test backspace functionality"""
    buffer, observer = observed_buffer

    # Type text and delete with backspace
    for char in "Hello":
        buffer.insert_char(char)

    buffer.backspace()  # Delete 'o'
    assert buffer.get_line(0) == "Hell"
    assert buffer.get_cursor_position() == Position(0, 4)

    # Test backspace at start of line
    buffer.insert_newline()
    for char in "World":
        buffer.insert_char(char)

    # Move to start of second line and backspace
    buffer.cursor.col = 0
    buffer.backspace()

    assert buffer.get_line_count() == 1
    assert buffer.get_line(0) == "HellWorld"
    assert buffer.get_cursor_position() == Position(0, 4)


def test_cursor_movement(buffer):
    """Test cursor movement in all directions"""
    # Setup some text
    for char in "Hello\nWorld":
        if char == "\n":
            buffer.insert_newline()
        else:
            buffer.insert_char(char)

    # Test moving right
    buffer.cursor = Position(0, 0)
    buffer.move_cursor_right()
    assert buffer.get_cursor_position() == Position(0, 1)

    # Test moving right at end of line
    buffer.cursor = Position(0, 5)
    buffer.move_cursor_right()
    assert buffer.get_cursor_position() == Position(1, 0)

    # Test moving left
    buffer.cursor = Position(1, 1)
    buffer.move_cursor_left()
    assert buffer.get_cursor_position() == Position(1, 0)

    # Test moving left at start of line
    buffer.cursor = Position(1, 0)
    buffer.move_cursor_left()
    assert buffer.get_cursor_position() == Position(0, 5)

    # Test moving up
    buffer.cursor = Position(1, 2)
    buffer.move_cursor_up()
    assert buffer.get_cursor_position() == Position(0, 2)

    # Test moving down
    buffer.cursor = Position(0, 2)
    buffer.move_cursor_down()
    assert buffer.get_cursor_position() == Position(1, 2)


def test_cursor_bounds(buffer):
    """Test cursor stays within valid bounds"""
    # Test at document start
    buffer.move_cursor_left()
    assert buffer.get_cursor_position() == Position(0, 0)
    buffer.move_cursor_up()
    assert buffer.get_cursor_position() == Position(0, 0)

    # Test at document end
    buffer.move_cursor_right()
    assert buffer.get_cursor_position() == Position(0, 0)
    buffer.move_cursor_down()
    assert buffer.get_cursor_position() == Position(0, 0)

    # Test with some text
    buffer.insert_char("a")
    buffer.cursor.col = 0
    buffer.move_cursor_left()
    assert buffer.get_cursor_position() == Position(0, 0)


def test_insert_char_simple():
    """Test simple character insertion."""
    buf = TextBuffer()
    buf.insert_char("H")
    assert buf.get_all_text() == "H"
    assert buf.get_cursor_position() == Position(0, 1)
    buf.insert_char("i")
    assert buf.get_all_text() == "Hi"
    assert buf.get_cursor_position() == Position(0, 2)


def test_insert_newline_empty_buffer():
    """Test inserting a newline in an empty buffer."""
    buf = TextBuffer()
    buf.insert_newline()
    assert buf.get_all_text() == "\n"
    assert buf.get_line_count() == 2
    assert buf.get_line(0) == ""
    assert buf.get_line(1) == ""
    assert buf.get_cursor_position() == Position(1, 0)


def test_insert_newline_in_middle_of_line():
    """Test inserting a newline in the middle of a line."""
    buf = TextBuffer()
    buf.insert_char("H")
    buf.insert_char("e")
    buf.insert_char("l")
    buf.insert_char("l")
    buf.insert_char("o")
    # Cursor at H e l l o |
    buf.cursor.col = 2  # Move cursor to H e | l l o
    buf.insert_newline()
    assert buf.get_all_text() == "He\nllo"
    assert buf.get_line_count() == 2
    assert buf.get_line(0) == "He"
    assert buf.get_line(1) == "llo"
    assert buf.get_cursor_position() == Position(1, 0)


def test_sequence_type_enter_enter_char():
    """Test the sequence: type '1', press Enter, press Enter, type '2'."""
    buf = TextBuffer()
    # Type '1'
    buf.insert_char("1")
    assert buf.get_all_text() == "1"
    assert buf.get_cursor_position() == Position(0, 1)

    # Press Enter (1st time)
    buf.insert_newline()
    assert buf.get_all_text() == "1\n"
    assert buf.get_line_count() == 2
    assert buf.get_line(0) == "1"
    assert buf.get_line(1) == ""
    assert buf.get_cursor_position() == Position(1, 0)

    # Press Enter (2nd time)
    buf.insert_newline()
    assert buf.get_all_text() == "1\n\n"
    assert buf.get_line_count() == 3
    assert buf.get_line(0) == "1"
    assert buf.get_line(1) == ""
    assert buf.get_line(2) == ""
    assert buf.get_cursor_position() == Position(2, 0)

    # Type '2'
    buf.insert_char("2")
    assert buf.get_all_text() == "1\n\n2"
    assert buf.get_line_count() == 3
    assert buf.get_line(0) == "1"
    assert buf.get_line(1) == ""
    assert buf.get_line(2) == "2"
    assert buf.get_cursor_position() == Position(2, 1)


def test_backspace_simple():
    """Test simple backspace."""
    buf = TextBuffer()
    buf.insert_char("a")
    buf.insert_char("b")  # Buffer: "ab", cursor at (0,2)
    buf.backspace()
    assert buf.get_all_text() == "a"
    assert buf.get_cursor_position() == Position(0, 1)
    buf.backspace()
    assert buf.get_all_text() == ""
    assert buf.get_cursor_position() == Position(0, 0)
    buf.backspace()  # Should do nothing
    assert buf.get_all_text() == ""
    assert buf.get_cursor_position() == Position(0, 0)


def test_backspace_join_lines():
    """Test backspace that joins two lines."""
    buf = TextBuffer()
    buf.insert_char("a")
    buf.insert_newline()  # Buffer: "a\n", cursor at (1,0)
    buf.insert_char("b")  # Buffer: "a\nb", cursor at (1,1)

    buf.cursor.row = 1
    buf.cursor.col = 0  # Move cursor to beginning of second line: "a\n|b"
    buf.backspace()  # Should delete the newline

    assert buf.get_all_text() == "ab"
    assert buf.get_line_count() == 1
    assert buf.get_line(0) == "ab"
    assert buf.get_cursor_position() == Position(0, 1)  # Cursor after 'a'


def test_backspace_at_beginning_of_buffer():
    """Test backspace at the very beginning of the buffer."""
    buf = TextBuffer()
    buf.backspace()
    assert buf.get_all_text() == ""
    assert buf.get_cursor_position() == Position(0, 0)


def test_move_cursor_left_right_simple():
    """Test simple left/right cursor movement on a single line."""
    buf = TextBuffer()
    buf.insert_char("H")
    buf.insert_char("i")  # "Hi", cursor (0,2)
    buf.move_cursor_left()
    assert buf.get_cursor_position() == Position(0, 1)
    buf.move_cursor_left()
    assert buf.get_cursor_position() == Position(0, 0)
    buf.move_cursor_left()  # At beginning
    assert buf.get_cursor_position() == Position(0, 0)
    buf.move_cursor_right()
    assert buf.get_cursor_position() == Position(0, 1)
    buf.move_cursor_right()
    assert buf.get_cursor_position() == Position(0, 2)
    buf.move_cursor_right()  # At end
    assert buf.get_cursor_position() == Position(0, 2)


def test_move_cursor_left_right_multiline():
    """Test left/right cursor movement across multiple lines."""
    buf = TextBuffer()
    buf.insert_char("a")
    buf.insert_char("b")  # "ab"
    buf.insert_newline()  # "ab\n"
    buf.insert_char("c")
    buf.insert_char("d")  # "ab\ncd"

    # Start at end of buffer: "ab\ncd|" -> cursor (1,2)
    buf.cursor.row = 1
    buf.cursor.col = 2

    buf.move_cursor_left()  # "ab\nc|d" -> (1,1)
    assert buf.get_cursor_position() == Position(1, 1)
    buf.move_cursor_left()  # "ab\n|cd" -> (1,0)
    assert buf.get_cursor_position() == Position(1, 0)
    buf.move_cursor_left()  # "ab|\ncd" -> (0,2) (end of previous line)
    assert buf.get_cursor_position() == Position(0, 2)
    buf.move_cursor_left()  # "a|b\ncd" -> (0,1)
    assert buf.get_cursor_position() == Position(0, 1)

    # From "a|b\ncd" (0,1)
    buf.move_cursor_right()  # "ab|\ncd" -> (0,2)
    assert buf.get_cursor_position() == Position(0, 2)
    buf.move_cursor_right()  # "ab\n|cd" -> (1,0) (start of next line)
    assert buf.get_cursor_position() == Position(1, 0)
    buf.move_cursor_right()  # "ab\nc|d" -> (1,1)
    assert buf.get_cursor_position() == Position(1, 1)


def test_move_cursor_up_down():
    """Test up/down cursor movement."""
    buf = TextBuffer()
    buf.insert_char("l")
    buf.insert_char("i")
    buf.insert_char("n")
    buf.insert_char("e")
    buf.insert_char("0")
    buf.insert_newline()
    buf.insert_char("l")
    buf.insert_char("i")
    buf.insert_char("n")
    buf.insert_char("e")
    buf.insert_char("1")
    buf.insert_newline()
    buf.insert_char("l")
    buf.insert_char("i")
    buf.insert_char("n")
    buf.insert_char("e")
    buf.insert_char("2")

    # Start at "line0\nline1\nlin|e2" -> (2,3)
    buf.cursor.row = 2
    buf.cursor.col = 3
    assert buf.get_cursor_position() == Position(2, 3)

    buf.move_cursor_up()  # "line0\nlin|e1\nline2" -> (1,3)
    assert buf.get_cursor_position() == Position(1, 3)
    buf.move_cursor_up()  # "lin|e0\nline1\nline2" -> (0,3)
    assert buf.get_cursor_position() == Position(0, 3)
    buf.move_cursor_up()  # Still (0,3) - at top
    assert buf.get_cursor_position() == Position(0, 3)

    # From "lin|e0\nline1\nline2" (0,3)
    buf.move_cursor_down()  # "line0\nlin|e1\nline2" -> (1,3)
    assert buf.get_cursor_position() == Position(1, 3)
    buf.move_cursor_down()  # "line0\nline1\nlin|e2" -> (2,3)
    assert buf.get_cursor_position() == Position(2, 3)
    buf.move_cursor_down()  # Still (2,3) - at bottom
    assert buf.get_cursor_position() == Position(2, 3)


def test_move_cursor_up_down_to_shorter_line():
    """Test up/down cursor movement to a shorter line."""
    buf = TextBuffer()
    text_lines = ["long line", "short", "longer line"]
    # Manually construct buffer state for precise cursor positioning before moves
    buf._rope = Rope("\n".join(text_lines))

    # Start at end of "long line|" -> (0,9)
    buf.cursor.row = 0
    buf.cursor.col = 9
    buf.move_cursor_down()  # Move to "short", cursor should be at end "short|" -> (1,5)
    assert buf.get_cursor_position() == Position(1, 5)

    # Reset cursor to end of "longer line|" -> (2,11)
    buf.cursor.row = 2
    buf.cursor.col = 11
    buf.move_cursor_up()  # Move to "short", cursor should be at end "short|" -> (1,5)
    assert buf.get_cursor_position() == Position(1, 5)
    # From (1,5) ("short|"), move up to "long line"
    # Original col was 5 (from being on "short" at col 5). Max col on line 0 is 9.
    # Cursor should go to (0,5) which is "long |line"
    buf.move_cursor_up()
    assert buf.get_cursor_position() == Position(0, 5)


def test_get_line_length():
    buf = TextBuffer()
    buf.insert_char("H")
    buf.insert_char("i")
    assert buf.get_line_length(0) == 2
    buf.insert_newline()
    assert buf.get_line_length(0) == 2  # Line 0 is still "Hi"
    assert buf.get_line_length(1) == 0  # Line 1 is empty
    buf.insert_char("T")
    buf.insert_char("h")
    buf.insert_char("e")
    buf.insert_char("r")
    buf.insert_char("e")
    assert buf.get_line_length(1) == 5  # Line 1 is "There"


def test_observer_notification():
    """Test that observers are notified on buffer changes."""

    class MockObserver:
        def __init__(self):
            self.notified_count = 0

        def on_buffer_changed(self):
            self.notified_count += 1

    buf = TextBuffer()
    observer = MockObserver()
    buf.add_observer(observer)

    buf.insert_char("x")
    assert observer.notified_count == 1
    observer.notified_count = 0

    buf.insert_newline()
    assert observer.notified_count == 1
    observer.notified_count = 0

    # Backspace on non-empty line
    buf.insert_char("y")  # buffer is "x\ny", cursor (1,1)
    observer.notified_count = 0
    buf.backspace()  # buffer is "x\n", cursor (1,0)
    assert observer.notified_count == 1
    observer.notified_count = 0

    # Backspace to join lines
    buf.backspace()  # buffer is "x", cursor (0,1)
    assert observer.notified_count == 1
    observer.notified_count = 0

    # Movements also notify
    buf.move_cursor_down()  # No effect if only one line
    assert observer.notified_count == 1
    observer.notified_count = 0

    buf.move_cursor_left()
    assert observer.notified_count == 1
    observer.notified_count = 0

    buf.move_cursor_right()  # No effect if at end of line
    assert observer.notified_count == 1
    observer.notified_count = 0

    buf.move_cursor_up()  # No effect if on first line
    assert observer.notified_count == 1
    observer.notified_count = 0
