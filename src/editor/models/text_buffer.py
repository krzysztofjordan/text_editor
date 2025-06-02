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
        self._rope = Rope()  # Use rope instead of list of lists
        self.cursor = Position()
        self._observers = []

    def add_observer(self, observer):
        """Add an observer to be notified of buffer changes"""
        self._observers.append(observer)

    def _notify_observers(self):
        """Notify all observers that the buffer has changed"""
        for observer in self._observers:
            observer.on_buffer_changed()

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

        # Calculate absolute position from row/col
        pos = 0
        for i in range(self.cursor.row):
            line = self.get_line(i)
            pos += len(line)
            # Add newline only if not at last line or if line is not empty
            if i < self.cursor.row - 1 or line:
                pos += 1  # Add newline
        pos += self.cursor.col

        # Insert character
        self._rope = self._rope.insert(pos, char)
        self.cursor.col += 1
        self._notify_observers()

    def insert_newline(self):
        """Insert a new line at the current cursor position"""
        # Calculate absolute position
        pos = 0
        for i in range(self.cursor.row):
            line = self.get_line(i)
            pos += len(line)
            # Add newline only if not at last line or if line is not empty
            if i < self.cursor.row - 1 or line:
                pos += 1
        pos += self.cursor.col

        # Insert newline
        self._rope = self._rope.insert(pos, "\n")
        self.cursor.row += 1
        self.cursor.col = 0
        self._notify_observers()

    def backspace(self):
        """Delete the character before the cursor"""
        if self.cursor.col > 0:
            # Calculate absolute position
            pos = 0
            for i in range(self.cursor.row):
                line = self.get_line(i)
                pos += len(line)
                # Add newline only if not at last line or if line is not empty
                if i < self.cursor.row - 1 or line:
                    pos += 1
            pos += self.cursor.col

            # Delete previous character
            self._rope = self._rope.delete(pos - 1, pos)
            self.cursor.col -= 1
        elif self.cursor.row > 0:
            # Move to end of previous line
            self.cursor.row -= 1
            self.cursor.col = len(self.get_line(self.cursor.row))

            # Calculate absolute position
            pos = 0
            for i in range(self.cursor.row):
                line = self.get_line(i)
                pos += len(line)
                # Add newline only if not at last line or if line is not empty
                if i < self.cursor.row - 1 or line:
                    pos += 1
            pos += self.cursor.col

            # Delete newline
            self._rope = self._rope.delete(pos, pos + 1)

        self._notify_observers()

    def move_cursor_left(self):
        """Move the cursor one position left"""
        if self.cursor.col > 0:
            self.cursor.col -= 1
        elif self.cursor.row > 0:
            self.cursor.row -= 1
            self.cursor.col = len(self.get_line(self.cursor.row))
        self._notify_observers()

    def move_cursor_right(self):
        """Move the cursor one position right"""
        current_line_length = len(self.get_line(self.cursor.row))
        if self.cursor.col < current_line_length:
            self.cursor.col += 1
        elif self.cursor.row < self.get_line_count() - 1:
            self.cursor.row += 1
            self.cursor.col = 0
        self._notify_observers()

    def move_cursor_up(self):
        """Move the cursor one line up"""
        if self.cursor.row > 0:
            self.cursor.row -= 1
            current_line_length = len(self.get_line(self.cursor.row))
            self.cursor.col = min(self.cursor.col, current_line_length)
        self._notify_observers()

    def move_cursor_down(self):
        """Move the cursor one line down"""
        if self.cursor.row < self.get_line_count() - 1:
            self.cursor.row += 1
            current_line_length = len(self.get_line(self.cursor.row))
            self.cursor.col = min(self.cursor.col, current_line_length)
        self._notify_observers()

    def get_cursor_position(self) -> Position:
        """Get the current cursor position"""
        return Position(self.cursor.row, self.cursor.col)
