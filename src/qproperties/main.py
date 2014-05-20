#!/usr/bin/python

import qproperties_ui
from PyQt4 import QtCore, QtGui
import sys, os, pwd, grp, stat

# prepare for lift-off
app = QtGui.QApplication(sys.argv)
Dialog = QtGui.QDialog()
ui = qproperties_ui.Ui_Dialog()
ui.setupUi(Dialog)

sfile = QtCore.QDir.currentPath()
for arg in sys.argv:
    if os.path.exists(arg):
         sfile = arg

info = QtCore.QFileInfo(sfile)
date = QtCore.QDateTime()

# FIXME: disable those who can not be set
for group in grp.getgrall():
    ui.groupBox.addItem(group.gr_name)

for user in pwd.getpwall():
    ui.ownerBox.addItem(user.pw_name)

group = ui.groupBox.findText(info.group())
ui.groupBox.setCurrentIndex(group)

owner = ui.ownerBox.findText(info.owner())
ui.ownerBox.setCurrentIndex(owner)

executable = ui.executableBox.findText(str(info.isExecutable()))
ui.executableBox.setCurrentIndex(executable)

ui.lastModifiedLabel.setText(QtCore.QDateTime.toString(info.lastModified()))
ui.lastReadLabel.setText(QtCore.QDateTime.toString(info.lastRead()))
ui.filePathLabel.setText(sfile)

def set_permissions(slist):
    new_group = str(ui.groupBox.currentText())
    new_owner = str(ui.ownerBox.currentText())
    new_executable = bool(ui.executableBox.currentText())
    print('Saving permissions', new_group, new_owner, new_executable)
    try:
        for sfile in slist:
            if not owner == new_owner or not group == new_group:
                os.chown(sfile, pwd.getpwnam(new_owner).pw_uid, grp.getgrnam(new_group).gr_gid)
            print executable, new_executable
            if executable == 0 and new_executable:
                st = os.stat(sfile)
                os.chmod(sfile, st.st_mode | stat.S_IEXEC)
            elif executable == 1 and not new_executable:
                st = os.stat(sfile)
                os.chmod(sfile, st.st_mode | -stat.S_IEXEC)
            sys.exit()
    except OSError as detail:
        QtGui.QMessageBox.critical(Dialog, 'Properties',str(detail))

def save_permissions(): 
    if ui.recursiveBox.currentText() == 'True':
        import libmisc
        slist = [sfile]
        slist.extend(libmisc.Misc().list_all(sfile))
        print('Recursive permssions change of', slist)
        set_permissions(slist)
    else:
        print('Permssions change of', sfile)
        set_permissions([sfile])

ui.okButton.clicked.connect(save_permissions)
ui.cancelButton.clicked.connect(sys.exit)

# run!
Dialog.show()
sys.exit(app.exec_())
