#!/bin/python2

import qpanel_ui
from PyQt4 import QtCore, QtGui
import sys, os
import libmisc
misc = libmisc.Misc()
import libqdesktop

# prepare for lift-off
app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()
ui = qpanel_ui.Ui_MainWindow()
ui.setupUi(MainWindow)

config = libqdesktop.Config()
general = libqdesktop.General()
icon = QtGui.QIcon()

def run_preferences():
    p = QtCore.QProcess()
    p.setWorkingDirectory(QtCore.QDir.homePath())
    p.startDetached('qsettings')
    p.close()

def setLook():
    config.read()
    ssheet = '/etc/qdesktop/styles/' + config.GENERAL_STYLESHEET + '/style.qss'
    if config.GENERAL_STYLESHEET and os.path.isfile(ssheet):
        app.setStyleSheet(misc.file_read(ssheet))
    else:
        app.setStyleSheet('')
    icon.setThemeName(config.GENERAL_ICONTHEME)
setLook()

def show_popup():
    ui.menuActions.popup(QtGui.QCursor.pos())

def do_shutdown():
    general.system_shutdown(MainWindow)

def do_reboot():
    general.system_reboot(MainWindow)

ui.actionPreferences.triggered.connect(run_preferences)
ui.actionShutdown.triggered.connect(do_shutdown)
ui.actionReboot.triggered.connect(do_reboot)
ui.actionLogout.triggered.connect(sys.exit)

ui.menubar.hide()
ui.MenuButton.clicked.connect(show_popup)

# create dynamic menu
menu = libqdesktop.Menu(app, ui.menuApplications)
menu.build()

# setup window
desktop = QtGui.QDesktopWidget()
MainWindow.resize(desktop.width(), 50)
MainWindow.move(0, desktop.rect().bottom() - 50)
MainWindow.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool)

# run!
MainWindow.show()
sys.exit(app.exec_())

