#!/usr/bin/python

''' System initializer '''

import sys, subprocess, ConfigParser, argparse

import libmessage
message = libmessage.Message()
import libmisc
misc = libmisc.Misc()
import libservice

try:
    init = libservice.Service()
    parser = argparse.ArgumentParser(prog='initctl', description='Init Control')
    parser.add_argument('-a', '--start', action='store',
        help='Start service')
    parser.add_argument('-t', '--stop', action='store',
        help='Stop service')
    parser.add_argument('-R', '--restart', action='store',
        help='Restart service')
    parser.add_argument('-r', '--reboot', action='store_true',
        help='Reboot system')
    parser.add_argument('-s', '--shutdown', action='store_true',
        help='Halt system')

    ARGS = parser.parse_args()
    if ARGS.start:
        misc.ipc_write(init.ipc, ARGS.start + '#START')
    elif ARGS.stop:
        misc.ipc_write(init.ipc, ARGS.stop + '#STOP')
    elif ARGS.restart:
        init.ipc_write(init.ipc, ARGS.restart + '#RESTART')
    elif ARGS.reboot:
        misc.ipc_write(init.ipc, '#REBOOT')
    elif ARGS.shutdown:
        misc.ipc_write(init.ipc, '#SHUTDOWN')

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
