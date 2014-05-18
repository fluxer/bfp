#!/usr/bin/python

import libqproperties
from PyQt4 import QtCore, QtGui
import sys, os, pwd, grp

# prepare for lift-off
app = QtGui.QApplication(sys.argv)
Dialog = QtGui.QDialog()
ui = libqproperties.Ui_Dialog()
ui.setupUi(Dialog)

sfile = QtCore.QDir.currentPath()
for arg in sys.argv:
    if os.path.exists(arg):
         sfile = arg

info = QtCore.QFileInfo(sfile)
date = QtCore.QDateTime()

for group in grp.getgrall():
    ui.groupBox.addItem(group.gr_name)

for user in pwd.getpwall():
    ui.ownerBox.addItem(user.pw_name)

index = ui.groupBox.findText(info.group())
ui.groupBox.setCurrentIndex(index)

index = ui.ownerBox.findText(info.owner())
ui.ownerBox.setCurrentIndex(index)

index = ui.executableBox.findText(str(info.isExecutable()))
ui.executableBox.setCurrentIndex(index)

ui.lastModifiedLabel.setText(QtCore.QDateTime.toString(info.lastModified()))
ui.lastReadLabel.setText(QtCore.QDateTime.toString(info.lastRead()))
ui.filePathLabel.setText(sfile)

# run!
Dialog.show()
sys.exit(app.exec_())
