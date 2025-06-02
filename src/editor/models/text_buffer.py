"""Handles text storage and manipulation operations"""

from .rope import Rope


class Position:
    """Represents a cursor position in the text buffer"""

    def __init__(self, row: int = 0, col: int = 0):
        self.row = row
        self.col = col

    def __eq__(self, other):
        if not isinstance(other, Position):
            return False
        return self.row == other.row and self.col == other.col


class TextBuffer:
    """Handles text storage and manipulation operations"""

    def __init__(self):
        self._rope = Rope()
        self.cursor = Position()
        self._observers = []

    def add_observer(self, observer):
        """Add an observer to be notified of buffer changes"""
        self._observers.append(observer)

    def _notify_observers(self):
        """Notify all observers that the buffer has changed"""
        for observer in self._observers:
            observer.on_buffer_changed()

    def _get_absolute_cursor_position(self) -> int:
        """Calculate the absolute character position of the cursor."""
        # Get the entire text up to the cursor's line
        text = self._rope.get_text()
        lines = text.split("\n")

        # Sum up the lengths of all lines before the cursor's line
        pos = 0
        for i in range(self.cursor.row):
            pos += len(lines[i]) + 1  # +1 for the newline character

        # Add the cursor's column position
        if self.cursor.row < len(lines):
            current_line_len = len(lines[self.cursor.row])
        else:
            current_line_len = 0
        pos += min(self.cursor.col, current_line_len)
        return pos

    def get_line(self, row: int) -> str:
        """Get the text content of a specific line"""
        try:
            return self._rope.get_line(row)
        except IndexError:
            return ""

    def get_all_text(self) -> str:
        """Get the entire text content"""
        return self._rope.get_text()

    def get_line_count(self) -> int:
        """Get the total number of lines"""
        return self._rope.get_line_count()

    def get_line_length(self, row: int) -> int:
        """Get the length of a specific line"""
        return len(self.get_line(row))

    def insert_char(self, char: str):
        """Insert a character at the current cursor position"""
        if not char:
            return

        pos = self._get_absolute_cursor_position()
        self._rope = self._rope.insert(pos, char)
        self.cursor.col += len(char)
        self._notify_observers()

    def insert_newline(self):
        """Insert a new line at the current cursor position"""
        pos = self._get_absolute_cursor_position()
        self._rope = self._rope.insert(pos, "\n")
        self.cursor.row += 1
        self.cursor.col = 0
        self._notify_observers()

    def backspace(self):
        """Delete the character before the cursor"""
        if self.cursor.col > 0:
            pos = self._get_absolute_cursor_position()
            self._rope = self._rope.delete(pos - 1, pos)
            self.cursor.col -= 1
        elif self.cursor.row > 0:
            # Cursor is at the beginning of a line, but not the first line.
            # We need to delete the newline character at the end of the
            # previous line. The absolute position of this newline is
            # equivalent to the cursor's current absolute position, minus 1.
            current_pos = self._get_absolute_cursor_position()
            if current_pos > 0:
                self.cursor.row -= 1
                self.cursor.col = self.get_line_length(self.cursor.row)
                self._rope = self._rope.delete(current_pos - 1, current_pos)
        self._notify_observers()

    def move_cursor_left(self):
        """Move the cursor one position left"""
        if self.cursor.col > 0:
            self.cursor.col -= 1
        elif self.cursor.row > 0:
            self.cursor.row -= 1
            self.cursor.col = self.get_line_length(self.cursor.row)
        self._notify_observers()

    def move_cursor_right(self):
        """Move the cursor one position right"""
        current_line_len = self.get_line_length(self.cursor.row)
        if self.cursor.col < current_line_len:
            self.cursor.col += 1
        elif self.cursor.row < self.get_line_count() - 1:
            self.cursor.row += 1
            self.cursor.col = 0
        self._notify_observers()

    def move_cursor_up(self):
        """Move the cursor one line up"""
        if self.cursor.row > 0:
            self.cursor.row -= 1
            self.cursor.col = min(
                self.cursor.col, self.get_line_length(self.cursor.row)
            )
        self._notify_observers()

    def move_cursor_down(self):
        """Move the cursor one line down"""
        if self.cursor.row < self.get_line_count() - 1:
            self.cursor.row += 1
            self.cursor.col = min(
                self.cursor.col, self.get_line_length(self.cursor.row)
            )
        self._notify_observers()

    def get_cursor_position(self) -> Position:
        """Get the current cursor position"""
        return Position(self.cursor.row, self.cursor.col)
