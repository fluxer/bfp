#!/bin/pyhton2

from PyQt4 import QtCore, QtGui
import libworkspace, mpv
general = libworkspace.General()


class Widget(QtGui.QWidget):
    ''' Tab widget '''
    def __init__(self, parent, spath=None):
        super(Widget, self).__init__()
        self.parent = parent
        self.spath = spath
        self.name = 'multimedia'

        self.pauseButton = QtGui.QPushButton(general.get_icon('player_pause'), '')
        #self.pauseButton.clicked.connect(self.player_pause)
        self.resumeButton = QtGui.QPushButton(general.get_icon('player_resume'), '')
        #self.resumeButton.clicked.connect(self.player_resume)
        self.mainLayout = QtGui.QGridLayout()
        self.mainLayout.addWidget(self.pauseButton)
        self.mainLayout.addWidget(self.resumeButton)
        self.setLayout(self.mainLayout)

        self.player = mpv.Context()
        # self.player.set_option('input-default-bindings')
        # self.player.set_option('osc')
        # self.player.set_option('vo', 'opengl')
        self.player.initialize()

        if self.spath:
            self.player.command('loadfile', self.spath)

#        while True:
#            event = self.player.wait_event(.01)
#            if event.id  == mpv.Events.none:
#                continue
#            print('EVENT: ' + event.name)
#            if event.id in [mpv.Events.end_file, mpv.Events.shutdown]:
#                print('EOF/SHUTDOWN')
#                break

        def update_gui(self):
            print(self.player.get_property('time_remaining'))

        def player_pause(self):
            self.player.request_event(0, 'pause')

        def player_resume(self):
            self.player.request_event(0, 'resume')


class Plugin(QtCore.QObject):
    ''' Plugin handler '''
    def __init__(self, parent):
        super(Plugin, self).__init__()
        self.parent = parent
        self.name = 'multimedia'
        self.version = '0.0.1'
        self.description = self.tr('Media plugin')
        self.icon = general.get_icon('multimedia-player')
        self.widget = None


        self.mediaButton = QtGui.QPushButton(self.icon, '')
        self.mediaButton.clicked.connect(lambda: self.open(None))
        self.applicationsLayout = self.parent.toolBox.widget(1).layout()
        self.applicationsLayout.addWidget(self.mediaButton)

        # FIXME: register MIMEs

    def open(self, spath):
        ''' Open path in new tab '''
        self.index = self.parent.tabWidget.currentIndex()+1
        self.widget = Widget(self.parent, spath)
        self.parent.tabWidget.insertTab(self.index, self.widget, self.icon, self.tr('Multimedia'))
        self.parent.tabWidget.setCurrentIndex(self.index)

    def close(self):
        ''' Close tab '''
        if self.widget:
            self.widget.destroy()
            self.parent.tabWidget.removeTab(self.index)

    def unload(self):
        ''' Unload plugin '''
        self.applicationsLayout.removeWidget(self.mediaButton)
        self.close()
