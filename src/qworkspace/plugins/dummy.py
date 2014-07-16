#!/bin/pyhton2

import libworkspace
general = libworkspace.General()


class Widget(QtGui.QWidget):
    ''' Tab widget '''
    def __init__(self, parent, spath=None):
        super(Widget, self).__init__(parent)
        self.name = 'editor'


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
