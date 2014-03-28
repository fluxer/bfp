#!/usr/bin/python

''' System initializer '''

import os, sys, time, subprocess, ConfigParser

import libmessage
message = libmessage.Message()
import libmisc
misc = libmisc.Misc()
import libservice


class MyService(libservice.Service):
    ''' Custom initializer '''
    def loop(self):
        ''' Main loop '''
        if os.path.exists(self.ipc):
            message.critical('Init daemon already running')
            sys.exit(2)

        message.info('Initializing system...')
        misc.ipc_create(self.ipc, 20)
        os.setsid()
        # to ensure fifo cleanup only from the running daemon not
        # possible second instance variable is asigned
        self.initialized = True
        self.system_boot()
        while True:
            content = misc.ipc_read(self.ipc)
            service = None
            action = None
            if content:
                service, action = content.split('#')

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
            time.sleep(2)

# here we go
try:
    init = MyService()
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
