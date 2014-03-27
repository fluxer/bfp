#!/usr/bin/python2

# http://qt-project.org/doc/qt-4.8/qstyle.html#StandardPixmap-enum
# http://standards.freedesktop.org/icon-naming-spec/icon-naming-spec-latest.html

import sys, os
from PyQt4 import QtCore, QtGui, QtDBus

class SystemTrayIcon(QtGui.QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        QtGui.QSystemTrayIcon.__init__(self, icon, parent)
        self.parent = parent
        self.systembus = QtDBus.QDBusConnection.systemBus()
        self.iface = QtDBus.QDBusInterface('org.mountd.MountD', '/org/mountd/MountD',
            'org.mountd.Interface', self.systembus)
        self.systembus.connect('org.mountd.MountD', '/org/mountd/MountD',
            'org.mountd.Interface', 'NotifyMount', self.AddDevice)
        self.systembus.connect('org.mountd.MountD', '/org/mountd/MountD',
            'org.mountd.Interface', 'NotifyUnmount', self.RemoveDevice)
        self.GenerateMenu()

    def GenerateMenu(self):
        ''' Generate tray menu based on devices available '''
        self.menu = QtGui.QMenu(self.parent)

        for dev in os.listdir('/dev/disk/by-uuid'):
            device = os.path.join('/dev/disk/by-uuid', dev)
            if os.path.ismount('/media/' + dev):
                entry = self.menu.addAction(QtGui.QIcon.fromTheme('media-eject'), dev)
                self.connect(entry, QtCore.SIGNAL('triggered()'),
                    lambda device=device: self.UnmountDevice(device))
            else:
                entry = self.menu.addAction(QtGui.QIcon.fromTheme('drive-removable-media'), dev)
                self.connect(entry, QtCore.SIGNAL('triggered()'),
                    lambda device=device: self.MountDevice(device))

        self.menu.addSeparator()
        self.menu.addAction(QtGui.QIcon.fromTheme('system-run'), 'Ping', self.Ping)
        self.menu.addAction(QtGui.QIcon.fromTheme('process-stop'), 'Kill', self.Kill)
        self.menu.addAction(QtGui.QIcon.fromTheme('application-exit'), 'Exit', sys.exit)
        self.setContextMenu(self.menu)

    def ErrorMessage(self, message):
        ''' Pop an error message '''
        QtGui.QMessageBox.critical(QtGui.QWidget(), 'Mount controller', message)
        sys.stderr.write(message)

    def Ping(self):
        ''' Wake up mount daemon '''
        msg = self.iface.call('Ping')
        reply = QtDBus.QDBusReply(msg)
        if not reply.isValid():
            self.ErrorMessage(reply.error().message())

    def Kill(self):
        ''' Exit mount daemon '''
        msg = self.iface.call('Exit')
        reply = QtDBus.QDBusReply(msg)
        if not reply.isValid():
            self.ErrorMessage(reply.error().message())

    @QtCore.pyqtSlot(str)
    def AddDevice(self, device):
        ''' Add device to the menu, called upon mount daemon notification '''
        self.GenerateMenu()
        self.BrowseDevice(str(device))

    @QtCore.pyqtSlot(str)
    def RemoveDevice(self, device):
        ''' Remove device from the menu, called upon mount daemon notification '''
        self.GenerateMenu()

    def BrowseDevice(self, device):
        ''' Browse mounted device with file-manager '''
        os.system('xdg-open /media/' + os.path.basename(device))

    def MountDevice(self, device):
        ''' Mount device and regenerate menu '''
        msg = self.iface.call('Mount', device)
        reply = QtDBus.QDBusReply(msg)
        if not reply.isValid():
            self.ErrorMessage(reply.error().message())
        self.GenerateMenu()

    def UnmountDevice(self, device):
        ''' Unmount device and regenerate menu '''
        msg = self.iface.call('Unmount', device)
        reply = QtDBus.QDBusReply(msg)
        if not reply.isValid():
            self.ErrorMessage(reply.error().message())
        self.GenerateMenu()

app = QtGui.QApplication(sys.argv)
style = app.style()
trayIcon = SystemTrayIcon(QtGui.QIcon.fromTheme('preferences-system'))
trayIcon.show()
sys.exit(app.exec_())
