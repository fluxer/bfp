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

        self.secondLayout = QtGui.QHBoxLayout()
        self.homeButton = QtGui.QPushButton(general.get_icon('user-home'), '')
        self.homeButton.clicked.connect(lambda: self.change_directory(spath))
        self.addressBar = QtGui.QLineEdit()
        self.addressBar.setReadOnly(True)
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
            self.parent.plugins.plugin_open(str(path))
            return
        root = self.model.setRootPath(path)
        self.storageView.setRootIndex(root)
        #os.chdir(path)
        self.addressBar.setText(os.path.normpath(str(path)))
        #disable_actions()


class Plugin(QtCore.QObject):
    ''' Plugin handler '''
    def __init__(self, parent):
        super(Plugin, self).__init__()
        self.parent = parent
        self.name = 'storage'
        self.version = '0.0.1'
        self.description = self.tr('Storage management plugin')
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
        index = self.parent.tabWidget.currentIndex()+1
        self.widget = Widget(self.parent, spath)
        self.parent.tabWidget.insertTab(index, self.widget, self.icon, self.tr('Storage'))
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
        self.applicationsLayout.removeWidget(self.storageButton)
        self.close()
