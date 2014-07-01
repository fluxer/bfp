#!/bin/python2

import qsettings_ui
from PyQt4 import QtCore, QtGui
import sys, os
import libmisc, libdesktop, libsystem

# prepare for lift-off
app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()
ui = qsettings_ui.Ui_MainWindow()
ui.setupUi(MainWindow)
icon = QtGui.QIcon()

misc = libmisc.Misc()
config = libdesktop.Config()
mime = libdesktop.Mime()
system = libsystem.System()

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
    QtGui.QMessageBox.about(MainWindow, "About", \
        '<b>QSettings v1.0.0</b> by SmiL3y - xakepa10@gmail.com - under GPLv2')

def setWallpaperStyle():
    setImageWallpaper(config.WALLPAPER_IMAGE)

def setImageWallpaper(simage):
    style = str(ui.WallpaperModeBox.currentText())
    if not simage:
        simage = QtGui.QFileDialog.getOpenFileName(MainWindow, \
            "Choose", QtCore.QDir.homePath(), "Image Files (*.jpg *.png *.jpeg);;All Files (*)")
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
    config.write('general/stylesheet', ssheet)
    setLook()

def setIconTheme():
    stheme = str(ui.IconThemeBox.currentText())
    config.write('general/icontheme', stheme)
    setLook()

def setTerminal():
    config.write('default/terminal', str(ui.TerminalBox.currentText()))

def setFileManager():
    config.write('default/filemanager', str(ui.FileManagerBox.currentText()))

def setWebBrowser():
    config.write('default/webbrowser', str(ui.WebBrowserBox.currentText()))

def unregisterMime():
    smime = ui.MimesView.selectedIndexes()
    if not smime:
        return

    mime.unregister(QtCore.QModelIndex(smime[0]).data().toString())
    ui.MimesView.clear()
    ui.MimesView.addItems(mime.get_mimes())

def registerMime():
    smime, ok = QtGui.QInputDialog.getText(MainWindow, "Mime", \
        "Mime:", QtGui.QLineEdit.Normal, '')
    smime = str(smime)
    if not smime or not ok:
        return
    sprogram = ui.ProgramsView.selectedIndexes()
    if not sprogram:
        return

    mime.register(smime, QtCore.QModelIndex(sprogram[0]).data().toString())
    ui.MimesView.addItem(smime)

def setMime():
    smime = ui.MimesView.selectedIndexes()
    if not smime:
        return
    sprogram = ui.ProgramsView.selectedIndexes()
    if not sprogram:
        return

    mime.register(QtCore.QModelIndex(smime[0]).data(), QtCore.QModelIndex(sprogram[0]).data())

def selectMime():
    sprogram = ui.ProgramsView.selectedIndexes()
    if not sprogram:
        return

    smime = mime.get_mime(QtCore.QModelIndex(sprogram[0]).data().toString())
    for s in ui.MimesView.findItems(sprogram, QtCore.Qt.MatchExactly):
        ui.MimesView.setItemSelected(s, True)

def selectProgram():
    smime = ui.MimesView.selectedIndexes()
    if not smime:
        return

    sprogram = mime.get_program(QtCore.QModelIndex(smime[0]).data().toString())
    for s in ui.ProgramsView.findItems(sprogram, QtCore.Qt.MatchExactly):
        ui.ProgramsView.setItemSelected(s, True)

def setDisk():
    svalue = str(ui.DiskBox.currentText())
    config.write('suspend/disk', svalue)

def setState():
    svalue = str(ui.StateBox.currentText())
    config.write('suspend/state', svalue)

def setGovernorPower():
    svalue = str(ui.GovernorPowerBox.currentText())
    config.write('cpu/power', svalue)

def setGovernorBattery():
    svalue = str(ui.GovernorBatteryBox.currentText())
    config.write('cpu/battery', svalue)

def setLidPower():
    svalue = str(ui.LidPowerBox.currentText())
    config.write('lid/power', svalue)

def setLidBattery():
    svalue = str(ui.LidBatteryBox.currentText())
    config.write('lid/battery', svalue)

def setLowBattery():
    svalue = str(ui.LowBatteryBox.currentText())
    config.write('battery/low', svalue)

# setup values of widgets
for svar in misc.list_dirs('/etc/qdesktop/styles'):
    if os.path.isfile(svar + '/style.qss'):
        ui.StyleBox.addItem(os.path.basename(svar))

for svar in misc.list_dirs(sys.prefix + '/share/icons'):
    if os.path.isfile(svar + '/index.theme'):
        ui.IconThemeBox.addItem(os.path.basename(svar))

for svar in system.get_cpu_governors():
    ui.GovernorPowerBox.addItem(svar)
    ui.GovernorBatteryBox.addItem(svar)

for svar in system.get_power_disks():
    ui.DiskBox.addItem(svar)
for svar in system.get_power_states():
    ui.StateBox.addItem(svar)

sprograms = mime.get_programs()
ui.MimesView.addItems(mime.get_mimes())
ui.ProgramsView.addItems(sprograms)

for program in sprograms:
    sbase = os.path.basename(program)
    if sbase == 'xterm' or sbase == 'uxterm' or sbase == 'urvxt':
        ui.TerminalBox.addItem(program)
    elif sbase == 'qfile' or sbase == 'pcmanfm' or sbase == 'qtfm' \
        or sbase == 'thunar' or sbase == 'nautilus':
        ui.FileManagerBox.addItem(program)
    elif sbase == 'qupzilla' or sbase == 'firefox' or sbase == 'chrome' \
        or sbase == 'chromium' or sbase == 'chromium-browser' \
        or sbase == 'midori' or sbase == 'opera':
        ui.WebBrowserBox.addItem(program)

index = ui.WallpaperModeBox.findText(config.WALLPAPER_STYLE)
ui.WallpaperModeBox.setCurrentIndex(index)
index = ui.StyleBox.findText(config.GENERAL_STYLESHEET)
ui.StyleBox.setCurrentIndex(index)
index = ui.IconThemeBox.findText(config.GENERAL_ICONTHEME)
ui.IconThemeBox.setCurrentIndex(index)
index = ui.TerminalBox.findText(config.DEFAULT_TERMINAL)
ui.TerminalBox.setCurrentIndex(index)
index = ui.FileManagerBox.findText(config.DEFAULT_FILEMANAGER)
ui.FileManagerBox.setCurrentIndex(index)
index = ui.WebBrowserBox.findText(config.DEFAULT_WEBBROWSER)
ui.WebBrowserBox.setCurrentIndex(index)

index = ui.DiskBox.findText(config.SUSPEND_DISK)
ui.DiskBox.setCurrentIndex(index)
index = ui.StateBox.findText(config.SUSPEND_STATE)
ui.StateBox.setCurrentIndex(index)
index = ui.GovernorPowerBox.findText(config.CPU_POWER)
ui.GovernorPowerBox.setCurrentIndex(index)
index = ui.GovernorBatteryBox.findText(config.CPU_BATTERY)
ui.GovernorBatteryBox.setCurrentIndex(index)
index = ui.LidPowerBox.findText(config.LID_POWER)
ui.LidPowerBox.setCurrentIndex(index)
index = ui.LidBatteryBox.findText(config.LID_BATTERY)
ui.LidBatteryBox.setCurrentIndex(index)
index = ui.LowBatteryBox.findText(config.LOW_BATTERY)
ui.LowBatteryBox.setCurrentIndex(index)

# connect widgets to actions
ui.actionQuit.triggered.connect(sys.exit)
ui.actionAbout.triggered.connect(run_about)
ui.ImageWallpaperButton.clicked.connect(setImageWallpaper)
ui.WallpaperModeBox.currentIndexChanged.connect(setWallpaperStyle)
ui.ColorWallpaperButton.clicked.connect(setColorWallpaper)
ui.StyleBox.currentIndexChanged.connect(setStyleSheet)
ui.IconThemeBox.currentIndexChanged.connect(setIconTheme)
ui.TerminalBox.currentIndexChanged.connect(setTerminal)
ui.FileManagerBox.currentIndexChanged.connect(setFileManager)
ui.WebBrowserBox.currentIndexChanged.connect(setWebBrowser)
ui.UnregisterButton.clicked.connect(unregisterMime)
ui.RegisterButton.clicked.connect(registerMime)
ui.AssociateButton.clicked.connect(setMime)
ui.MimesView.currentItemChanged.connect(selectProgram)
ui.ProgramsView.currentItemChanged.connect(selectMime)
ui.DiskBox.currentIndexChanged.connect(setDisk)
ui.StateBox.currentIndexChanged.connect(setState)
ui.GovernorPowerBox.currentIndexChanged.connect(setGovernorPower)
ui.GovernorBatteryBox.currentIndexChanged.connect(setGovernorBattery)
ui.LidPowerBox.currentIndexChanged.connect(setLidPower)
ui.LidBatteryBox.currentIndexChanged.connect(setLidBattery)
ui.LowBatteryBox.currentIndexChanged.connect(setLowBattery)

if config.WALLPAPER_IMAGE:
    setImageWallpaper(config.WALLPAPER_IMAGE)
else:
    setColorWallpaper(config.WALLPAPER_COLOR)

# run!
MainWindow.show()
sys.exit(app.exec_())
