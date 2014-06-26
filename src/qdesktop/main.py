#!/bin/python2

import qdesktop_ui
from PyQt4 import QtCore, QtGui
import sys, os
import libmisc
misc = libmisc.Misc()
import libqdesktop
import libsystem

# prepare for lift-off
app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()
ui = qdesktop_ui.Ui_MainWindow()
ui.setupUi(MainWindow)

# some variables
config = libqdesktop.Config()
mime = libqdesktop.Mime()
actions = libqdesktop.Actions(MainWindow, app)
system = libsystem.System()
icon = QtGui.QIcon()

# setup desktop widget
model = QtGui.QFileSystemModel()
ui.DesktopView.setModel(model)
desktop = str(QtCore.QDir.homePath())
misc.dir_create(desktop)
root = model.setRootPath(desktop)
ui.DesktopView.setRootIndex(root)
os.chdir(desktop)
ui.DesktopView.setViewMode(ui.DesktopView.IconMode)

def setLook():
    config.read()
    ssheet = '/etc/qdesktop/styles/' + config.GENERAL_STYLESHEET + '/style.qss'
    if config.GENERAL_STYLESHEET and os.path.isfile(ssheet):
        app.setStyleSheet(misc.file_read(ssheet))
    else:
        app.setStyleSheet('')
    icon.setThemeName(config.GENERAL_ICONTHEME)
setLook()

def setWallpaper():
    if config.WALLPAPER_IMAGE:
        ui.DesktopView.setStyleSheet("border-image: url(" + \
            config.WALLPAPER_IMAGE + ") 0 0 0 0 " + config.WALLPAPER_STYLE + \
            " " + config.WALLPAPER_STYLE + "; color: rgb(179, 179, 179);")
    else:
        ui.DesktopView.setStyleSheet("background-color: " + config.WALLPAPER_COLOR + ";")
setWallpaper()

# setup desktop menu
def show_popup():
    ui.menuActions.popup(QtGui.QCursor.pos())

def open_file():
    for sfile in ui.DesktopView.selectedIndexes():
        sfile = str(model.filePath(sfile))
        mime.open(sfile)

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
    for svar in ui.DesktopView.selectedIndexes():
        sfile = str(model.filePath(svar))
        if misc.archive_supported(sfile):
            ui.actionDecompress.setEnabled(True)
        else:
            ui.actionCompressGzip.setEnabled(True)
            ui.actionCompressBzip2.setEnabled(True)

    if ui.DesktopView.selectedIndexes():
        if os.access(sfile, os.W_OK):
            ui.actionRename.setEnabled(True)
            ui.actionCut.setEnabled(True)
            ui.actionDelete.setEnabled(True)
        if os.access(sfile, os.R_OK):
            ui.actionOpen.setEnabled(True)
            ui.actionCopy.setEnabled(True)
        ui.actionProperties.setEnabled(True)
    else:
        disable_actions()

def cut_directory():
    selected_items = []
    for svar in ui.DesktopView.selectedIndexes():
        selected_items.append(str(model.filePath(svar)))
    actions.cut_items(selected_items)
    ui.actionPaste.setEnabled(True)

def copy_directory():
    selected_items = []
    for svar in ui.DesktopView.selectedIndexes():
        selected_items.append(str(model.filePath(svar)))
    actions.copy_items(selected_items)
    ui.actionPaste.setEnabled(True)

def paste_directory():
    actions.paste_items()
    ui.actionPaste.setEnabled(False)

def rename_directory():
    selected_items = []
    for svar in ui.DesktopView.selectedIndexes():
        selected_items.append(str(model.filePath(svar)))
    actions.rename_items(selected_items)

def delete_directory():
    selected_items = []
    for svar in ui.DesktopView.selectedIndexes():
        selected_items.append(str(model.filePath(svar)))
    actions.delete_items(selected_items)

def file_properties():
    selected_items = []
    for svar in ui.DesktopView.selectedIndexes():
        selected_items.append(str(model.filePath(svar)))
    actions.properties_items(selected_items)

def new_file():
    actions.new_file()

def new_directory():
    actions.new_directory()

def extract_archives():
    selected_items = []
    for svar in ui.DesktopView.selectedIndexes():
        selected_items.append(str(model.filePath(svar)))
    actions.extract_items(selected_items)

def compress_gzip():
    selected_items = []
    for svar in ui.DesktopView.selectedIndexes():
        selected_items.append(str(model.filePath(svar)))
    actions.gzip_items(selected_items)

def compress_bzip2():
    selected_items = []
    for svar in ui.DesktopView.selectedIndexes():
        selected_items.append(str(model.filePath(svar)))
    actions.bzip2_items(selected_items)

def change_directory():
    mime.open(str(model.filePath(ui.DesktopView.currentIndex())))

def run_terminal():
    p = QtCore.QProcess()
    p.setWorkingDirectory(QtCore.QDir.homePath())
    p.startDetached(config.DEFAULT_TERMINAL)
    p.close()

def run_filemanager():
    p = QtCore.QProcess()
    p.setWorkingDirectory(QtCore.QDir.homePath())
    p.startDetached(config.DEFAULT_FILEMANAGER)
    p.close()

def run_webbrowser():
    p = QtCore.QProcess()
    p.setWorkingDirectory(QtCore.QDir.homePath())
    p.startDetached(config.DEFAULT_WEBBROWSER)
    p.close()

def run_preferences():
    p = QtCore.QProcess()
    p.setWorkingDirectory(QtCore.QDir.homePath())
    p.startDetached('qsettings')
    p.close()

# setup desktop view
ui.DesktopView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
ui.DesktopView.customContextMenuRequested.connect(enable_actions)
ui.DesktopView.customContextMenuRequested.connect(show_popup)
ui.menubar.hide()

# setup signals
# FIXME: open directory on enter
ui.DesktopView.doubleClicked.connect(change_directory)
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
ui.actionTerminal.triggered.connect(run_terminal)
ui.actionFileManager.triggered.connect(run_filemanager)
ui.actionWebBrowser.triggered.connect(run_webbrowser)
ui.actionPreferences.triggered.connect(run_preferences)
ui.actionShutdown.triggered.connect(system.do_shutdown)
ui.actionReboot.triggered.connect(system.do_reboot)
ui.actionLogout.triggered.connect(sys.exit)
ui.DesktopView.clicked.connect(enable_actions)

# setup window
MainWindow.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.SplashScreen)
MainWindow.setCentralWidget(ui.DesktopView)

# create dynamic menu
menu = libqdesktop.Menu(app, ui.menuApplications)
menu.build()

# run!
MainWindow.showMaximized()
sys.exit(app.exec_())
