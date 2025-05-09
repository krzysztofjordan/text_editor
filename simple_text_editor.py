import tkinter as tk


class SimpleTextEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simple Text Editor")
        self.geometry("600x400")
        self.text_widget = tk.Text(self, wrap='none', undo=True)
        self.text_widget.pack(fill=tk.BOTH, expand=1)
        self.text_widget.focus_set()
        self.bind_events()

    def bind_events(self):
        self.text_widget.bind('<Up>', self.move_cursor_up)
        self.text_widget.bind('<Down>', self.move_cursor_down)
        self.text_widget.bind('<Left>', self.move_cursor_left)
        self.text_widget.bind('<Right>', self.move_cursor_right)

    def move_cursor_up(self, event):
        self.text_widget.mark_set("insert", "insert -1 lines")
        return "break"

    def move_cursor_down(self, event):
        self.text_widget.mark_set("insert", "insert +1 lines")
        return "break"

    def move_cursor_left(self, event):
        self.text_widget.mark_set("insert", "insert -1c")
        return "break"

    def move_cursor_right(self, event):
        self.text_widget.mark_set("insert", "insert +1c")
        return "break"
