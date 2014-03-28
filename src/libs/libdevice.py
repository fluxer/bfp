#!/usr/bin/python

import subprocess, os

import libmisc
import libmessage
message = libmessage.Message()
misc = libmisc.Misc()


class Device(object):
    ''' Device initializer '''
    def __init__(self):
        ''' Initializer '''
        self.initialized = False
        self.ipc = '/run/device.fifo'
        # set custom log file
        message.LOG_FILE = '/var/log/device.log'
        
        self.MOUNT_PRE = None
        self.MOUNT_POST = None
        self.UNMOUNT_PRE = None
        self.UNMOUNT_POST = None

    def pre_actions(self, actions):
        if not actions:
            return
        for action in actions:
            message.sub_info('Executing pre-action', action)
            subprocess.check_call((action))

    def post_actions(self, actions):
        if not actions:
            return
        for action in actions:
            message.sub_info('Executing post-action', action)
            subprocess.check_call((action))

    def check_mounted(self, string):
        for line in misc.file_readlines('/proc/mounts'):
            device, directory, type, options, fsck, fsck2 = line.split()
            if device == string or directory == string:
                return True
        return False

    def do_mount(self, device):
        message.sub_info('Mounting device', device)
        self.pre_actions(self.MOUNT_PRE)
        directory = '/media/' + os.path.basename(device)
        if not os.path.isdir(directory):
            os.makedirs(directory)
        if not self.check_mounted(device):
            subprocess.check_call((misc.whereis('mount'), device, directory))
        else:
            return
        self.post_actions(self.MOUNT_POST)

    def do_unmount(self, device):
        message.sub_info('Unmounting device', device)
        self.pre_actions(self.UNMOUNT_PRE)
        directory = '/media/' + os.path.basename(device)
        if self.check_mounted(device):
            subprocess.check_call((misc.whereis('umount'), device))
        elif os.path.ismount(directory):
            subprocess.check_call((misc.whereis('umount'), directory))
        else:
            return
        if os.path.isdir(directory):
            os.rmdir(directory)
        self.post_actions(self.UNMOUNT_POST)
