#!/usr/bin/python

import libqdesktop
from PyQt4 import QtCore, QtGui
import sys, os, shutil
import libmisc
misc = libmisc.Misc()

# prepare for lift-off
app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()
ui = libqdesktop.Ui_MainWindow()
ui.setupUi(MainWindow)

# some variables
cut_dirs = None
copy_dirs = []
delete_dirs = []
p = None

# setup desktop widget
model = QtGui.QFileSystemModel()
ui.DesktopView.setModel(model)
desktop = str(QtCore.QDir.homePath())+ '/Desktop'
root = model.setRootPath(desktop)
ui.DesktopView.setRootIndex(root)
os.chdir(desktop)
ui.DesktopView.setViewMode(ui.DesktopView.IconMode)

# setup desktop menu
def show_popup():
    ui.menuActions.popup(QtGui.QCursor.pos())

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

def enable_actions():
    selected_items = []
    for sdir in ui.DesktopView.selectedIndexes():
        selected_items.append(model.filePath(sdir))
        if misc.archive_supported(str(model.filePath(sdir))):
            ui.actionDecompress.setEnabled(True)
        else:
            ui.actionCompressGzip.setEnabled(True)
            ui.actionCompressBzip2.setEnabled(True)

    if selected_items:
        ui.actionOpen.setEnabled(True)
        ui.actionRename.setEnabled(True)
        ui.actionCut.setEnabled(True)
        ui.actionCopy.setEnabled(True)
        ui.actionDelete.setEnabled(True)
        ui.actionProperties.setEnabled(True)
    else:
        disable_actions()

def rename_directory():
    for svar in ui.DesktopView.selectedIndexes():
        svar = str(model.filePath(svar))
        svar_basename = os.path.basename(svar)
        svar_dirname = os.path.dirname(svar)

        svar_new, ok = QtGui.QInputDialog.getText(MainWindow, "Desktop Manager",
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
    for sdir in ui.DesktopView.selectedIndexes():
        cut_dirs.append(model.filePath(sdir))
    copy_dirs = []
    ui.actionPaste.setEnabled(True)

def copy_directory():
    global cut_dirs
    global copy_dirs
    cut_dirs = []
    copy_dirs = []
    for sdir in ui.DesktopView.selectedIndexes():
        copy_dirs.append(model.filePath(sdir))
    ui.actionPaste.setEnabled(True)

def check_exists(svar):
    svar_basename = os.path.basename(svar)
    svar_dirname = os.path.dirname(svar)
    svar_basename, ok = QtGui.QInputDialog.getText(MainWindow, "Desktop Manager",
            "File/directory exists, new name:", QtGui.QLineEdit.Normal, svar_basename)
    if ok and svar_basename:
        if not os.path.exists(svar_dirname + '/' + svar_basename):
            return svar_basename
        else:
            return check_exists(svar)
    elif not ok:
        return None

def paste_directory():
    cur_dir = str(model.filePath(ui.DesktopView.rootIndex()))
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
            svar_copy = cur_dir + '/' + svar_basename
            print('Copying: ', svar, ' To: ', svar_copy)
            if os.path.isdir(svar):
                shutil.copytree(svar, svar_copy)
            else:
                shutil.copy2(svar, svar_copy)
    ui.actionPaste.setEnabled(False)

def delete_directory():
    for svar in ui.DesktopView.selectedIndexes():
        svar = str(model.filePath(svar))
        reply = QtGui.QMessageBox.question(MainWindow, "Desktop Manager ",
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
    for sdir in ui.DesktopView.selectedIndexes():
        sfile = str(model.filePath(sdir))
        if misc.archive_supported(sfile):
            sfile_dirname = os.path.dirname(sfile)
            print('Extracting: ', sfile, 'To: ', sfile_dirname)
            misc.archive_decompress(sfile, sfile_dirname)

def compress_gzip():
    selected_items = []
    for sdir in ui.DesktopView.selectedIndexes():
        sfile = str(model.filePath(sdir))
        selected_items.append(sfile)
    sfile_archive = sfile + '.tar.gz'
    print('Compressing: ', selected_items, 'To: ', sfile_archive)
    misc.archive_compress(selected_items, sfile_archive, 'gz', True)

def compress_bzip2():
    selected_items = []
    for sdir in ui.DesktopView.selectedIndexes():
        sfile = str(model.filePath(sdir))
        selected_items.append(sfile)
    sfile_archive = sfile + '.tar.bz2'
    print('Compressing: ', selected_items, 'To: ', sfile_archive)
    misc.archive_compress(selected_items, sfile_archive, 'bz2', True)

def new_file():
    svar, ok = QtGui.QInputDialog.getText(MainWindow, "Desktop Manager",
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
    svar, ok = QtGui.QInputDialog.getText(MainWindow, "Desktop Manager",
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

def change_directory():
    QtGui.QDesktopServices.openUrl(QtCore.QUrl(model.filePath(ui.DesktopView.currentIndex())))

def file_properties():
    global p
    for sdir in ui.DesktopView.selectedIndexes():
        sfile = str(model.filePath(sdir))
        p = QtCore.QProcess()
        p.startDetached('qproperties ' + sfile)

# setup desktop view
ui.DesktopView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
ui.DesktopView.customContextMenuRequested.connect(enable_actions)
ui.DesktopView.customContextMenuRequested.connect(show_popup)
ui.menubar.hide()

# setup background
#ui.DesktopView.setStyleSheet("background-image: url(:/resources/image.jpg)")
ui.DesktopView.setStyleSheet("background-image: url(/home/smil3y/Wallpapers/linux_splash_screen) 0 0 0 0 stretch stretch")

# setup signals
ui.DesktopView.doubleClicked.connect(change_directory)
ui.actionOpen.triggered.connect(change_directory)
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
# FIXME: send signal to session leader
ui.actionLogout.triggered.connect(sys.exit)
ui.DesktopView.clicked.connect(enable_actions)

# setup window
MainWindow.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.SplashScreen)
MainWindow.setCentralWidget(ui.DesktopView)

# create dynamic menu
#from __future__ import print_function
import xdg.Menu
import xdg.DesktopEntry

smenu = xdg.Menu.parse('/etc/xdg/menus/kde-applications.menu')

p = None
def execute_program(sfile):
    # FIXME: TryExec
    global p
    x = xdg.Menu.MenuEntry(sfile)
    program = x.DesktopEntry.getExec()
    print('Executing: ', program)
    p = QtCore.QProcess()
    p.startDetached(program)

def show_menu(menu, depth=0, widget=ui.menuApplications):
    print(depth*"-" + "\x1b[01m" + menu.getName() + "\x1b[0m")
    depth += 1
    for entry in menu.getEntries():
        if isinstance(entry, xdg.Menu.Menu):
            show_menu(entry, depth, ui.menuApplications.addMenu(str(entry)))
        elif isinstance(entry, xdg.Menu.MenuEntry):
            icon = QtGui.QIcon.fromTheme(entry.DesktopEntry.getIcon())
            name = entry.DesktopEntry.getName()
            print entry.DesktopEntry.getFileName()
            e = widget.addAction(icon, name)
            MainWindow.connect(e, QtCore.SIGNAL('triggered()'),
                    lambda sfile=entry.DesktopEntry.getFileName(): execute_program(sfile))
            #action.triggered.connect(lambda: execute_program(entry.DesktopEntry.getFileName()))
            #widget.addAction(action)
            # entry.DesktopEntry.getName())
            # menu.getPath()
            # entry.DesktopFileID
            # entry.DesktopEntry.getFileName())
        elif isinstance(entry, xdg.Menu.Separator):
            widget.addSeparator()
        elif isinstance(entry, xdg.Menu.Header):
            print(depth*"-" + "\x1b[01m" + entry.Name + "\x1b[0m")
    depth -= 1

show_menu(smenu)

# run!
MainWindow.showMaximized()
sys.exit(app.exec_())
