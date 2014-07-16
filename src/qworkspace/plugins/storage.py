#!/bin/python2

from PyQt4 import QtCore, QtGui
import sys, os, libmisc, libworkspace
general = libworkspace.General()
settings = libworkspace.Settings()
mime = libworkspace.Mimes()

class Widget(QtGui.QWidget):
    ''' Tab widget '''
    def __init__(self, spath=os.curdir, parent=None):
        super(Widget, self).__init__(parent)
        self.secondLayout = QtGui.QHBoxLayout()
        self.homeButton = QtGui.QPushButton(general.get_icon('home'), '')
        self.homeButton.clicked.connect(lambda: self.change_directory(str(QtCore.QDir.homePath())))
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
        self.storageView.setModel(self.model)
        self.storageView.setViewMode(self.storageView.IconMode)
        self.storageView.doubleClicked.connect(self.change_directory)
        self.change_directory(spath)

    def change_directory(self, path):
        if not path:
            path = self.storageView.selectedIndexes()
        if not isinstance(path, QtCore.QString) and not isinstance(path, str):
            path = self.model.filePath(path)
        if not os.path.isdir(path):
            self.mime.open(str(path))
            return
        root = self.model.setRootPath(path)
        self.storageView.setRootIndex(root)
        os.chdir(path)
        self.addressBar.setText(str(path))
        #disable_actions()


class Plugin(object):
    def __init__(self, parent=None):
        self.parent = parent
        self.name = 'storage'
        self.version = '0.0.1'
        self.description = 'Storage management plugin'
        self.icon = general.get_icon('delete')

    def load(self, spath=os.curdir):
        self.index = self.parent.tabWidget.currentIndex()+1
        self.parent.tabWidget.insertTab(self.index, Widget(spath), 'Storage')
        self.parent.tabWidget.setCurrentIndex(self.index)
        self.widget = self.parent.tabWidget.widget(self.index)

        watcher1 = QtCore.QFileSystemWatcher()
        watcher1.addPath(settings.settings.fileName())
        watcher1.fileChanged.connect(self.reload_storage)

    def unload(self):
        self.widget.deleteLater()
        self.parent.tabWidget.removeTab(self.index)

    def reload_storage(self):
        reload(libworkspace)
        self.settings = libworkspace.Settings()
        self.mime = libworkspace.Mimes()
