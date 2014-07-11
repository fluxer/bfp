#!/bin/python2

import qfile_ui
from PyQt4 import QtCore, QtGui
import sys, os, libmisc, libdesktop

# prepare for lift-off
app_version = "0.9.10 (df2acda)"
app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()
ui = qfile_ui.Ui_MainWindow()
ui.setupUi(MainWindow)
model = QtGui.QFileSystemModel()
actions = libdesktop.Actions(MainWindow, app)
config = libdesktop.Config()
general = libdesktop.General()
mime = libdesktop.Mime()
misc = libmisc.Misc()

def setLook():
    general.set_style(app)
setLook()

def disable_actions():
    ui.actionExecute.setEnabled(False)
    ui.actionOpen.setEnabled(False)
    ui.actionOpenWith.setEnabled(False)
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
        mime.open(sfile)

def open_file_with():
    selected_items = []
    for svar in ui.ViewWidget.selectedIndexes():
        selected_items.append(str(model.filePath(svar)))
    actions.open_items(selected_items)

def change_directory(path=ui.ViewWidget.selectedIndexes()):
    if not isinstance(path, QtCore.QString) and not isinstance(path, str):
        path = model.filePath(path)
    if not os.path.isdir(path):
        mime.open(str(path))
        return
    root = model.setRootPath(path)
    ui.ViewWidget.setRootIndex(root)
    os.chdir(path)
    # model.sortItems()
    ui.AddressBar.setText(str(path))
    disable_actions()

start_dir = QtCore.QDir.currentPath()
ui.ViewWidget.setModel(model)
for arg in sys.argv:
    if os.path.isdir(arg):
        start_dir = arg
change_directory(start_dir)

def run_about():
    QtGui.QMessageBox.about(MainWindow, 'About', \
        '<b>QFile v' + app_version + '</b> by SmiL3y - xakepa10@gmail.com - under GPLv2')

def run_terminal():
    general.execute_program(config.DEFAULT_TERMINAL)

def change_view_icons():
    ui.ViewWidget.setViewMode(ui.ViewWidget.IconMode)

def change_view_list():
    ui.ViewWidget.setViewMode(ui.ViewWidget.ListMode)

def change_view_hidden():
    if ui.actionViewHidden.isChecked():
        model.setFilter(QtCore.QDir.Files | QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot | QtCore.QDir.Hidden)
    else:
        model.setFilter(QtCore.QDir.Files | QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot)

def change_home():
    change_directory(QtCore.QDir.homePath())

def change_back_directory():
    change_directory(os.path.realpath(str(model.rootPath()) + '/..'))

def execute_file():
    selected_items = []
    for svar in ui.ViewWidget.selectedIndexes():
        selected_items.append(str(model.filePath(svar)))
    actions.execute_items(selected_items)

def cut_directory():
    selected_items = []
    for svar in ui.ViewWidget.selectedIndexes():
        selected_items.append(str(model.filePath(svar)))
    actions.cut_items(selected_items)
    ui.actionPaste.setEnabled(True)

def copy_directory():
    selected_items = []
    for svar in ui.ViewWidget.selectedIndexes():
        selected_items.append(str(model.filePath(svar)))
    actions.copy_items(selected_items)
    ui.actionPaste.setEnabled(True)

def paste_directory():
    actions.paste_items()
    ui.actionPaste.setEnabled(False)

def rename_directory():
    selected_items = []
    for svar in ui.ViewWidget.selectedIndexes():
        selected_items.append(str(model.filePath(svar)))
    actions.rename_items(selected_items)

def delete_directory():
    selected_items = []
    for svar in ui.ViewWidget.selectedIndexes():
        selected_items.append(str(model.filePath(svar)))
    actions.delete_items(selected_items)

def file_properties():
    selected_items = []
    for svar in ui.ViewWidget.selectedIndexes():
        selected_items.append(str(model.filePath(svar)))
    actions.properties_items(selected_items)

def new_file():
    actions.new_file()

def new_directory():
    actions.new_directory()

def extract_archives():
    selected_items = []
    for svar in ui.ViewWidget.selectedIndexes():
        selected_items.append(str(model.filePath(svar)))
    actions.extract_items(selected_items)

def compress_gzip():
    selected_items = []
    for svar in ui.ViewWidget.selectedIndexes():
        selected_items.append(str(model.filePath(svar)))
    actions.gzip_items(selected_items)

def compress_bzip2():
    selected_items = []
    for svar in ui.ViewWidget.selectedIndexes():
        selected_items.append(str(model.filePath(svar)))
    actions.bzip2_items(selected_items)

def enable_actions():
    for svar in ui.ViewWidget.selectedIndexes():
        sfile = str(model.filePath(svar))
        if misc.archive_supported(sfile):
            ui.actionDecompress.setEnabled(True)
        else:
            ui.actionCompressGzip.setEnabled(True)
            ui.actionCompressBzip2.setEnabled(True)

    if app.clipboard().text():
        ui.actionPaste.setEnabled(True)

    if ui.ViewWidget.selectedIndexes():
        if os.access(sfile, os.W_OK):
            ui.actionRename.setEnabled(True)
            ui.actionCut.setEnabled(True)
            ui.actionDelete.setEnabled(True)
        if os.access(sfile, os.X_OK) and os.path.isfile(sfile):
            ui.actionExecute.setEnabled(True)
        if os.access(sfile, os.R_OK):
            ui.actionOpen.setEnabled(True)
            ui.actionOpenWith.setEnabled(True)
            ui.actionCopy.setEnabled(True)
        ui.actionProperties.setEnabled(True)
    else:
        disable_actions()

    if os.access(model.rootPath(), os.W_OK):
        ui.actionFile.setEnabled(True)
        ui.actionFolder.setEnabled(True)
    else:
        ui.actionFile.setEnabled(False)
        ui.actionFolder.setEnabled(False)

ui.actionQuit.triggered.connect(sys.exit)
ui.actionAbout.triggered.connect(run_about)
ui.actionIcons.triggered.connect(change_view_icons)
ui.actionList.triggered.connect(change_view_list)
ui.actionViewHidden.triggered.connect(change_view_hidden)
ui.actionExecute.triggered.connect(execute_file)
ui.actionOpen.triggered.connect(open_file)
ui.actionOpenWith.triggered.connect(open_file_with)
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

ui.ViewWidget.customContextMenuRequested.connect(enable_actions)
ui.ViewWidget.customContextMenuRequested.connect(show_popup)

# watch configs for changes
def reload_file():
    global config, mime
    reload(libdesktop)
    config = libdesktop.Config()
    mime = libdesktop.Mime()
    setLook()

watcher1 = QtCore.QFileSystemWatcher()
watcher1.addPaths((config.settings.fileName(), mime.settings.fileName()))
watcher1.fileChanged.connect(reload_file)

# run!
MainWindow.show()
sys.exit(app.exec_())
