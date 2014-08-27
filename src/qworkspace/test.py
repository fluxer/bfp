#!/bin/python2

import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

import qworkspace_ui
from PyQt4 import QtCore, QtGui
import sys, os, gc, libworkspace, libmisc

# prepare for lift-off
app_version = "0.9.34 (987cd95)"
app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()
ui = qworkspace_ui.Ui_MainWindow()
ui.setupUi(MainWindow)
general = libworkspace.General()
misc = libmisc.Misc()
ui.app = app
ui.plugins = libworkspace.Plugins(ui)
ui.window = MainWindow

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

# unload all plugins
for plugin in reversed(ui.plugins.plugins_all):
    ui.plugins.plugin_unload(plugin)
