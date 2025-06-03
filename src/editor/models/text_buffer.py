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
            current_pos = self._get_absolute_cursor_position()
            if current_pos > 0:
                original_cursor_row = self.cursor.row

                # Standard cursor update: to end of previous line
                self.cursor.row -= 1
                self.cursor.col = self.get_line_length(self.cursor.row)

                delete_start = current_pos - 1
                delete_end = current_pos  # Default: delete 1 char

                # If the line where backspace was pressed was empty,
                # and current_pos is not at the very end of the document,
                # extend deletion to remove the newline forming the empty line.
                if self.get_line_length(original_cursor_row) == 0 and current_pos < len(
                    self._rope
                ):
                    delete_end = current_pos + 1

                self._rope = self._rope.delete(delete_start, delete_end)
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

    def set_cursor_position(self, row: int, col: int):
        """Set the cursor to a specific row and column."""
        # Ensure row is within buffer bounds
        num_lines = self.get_line_count()
        if num_lines == 0:
            validated_row = 0
        else:
            validated_row = max(0, min(row, num_lines - 1))

        # Ensure col is within line bounds
        if num_lines == 0:
            validated_col = 0
        else:
            line_len = self.get_line_length(validated_row)
            validated_col = max(0, min(col, line_len))

        self.cursor.row = validated_row
        self.cursor.col = validated_col
        self._notify_observers()

    def clear(self):
        """Clear the entire text buffer and reset cursor position."""
        self._rope = Rope()  # Re-initialize with a new empty Rope
        self.cursor = Position(0, 0)
        self._notify_observers()

    def set_content(self, content: str):
        """
        Replaces the entire content of the buffer with the provided string.

        The cursor is reset to Position(0,0), and observers are notified.

        Args:
            content: The new string content for the buffer.
        """
        self._rope = Rope(content)  # Initialize Rope directly with the new content
        self.cursor = Position(0, 0)   # Reset cursor to the beginning
        self._notify_observers()       # Notify observers of the change
