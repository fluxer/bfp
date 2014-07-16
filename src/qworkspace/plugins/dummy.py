#!/bin/pyhton2

import libworkspace

general = libworkspace.General()

class Plugin(object):
    def __init__(self, parent=None):
        self.name = 'dummy'
        self.version = '0.0.1'
        self.description = 'Dummy plugin'
        self.icon = general.get_icon('delete')

    def open(self, spath):
        pass

    def close(self):
        pass

    def unload(self):
        pass
