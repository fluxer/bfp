#!/bin/pyhton2

from PyQt4 import QtCore, QtGui
import libworkspace
general = libworkspace.General()


class Widget(QtGui.QWidget):
    ''' Tab widget '''
    def __init__(self, parent, spath=None):
        super(Widget, self).__init__()
        self.parent = parent
        self.spath = spath
        self.name = 'embed'
        self.mainLayout = QtGui.QGridLayout()
        self.container = QtGui.QX11EmbedContainer(self)
        self.mainLayout.addWidget(self.container)
        self.setLayout(self.mainLayout)
        self.process = QtCore.QProcess(self.container)
        self.process.start(self.spath)

class Plugin(object):
    ''' Plugin handler '''
    def __init__(self, parent=None):
        self.parent = parent
        self.name = 'embed'
        self.version = '0.0.1'
        self.description = 'Embed test plugin'
        self.icon = general.get_icon('xterm')
        self.widget = None

        self.embedButton = QtGui.QPushButton(self.icon, '')
        self.embedButton.clicked.connect(lambda: self.open('xterm'))
        self.applicationsLayout = self.parent.toolBox.widget(1).layout()
        self.applicationsLayout.addWidget(self.embedButton)

    def open(self, spath):
        ''' Open path in new tab '''
        self.index = self.parent.tabWidget.currentIndex()+1
        self.widget = Widget(self.parent, spath)
        self.parent.tabWidget.insertTab(self.index, self.widget, self.icon, 'Xterm')
        self.parent.tabWidget.setCurrentIndex(self.index)
        self.widget = self.parent.tabWidget.widget(self.index)
        self.widget.process.finished.connect(self.close)

    def close(self):
        ''' Close tab '''
        if self.widget:
            self.widget.destroy()
            self.widget.process.terminate()
            self.widget.process.close()
            self.parent.tabWidget.removeTab(self.index)

    def unload(self):
        ''' Unload plugin '''
        self.applicationsLayout.removeWidget(self.embedButton)
        self.close()
