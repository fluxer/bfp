#!/bin/python2

import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

import qworkspace_ui
from PyQt4 import QtCore, QtGui
import sys, os, gc, libworkspace, libmisc

# prepare for lift-off
app_version = "0.9.35 (9efc4b1)"
app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()
ui = qworkspace_ui.Ui_MainWindow()
ui.setupUi(MainWindow)
settings = libworkspace.Settings()
general = libworkspace.General()
misc = libmisc.Misc()
ui.app = app
ui.plugins = libworkspace.Plugins(ui)
ui.window = MainWindow

# setup look of application
def setLook():
    general.set_style(app)
setLook()

# setup fixed window size
desktop = app.desktop()
def setSize():
    MainWindow.setFixedSize(desktop.screenGeometry().size())
setSize()
desktop.resized.connect(setSize)

# setup translator
def setTranslator():
    locale = QtCore.QLocale.system().name()
    translator = QtCore.QTranslator()
    tr_path = QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.TranslationsPath)
    if translator.load('qworkspace_' + locale, tr_path):
        app.installTranslator(translator)
setTranslator()

# load all plugins
for plugin in ui.plugins.plugins_all:
    ui.plugins.plugin_load(plugin)
ui.plugins.recent_restore()

def tab_close(index):
    widget = ui.tabWidget.widget(index)
    if ui.tabWidget.tabText(index) == 'Welcome':
        widget.layout().deleteLater()
        ui.tabWidget.removeTab(index)
        return
    ui.plugins.plugin_close(widget.name, index)
    gc.collect()
ui.tabWidget.tabCloseRequested.connect(tab_close)

# watch configs for changes
if os.path.isfile(settings.settings.fileName()):
    watcher = QtCore.QFileSystemWatcher()
    watcher.addPath(settings.settings.fileName())
    watcher.fileChanged.connect(setLook)

# show window and run application
MainWindow.showMaximized()
r = app.exec_()

# unload all plugins
for plugin in reversed(ui.plugins.plugins_all):
    ui.plugins.plugin_unload(plugin)

sys.exit(r)
