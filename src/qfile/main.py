#!/usr/bin/python

import qfile
from PyQt4 import QtCore, QtGui
import sys, os, shutil
import libmisc
misc = libmisc.Misc()

# prepare for lift-off
app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()
ui = qfile.Ui_MainWindow()
ui.setupUi(MainWindow)

model = QtGui.QFileSystemModel()
# model.setSorted(True)
cut_dirs = None
copy_dirs = []
delete_dirs = []


def disable_actions():
    ui.actionRename.setEnabled(False)
    ui.actionCut.setEnabled(False)
    ui.actionCopy.setEnabled(False)
    ui.actionDelete.setEnabled(False)
    ui.actionProperties.setEnabled(False)

def change_directory(path=ui.ViewWidget.currentIndex()):
    if not isinstance(path, QtCore.QString):
        path = model.filePath(path)
    if not os.path.isdir(path):
        # FIXME: meta function with file and dir handlers
        os.system('qedit ' + str(path))
        return
    root = model.setRootPath(path)
    ui.ViewWidget.setRootIndex(root)
    # ui.ViewWidget.sortItems()
    ui.AddressBar.setText(os.path.normpath(str(path)))
    disable_actions()

ui.ViewWidget.setModel(model)
change_directory(QtCore.QDir.currentPath())

q = QtGui.QFileIconProvider()
model.setIconProvider(q)

#Layout = QtGui.QVBoxLayout(ui.ViewWidget)
#Layout.addWidget(ui.ViewWidget)
#ui.setLayout(Layout)

def run_terminal():
    os.system('xterm')

def run_about():
    QtGui.QMessageBox.about(MainWindow, "About", '<b>QFile v1.0.0</b> by SmiL3y - xakepa10@gmail.com - under GPLv2')

def change_view_icons():
    ui.ViewWidget.setViewMode(ui.ViewWidget.IconMode)

def change_view_list():
    ui.ViewWidget.setViewMode(ui.ViewWidget.ListMode)

def change_home():
    change_directory(QtCore.QDir.homePath())

def change_back_directory():
    change_directory(model.rootPath() + '/..')

def change_mount_drectory():
    change_directory(ui.MountsWidget.indexFromItem()) 
    change_directory(ui.MountsWidget.currentIndex()) 
    change_directory(ui.MountsWidget.currentItem())

def rename_directory():
    for svar in ui.ViewWidget.selectedIndexes():
        svar = str(model.filePath(svar))
        svar_basename = os.path.basename(svar)
        svar_dirname = os.path.dirname(svar)

        svar_new, ok = QtGui.QInputDialog.getText(MainWindow, "File Manager",
                "New name:", QtGui.QLineEdit.Normal, svar_basename)
        if ok and svar_new != '':
            pass
        else:
            return

        new_name = os.path.join(svar_dirname,str(svar_new))
        print('Renaming: ', svar, ' To: ', new_name)
        os.rename(svar, new_name)

def cut_directory():
    global cut_dirs
    global copy_dirs
    cut_dirs = []
    for sdir in ui.ViewWidget.selectedIndexes():
        cut_dirs.append(model.filePath(sdir))
    copy_dirs = []
    ui.actionPaste.setEnabled(True)

def copy_directory():
    global cut_dirs
    global copy_dirs
    cut_dirs = []
    copy_dirs = []
    for sdir in ui.ViewWidget.selectedIndexes():
        copy_dirs.append(model.filePath(sdir))
    ui.actionPaste.setEnabled(True)

def paste_directory():
    cur_dir = str(model.filePath(ui.ViewWidget.rootIndex()))
    if cut_dirs:
        for svar in cut_dirs:
            svar = str(svar)
            print('Moving: ', svar, ' To: ', cur_dir)
            shutil.copy2(svar, cur_dir)
            if os.path.isdir(svar):
                misc.dir_remove(svar)
            else:
                os.unlink(svar)
    elif copy_dirs:
        for svar in copy_dirs:
            svar = str(svar)
            print('Copying: ', svar, ' To: ', cur_dir)
            shutil.copy2(svar, cur_dir)
    ui.actionPaste.setEnabled(False)

def delete_directory():
        for svar in ui.ViewWidget.selectedIndexes():
            svar = str(model.filePath(svar))
            reply = QtGui.QMessageBox.question(MainWindow, "File Manager ",
                "Are you sure you want to delete <b>" + svar + "</b>? ", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel)
            if reply == QtGui.QMessageBox.Yes:
                pass
            elif reply == QtGui.QMessageBox.No:
                continue
            else:
                return

            print('Removing: ', svar)
            if os.path.isdir(svar):
                misc.dir_remove(svar)
            else:
                os.unlink(svar)

def enable_actions():
    selected_items = []
    for sdir in ui.ViewWidget.selectedIndexes():
        selected_items.append(model.filePath(sdir))
    if selected_items:
        ui.actionRename.setEnabled(True)
        ui.actionCut.setEnabled(True)
        ui.actionCopy.setEnabled(True)
        ui.actionDelete.setEnabled(True)
        ui.actionProperties.setEnabled(True)
    else:
        disable_actions()

ui.actionQuit.triggered.connect(sys.exit)
ui.actionTerminal.triggered.connect(run_terminal)
ui.actionAbout.triggered.connect(run_about)
ui.actionIcons.triggered.connect(change_view_icons)
ui.actionList.triggered.connect(change_view_list)
ui.actionRename.triggered.connect(rename_directory)
ui.actionCut.triggered.connect(cut_directory)
ui.actionCopy.triggered.connect(copy_directory)
ui.actionPaste.triggered.connect(paste_directory)
ui.actionDelete.triggered.connect(delete_directory)
ui.ViewWidget.doubleClicked.connect(change_directory)
ui.ViewWidget.clicked.connect(enable_actions)
ui.BackButton.clicked.connect(change_back_directory)
ui.HomeButton.clicked.connect(change_home)

ui.MountsWidget.clicked.connect(change_mount_drectory)


def show_popup():
    ui.menuActions.popup(QtGui.QCursor.pos())

ui.ViewWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
ui.ViewWidget.customContextMenuRequested.connect(enable_actions)
ui.ViewWidget.customContextMenuRequested.connect(show_popup)

# show mounted filesystems
s = QtGui.QStandardItemModel()
for device in misc.file_readlines('/proc/mounts'):
    if device.startswith('/'):
        s.appendRow(QtGui.QStandardItem(QtGui.QIcon('/usr/share/icons/elementary_usu/apps/48/ax-applet.svg'), device.split()[1]))
        ui.MountsWidget.setModel(s)
#ui.MountsWidget.sortItems()

# run!
MainWindow.show()
sys.exit(app.exec_())
