#!/usr/bin/python2


import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

import sys, argparse, time
from PyQt4 import QtCore, QtDBus
import libmessage
message = libmessage.Message()

app = QtCore.QCoreApplication(sys.argv)
bus = QtDBus.QDBusConnection.systemBus()
if not bus.isConnected():
    message.critical('Cannot connect to the D-Bus session bus')
    sys.exit(1)

iface = QtDBus.QDBusInterface('com.spm.Daemon', '/com/spm/Daemon', \
    'com.spm.Daemon', bus)

def dbus_call(method, args=None):
    if iface.isValid():
        if args:
            result = iface.asyncCall(method, args)
        else:
            result = iface.asyncCall(method)
        iface.connect(app, QtCore.SIGNAL('Finished(QString)'), message.sub_info)
        while True:
            result = iface.asyncCall('isWorking')
            reply = QtDBus.QDBusReply(result)
            if reply.value() == False:
                break
            time.sleep(1)
    else:
        message.sub_critical(str(bus.lastError().message()))

app_version = "1.8.0 (9496d16)"

try:
    parser = argparse.ArgumentParser(prog='spmctl', \
        description='SPM daemon controller')
    parser.add_argument('-r', '--remote', type=str, \
        help='Get remote target metadata')
    parser.add_argument('-l', '--local', type=str, \
        help='Get local target metadata')
    parser.add_argument('-s', '--sync', action='store_true', \
        help='Sync repositories')
    parser.add_argument('-b', '--build', nargs='+', type=str, \
        help='Build a package')
    parser.add_argument('-i', '--install', nargs='+', type=str, \
        help='Install a package')
    parser.add_argument('-R', '--remove', nargs='+', type=str, \
        help='Remove a package')
    parser.add_argument('--debug', action='store_true', \
        help='Enable debug messages')
    parser.add_argument('--version', action='version', \
        version='spmctl v' + app_version, \
        help='Show spmctl version and exit')

    ARGS = parser.parse_args()

    if ARGS.remote:
        dbus_call('RemoteInfo', ARGS.remote)
    elif ARGS.local:
        dbus_call('LocalInfo', ARGS.local)
    elif ARGS.sync:
        dbus_call('Sync')
    elif ARGS.build:
        dbus_call('Build', ARGS.build)
    elif ARGS.install:
        dbus_call('Install', ARGS.install)
    elif ARGS.remove:
        dbus_call('Remove', ARGS.remove)
    else:
        parser.print_help()

except OSError as detail:
    message.critical('OS', detail)
    sys.exit(3)
except IOError as detail:
    message.critical('IO', detail)
    sys.exit(4)
except KeyboardInterrupt:
    message.critical('Interrupt signal received')
    sys.exit(5)
except SystemExit:
    sys.exit(2)
except Exception as detail:
    message.critical('Unexpected error', detail)
    sys.exit(1)
finally:
    if not 'stable' in app_version and sys.exc_info()[0]:
        raise
