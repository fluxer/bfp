#!/usr/bin/python

# This is only needed for Python v2 but is harmless for Python v3.
import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

import qnetwork_ui
from PyQt4 import QtCore, QtGui, QtDBus
import sys, os
import libmisc
misc = libmisc.Misc()
import libqdesktop

# prepare for lift-off
app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()
ui = qnetwork_ui.Ui_MainWindow()
ui.setupUi(MainWindow)

# some variables
actions = libqdesktop.Actions(MainWindow, app)
config = libqdesktop.Config()
icon = QtGui.QIcon()
bus = QtDBus.QDBusConnection.systemBus()

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
    QtGui.QMessageBox.about(MainWindow, "About", '<b>QNetwork v1.0.0</b> by SmiL3y - xakepa10@gmail.com - under GPLv2')

def connect_ethernet():
    pass

def connect_wifi():
    pass

def ethernet_scan():
    ethernet = QtDBus.QDBusInterface('net.connman', '/net/connman/technology/ethernet', 'net.connman.Technology', bus)
    manager = QtDBus.QDBusInterface('net.connman', '/', 'net.connman.Manager', bus)
    if ethernet.isValid():
        msg = ethernet.call('Scan')
        reply = QtDBus.QDBusReply(msg)

        if reply.isValid():
            print('Ethernet scan complete')
        else:
            print('Call failed:', reply.error().message())
            ui.tabWidget.setTabEnabled(0, False)
    else:
        print(bus.lastError().message())
        ui.tabWidget.setTabEnabled(0, False)

    # get managed services
    if manager.isValid():
        msg = manager.call('GetServices')
        reply = QtDBus.QDBusReply(msg)

        if reply.isValid():
            ui.EthernetList.clear()
            for r in reply.value():
                data = r[1]
                type = data.get('Type')
                if type == 'ethernet':
                    name = data.get('Name')
                    status = data.get('Status')
                    print(name, status)
                    ui.EthernetList.insertRow(name, status)
        else:
            print('Call failed:', reply.error().message())
            ui.tabWidget.setTabEnabled(0, False)

def wifi_scan():
    wifi = QtDBus.QDBusInterface('net.connman', '/net/connman/technology/wifi', 'net.connman.Technology', bus)
    manager = QtDBus.QDBusInterface('net.connman', '/', 'net.connman.Manager', bus)
    if wifi.isValid():
        msg = wifi.call('Scan')
        reply = QtDBus.QDBusReply(msg)

        if reply.isValid():
            print('WiFi scan complete')
        else:
            print('Call failed:', reply.error().message())
            ui.tabWidget.setTabEnabled(1, False)
    else:
        print(bus.lastError().message())
        ui.tabWidget.setTabEnabled(1, False)

    # get managed services
    if manager.isValid():
        msg = manager.call('GetServices')
        reply = QtDBus.QDBusReply(msg)

        if reply.isValid():
            ui.WiFiList.clear()
            for r in reply.value():
                data = r[1]
                type = data.get('Type')
                if type == 'wifi':
                    name = data.get('Name')
                    strength = data.get('Strength')
                    security = data.get('Security')
                    print(name, strength, security)
                    # ui.WiFiList.insertRow(name, strength, security)
        else:
            print('Call failed:', reply.error().message())
            ui.tabWidget.setTabEnabled(1, False)

def enable_widgets():
    ethernet_scan()
    wifi_scan()
    pass

enable_widgets()

ui.actionQuit.triggered.connect(sys.exit)
ui.actionAbout.triggered.connect(run_about)
ui.EthernetScan.clicked.connect(ethernet_scan)
ui.WiFiScan.clicked.connect(wifi_scan)

# run!
MainWindow.show()
sys.exit(app.exec_())
