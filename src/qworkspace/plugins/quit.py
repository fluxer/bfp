#!/bin/pyhton2

from PyQt4 import QtGui
import sys, libworkspace
general = libworkspace.General()


class Plugin(object):
    ''' Plugin handler '''
    def __init__(self, parent):
        self.parent = parent
        self.name = 'Quit'
        self.version = '0.0.1'
        self.description = 'Quit plugin'
        self.icon = general.get_icon('exit')

        self.quitButton = QtGui.QPushButton(self.icon, '')
        self.quitButton.clicked.connect(sys.exit)
        #self.parent.toolBox.addItem('System')
        self.parent.toolBox.widget(1).layout().addWidget(self.quitButton)

    def unload(self):
        ''' Unload plugin '''
        self.parent.toolBox.widget(1).removeWidget(self.quitButton)
