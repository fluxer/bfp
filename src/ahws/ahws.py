#!/bin/python2

import time, os, sys, subprocess, libudev, libmessage, libmisc
message = libmessage.Message()
message.DEBUG = True
misc = libmisc.Misc()

app_version = "1.7.6 (e55cc49)"

class Device(object):
    def __init__(self):
        self.udev = libudev.udev_new()
        if not self.udev:
            message.sub_critical('Can not get udev context')
            sys.exit(1)
        self.HANDLERS_DIR = '/etc/ahws.d'
        self.SUBSYSTEMS = ['pci', 'usb', 'video4linux', 'sound', 'snd', 'printer', 'drm']

    def Properties(self, dev):
        DEVNAME = libudev.udev_device_get_property_value(dev, 'DEVNAME')
        if not DEVNAME:
            DEVNAME = libudev.udev_device_get_property_value(dev,'KERNEL')
        if not DEVNAME:
            DEVNAME = 'Unknown'

        # ieee1394_id ?
        PRODUCT = libudev.udev_device_get_property_value(dev, 'ID_MODEL_ID')
        if not PRODUCT:
            PRODUCT = libudev.udev_device_get_sysattr_value(dev,'idProduct')
        if not PRODUCT:
            PRODUCT = libudev.udev_device_get_sysattr_value(dev,'device')

        VENDOR = libudev.udev_device_get_property_value(dev, 'ID_VENDOR_ID')
        if not VENDOR:
            VENDOR = libudev.udev_device_get_sysattr_value(dev,'idVendor')
        if not VENDOR:
            VENDOR = libudev.udev_device_get_sysattr_value(dev,'vendor')

        SERIAL = libudev.udev_device_get_property_value(dev, 'ID_SERIAL')
        if not SERIAL:
            libudev.udev_device_get_sysattr_value(dev, 'serial')
        if not SERIAL:
            libudev.udev_device_get_sysattr_value(dev, 'product')

        return DEVNAME, PRODUCT, VENDOR, SERIAL

    def Initialize(self):
        ''' Handle all current devices '''
        enumerate = libudev.udev_enumerate_new(self.udev);
        try:
            for subsystem in self.SUBSYSTEMS:
                libudev.udev_enumerate_add_match_subsystem(enumerate, subsystem)
            libudev.udev_enumerate_scan_devices(enumerate);
            entry = libudev.udev_enumerate_get_list_entry(enumerate)
            while entry:
                devname = libudev.udev_list_entry_get_name(entry)
                dev = libudev.udev_device_new_from_syspath(self.udev, devname)
                try:
                    self.Online(self.Properties(dev))
                finally:
                    libudev.udev_device_unref(dev)
                entry = libudev.udev_list_entry_get_next(entry)
        finally:
            libudev.udev_enumerate_unref(enumerate);

    def Handle(self, properties, action):
        DEVNAME, MODEL, VENDOR, SERIAL = properties
        handle = '%s/%s_%s' % (self.HANDLERS_DIR, VENDOR, MODEL)
        if not MODEL or not VENDOR:
            message.sub_warning('Model or vendor ID missing for', \
                '%s (%s, %s)' % (DEVNAME, VENDOR, MODEL))
            return
        elif os.path.isfile(handle):
            message.sub_info('Handling event for', \
                '%s (%s, %s)' % (SERIAL, VENDOR, MODEL))
            try:
                misc.system_command((handle, action))
            except Exception as detail:
                message.sub_critical(str(detail))
        else:
            message.sub_debug('No handle for', \
                '%s (%s, %s)' % (SERIAL, VENDOR, MODEL))

    def Add(self, properties):
        ''' Emit that device add action happend '''
        message.sub_info('Added', properties[0])
        self.Handle(properties, 'added')

    def Remove(self, properties):
        ''' Emit that device remove action happend '''
        message.sub_info('Removed', properties[0])
        self.Handle(properties, 'removed')

    def Change(self, properties):
        ''' Emit that device change action happend '''
        message.sub_info('Changed', properties[0])
        self.Handle(properties, 'changed')

    def Online(self, properties):
        ''' Emit that device online action happend '''
        message.sub_info('Onlined', properties[0])
        self.Handle(properties, 'online')

    def Offline(self, properties):
        ''' Emit that device offline action happend '''
        message.sub_info('Offlined', properties[0])
        self.Handle(properties, 'offline')

    def Daemon(self):
        ''' Daemon that monitors events '''
        try:
            monitor = libudev.udev_monitor_new_from_netlink(self.udev, 'udev')
            for subsystem in self.SUBSYSTEMS:
                libudev.udev_monitor_filter_add_match_subsystem_devtype(monitor, subsystem, None)
            libudev.udev_monitor_enable_receiving(monitor)
            while True:
                if monitor:
                    fd = libudev.udev_monitor_get_fd(monitor)
                if monitor and fd:
                    dev = libudev.udev_monitor_receive_device(monitor)
                    if dev:
                        action = libudev.udev_device_get_action(dev)
                        if action == 'add':
                            self.Add(self.Properties(dev))
                        elif action == 'remove':
                            self.Remove(self.Properties(dev))
                        elif action == 'change':
                            self.Change(self.Properties(dev))
                        elif action == 'online':
                            self.Online(self.Properties(dev))
                        elif action == 'offline':
                            self.Offline(self.Properties(dev))
                        libudev.udev_device_unref(dev)
                    else:
                        time.sleep(1)
        except Exception as detail:
            message.sub_critical(str(detail))
        finally:
            libudev.udev_unref(self.udev)

try:
    device = Device()
    message.info('Initializing AHWS v%s' % app_version)
    device.Initialize()
    message.info('Daemonizing AHWS')
    device.Daemon()
except KeyboardInterrupt:
    message.sub_critical('Keyboard interrupt')
finally:
    pass
