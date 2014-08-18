#!/bin/pyhton2

from PyQt4 import QtCore, QtGui
import libworkspace, libmisc
general = libworkspace.General()
misc = libmisc.Misc()

class Widget(QtGui.QWidget):
    ''' Tab widget '''
    def __init__(self, parent, spath=None):
        super(Widget, self).__init__()
        self.parent = parent
        self.spath = spath
        self.name = 'multimedia'

        self.container = QtGui.QX11EmbedContainer(self)
        self.mainLayout = QtGui.QGridLayout()
        self.mainLayout.addWidget(self.container)
        self.setLayout(self.mainLayout)

        self.process = QtCore.QProcess(self.container)
        args = ['--wid', str(self.container.winId())]
        if spath:
            args.append(spath)
        self.process.start(misc.whereis('mpv'), args)
        self.process.waitForStarted()
        # self.container.embedClient(self.container.clientWinId())
        # self.container.setFocus()


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
            # self.widget.container.discardClient()
            self.widget.process.terminate()
            self.widget.process.close()
            self.widget.destroy()
            self.parent.tabWidget.removeTab(index)

    def unload(self):
        ''' Unload plugin '''
        self.applicationsLayout.removeWidget(self.mediaButton)
        self.close()
