#!/bin/python2

import qimage_ui
from PyQt4 import QtCore, QtGui
import sys, os, libmisc, libdesktop

# prepare for lift-off
app_version = "0.9.10 (1612195)"
app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()
ui = qimage_ui.Ui_MainWindow()
ui.setupUi(MainWindow)
general = libdesktop.General()
config = libdesktop.Config()
misc = libmisc.Misc()

def setLook():
    general.set_style(app)
setLook()

def run_about():
    QtGui.QMessageBox.about(MainWindow, 'About', \
        '<b>QImage v' + app_version + '</b> by SmiL3y - xakepa10@gmail.com - under GPLv2')

def set_image(sfile):
    image = QtGui.QImage(sfile)
    desktop = QtGui.QDesktopWidget().screenGeometry(MainWindow)
    ui.imageView.setPixmap(QtGui.QPixmap.fromImage(image))
    wscale = image.width()
    hscale = image.height()
    if image.width() > desktop.width():
        wscale = desktop.width() / (image.width()/desktop.width())
    if image.height() > desktop.height():
        hscale = desktop.heigth() / (image.height()/desktop.height())
    MainWindow.resize(wscale, hscale)

def open_file(sfile):
    if not sfile or not os.path.isfile(sfile):
        sfile = QtGui.QFileDialog.getOpenFileName(MainWindow, 'Open', \
            QtCore.QDir.currentPath(), 'Image Files (*.png *.jpg *.jpeg *.svg);;All Files (*)')
        if not sfile:
            return
    set_image(str(sfile))
    ui.actionReload.setEnabled(True)

def reload_file():
    set_image(ui.imageView.pixmap())

ui.actionQuit.triggered.connect(sys.exit)
ui.actionAbout.triggered.connect(run_about)
ui.actionOpen.triggered.connect(open_file)
ui.actionReload.triggered.connect(reload_file)

simage = None
for arg in sys.argv[1:]:
    if os.path.isfile(arg):
        simage = arg
open_file(simage)

# watch configs for changes
def reload_image():
    global config
    reload(libdesktop)
    config = libdesktop.Config()
    setLook()

watcher1 = QtCore.QFileSystemWatcher()
watcher1.addPath(config.settings.fileName())
watcher1.fileChanged.connect(reload_image)

# run!
MainWindow.show()
sys.exit(app.exec_())
