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
        self.name = 'multimedia'

        self.pauseButton = QtGui.QPushButton(general.get_icon('player_pause'), '')
        self.pauseButton.clicked.connect(self.player_pause)
        self.resumeButton = QtGui.QPushButton(general.get_icon('player_play'), '')
        self.resumeButton.clicked.connect(self.player_resume)
        self.mainLayout = QtGui.QGridLayout()
        self.mainLayout.addWidget(self.pauseButton)
        self.mainLayout.addWidget(self.resumeButton)
        self.setLayout(self.mainLayout)

        if self.spath:
            self.open_file(self.spath)

    def update_gui(self):
        pass

    def open_file(self, spath):
        pass

    def player_pause(self):
        pass

    def player_resume(self):
        pass


class Plugin(QtCore.QObject):
    ''' Plugin handler '''
    def __init__(self, parent):
        super(Plugin, self).__init__()
        self.parent = parent
        self.name = 'multimedia'
        self.version = '0.0.1'
        self.description = self.tr('Multimedia plugin')
        self.icon = general.get_icon('multimedia-player')
        self.widget = None


        self.mediaButton = QtGui.QPushButton(self.icon, '')
        self.mediaButton.clicked.connect(lambda: self.open(None))
        self.applicationsLayout = self.parent.toolBox.widget(1).layout()
        self.applicationsLayout.addWidget(self.mediaButton)

        self.parent.plugins.mime_register('audio/x-wav', self.name)
        self.parent.plugins.mime_register('audio/mpeg', self.name)
        self.parent.plugins.mime_register('video/x-matroska', self.name)
        self.parent.plugins.mime_register('video/x-msvideo', self.name)
        self.parent.plugins.mime_register('video/x-flv', self.name)
        self.parent.plugins.mime_register('video/x-ms-asf', self.name)
        self.parent.plugins.mime_register('video/3gp', self.name)
        self.parent.plugins.mime_register('video/mpeg', self.name)
        self.parent.plugins.mime_register('video/mp4', self.name)

    def open(self, spath):
        ''' Open path in new tab '''
        index = self.parent.tabWidget.currentIndex()+1
        self.widget = Widget(self.parent, spath)
        self.parent.tabWidget.insertTab(index, self.widget, self.icon, self.tr('Multimedia'))
        self.parent.tabWidget.setCurrentIndex(index)

    def close(self, index=None):
        ''' Close tab '''
        if not index:
            index = self.parent.tabWidget.currentIndex()
        if self.widget:
            self.widget.destroy()
            self.parent.tabWidget.removeTab(index)

    def unload(self):
        ''' Unload plugin '''
        self.applicationsLayout.removeWidget(self.mediaButton)
        self.close()
