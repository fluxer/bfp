#!/usr/bin/python

''' System initializer '''

import os, sys, time, subprocess, ConfigParser, threading

import libmessage
message = libmessage.Message()
import libmisc
misc = libmisc.Misc()
import libsystem

if not os.path.isfile('/etc/system.conf'):
    message.warning('Configuration file does not exist', '/etc/system.comf')

    BATTERY_LID = 'shutdown'
    BATTERY_LOW = 'suspend'
    BATTERY_CPU = 'ondemand'
    BATTERY_BACKLIGHT = '10'
    POWER_LID = 'suspend'
    POWER_CPU = 'performance'
    POWER_BACKLIGHT = '15'

    MOUNT_PRE = None
    MOUNT_POST = None
    UNMOUNT_PRE = None
    UNMOUNT_POST = None

    REBOOT_PRE = None
    SHUTDOWN_PRE = None
    SUSPEND_PRE = None
    SUSPEND_DISK = 'platform'
    SUSPEND_STATE = 'mem'
    SUSPEND_POST = None
else:
    conf = ConfigParser.SafeConfigParser()
    conf.read('/etc/system.conf')

    BATTERY_LID = conf.get('battery', 'lid')
    BATTERY_LOW = conf.get('battery', 'low')
    BATTERY_CPU = conf.get('battery', 'cpu')
    BATTERY_BACKLIGHT = conf.get('battery', 'backlight')
    POWER_LID = conf.get('power', 'lid')
    POWER_CPU = conf.get('power', 'cpu')
    POWER_BACKLIGHT = conf.get('power', 'backlight')

    MOUNT_PRE = conf.get('mount', 'pre')
    MOUNT_POST = conf.get('mount', 'post')
    UNMOUNT_PRE = conf.get('unmount', 'pre')
    UNMOUNT_POST = conf.get('unmount', 'post')

    REBOOT_PRE = conf.get('reboot', 'pre')
    SHUTDOWN_PRE = conf.get('shutdown', 'pre')
    SUSPEND_PRE = conf.get('suspend', 'pre')
    SUSPEND_DISK = conf.get('suspend', 'disk')
    SUSPEND_STATE = conf.get('suspend', 'state')
    SUSPEND_POST = conf.get('suspend', 'post')

class MySystem(libsystem.System):
    ''' Custom initializer '''
    def system_initialize(self):
        ''' Initialize system '''
        message.info('Initializing system')
        os.setsid()
        misc.ipc_create(self.ipc, 20)
        # to ensure fifo cleanup only from the running daemon not
        # possible second instance variable is asigned
        self.initialized = True
        self.do_boot()

    def monitor_lid(self):
        ''' Monitor LID state '''
        message.sub_info('Monitoring LID state')
        if not os.path.exists('/proc/acpi/button/lid/LID/state'):
            message.sub_warning('No LID support')
            return
        while not self.stop:
            before = self.check_lid_status()
            time.sleep(2)
            after = self.check_lid_status()
            if not before == after:
                message.sub_debug('LID status changed', after)
                if after == 'closed' and self.LID_VALUE == 'suspend':
                    self.do_suspend()
                elif after == 'closed' and self.LID_VALUE == 'shutdown':
                    self.do_shutdown()
                elif after == 'closed':
                    message.sub_warning('Invalid value for LID action', self.LID_VALUE)
                    self.do_suspend()

    def monitor_power(self):
        ''' Monitor power state '''
        message.sub_info('Monitoring power state')
        while not self.stop:
            before = self.check_power_supply()
            time.sleep(2)
            after = self.check_power_supply()
            if not before == after:
                message.sub_debug('Power state changed', after)
                if after == 'DC':
                    self.LID_VALUE = BATTERY_LID
                    self.CPU_VALUE = BATTERY_CPU
                    self.BACKLIGHT_VALUE = BATTERY_BACKLIGHT
                    capacity = self.check_battery_capacity()
                    if capacity < 15:
                        message.sub_warning('Low battery', capacity)
                        if BATTERY_LOW == 'suspend':
                            self.do_suspend()
                        elif BATTERY_LOW == 'shutdown':
                            self.do_shutdown()
                        else:
                            message.sub_warning('Low battery', BATTERY_LOW)
                else:
                    self.LID_VALUE = POWER_LID
                    self.CPU_VALUE = POWER_CPU
                    self.BACKLIGHT_VALUE = POWER_BACKLIGHT
                self.do_cpu_governor()
                self.do_backlight()

    def monitor_devices(self):
        ''' Monitor devices state '''
        message.sub_info('Monitoring devices state')
        while not self.stop:
            before = os.listdir('/dev/disk/by-uuid')
            time.sleep(2)
            after = os.listdir('/dev/disk/by-uuid')
            for f in after:
                if '.tmp' in f:
                    continue
                if not f in before:
                    self.do_mount(os.path.join('/dev/disk/by-uuid', f))
            for f in before:
                if '.tmp' in f:
                    continue
                if not f in after:
                    self.do_unmount(os.path.join('/dev/disk/by-uuid', f))
            time.sleep(2)

    def loop(self):
        ''' Main loop '''
        while not self.stop:
            content = misc.ipc_read(self.ipc)
            string = None
            action = None
            if content:
                string, action = content.split('#')

            if action == 'REBOOT':
                self.do_reboot()
            elif action == 'SHUTDOWN':
                self.do_shutdown()
            elif action == 'SUSPEND':
                self.do_suspend()
            elif action == 'RELOAD':
                reload(libmessage)
                reload(libmisc)
                reload(libsystem)
                self.__init__()
            elif string and self.service_check(string) and action == 'START':
                self.service_start(string)
            elif string and self.service_check(string) and action == 'STOP':
                self.service_stop(string)
            elif string and self.service_check(string) and action == 'RESTART':
                self.service_start(string)
                self.service_stop(string)
            elif string and action == 'MOUNT':
                self.do_mount(string)
            elif string and action == 'UNMOUNT':
                self.do_unmount(string)
            elif action == 'EXIT':
                break
            time.sleep(2)

# here we go
try:
    init = MySystem()
    init.stop = False
    if os.path.exists(init.ipc):
        message.critical('Init daemon already running')
        sys.exit(2)

    init.system_initialize()

    #t1 = threading.Thread(target=init.monitor_lid)
    t2 = threading.Thread(target=init.monitor_power)
    t3 = threading.Thread(target=init.monitor_devices)
    t4 = threading.Thread(target=init.loop)

    #t1.start()
    t2.start()
    t3.start()
    t4.start()
    t4.join()
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
    if not init.initialized and os.path.isfile('/bin/shell'):
        message.warning('Running one time shell!')
        os.system('/bin/shell')
    sys.exit(1)
finally:
    if init.initialized and os.path.exists(init.ipc):
        os.remove(init.ipc)
    init.stop = True
