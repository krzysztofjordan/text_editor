import tkinter as tk

class MenuBar(tk.Menu):
    def __init__(self, parent):
        super().__init__(parent, tearoff=0)

        file_menu = tk.Menu(self, tearoff=0)
        file_menu.add_command(label="New")
        file_menu.add_command(label="Open")
        file_menu.add_command(label="Save")
        file_menu.add_separator()
        file_menu.add_command(label="Exit")
        self.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(self, tearoff=0)
        edit_menu.add_command(label="Cut")
        edit_menu.add_command(label="Copy")
        edit_menu.add_command(label="Paste")
        self.add_cascade(label="Edit", menu=edit_menu)

        view_menu = tk.Menu(self, tearoff=0)
        view_menu.add_command(label="Zoom In")
        view_menu.add_command(label="Zoom Out")
        self.add_cascade(label="View", menu=view_menu)
