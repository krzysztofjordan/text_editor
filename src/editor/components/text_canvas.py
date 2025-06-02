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
        self.text_x = 35  # Increased left margin for line numbers
        self.text_y = 10  # Top margin

        # Window dimensions
        self.canvas_width = 0
        self.canvas_height = 0

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
        self.bind("<Configure>", self.handle_resize)
        self.bind("<Key>", self.handle_keypress)
        self.bind("<Return>", self.handle_enter)
        self.bind("<BackSpace>", self.handle_backspace)

    def handle_resize(self, event):
        """Handle window resize events"""
        self.canvas_width = event.width
        self.canvas_height = event.height
        self.render_text()

    def get_visible_lines(self):
        """Calculate how many lines can be displayed in the current window"""
        if self.canvas_height <= 0:
            return 1
        visible_height = self.canvas_height - 2 * self.text_y
        return max(1, visible_height // self.line_height)

    def get_chars_per_line(self):
        """Calculate how many characters can fit in one line"""
        if self.canvas_width <= 0:
            return 1
        return max(1, (self.canvas_width - 2 * self.text_x) // self.char_width)

    def blink_cursor(self):
        self.cursor_visible = not self.cursor_visible
        self.render_text()
        self.after(self.cursor_blink_delay, self.blink_cursor)

    def render_text(self):
        self.delete("all")

        # Calculate visible area
        visible_lines = self.get_visible_lines()
        chars_per_line = self.get_chars_per_line()

        # Draw separator line between line numbers and text
        self.create_line(
            self.text_x - 10, 0, self.text_x - 10, self.canvas_height, fill="gray90"
        )

        # Draw each line of text
        for row, line in enumerate(self.buffer):
            text = "".join(line)
            x = self.text_x
            y = self.text_y + (row * self.line_height)

            # Only render if line is in visible area
            if y + self.line_height > 0 and y < self.canvas_height:
                # Draw line number
                self.create_text(
                    self.text_x - 15,
                    y,
                    text=str(row + 1),
                    font=self.font,
                    anchor="ne",
                    fill="gray60",
                )

                # Draw text with word wrap if needed
                if len(text) > chars_per_line:
                    # Simple word wrap implementation
                    wrapped_text = ""
                    current_line = ""
                    words = text.split()

                    for word in words:
                        if len(current_line) + len(word) + 1 <= chars_per_line:
                            current_line += word + " "
                        else:
                            wrapped_text += current_line + "\n"
                            current_line = word + " "
                    wrapped_text += current_line

                    self.create_text(
                        x, y, text=wrapped_text, font=self.font, anchor="nw"
                    )
                else:
                    self.create_text(x, y, text=text, font=self.font, anchor="nw")

        # Draw blinking cursor
        if self.cursor_visible:
            cursor_x = self.text_x + (self.cursor_col * self.char_width)
            cursor_y = self.text_y + (self.cursor_row * self.line_height)
            self.create_text(cursor_x, cursor_y, text="|", font=self.font, anchor="nw")

        # Draw scrollbar if needed
        if len(self.buffer) > visible_lines:
            self.draw_scrollbar()

    def draw_scrollbar(self):
        """Draw a simple scrollbar on the right side"""
        total_lines = len(self.buffer)
        visible_lines = self.get_visible_lines()

        if total_lines > visible_lines:
            scrollbar_height = self.canvas_height
            thumb_height = max(20, scrollbar_height * (visible_lines / total_lines))
            scroll_ratio = self.cursor_row / total_lines
            thumb_pos = scroll_ratio * (scrollbar_height - thumb_height)

            # Draw scrollbar background
            self.create_rectangle(
                self.canvas_width - 10,
                0,
                self.canvas_width,
                self.canvas_height,
                fill="lightgray",
            )

            # Draw scrollbar thumb
            self.create_rectangle(
                self.canvas_width - 10,
                thumb_pos,
                self.canvas_width,
                thumb_pos + thumb_height,
                fill="gray",
            )

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
