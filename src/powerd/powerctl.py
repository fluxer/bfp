#!/usr/bin/python2

import sys
import argparse
import ConfigParser
import subprocess
import re
from dbus import SystemBus, Interface, DBusException

app_version = "0.0.8 (90d7e1e)"

try:
    import libmessage
    message = libmessage.Message()

    bus = SystemBus()
    remote_object = bus.get_object('org.powerd.PowerD', '/org/powerd/PowerD')
    iface = Interface(remote_object, 'org.powerd.Interface')

    parser = argparse.ArgumentParser(prog='powerctl', description='Power Control')
    parser.add_argument('-r', '--reboot', action='store_true',
        help='Reboot system')
    parser.add_argument('-s', '--shutdown', action='store_true',
        help='Halt system')
    parser.add_argument('-S', '--suspend', action='store_true',
        help='Suspend system')
    parser.add_argument('-m', '--mount', action='store',
        help='Mount device')
    parser.add_argument('-u', '--unmount', action='store',
        help='Unmount device')
    parser.add_argument('-p', '--ping', action='store_true',
        help='Wakeup power daemon')
    parser.add_argument('-e', '--exit', action='store_true',
        help='Kill power daemon')
    parser.add_argument('-v', '--version', action='version',
        version='Power Control v' + app_version,
        help='Show Power Control version and exit')

    ARGS = parser.parse_args()
    if ARGS.reboot:
        iface.Reboot()
    elif ARGS.shutdown:
        iface.Shutdown()
    elif ARGS.suspend:
        iface.Suspend()
    elif ARGS.mount:
        iface.Mount(ARGS.mount)
    elif ARGS.unmount:
        iface.Unmount(ARGS.unmount)
    elif ARGS.ping:
        iface.Ping()
    elif ARGS.exit:
        iface.Exit()

except ConfigParser.Error as detail:
    message.critical('CONFIGPARSER', detail)
    sys.exit(3)
except subprocess.CalledProcessError as detail:
    message.critical('SUBPROCESS', detail)
    sys.exit(4)
except OSError as detail:
    message.critical('OS', detail)
    sys.exit(5)
except IOError as detail:
    message.critical('IO', detail)
    sys.exit(6)
except re.error as detail:
    message.critical('REGEXP', detail)
    sys.exit(7)
except DBusException as detail:
    message.critical('DBUS', detail)
    sys.exit(8)
except KeyboardInterrupt:
    message.critical('Interrupt signal received')
    sys.exit(9)
except SystemExit:
    sys.exit(2)
except Exception as detail:
    message.critical('Unexpected error', detail)
    sys.exit(1)
#finally:
#    raise
