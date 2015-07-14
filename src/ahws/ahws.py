#!/usr/bin/python2

import time, os, sys, libmessage, libmisc
message = libmessage.Message()
message.DEBUG = True
misc = libmisc.Misc()
udev = libmisc.UDev()

app_version = "1.8.2 (d19e85c)"

class AHWS(object):
    def __init__(self):
        self.HANDLERS_DIR = '/etc/ahws.d'
        self.SUBSYSTEMS = ['pci', 'usb', 'video4linux', 'sound', 'snd', 'printer', 'drm']

    def Properties(self, dev):
        DEVNAME = udev.libudev.udev_device_get_property_value(dev, 'DEVNAME')
        if not DEVNAME:
            DEVNAME = udev.libudev.udev_device_get_property_value(dev, 'KERNEL')
        if not DEVNAME:
            DEVNAME = 'Unknown'

        # ieee1394_id ?
        PRODUCT = udev.libudev.udev_device_get_property_value(dev, 'ID_MODEL_ID')
        if not PRODUCT:
            PRODUCT = udev.libudev.udev_device_get_sysattr_value(dev, 'idProduct')
        if not PRODUCT:
            PRODUCT = udev.libudev.udev_device_get_sysattr_value(dev, 'device')

        VENDOR = udev.libudev.udev_device_get_property_value(dev, 'ID_VENDOR_ID')
        if not VENDOR:
            VENDOR = udev.libudev.udev_device_get_sysattr_value(dev, 'idVendor')
        if not VENDOR:
            VENDOR = udev.libudev.udev_device_get_sysattr_value(dev, 'vendor')

        SERIAL = udev.libudev.udev_device_get_property_value(dev, 'ID_SERIAL')
        if not SERIAL:
            udev.libudev.udev_device_get_sysattr_value(dev, 'serial')
        if not SERIAL:
            udev.libudev.udev_device_get_sysattr_value(dev, 'product')

        SUBSYSTEM = udev.libudev.udev_device_get_subsystem(dev)

        return DEVNAME, PRODUCT, VENDOR, SERIAL, SUBSYSTEM

    def Handle(self, properties, action):
        DEVNAME, MODEL, VENDOR, SERIAL, SUBSYSTEM = properties
        if not MODEL or not VENDOR:
            message.sub_warning('Model or vendor ID missing for', \
                '%s (%s, %s)' % (DEVNAME, VENDOR, MODEL))
            return

        subhandle = '%s/%s' % (self.HANDLERS_DIR, SUBSYSTEM)
        if os.path.isfile(subhandle):
            message.sub_info('Handling subsystem %s for' % action, \
                '%s (%s, %s)' % (SUBSYSTEM, VENDOR, MODEL))
            try:
                misc.system_command((subhandle, action, DEVNAME))
            except Exception as detail:
                message.sub_critical(str(detail))
        else:
            message.sub_debug('No subsystem handle for', \
                '%s (%s)' % (SUBSYSTEM, DEVNAME))

        devhandle = '%s/%s_%s' % (self.HANDLERS_DIR, VENDOR, MODEL)
        if os.path.isfile(devhandle):
            message.sub_info('Handling device %s for' % action, \
                '%s (%s, %s)' % (SERIAL, VENDOR, MODEL))
            try:
                misc.system_command((devhandle, action))
            except Exception as detail:
                message.sub_critical(str(detail))
        else:
            message.sub_debug('No device handle for', \
                '%s (%s, %s)' % (SERIAL, VENDOR, MODEL))

    def Initialize(self):
        ''' Handle all current devices '''
        udevenum = udev.libudev.udev_enumerate_new(udev.udev)
        try:
            for subsystem in self.SUBSYSTEMS:
                udev.libudev.udev_enumerate_add_match_subsystem(udevenum, subsystem)
            udev.libudev.udev_enumerate_scan_devices(udevenum)
            entry = udev.libudev.udev_enumerate_get_list_entry(udevenum)
            while entry:
                devname = udev.libudev.udev_list_entry_get_name(entry)
                dev = udev.libudev.udev_device_new_from_syspath(udev.udev, devname)
                try:
                    self.Handle(self.Properties(dev), 'online')
                finally:
                    udev.libudev.udev_device_unref(dev)
                entry = udev.libudev.udev_list_entry_get_next(entry)
        finally:
            udev.libudev.udev_enumerate_unref(udevenum)

    def Daemonize(self):
        ''' Daemon that monitors events '''
        try:
            monitor = udev.libudev.udev_monitor_new_from_netlink(udev.udev, 'udev')
            for subsystem in self.SUBSYSTEMS:
                udev.libudev.udev_monitor_filter_add_match_subsystem_devtype(monitor, subsystem, None)
            udev.libudev.udev_monitor_enable_receiving(monitor)
            while True:
                if monitor:
                    fd = udev.libudev.udev_monitor_get_fd(monitor)
                if monitor and fd:
                    dev = udev.libudev.udev_monitor_receive_device(monitor)
                    if dev:
                        action = udev.libudev.udev_device_get_action(dev)
                        self.Handle(self.Properties(dev), action)
                        udev.libudev.udev_device_unref(dev)
                    else:
                        time.sleep(1)
        except Exception as detail:
            message.sub_critical(str(detail))


pidfile = '/var/run/ahws.pid'
try:
    misc.file_write(pidfile, str(os.getpid()))
    ahws = AHWS()
    message.info('Initializing AHWS v%s' % app_version)
    ahws.Initialize()
    message.info('Daemonizing AHWS')
    ahws.Daemonize()
except Exception as detail:
    message.sub_critical(str(detail))
    sys.exit(1)
finally:
    if os.path.isfile(pidfile):
        os.unlink(pidfile)
