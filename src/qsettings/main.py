#!/usr/bin/python

import qsettings_ui
from PyQt4 import QtCore, QtGui
import sys, os, shutil
import libmisc
misc = libmisc.Misc()
import libqdesktop
config = libqdesktop.Config()

# prepare for lift-off
app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()
ui = qsettings_ui.Ui_MainWindow()
ui.setupUi(MainWindow)

fifo = '/tmp/qdesktop.fifo'
misc.ipc_create(fifo, 100)

index = ui.WallpaperModeBox.findText(config.WALLPAPER_STYLE)
ui.WallpaperModeBox.setCurrentIndex(index)

def run_about():
    QtGui.QMessageBox.about(MainWindow, "About", '<b>QSettings v1.0.0</b> by SmiL3y - xakepa10@gmail.com - under GPLv2')

def setWallpaperStyle():
    setImageWallpaper(config.WALLPAPER_IMAGE)

def setImageWallpaper(simage):
    path = ''
    style = str(ui.WallpaperModeBox.currentText())
    if not simage:
        simage = QtGui.QFileDialog.getOpenFileName(MainWindow,
                "Choose",
                QtCore.QDir.homePath(),
                "Image Files (*.jpg *.png *.jpeg);;All Files (*);;")
        simage = str(simage)
    path = os.path.dirname(simage)
    ui.WallpaperView.setStyleSheet("border-image: url(" + simage + ") 0 0 0 0 " + style + " " + style + ";")
    config.write('wallpaper/image', simage)
    config.write('wallpaper/style', style)
    misc.ipc_write(fifo, 'update')

def setColorWallpaper(scolor):
    if not scolor:
        scolor = QtGui.QColorDialog.getColor(QtGui.QColor(config.WALLPAPER_COLOR), MainWindow)
        if scolor.isValid():
            scolor = str(scolor.name())
    ui.WallpaperView.setStyleSheet("background-color: " + scolor + ";")
    config.write('wallpaper/image', '')
    config.write('wallpaper/color', str(scolor))

if config.WALLPAPER_IMAGE:
    setImageWallpaper(config.WALLPAPER_IMAGE)
else:
    setColorWallpaper(config.WALLPAPER_COLOR)

ui.actionQuit.triggered.connect(sys.exit)
ui.actionAbout.triggered.connect(run_about)
ui.ImageWallpaperButton.clicked.connect(setImageWallpaper)
ui.WallpaperModeBox.currentIndexChanged.connect(setWallpaperStyle)
ui.ColorWallpaperButton.clicked.connect(setColorWallpaper)

# run!
MainWindow.show()
sys.exit(app.exec_())
