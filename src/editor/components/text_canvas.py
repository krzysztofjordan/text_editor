import tkinter as tk
import tkinter.font as tkfont


class TextCanvas(tk.Canvas):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Initialize text buffer as 2D array of characters
        self.buffer = [[]]
        self.cursor_row = 0
        self.cursor_col = 0

        # Configure font and dimensions
        self.font = ("Courier", 12)
        self.font_obj = tkfont.Font(family="Courier", size=12)
        self.char_width = self.font_obj.measure("0")
        self.line_height = self.font_obj.metrics()["linespace"]
        self.text_x = 10  # Left margin
        self.text_y = 10  # Top margin

        # Cursor blinking state
        self.cursor_visible = True
        self.cursor_blink_delay = 600  # milliseconds

        self.bind_events()
        self.render_text()
        self.blink_cursor()

    def bind_events(self):
        self.bind("<Up>", self.move_cursor_up)
        self.bind("<Down>", self.move_cursor_down)
        self.bind("<Left>", self.move_cursor_left)
        self.bind("<Right>", self.move_cursor_right)
        self.bind("<Configure>", lambda e: self.render_text())
        self.bind("<Key>", self.handle_keypress)
        self.bind("<Return>", self.handle_enter)
        self.bind("<BackSpace>", self.handle_backspace)

    def blink_cursor(self):
        self.cursor_visible = not self.cursor_visible
        self.render_text()
        self.after(self.cursor_blink_delay, self.blink_cursor)

    def render_text(self):
        self.delete("all")

        # Draw each line of text
        for row, line in enumerate(self.buffer):
            text = "".join(line)
            x = self.text_x
            y = self.text_y + (row * self.line_height)
            self.create_text(x, y, text=text, font=self.font, anchor="nw")

        # Draw blinking cursor
        if self.cursor_visible:
            cursor_x = self.text_x + (self.cursor_col * self.char_width)
            cursor_y = self.text_y + (self.cursor_row * self.line_height)
            self.create_text(cursor_x, cursor_y, text="|", font=self.font, anchor="nw")

    def move_cursor_up(self, event):
        if self.cursor_row > 0:
            self.cursor_row -= 1
            # Ensure cursor doesn't go beyond line length
            max_col = len(self.buffer[self.cursor_row])
            self.cursor_col = min(self.cursor_col, max_col)
            self.render_text()
        return "break"

    def move_cursor_down(self, event):
        if self.cursor_row < len(self.buffer) - 1:
            self.cursor_row += 1
            # Ensure cursor doesn't go beyond line length
            max_col = len(self.buffer[self.cursor_row])
            self.cursor_col = min(self.cursor_col, max_col)
            self.render_text()
        return "break"

    def move_cursor_left(self, event):
        if self.cursor_col > 0:
            self.cursor_col -= 1
        elif self.cursor_row > 0:
            # Move to end of previous line
            self.cursor_row -= 1
            self.cursor_col = len(self.buffer[self.cursor_row])
        self.render_text()
        return "break"

    def move_cursor_right(self, event):
        if self.cursor_col < len(self.buffer[self.cursor_row]):
            self.cursor_col += 1
        elif self.cursor_row < len(self.buffer) - 1:
            # Move to start of next line
            self.cursor_row += 1
            self.cursor_col = 0
        self.render_text()
        return "break"

    def handle_keypress(self, event):
        # Ignore special keys and modifier keys
        if len(event.char) == 0 or event.char == "\r" or event.char == "\x08":
            return "break"

        # Insert character at current cursor position
        current_line = self.buffer[self.cursor_row]
        current_line.insert(self.cursor_col, event.char)
        self.cursor_col += 1
        self.render_text()
        return "break"

    def handle_enter(self, event):
        # Split current line at cursor position
        current_line = self.buffer[self.cursor_row]
        new_line = current_line[self.cursor_col :]
        self.buffer[self.cursor_row] = current_line[: self.cursor_col]

        # Insert new line after current line
        self.buffer.insert(self.cursor_row + 1, list(new_line))

        # Move cursor to beginning of new line
        self.cursor_row += 1
        self.cursor_col = 0
        self.render_text()
        return "break"

    def handle_backspace(self, event):
        if self.cursor_col > 0:
            # Remove character before cursor in current line
            current_line = self.buffer[self.cursor_row]
            current_line.pop(self.cursor_col - 1)
            self.cursor_col -= 1
        elif self.cursor_row > 0:
            # At start of line, merge with previous line
            current_line = self.buffer[self.cursor_row]
            prev_line = self.buffer[self.cursor_row - 1]
            self.cursor_col = len(prev_line)
            prev_line.extend(current_line)
            self.buffer.pop(self.cursor_row)
            self.cursor_row -= 1
        self.render_text()
        return "break"

    # Helper methods for testing
    def get_text(self):
        """Returns the entire text content as a string."""
        return "\n".join("".join(line) for line in self.buffer)

    def get_cursor_position(self):
        """Returns the current cursor position as (row, col)."""
        return (self.cursor_row, self.cursor_col)
