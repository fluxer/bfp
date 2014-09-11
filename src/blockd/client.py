#!/bin/python2


import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

import sys, argparse
from PyQt4 import QtCore, QtDBus

app = QtCore.QCoreApplication(sys.argv)
bus = QtDBus.QDBusConnection.systemBus()
if not bus.isConnected():
    sys.stderr.write("Cannot connect to the D-Bus session bus.\n")
    sys.exit(1)

iface = QtDBus.QDBusInterface('com.blockd.Block', '/com/blockd/Block', \
    'com.blockd.Block', bus)

def dbus_call(method, args):
    if iface.isValid():
        result = iface.call(method, args)
        reply = QtDBus.QDBusReply(result)
        if reply.isValid():
            print(reply.value())
        else:
            print(str(reply.error().message()))
    else:
        print(str(bus.lastError().message()))

app_version = "0.9.38 (d6b9bbd)"

try:
    parser = argparse.ArgumentParser(prog='blockdctl', \
        description='Block daemon controller')
    parser.add_argument('-i', '--info', type=str, \
        help='Get information about block device')
    parser.add_argument('-m', '--mount', type=str, \
        help='Mount a block device')
    parser.add_argument('-u', '--unmount', type=str, \
        help='Unmount a block device')
    parser.add_argument('--debug', action='store_true', \
        help='Enable debug messages')
    parser.add_argument('--version', action='version', \
        version='blockdctl v' + app_version, \
        help='Show blockdctl version and exit')

    ARGS = parser.parse_args()

    if ARGS.info:
        dbus_call('Info', ARGS.info)
    elif ARGS.mount:
        dbus_call('Mount', ARGS.mount)
    elif ARGS.unmount:
        dbus_call('Unmount', ARGS.unmount)
    else:
        parser.print_help()

except OSError as detail:
    print('OS', detail)
    sys.exit(3)
except IOError as detail:
    print('IO', detail)
    sys.exit(4)
except KeyboardInterrupt:
    print('Interrupt signal received')
    sys.exit(5)
except SystemExit:
    sys.exit(2)
except Exception as detail:
    print('Unexpected error', detail)
    sys.exit(1)
#finally:
#    raise
