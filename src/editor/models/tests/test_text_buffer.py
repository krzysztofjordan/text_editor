import pytest
from editor.models.text_buffer import TextBuffer, Position


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


def test_initial_state(buffer):
    """Test the initial state of the buffer"""
    assert buffer.get_line_count() == 1
    assert buffer.get_line(0) == ""
    assert buffer.get_all_text() == ""
    pos = buffer.get_cursor_position()
    assert (pos.row, pos.col) == (0, 0)


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
