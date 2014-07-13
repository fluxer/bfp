#!/bin/python2

import qimage_ui
from PyQt4 import QtCore, QtGui
import sys, os, libmisc, libdesktop

# prepare for lift-off
app_version = "0.9.10 (9a80322)"
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
    ui.imageView.fileName = sfile
    wscale = image.width()
    hscale = image.height()
    if image.width() > desktop.width():
        wscale = desktop.width() / (image.width()/desktop.width())
    if image.height() > desktop.height():
        hscale = desktop.height() / (image.height()/desktop.height())
    MainWindow.resize(wscale, hscale)

    slist = images_list()
    for simage in slist:
        if simage == sfile:
            sindex = slist.index(sfile)
            if sindex == 0:
                ui.previousButton.setEnabled(False)
                ui.nextButton.setEnabled(True)
            elif sindex+1 == len(slist):
                ui.previousButton.setEnabled(True)
                ui.nextButton.setEnabled(False)
            else:
                ui.previousButton.setEnabled(True)
                ui.nextButton.setEnabled(True)
            break

def open_file(sfile):
    if not sfile or not os.path.isfile(sfile):
        sfile = QtGui.QFileDialog.getOpenFileName(MainWindow, 'Open', \
            QtCore.QDir.currentPath(), 'Image Files (*.png *.jpg *.jpeg *.svg);;All Files (*)')
        if not sfile:
            return
    set_image(str(sfile))
    ui.actionReload.setEnabled(True)

def reload_file():
    set_image(ui.imageView.fileName)

def images_list():
    scurrent = ui.imageView.fileName
    sdir = os.path.dirname(scurrent)
    if not os.path.isdir(sdir):
        ui.previousButton.setEnabaled(False)
        ui.nextButton.setEnabled(False)
        return

    slist = []
    for sfile in os.listdir(sdir):
        sfull = sdir + '/' + sfile
        if os.path.isfile(sfull):
            smime = misc.file_mime(sfull)
            if smime == 'image/png' or smime == 'image/jpeg' \
                or smime == 'image/x-ms-bmp' or smime == 'image/bmp' \
                or smime == 'image/svg+xml':
                slist.append(sdir + '/' + sfile)
    return slist

def previous_image():
    slist = images_list()
    if ui.imageView.fileName in slist:
        set_image(slist[slist.index(ui.imageView.fileName) - 1])

def next_image():
    slist = images_list()
    if ui.imageView.fileName in slist:
        set_image(slist[slist.index(ui.imageView.fileName) + 1])

ui.actionQuit.triggered.connect(sys.exit)
ui.actionAbout.triggered.connect(run_about)
ui.actionOpen.triggered.connect(open_file)
ui.actionReload.triggered.connect(reload_file)
ui.previousButton.clicked.connect(previous_image)
ui.nextButton.clicked.connect(next_image)

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
