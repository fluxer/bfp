#!/bin/pyhton2

# http://git.kernel.org/cgit/network/connman/connman.git/tree/doc

from PyQt4 import QtCore, QtGui, QtDBus
import os, libworkspace, libmisc
general = libworkspace.General()
misc = libmisc.Misc()


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
        self.EthernetList.setColumnCount(2)
        self.EthernetList.setHorizontalHeaderLabels(('Name', 'State'))
        self.EthernetList.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.EthernetList.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.WiFiList = QtGui.QTableWidget()
        self.WiFiList.setColumnCount(3)
        self.WiFiList.setHorizontalHeaderLabels(('Name', 'Strength', 'Security'))
        self.WiFiList.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.WiFiList.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tabWidget.insertTab(0, self.EthernetList, 'Ethernet')
        self.tabWidget.insertTab(1, self.WiFiList, 'WiFi')
        self.secondLayout = QtGui.QHBoxLayout()
        self.scanButton = QtGui.QPushButton(general.get_icon('edit-find'), '')
        self.connectButton = QtGui.QPushButton(general.get_icon('edit-redo'), '')
        self.disconnectButton = QtGui.QPushButton(general.get_icon('edit-undo'), '')
        self.detailsButton = QtGui.QPushButton(general.get_icon('document-properties'), '')
        self.tabWidget.currentChanged.connect(self.enable_buttons)
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

        self.scan_any()

        # FIXME: Nuitka can't deal with method decorators
        # self.bus.connect('net.connman', '/', 'net.connman.Manager', 'ServicesChanged', self.scan)
        # self.bus.connect('net.connman', '/', 'net.connman.Manager', 'TechnologyAdded', self.scan)
        # self.bus.connect('net.connman', '/', 'net.connman.Manager', 'TechnologyRemoved', self.scan)

        # because of the above, timer is installed to deal with state changes
        self.timer = QtCore.QTimer()
        self.timer.setInterval(5000)
        self.timer.timeout.connect(self.scan_any)
        self.timer.start()

    def dbus_call(self, spath, smethod, scall):
        interface = QtDBus.QDBusInterface('net.connman', spath, smethod, self.bus)
        if interface.isValid():
            result = interface.call(scall)
            reply = QtDBus.QDBusReply(result)
            if reply.isValid():
                return reply.value()
            else:
                QtGui.QMessageBox.critical(self, self.tr('Critical'), \
                    str(reply.error().message()))
                return False
        else:
            QtGui.QMessageBox.critical(self, self.tr('Critical'), \
                str(self.bus.lastError().message()))
            return False

    def technology_enabled(self, stech):
        result = self.dbus_call('/', 'net.connman.Manager', 'GetTechnologies')
        for tech in result:
            if tech[0] == ('/net/connman/technology/' + stech):
                return tech[1].get('Powered')
        return False

    def connect(self, name):
        self.dbus_call(name, 'net.connman.Service', 'Connect')
        self.parent.plugins.notify_information(self.tr('Connected to: %s' % os.path.basename(name)))

    def disconnect(self, name):
        self.dbus_call(name, 'net.connman.Service', 'Disconnect')
        self.parent.plugins.notify_information(self.tr('Disconnected from: %s' % os.path.basename(name)))

    def connect_ethernet(self):
        selection = self.EthernetList.selectedIndexes()
        if not selection:
            return
        sconnect = QtCore.QModelIndex(selection[0]).data()

        rdata = self.dbus_call('/', 'net.connman.Manager', 'GetServices')
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

        rdata = self.dbus_call('/', 'net.connman.Manager', 'GetServices')
        if rdata:
            for r in rdata:
                data = r[1]
                if data.get('Name') == sconnect:
                    self.connect(r[0])

    def disconnect_ethernet(self):
        selection = self.EthernetList.selectedIndexes()
        if not selection:
            return
        sconnect = QtCore.QModelIndex(selection[0]).data()

        rdata = self.dbus_call('/', 'net.connman.Manager', 'GetServices')
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

        rdata = self.dbus_call('/', 'net.connman.Manager', 'GetServices')
        if rdata:
            for r in rdata:
                data = r[1]
                if data.get('Name') == sconnect:
                    self.disconnect(r[0])

    def scan_ethernet(self):
        # self.dbus_call('/net/connman/technology/ethernet', 'net.connman.Technology', 'Scan')

        # get managed services
        rdata = self.dbus_call('/', 'net.connman.Manager', 'GetServices')
        if rdata:
            irow = 0
            self.EthernetList.clearContents()
            for r in rdata:
                data = r[1]
                if data.get('Type') == 'ethernet':
                    name = data.get('Name')
                    state = data.get('State')
                    self.EthernetList.setRowCount(irow+1)
                    self.EthernetList.setItem(irow, 0, QtGui.QTableWidgetItem(name))
                    self.EthernetList.setItem(irow, 1, QtGui.QTableWidgetItem(state))
                    irow += 1
        else:
            self.tabWidget.setTabEnabled(0, False)

    def scan_wifi(self):
        self.dbus_call('/net/connman/technology/wifi', 'net.connman.Technology', 'Scan')

        # get managed services
        rdata = self.dbus_call('/', 'net.connman.Manager', 'GetServices')
        if rdata:
            srow = 1
            self.WiFiList.clearContents()
            for r in rdata:
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

        rdata = self.dbus_call('/', 'net.connman.Manager', 'GetServices')
        if rdata:
            for r in rdata:
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

        rdata = self.dbus_call('/', 'net.connman.Manager', 'GetServices')
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
                    QtGui.QMessageBox.information(self, self.tr('Details'), message)
        else:
            self.tabWidget.setTabEnabled(1, False)

    def scan_any(self):
        if self.technology_enabled('ethernet'):
            self.tabWidget.setTabEnabled(0, True)
            self.scan_ethernet()
        else:
            self.tabWidget.setTabEnabled(0, False)

        if self.technology_enabled('wifi'):
            self.tabWidget.setTabEnabled(1, True)
            self.scan_wifi()
        else:
            self.tabWidget.setTabEnabled(1, False)
        self.enable_buttons()

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
        self.detailsButton.setEnabled(False)
        self.disconnectButton.setEnabled(False)
        self.connectButton.setEnabled(False)

        if self.tabWidget.currentIndex() == 0:
            sethernet = QtCore.QModelIndex(self.EthernetList.currentIndex()).data()
            if sethernet:
                self.detailsButton.setEnabled(True)
                rdata = self.dbus_call('/', 'net.connman.Manager', 'GetServices')
                if rdata:
                    for r in rdata:
                        data = r[1]
                        if data.get('Name') == sethernet:
                            if data.get('State') == 'online':
                                self.disconnectButton.setEnabled(True)
                            else:
                                self.connectButton.setEnabled(True)

        if self.tabWidget.currentIndex() == 1:
            swifi = QtCore.QModelIndex(self.WiFiList.currentIndex()).data()
            if swifi:
                self.detailsButton.setEnabled(True)
                rdata = self.dbus_call('/', 'net.connman.Manager', 'GetServices')
                if rdata:
                    for r in rdata:
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
        self.version = "0.9.31 (c43dd85)"
        self.description = self.tr('Network manager plugin')
        self.icon = general.get_icon('preferences-system-network')
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
