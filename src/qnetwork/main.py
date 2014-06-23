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

def dbus_call(sobject, spath, smethod, scall):
    interface = QtDBus.QDBusInterface(sobject, spath, smethod, bus)
    if interface.isValid():
        reply = QtDBus.QDBusReply(interface.call(scall))
        if reply.isValid():
            return reply.value()
        else:
            QtGui.QMessageBox.critical(MainWindow, 'Error', str(reply.error().message()))
            return False
    else:
        QtGui.QMessageBox.critical(MainWindow, 'Error', str(bus.lastError().message()))
        return False

def connect(name):
    if dbus_call('net.connman', name, 'net.connman.Service', 'Connect'):
        print('Connected to', name)

def connect_ethernet():
    selection = ui.EthernetList.selectedIndexes()
    if not selection:
        return
    sconnect = QtCore.QModelIndex(selection[0]).data()

    rdata = dbus_call('net.connman', '/', 'net.connman.Manager', 'GetServices')
    if rdata:
        for r in rdata:
            data = r[1]
            if data.get('Name') == sconnect:
                connect(r[0])

def connect_wifi():
    selection = ui.WiFiList.selectedIndexes()
    if not selection:
        return
    sconnect = QtCore.QModelIndex(selection[0]).data()

    rdata = dbus_call('net.connman', '/', 'net.connman.Manager', 'GetServices')
    if rdata:
        for r in rdata:
            data = r[1]
            if data.get('Name') == sconnect:
                connect(r[0])

def disconnect(name):
    if dbus_call('net.connman', name, 'net.connman.Service', 'Disconnect'):
        print('Disconnected from', name)

def disconnect_ethernet():
    selection = ui.EthernetList.selectedIndexes()
    if not selection:
        return
    sconnect = QtCore.QModelIndex(selection[0]).data()

    rdata = dbus_call('net.connman', '/', 'net.connman.Manager', 'GetServices')
    if rdata:
        for r in rdata:
            data = r[1]
            if data.get('Name') == sconnect:
                disconnect(r[0])

def disconnect_wifi():
    selection = ui.WiFiList.selectedIndexes()
    if not selection:
        return
    sconnect = QtCore.QModelIndex(selection[0]).data()

    rdata = dbus_call('net.connman', '/', 'net.connman.Manager', 'GetServices')
    if rdata:
        for r in rdata:
            data = r[1]
            if data.get('Name') == sconnect:
                disconnect(r[0])

def ethernet_scan():
    # dbus_call('net.connman', '/net/connman/technology/ethernet', 'net.connman.Technology', 'Scan'):

    # get managed services
    rdata = dbus_call('net.connman', '/', 'net.connman.Manager', 'GetServices')
    if rdata:
        srow = 1
        ui.EthernetList.clearContents()
        for r in rdata:
            data = r[1]
            if data.get('Type') == 'ethernet':
                name = data.get('Name')
                state = data.get('State')
                ui.EthernetList.setRowCount(srow)
                ui.EthernetList.setItem(srow-1, 0, QtGui.QTableWidgetItem(name))
                ui.EthernetList.setItem(srow-1, 1, QtGui.QTableWidgetItem(state))
                srow += 1
    else:
        ui.tabWidget.setTabEnabled(0, False)

def wifi_scan():
    dbus_call('net.connman', '/net/connman/technology/wifi', 'net.connman.Technology', 'Scan')

    # get managed services
    rdata = dbus_call('net.connman', '/', 'net.connman.Manager', 'GetServices')
    if rdata:
        srow = 1
        ui.WiFiList.clearContents()
        for r in rdata:
            data = r[1]
            if data.get('Type') == 'wifi':
                name = data.get('Name')
                strength = misc.string_convert(data.get('Strength'))
                security = misc.string_convert(data.get('Security'))
                ui.WiFiList.setRowCount(srow)
                ui.WiFiList.setItem(srow-1, 0, QtGui.QTableWidgetItem(name))
                ui.WiFiList.setItem(srow-1, 1, QtGui.QTableWidgetItem(strength))
                ui.WiFiList.setItem(srow-1, 2, QtGui.QTableWidgetItem(security))
                srow += 1
    else:
        ui.tabWidget.setTabEnabled(1, False)

def details_ethernet():
    selection = ui.EthernetList.selectedIndexes()
    if not selection:
        return
    sconnect = QtCore.QModelIndex(selection[0]).data()

    rdata = dbus_call('net.connman', '/', 'net.connman.Manager', 'GetServices')
    if rdata:
        for r in rdata:
            data = r[1]
            name = data.get('Name')
            if name == sconnect:
                message = ''
                for d in data:
                    message += d + ': ' + str(data.get(d)) + '\n'
                QtGui.QMessageBox.information(MainWindow, 'Details', message)
    else:
        ui.tabWidget.setTabEnabled(1, False)

def details_wifi():
    selection = ui.WiFiList.selectedIndexes()
    if not selection:
        return
    sconnect = QtCore.QModelIndex(selection[0]).data()

    rdata = dbus_call('net.connman', '/', 'net.connman.Manager', 'GetServices')
    if rdata:
        for r in rdata:
            data = r[1]
            name = data.get('Name')
            if name == sconnect:
                message = ''
                for d in data:
                    message += d + ': ' + str(data.get(d)) + '\n'
                QtGui.QMessageBox.information(MainWindow, 'Details', message)
    else:
        ui.tabWidget.setTabEnabled(1, False)

def enable_buttons():
    sethernet = QtCore.QModelIndex(ui.EthernetList.currentIndex()).data()
    swifi = QtCore.QModelIndex(ui.WiFiList.currentIndex()).data()

    ui.EthernetDetails.setEnabled(False)
    ui.EthernetDisconnect.setEnabled(False)
    ui.EthernetConnect.setEnabled(False)
    if sethernet:
        ui.EthernetDetails.setEnabled(True)
        rdata = dbus_call('net.connman', '/', 'net.connman.Manager', 'GetServices')
        if rdata:
            for r in rdata:
                data = r[1]
                if data.get('Name') == sethernet:
                    if data.get('State') == 'online':
                        ui.EthernetDisconnect.setEnabled(True)
                    else:
                        ui.EthernetConnect.setEnabled(True)

    ui.WiFiDetails.setEnabled(False)
    ui.WiFiDisconnect.setEnabled(False)
    ui.WiFiConnect.setEnabled(False)
    if swifi:
        ui.WiFiDetails.setEnabled(True)
        rdata = dbus_call('net.connman', '/', 'net.connman.Manager', 'GetServices')
        if rdata:
            for r in rdata:
                data = r[1]
                if data.get('Name') == swifi:
                    if data.get('State') == 'online':
                        ui.WiFiDisconnect.setEnabled(True)
                    else:
                        ui.WiFiConnect.setEnabled(True)

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
ui.WiFiDetails.clicked.connect(details_wifi)
ui.EthernetDetails.clicked.connect(details_ethernet)

ethernet_scan()
wifi_scan()

# run!
MainWindow.show()
sys.exit(app.exec_())
