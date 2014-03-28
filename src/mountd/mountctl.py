#!/usr/bin/python2

import os
import sys
import argparse
import ConfigParser
import subprocess
import re

import libmisc
import libmessage
import libdevice
message = libmessage.Message()
misc = libmisc.Misc()
device = libdevice.Device()


try:
    if not os.path.exists(device.ipc):
        message.critical('Mount daemon is not running')
        sys.exit(2)

    parser = argparse.ArgumentParser(prog='mountctl', description='Mount Control')
    parser.add_argument('-m', '--mount', action='store',
        help='Mount device')
    parser.add_argument('-u', '--unmount', action='store',
        help='Unmount device')
    parser.add_argument('-e', '--exit', action='store_true',
        help='Kill mount daemon')

    ARGS = parser.parse_args()
    if ARGS.mount:
        misc.ipc_write(device.ipc, ARGS.mount + '#MOUNT')
    elif ARGS.unmount:
        misc.ipc_write(device.ipc, ARGS.unmount + '#UNMOUNT')
    elif ARGS.exit:
        misc.ipc_write(device.ipc, '#EXIT')

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
