#!/usr/bin/python

import qsettings_ui
from PyQt4 import QtCore, QtGui, QtDBus
import sys
import libmisc
misc = libmisc.Misc()
import libqdesktop
config = libqdesktop.Config()

# prepare for lift-off
app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()
ui = qsettings_ui.Ui_MainWindow()
ui.setupUi(MainWindow)

# setup values ofwidgets
index = ui.WallpaperModeBox.findText(config.WALLPAPER_STYLE)
ui.WallpaperModeBox.setCurrentIndex(index)
ui.StyleSheetEdit.setText(config.GENERAL_STYLESHEET)
ui.IconThemeEdit.setText(config.GENERAL_ICONTHEME)
ui.TerminalEdit.setText(config.DEFAULT_TERMINAL)
ui.FileManagerEdit.setText(config.DEFAULT_FILEMANAGER)
ui.WebBrowserEdit.setText(config.DEFAULT_WEBBROWSER)

# dbus setup
if not QtDBus.QDBusConnection.sessionBus().isConnected():
    sys.stderr.write("Cannot connect to the D-Bus session bus.\n"
        "To start it, run:\n"
        "\teval `dbus-launch --auto-syntax`\n")
    sys.exit(1)

iface = QtDBus.QDBusInterface('com.trolltech.QtDBus.PingExample', '/', '',
    QtDBus.QDBusConnection.sessionBus())

def emit_update(arg, arg2):
    if iface.isValid():
        reply = QtDBus.QDBusReply(iface.call('ping', arg, arg2))
        if not reply.isValid():
            sys.stderr.write("DBus call failed: %s\n" % reply.error().message())

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
    emit_update(simage, style)

def setColorWallpaper(scolor):
    if not scolor:
        scolor = QtGui.QColorDialog.getColor(QtGui.QColor(config.WALLPAPER_COLOR), MainWindow)
        if scolor.isValid():
            scolor = str(scolor.name())
    ui.WallpaperView.setStyleSheet("background-color: " + scolor + ";")
    config.write('wallpaper/image', '')
    config.write('wallpaper/color', str(scolor))
    emit_update(scolor, '')

def setStyleSheet():
    ssheet = QtGui.QFileDialog.getOpenFileName(MainWindow,
        "Choose",
        QtCore.QDir.homePath(),
        "Stylesheets (*.css);;All Files (*)")
    ssheet = str(ssheet)
    # FIXME: set stylesheet
    config.write('general/stylesheet', ssheet)
    # FIXME: emit stylesheet update signal
    # emit_update(ssheet)

if config.WALLPAPER_IMAGE:
    setImageWallpaper(config.WALLPAPER_IMAGE)
else:
    setColorWallpaper(config.WALLPAPER_COLOR)

ui.actionQuit.triggered.connect(sys.exit)
ui.actionAbout.triggered.connect(run_about)
ui.ImageWallpaperButton.clicked.connect(setImageWallpaper)
ui.WallpaperModeBox.currentIndexChanged.connect(setWallpaperStyle)
ui.ColorWallpaperButton.clicked.connect(setColorWallpaper)
ui.StyleSheetButton.clicked.connect(setStyleSheet)

# run!
MainWindow.show()
sys.exit(app.exec_())
