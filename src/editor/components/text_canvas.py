import tkinter as tk
import tkinter.font as tkfont
from editor.models.text_buffer import TextBuffer


class TextCanvas(tk.Canvas):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Initialize text buffer
        self.buffer = TextBuffer()
        self.buffer.add_observer(self)

        # Configure font and dimensions
        self.font = ("Courier", 12)
        self.font_obj = tkfont.Font(family="Courier", size=12)
        self.char_width = self.font_obj.measure("0")
        self.line_height = self.font_obj.metrics()["linespace"]
        self.text_x = 35  # Increased left margin for line numbers
        self.text_y = 10  # Top margin

        # Tab size
        self.tab_size = 4  # Default tab size

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
        self.bind("<Up>", lambda e: self.buffer.move_cursor_up())
        self.bind("<Down>", lambda e: self.buffer.move_cursor_down())
        self.bind("<Left>", lambda e: self.buffer.move_cursor_left())
        self.bind("<Right>", lambda e: self.buffer.move_cursor_right())
        self.bind("<Configure>", self.handle_resize)
        self.bind("<Key>", self.handle_keypress)
        self.bind("<Return>", lambda e: self.buffer.insert_newline())
        self.bind("<BackSpace>", lambda e: self.buffer.backspace())
        self.bind("<Tab>", self.handle_tab_press)
        self.bind("<Button-1>", self.handle_mouse_click)

    def on_buffer_changed(self):
        """Called by TextBuffer when its content changes"""
        self.render_text()

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
        separator_x = self.text_x - 10
        self.create_line(separator_x, 0, separator_x, self.canvas_height, fill="gray90")

        # Draw each line of text
        for row in range(self.buffer.get_line_count()):
            text = self.buffer.get_line(row)
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
                        line_len = len(current_line) + len(word) + 1
                        if line_len <= chars_per_line:
                            current_line += word + " "
                        else:
                            wrapped_text += current_line + "\n"
                            current_line = word + " "
                    wrapped_text += current_line

                    self.create_text(
                        x,
                        y,
                        text=wrapped_text,
                        font=self.font,
                        anchor="nw",
                        tags=("text_content", f"text_content_row_{row}"),
                    )
                else:
                    self.create_text(
                        x,
                        y,
                        text=text,
                        font=self.font,
                        anchor="nw",
                        tags=("text_content", f"text_content_row_{row}"),
                    )

        # Draw blinking cursor
        if self.cursor_visible:
            cursor_pos = self.buffer.get_cursor_position()
            x = self.text_x + (cursor_pos.col * self.char_width)
            y = self.text_y + (cursor_pos.row * self.line_height)
            self.create_text(x, y, text="|", font=self.font, anchor="nw")

        # Draw scrollbar if needed
        if self.buffer.get_line_count() > visible_lines:
            self.draw_scrollbar()

    def draw_scrollbar(self):
        """Draw a simple scrollbar."""
        total_lines = self.buffer.get_line_count()
        visible_lines = self.get_visible_lines()

        if total_lines > visible_lines:
            scrollbar_height = self.canvas_height
            thumb_height = max(20, scrollbar_height * (visible_lines / total_lines))
            cursor_pos = self.buffer.get_cursor_position()
            scroll_ratio = cursor_pos.row / total_lines
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

    def handle_keypress(self, event):
        # Ignore special keys and modifier keys
        if len(event.char) == 0 or event.char == "\r" or event.char == "\x08":
            return "break"

        self.buffer.insert_char(event.char)
        return "break"

    def handle_tab_press(self, event):
        """Handle Tab key press for indentation."""
        for _ in range(self.tab_size):
            self.buffer.insert_char(" ")
        return "break"

    def handle_mouse_click(self, event):
        """Handle left mouse clicks to move the cursor."""
        clicked_row = (event.y - self.text_y) // self.line_height
        clicked_col = (event.x - self.text_x) // self.char_width

        # The TextBuffer.set_cursor_position method now handles validation.
        self.buffer.set_cursor_position(clicked_row, clicked_col)

    # Helper methods for testing
    def get_text(self):
        """Returns the entire text content as a string."""
        return self.buffer.get_all_text()

    def get_cursor_position(self):
        """Returns the current cursor position as (row, col)."""
        pos = self.buffer.get_cursor_position()
        return (pos.row, pos.col)
