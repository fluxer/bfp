#!/bin/pyhton2

from PyQt4 import QtCore, QtGui
import libworkspace
general = libworkspace.General()


class Widget(QtGui.QWidget):
    ''' Tab widget '''
    def __init__(self, parent, spath=None):
        super(Widget, self).__init__(parent)
        self.parent = parent
        self.spath = spath
        self.name = 'dummy'


class Plugin(QtCore.QObject):
    ''' Plugin handler '''
    def __init__(self, parent):
        self.parent = parent
        self.name = 'dummy'
        self.version = '0.0.1'
        self.description = self.tr('Dummy plugin')
        self.icon = general.get_icon('delete')
        self.widget = None

    def open(self, spath):
        ''' Open path in new tab '''
        self.index = self.parent.tabWidget.currentIndex()+1
        self.widget = Widget(self.parent, spath)
        self.parent.tabWidget.insertTab(self.index, self.widget, self.icon, self.tr('Dummy'))
        self.parent.tabWidget.setCurrentIndex(self.index)

    def close(self):
        ''' Close tab '''
        if self.widget:
            self.widget.destroy()
            self.parent.tabWidget.removeTab(self.index)

    def unload(self):
        ''' Unload plugin '''
        self.close()
