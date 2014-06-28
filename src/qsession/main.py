#!/bin/python2

import qsession_ui
from PyQt4 import QtCore, QtGui
import sys, os, pwd, crypt
import libmisc, libqdesktop
misc = libmisc.Misc()

# prepare for lift-off
app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()
ui = qsession_ui.Ui_MainWindow()
ui.setupUi(MainWindow)

# some variables
config = libqdesktop.Config()
menu = libqdesktop.Menu(app, ui.menuActions)
general = libqdesktop.General()
icon = QtGui.QIcon()

# setup desktop widget
os.chdir('/')

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
        MainWindow.setStyleSheet("border-image: url(" + \
            config.WALLPAPER_IMAGE + ") 0 0 0 0 " + config.WALLPAPER_STYLE + \
            " " + config.WALLPAPER_STYLE + ";")
    else:
        MainWindow.setStyleSheet("background-color: " + config.WALLPAPER_COLOR + ";")
# setWallpaper()

def login():
    username = str(ui.UserNameBox.currentText())
    password = str(ui.PasswordEdit.text())
    desktop = str(ui.DesktopBox.currentText())

    cryptedpasswd = pwd.getpwnam(username).pw_passwd
    if cryptedpasswd == 'x' or cryptedpasswd == '*':
        QtGui.QMessageBox.critical(MainWindow, 'Error', 'Sorry, currently no support for shadow passwords')
        ui.UserNameBox.setFocus()
        ui.PasswordEdit.clear()
        return

    if crypt.crypt(password, cryptedpasswd) == cryptedpasswd:
        try:
            # os.setsid()
            os.setgid(pwd.getpwnam(username).pw_gid)
            os.setuid(pwd.getpwnam(username).pw_uid)
            os.putenv('HOME', pwd.getpwnam(username).pw_dir)
            MainWindow.hide()
            os.system('xinit ' + desktop + ' -- :9')
        except Exception as detail:
            QtGui.QMessageBox.critical(MainWindow, 'Error', 'Login was not sucessful:\n\n' + str(detail))
            ui.PasswordEdit.setFocus()
            ui.PasswordEdit.clear()
        finally:
            MainWindow.showMaximized()
    else:
        QtGui.QMessageBox.critical(MainWindow, 'Error', 'Incorrect password.')
        ui.PasswordEdit.setFocus()
        ui.PasswordEdit.clear()

def do_shutdown():
    general.system_shutdown(MainWindow)

def do_reboot():
    general.system_reboot(MainWindow)


for p in pwd.getpwall():
    ui.UserNameBox.addItem(p.pw_name)

for x in ('startfluxbox', 'startkde'):
    b = misc.whereis(x, fallback=False)
    if b:
        ui.DesktopBox.addItem(b)

# setup desktop menu
def show_popup():
    ui.menuActions.popup(QtGui.QCursor.pos())

# setup signals
ui.LoginButton.clicked.connect(login)
ui.actionShutdown.triggered.connect(do_shutdown)
ui.actionReboot.triggered.connect(do_reboot)

# setup window
MainWindow.setWindowFlags(QtCore.Qt.FramelessWindowHint)
d = QtGui.QDesktopWidget().screenGeometry(MainWindow)
ui.frame.move((d.width()/2)-165, (d.height()/2)-120)

# run!
MainWindow.showMaximized()
sys.exit(app.exec_())
