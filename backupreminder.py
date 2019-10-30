#!/usr/bin/python3

# Backup reminder
# Copyright 2019 David Purton
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkX11

import threading
import subprocess

class BackupWindow(Gtk.Window):
    
    def __init__(self):
        Gtk.Window.__init__(self, title = "Backup reminder")
        
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_border_width(20)
        
        vbox = Gtk.VBox(spacing = 40)
        
        hbox = Gtk.HBox(spacing = 20)
        icon = Gtk.Image()
        icon.set_from_icon_name("dialog-question-symbolic", Gtk.IconSize.DIALOG)
        hbox.pack_start(icon, False, False, 0)
        self.label = Gtk.Label(label = "<b>Backup reminder</b>\n\nIt's time to run a backup! Would you like to do this now?")
        self.label.set_xalign(0)
        self.label.set_use_markup(True)
        hbox.pack_start(self.label, False, False, 0)
        vbox.pack_start(hbox, False, False, 0)
        hbox.show_all()
        
        hbox = Gtk.HBox(spacing = 10)
        self.shutdown_button = Gtk.CheckButton.new_with_label("Shutdown after backup completes.");
        hbox.pack_start(self.shutdown_button, False, False, 0)
        self.shutdown_button.show()
        self.ok_button = Gtk.Button.new_with_label("OK")
        self.ok_button.set_property("width-request", 90)
        self.ok_button.connect("clicked", self.on_ok_clicked)
        hbox.pack_end(self.ok_button, False, False, 0)
        self.ok_button.show()
        self.cancel_button = Gtk.Button.new_with_label("Cancel")
        self.cancel_button.set_property("width-request", 90)
        self.cancel_button.connect("clicked", self.on_cancel_clicked)
        hbox.pack_end(self.cancel_button, False, False, 0)
        self.cancel_button.show()
        self.close_button = Gtk.Button.new_with_label("Close")
        self.close_button.set_property("width-request", 90)
        self.close_button.connect("clicked", self.on_cancel_clicked)
        hbox.pack_end(self.close_button, False, False, 0)
        vbox.pack_end(hbox, False, False, 0)
        hbox.show()
        self.ok_button.grab_focus()
        
        self.add(vbox)
        vbox.show()
        
        self.connect("key-press-event",self.on_key_press_event)        
        
        self.show()
        self.window_id = self.get_property('window').get_xid()
        
        window_size = self.get_preferred_size()
        self.set_size_request(window_size.natural_size.width, -1)
        
        self.connect("delete-event", self.on_delete)
        self.connect("destroy", Gtk.main_quit)
    
    def on_delete(self, event, data):
        if self.ok_to_quit():
            return False
        else:
            return True
    
    def on_ok_clicked(self, button):
        self.run_backup()
    
    def on_cancel_clicked(self, button):
        if self.ok_to_quit():
            Gtk.main_quit()
    
    def on_key_press_event(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            if self.ok_to_quit():
                Gtk.main_quit()
    
    def run_backup(self):
        def run_backup_thread():
            self.backup_proc = subprocess.Popen(["/usr/bin/duply", "binky", "backup"],
                                                stdout = subprocess.DEVNULL)
            returncode = self.backup_proc.wait()
            self.backup_finished(returncode)
        subprocess.run(["/usr/bin/xdg-screensaver", "suspend", str(self.window_id)])
        self.backup_thread = threading.Thread(target=run_backup_thread)
        self.backup_thread.start()
        self.ok_button.hide()
        self.cancel_button.grab_focus()
        self.label.set_label("<b>Backup reminder</b>\n\nBackup running...")
    
    def backup_finished(self, backup_returncode):
        self.close_button.show()
        self.cancel_button.hide()
        self.close_button.grab_focus()
        subprocess.run(["/usr/bin/xdg-screensaver", "resume", str(self.window_id)])
        if backup_returncode != 0:
            self.label.set_label("<b>Warning</b>\n\nBackup did <b>not</b> finish successfully.")
            print("Warning: Binky backup did *not* finish successfully.")
        else:
            self.label.set_label("<b>Backup reminder</b>\n\nBackup finished successfully.")
            self.set_urgency_hint(True)
            if self.shutdown_button.get_active():
                subprocess.run(["/usr/bin/systemctl", "poweroff"])
    
    def backup_running(self):
        if hasattr(self, 'backup_thread'):
            return self.backup_thread.is_alive()
        else:
            return False
    
    def backup_terminate(self):
        if self.backup_running():
            self.backup_proc.terminate()

    def ok_to_quit(self):
        if self.backup_running():
            quitdialog = QuitDialog(self)
            response = quitdialog.run()
            quitdialog.destroy()
            if response == Gtk.ResponseType.OK:
                self.backup_terminate()
                return True
            else:
                return False
        else:
            return True

class  QuitDialog(Gtk.Dialog):
    
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Cancel backup?", parent,
                            modal = True, destroy_with_parent = True)
        self.set_skip_taskbar_hint(True)
        self.set_resizable(False)
        self.set_role("pop-up")
        self.set_transient_for(parent)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.set_border_width(20)
        label = Gtk.Label(label = "Are you sure you want to cancel the backup?")
        self.vbox.set_spacing(40)
        self.add_buttons("Cancel", Gtk.ResponseType.CANCEL, "OK", Gtk.ResponseType.OK)
        box = self.get_content_area()
        box.add(label)
        self.show_all()

if __name__ == "__main__":
    backupwin = BackupWindow()
    Gtk.main()
