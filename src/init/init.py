#!/usr/bin/python

''' System initializer '''

import os, sys, time, subprocess, ConfigParser

import libmessage
message = libmessage.Message()
import libmisc
misc = libmisc.Misc()
import libservice


class MyInit(libservice.Init):
    ''' Custom initializer '''
    def loop(self):
        ''' Main loop '''
        # ensure only one instance
        if os.path.exists(self.ipc):
            message.critical('System initializer already running')
            sys.exit(2)

        message.info('Initializing system...')
        self.ipc_create()
        self.system_boot()
        while True:
            # read fifo every 0.5 seconds and do stuff
            service, action = self.ipc_read()
            if action == 'REBOOT':
                self.system_reboot()
            elif action == 'SHUTDOWN':
                self.system_shutdown()
            elif self.service_check(service) and action == 'START':
                self.service_start(service)
            elif self.service_check(service) and action == 'STOP':
                self.service_stop(service)
            elif self.service_check(service) and action == 'RESTART':
                self.service_start(service)
                self.service_stop(service)
            time.sleep(1)

# here we go
try:
    init = MyInit()
    init.loop()
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
    if os.path.isfile('/bin/shell'):
        message.warning('Running one time shell!')
        os.system('/bin/shell')
    sys.exit(1)
finally:
    if init.initialized and os.path.exists(init.ipc):
        os.remove(init.ipc)
