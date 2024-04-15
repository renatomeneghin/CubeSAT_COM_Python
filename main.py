#! /usr/bin/env python
# -*- coding: utf-8 -*-
import gi
gi.require_version("Gtk","3.0")
from gi.repository import Gtk

PEOPLE =    [
            "Frank",
            "Martha",
            "Jim Bob",
            "Francis"
            ]

class TreeCombo(object):
    def __init__(self):
        self.win = Gtk.Window(title="Combo with liststore")
        self.win.connect('delete-event', Gtk.main_quit)

        self.store = Gtk.ListStore(str)
        for person in PEOPLE:
            self.store.append([person])

        # self.combo = Gtk.ComboBox.new_with_model(self.store)
        self.combo = Gtk.ComboBox()

        self.tree = Gtk.TreeView(self.store)
        self.selector = self.tree.get_selection()
        self.selector.set_mode(Gtk.SelectionMode.MULTIPLE)

        self.combo_cell_text = Gtk.CellRendererText()

        self.column_text = Gtk.TreeViewColumn("Text", self.combo_cell_text, text=0)

        self.tree.append_column(self.column_text)

        self.combo.add(self.tree)

        self.win.add(self.combo)

        self.win.show_all()

def main():
    prog = TreeCombo()
    Gtk.main()

if __name__ == "__main__":
    main()