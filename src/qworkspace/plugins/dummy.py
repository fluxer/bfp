#!/bin/pyhton2

import libworkspace
general = libworkspace.General()


class Widget(QtGui.QWidget):
    ''' Tab widget '''
    def __init__(self, parent, spath=None):
        super(Widget, self).__init__(parent)
        self.name = 'dummy'


class Plugin(object):
    ''' Plugin handler '''
    def __init__(self, parent=None):
        self.name = 'dummy'
        self.version = '0.0.1'
        self.description = 'Dummy plugin'
        self.icon = general.get_icon('delete')

    def open(self, spath):
        ''' Open path in new tab '''
        self.index = self.parent.tabWidget.currentIndex()+1
        self.parent.tabWidget.insertTab(self.index, Widget(self.parent, spath), 'Storage')
        self.parent.tabWidget.setCurrentIndex(self.index)
        self.widget = self.parent.tabWidget.widget(self.index)

    def close(self):
        ''' Close tab '''
        if self.widget:
            self.widget.deleteLater()
            self.parent.tabWidget.removeTab(self.index)

    def unload(self):
        ''' Unload plugin '''
        self.close()
