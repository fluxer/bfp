#!/usr/bin/python2


import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

import sys, os
from PyQt4 import QtCore, QtDBus

app = QtCore.QCoreApplication(sys.argv)
bus = QtDBus.QDBusConnection.sessionBus()
if not bus.isConnected():
    sys.stderr.write("Cannot connect to the D-Bus session bus.\n")
    sys.exit(1)

iface = QtDBus.QDBusInterface('com.blockd.Block', '/com/blockd/Block', 'com.blockd.Block', bus)

def dbus_call(method, args):
    if iface.isValid():
        result = iface.call(method, args)
        reply = QtDBus.QDBusReply(result)
        if reply.isValid():
            print(reply.value(), result)
        else:
            print(str(reply.error().message()))
    else:
        print(str(bus.lastError().message()))

class connector(QtCore.QObject):
    def __init__(self, parent=None):
        super(connector, self).__init__(parent)

    @QtCore.pyqtSlot(str)
    def add_connect(msg):
        print(msg)

    @QtCore.pyqtSlot(str)
    def remove_connect(msg):
        print(msg)

dbus_call('Info', '/dev/sdb4')
con = connector()
bus.connect('com.blockd.Block', '/com/blockd/Block', 'com.blockd.Block', 'Add', con.add_connect)
bus.connect('com.blockd.Block', '/com/blockd/Block', 'com.blockd.Block', 'Remove', con.remove_connect)


sys.exit(app.exec_())
