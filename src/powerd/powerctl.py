#!/usr/bin/python2

import os
import sys
import argparse
import ConfigParser
import subprocess
import re

import libmisc
import libmessage
import libpower
message = libmessage.Message()
misc = libmisc.Misc()
power = libpower.Power()

try:
    if not os.path.exists(power.ipc):
        message.critical('Power daemon is not running')
        sys.exit(2)

    parser = argparse.ArgumentParser(prog='powerctl', description='Power Control')
    parser.add_argument('-r', '--reboot', action='store_true',
        help='Reboot system')
    parser.add_argument('-s', '--shutdown', action='store_true',
        help='Halt system')
    parser.add_argument('-S', '--suspend', action='store_true',
        help='Suspend system')
    parser.add_argument('-e', '--exit', action='store_true',
        help='Kill power daemon')

    ARGS = parser.parse_args()
    if ARGS.reboot:
        misc.ipc_write(power.ipc, ARGS.mount + 'REBOOT')
    elif ARGS.shutdown:
        misc.ipc_write(power.ipc, ARGS.mount + 'SHUTDOWN')
    elif ARGS.suspend:
        misc.ipc_write(power.ipc, ARGS.mount + 'SUSPEND')
    elif ARGS.exit:
        misc.ipc_write(power.ipc, ARGS.mount + 'EXIT')

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
