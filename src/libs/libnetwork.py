#!/usr/bin/python

import subprocess, os

import libmisc
import libmessage
message = libmessage.Message()
misc = libmisc.Misc()


class Network(object):
    def __init__(self):
        self.CONNECT_PRE = None
        self.CONNECT_POST = None
        self.DISCONNECT_PRE = None
        self.DISCONNECT_POST = None

        # changed depending on network state
        self.NETWORK_VALUE = False


    def get_interfaces(self):
        interfaces = []
        for sdir in os.listdir('/sys/class/net'):
            interfaces.append(os.path.join('/sys/class/net', sdir))
        return interfaces

    def get_status(self):
        pass

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

    def do_connect(self):
        message.sub_info('Connecting interface...')
        self.pre_actions(self.CONNECT_PRE)
        # FIXME: actually connect
        self.post_actions(self.CONNECT_POST)

    def do_disconnect(self):
        message.sub_info('Disconnecting interface...')
        self.pre_actions(self.DISCONNECT_PRE)
        # FIXME: actually disconnect
        self.post_actions(self.DISCONNECT_POST)
