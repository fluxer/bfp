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
        self.homeButton.setToolTip(self.tr('Go to Home directory'))
        self.homeButton.clicked.connect(lambda: self.path_open(self.shome))
        self.viewBox = QtGui.QComboBox()
        self.viewBox.addItem(self.tr('Icons view'))
        self.viewBox.addItem(self.tr('List view'))
        self.viewBox.setToolTip(self.tr('Set view mode of files and directories'))
        self.viewBox.currentIndexChanged.connect(self.change_view)
        self.hiddenBox = QtGui.QCheckBox(self.tr('Show hidden'))
        self.hiddenBox.setToolTip(self.tr('Set wheather to show or hide hidden (dot) files and directories'))
        self.hiddenBox.stateChanged.connect(self.change_hidden)
        self.addressBar = QtGui.QLineEdit()
        self.addressBar.setReadOnly(True)
        self.addressBar.setToolTip(self.tr('Path to current directory'))
        self.secondLayout.addWidget(self.homeButton)
        self.secondLayout.addWidget(self.viewBox)
        self.secondLayout.addWidget(self.hiddenBox)
        self.secondLayout.addWidget(self.addressBar)
        self.mainLayout = QtGui.QGridLayout()
        self.mainLayout.addLayout(self.secondLayout, 0, 0)
        self.storageView = QtGui.QListView()
        self.mainLayout.addWidget(self.storageView)
        self.setLayout(self.mainLayout)

        self.model = QtGui.QFileSystemModel()
        index = self.viewBox.findText(settings.get('storage/view', \
            self.tr('Icons view')))
        self.viewBox.setCurrentIndex(index)
        # the index does not change if settings point to first
        self.change_view()
        self.hiddenBox.setChecked(settings.get_bool('storage/show_hidden', False))
        # set the initial model filter
        self.change_hidden()
        self.storageView.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.storageView.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        self.storageView.setModel(self.model)
        self.storageView.doubleClicked.connect(self.path_open)
        self.storageView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.storageView.customContextMenuRequested.connect(self.menu_show)

        self.icon_execute = general.get_icon('system-run')
        self.icon_open = general.get_icon('document-open')
        self.icon_open_with = general.get_icon('application-default-icon')
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

    def change_hidden(self):
        if self.hiddenBox.isChecked():
            self.model.setFilter(QtCore.QDir.AllEntries | QtCore.QDir.NoDot \
                | QtCore.QDir.Hidden)
        else:
            self.model.setFilter(QtCore.QDir.AllEntries | QtCore.QDir.NoDot)

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
        for svar in self.storageView.selectedIndexes():
            splugin, bok = QtGui.QInputDialog.getItem(self, \
                self.tr('Open with'), '', self.parent.plugins.plugins_all, \
                editable=False)
            if bok:
                self.parent.plugins.plugin_open_with(splugin, \
                    str(self.model.filePath(svar)))

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
                    shutil.copytree(svar, os.path.join(sdest, os.path.basename(svar)))
                    misc.dir_remove(svar)
                else:
                    shutil.copy2(svar, os.path.join(sdest, os.path.basename(svar)))
                    os.unlink(svar)
        elif self.copy:
            for svar in self.copy:
                if os.path.isdir(svar):
                    shutil.copytree(svar, os.path.join(sdest, os.path.basename(svar)))
                else:
                    shutil.copy2(svar, os.path.join(sdest, os.path.basename(svar)))
        else:
            # FIXME: it will break on paths with spaces,
            #        is it OK to use \n in the clipboard content to solve this?
            # FIXME: download URLs
            for svar in self.clipboard.text().split(' '):
                if os.path.isdir(svar):
                    shutil.copytree(svar, os.path.join(sdest, os.path.basename(svar)))
                else:
                    shutil.copy2(svar, os.path.join(sdest, os.path.basename(svar)))

    def menu_rename(self):
        ''' Rename files/directories '''
        # FIXME: _check_exists()
        sdest = str(self.model.rootPath())
        for svar in self.storageView.selectedIndexes():
            snvar, ok = QtGui.QInputDialog.getText(self, self.tr('Rename'), \
                self.tr('New name:'), QtGui.QLineEdit.Normal)
            if ok:
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
            sfile = str(self.model.filePath(svar))
            info = QtCore.QFileInfo(sfile)
            executable = str(info.isExecutable())
            modified = QtCore.QDateTime.toString(info.lastModified())
            read = QtCore.QDateTime.toString(info.lastRead())
            mime = misc.file_mime(sfile)
            plugin = self.parent.plugins.mime_plugin(mime)
            QtGui.QMessageBox.information(self, self.tr('Information'), \
                'Executable: %s\nModified: %s\nRead: %s\nMime: %s\nPlugin: %s' % \
                (executable, modified, read, mime, plugin))

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
        self.storageMenu = QtGui.QMenu()
        sfile = None
        for svar in self.storageView.selectedIndexes():
            sfile = str(self.model.filePath(svar))

        if sfile:
            if os.access(sfile, os.X_OK) and os.path.isfile(sfile):
                self.storageMenu.addAction(self.icon_execute, \
                    self.tr('Execute'), self.menu_execute)
            self.storageMenu.addAction(self.icon_open, \
                self.tr('Open'), self.menu_open)
            self.storageMenu.addAction(self.icon_open_with, \
                self.tr('Open with'), self.menu_open_with)
            self.storageMenu.addSeparator()

            if os.access(sfile, os.W_OK):
                self.storageMenu.addAction(self.icon_cut, \
                    self.tr('Cut'), self.menu_cut)
            if os.access(sfile, os.R_OK):
                self.storageMenu.addAction(self.icon_copy, \
                    self.tr('Copy'), self.menu_copy)
            if (self.cut or self.copy or self.clipboard.text()) and os.access(self.model.rootPath(), os.W_OK):
                self.storageMenu.addAction(self.icon_paste, \
                    self.tr('Paste'), self.menu_paste)
            if os.access(sfile, os.R_OK) and os.access(self.model.rootPath(), os.W_OK):
                self.storageMenu.addAction(self.icon_rename, \
                    self.tr('Rename'), self.menu_rename)
                self.storageMenu.addAction(self.icon_delete, \
                    self.tr('Delete'), self.menu_delete)
            if os.access(sfile, os.R_OK):
                self.storageMenu.addAction(self.icon_properties, \
                    self.tr('Properties'), self.menu_properties)
            self.storageMenu.addSeparator()

        if os.access(self.model.rootPath(), os.W_OK):
            self.storageMenu.addSeparator()
            self.storageMenu.addAction(self.icon_new_file, \
                self.tr('New file'), self.menu_new_file)
            self.storageMenu.addAction(self.icon_new_dir, \
                self.tr('New directory'), self.menu_new_directory)

        if sfile and misc.archive_supported(sfile):
            # FIXME: implement
            pass

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
                        self.emit(QtCore.SIGNAL('failed'), str(detail))
            for f in before:
                if '.tmp' in f:
                    continue
                if not f in after:
                    try:
                        system.do_unmount('/dev/' + f)
                        self.emit(QtCore.SIGNAL('unmounted'), '/media/' + f)
                    except Exception as detail:
                        self.emit(QtCore.SIGNAL('failed'), str(detail))
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
        self.version = "0.9.35 (f7385d6)"
        self.description = self.tr('Storage management plugin')
        self.icon = general.get_icon('system-file-manager')
        self.widget = None

        self.storageButton = QtGui.QPushButton(self.icon, '')
        self.storageButton.setToolTip(self.description)
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
        self.connect(self.daemon, QtCore.SIGNAL('failed'), self.parent.plugins.notify_critical)
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
            settings.set('storage/show_hidden', self.widget.hiddenBox.isChecked())
            self.widget.deleteLater()
            self.widget = None
            self.parent.tabWidget.removeTab(index)

    def unload(self):
        ''' Unload plugin '''
        self.applicationsLayout.removeWidget(self.storageButton)
        self.daemon.quit()
        self.tool.deleteLater()
        self.close()
