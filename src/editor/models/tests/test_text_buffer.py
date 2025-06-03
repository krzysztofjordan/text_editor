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

    buffer.backspace()
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
    buf.backspace()

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
    # Manually construct buffer state for precise cursor positioning
    buf._rope = Rope("\n".join(text_lines))

    # Start at end of "long line|" -> (0,9)
    buf.cursor.row = 0
    buf.cursor.col = 9
    # Move to "short", cursor should be at end "short|" -> (1,5)
    buf.move_cursor_down()
    assert buf.get_cursor_position() == Position(1, 5)

    # Reset cursor to end of "longer line|" -> (2,11)
    buf.cursor.row = 2
    buf.cursor.col = 11
    # Move to "short", cursor should be at end "short|" -> (1,5)
    buf.move_cursor_up()
    assert buf.get_cursor_position() == Position(1, 5)
    # From (1,5) ("short|"), move up to "long line"
    # Original col was 5 (from being on "short" at col 5).
    # Max col on line 0 is 9.
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


def test_buffer_with_only_newline():
    """Test operations on a buffer containing only a single newline."""
    buf = TextBuffer()
    buf._rope = Rope("\n")  # Initialize with a single newline
    buf.cursor = Position(0, 0)  # Ensure cursor at start

    assert buf.get_all_text() == "\n"
    assert buf.get_line_count() == 2, "Buffer with '\n' has 2 lines"
    assert buf.get_line(0) == "", "Line 0 should be empty"
    assert buf.get_line(1) == "", "Line 1 should be empty"

    # Insert char at (0,0)
    buf.cursor = Position(0, 0)
    buf.insert_char("a")
    assert buf.get_all_text() == "a\n", "Insert at (0,0) on '\n'"
    assert buf.get_line_count() == 2
    assert buf.get_line(0) == "a"
    assert buf.get_line(1) == ""
    assert buf.get_cursor_position() == Position(0, 1)

    # Reset buffer and test insert char at (1,0)
    buf._rope = Rope("\n")
    buf.cursor = Position(1, 0)
    buf.insert_char("b")
    assert buf.get_all_text() == "\nb", "Insert at (1,0) on '\n'"
    assert buf.get_line_count() == 2
    assert buf.get_line(0) == ""
    assert buf.get_line(1) == "b"
    assert buf.get_cursor_position() == Position(1, 1)

    # Reset buffer and test backspace at (1,0)
    buf._rope = Rope("\n")
    buf.cursor = Position(1, 0)
    buf.backspace()
    assert buf.get_all_text() == "", "Backspace at (1,0) on '\n'"
    assert buf.get_line_count() == 1
    assert buf.get_line(0) == ""
    assert buf.get_cursor_position() == Position(0, 0)  # Cursor to (0,0)

    # Reset buffer and test backspace at (0,0) - should do nothing
    buf._rope = Rope("\n")
    buf.cursor = Position(0, 0)
    initial_text = buf.get_all_text()
    buf.backspace()
    assert buf.get_all_text() == initial_text, "BS at (0,0) on '\n' no change"
    assert buf.get_cursor_position() == Position(0, 0)


def test_buffer_ending_with_multiple_newlines():
    """Test operations on a buffer ending with multiple newlines."""
    buf = TextBuffer()
    initial_content = "abc\n\n"
    buf._rope = Rope(initial_content)  # "abc\n\n"
    # Line 0: "abc"
    # Line 1: ""
    # Line 2: ""

    assert buf.get_all_text() == initial_content
    assert buf.get_line_count() == 3, "'abc\n\n' should have 3 lines"
    assert buf.get_line(0) == "abc"
    assert buf.get_line(1) == ""
    assert buf.get_line(2) == ""

    # Insert char at the start of the last empty line (2,0)
    buf.cursor = Position(2, 0)
    buf.insert_char("d")
    assert buf.get_all_text() == "abc\n\nd", "Insert 'd' at (2,0)"
    assert buf.get_line_count() == 3
    assert buf.get_line(2) == "d"
    assert buf.get_cursor_position() == Position(2, 1)

    # Reset, then backspace at the start of the last empty line (2,0)
    buf._rope = Rope(initial_content)
    buf.cursor = Position(2, 0)
    buf.backspace()
    assert buf.get_all_text() == "abc\n", "BS at (2,0) removes one NL"
    assert buf.get_line_count() == 2
    assert buf.get_line(1) == ""
    # Cursor should be at the end of the previous line (line 1, which is empty)
    assert buf.get_cursor_position() == Position(1, 0)

    # Backspace again (now at (1,0) on "abc\n")
    buf.backspace()
    assert buf.get_all_text() == "abc", "BS at (1,0) removes another NL"
    assert buf.get_line_count() == 1
    assert buf.get_line(0) == "abc"
    assert buf.get_cursor_position() == Position(0, 3)  # End of "abc"


def test_operations_on_empty_line_in_middle():
    """Test operations on an empty line between other lines."""
    buf = TextBuffer()
    initial_content = "abc\n\ndef"
    buf._rope = Rope(initial_content)  # "abc\n\ndef"
    # Line 0: "abc"
    # Line 1: ""  <- Cursor will be here
    # Line 2: "def"

    # Test inserting a character on the empty line
    buf.cursor = Position(1, 0)  # Cursor at start of the empty line
    buf.insert_char("x")
    assert buf.get_all_text() == "abc\nx\ndef"
    assert buf.get_line_count() == 3
    assert buf.get_line(0) == "abc"
    assert buf.get_line(1) == "x"
    assert buf.get_line(2) == "def"
    assert buf.get_cursor_position() == Position(1, 1)

    # Reset buffer for backspace test
    buf._rope = Rope(initial_content)
    buf.cursor = Position(1, 0)  # Cursor at start of the empty line
    buf.backspace()
    # Backspacing on an empty line between two non-empty lines should join them
    assert buf.get_all_text() == "abcdef", "BS on empty mid-line joins"
    assert buf.get_line_count() == 1
    assert buf.get_line(0) == "abcdef"
    # Cursor should be at the previous end of the first line
    assert buf.get_cursor_position() == Position(0, 3)


def test_insert_empty_char(observed_buffer):
    """Test inserting an empty string does nothing."""
    buffer, observer = observed_buffer
    initial_text = buffer.get_all_text()
    initial_pos = buffer.get_cursor_position()
    initial_observer_count = observer.change_count

    buffer.insert_char("")

    assert buffer.get_all_text() == initial_text, "Text unchanged"
    assert buffer.get_cursor_position() == initial_pos, "Cursor unchanged"
    assert observer.change_count == initial_observer_count, "No notification"


def test_unicode_characters(buffer):
    """Test handling of Unicode (non-ASCII) characters."""
    # Insert a character with an accent
    buffer.insert_char("é")  # 1 character
    assert buffer.get_all_text() == "é"
    assert buffer.get_line_length(0) == 1, "Len 'é' is 1"
    assert buffer.get_cursor_position() == Position(0, 1)

    # Insert a CJK character
    buffer.insert_char("世")  # 1 character
    assert buffer.get_all_text() == "é世"
    assert buffer.get_line_length(0) == 2, "Len 'é世' is 2"
    assert buffer.get_cursor_position() == Position(0, 2)

    # Insert an emoji (might be multiple code units but one character)
    buffer.insert_char("😊")  # 1 character
    assert buffer.get_all_text() == "é世😊"
    assert buffer.get_line_length(0) == 3, "Len 'é世😊' is 3"
    assert buffer.get_cursor_position() == Position(0, 3)

    # Test backspace
    buffer.backspace()  # Delete 😊
    assert buffer.get_all_text() == "é世"
    assert buffer.get_line_length(0) == 2
    assert buffer.get_cursor_position() == Position(0, 2)

    buffer.backspace()  # Delete 世
    assert buffer.get_all_text() == "é"
    assert buffer.get_line_length(0) == 1
    assert buffer.get_cursor_position() == Position(0, 1)

    # Test inserting a newline after unicode
    buffer.insert_newline()  # Cursor at (0,1) "é|"
    assert buffer.get_all_text() == "é\n"
    assert buffer.get_line_count() == 2
    assert buffer.get_line(0) == "é"
    assert buffer.get_line(1) == ""
    assert buffer.get_cursor_position() == Position(1, 0)

    # Insert unicode on the new line
    buffer.insert_char("✅")
    assert buffer.get_all_text() == "é\n✅"
    assert buffer.get_line_length(1) == 1, "Len '✅' on new line"
    assert buffer.get_cursor_position() == Position(1, 1)

    # Test _get_absolute_cursor_position implicitly
    buf2 = TextBuffer()
    buf2.insert_char("a")
    buf2.insert_char("b")
    buf2.insert_char("世")  # ab世
    buf2.insert_char("c")  # ab世c
    buf2.cursor = Position(0, 2)  # cursor after 'b': ab|世c
    abs_pos = buf2._get_absolute_cursor_position()
    assert abs_pos == 2  # 'a' and 'b' are 1 char each

    buf2.insert_char("-")  # ab-世c
    assert buf2.get_all_text() == "ab-世c"
    assert buf2._get_absolute_cursor_position() == 3  # a, b, -


def test_clear_method(observed_buffer):
    """Test that the clear() method resets the buffer and notifies observers."""
    buffer, observer = observed_buffer

    # 1. Add some content and move cursor
    buffer.insert_char("L")
    buffer.insert_char("i")
    buffer.insert_char("n")
    buffer.insert_char("e")
    buffer.insert_char("1")
    buffer.insert_newline()
    buffer.insert_char("L")
    buffer.insert_char("i")
    buffer.insert_char("n")
    buffer.insert_char("e")
    buffer.insert_char("2")
    # Buffer: "Line1\nLine2", cursor at (1, 5)

    # 2. Reset observer count for the clear() action
    observer.change_count = 0

    # 3. Call clear()
    buffer.clear()

    # 4. Assert buffer state
    assert buffer.get_all_text() == "", "Buffer text should be empty after clear"
    assert buffer.get_line_count() == 1, "Line count should be 1 after clear"
    assert buffer.get_line(0) == "", "Line 0 should be empty after clear"

    # 5. Assert cursor position
    assert buffer.get_cursor_position() == Position(
        0, 0
    ), "Cursor should be at (0,0) after clear"

    # 6. Assert observer notification
    assert observer.change_count == 1, "Observer should be notified once by clear()"


def test_set_content_replaces_existing(observed_buffer):
    """Test that set_content correctly replaces existing buffer content."""
    buffer, observer = observed_buffer
    buffer.insert_char("O")
    buffer.insert_char("l")
    buffer.insert_char("d")
    buffer.insert_char(" ")
    buffer.insert_char("C")
    buffer.insert_char("o")
    buffer.insert_char("n")
    buffer.insert_char("t")
    buffer.insert_char("e")
    buffer.insert_char("n")
    buffer.insert_char("t")
    # Old Content: "Old Content"

    observer.change_count = 0 # Reset observer for set_content action
    new_content = "New Content\nWith multiple lines."
    buffer.set_content(new_content)

    assert buffer.get_all_text() == new_content
    assert buffer.get_line_count() == 2 # "New Content" is line 0, "With multiple lines." is line 1
    assert buffer.get_line(0) == "New Content"
    assert buffer.get_line(1) == "With multiple lines."
    assert observer.change_count == 1, "Observer should be notified once by set_content()"

def test_set_content_with_empty_string_clears_buffer(observed_buffer):
    """Test that set_content with an empty string clears the buffer."""
    buffer, observer = observed_buffer
    buffer.insert_char("S")
    buffer.insert_char("o")
    buffer.insert_char("m")
    buffer.insert_char("e")
    buffer.insert_char("t")
    buffer.insert_char("h")
    buffer.insert_char("i")
    buffer.insert_char("n")
    buffer.insert_char("g")
    # Buffer has "Something"

    observer.change_count = 0
    buffer.set_content("") # Set to empty string

    assert buffer.get_all_text() == ""
    assert buffer.get_line_count() == 1 # An empty buffer has one empty line
    assert buffer.get_line(0) == ""
    assert observer.change_count == 1

def test_set_content_resets_cursor(buffer): # Using non-observed buffer for simplicity
    """Test that the cursor is reset to Position(0,0) after set_content."""
    buffer.insert_char("a") # Make content non-empty
    buffer.insert_newline()
    buffer.insert_char("b") # Content "a\nb", cursor at (1,1)
    assert buffer.get_cursor_position() == Position(1,1)

    buffer.set_content("New text")
    assert buffer.get_cursor_position() == Position(0,0), "Cursor should be at (0,0) after set_content"

    buffer.set_content("") # Also for empty content
    assert buffer.get_cursor_position() == Position(0,0), "Cursor should be at (0,0) after set_content with empty string"

def test_set_content_notifies_observers(observed_buffer):
    """Test that observers are notified when set_content is called."""
    buffer, observer = observed_buffer
    buffer.insert_char("Initial") # Some initial content

    observer.change_count = 0 # Reset count
    buffer.set_content("New data")
    assert observer.change_count == 1, "Observer should be notified by set_content"

    observer.change_count = 0 # Reset count
    buffer.set_content("") # Also notify for setting empty content
    assert observer.change_count == 1, "Observer should be notified by set_content with empty string"
