#!/usr/bin/python

import qimage_ui
from PyQt4 import QtCore, QtGui
import sys, os
import libmisc
misc = libmisc.Misc()
import libqdesktop

# prepare for lift-off
app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()
ui = qimage_ui.Ui_MainWindow()
ui.setupUi(MainWindow)

# some variables
scene = QtGui.QGraphicsScene()
ui.graphicsView.setScene(scene)
actions = libqdesktop.Actions(MainWindow, app)
config = libqdesktop.Config()
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

simage = None
for arg in sys.argv[1:]:
    if os.path.isfile(arg):
        simage = arg

def run_about():
    QtGui.QMessageBox.about(MainWindow, "About", '<b>QImage v1.0.0</b> by SmiL3y - xakepa10@gmail.com - under GPLv2')

def open_file(sfile):
    global simage
    if not sfile:
        sfile = QtGui.QFileDialog.getOpenFileName(MainWindow, "Open", \
            QtCore.QDir.currentPath(), "Image Files (*.jpg *.png *.jpeg);;All Files (*)")
        if sfile:
            sfile = str(sfile)
            image = QtGui.QImage(sfile)
            scene.clear()
            scene.addPixmap(QtGui.QPixmap.fromImage(image))
    elif os.path.isfile(sfile):
        image = QtGui.QImage(sfile)
        scene.clear()
        scene.addPixmap(QtGui.QPixmap.fromImage(image))
    simage = sfile
    ui.actionReload.setEnabled(True)

def reload_file():
    open_file(simage)

ui.actionQuit.triggered.connect(sys.exit)
ui.actionAbout.triggered.connect(run_about)
ui.actionOpen.triggered.connect(open_file)
ui.actionReload.triggered.connect(reload_file)

if simage:
    open_file(simage)

# run!
MainWindow.show()
sys.exit(app.exec_())
