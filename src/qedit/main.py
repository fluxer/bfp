#!/usr/bin/python

import qedit_ui
from PyQt4 import QtCore, QtGui
import sys, os
import libmisc
misc = libmisc.Misc()
import libqdesktop

# prepare for lift-off
app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()
ui = qedit_ui.Ui_MainWindow()
ui.setupUi(MainWindow)

# some variables
model = QtGui.QFileSystemModel()
actions = libqdesktop.Actions(MainWindow, app)
config = libqdesktop.Config()
icon = QtGui.QIcon()

def setLook():
    config.read()
    ssheet = '/etc/qdesktop/styles/' + config.GENERAL_STYLESHEET + '/style.qss'
    if config.GENERAL_STYLESHEET and os.path.isfile(ssheet):
        app.setStyleSheet(misc.file_read(ssheet))
    else:
        app.setStyleSheet('')
    icon.setThemeName(config.GENERAL_ICONTHEME)
setLook()

def disable_actions():
    ui.actionRevert.setEnabled(False)

sedit = None
for arg in sys.argv:
    if os.path.isfile(arg):
        sedit = arg

def run_about():
    QtGui.QMessageBox.about(MainWindow, "About", '<b>QEdit v1.0.0</b> by SmiL3y - xakepa10@gmail.com - under GPLv2')

def new_file():
    sfile = actions.new_file()
    if sfile:
        open_file(sfile)

def open_file(sfile):
    global sedit
    if not sfile:
        sfile = QtGui.QFileDialog.getOpenFileName(MainWindow, "Open",
            os.curdir,
            "All Files (*);;Text Files (*.txt)")
        if sfile:
            sfile = str(sfile)
            ui.textEdit.setText(misc.file_read(sfile))
    elif os.path.isfile(sfile):
        ui.textEdit.setText(misc.file_read(sfile))
    sedit = sfile

def save_file():
    if sedit:
        misc.file_write(os.path.realpath(sedit), ui.textEdit.toPlainText())

def save_as_file():
    global sedit
    sfile = QtGui.QFileDialog.getSaveFileName(MainWindow, "Save as",
                os.curdir,
                "All Files (*);;Text Files (*.txt)")
    if sfile:
        sedit = str(sfile)
        save_file()

def set_font():
    font, ok = QtGui.QFontDialog.getFont(QtGui.QFont(ui.textEdit.font))
    if ok:
       ui.textEdit.setFont(font)

def enable_actions():
    if True:
        pass
    else:
        disable_actions()

ui.actionQuit.triggered.connect(sys.exit)
ui.actionAbout.triggered.connect(run_about)
ui.actionOpen.triggered.connect(open_file)
ui.actionNew.triggered.connect(new_file)
ui.actionSave.triggered.connect(save_file)
ui.actionSaveAs.triggered.connect(save_as_file)
ui.actionFont.triggered.connect(set_font)

open_file(sedit)

# run!
MainWindow.show()
sys.exit(app.exec_())
