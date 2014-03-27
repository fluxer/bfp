#!/usr/bin/python

import subprocess, os

import libmisc
import libmessage
import libservice
message = libmessage.Message()
misc = libmisc.Misc()
service = libservice.Init()


class Device(object):
    def __init__(self):
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

    def do_mount(self, device):
        message.sub_info('Mounting device', device)
        self.pre_actions(self.MOUNT_PRE)
        directory = '/media/' + os.path.basename(device)
        if not os.path.isdir(directory):
            os.makedirs(directory)
        if os.path.ismount(directory):
            return
        subprocess.check_call((misc.whereis('mount'), device, directory))
        self.post_actions(self.MOUNT_POST)

    def do_unmount(self, device):
        message.sub_info('Unmounting device', device)
        self.pre_actions(self.UNMOUNT_PRE)
        directory = '/media/' + os.path.basename(device)
        if not os.path.ismount(directory):
            return
        subprocess.check_call((misc.whereis('umount'), directory))
        if os.path.isdir(directory):
            os.rmdir(directory)
        self.post_actions(self.UNMOUNT_POST)
