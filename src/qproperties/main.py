#!/bin/python2

import qproperties_ui
from PyQt4 import QtCore, QtGui
import sys, os, pwd, grp, stat, libmisc, libdesktop

# prepare for lift-off
sfile = str(QtCore.QDir.currentPath())
for arg in sys.argv:
    if os.path.exists(arg):
        sfile = arg

app = QtGui.QApplication(sys.argv)
Dialog = QtGui.QDialog()
ui = qproperties_ui.Ui_Dialog()
ui.setupUi(Dialog)
config = libdesktop.Config()
misc = libmisc.Misc()
mime = libdesktop.Mime()
general = libdesktop.General()
info = QtCore.QFileInfo(sfile)
date = QtCore.QDateTime()
icon = QtGui.QIcon()

def setLook():
    general.set_style(app)
    icon.setThemeName(config.GENERAL_ICONTHEME)
setLook()

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
smime = misc.file_mime(sfile)
ui.mimeLabel.setText(smime)
ui.programBox.addItems(mime.get_programs())
index = ui.programBox.findText(mime.get_program(smime))
ui.programBox.setCurrentIndex(index)

# avoid locking of the application on huge files/directories
class SizeThread(QtCore.QThread):
    ''' Size calculating thread '''
    def run(self):
        if os.path.isdir(sfile):
            size = str(misc.dir_size(sfile))
        else:
            size = str(os.path.getsize(sfile))
        units = 'b'
        lenght = len(size)
        if lenght > 12:
            units = 'Tb'
            size = size[:(lenght-12)]
        elif lenght > 9:
            units = 'Gb'
            size = size[:(lenght-9)]
        elif lenght > 6:
            units = 'Mb'
            size = size[:(lenght-6)]
        elif lenght > 3:
            units = 'Kb'
            size = size[:(lenght-3)]
        ui.totalSizeLabel.setText(size + ' ' + units)

t = SizeThread()
t.start()

def set_permissions(slist):
    new_group = str(ui.groupBox.currentText())
    new_owner = str(ui.ownerBox.currentText())
    new_executable = bool(ui.executableBox.currentText())
    try:
        for sfile in slist:
            if not owner == new_owner or not group == new_group:
                os.chown(sfile, pwd.getpwnam(new_owner).pw_uid, grp.getgrnam(new_group).gr_gid)
            if executable == 0 and new_executable:
                st = os.stat(sfile)
                os.chmod(sfile, st.st_mode | stat.S_IEXEC)
            elif executable == 1 and not new_executable:
                st = os.stat(sfile)
                os.chmod(sfile, st.st_mode | -stat.S_IEXEC)
    except OSError as detail:
        QtGui.QMessageBox.critical(Dialog, 'Critical', str(detail))

def save_properties():
    recursive = False

    # FIXME: directory symlink
    if os.path.isdir(sfile):
        reply = QtGui.QMessageBox.question(Dialog, 'Question', \
            'Do you want to set properties of <b>' + sfile + '</b> recursively?', \
            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            recursive = True

    if recursive:
        slist = [sfile]
        slist.extend(misc.list_all(sfile))
        set_permissions(slist)
    else:
        set_permissions([sfile])

    sprogram = str(ui.programBox.currentText())
    if not sprogram:
        mime.unregister(smime)
    else:
        mime.register(smime, sprogram)
    sys.exit()

ui.okButton.clicked.connect(save_properties)
ui.cancelButton.clicked.connect(sys.exit)

# run!
Dialog.show()
sys.exit(app.exec_())
