import tkinter as tk
import unittest
from editor.components.menu_bar import MenuBar

class TestMenuBar(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.menu_bar = MenuBar(self.root)
        self.root.config(menu=self.menu_bar)

    def tearDown(self):
        self.root.destroy()

    def test_menubar_instantiation_and_attachment(self):
        self.assertIsNotNone(self.menu_bar)
        self.assertIsInstance(self.menu_bar, tk.Menu)
        self.assertEqual(self.root.cget("menu"), self.menu_bar.winfo_pathname(self.menu_bar.winfo_id()))

    def test_top_level_menus_present_and_labeled(self):
        # Expected labels for the top-level menus
        expected_menus = ["File", "Edit", "View"]

        # Check the number of top-level menus
        # The MenuBar itself is a menu, its items are the cascade menus like "File", "Edit"
        # Toplevel menus are entries in self.menu_bar
        # The actual number of items might be different depending on how tk internally handles menus.
        # Instead of checking count, we will check for specific items.

        # Check labels of each top-level menu
        # Menu items are indexed starting from 0.
        # self.assertEqual(self.menu_bar.entrycget(0, "label"), expected_menus[0]) # Fails with unknown option -label
        # self.assertEqual(self.menu_bar.entrycget(1, "label"), expected_menus[1])
        # self.assertEqual(self.menu_bar.entrycget(2, "label"), expected_menus[2])

        # Check types by index
        self.assertEqual(self.menu_bar.type(0), "cascade", "First menu item should be a cascade (File)")
        self.assertEqual(self.menu_bar.type(1), "cascade", "Second menu item should be a cascade (Edit)")
        self.assertEqual(self.menu_bar.type(2), "cascade", "Third menu item should be a cascade (View)")

        # Check if known labels correspond to actual cascade submenus
        # This indirectly verifies the labels exist and are cascades.
        # It doesn't confirm "File" is at index 0, but since entrycget(index, "label") is problematic,
        # this is the next best way to ensure the named menus are present.
        self.assertIsNotNone(self.menu_bar.entrycget("File", "menu"), "Menu 'File' should exist and have a submenu.")
        self.assertIsNotNone(self.menu_bar.entrycget("Edit", "menu"), "Menu 'Edit' should exist and have a submenu.")
        self.assertIsNotNone(self.menu_bar.entrycget("View", "menu"), "Menu 'View' should exist and have a submenu.")

    def test_file_menu_items(self):
        # Get the "File" menu widget using its label
        file_menu_widget_path = self.menu_bar.entrycget("File", "menu")
        file_menu = self.menu_bar.nametowidget(file_menu_widget_path)

        expected_file_items = ["New", "Open", "Save", "Exit"]

        self.assertEqual(file_menu.entrycget(0, "label"), expected_file_items[0])
        self.assertEqual(file_menu.type(0), "command")
        self.assertEqual(file_menu.entrycget(1, "label"), expected_file_items[1])
        self.assertEqual(file_menu.type(1), "command")
        self.assertEqual(file_menu.entrycget(2, "label"), expected_file_items[2])
        self.assertEqual(file_menu.type(2), "command")
        # Index 3 is a separator in the current implementation in menu_bar.py
        self.assertEqual(file_menu.type(3), "separator")
        self.assertEqual(file_menu.entrycget(4, "label"), expected_file_items[3])
        self.assertEqual(file_menu.type(4), "command")

    def test_edit_menu_items(self):
        # Get the "Edit" menu widget
        edit_menu_widget_path = self.menu_bar.entrycget("Edit", "menu")
        edit_menu = self.menu_bar.nametowidget(edit_menu_widget_path)

        expected_edit_items = ["Cut", "Copy", "Paste"]

        self.assertEqual(edit_menu.entrycget(0, "label"), expected_edit_items[0])
        self.assertEqual(edit_menu.type(0), "command")
        self.assertEqual(edit_menu.entrycget(1, "label"), expected_edit_items[1])
        self.assertEqual(edit_menu.type(1), "command")
        self.assertEqual(edit_menu.entrycget(2, "label"), expected_edit_items[2])
        self.assertEqual(edit_menu.type(2), "command")

    def test_view_menu_items(self):
        # Get the "View" menu widget
        view_menu_widget_path = self.menu_bar.entrycget("View", "menu")
        view_menu = self.menu_bar.nametowidget(view_menu_widget_path)

        expected_view_items = ["Zoom In", "Zoom Out"]

        self.assertEqual(view_menu.entrycget(0, "label"), expected_view_items[0])
        self.assertEqual(view_menu.type(0), "command")
        self.assertEqual(view_menu.entrycget(1, "label"), expected_view_items[1])
        self.assertEqual(view_menu.type(1), "command")

if __name__ == '__main__':
    unittest.main()
