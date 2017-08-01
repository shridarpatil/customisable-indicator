"""Dialog."""

import json
from gi.repository import Gtk


class Dialog(Gtk.Dialog):
    """Dialog."""

    def __init__(self, parent):
        """Init."""
        Gtk.Dialog.__init__(self, "My Dialog", parent, 0,
            (
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OK, Gtk.ResponseType.OK
            )
        )

        self.set_default_size(150, 100)

        label = Gtk.Label("This is a dialog to display additional information")

        box = self.get_content_area()
        box.add(label)
        self.show_all()


class DialogWindow(Gtk.Window):
    """Dialog window."""

    def __init__(self):
        """Init"""
        Gtk.Window.__init__(self, title="Button Demo")
        self.set_border_width(10)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        self.menu_name = Gtk.Entry()
        self.menu_name.set_text("Enter Menu Name")
        vbox.pack_start(self.menu_name, True, True, 0)

        self.command = Gtk.Entry()
        self.command.set_text("Enter Command")
        vbox.pack_start(self.command, True, True, 0)

        hbox = Gtk.Box(spacing=6)
        vbox.pack_start(hbox, True, True, 0)

        self.button = Gtk.Button.new_with_label("Save")
        self.button.connect("clicked", self.save)
        hbox.pack_start(self.button, True, True, 0)

        self.button = Gtk.Button.new_with_mnemonic("Cancel")
        self.button.connect("clicked", self.cancel)
        hbox.pack_start(self.button, True, True, 0)

    def save(self, widget):
        """-."""
        dialog = Dialog(self)
        response = dialog.run()

        menu = self.menu_name.get_text()
        command = self.command.get_text()

        if response == Gtk.ResponseType.OK:
            print("The OK button was clicked")
            self.create_config(menu, command)
        elif response == Gtk.ResponseType.CANCEL:
            print("The Cancel button was clicked")

        dialog.destroy()

    def cancel(self, widget):
        """Cancel."""
        pass

    def create_config(self, menu, command):
        """Create config."""
        json_data = {"menu": menu, "command": command}

        try:
            with open('data', 'a+') as outfile:
                data = json.load(outfile)
        except ValueError as e:
            print(e)
            data = []
            pass
        data.append(json_data)
        with open('data', 'a+') as outfile:
            json.dump(
                data, outfile, sort_keys=True,
                indent=4, ensure_ascii=False
            )
