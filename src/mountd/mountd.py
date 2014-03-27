#!/usr/bin/python2

import sys
import ConfigParser
import subprocess
import re
import os, time

import libmisc
import libmessage
import libdevice
message = libmessage.Message()
misc = libmisc.Misc()
device = libdevice.Device()


app_version = "0.0.8 (90d7e1e)"

if not os.path.isfile('/etc/mountd.conf'):
    message.warning('Configuration file does not exist', '/etc/mountd.comf')
    MOUNT_PRE = None
    MOUNT_POST = None

    UNMOUNT_PRE = None
    UNMOUNT_POST = None
else:
    conf = ConfigParser.SafeConfigParser()
    conf.read('/etc/mountd.conf')

    MOUNT_PRE = conf.get('mount', 'pre')
    MOUNT_POST = conf.get('mount', 'post')

    UNMOUNT_PRE = conf.get('unmount', 'pre')
    UNMOUNT_POST = conf.get('unmount', 'post')

try:
    if not os.geteuid() == 0:
        message.critical('You are not root')
    else:
        # FIXME: lock
        message.info('Initializing mount daemon...')
        import glib
        import dbus, dbus.service, dbus.mainloop.glib

        class MountObject(dbus.service.Object):
            def __init__(self, conn, object_path):
                dbus.service.Object.__init__(self, conn, object_path)

            @dbus.service.signal('org.mountd.Interface')
            def NotifyMount(self, sdevice):
                return str(sdevice)

            @dbus.service.signal('org.mountd.Interface')
            def NotifyUnmount(self, sdevice):
                return str(sdevice)

            @dbus.service.method('org.mountd.Interface', in_signature='s', out_signature='')
            def Mount(self, sdevice):
                device.do_mount(str(sdevice))
                self.NotifyMount(str(sdevice))

            @dbus.service.method('org.mountd.Interface', in_signature='s', out_signature='')
            def Unmount(self, sdevice):
                device.do_unmount(str(sdevice))
                self.NotifyUnmount(str(sdevice))

            @dbus.service.method('org.mountd.Interface', in_signature='', out_signature='')
            def Ping(self):
                message.sub_info('Ping')

            @dbus.service.method('org.mountd.Interface', in_signature='', out_signature='')
            def Exit(self):
                message.info('Exiting daemon...')
                global pool
                mainloop.quit()
                pool.close()
                pool.terminate()

        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        system_bus = dbus.SystemBus()
        mount_name = dbus.service.BusName('org.mountd.MountD', system_bus)
        mount_obj = MountObject(system_bus, '/org/mountd/MountD')

        def monitor_disks():
            message.sub_info('Monitoring disks')
            while True:
                before = os.listdir('/dev/disk/by-uuid')
                time.sleep(2)
                after = os.listdir('/dev/disk/by-uuid')
                for f in after:
                    if '.tmp' in f:
                        continue
                    if not f in before:
                        mount_obj.Mount(os.path.join('/dev/disk/by-uuid', f))
                for f in before:
                    if '.tmp' in f:
                        continue
                    if not f in after:
                        mount_obj.Unmount(os.path.join('/dev/disk/by-uuid', f))

        glib.threads_init()
        mainloop = glib.MainLoop()

        from multiprocessing import Pool
        pool = Pool(1)
        pool.apply_async(monitor_disks)
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
