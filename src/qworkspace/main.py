#!/bin/python2

import qworkspace_ui
from PyQt4 import QtCore, QtGui
import sys, os, gc, libworkspace, libmisc

# prepare for lift-off
app_version = "0.9.13 (bdb6060)"
app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()
ui = qworkspace_ui.Ui_MainWindow()
ui.setupUi(MainWindow)
settings = libworkspace.Settings()
general = libworkspace.General()
plugins = libworkspace.Plugins(ui)
misc = libmisc.Misc()

def setLook():
    general.set_style(app)
setLook()

try:
    for plugin in plugins.plugins_all:
        plugins.load(plugin)
finally:
    pass

def tab_close(index):
    widget = ui.tabWidget.widget(index)
    if ui.tabWidget.tabText(index) == 'Welcome':
        widget.layout().deleteLater()
        ui.tabWidget.removeTab(index)
        return
    plugins.close(widget.name)
    gc.collect()
ui.tabWidget.tabCloseRequested.connect(tab_close)

def reload_browser():
    global settings
    reload(libworkspace)
    settings = libworkspace.Settings()
    setLook()
watcher1 = QtCore.QFileSystemWatcher()
watcher1.addPath(settings.settings.fileName())
watcher1.fileChanged.connect(reload_browser)

MainWindow.showMaximized()
r = app.exec_()

try:
    for plugin in reversed(plugins.plugins_all):
        plugins.unload(plugin)
finally:
    pass

sys.exit(r)
