#!/bin/python2

import time, os, sys, subprocess, libudev, libmessage, libmisc
message = libmessage.Message()
message.DEBUG = True
misc = libmisc.Misc()

app_version = "1.7.6 (83ae7f1)"

class Device(object):
    def __init__(self):
        self.udev = libudev.udev_new()
        if not self.udev:
            message.sub_critical('Can not get udev context')
            sys.exit(1)
        self.CONFDIR = '/etc/ahws.d'

    def Initialize(self):
        ''' Handle all current devices '''
        enumerate = libudev.udev_enumerate_new(self.udev);
        try:
            # libudev.udev_enumerate_add_match_subsystem(enumerate, "pci");
            libudev.udev_enumerate_scan_devices(enumerate);
            entry = libudev.udev_enumerate_get_list_entry(enumerate)
            while entry:
                devname = libudev.udev_list_entry_get_name(entry)
                dev = libudev.udev_device_new_from_syspath(self.udev, devname)
                DEVNAME = libudev.udev_device_get_property_value(dev, 'DEVNAME')
                ID_MODEL_ID = libudev.udev_device_get_property_value(dev, 'ID_MODEL_ID')
                ID_VENDOR_ID = libudev.udev_device_get_property_value(dev, 'ID_VENDOR_ID')
                ID_SERIAL = libudev.udev_device_get_property_value(dev, 'ID_SERIAL')

                # print(libudev.udev_device_get_sysattr_value(dev,"idVendor"))
                # print(libudev.udev_device_get_sysattr_value(dev, "idProduct"))

                self.Online(DEVNAME, ID_MODEL_ID, ID_VENDOR_ID, ID_SERIAL)
                libudev.udev_device_unref(dev)
                entry = libudev.udev_list_entry_get_next(entry)
        finally:
            libudev.udev_enumerate_unref(enumerate);

    def Handle(self, DEVNAME, ID_MODEL_ID, ID_VENDOR_ID, ID_SERIAL, action):
        handle = '%s/%s_%s' % (self.CONFDIR, ID_MODEL_ID, ID_VENDOR_ID)
        if not DEVNAME:
            return
        if not ID_MODEL_ID or not ID_VENDOR_ID:
            message.sub_warning('Model or vendor ID missing for', \
                '%s (%s, %s)' % (DEVNAME, ID_MODEL_ID, ID_VENDOR_ID))
            return
        elif os.path.isfile(handle):
            message.sub_info('Handling event for', \
                '%s (%s, %s)' % (ID_SERIAL, ID_MODEL_ID, ID_VENDOR_ID))
            try:
                misc.system_command((handle, action))
            except Exception as detail:
                message.sub_critical(str(detail))
        else:
            message.sub_debug('No handle for', \
                '%s (%s, %s)' % (ID_SERIAL, ID_MODEL_ID, ID_VENDOR_ID))

    def Add(self, DEVNAME, ID_MODEL_ID, ID_VENDOR_ID, ID_SERIAL):
        ''' Emit that device add action happend '''
        message.sub_info('Added', DEVNAME)
        self.Handle(DEVNAME, ID_MODEL_ID, ID_VENDOR_ID, ID_SERIAL, 'added')

    def Remove(self, DEVNAME, ID_MODEL_ID, ID_VENDOR_ID, ID_SERIAL):
        ''' Emit that device remove action happend '''
        message.sub_info('Removed', DEVNAME)
        self.Handle(DEVNAME, ID_MODEL_ID, ID_VENDOR_ID, ID_SERIAL, 'removed')

    def Change(self, DEVNAME, ID_MODEL_ID, ID_VENDOR_ID, ID_SERIAL):
        ''' Emit that device change action happend '''
        message.sub_info('Changed', DEVNAME)
        self.Handle(DEVNAME, ID_MODEL_ID, ID_VENDOR_ID, ID_SERIAL, 'changed')

    def Online(self, DEVNAME, ID_MODEL_ID, ID_VENDOR_ID, ID_SERIAL):
        ''' Emit that device online action happend '''
        message.sub_info('Onlined', DEVNAME)
        self.Handle(DEVNAME, ID_MODEL_ID, ID_VENDOR_ID, ID_SERIAL, 'onlined')

    def Offline(self, DEVNAME, ID_MODEL_ID, ID_VENDOR_ID, ID_SERIAL):
        ''' Emit that device offline action happend '''
        message.sub_info('Offlined', DEVNAME)
        self.Handle(DEVNAME, ID_MODEL_ID, ID_VENDOR_ID, ID_SERIAL, 'offlined')

    def Daemon(self):
        ''' Daemon that monitors events '''
        try:
            monitor = libudev.udev_monitor_new_from_netlink(self.udev, 'udev')
            # libudev.udev_monitor_filter_add_match_subsystem_devtype(monitor, "pci", None)
            libudev.udev_monitor_enable_receiving(monitor)
            while True:
                if monitor:
                    fd = libudev.udev_monitor_get_fd(monitor)
                if monitor and fd:
                    dev = libudev.udev_monitor_receive_device(monitor)
                    if dev:
                        DEVNAME = libudev.udev_device_get_property_value(dev, 'DEVNAME')
                        ID_MODEL_ID = libudev.udev_device_get_property_value(dev, 'ID_MODEL_ID')
                        ID_VENDOR_ID = libudev.udev_device_get_property_value(dev, 'ID_VENDOR_ID')
                        ID_SERIAL = libudev.udev_device_get_property_value(dev, 'ID_SERIAL')
                        action = libudev.udev_device_get_action(dev)
                        libudev.udev_device_unref(dev)
                        if action == 'add' and DEVNAME:
                            self.Add(DEVNAME, ID_MODEL_ID, ID_VENDOR_ID, ID_SERIAL)
                        elif action == 'remove' and DEVNAME:
                            self.Remove(DEVNAME, ID_MODEL_ID, ID_VENDOR_ID, ID_SERIAL)
                        elif action == 'change' and DEVNAME:
                            self.Change(DEVNAME, ID_MODEL_ID, ID_VENDOR_ID, ID_SERIAL)
                        elif action == 'online' and DEVNAME:
                            self.Online(DEVNAME, ID_MODEL_ID, ID_VENDOR_ID, ID_SERIAL)
                        elif action == 'offline' and DEVNAME:
                            self.Offline(DEVNAME, ID_MODEL_ID, ID_VENDOR_ID, ID_SERIAL)
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
