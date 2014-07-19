#!/bin/pyhton2

from PyQt4 import QtCore, QtGui
import sys, libworkspace
general = libworkspace.General()


class Plugin(QtCore.QObject):
    ''' Plugin handler '''
    def __init__(self, parent):
        self.parent = parent
        self.name = 'quit'
        self.version = '0.0.1'
        self.description = self.tr('Quit plugin')
        self.icon = general.get_icon('exit')

        self.app = QtGui.QApplication(sys.argv)
        self.quitButton = QtGui.QPushButton(self.icon, '')
        self.quitButton.clicked.connect(self.app.quit)
        #self.parent.toolBox.addItem('System')
        self.parent.toolBox.widget(1).layout().addWidget(self.quitButton)

    def unload(self):
        ''' Unload plugin '''
        self.parent.toolBox.widget(1).removeWidget(self.quitButton)
