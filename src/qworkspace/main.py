#!/bin/python2

import qworkspace_ui
from PyQt4 import QtCore, QtGui
import sys, gc, libworkspace, libmisc

app_version = "0.9.17 (ac172da)"
app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()
ui = qworkspace_ui.Ui_MainWindow()
ui.setupUi(MainWindow)
settings = libworkspace.Settings()
general = libworkspace.General()
misc = libmisc.Misc()
ui.plugins = libworkspace.Plugins(ui)

def setLook():
    general.set_style(app)
setLook()

def setTranslator():
    locale = QtCore.QLocale.system().name()
    translator = QtCore.QTranslator()
    if translator.load('qt_' + locale, QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.TranslationsPath)):
        app.installTranslator(translator)
setTranslator()

for plugin in ui.plugins.plugins_all:
    ui.plugins.plugin_load(plugin)
ui.plugins.recent_restore()

def tab_close(index):
    widget = ui.tabWidget.widget(index)
    if ui.tabWidget.tabText(index) == 'Welcome':
        widget.layout().deleteLater()
        ui.tabWidget.removeTab(index)
        return
    ui.plugins.plugin_close(widget.name)
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

for plugin in reversed(ui.plugins.plugins_all):
    ui.plugins.plugin_unload(plugin)

sys.exit(r)
