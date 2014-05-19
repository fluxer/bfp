#!/usr/bin/python

import libqfile
from PyQt4 import QtCore, QtGui
import sys, os, shutil
import libmisc
misc = libmisc.Misc()

# prepare for lift-off
app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()
ui = libqfile.Ui_MainWindow()
ui.setupUi(MainWindow)

model = QtGui.QFileSystemModel()
cut_dirs = None
copy_dirs = []
delete_dirs = []

def disable_actions():
    ui.actionOpen.setEnabled(False)
    ui.actionRename.setEnabled(False)
    ui.actionCut.setEnabled(False)
    ui.actionCopy.setEnabled(False)
    ui.actionDelete.setEnabled(False)
    ui.actionProperties.setEnabled(False)
    ui.actionDecompress.setEnabled(False)
    ui.actionCompressGzip.setEnabled(False)
    ui.actionCompressBzip2.setEnabled(False)

def open_file():
    for sfile in ui.ViewWidget.selectedIndexes():
        sfile = str(model.filePath(sfile))
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(sfile))

def change_directory(path=ui.ViewWidget.selectedIndexes()):
    if not isinstance(path, QtCore.QString) and not isinstance(path, str):
        path = model.filePath(path)
    if not os.path.isdir(path):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(path))
        return
    root = model.setRootPath(path)
    ui.ViewWidget.setRootIndex(root)
    # model.sortItems()
    ui.AddressBar.setText(str(path))
    disable_actions()

start_dir = QtCore.QDir.currentPath()
ui.ViewWidget.setModel(model)
for arg in sys.argv:
    if os.path.isdir(arg):
         start_dir = arg
change_directory(start_dir)

def run_terminal():
    p = QtCore.QProcess()
    p.setWorkingDirectory(model.rootPath())
    p.startDetached('xterm')

def run_about():
    QtGui.QMessageBox.about(MainWindow, "About", '<b>QFile v1.0.0</b> by SmiL3y - xakepa10@gmail.com - under GPLv2')

def change_view_icons():
    ui.ViewWidget.setViewMode(ui.ViewWidget.IconMode)

def change_view_list():
    ui.ViewWidget.setViewMode(ui.ViewWidget.ListMode)

def change_home():
    change_directory(QtCore.QDir.homePath())

def change_back_directory():
    change_directory(os.path.realpath(str(model.rootPath()) + '/..'))

def rename_directory():
    for svar in ui.ViewWidget.selectedIndexes():
        svar = str(model.filePath(svar))
        svar_basename = os.path.basename(svar)
        svar_dirname = os.path.dirname(svar)

        svar_new, ok = QtGui.QInputDialog.getText(MainWindow, "File Manager",
            "New name:", QtGui.QLineEdit.Normal, svar_basename)
        if ok and svar_new:
            pass
        else:
            return

        svar_new = str(svar_new)
        if os.path.exists(svar_dirname + '/' + svar_new):
            svar_new = check_exists(svar_dirname + '/' + svar_new)
            if not svar_new:
                continue
        new_name = os.path.join(svar_dirname, str(svar_new))
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

def check_exists(svar):
    svar_basename = os.path.basename(svar)
    svar_dirname = os.path.dirname(svar)
    dialog = QtGui.QInputDialog()
    # dialog.ComboBoxItems('das', 'asd')
    svar_basename, ok = dialog.getText(MainWindow, "File Manager",
            "File/directory exists, new name:", QtGui.QLineEdit.Normal, svar_basename)
    if ok and svar_basename:
        if not os.path.exists(svar_dirname + '/' + svar_basename):
            return svar_basename
        else:
            return check_exists(svar)
    elif not ok:
        return None

def paste_directory():
    cur_dir = str(model.filePath(ui.ViewWidget.rootIndex()))
    if cut_dirs:
        for svar in cut_dirs:
            svar = str(svar)
            svar_basename = os.path.basename(svar)
            if os.path.exists(cur_dir + '/' + svar_basename):
                svar_basename = check_exists(cur_dir + '/' + svar_basename)
                if not svar_basename:
                    continue
            svar_copy = cur_dir + '/' + svar_basename
            print('Moving: ', svar, ' To: ', svar_copy)
            os.rename(svar, svar_copy)
    elif copy_dirs:
        for svar in copy_dirs:
            svar = str(svar)
            svar_basename = os.path.basename(svar)
            if os.path.exists(cur_dir + '/' + svar_basename):
                svar_basename = check_exists(cur_dir + '/' + svar_basename)
                if not svar_basename:
                    continue
            svar_copy = cur_dir + '/' + str(svar_basename)
            print('Copying: ', svar, ' To: ', svar_copy)
            if os.path.isdir(svar):
                shutil.copytree(svar, svar_copy)
            else:
                shutil.copy2(svar, svar_copy)
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

def extract_archives():
    for sdir in ui.ViewWidget.selectedIndexes():
        sfile = str(model.filePath(sdir))
        if misc.archive_supported(sfile):
            sfile_dirname = os.path.dirname(sfile)
            print('Extracting: ', sfile, 'To: ', sfile_dirname)
            misc.archive_decompress(sfile, sfile_dirname)

def compress_gzip():
    selected_items = []
    for sdir in ui.ViewWidget.selectedIndexes():
        sfile = str(model.filePath(sdir))
        selected_items.append(sfile)
    sfile_archive = sfile + '.tar.gz'
    print('Compressing: ', selected_items, 'To: ', sfile_archive)
    misc.archive_compress(selected_items, sfile_archive, 'gz', True)

def compress_bzip2():
    selected_items = []
    for sdir in ui.ViewWidget.selectedIndexes():
        sfile = str(model.filePath(sdir))
        selected_items.append(sfile)
    sfile_archive = sfile + '.tar.bz2'
    print('Compressing: ', selected_items, 'To: ', sfile_archive)
    misc.archive_compress(selected_items, sfile_archive, 'bz2', True)

def new_file():
    svar, ok = QtGui.QInputDialog.getText(MainWindow, "File Manager",
        "Name:", QtGui.QLineEdit.Normal)
    svar = os.path.realpath(str(svar))
    if ok and svar:
        if os.path.exists(svar):
            svar = check_exists(svar)
            if not svar:
                return
        svar = str(svar)
        print('New file: ', svar)
        misc.file_write(os.path.realpath(svar), '')

def new_directory():
    svar, ok = QtGui.QInputDialog.getText(MainWindow, "File Manager",
        "Name:", QtGui.QLineEdit.Normal)
    svar = os.path.realpath(str(svar))
    if ok and svar:
        if os.path.isdir(svar):
            svar = check_exists(svar)
            if not svar:
                return
        svar = str(svar)
        print('New directory: ', svar)
        misc.dir_create(svar)

def file_properties():
    for sdir in ui.ViewWidget.selectedIndexes():
        sfile = str(model.filePath(sdir))
        p = QtCore.QProcess()
        p.startDetached('qproperties ' + sfile)

def enable_actions():
    for sdir in ui.ViewWidget.selectedIndexes():
        if misc.archive_supported(str(model.filePath(sdir))):
            ui.actionDecompress.setEnabled(True)
        else:
            ui.actionCompressGzip.setEnabled(True)
            ui.actionCompressBzip2.setEnabled(True)

    if ui.ViewWidget.selectedIndexes():
        ui.actionOpen.setEnabled(True)
        ui.actionRename.setEnabled(True)
        ui.actionCut.setEnabled(True)
        ui.actionCopy.setEnabled(True)
        ui.actionDelete.setEnabled(True)
        ui.actionProperties.setEnabled(True)
    else:
        disable_actions()

ui.actionQuit.triggered.connect(sys.exit)
ui.actionAbout.triggered.connect(run_about)
ui.actionIcons.triggered.connect(change_view_icons)
ui.actionList.triggered.connect(change_view_list)
ui.actionOpen.triggered.connect(open_file)
ui.actionRename.triggered.connect(rename_directory)
ui.actionCut.triggered.connect(cut_directory)
ui.actionCopy.triggered.connect(copy_directory)
ui.actionPaste.triggered.connect(paste_directory)
ui.actionDelete.triggered.connect(delete_directory)
ui.actionProperties.triggered.connect(file_properties)
ui.actionFile.triggered.connect(new_file)
ui.actionFolder.triggered.connect(new_directory)
ui.actionDecompress.triggered.connect(extract_archives)
ui.actionCompressGzip.triggered.connect(compress_gzip)
ui.actionCompressBzip2.triggered.connect(compress_bzip2)
# FIXME: open directory on enter
ui.ViewWidget.doubleClicked.connect(change_directory)
ui.ViewWidget.clicked.connect(enable_actions)
ui.BackButton.clicked.connect(change_back_directory)
ui.HomeButton.clicked.connect(change_home)
ui.TerminalButton.clicked.connect(run_terminal)

def show_popup():
    ui.menuActions.popup(QtGui.QCursor.pos())

ui.ViewWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
ui.ViewWidget.customContextMenuRequested.connect(enable_actions)
ui.ViewWidget.customContextMenuRequested.connect(show_popup)

def mount_device(device):
    print device
# show mounted filesystems
for device in os.listdir('/sys/class/block'):
    if device.startswith('s') or device.startswith('h') or device.startswith('v'):
        if os.path.exists('/sys/class/block/' + device + '/removable'):
            continue
        device = '/dev/' + device
        icon = QtGui.QIcon('/home/smil3y/projects/bfp/src/qresources/resources/drive-harddisk.svg') # fromTheme
        e = ui.menuDevices.addAction(icon, device)
        MainWindow.connect(e, QtCore.SIGNAL('triggered()'), lambda device=device: mount_device(device))
#ui.MountsWidget.sortItems()

# run!
MainWindow.show()
sys.exit(app.exec_())
