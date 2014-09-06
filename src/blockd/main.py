#!/bin/python2

import libudev, time, os, libsystem, threading
import gobject, dbus, dbus.service, dbus.mainloop.glib

system = libsystem.System()
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
session_bus = dbus.SessionBus()

class QMount(dbus.service.Object):
    def __init__(self, conn, object_path='/com/blockd/Block'):
        dbus.service.Object.__init__(self, conn, object_path)
        self.udev = libudev.udev_new()
        if not self.udev:
            raise(Exception('Can not get udev context'))

    @dbus.service.signal('com.blockd.Block')
    def Add(self, info):
        print("Added", info.splitlines())
        return info

    @dbus.service.signal('com.blockd.Block')
    def Remove(self, info):
        print("Removed", info.splitlines())
        return info

    @dbus.service.signal('com.blockd.Block')
    def Change(self, info):
        print("Changed", info.splitlines())
        return info

    @dbus.service.signal('com.blockd.Block')
    def Unknown(self, info):
        print("Unknown", info.splitlines())
        return info

    @dbus.service.method("com.blockd.Block", in_signature='s', out_signature='s')
    def Info(self, devname):
        devname = str(devname)
        val = ''
        print('Info about %s requested' % devname)
        dev = libudev.udev_device_new_from_syspath(self.udev, \
            '/sys/class/block/' + os.path.basename(devname))
        try:
            name = libudev.udev_device_get_property_value(dev, "DEVNAME")
            action = libudev.udev_device_get_action(dev)
            label = libudev.udev_device_get_property_value(dev, "ID_FS_LABEL")
            fstype = libudev.udev_device_get_property_value(dev, "ID_FS_TYPE")
            fsusage = libudev.udev_device_get_property_value(dev, "ID_FS_USAGE")
            fsuuid = libudev.udev_device_get_property_value(dev, "ID_FS_UUID")
            tabletype = libudev.udev_device_get_property_value(dev, "ID_PART_TABLE_TYPE")
            tablename = libudev.udev_device_get_property_value(dev, "ID_PART_TABLE_NAME")
            entrytype = libudev.udev_device_get_property_value(dev, "ID_PART_ENTRY_TYPE")
            dmname = libudev.udev_device_get_property_value(dev, "DM_NAME")
            dmlevel = libudev.udev_device_get_property_value(dev, "DM_LEVEL")
            val = '%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s' % \
                (name, action, label, fstype, fsusage, fsuuid, tabletype, \
                tablename, entrytype, dmname, dmlevel)
        finally:
            libudev.udev_device_unref(dev)
        return val

    @dbus.service.method("com.blockd.Block", in_signature='ss', out_signature='s')
    def Property(self, devname, prop):
        devname = str(devname)
        prop = str(prop)
        print('Property of %s requested: %s' % (devname, prop))
        val = None
        dev = libudev.udev_device_new_from_syspath(self.udev, \
            '/sys/class/block/' + os.path.basename(devname))
        try:
            val = libudev.udev_device_get_property_value(dev, prop)
        finally:
            libudev.udev_device_unref(dev)
        return val

    @dbus.service.method("com.blockd.Block", in_signature='s', out_signature='b')
    def CheckMounted(self, devname):
        if not system.check_mounted(devname):
            print("%s is not mounted" % devname)
            return False
        print("%s is mounted" % devname)
        return True

    @dbus.service.method("com.blockd.Block", in_signature='s', out_signature='s')
    def Mount(self, devname):
        if not self.Property(devname, "ID_FS_TYPE"):
            print("No filesystem on %s" % devname)
            return("No filesystem on %s" % devname)

        print("Mounting", devname)
        return str(system.do_mount(devname))

    @dbus.service.method("com.blockd.Block", in_signature='s', out_signature='s')
    def Unmount(self, devname):
        if not system.check_mounted(devname):
            print("%s is not mounted" % devname)
            return("%s is not mounted" % devname)

        print("Unmounting %s" % devname)
        return str(system.do_unmount(devname))

    @dbus.service.method("com.blockd.Block", in_signature='', out_signature='')
    def Exit(self):
        loop.quit()

    def Daemon(self):
        try:
            monitor = libudev.udev_monitor_new_from_netlink(self.udev, "udev");
            libudev.udev_monitor_filter_add_match_subsystem_devtype(monitor, "block", None)
            libudev.udev_monitor_enable_receiving(monitor)

            while True:
                if monitor:
                    fd = libudev.udev_monitor_get_fd(monitor)

                if monitor and fd:
                    dev = libudev.udev_monitor_receive_device(monitor)
                    if dev:
                        name = libudev.udev_device_get_property_value(dev, "DEVNAME")
                        action = libudev.udev_device_get_action(dev)
                        libudev.udev_device_unref(dev)
                        if action == 'add':
                            self.Add(self.Info(name))
                        elif action == 'remove':
                            self.Remove(self.Info(name))
                        elif action == 'change':
                            self.Change(self.Info(name))
                        else:
                            self.Unknown(self.Info(name))
                    time.sleep(1)
        except Exception as detail:
            print(str(detail))
        finally:
            libudev.udev_unref(self.udev)

try:
    object = QMount(session_bus)
    thread = threading.Thread(target=object.Daemon)
    thread.start()
    name = dbus.service.BusName('com.blockd.Block', session_bus)
    loop = gobject.MainLoop()
    gobject.threads_init()
    loop.run()
except KeyboardInterrupt:
    print('Keyboard interrupt')
finally:
    pass
