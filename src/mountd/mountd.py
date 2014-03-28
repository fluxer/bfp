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

class MyMount(libdevice.Device):
    ''' Custom initializer '''
    def loop(self):
        ''' Main loop '''
        if not os.geteuid() == 0:
            message.critical('You are not root')
            sys.exit(2)
        elif os.path.exists(self.ipc):
            message.critical('Mount daemon already running')
            sys.exit(2)

        message.info('Monitoring devices...')
        misc.ipc_create(self.ipc, 9)
        # to ensure fifo cleanup only from the running daemon not
        # possible second instance variable is asigned
        self.initialized = True

        for line in misc.file_readlines('/etc/fstab'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            device, directory, type, options, fsck, fsck2 = line.split()
            if device.startswith('/'):
                self.do_mount(device)
            # FIXME: check if mounts is bogus
            #elif device.startswith('UUID='):
            #    self.do_mount(os.path.join('/dev/disk/by-uuid',
            #        device.replace('UUID=', '')))
        # FIXME: mounts partitions without filesystem
        #for device in os.listdir('/sys/class/block'):
        #    if not len(device) > 3:
        #        continue
        #    self.do_mount(os.path.join('/dev', device))

        while True:
            content = misc.ipc_read(self.ipc)
            device = None
            action = None
            if content:
                device, action = content.split('#')

            if action == 'MOUNT':
                self.do_mount(device)
            elif action == 'UNMOUNT':
                self.do_unmount(device)
            elif action == 'EXIT':
                break

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


# here we go
try:
    mount = MyMount()
    mount.loop()
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
    sys.exit(1)
finally:
    if mount.initialized and os.path.exists(mount.ipc):
        os.remove(mount.ipc)
