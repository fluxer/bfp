#!/bin/python2

import qsession_ui
from PyQt4 import QtCore, QtGui
import sys, os, pwd, crypt, libmisc, libdesktop

# prepare for lift-off
app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()
ui = qsession_ui.Ui_MainWindow()
ui.setupUi(MainWindow)
config = libdesktop.Config()
general = libdesktop.General()
misc = libmisc.Misc()

def setLook():
    general.set_style(app)
setLook()

def setWallpaper():
    if config.WALLPAPER_IMAGE:
        MainWindow.setStyleSheet("border-image: url(" + \
            config.WALLPAPER_IMAGE + ") 0 0 0 0 " + config.WALLPAPER_STYLE + \
            " " + config.WALLPAPER_STYLE + ";")
    else:
        MainWindow.setStyleSheet("background-color: " + config.WALLPAPER_COLOR + ";")
# setWallpaper()

def login(autologin=None):
    username = str(ui.UserNameBox.currentText())
    password = str(ui.PasswordEdit.text())
    desktop = misc.whereis('startfluxbox')
    if autologin:
        username = autologin

    pw_passwd = pwd.getpwnam(username).pw_passwd
    pw_uid = pwd.getpwnam(username).pw_uid
    pw_gid = pwd.getpwnam(username).pw_gid
    pw_dir = pwd.getpwnam(username).pw_dir
    pw_shell = pwd.getpwnam(username).pw_shell

    if pw_passwd == 'x' or pw_passwd == '*':
        QtGui.QMessageBox.critical(MainWindow, 'Critical', 'Shadow passwords are hot supported')
        ui.UserNameBox.setFocus()
        ui.PasswordEdit.clear()
        return

    if autologin or crypt.crypt(password, pw_passwd) == pw_passwd:
        try:
            try:
                os.setsid()
            except Exception as detail:
                print(str(detail))
            os.setgid(pw_gid)
            os.setuid(pw_uid)
            os.putenv('HOME', pw_dir)
            os.putenv('SHELL', pw_shell)
            if os.path.isdir(pw_dir):
                os.chdir(pw_dir)
            else:
                os.chdir('/')
            MainWindow.hide()
            os.system('xinit ' + desktop + ' -- :9')
        except Exception as detail:
            QtGui.QMessageBox.critical(MainWindow, 'Critical', 'Login was not sucessful:\n\n' + str(detail))
            ui.PasswordEdit.setFocus()
            ui.PasswordEdit.clear()
        finally:
            MainWindow.show()
    else:
        QtGui.QMessageBox.critical(MainWindow, 'Critical', 'Incorrect password.')
        ui.PasswordEdit.setFocus()
        ui.PasswordEdit.clear()

def do_shutdown():
    general.system_shutdown(MainWindow)

def do_reboot():
    general.system_reboot(MainWindow)

# setup signals
ui.LoginButton.clicked.connect(login)
ui.actionShutdown.triggered.connect(do_shutdown)
ui.actionReboot.triggered.connect(do_reboot)

# setup window
MainWindow.setWindowFlags(QtCore.Qt.FramelessWindowHint)
d = QtGui.QDesktopWidget().screenGeometry(MainWindow)
ui.frame.move((d.width()/2)-165, (d.height()/2)-120)

# watch configs for changes
def reload_session():
    global config
    reload(libdesktop)
    config = libdesktop.Config()
    setLook()
    # setWallpaper()

watcher1 = QtCore.QFileSystemWatcher()
watcher1.addPath(config.settings.fileName())
watcher1.fileChanged.connect(reload_session)

autologin = False
for p in pwd.getpwall():
    # skip system users
    if p.pw_uid == 0 or p.pw_uid > 999:
        ui.UserNameBox.addItem(p.pw_name)
        for arg in sys.argv[1:]:
            if arg == p.pw_name:
                autologin = p.pw_name
if autologin:
    login(p.pw_name)

# run!
os.chdir('/')
MainWindow.showMaximized()
sys.exit(app.exec_())
