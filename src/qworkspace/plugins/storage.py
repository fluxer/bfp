#!/bin/python2

from PyQt4 import QtCore, QtGui
import os, libworkspace
general = libworkspace.General()
settings = libworkspace.Settings()

class Widget(QtGui.QWidget):
    ''' Tab widget '''
    def __init__(self, parent, spath=None):
        super(Widget, self).__init__()
        self.parent = parent
        self.spath = spath
        self.name = 'storage'

        self.api = libworkspace.API(self.parent)
        self.secondLayout = QtGui.QHBoxLayout()
        self.homeButton = QtGui.QPushButton(general.get_icon('home'), '')
        self.homeButton.clicked.connect(lambda: self.change_directory(spath))
        self.addressBar = QtGui.QLineEdit()
        self.secondLayout.addWidget(self.homeButton)
        self.secondLayout.addWidget(self.addressBar)
        self.mainLayout = QtGui.QGridLayout()
        self.mainLayout.addLayout(self.secondLayout, 0, 0)
        self.storageView = QtGui.QListView()
        self.mainLayout.addWidget(self.storageView)
        self.setLayout(self.mainLayout)

        self.model = QtGui.QFileSystemModel()
        self.model.setFilter(QtCore.QDir.AllEntries | QtCore.QDir.NoDot)
        self.storageView.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.storageView.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        self.storageView.setModel(self.model)
        self.storageView.setViewMode(self.storageView.IconMode)
        self.storageView.doubleClicked.connect(self.change_directory)
        self.change_directory(self.spath)

    def change_directory(self, path):
        if not path:
            path = self.storageView.selectedIndexes()
        if not path:
            path = str(QtCore.QDir.homePath())

        if not isinstance(path, QtCore.QString) and not isinstance(path, str):
            path = self.model.filePath(path)
        if not os.path.isdir(path):
            self.mime.open(str(path))
            return
        root = self.model.setRootPath(path)
        self.storageView.setRootIndex(root)
        #os.chdir(path)
        self.addressBar.setText(str(path))
        #disable_actions()


class Plugin(object):
    ''' Plugin handler '''
    def __init__(self, parent):
        self.parent = parent
        self.name = 'storage'
        self.version = '0.0.1'
        self.description = 'Storage management plugin'
        self.icon = general.get_icon('file-manager')
        self.widget = None

        self.storageButton = QtGui.QPushButton(self.icon, '')
        self.storageButton.clicked.connect(lambda: self.open(None))
        self.applicationsLayout = self.parent.toolBox.widget(1).layout()
        self.applicationsLayout.addWidget(self.storageButton)

        # FIXME: register MIMEs
        # FIXME: add item to toolbox for media storage

    def open(self, spath):
        ''' Open path in new tab '''
        self.widget = Widget(self.parent, spath)
        self.index = self.parent.tabWidget.currentIndex()+1
        self.parent.tabWidget.insertTab(self.index, self.widget, self.icon, 'Storage')
        self.parent.tabWidget.setCurrentIndex(self.index)

    def close(self):
        ''' Close tab '''
        if self.widget:
            self.widget.destroy()
            self.parent.tabWidget.removeTab(self.index)

    def unload(self):
        ''' Unload plugin '''
        self.applicationsLayout.removeWidget(self.storageButton)
        self.close()
