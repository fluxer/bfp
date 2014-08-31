#!/bin/pyhton2

from PyQt4 import QtCore, QtGui
import os, SimpleHTTPServer, SocketServer, libworkspace
general = libworkspace.General()


class Daemon(QtCore.QThread):
    def __init__(self, parent, address, port, path):
        super(Daemon, self).__init__()
        self.parent = parent
        self.address = address
        self.port = port
        self.path = path
        self.httpd = None

    def run(self):
        ''' Monitor block devices state '''
        try:
            os.chdir(self.path)
            handler = SimpleHTTPServer.SimpleHTTPRequestHandler
            self.httpd = SocketServer.TCPServer((self.address, self.port), handler)
            self.httpd.serve_forever()
        except Exception as detail:
            self.emit(QtCore.SIGNAL('failed'), str(detail))


class Widget(QtGui.QWidget):
    ''' Tab widget '''
    def __init__(self, parent, spath=None):
        super(Widget, self).__init__()
        self.parent = parent
        self.spath = spath
        self.name = 'server'

        self.mainLayout = QtGui.QGridLayout()
        self.addressEdit = QtGui.QLineEdit() # FIXME: store in settings
        self.addressEdit.setToolTip(self.tr('Address'))
        self.addressEdit.setPlaceholderText(self.tr('Address'))
        self.portBox = QtGui.QSpinBox()
        self.portBox.setMaximum(99999)
        self.portBox.setValue(8000) # FIXME: store in settings
        self.portBox.setToolTip(self.tr('Port'))
        self.directoryEdit = QtGui.QLineEdit()
        self.directoryEdit.setToolTip(self.tr('Directory to serve'))
        self.directoryEdit.setPlaceholderText(self.tr('Directory to serve'))
        self.startButton = QtGui.QPushButton(general.get_icon('system-run'), '')
        self.startButton.setToolTip(self.tr('Start server'))
        self.startButton.clicked.connect(self.server_start)
        self.stopButton = QtGui.QPushButton(general.get_icon('process-stop'), '')
        self.stopButton.setEnabled(False)
        self.stopButton.setToolTip(self.tr('Stop server'))
        self.stopButton.clicked.connect(self.server_stop)
        self.mainLayout.addWidget(self.addressEdit)
        self.mainLayout.addWidget(self.portBox)
        self.mainLayout.addWidget(self.directoryEdit)
        self.mainLayout.addWidget(self.startButton)
        self.mainLayout.addWidget(self.stopButton)
        self.setLayout(self.mainLayout)
        self.daemon = None

        if self.spath:
            self.server_start(self.spath)

    def server_start(self, spath=None):
        ''' Server wrapper '''
        if not self.directoryEdit.text():
            QtGui.QMessageBox.critical(self, self.tr('Critical'), \
                self.tr('No directory entered'))
            return
        elif not os.path.isdir(self.directoryEdit.text()):
            QtGui.QMessageBox.critical(self, self.tr('Critical'), \
                self.tr('The path entered is not directory'))
            return
        if not spath:
            spath = self.directoryEdit.text()
        try:
            self.daemon = Daemon(self.parent, self.addressEdit.text(), \
                self.portBox.value(), spath)
            self.connect(self.daemon, QtCore.SIGNAL('failed'), \
                self.parent.plugins.notify_critical)
            self.connect(self.daemon, QtCore.SIGNAL('failed'), \
                self.server_stop)
            self.daemon.start()
            self.startButton.setEnabled(False)
            self.stopButton.setEnabled(True)
        except Exception as detail:
            self.parent.plugins.notify_critical(str(detail))

    def server_stop(self):
        if self.daemon.httpd:
            self.daemon.httpd.shutdown()
        self.daemon.quit()
        self.daemon = None
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)

class Plugin(QtCore.QObject):
    ''' Plugin handler '''
    def __init__(self, parent):
        super(Plugin, self).__init__()
        self.parent = parent
        self.name = 'server'
        self.version = "0.9.36 (c166360)"
        self.description = self.tr('Server plugin')
        self.icon = general.get_icon('applications-geography')
        self.widget = None

        self.serverButton = QtGui.QPushButton(self.icon, '')
        self.serverButton.setToolTip(self.description)
        self.serverButton.clicked.connect(lambda: self.open(None))
        self.applicationsLayout = self.parent.toolBox.widget(1).layout()
        self.applicationsLayout.addWidget(self.serverButton)

    def open(self, spath):
        ''' Open path in new tab '''
        index = self.parent.tabWidget.currentIndex()+1
        self.widget = Widget(self.parent, spath)
        self.parent.tabWidget.insertTab(index, self.widget, self.icon, self.tr('Server'))
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
        self.applicationsLayout.removeWidget(self.serverButton)
        if self.widget and self.widget.daemon:
            self.widget.daemon.quit()
        self.close()
