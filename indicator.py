#!/bin/env python
# -*- coding: utf-8 -*-
"""Indicator."""
# This code is an example for a tutorial on Ubuntu Unity/Gnome AppIndicators:
# http://candidtim.github.io/appindicator/2014/09/13/ubuntu-appindicator-step-by-step.html

import os
import subprocess
import signal
import json
import gi
import time

from threading import Thread

from urllib2 import Request, urlopen

gi.require_version("Gtk", "3.0")
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')

from utilities.dialog import DialogWindow

from gi.repository import Gtk
from gi.repository import AppIndicator3
from gi.repository import GObject
from gi.repository import Notify


APPINDICATOR_ID = 'myappindicator'

global indicator
global menu
global item_download


def main():
    """Main."""
    global indicator
    indicator = AppIndicator3.Indicator.new(
        APPINDICATOR_ID,
        '/home/shri/Documents/My/python/kivy/indicator/icons/Git_icon.svg.png',
        AppIndicator3.IndicatorCategory.SYSTEM_SERVICES
    )
    indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
    indicator.set_menu(build_menu())
    update = Thread(target=net_speed)
    # daemonize the thread to make the indicator stopable
    update.setDaemon(True)
    update.start()
    Notify.init(APPINDICATOR_ID)
    GObject.threads_init()
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    Gtk.main()


def build_menu(downloads=None):
    """Build menu"""
    global menu
    global item_download

    menu = Gtk.Menu()
    item_joke = Gtk.MenuItem('Joke')
    item_joke.connect('activate', joke)
    menu.append(item_joke)

    bench = Gtk.MenuItem('Create Menu')
    bench.connect('activate', bench_start)
    menu.append(bench)

    item_download = Gtk.MenuItem("downloads")
    item_download.connect('activate', joke)
    menu.append(item_download)
    item_download.show()

    try:

        with open('data') as outfile:
                menu_items = json.load(outfile)

    except ValueError as e:
        print(e)
        pass
    else:
        for menu_item in menu_items:
            item_download = Gtk.MenuItem(menu_item['menu'])
            item_download.connect('activate', create_command)
            menu.append(item_download)
            item_download.show()

    menu_sep = Gtk.SeparatorMenuItem()
    menu.append(menu_sep)

    item_quit = Gtk.MenuItem('Quit')
    item_quit.connect('activate', quit)
    menu.append(item_quit)

    # img = Gtk.Image()
    # img.set_from_file('/home/shri/Documents/My/python/kivy/indicator/icons/Git_icon.svg.png')
    # new = Gtk.ImageMenuItem(Gtk.STOCK_NEW, 'New')
    # new.set_image(img)
    # new.set_always_show_image(True)
    # menu.append(new)
    menu.show_all()
    return menu


def create_command(_):
    """Create command."""
    lable = _.get_label()
    with open('data') as outfile:
        menu_items = json.load(outfile)

    for menu_item in menu_items:
        if lable == menu_item['menu']:
            print menu_item['command']
            command = """gnome-terminal -e 'bash -c
                   \"{};  bash\" '""".format(menu_item['command'])
            status = os.system(command)
            if status == 0:
                title = "<b>{}</b>".format(lable)
                message = "Command {} executed.".format(menu_item['command'])
                Notify.Notification.new(
                    title,
                    message,
                    icon=os.path.abspath('icons/frappe.png')
                ).show()
            break


def fetch_joke():
    """Fetch jokes"""
    request = Request('http://api.icndb.com/jokes/random?limitTo=[nerdy]')
    response = urlopen(request)
    joke = json.loads(response.read())['value']['joke']
    return joke


def joke(_):
    """Notify joke."""
    Notify.Notification.new("<b>Joke</b>", fetch_joke(), None).show()


def bench_start(_):
    """Start frappe bench."""
    win = DialogWindow()
    win.show_all()
    print _.get_label()

    # status = os.system("""gnome-terminal -e 'bash -c
    #        \"cd /home/shri/frappe-bench && bench start;  bash\" '""")
    # if status == 0:
    #     Notify.Notification.new(
    #         "<b>Frappe</b>",
    #         "Frappe Started",
    #         icon='/home/shri/Documents/My/python/kivy/indicator/icons/frappe.png'
    #     ).show()


def net_speed():
    """Net speed."""
    global indicator
    global item_download

    while True:
        try:
            net_type = shell_command("route -n | awk 'FNR == 3 {print $8}'")

            rx_bytes_command = "cat /sys/class/net/{}/statistics/rx_bytes".format(
                net_type
            )

            tx_bytes_command = "cat /sys/class/net/{}/statistics/tx_bytes".format(
                net_type
            )

            rx_bytes_1 = int(shell_command(rx_bytes_command))
            tx_bytes_1 = int(shell_command(tx_bytes_command))

            time.sleep(1)

            rx_bytes_2 = int(shell_command(rx_bytes_command))
            tx_bytes_2 = int(shell_command(tx_bytes_command))

            upload_bytes = tx_bytes_2 - tx_bytes_1

            if upload_bytes < 1024:
                uploads = "{}bytes/s".format(upload_bytes)

            if upload_bytes >= 1024:
                upload_bytes = upload_bytes // 1024
                uploads = "{}KiB/s".format(upload_bytes)

            if upload_bytes >= 1024:
                upload_bytes = upload_bytes // 1024
                uploads = "{}mb/s".format(upload_bytes // 1024)

            download_bytes = rx_bytes_2 - rx_bytes_1

            if download_bytes < 1024:
                downloads = "{}bytes/s".format(download_bytes)

            if download_bytes >= 1024:
                download_bytes = download_bytes // 1024
                downloads = "{}KiB/s".format(download_bytes)

            if download_bytes >= 1024:
                download_bytes = download_bytes // 1024
                downloads = "{}mb/s".format(download_bytes // 1024)

            message = "dl: {}".format(downloads)

            GObject.idle_add(
                indicator.set_label,
                message, APPINDICATOR_ID,
                priority=GObject.PRIORITY_DEFAULT
            )

            # item_download = Gtk.MenuItem(downloads)
            # item_download.connect('activate', quit)
            # menu.append(item_download)
            item_download.get_child().set_text("up: {0}".format(uploads))
            item_download.show()
        except ValueError as e:
            print e
            time.sleep(2)
            message = "up: {0}kbps".format(0)
            GObject.idle_add(
                indicator.set_label,
                message, APPINDICATOR_ID,
                priority=GObject.PRIORITY_DEFAULT
            )
            set_icon(0, 0)
        else:
            set_icon(upload_bytes, download_bytes)


def set_icon(upload, download):
    """Set icon."""
    global indicator

    if upload == 0 and download == 0:
        icon = os.path.abspath('icons/gnome-netstatus-idle.svg')
    elif upload == 0:
        icon = os.path.abspath('icons/gnome-netstatus-rx.svg')
    elif download == 0:
        icon = os.path.abspath('icons/gnome-netstatus-tx.svg')
    else:
        icon = os.path.abspath('icons/gnome-netstatus-rx-tx.svg')

    indicator.set_icon_full(icon, "")


def shell_command(cmd):
    """Run shell command."""
    try:

        response = subprocess.Popen(
            cmd,
            shell=True, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        ).stdout.read()
    except ValueError as e:
        raise e

    return response.rstrip('\n')


def quit(_):
    """Quit."""
    Notify.uninit()
    Gtk.main_quit()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    main()
