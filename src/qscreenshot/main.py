#!/bin/python2

import qscreenshot_ui
from PyQt4 import QtGui
import sys, time, libmisc, libdesktop

# prepare for lift-off
app_version = "0.9.9 (e3463c2)"
app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()
ui = qscreenshot_ui.Ui_MainWindow()
ui.setupUi(MainWindow)
misc = libmisc.Misc()
config = libdesktop.Config()
general = libdesktop.General()

def setLook():
    general.set_style(app)
setLook()

def run_about():
    QtGui.QMessageBox.about(MainWindow, 'About', \
        '<b>QScreenshot v' + app_version + '</b> by SmiL3y - xakepa10@gmail.com - under GPLv2')

def get_filename():
    sfile = QtGui.QFileDialog.getSaveFileName(MainWindow, 'Save', \
        'screenshot.png', 'Image Files (*.png *.jpg *.jpeg *.svg);;All Files (*)')
    if sfile:
        return str(sfile)
    return None

def get_extension(sfile):
    ext = sfile.split('.')[-1]
    if ext == sfile:
        return 'png'
    return ext

def take_screenshot():
    delay = ui.delayBox.value()
    MainWindow.hide()

    if delay > 0:
        time.sleep(delay)

    sfile = get_filename()
    if sfile:
        extension = get_extension(sfile)
        if not sfile.endswith(extension):
            sfile = sfile + '.' + extension
        # to avoid the save dialog being captured
        time.sleep(1)
        p = QtGui.QPixmap.grabWindow(app.desktop().winId())
        p.save(sfile, extension)
        sys.exit()

ui.actionQuit.triggered.connect(sys.exit)
ui.actionAbout.triggered.connect(run_about)
ui.takeButton.clicked.connect(take_screenshot)

MainWindow.show()
sys.exit(app.exec_())