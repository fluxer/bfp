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

        self.secondLayout = QtGui.QHBoxLayout()
        self.openButton = QtGui.QPushButton(general.get_icon('document-open'), '')
        self.openButton.clicked.connect(self.open_file)
        self.outputBox = QtGui.QComboBox()
        # https://github.com/mpv-player/mpv/blob/master/DOCS/man/vo.rst
        self.outputBox.addItems(('x11', 'vdpau', 'vaapi', 'opengl'))
        self.outputBox.currentIndexChanged.connect(self.mpv_restart)
        self.secondLayout.addWidget(self.openButton)
        self.secondLayout.addWidget(self.outputBox)
        # HACK!!! QX11EmbedWidget breaks the layout horribly
        self.dummy = QtGui.QWidget(self)
        self.mainLayout = QtGui.QGridLayout()
        self.container = QtGui.QX11EmbedWidget(self.dummy)
        self.mainLayout.addLayout(self.secondLayout, 0, 0)
        self.mainLayout.addWidget(self.dummy)
        self.setLayout(self.mainLayout)

        self.process = None
        self.mpv = misc.whereis('mpv')

        if self.spath:
            self.mpv_start(self.spath)

    def open_file(self):
        sfile = QtGui.QFileDialog.getOpenFileName(self, self.tr('Open'), \
            self.spath, self.tr('Media (*.wav *.mpeg *.mkv *.avi *.flv *.3gp *.mp4);;All (*)'))
        if sfile:
            self.spath = sfile
            self.mpv_restart()

    def mpv_start(self, spath=None):
        arguments = ['--wid', str(self.dummy.winId()), \
            '-vo', str(self.outputBox.currentText())]
        if self.spath:
            arguments.append(self.spath)
        elif spath:
            arguments.append(spath)

        self.process = QtCore.QProcess(self.container)
        self.process.start(self.mpv, arguments)
        self.process.waitForStarted()

    def mpv_restart(self):
        self.mpv_stop()
        self.mpv_start()

    def mpv_stop(self):
        if self.process:
            self.process.terminate()
            self.process.close()

class Plugin(QtCore.QObject):
    ''' Plugin handler '''
    def __init__(self, parent):
        super(Plugin, self).__init__()
        self.parent = parent
        self.name = 'multimedia'
        self.version = "0.9.31 (ee00476)"
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
            if self.widget.process:
                self.widget.mpv_stop()
            self.widget.deleteLater()
            self.widget = None
            self.parent.tabWidget.removeTab(index)

    def unload(self):
        ''' Unload plugin '''
        self.applicationsLayout.removeWidget(self.mediaButton)
        self.close()
