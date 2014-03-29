#!/usr/bin/python

''' System initializer '''

import os, sys, subprocess, ConfigParser, argparse

import libmessage
import libmisc
import libsystem
message = libmessage.Message()
misc = libmisc.Misc()
init = libsystem.System()

try:
    if not os.path.exists(init.ipc):
        message.critical('Init daemon is not running')
        sys.exit(2)

    parser = argparse.ArgumentParser(prog='initctl', description='Init Control')
    parser.add_argument('-a', '--start', action='store',
        help='Start service')
    parser.add_argument('-t', '--stop', action='store',
        help='Stop service')
    parser.add_argument('-R', '--restart', action='store',
        help='Restart service')
    parser.add_argument('-m', '--mount', action='store',
        help='Mount device')
    parser.add_argument('-u', '--unmount', action='store',
        help='Unmount device')
    parser.add_argument('-r', '--reboot', action='store_true',
        help='Reboot system')
    parser.add_argument('-s', '--shutdown', action='store_true',
        help='Halt system')
    parser.add_argument('-S', '--suspend', action='store_true',
        help='Suspend system')

    ARGS = parser.parse_args()
    if ARGS.start:
        misc.ipc_write(init.ipc, ARGS.start + '#START')
    elif ARGS.stop:
        misc.ipc_write(init.ipc, ARGS.stop + '#STOP')
    elif ARGS.restart:
        init.ipc_write(init.ipc, ARGS.restart + '#RESTART')
    elif ARGS.mount:
        misc.ipc_write(init.ipc, ARGS.mount + '#MOUNT')
    elif ARGS.unmount:
        misc.ipc_write(init.ipc, ARGS.unmount + '#UNMOUNT')
    elif ARGS.reboot:
        misc.ipc_write(init.ipc, '#REBOOT')
    elif ARGS.shutdown:
        misc.ipc_write(init.ipc, '#SHUTDOWN')
    elif ARGS.suspend:
        misc.ipc_write(init.ipc, '#SUSPEND')

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
except KeyboardInterrupt:
    message.critical('Interrupt signal received')
    sys.exit(7)
except SystemExit:
    sys.exit(2)
except Exception as detail:
    message.critical('Unexpected error', detail)
    sys.exit(1)
