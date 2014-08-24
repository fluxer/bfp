#!/bin/python2

from PyQt4 import QtCore, QtGui
import os, shutil, time, libmisc, libmessage, libsystem, libworkspace
general = libworkspace.General()
settings = libworkspace.Settings()
misc = libmisc.Misc()
system = libsystem.System()
message = libmessage.Message()

class Widget(QtGui.QWidget):
    ''' Tab widget '''
    def __init__(self, parent, spath=None):
        super(Widget, self).__init__()
        self.parent = parent
        self.spath = spath
        self.name = 'storage'

        self.shome = QtCore.QDir.homePath()
        self.clipboard = self.parent.app.clipboard()
        self.cut = []
        self.copy = []

        self.secondLayout = QtGui.QHBoxLayout()
        self.homeButton = QtGui.QPushButton(general.get_icon('user-home'), '')
        self.homeButton.clicked.connect(lambda: self.path_open(self.shome))
        self.viewBox = QtGui.QComboBox()
        self.viewBox.addItem(self.tr('Icons view'))
        self.viewBox.addItem(self.tr('List view'))
        self.viewBox.currentIndexChanged.connect(self.change_view)
        self.addressBar = QtGui.QLineEdit()
        self.addressBar.setReadOnly(True)
        self.secondLayout.addWidget(self.homeButton)
        self.secondLayout.addWidget(self.viewBox)
        self.secondLayout.addWidget(self.addressBar)
        self.mainLayout = QtGui.QGridLayout()
        self.mainLayout.addLayout(self.secondLayout, 0, 0)
        self.storageView = QtGui.QListView()
        self.mainLayout.addWidget(self.storageView)
        self.setLayout(self.mainLayout)

        self.model = QtGui.QFileSystemModel()
        self.model.setFilter(QtCore.QDir.AllEntries | QtCore.QDir.NoDot)
        index = self.viewBox.findText(settings.get('storage/view', self.tr('Icons view')))
        self.viewBox.setCurrentIndex(index)
        self.storageView.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.storageView.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        self.storageView.setModel(self.model)
        self.storageView.doubleClicked.connect(self.path_open)
        self.storageView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.storageView.customContextMenuRequested.connect(self.menu_show)

        self.icon_execute = general.get_icon('system-run')
        self.icon_open = general.get_icon('document-open')
        self.icon_open_with = general.get_icon('dcument-import')
        self.icon_cut = general.get_icon('edit-cut')
        self.icon_copy = general.get_icon('edit-copy')
        self.icon_paste = general.get_icon('edit-paste')
        self.icon_rename = general.get_icon('edit-rename')
        self.icon_delete = general.get_icon('edit-delete')
        self.icon_properties = general.get_icon('document-properties')
        self.icon_new_file = general.get_icon('document-new')
        self.icon_new_dir = general.get_icon('folder-new')


        self.path_open(self.spath or self.shome)

    def _check_exists(self, sfile):
        ''' Check if file/dir exists and offer to rename '''
        sfile_basename = os.path.basename(sfile)
        sfile_dirname = os.path.dirname(sfile)
        sfile_basename, ok = QtGui.QInputDialog.getText(self, \
            self.tr('File/directory exists'), \
            self.tr('File/directory exists, new name:'), \
            QtGui.QLineEdit.Normal, sfile_basename)
        sfile_basename = str(sfile_basename)
        if ok and sfile_basename:
            if not os.path.exists(sfile_dirname + '/' + sfile_basename):
                return sfile_basename
            else:
                return self.check_exists(sfile)
        elif not ok:
            return

    def change_view(self):
        if str(self.viewBox.currentText()) == self.tr('Icons view'):
            self.storageView.setViewMode(self.storageView.IconMode)
        else:
            self.storageView.setViewMode(self.storageView.ListMode)

    def path_open(self, spath):
        if not spath:
            spath = self.storageView.currentIndex()

        if not isinstance(spath, unicode) and not isinstance(spath, str):
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
        ''' Execute files with default software '''
        for svar in self.storageView.selectedIndexes():
            spath = str(self.model.filePath(svar))
            if os.path.isfile(spath):
                general.execute_program(spath)

    def menu_open(self):
        for svar in self.storageView.selectedIndexes():
            self.path_open(str(self.model.filePath(svar)))

    def menu_open_with(self):
        # FIXME: implement
        # self.parent.plugins.plugins_open_with(str(self.model.filePath(svar)))
        for svar in self.storageView.selectedIndexes():
            pass

    def menu_cut(self):
        ''' Cut files/directories for future paste '''
        self.cut = []
        self.copy = []
        for svar in self.storageView.selectedIndexes():
            self.cut.append(str(self.model.filePath(svar)))
        self.clipboard.setText(misc.string_convert(self.cut))

    def menu_copy(self):
        ''' Copy files/directories for future paste '''
        self.cut = []
        self.copy = []
        for svar in self.storageView.selectedIndexes():
            self.copy.append(str(self.model.filePath(svar)))
        self.clipboard.setText(misc.string_convert(self.copy))

    def menu_paste(self):
        ''' Paste files/directories '''
        # FIXME: _check_exists()
        sdest = str(self.model.rootPath())
        if self.cut:
            for svar in self.cut:
                if os.path.isdir(svar):
                    shutil.copytree(svar, sdest)
                    misc.dir_remove(svar)
                else:
                    shutil.copy2(svar, sdest)
                    os.unlink(svar)
        elif self.copy:
            for svar in self.copy:
                if os.path.isdir(svar):
                    shutil.copytree(svar, sdest)
                else:
                    shutil.copy2(svar, sdest)
        else:
            # FIXME: it will break on paths with spaces,
            #        is it OK to use \n in the clipboard content to solve this?
            # FIXME: download URLs
            for svar in self.clipboard.text().split(' '):
                if os.path.isdir(svar):
                    shutil.copytree(svar, sdest)
                else:
                    shutil.copy2(svar, sdest)

    def menu_rename(self):
        ''' Rename files/directories '''
        # FIXME: _check_exists()
        sdest = str(self.model.rootPath())
        for svar in self.storageView.selectedIndexes():
            snvar, ok = QtGui.QInputDialog.getText(self, self.tr('Rename'), \
                self.tr('New name:'), QtGui.QLineEdit.Normal)
            os.rename(str(self.model.filePath(svar)), sdest + '/' + str(snvar))

    def menu_delete(self):
        ''' Delete files/directories '''
        for svar in self.storageView.selectedIndexes():
            spath = str(self.model.filePath(svar))
            if os.path.isdir(spath):
                misc.dir_remove(spath)
            else:
                os.unlink(spath)

    def menu_properties(self):
        selected_items = []
        for svar in self.storageView.selectedIndexes():
            selected_items.append(str(self.model.filePath(svar)))
        # FIXME: implement

    def menu_new_file(self):
        ''' Create a new file '''
        svar, ok = QtGui.QInputDialog.getText(self, self.tr('New file'), \
            self.tr('Name:'), QtGui.QLineEdit.Normal)
        svar = os.path.realpath(str(self.model.rootPath() + '/' + svar))
        if ok and svar:
            if os.path.exists(svar):
                svar = self._check_exists(svar)
                if not svar:
                    return
            misc.file_touch(os.path.realpath(str(svar)))

    def menu_new_directory(self):
        ''' Create a new directory '''
        svar, ok = QtGui.QInputDialog.getText(self, self.tr('New directory'), \
            self.tr('Name:'), QtGui.QLineEdit.Normal)
        svar = os.path.realpath(str(self.model.rootPath() + '/' + svar))
        if ok and svar:
            if os.path.isdir(svar):
                svar = self._check_exists(svar)
                if not svar:
                    return
            misc.dir_create(str(svar))

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

    def menu_extract(self):
        ''' Extract archives '''
        # FIXME: implement
        pass

    def menu_gzip(self):
        ''' Gzip files/directories into archive '''
        # FIXME: implement
        pass

    def menu_bzip2(self):
        ''' BZip2 files/directories into archive '''
        # FIXME: implement
        pass


class Daemon(QtCore.QThread):
    def __init__(self, parent):
        super(Daemon, self).__init__()
        self.parent = parent

    def run(self):
        ''' Monitor block devices state '''
        if not os.path.exists('/sys/class/block'):
            self.parent.plugins.notify_information(self.tr('No sysfs support'))
            return

        while True:
            before = os.listdir('/sys/class/block')
            time.sleep(1)
            after = os.listdir('/sys/class/block')
            for f in after:
                if '.tmp' in f:
                    continue
                if not f in before:
                    try:
                        system.do_mount('/dev/' + f)
                        self.emit(QtCore.SIGNAL('mounted'), '/media/' + f)
                    except Exception as detail:
                        message.sub_critical(str(detail))
            for f in before:
                if '.tmp' in f:
                    continue
                if not f in after:
                    try:
                        system.do_unmount('/dev/' + f)
                        self.emit(QtCore.SIGNAL('unmounted'), '/media/' + f)
                    except Exception as detail:
                        message.sub_critical(str(detail))
            time.sleep(1)


class ToolWidget(QtGui.QWidget):
    ''' Tool widget '''
    def __init__(self, parent=None):
        super(ToolWidget, self).__init__()
        self.parent = parent
        self.mainLayout = QtGui.QGridLayout()
        self.setLayout(self.mainLayout)

    def add_button(self, sname):
        self.testButton = QtGui.QPushButton(general.get_icon('drive-harddisk'), sname)
        self.testButton.clicked.connect(lambda: self.parent.plugins.plugin_open(sname))
        self.mainLayout.addWidget(self.testButton)
        self.parent.plugins.notify_information(self.tr('Device mounted to: %s' % sname))

    def remove_button(self, sname):
        # FIXME: actually remove button
        self.parent.plugins.notify_information(self.tr('Device unmounted from: %s' % sname))

class Plugin(QtCore.QObject):
    ''' Plugin handler '''
    def __init__(self, parent):
        super(Plugin, self).__init__()
        self.parent = parent
        self.name = 'storage'
        self.version = "0.9.32 (c86f8f3)"
        self.description = self.tr('Storage management plugin')
        self.icon = general.get_icon('system-file-manager')
        self.widget = None

        self.storageButton = QtGui.QPushButton(self.icon, '')
        self.storageButton.clicked.connect(lambda: self.open(None))
        self.applicationsLayout = self.parent.toolBox.widget(1).layout()
        self.applicationsLayout.addWidget(self.storageButton)

        self.parent.toolBox.plugins = self.parent.plugins
        self.tool = ToolWidget(self.parent.toolBox)
        self.parent.toolBox.addItem(self.tool, 'Storage')

        self.parent.plugins.mime_register('inode/directory', self.name)

        self.daemon = Daemon(self.parent)
        self.connect(self.daemon, QtCore.SIGNAL('mounted'), self.tool.add_button)
        self.connect(self.daemon, QtCore.SIGNAL('unmounted'), self.tool.remove_button)
        self.daemon.start()

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
            settings.set('storage/view', self.widget.viewBox.currentText())
            self.widget.deleteLater()
            self.widget = None
            self.parent.tabWidget.removeTab(index)

    def unload(self):
        ''' Unload plugin '''
        self.applicationsLayout.removeWidget(self.storageButton)
        #self.tool.destroy()
        self.daemon.quit()
        self.close()
