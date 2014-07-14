#!/bin/python2

import qpanel_ui
from PyQt4 import QtCore, QtGui
import sys, libmisc, libdesktop
from Xlib.display import Display
from Xlib import X, protocol

# prepare for lift-off
app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()
ui = qpanel_ui.Ui_MainWindow()
ui.setupUi(MainWindow)
config = libdesktop.Config()
general = libdesktop.General()
misc = libmisc.Misc()

def setLook():
    general.set_style(app)
setLook()

def show_popup():
    ui.menuActions.popup(QtGui.QCursor.pos())

def run_preferences():
    general.execute_program('qsettings')

def do_suspend():
    general.system_suspend(MainWindow)

def do_shutdown():
    general.system_shutdown(MainWindow)

def do_reboot():
    general.system_reboot(MainWindow)

display = Display()
root = display.screen().root
def window_activate_deactivate(sid):
    window = display.create_resource_object('window', wid)
    print window.get_wm_state()
    if window.get_wm_state() == 1:
        # FIXME: deactivate
        window.set_wm_state()
    else:
        # FIXME: activate
        general.execute_command('wmctrl -i -a ' + sid)

def window_close(sid):
    general.execute_command('wmctrl -i -c ' + sid)

def window_state(sid, state):
    general.execute_command('wmctrl -i ' + sid + ' -b toggle,' + state)

def window_button(sid, sicon, sname):
    button = QtGui.QToolButton()
    button.setText(sname)
    if sicon:
        button.setIcon(general.get_icon(sicon))
    #action = QtGui.QAction(general.get_icon('exit'), 'close', button)
    #action.triggered.connect(lambda: window_close(sid))
    #button.addAction(action)
    button.triggered.connect(lambda: window_activate_deactivate(sid))
    return button

windowIDs = root.get_full_property(display.intern_atom('_NET_CLIENT_LIST'), X.AnyPropertyType).value
for wid in windowIDs:
    window = display.create_resource_object('window', wid)
    wicon = window.get_wm_icon_name()
    wname = window.get_wm_name()
    # pid = window.get_full_property(display.intern_atom('_NET_WM_PID'), X.AnyPropertyType)
    ui.horizontalLayout.addWidget(window_button(wid, wicon, wname))

def update_time():
    ui.clockLCDNumber.display(QtCore.QTime.currentTime().toString('hh:mm'))
timer = QtCore.QTimer()
timer.timeout.connect(update_time)
timer.start(60000)
update_time()

ui.actionPreferences.triggered.connect(run_preferences)
ui.actionSuspend.triggered.connect(do_suspend)
ui.actionShutdown.triggered.connect(do_shutdown)
ui.actionReboot.triggered.connect(do_reboot)
ui.actionLogout.triggered.connect(sys.exit)

ui.menubar.hide()
ui.menuButton.clicked.connect(show_popup)

# create dynamic menu
menu = libdesktop.Menu(app, ui.menuApplications)
menu.build()

# setup window
desktop = QtGui.QDesktopWidget()
MainWindow.resize(desktop.width(), 50)
MainWindow.move(0, desktop.rect().bottom() - 50)
MainWindow.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool)

# watch configs for changes
def reload_panel():
    global config, general
    reload(libdesktop)
    config = libdesktop.Config()
    general = libdesktop.General()
    menu.build()
    setLook()

watcher1 = QtCore.QFileSystemWatcher()
watcher1.addPath(config.settings.fileName())
watcher1.fileChanged.connect(reload_panel)

watcher2 = QtCore.QFileSystemWatcher()
watcher2.addPath(sys.prefix + '/share/applications')
watcher2.directoryChanged.connect(menu.build)

# run!
MainWindow.show()
sys.exit(app.exec_())

