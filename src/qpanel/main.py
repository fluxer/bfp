#!/bin/python2

import qpanel_ui
from PyQt4 import QtCore, QtGui
import sys, libmisc, libdesktop, libxlib

# prepare for lift-off
app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()
ui = qpanel_ui.Ui_MainWindow()
ui.setupUi(MainWindow)
config = libdesktop.Config()
general = libdesktop.General()
misc = libmisc.Misc()
wm = libxlib.WM()

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

def window_activate_deactivate(sid):
    state = wm.get_window_state(sid)
    print state, state.hidden
    if state.hidden == None:
        print('Activating window')
        wm.focus_and_raise(sid)
    else:
        print('Deactivating window')
        wm.deactivate_window(sid)

def window_close(sid):
    wm.close_window(sid)

def context_menu(sid):
    menu = QtGui.QMenu()
    # FIXME: sticky
    menu.addAction(general.get_icon('window'), 'Activate/Deactivate', lambda: window_activate_deactivate(sid))
    menu.addAction(general.get_icon('exit'), 'Close', lambda: window_close(sid))
    menu.popup(QtGui.QCursor.pos())

def window_button(sid, sicon, sname):
    button = QtGui.QPushButton()
    button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
    button.customContextMenuRequested.connect(lambda: context_menu(sid))
    button.setText(sname)
    if sicon:
        button.setIcon(general.get_icon(sicon))
    button.clicked.connect(lambda: window_activate_deactivate(sid))
    return button

for wid in wm.get_clients():
    wicon = wm.get_window_icon(wid)
    wname = wm.get_window_title(wid)
    wstate = wm.get_window_state(wid)
    if wstate == wstate.skip_taskbar or wstate == wstate.hidden or not wname:
        continue
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
wm.reserve_space(MainWindow.winId(), 0, MainWindow.width(), 50, 0)

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

