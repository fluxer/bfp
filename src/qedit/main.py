#!/bin/python2

import qedit_ui
from PyQt4 import QtCore, QtGui
import sys, os, libmisc, libdesktop, libhighlighter

# prepare for lift-off
app_version = "0.9.6 (e082da9)"
app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()
ui = qedit_ui.Ui_MainWindow()
ui.setupUi(MainWindow)
actions = libdesktop.Actions(MainWindow, app)
config = libdesktop.Config()
general = libdesktop.General()
misc = libmisc.Misc()
icon = QtGui.QIcon()

def setLook():
    general.set_style(app)
    icon.setThemeName(config.GENERAL_ICONTHEME)
setLook()

sedit = None
for arg in sys.argv[1:]:
    if os.path.isfile(arg):
        sedit = arg

def run_about():
    QtGui.QMessageBox.about(MainWindow, "About", '<b>QEdit v' + app_version + '</b> by SmiL3y - xakepa10@gmail.com - under GPLv2')

def new_file():
    sfile = actions.new_file()
    if sfile:
        open_file(sfile)

def open_file(sfile):
    global sedit
    if not sfile:
        sfile = QtGui.QFileDialog.getOpenFileName(MainWindow, "Open", \
            QtCore.QDir.currentPath(), "All Files (*);;Text Files (*.txt)")
        if sfile:
            sfile = str(sfile)
            ui.textEdit.setText(misc.file_read(sfile))
        else:
            # prevent sedit being set to None
            return
    elif os.path.isfile(sfile):
        ui.textEdit.setText(misc.file_read(sfile))
    sedit = sfile
    ui.actionReload.setEnabled(True)

def save_file():
    if sedit:
        misc.file_write(os.path.realpath(sedit), ui.textEdit.toPlainText())

def save_as_file():
    global sedit
    sfile = QtGui.QFileDialog.getSaveFileName(MainWindow, "Save as", \
        QtCore.QDir.currentPath(), "All Files (*);;Text Files (*.txt)")
    if sfile:
        sedit = str(sfile)
        save_file()

def find():
    svar, ok = QtGui.QInputDialog.getText(MainWindow, 'Find', '')
    if ok and svar:
        ui.textEdit.find(svar)

def reload_file():
    open_file(sedit)

def set_font():
    font, ok = QtGui.QFontDialog.getFont(QtGui.QFont(ui.textEdit.font))
    if ok:
        ui.textEdit.setFont(font)

def highlight_plain():
    try:
        ui.highlighter.setDocument(None)
    except AttributeError:
        pass

def highlight_python():
    ui.highlighter = libhighlighter.HighlighterPython(ui.textEdit.document())

def highlight_shell():
    ui.highlighter = libhighlighter.HighlighterShell(ui.textEdit.document())

def highlight_c():
    ui.highlighter = libhighlighter.HighlighterC(ui.textEdit.document())

ui.actionQuit.triggered.connect(sys.exit)
ui.actionAbout.triggered.connect(run_about)
ui.actionOpen.triggered.connect(open_file)
ui.actionNew.triggered.connect(new_file)
ui.actionSave.triggered.connect(save_file)
ui.actionSaveAs.triggered.connect(save_as_file)
ui.actionReload.triggered.connect(reload_file)
ui.actionFind.triggered.connect(find)
ui.actionUndo.triggered.connect(ui.textEdit.undo)
ui.actionRedo.triggered.connect(ui.textEdit.redo)
ui.actionFont.triggered.connect(set_font)
ui.actionPlain.triggered.connect(highlight_plain)
ui.actionPython.triggered.connect(highlight_python)
ui.actionShell.triggered.connect(highlight_shell)
ui.actionC.triggered.connect(highlight_c)

if sedit:
    open_file(sedit)

# watch configs for changes
def reload_edit():
    global config
    reload(libdesktop)
    config = libdesktop.Config()
    setLook()

watcher1 = QtCore.QFileSystemWatcher()
watcher1.addPath(config.settings.fileName())
watcher1.fileChanged.connect(reload_edit)

# run!
MainWindow.show()
sys.exit(app.exec_())
