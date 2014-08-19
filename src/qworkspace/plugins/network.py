#!/bin/pyhton2

from PyQt4 import QtCore, QtGui, QtDBus
import libworkspace
general = libworkspace.General()


class Widget(QtGui.QWidget):
    ''' Tab widget '''
    def __init__(self, parent, spath=None):
        super(Widget, self).__init__()
        self.parent = parent
        self.spath = spath
        self.name = 'network'

        self.bus = QtDBus.QDBusConnection.systemBus()
        self.mainLayout = QtGui.QGridLayout()
        self.tabWidget = QtGui.QTabWidget()
        self.EthernetList = QtGui.QTableWidget()
        self.WiFiList = QtGui.QTableWidget()
        self.tabWidget.insertTab(0, self.EthernetList, 'Ethernet')
        self.tabWidget.insertTab(1, self.WiFiList, 'WiFi')
        self.secondLayout = QtGui.QHBoxLayout()
        self.scanButton = QtGui.QPushButton(general.get_icon('find'), '')
        self.connectButton = QtGui.QPushButton(general.get_icon('connect'), '')
        self.disconnectButton = QtGui.QPushButton(general.get_icon('diconnect'), '')
        self.detailsButton = QtGui.QPushButton(general.get_icon('details'), '')
        self.secondLayout.addWidget(self.scanButton)
        self.secondLayout.addWidget(self.connectButton)
        self.secondLayout.addWidget(self.disconnectButton)
        self.secondLayout.addWidget(self.detailsButton)
        self.mainLayout.addWidget(self.tabWidget)
        self.mainLayout.addLayout(self.secondLayout, QtCore.Qt.AlignBottom, 0)
        self.setLayout(self.mainLayout)

        self.scanButton.clicked.connect(self.scan_any)
        self.connectButton.clicked.connect(self.connect_any)
        self.disconnectButton.clicked.connect(self.disconnect_any)
        self.detailsButton.clicked.connect(self.details_any)
        self.WiFiList.currentItemChanged.connect(self.enable_buttons)
        self.EthernetList.currentItemChanged.connect(self.enable_buttons)

        self.bus.connect('net.connman', '/', 'net.connman.Manager', 'ServicesChanged', self.scan)
        self.bus.connect('net.connman', '/', 'net.connman.Manager', 'TechnologyAdded', self.scan)
        self.bus.connect('net.connman', '/', 'net.connman.Manager', 'TechnologyRemoved', self.scan)

        self.scan_ethernet()
        self.scan_wifi()

    def dbus_call(self, sobject, spath, smethod, scall):
        interface = QtDBus.QDBusInterface(sobject, spath, smethod, self.bus)
        if interface.isValid():
            reply = QtDBus.QDBusReply(interface.call(scall))
            if reply.isValid():
                return reply.value()
            else:
                QtGui.QMessageBox.critical(self, self.tr('Critical'), str(reply.error().message()))
                return False
        else:
            QtGui.QMessageBox.critical(self, self.tr('Critical'), str(self.bus.lastError().message()))
            return False

    def connect(self, name):
        if self.dbus_call('net.connman', name, 'net.connman.Service', 'Connect'):
            print('Connected to', name)

    def connect_ethernet(self):
        selection = self.EthernetList.selectedIndexes()
        if not selection:
            return
        sconnect = QtCore.QModelIndex(selection[0]).data()

        rdata = self.dbus_call('net.connman', '/', 'net.connman.Manager', 'GetServices')
        if rdata:
            for r in rdata:
                data = r[1]
                if data.get('Name') == sconnect:
                    self.connect(r[0])

    def connect_wifi(self):
        selection = self.WiFiList.selectedIndexes()
        if not selection:
            return
        sconnect = QtCore.QModelIndex(selection[0]).data()

        rdata = self.dbus_call('net.connman', '/', 'net.connman.Manager', 'GetServices')
        if rdata:
            for r in rdata:
                data = r[1]
                if data.get('Name') == sconnect:
                    self.connect(r[0])

    def disconnect(self, name):
        if self.dbus_call('net.connman', name, 'net.connman.Service', 'Disconnect'):
            print('Disconnected from', name)

    def disconnect_ethernet(self):
        selection = self.EthernetList.selectedIndexes()
        if not selection:
            return
        sconnect = QtCore.QModelIndex(selection[0]).data()

        rdata = self.dbus_call('net.connman', '/', 'net.connman.Manager', 'GetServices')
        if rdata:
            for r in rdata:
                data = r[1]
                if data.get('Name') == sconnect:
                    self.disconnect(r[0])

    def disconnect_wifi(self):
        selection = self.WiFiList.selectedIndexes()
        if not selection:
            return
        sconnect = QtCore.QModelIndex(selection[0]).data()

        rdata = self.dbus_call('net.connman', '/', 'net.connman.Manager', 'GetServices')
        if rdata:
            for r in rdata.toStringList():
                data = r[1]
                if data.get('Name') == sconnect:
                    self.disconnect(r[0])

    def scan_ethernet(self):
        # self.dbus_call('net.connman', '/net/connman/technology/ethernet', 'net.connman.Technology', 'Scan'):

        # get managed services
        rdata = self.dbus_call('net.connman', '/', 'net.connman.Manager', 'GetServices')
        if rdata:
            srow = 1
            self.EthernetList.clearContents()
            for r in rdata.toStringList():
                data = r[1]
                if data.get('Type') == 'ethernet':
                    name = data.get('Name')
                    state = data.get('State')
                    self.EthernetList.setRowCount(srow)
                    self.EthernetList.setItem(srow-1, 0, QtGui.QTableWidgetItem(name))
                    self.EthernetList.setItem(srow-1, 1, QtGui.QTableWidgetItem(state))
                    srow += 1
        else:
            self.tabWidget.setTabEnabled(0, False)

    def scan_wifi(self):
        self.dbus_call('net.connman', '/net/connman/technology/wifi', 'net.connman.Technology', 'Scan')

        # get managed services
        rdata = self.dbus_call('net.connman', '/', 'net.connman.Manager', 'GetServices')
        if rdata:
            srow = 1
            self.WiFiList.clearContents()
            for r in rdata.toStringList():
                data = r[1]
                if data.get('Type') == 'wifi':
                    name = data.get('Name')
                    strength = str(ord(data.get('Strength')))
                    security = misc.string_convert(data.get('Security'))
                    self.WiFiList.setRowCount(srow)
                    self.WiFiList.setItem(srow-1, 0, QtGui.QTableWidgetItem(name))
                    self.WiFiList.setItem(srow-1, 1, QtGui.QTableWidgetItem(strength))
                    self.WiFiList.setItem(srow-1, 2, QtGui.QTableWidgetItem(security))
                    srow += 1
        else:
            self.tabWidget.setTabEnabled(1, False)

    def details_ethernet(self):
        selection = self.EthernetList.selectedIndexes()
        if not selection:
            return
        sconnect = QtCore.QModelIndex(selection[0]).data()

        rdata = self.dbus_call('net.connman', '/', 'net.connman.Manager', 'GetServices')
        if rdata:
            for r in rdata.toStringList():
                data = r[1]
                name = data.get('Name')
                if name == sconnect:
                    message = ''
                    for d in data:
                        message += d + ': ' + str(data.get(d)) + '\n'
                    QtGui.QMessageBox.information(self, self.tr('Details'), message)
        else:
            self.tabWidget.setTabEnabled(1, False)

    def details_wifi(self):
        selection = self.WiFiList.selectedIndexes()
        if not selection:
            return
        sconnect = QtCore.QModelIndex(selection[0]).data()

        rdata = self.dbus_call('net.connman', '/', 'net.connman.Manager', 'GetServices')
        if rdata:
            for r in rdata.toStringList():
                data = r[1]
                name = data.get('Name')
                if name == sconnect:
                    message = ''
                    for d in data:
                        if d == 'Strength':
                            message += d + ': ' + str(ord(data.get(d))) + '\n'
                        else:
                            message += d + ': ' + str(data.get(d)) + '\n'
                    QtGui.QMessageBox.information(self, self.tr('Details'), message)
        else:
            self.tabWidget.setTabEnabled(1, False)

    def scan_any(self):
        if self.tabWidget.currentIndex() == 0:
            self.scan_ethernet()
        elif self.tabWidget.currentIndex() == 1:
            self.scan_wifi()

    def disconnect_any(self):
        if self.EthernetList.selectedIndexes():
            self.disconnect_ethernet()
        elif self.WiFiList.selectedIndexes():
            self.disconnect_wifi()

    def connect_any(self):
        if self.EthernetList.selectedIndexes():
            self.connect_ethernet()
        elif self.WiFiList.selectedIndexes():
            self.connect_wifi()

    def details_any(self):
        if self.EthernetList.selectedIndexes():
            self.details_ethernet()
        elif self.WiFiList.selectedIndexes():
            self.details_wifi()

    def enable_buttons(self):
        sethernet = QtCore.QModelIndex(ui.EthernetList.currentIndex()).data()
        swifi = QtCore.QModelIndex(ui.WiFiList.currentIndex()).data()

        self.detailsButton.setEnabled(False)
        self.disconnectButton.setEnabled(False)
        self.connectButton.setEnabled(False)

        if sethernet:
            self.detailsButton.setEnabled(True)
            rdata = self.dbus_call('net.connman', '/', 'net.connman.Manager', 'GetServices')
            if rdata:
                for r in rdata.toStringList():
                    data = r[1]
                    if data.get('Name') == sethernet:
                        if data.get('State') == 'online':
                            self.disconnectButton.setEnabled(True)
                        else:
                            self.connectButton.setEnabled(True)


        if swifi:
            self.detailsButton.setEnabled(True)
            rdata = self.dbus_call('net.connman', '/', 'net.connman.Manager', 'GetServices')
            if rdata:
                for r in rdata.toStringList():
                    data = r[1]
                    if data.get('Name') == swifi:
                        if data.get('State') == 'online':
                            self.disconnectButton.setEnabled(True)
                        else:
                            self.connectButton.setEnabled(True)

    @QtCore.pyqtSlot(QtDBus.QDBusMessage)
    def scan(self):
        self.scan_wifi()
        self.scan_ethernet()


class Plugin(QtCore.QObject):
    ''' Plugin handler '''
    def __init__(self, parent):
        super(Plugin, self).__init__()
        self.parent = parent
        self.name = 'network'
        self.version = '0.0.1'
        self.description = self.tr('Network manager plugin')
        self.icon = general.get_icon('network')
        self.widget = None

        self.networkButton = QtGui.QPushButton(self.icon, '')
        self.networkButton.clicked.connect(self.open)
        self.applicationsLayout = self.parent.toolBox.widget(1).layout()
        self.applicationsLayout.addWidget(self.networkButton)

    def open(self, spath):
        ''' Open path in new tab '''
        index = self.parent.tabWidget.currentIndex()+1
        self.widget = Widget(self.parent, spath)
        self.parent.tabWidget.insertTab(index, self.widget, self.icon, self.tr('Network'))
        self.parent.tabWidget.setCurrentIndex(index)

    def close(self, index=None):
        ''' Close tab '''
        if not index:
            index = self.parent.tabWidget.currentIndex()
        if self.widget:
            self.widget.deleteLater()
            self.widget = None
            self.parent.tabWidget.removeTab(index)

    def unload(self):
        ''' Unload plugin '''
        self.applicationsLayout.removeWidget(self.networkButton)
        self.close()
