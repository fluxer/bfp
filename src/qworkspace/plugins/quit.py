#!/bin/pyhton2

from PyQt4 import QtCore, QtGui
import libworkspace
general = libworkspace.General()

class Plugin(QtCore.QObject):
    ''' Plugin handler '''
    def __init__(self, parent):
        super(Plugin, self).__init__()
        self.parent = parent
        self.name = 'quit'
        self.version = "0.9.37 (1db7d9d)"
        self.description = self.tr('Quit plugin')
        self.icon = general.get_icon('system-log-out')

        self.quitButton = QtGui.QPushButton(self.icon, '')
        self.quitButton.setToolTip(self.description)
        self.quitButton.clicked.connect(self.parent.app.quit)
        #self.parent.toolBox.addItem('System')
        self.parent.toolBox.widget(1).layout().addWidget(self.quitButton)

    def unload(self):
        ''' Unload plugin '''
        self.parent.toolBox.widget(1).layout().removeWidget(self.quitButton)
