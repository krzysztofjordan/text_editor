import tkinter as tk
from editor.components.text_canvas import TextCanvas


class SimpleTextEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simple Text Editor")
        self.geometry("600x400")

        # Create and configure the text canvas
        self.text_canvas = TextCanvas(self)
        self.text_canvas.pack(fill=tk.BOTH, expand=1)
        self.text_canvas.focus_set()


if __name__ == "__main__":
    editor = SimpleTextEditor()
    editor.mainloop()
