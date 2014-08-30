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
        self.name = 'plugins'

        self.mainLayout = QtGui.QGridLayout()
        self.pluginsTable = QtGui.QTableWidget()
        self.pluginsTable.setColumnCount(4)
        self.pluginsTable.setHorizontalHeaderLabels(('Name', 'Version', 'Description', 'Loaded'))
        self.pluginsTable.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.pluginsTable.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        irow = 0
        # FIXME: this works only when all plugins are loaded
        for plugin in self.parent.plugins.plugins_all:
            pobject = self.parent.plugins.plugin_object(plugin)
            self.pluginsTable.setRowCount(irow+1)
            self.pluginsTable.setItem(irow, 0, QtGui.QTableWidgetItem(pobject.name))
            self.pluginsTable.setItem(irow, 1, QtGui.QTableWidgetItem(pobject.version))
            self.pluginsTable.setItem(irow, 2, QtGui.QTableWidgetItem(self.tr(pobject.description)))
            self.pluginsTable.setItem(irow, 3, QtGui.QTableWidgetItem('True'))
            irow += 1
        self.mainLayout.addWidget(self.pluginsTable)
        self.setLayout(self.mainLayout)


class Plugin(QtCore.QObject):
    ''' Plugin handler '''
    def __init__(self, parent):
        super(Plugin, self).__init__()
        self.parent = parent
        self.name = 'plugins'
        self.version = "0.9.35 (9efc4b1)"
        self.description = self.tr('Plugins manager plugin')
        self.icon = general.get_icon('extension')
        self.widget = None

        self.pluginsButton = QtGui.QPushButton(self.icon, '')
        self.pluginsButton.setToolTip(self.description)
        self.pluginsButton.clicked.connect(lambda: self.open(None))
        self.applicationsLayout = self.parent.toolBox.widget(1).layout()
        self.applicationsLayout.addWidget(self.pluginsButton)

    def open(self, spath):
        ''' Open path in new tab '''
        index = self.parent.tabWidget.currentIndex()+1
        self.widget = Widget(self.parent, spath)
        self.parent.tabWidget.insertTab(index, self.widget, self.icon, self.tr('Plugins'))
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
        self.applicationsLayout.removeWidget(self.pluginsButton)
        self.close()
