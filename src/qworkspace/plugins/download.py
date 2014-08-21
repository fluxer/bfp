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
        self.name = 'download'

        self.addButton = QtGui.QPushButton(general.get_icon('list-add'), '')
        self.removeButton = QtGui.QPushButton(general.get_icon('list-remove'), '')
        self.startButton = QtGui.QPushButton(general.get_icon('media-playback-start'), '')
        self.stopButton = QtGui.QPushButton(general.get_icon('process-stop'), '')
        self.secondLayout = QtGui.QHBoxLayout()
        self.secondLayout.addWidget(self.addButton)
        self.secondLayout.addWidget(self.removeButton)
        self.secondLayout.addWidget(self.startButton)
        self.secondLayout.addWidget(self.stopButton)
        self.mainLayout = QtGui.QGridLayout()
        self.downloadView = QtGui.QTableView()
        self.mainLayout.addLayout(self.secondLayout, 0, 0)
        self.mainLayout.addWidget(self.downloadView)
        self.setLayout(self.mainLayout)


class Plugin(QtCore.QObject):
    ''' Plugin handler '''
    def __init__(self, parent):
        super(Plugin, self).__init__()
        self.parent = parent
        self.name = 'download'
        self.version = '0.0.1'
        self.description = self.tr('Download manager plugin')
        self.icon = general.get_icon('document-save-as')
        self.widget = None

        self.downloadButton = QtGui.QPushButton(self.icon, '')
        self.downloadButton.clicked.connect(lambda: self.open(None))
        self.applicationsLayout = self.parent.toolBox.widget(1).layout()
        self.applicationsLayout.addWidget(self.downloadButton)

    def open(self, spath):
        ''' Open path in new tab '''
        index = self.parent.tabWidget.currentIndex()+1
        self.widget = Widget(self.parent, spath)
        self.parent.tabWidget.insertTab(index, self.widget, self.icon, self.tr('Download'))
        self.parent.tabWidget.setCurrentIndex(index)

    def close(self, index=None):
        ''' Close tab '''
        if not index:
            index = self.parent.tabWidget.currentIndex()
        if self.widget:
            self.widget.deleteLater()
            self.widget = None
            self.parent.tabWidget.removeTab(index)

    def unload(self):
        ''' Unload plugin '''
        self.applicationsLayout.removeWidget(self.downloadButton)
        self.close()
