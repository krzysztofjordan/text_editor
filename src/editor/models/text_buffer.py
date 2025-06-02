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
        self._lines = [[]]  # Start with one empty line
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
        if 0 <= row < len(self._lines):
            return "".join(self._lines[row])
        return ""

    def get_all_text(self) -> str:
        """Get the entire text content"""
        return "\n".join("".join(line) for line in self._lines)

    def get_line_count(self) -> int:
        """Get the total number of lines"""
        return len(self._lines)

    def get_line_length(self, row: int) -> int:
        """Get the length of a specific line"""
        if 0 <= row < len(self._lines):
            return len(self._lines[row])
        return 0

    def insert_char(self, char: str):
        """Insert a character at the current cursor position"""
        if not char:
            return

        current_line = self._lines[self.cursor.row]
        current_line.insert(self.cursor.col, char)
        self.cursor.col += 1
        self._notify_observers()

    def insert_newline(self):
        """Insert a new line at the current cursor position"""
        current_line = self._lines[self.cursor.row]
        new_line = current_line[self.cursor.col :]
        self._lines[self.cursor.row] = current_line[: self.cursor.col]
        self._lines.insert(self.cursor.row + 1, list(new_line))
        self.cursor.row += 1
        self.cursor.col = 0
        self._notify_observers()

    def backspace(self):
        """Delete the character before the cursor"""
        if self.cursor.col > 0:
            # Remove character in current line
            current_line = self._lines[self.cursor.row]
            current_line.pop(self.cursor.col - 1)
            self.cursor.col -= 1
        elif self.cursor.row > 0:
            # Merge with previous line
            current_line = self._lines[self.cursor.row]
            prev_line = self._lines[self.cursor.row - 1]
            self.cursor.col = len(prev_line)
            prev_line.extend(current_line)
            self._lines.pop(self.cursor.row)
            self.cursor.row -= 1
        self._notify_observers()

    def move_cursor_left(self):
        """Move the cursor one position left"""
        if self.cursor.col > 0:
            self.cursor.col -= 1
        elif self.cursor.row > 0:
            self.cursor.row -= 1
            self.cursor.col = len(self._lines[self.cursor.row])
        self._notify_observers()

    def move_cursor_right(self):
        """Move the cursor one position right"""
        current_line_length = len(self._lines[self.cursor.row])
        if self.cursor.col < current_line_length:
            self.cursor.col += 1
        elif self.cursor.row < len(self._lines) - 1:
            self.cursor.row += 1
            self.cursor.col = 0
        self._notify_observers()

    def move_cursor_up(self):
        """Move the cursor one line up"""
        if self.cursor.row > 0:
            self.cursor.row -= 1
            current_line_length = len(self._lines[self.cursor.row])
            self.cursor.col = min(self.cursor.col, current_line_length)
        self._notify_observers()

    def move_cursor_down(self):
        """Move the cursor one line down"""
        if self.cursor.row < len(self._lines) - 1:
            self.cursor.row += 1
            current_line_length = len(self._lines[self.cursor.row])
            self.cursor.col = min(self.cursor.col, current_line_length)
        self._notify_observers()

    def get_cursor_position(self) -> Position:
        """Get the current cursor position"""
        return Position(self.cursor.row, self.cursor.col)
