#!/usr/bin/python2

import time, os, sys, libmessage, libmisc
message = libmessage.Message()
message.DEBUG = True
misc = libmisc.Misc()
udev = libmisc.UDev()

app_version = "1.8.2 (6109f03)"

class AHWS(object):
    def __init__(self):
        self.HANDLERS_DIR = '/etc/ahws.d'
        self.SUBSYSTEMS = ['pci', 'usb', 'video4linux', 'sound', 'snd', 'printer', 'drm']

    def Properties(self, dev):
        DEVNAME = udev.get_property(dev, 'DEVNAME')
        if not DEVNAME:
            DEVNAME = udev.get_property(dev, 'KERNEL')
        if not DEVNAME:
            DEVNAME = 'Unknown'

        # ieee1394_id ?
        PRODUCT = udev.get_property(dev, 'ID_MODEL_ID')
        if not PRODUCT:
            PRODUCT = udev.get_sysattr(dev, 'idProduct')
        if not PRODUCT:
            PRODUCT = udev.get_sysattr(dev, 'device')

        VENDOR = udev.get_property(dev, 'ID_VENDOR_ID')
        if not VENDOR:
            VENDOR = udev.get_sysattr(dev, 'idVendor')
        if not VENDOR:
            VENDOR = udev.get_sysattr(dev, 'vendor')

        SERIAL = udev.get_property(dev, 'ID_SERIAL')
        if not SERIAL:
            udev.get_sysattr(dev, 'serial')
        if not SERIAL:
            udev.get_sysattr(dev, 'product')

        SUBSYSTEM = udev.get_subsystem(dev)

        return DEVNAME, PRODUCT, VENDOR, SERIAL, SUBSYSTEM

    def Handle(self, properties, action):
        DEVNAME, MODEL, VENDOR, SERIAL, SUBSYSTEM = properties
        MODEL = '0x%s' % MODEL
        VENDOR = '0x%s' % VENDOR
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
                        action = udev.get_action(dev)
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
    message.critical(detail)
    sys.exit(1)
finally:
    if os.path.isfile(pidfile):
        os.unlink(pidfile)
