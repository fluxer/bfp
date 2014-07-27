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

        self.shome = QtCore.QDir.homePath()
        self.actions = libworkspace.Actions(self.parent)
        self.secondLayout = QtGui.QHBoxLayout()
        self.homeButton = QtGui.QPushButton(general.get_icon('user-home'), '')
        self.homeButton.clicked.connect(lambda: self.path_open(self.shome))
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
        self.storageView.doubleClicked.connect(self.path_open)
        self.storageView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.storageView.customContextMenuRequested.connect(self.menu_show)

        self.icon_execute = general.get_icon('gtk-execute')
        self.icon_open = general.get_icon('fileopen')
        self.icon_open_with = general.get_icon('fileopen_with')
        self.icon_cut = general.get_icon('edit-cut')
        self.icon_copy = general.get_icon('edit-copy')
        self.icon_paste = general.get_icon('edit-paste')
        self.icon_rename = general.get_icon('edit-rename')
        self.icon_delete = general.get_icon('edit-delete')
        self.icon_properties = general.get_icon('stock_properties')
        self.icon_new_file = general.get_icon('filenew')
        self.icon_new_dir = general.get_icon('stock_new-dir')


        self.path_open(self.spath or self.shome)

    def path_open(self, spath):
        if not spath:
            spath = self.storageView.currentIndex()

        if not isinstance(spath, QtCore.QString) and not isinstance(spath, str):
            spath = self.model.filePath(spath)

        if not os.path.isdir(spath):
            self.parent.plugins.plugin_open(str(spath))
            return

        root = self.model.setRootPath(spath)
        self.storageView.setRootIndex(root)
        #os.chdir(path)
        self.addressBar.setText(os.path.normpath(str(spath)))
        #disable_actions()

    def menu_execute(self):
        selected_items = []
        for svar in self.storageView.selectedIndexes():
            selected_items.append(str(self.model.filePath(svar)))
        self.actions.execute_items(selected_items)

    def menu_open(self):
        for svar in self.storageView.selectedIndexes():
            self.path_open(str(self.model.filePath(svar)))

    def menu_open_with(self):
        selected_items = []
        for svar in self.storageView.selectedIndexes():
            selected_items.append(str(self.model.filePath(svar)))
        self.actions.open_items(selected_items)

    def menu_cut(self):
        selected_items = []
        for svar in self.storageView.selectedIndexes():
            selected_items.append(str(self.model.filePath(svar)))
        self.actions.cut_items(selected_items)
        ui.actionPaste.setEnabled(True)

    def menu_copy(self):
        selected_items = []
        for svar in self.storageView.selectedIndexes():
            selected_items.append(str(self.model.filePath(svar)))
        self.actions.copy_items(selected_items)
        ui.actionPaste.setEnabled(True)

    def menu_paste(self):
        self.actions.paste_items()

    def menu_rename(self):
        selected_items = []
        for svar in self.storageView.selectedIndexes():
            selected_items.append(str(self.model.filePath(svar)))
        self.actions.rename_items(selected_items)

    def menu_delete(self):
        selected_items = []
        for svar in self.storageView.selectedIndexes():
            selected_items.append(str(self.model.filePath(svar)))
        self.actions.delete_items(selected_items)

    def menu_properties(self):
        selected_items = []
        for svar in self.storageView.selectedIndexes():
            selected_items.append(str(self.model.filePath(svar)))
        self.actions.properties_items(selected_items)

    def menu_new_file(self):
        actions.new_file()

    def menu_new_directory(self):
        self.actions.new_directory()

    def menu_show(self):
        # FIXME: enable actions depending on permissions and such
        self.storageMenu = QtGui.QMenu()
        self.storageMenu.addAction(self.icon_execute, self.tr('Execute'), self.menu_execute)
        self.storageMenu.addAction(self.icon_open, self.tr('Open'), self.menu_open)
        self.storageMenu.addAction(self.icon_open_with, self.tr('Open with'), self.menu_open_with)
        self.storageMenu.addSeparator()
        self.storageMenu.addAction(self.icon_cut, self.tr('Cut'), self.menu_cut)
        self.storageMenu.addAction(self.icon_copy, self.tr('Copy'), self.menu_copy)
        self.storageMenu.addAction(self.icon_paste, self.tr('Paste'), self.menu_paste)
        self.storageMenu.addSeparator()
        self.storageMenu.addAction(self.icon_rename, self.tr('Rename'), self.menu_rename)
        self.storageMenu.addAction(self.icon_delete, self.tr('Delete'), self.menu_delete)
        self.storageMenu.addAction(self.icon_properties, self.tr('Properties'), self.menu_properties)
        self.storageMenu.addSeparator()
        self.storageMenu.addAction(self.icon_new_file, self.tr('New file'), self.menu_new_file)
        self.storageMenu.addAction(self.icon_new_dir, self.tr('New directory'), self.menu_new_directory)
        self.storageMenu.popup(QtGui.QCursor.pos())

class ToolWidget(QtGui.QWidget):
    ''' Tool widget '''
    def __init__(self, parent=None):
        super(ToolWidget, self).__init__()
        self.parent = parent
        self.testButton = QtGui.QPushButton(general.get_icon('file-manager'), 'TEST')
        self.addWidget(self.testButton)

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

        #self.tool = ToolWidget(self.parent.toolBox)
        #self.parent.toolBox.addItem(self.tool, 'Storage')

        self.parent.plugins.mime_register('inode/directory', self.name)
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
        #self.tool.destroy()
        self.close()
