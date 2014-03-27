#!/usr/bin/python2

import sys
import ConfigParser
import subprocess
import re
import os, time

import libmisc
import libmessage
import libpower
message = libmessage.Message()
misc = libmisc.Misc()
power = libpower.Power()


app_version = "0.0.8 (90d7e1e)"

if not os.path.isfile('/etc/powerd.conf'):
    message.warning('Configuration file does not exist', '/etc/powerd.comf')

    REBOOT_PRE = None

    SHUTDOWN_PRE = None

    SUSPEND_PRE = None
    SUSPEND_DISK = 'platform'
    SUSPEND_STATE = 'mem'
    SUSPEND_POST = None

    MOUNT_PRE = None
    MOUNT_POST = None

    UNMOUNT_PRE = None
    UNMOUNT_POST = None

    BATTERY_LID = 'shutdown'
    BATTERY_LOW = 'suspend'
    BATTERY_CPU = 'ondemand'
    BATTERY_BACKLIGHT = '10'

    POWER_LID = 'suspend'
    POWER_CPU = 'performance'
    POWER_BACKLIGHT = '15'
else:
    conf = ConfigParser.SafeConfigParser()
    conf.read('/etc/powerd.conf')

    REBOOT_PRE = conf.get('reboot', 'pre')

    SHUTDOWN_PRE = conf.get('shutdown', 'pre')

    SUSPEND_PRE = conf.get('suspend', 'pre')
    SUSPEND_DISK = conf.get('suspend', 'disk')
    SUSPEND_STATE = conf.get('suspend', 'state')
    SUSPEND_POST = conf.get('suspend', 'post')

    MOUNT_PRE = conf.get('mount', 'pre')
    MOUNT_POST = conf.get('mount', 'post')

    UNMOUNT_PRE = conf.get('unmount', 'pre')
    UNMOUNT_POST = conf.get('unmount', 'post')

    BATTERY_LID = conf.get('battery', 'lid')
    BATTERY_LOW = conf.get('battery', 'low')
    BATTERY_CPU = conf.get('battery', 'cpu')
    BATTERY_BACKLIGHT = conf.get('battery', 'backlight')

    POWER_LID = conf.get('power', 'lid')
    POWER_CPU = conf.get('power', 'cpu')
    POWER_BACKLIGHT = conf.get('power', 'backlight')

try:
    if not os.geteuid() == 0:
        message.critical('You are not root')
    else:
        # FIXME: lock
        message.info('Initializing power daemon...')
        import glib
        import dbus, dbus.service, dbus.mainloop.glib

        class PowerdObject(dbus.service.Object):
            def __init__(self, conn, object_path):
                dbus.service.Object.__init__(self, conn, object_path)

            @dbus.service.signal('org.powerd.Interface')
            def NotifyPower(self, state):
                return str(state)

            @dbus.service.signal('org.powerd.Interface')
            def NotifyLid(self, state):
                return str(state)

            @dbus.service.signal('org.powerd.Interface')
            def NotifyLow(self, capacity):
                return int(capacity)

            @dbus.service.method('org.powerd.Interface', in_signature='', out_signature='')
            def Reboot(self):
                power.do_reboot()

            @dbus.service.method('org.powerd.Interface', in_signature='', out_signature='')
            def Shutdown(self):
                power.do_shutdown()

            @dbus.service.method('org.powerd.Interface', in_signature='', out_signature='')
            def Suspend(self):
                power.do_suspend()

            @dbus.service.method('org.powerd.Interface', in_signature='', out_signature='')
            def Ping(self):
                message.sub_info('Ping')

            @dbus.service.method('org.powerd.Interface', in_signature='', out_signature='')
            def Exit(self):
                message.info('Exiting daemon...')
                global pool
                mainloop.quit()
                pool.close()
                pool.terminate()

        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        system_bus = dbus.SystemBus()
        power_name = dbus.service.BusName('org.powerd.PowerD', system_bus)
        power_obj = PowerdObject(system_bus, '/org/powerd/PowerD')

        def monitor_lid():
            message.sub_info('Monitoring LID state')
            if not os.path.exists('/proc/acpi/button/lid/LID/state'):
                message.sub_warning('No LID support')
                return
            while True:
                before = power.check_lid_status()
                time.sleep(2)
                after = power.check_lid_status()
                if not before == after:
                    message.sub_debug('LID status changed', after)
                    power_obj.NotifyLid(after)
                    if after == 'closed' and power.LID_VALUE == 'suspend':
                        power.do_suspend()
                    elif after == 'closed' and power.LID_VALUE == 'shutdown':
                        power.do_shutdown()
                    elif after == 'closed':
                        message.sub_warning('Invalid value for LID action', power.LID_VALUE)
                        power.do_suspend()

        def monitor_power():
            message.sub_info('Monitoring power state')
            while True:
                before = power.check_power_supply()
                time.sleep(2)
                after = power.check_power_supply()
                if not before == after:
                    power_obj.NotifyPower(after)
                    if after == 'DC':
                        power.LID_VALUE = BATTERY_LID
                        power.CPU_VALUE = BATTERY_CPU
                        power.BACKLIGHT_VALUE = BATTERY_BACKLIGHT
                        capacity = int(power.check_battery_capacity())
                        if capacity < 15:
                            message.sub_warning('Low battery', capacity)
                            power_obj.NotifyLow(capacity)
                            if BATTERY_LOW == 'suspend':
                                power.do_suspend()
                            elif BATTERY_LOW == 'shutdown':
                                power.do_shutdown()
                            else:
                                message.sub_warning('Invalid action for low battery',
                                    BATTERY_LOW)
                                power.do_suspend()
                    else:
                        power.LID_VALUE = POWER_LID
                        power.CPU_VALUE = POWER_CPU
                        power.BACKLIGHT_VALUE = POWER_BACKLIGHT
                power.do_cpu_governor()
                power.do_backlight()
                time.sleep(2)

        glib.threads_init()
        mainloop = glib.MainLoop()

        from multiprocessing import Pool
        pool = Pool(2)
        pool.apply_async(monitor_lid)
        pool.apply_async(monitor_power)
        mainloop.run()

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
    sys.exit(8)
except SystemExit:
    sys.exit(2)
except Exception as detail:
    message.critical('Unexpected error', detail)
    sys.exit(1)
#finally:
#    raise
