#!/usr/bin/python

import qsettings_ui
from PyQt4 import QtCore, QtGui
import sys, os
import libmisc
misc = libmisc.Misc()
import libqdesktop
config = libqdesktop.Config()

# prepare for lift-off
app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()
ui = qsettings_ui.Ui_MainWindow()
ui.setupUi(MainWindow)
icon = QtGui.QIcon()

def setLook():
    config.read()
    ssheet = '/etc/qdesktop/styles/' + config.GENERAL_STYLESHEET + '/style.qss'
    if config.GENERAL_STYLESHEET and os.path.isfile(ssheet):
        app.setStyleSheet(misc.file_read(ssheet))
    else:
        app.setStyleSheet('')
    icon.setThemeName(config.GENERAL_ICONTHEME)
setLook()

def run_about():
    QtGui.QMessageBox.about(MainWindow, "About", '<b>QSettings v1.0.0</b> by SmiL3y - xakepa10@gmail.com - under GPLv2')

def setWallpaperStyle():
    setImageWallpaper(config.WALLPAPER_IMAGE)

def setImageWallpaper(simage):
    style = str(ui.WallpaperModeBox.currentText())
    if not simage:
        simage = QtGui.QFileDialog.getOpenFileName(MainWindow,
                "Choose",
                QtCore.QDir.homePath(),
                "Image Files (*.jpg *.png *.jpeg);;All Files (*)")
        simage = str(simage)
    ui.WallpaperView.setStyleSheet("border-image: url(" + simage + ") 0 0 0 0 " + style + " " + style + ";")
    config.write('wallpaper/image', simage)
    config.write('wallpaper/style', style)

def setColorWallpaper(scolor):
    if not scolor:
        scolor = QtGui.QColorDialog.getColor(QtGui.QColor(config.WALLPAPER_COLOR), MainWindow)
        if scolor.isValid():
            scolor = str(scolor.name())
    ui.WallpaperView.setStyleSheet("background-color: " + scolor + ";")
    config.write('wallpaper/image', '')
    config.write('wallpaper/color', str(scolor))

def setStyleSheet():
    ssheet = str(ui.StyleBox.currentText())
    # FIXME: apply stylesheet
    config.write('general/stylesheet', ssheet)

def setIconTheme():
    stheme = str(ui.IconThemeBox.currentText())
    # FIXME: apply icon theme
    config.write('general/icontheme', stheme)

def setMenu():
    smenu = QtGui.QFileDialog.getOpenFileName(MainWindow,
        "Choose",
        QtCore.QDir.homePath(),
        "Menus (*.menu);;All Files (*)")
    smenu = str(smenu)
    ui.MenuEdit.setText(smenu)
    config.write('general/menu', smenu)

def setTerminal():
    sterminal = QtGui.QFileDialog.getOpenFileName(MainWindow,
        "Choose",
        QtCore.QDir.homePath(),
        "All Files (*)")
    sterminal = str(sterminal)
    ui.TerminalEdit.setText(sterminal)
    config.write('default/terminal', sterminal)

def setFileManager():
    sfmanager = QtGui.QFileDialog.getOpenFileName(MainWindow,
        "Choose",
        QtCore.QDir.homePath(),
        "All Files (*)")
    sfmanager = str(sfmanager)
    ui.FileManagerEdit.setText(sfmanager)
    config.write('default/filemanager', sfmanager)

def setWebBrowser():
    swbrowser = QtGui.QFileDialog.getOpenFileName(MainWindow,
        "Choose",
        QtCore.QDir.homePath(),
        "All Files (*)")
    swbrowser = str(swbrowser)
    ui.WebBrowserEdit.setText(swbrowser)
    config.write('default/webbrowser', swbrowser)

# connect widgets to actions
ui.actionQuit.triggered.connect(sys.exit)
ui.actionAbout.triggered.connect(run_about)
ui.ImageWallpaperButton.clicked.connect(setImageWallpaper)
ui.WallpaperModeBox.currentIndexChanged.connect(setWallpaperStyle)
ui.ColorWallpaperButton.clicked.connect(setColorWallpaper)
ui.StyleBox.currentIndexChanged.connect(setStyleSheet)
ui.IconThemeBox.currentIndexChanged.connect(setIconTheme)
ui.MenuButton.clicked.connect(setMenu)
ui.TerminalButton.clicked.connect(setTerminal)
ui.FileManagerButton.clicked.connect(setFileManager)
ui.WebBrowserButton.clicked.connect(setWebBrowser)

# setup values of widgets
for svar in misc.list_dirs('/etc/qdesktop/styles'):
    print svar
    if os.path.isfile(svar + '/style.qss'):
        ui.StyleBox.addItem(os.path.basename(svar))

for svar in misc.list_dirs('/usr/share/icons'):
    if os.path.isfile(svar + '/index.theme'):
        ui.IconThemeBox.addItem(os.path.basename(svar))

index = ui.WallpaperModeBox.findText(config.WALLPAPER_STYLE)
ui.WallpaperModeBox.setCurrentIndex(index)
index = ui.StyleBox.findText(config.GENERAL_STYLESHEET)
ui.StyleBox.setCurrentIndex(index)
index = ui.IconThemeBox.findText(config.GENERAL_ICONTHEME)
ui.IconThemeBox.setCurrentIndex(index)
ui.MenuEdit.setText(config.GENERAL_MENU)
ui.TerminalEdit.setText(config.DEFAULT_TERMINAL)
ui.FileManagerEdit.setText(config.DEFAULT_FILEMANAGER)
ui.WebBrowserEdit.setText(config.DEFAULT_WEBBROWSER)

if config.WALLPAPER_IMAGE:
    setImageWallpaper(config.WALLPAPER_IMAGE)
else:
    setColorWallpaper(config.WALLPAPER_COLOR)

# run!
MainWindow.show()
sys.exit(app.exec_())
