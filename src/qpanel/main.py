#!/bin/python2

import qpanel_ui
from PyQt4 import QtCore, QtGui
import sys, libmisc, libdesktop

# prepare for lift-off
app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()
ui = qpanel_ui.Ui_MainWindow()
ui.setupUi(MainWindow)
config = libdesktop.Config()
general = libdesktop.General()
misc = libmisc.Misc()

def setLook():
    general.set_style(app)
setLook()

def show_popup():
    ui.menuActions.popup(QtGui.QCursor.pos())

def run_preferences():
    general.execute_program('qsettings')

def do_suspend():
    general.system_suspend(MainWindow)

def do_shutdown():
    general.system_shutdown(MainWindow)

def do_reboot():
    general.system_reboot(MainWindow)

ui.actionPreferences.triggered.connect(run_preferences)
ui.actionSuspend.triggered.connect(do_suspend)
ui.actionShutdown.triggered.connect(do_shutdown)
ui.actionReboot.triggered.connect(do_reboot)
ui.actionLogout.triggered.connect(sys.exit)

ui.menubar.hide()
ui.MenuButton.clicked.connect(show_popup)

# create dynamic menu
menu = libdesktop.Menu(app, ui.menuApplications)
menu.build()

# setup window
desktop = QtGui.QDesktopWidget()
MainWindow.resize(desktop.width(), 50)
MainWindow.move(0, desktop.rect().bottom() - 50)
MainWindow.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool)

# watch configs for changes
def reload_panel():
    global config, general
    reload(libdesktop)
    config = libdesktop.Config()
    general = libdesktop.General()
    menu.build()
    setLook()

watcher1 = QtCore.QFileSystemWatcher()
watcher1.addPath(config.settings.fileName())
watcher1.fileChanged.connect(reload_panel)

watcher2 = QtCore.QFileSystemWatcher()
watcher2.addPath(sys.prefix + '/share/applications')
watcher2.directoryChanged.connect(menu.build)

# run!
MainWindow.show()
sys.exit(app.exec_())

