#!/bin/python2

# This is only needed for Python v2 but is harmless for Python v3.
import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

import qnetwork_ui
from PyQt4 import QtCore, QtGui, QtDBus
import sys, os, libmisc, libdesktop

# prepare for lift-off
app_version = "0.9.4 (1d13283)"
app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()
ui = qnetwork_ui.Ui_MainWindow()
ui.setupUi(MainWindow)
misc = libmisc.Misc()
actions = libdesktop.Actions(MainWindow, app)
general = libdesktop.General()
config = libdesktop.Config()
icon = QtGui.QIcon()
bus = QtDBus.QDBusConnection.systemBus()

def setLook():
    general.set_style(app)
    icon.setThemeName(config.GENERAL_ICONTHEME)
setLook()

def run_about():
    QtGui.QMessageBox.about(MainWindow, 'About', \
        '<b>QNetwork v' + app_version + '<</b> by SmiL3y - xakepa10@gmail.com - under GPLv2')

def dbus_call(sobject, spath, smethod, scall):
    interface = QtDBus.QDBusInterface(sobject, spath, smethod, bus)
    if interface.isValid():
        reply = QtDBus.QDBusReply(interface.call(scall))
        if reply.isValid():
            return reply.value()
        else:
            QtGui.QMessageBox.critical(MainWindow, 'Critical', str(reply.error().message()))
            return False
    else:
        QtGui.QMessageBox.critical(MainWindow, 'Critical', str(bus.lastError().message()))
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

def scan_ethernet():
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

def scan_wifi():
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
                strength = str(ord(data.get('Strength')))
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
                    if d == 'Strength':
                        message += d + ': ' + str(ord(data.get(d))) + '\n'
                    else:
                        message += d + ': ' + str(data.get(d)) + '\n'
                QtGui.QMessageBox.information(MainWindow, 'Details', message)
    else:
        ui.tabWidget.setTabEnabled(1, False)

def scan_any():
    if ui.tabWidget.currentIndex() == 0:
        scan_ethernet()
    elif ui.tabWidget.currentIndex() == 1:
        scan_wifi()

def disconnect_any():
    if ui.EthernetList.selectedIndexes():
        disconnect_ethernet()
    elif ui.WiFiList.selectedIndexes():
        disconnect_wifi()

def connect_any():
    if ui.EthernetList.selectedIndexes():
        connect_ethernet()
    elif ui.WiFiList.selectedIndexes():
        connect_wifi()

def details_any():
    if ui.EthernetList.selectedIndexes():
        details_ethernet()
    elif ui.WiFiList.selectedIndexes():
        details_wifi()

def enable_buttons():
    sethernet = QtCore.QModelIndex(ui.EthernetList.currentIndex()).data()
    swifi = QtCore.QModelIndex(ui.WiFiList.currentIndex()).data()

    ui.actionDetails.setEnabled(False)
    ui.actionDisconnect.setEnabled(False)
    ui.actionConnect.setEnabled(False)

    ui.EthernetDetails.setEnabled(False)
    ui.EthernetDisconnect.setEnabled(False)
    ui.EthernetConnect.setEnabled(False)
    if sethernet:
        ui.EthernetDetails.setEnabled(True)
        ui.actionDetails.setEnabled(True)
        rdata = dbus_call('net.connman', '/', 'net.connman.Manager', 'GetServices')
        if rdata:
            for r in rdata:
                data = r[1]
                if data.get('Name') == sethernet:
                    if data.get('State') == 'online':
                        ui.EthernetDisconnect.setEnabled(True)
                        ui.actionDisconnect.setEnabled(True)
                    else:
                        ui.EthernetConnect.setEnabled(True)
                        ui.actionConnect.setEnabled(True)

    ui.WiFiDetails.setEnabled(False)
    ui.WiFiDisconnect.setEnabled(False)
    ui.WiFiConnect.setEnabled(False)
    if swifi:
        ui.WiFiDetails.setEnabled(True)
        ui.actionDetails.setEnabled(True)
        rdata = dbus_call('net.connman', '/', 'net.connman.Manager', 'GetServices')
        if rdata:
            for r in rdata:
                data = r[1]
                if data.get('Name') == swifi:
                    if data.get('State') == 'online':
                        ui.WiFiDisconnect.setEnabled(True)
                        ui.actionDisconnect.setEnabled(True)
                    else:
                        ui.WiFiConnect.setEnabled(True)
                        ui.actionConnect.setEnabled(True)

ui.actionQuit.triggered.connect(sys.exit)
ui.actionAbout.triggered.connect(run_about)
ui.EthernetScan.clicked.connect(scan_ethernet)
ui.WiFiScan.clicked.connect(scan_wifi)
ui.WiFiList.currentItemChanged.connect(enable_buttons)
ui.EthernetList.currentItemChanged.connect(enable_buttons)
ui.WiFiDisconnect.clicked.connect(disconnect_wifi)
ui.EthernetDisconnect.clicked.connect(disconnect_ethernet)
ui.WiFiConnect.clicked.connect(connect_wifi)
ui.EthernetConnect.clicked.connect(connect_ethernet)
ui.WiFiDetails.clicked.connect(details_wifi)
ui.EthernetDetails.clicked.connect(details_ethernet)
ui.actionScan.triggered.connect(scan_any)
ui.actionDetails.triggered.connect(details_any)
ui.actionDisconnect.triggered.connect(disconnect_any)
ui.actionConnect.triggered.connect(connect_any)

class Connector(QtCore.QObject):
    @QtCore.pyqtSlot(QtDBus.QDBusMessage)
    def scan(self):
        scan_wifi()
        scan_ethernet()

connector = Connector()
bus.connect('net.connman', '/', 'net.connman.Manager', 'ServicesChanged', connector.scan)
bus.connect('net.connman', '/', 'net.connman.Manager', 'TechnologyAdded', connector.scan)
bus.connect('net.connman', '/', 'net.connman.Manager', 'TechnologyRemoved', connector.scan)

scan_ethernet()
scan_wifi()

# run!
MainWindow.show()
sys.exit(app.exec_())
