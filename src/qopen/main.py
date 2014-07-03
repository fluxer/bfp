#!/bin/python2

import qopen_ui
from PyQt4 import QtCore, QtGui
import sys, os, libmisc, libdesktop

# prepare for lift-off
app = QtGui.QApplication(sys.argv)
Dialog = QtGui.QDialog()
ui = qopen_ui.Ui_Dialog()
ui.setupUi(Dialog)
config = libdesktop.Config()
menu = libdesktop.Menu(app, None)
general = libdesktop.General()
misc = libmisc.Misc()
icon = QtGui.QIcon()

def setLook():
    general.set_style(app)
    icon.setThemeName(config.GENERAL_ICONTHEME)
setLook()

def open_file():
    for dfile in misc.list_files(sys.prefix + '/share/applications'):
        if str(ui.programBox.currentText()) == os.path.basename(dfile).replace('.desktop', ''):
            menu.execute_desktop(dfile, sfile)
            sys.exit(0)

for dfile in misc.list_files(sys.prefix + '/share/applications'):
    ui.programBox.addItem(os.path.basename(dfile).replace('.desktop', ''))

ui.okButton.clicked.connect(open_file)
ui.cancelButton.clicked.connect(sys.exit)

sfile = str(QtCore.QDir.currentPath())
for arg in sys.argv[1:]:
    if os.path.exists(arg):
        sfile = arg

# run!
Dialog.show()
sys.exit(app.exec_())
