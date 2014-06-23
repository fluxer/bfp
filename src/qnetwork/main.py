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

def connect(name):
    service = QtDBus.QDBusInterface('net.connman', name, 'net.connman.Service', bus)
    if service.isValid():
        msg = service.call('Connect')
        reply = QtDBus.QDBusReply(msg)

        if reply.isValid():
            print('Connected to', name)
        else:
            QtGui.QMessageBox.critical(MainWindow, 'Error', str(reply.error().message()))
    else:
        QtGui.QMessageBox.critical(MainWindow, 'Error', str(bus.lastError().message()))

def connect_ethernet():
    selection = ui.EthernetList.selectedIndexes()
    if not selection:
        return
    sconnect = QtCore.QModelIndex(selection[0]).data()
    manager = QtDBus.QDBusInterface('net.connman', '/', 'net.connman.Manager', bus)

    if manager.isValid():
        msg = manager.call('GetServices')
        reply = QtDBus.QDBusReply(msg)

        if reply.isValid():
            for r in reply.value():
                data = r[1]
                if data.get('Name') == sconnect:
                    connect(r[0])
    else:
        QtGui.QMessageBox.critical(MainWindow, 'Error', str(bus.lastError().message()))

def connect_wifi():
    selection = ui.WiFiList.selectedIndexes()
    if not selection:
        return
    sconnect = QtCore.QModelIndex(selection[0]).data()
    manager = QtDBus.QDBusInterface('net.connman', '/', 'net.connman.Manager', bus)

    if manager.isValid():
        msg = manager.call('GetServices')
        reply = QtDBus.QDBusReply(msg)

        if reply.isValid():
            for r in reply.value():
                data = r[1]
                if data.get('Name') == sconnect:
                    connect(r[0])
    else:
        QtGui.QMessageBox.critical(MainWindow, 'Error', str(bus.lastError().message()))


def disconnect(name):
    service = QtDBus.QDBusInterface('net.connman', name, 'net.connman.Service', bus)
    if service.isValid():
        msg = service.call('Disconnect')
        reply = QtDBus.QDBusReply(msg)

        if reply.isValid():
            print('Disconnected from', name)
        else:
            QtGui.QMessageBox.critical(MainWindow, 'Error', str(reply.error().message()))
    else:
        QtGui.QMessageBox.critical(MainWindow, 'Error', str(bus.lastError().message()))

def disconnect_ethernet():
    selection = ui.EthernetList.selectedIndexes()
    if not selection:
        return
    sconnect = QtCore.QModelIndex(selection[0]).data()
    manager = QtDBus.QDBusInterface('net.connman', '/', 'net.connman.Manager', bus)

    if manager.isValid():
        msg = manager.call('GetServices')
        reply = QtDBus.QDBusReply(msg)

        if reply.isValid():
            for r in reply.value():
                data = r[1]
                if data.get('Name') == sconnect:
                    disconnect(r[0])
    else:
        QtGui.QMessageBox.critical(MainWindow, 'Error', str(bus.lastError().message()))

def disconnect_wifi():
    selection = ui.WiFiList.selectedIndexes()
    if not selection:
        return
    sconnect = QtCore.QModelIndex(selection[0]).data()
    manager = QtDBus.QDBusInterface('net.connman', '/', 'net.connman.Manager', bus)

    if manager.isValid():
        msg = manager.call('GetServices')
        reply = QtDBus.QDBusReply(msg)

        if reply.isValid():
            for r in reply.value():
                data = r[1]
                if data.get('Name') == sconnect:
                    disconnect(r[0])
    else:
        QtGui.QMessageBox.critical(MainWindow, 'Error', str(bus.lastError().message()))




def ethernet_scan():
    ethernet = QtDBus.QDBusInterface('net.connman', '/net/connman/technology/ethernet', 'net.connman.Technology', bus)
    manager = QtDBus.QDBusInterface('net.connman', '/', 'net.connman.Manager', bus)

    # get managed services
    if manager.isValid():
        msg = manager.call('GetServices')
        reply = QtDBus.QDBusReply(msg)

        if reply.isValid():
            srow = 1
            ui.EthernetList.clearContents()
            for r in reply.value():
                data = r[1]
                if data.get('Type') == 'ethernet':
                    name = data.get('Name')
                    state = data.get('State')
                    ui.EthernetList.setRowCount(srow)
                    ui.EthernetList.setItem(srow-1, 0, QtGui.QTableWidgetItem(name))
                    ui.EthernetList.setItem(srow-1, 1, QtGui.QTableWidgetItem(state))
                    srow += 1
        else:
            QtGui.QMessageBox.critical(MainWindow, 'Error', str(bus.lastError().message()))
            ui.tabWidget.setTabEnabled(0, False)
    else:
        print(bus.lastError().message())

def wifi_scan():
    wifi = QtDBus.QDBusInterface('net.connman', '/net/connman/technology/wifi', 'net.connman.Technology', bus)
    manager = QtDBus.QDBusInterface('net.connman', '/', 'net.connman.Manager', bus)
    if wifi.isValid():
        msg = wifi.call('Scan')
        reply = QtDBus.QDBusReply(msg)

        if reply.isValid():
            print('WiFi scan complete')
        else:
            QtGui.QMessageBox.critical(MainWindow, 'Error', str(reply.error().message()))
            ui.tabWidget.setTabEnabled(1, False)
    else:
        QtGui.QMessageBox.critical(MainWindow, 'Error', str(bus.lastError().message()))
        ui.tabWidget.setTabEnabled(1, False)

    # get managed services
    if manager.isValid():
        msg = manager.call('GetServices')
        reply = QtDBus.QDBusReply(msg)

        if reply.isValid():
            srow = 1
            ui.WiFiList.clearContents()
            for r in reply.value():
                data = r[1]
                if data.get('Type') == 'wifi':
                    name = data.get('Name')
                    strength = misc.string_convert(data.get('Strength'))
                    security = misc.string_convert(data.get('Security'))
                    print(name, strength, security)
                    ui.WiFiList.setRowCount(srow)
                    ui.WiFiList.setItem(srow-1, 0, QtGui.QTableWidgetItem(name))
                    ui.WiFiList.setItem(srow-1, 1, QtGui.QTableWidgetItem(strength))
                    ui.WiFiList.setItem(srow-1, 2, QtGui.QTableWidgetItem(security))
                    srow += 1
        else:
            QtGui.QMessageBox.critical(MainWindow, 'Error', str(bus.lastError().message()))
            ui.tabWidget.setTabEnabled(1, False)

def enable_buttons():
    sethernet = QtCore.QModelIndex(ui.EthernetList.currentIndex()).data()
    swifi = QtCore.QModelIndex(ui.WiFiList.currentIndex()).data()
    if sethernet:
        ui.EthernetDetails.setEnabled(True)
        ui.EthernetDisconnect.setEnabled(True)
        ui.EthernetConnect.setEnabled(True)
    else:
        ui.EthernetDetails.setEnabled(False)
        ui.EthernetDisconnect.setEnabled(False)
        ui.EthernetConnect.setEnabled(False)

    if swifi:
        ui.WiFiDetails.setEnabled(True)
        ui.WiFiDisconnect.setEnabled(True)
        ui.WiFiConnect.setEnabled(True)
    else:
        ui.WiFiDetails.setEnabled(False)
        ui.WiFiDisconnect.setEnabled(False)
        ui.WiFiConnect.setEnabled(False)

ui.actionQuit.triggered.connect(sys.exit)
ui.actionAbout.triggered.connect(run_about)
ui.EthernetScan.clicked.connect(ethernet_scan)
ui.WiFiScan.clicked.connect(wifi_scan)
ui.WiFiList.currentItemChanged.connect(enable_buttons)
ui.EthernetList.currentItemChanged.connect(enable_buttons)
ui.WiFiDisconnect.clicked.connect(disconnect_wifi)
ui.EthernetDisconnect.clicked.connect(disconnect_ethernet)
ui.WiFiConnect.clicked.connect(connect_wifi)
ui.EthernetConnect.clicked.connect(connect_ethernet)

ethernet_scan()
wifi_scan()

# run!
MainWindow.show()
sys.exit(app.exec_())
