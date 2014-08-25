#!/bin/pyhton2

from PyQt4 import QtCore, QtGui
import libworkspace, libpackage, libspm
general = libworkspace.General()
database = libpackage.Database()

class Thread(QtCore.QThread):
    ''' Worker thread '''
    def __init__(self, parent, func):
        super(Thread, self).__init__()
        self.parent = parent
        self.func = func

    def run(self):
        try:
            self.func()
        except SystemExit:
            # HACK!!! ignore system exit calls
            pass
        except Exception as detail:
            self.emit(QtCore.SIGNAL('failed'), str(detail))

class Widget(QtGui.QWidget):
    ''' Tab widget '''
    def __init__(self, parent, spath=None):
        super(Widget, self).__init__()
        self.parent = parent
        self.spath = spath
        self.name = 'package'

        self.mainLayout = QtGui.QGridLayout()
        self.targetsList = QtGui.QListWidget()
        self.targetsList.currentItemChanged.connect(self.refresh_buttons)
        self.infoTab = QtGui.QTabWidget()
        self.footprintEdit = QtGui.QTextEdit()
        self.footprintEdit.setReadOnly(True)
        self.infoTab.insertTab(0, self.footprintEdit, 'Footprint')
        self.metadataEdit = QtGui.QTextEdit()
        self.footprintEdit.setReadOnly(True)
        self.infoTab.insertTab(0, self.metadataEdit, 'Metadata')
        self.infoTab.setCurrentIndex(0)
        self.secondLayout = QtGui.QHBoxLayout()
        self.syncButton = QtGui.QPushButton(general.get_icon('view-refresh'), '')
        self.syncButton.setToolTip(self.tr('Sync package repositories'))
        self.syncButton.clicked.connect(self.targets_sync)
        self.updateButton = QtGui.QPushButton(general.get_icon('system-software-update'), '')
        self.updateButton.setToolTip(self.tr('Update system packages'))
        self.updateButton.clicked.connect(self.targets_update)
        self.buildButton = QtGui.QPushButton(general.get_icon('system-run'), '')
        self.buildButton.setToolTip(self.tr('Build selected package(s)'))
        self.buildButton.clicked.connect(self.targets_build)
        self.removeButton = QtGui.QPushButton(general.get_icon('edit-delete'), '')
        self.removeButton.setToolTip(self.tr('Remove selected package(s)'))
        self.removeButton.clicked.connect(self.targets_remove)
        self.targetsFilter = QtGui.QComboBox()
        self.targetsFilter.addItems((self.tr('all'), self.tr('updates'), \
            self.tr('local'), self.tr('candidates'), self.tr('unneeded')))
        self.targetsFilter.addItems(database.remote_aliases())
        self.targetsFilter.setToolTip(self.tr('Set packages filter'))
        self.targetsFilter.currentIndexChanged.connect(self.refresh_targets)
        self.mainLayout.addLayout(self.secondLayout, 0, 0)
        self.secondLayout.addWidget(self.syncButton)
        self.secondLayout.addWidget(self.updateButton)
        self.secondLayout.addWidget(self.buildButton)
        self.secondLayout.addWidget(self.removeButton)
        self.secondLayout.addWidget(self.targetsFilter)
        self.mainLayout.addWidget(self.targetsList)
        self.mainLayout.addWidget(self.infoTab)
        self.progressBar = QtGui.QProgressBar()
        self.progressBar.setRange(0, 1)
        self.progressBar.hide()
        self.mainLayout.addWidget(self.progressBar)
        self.setLayout(self.mainLayout)

        self.refresh_all()

    def refresh_targets(self):
        ''' Refresh targets list view '''
        self.targetsList.clear()
        current = str(self.targetsFilter.currentText())
        if current == self.tr('all'):
            targets = database.remote_all(basename=True)
        elif current == self.tr('updates'):
            targets = []
            for target in database.local_all(basename=True):
                if not database.local_uptodate(target):
                    targets.append(target)
        elif current == self.tr('local'):
            targets = database.local_all(basename=True)
        elif current == self.tr('candidates'):
            targets = []
            for target in database.remote_all(basename=True):
                if not database.local_installed(target):
                    targets.append(target)
        elif current == self.tr('unneeded'):
            targets = []
            for target in database.local_all(basename=True):
                if not database.local_rdepends(target):
                    targets.append(target)
        else:
            targets = database.remote_alias(current)

        for target in targets:
            self.targetsList.addItem(target)

        self.targetsList.setCurrentRow(0)

    def refresh_buttons(self):
        ''' Refresh buttons depending on selected target, also metadata and footprint '''
        self.buildButton.setEnabled(False)
        self.removeButton.setEnabled(False)
        item = self.targetsList.currentItem()
        if not item:
            return
        current = str(item.text())
        self.metadataEdit.setText('')
        self.footprintEdit.setText('')
        if database.local_installed(current):
            self.removeButton.setEnabled(True)
            self.metadataEdit.append('Version: ' + database.local_metadata(current, 'version'))
            self.metadataEdit.append('Description: ' + database.local_metadata(current, 'description'))
            self.metadataEdit.append('Depends: ' + database.local_metadata(current, 'depends'))
            self.metadataEdit.append('Reverse: ' + str(database.local_rdepends(current)))
            self.metadataEdit.append('Size: ' + database.local_metadata(current, 'size'))
            self.footprintEdit.setText(database.local_footprint(current))
        else:
            self.removeButton.setEnabled(False)
            self.metadataEdit.append('Version: ' + database.remote_metadata(current, 'version'))
            self.metadataEdit.append('Description: ' + database.remote_metadata(current, 'description'))
            self.metadataEdit.append('Depends: ' + str(database.remote_metadata(current, 'depends')))
            self.metadataEdit.append('Make depends: ' + str(database.remote_metadata(current, 'makedepends')))
            self.metadataEdit.append('Sources: ' + str(database.remote_metadata(current, 'sources')))
            self.metadataEdit.append('Options: ' + str(database.remote_metadata(current, 'options')))
            self.metadataEdit.append('Backup: ' + str(database.remote_metadata(current, 'backup')))
        self.buildButton.setEnabled(True)

    def refresh_all(self):
        ''' Refresh both targets view and buttons '''
        self.refresh_targets()
        self.refresh_buttons()

    def worker_started(self):
        ''' Worker started slot '''
        self.progressBar.setRange(0, 0)
        self.progressBar.show()
        self.syncButton.setEnabled(False)
        self.updateButton.setEnabled(False)
        self.buildButton.setEnabled(False)
        self.removeButton.setEnabled(False)

    def worker_stopped(self):
        ''' Worker stopped slot '''
        self.progressBar.setRange(0, 1)
        self.progressBar.hide()
        self.syncButton.setEnabled(True)
        self.updateButton.setEnabled(True)
        self.refresh_all()

    def worker(self, func):
        ''' Main worker wrapper '''
        self.thread = Thread(self, func)
        self.thread.finished.connect(self.worker_stopped)
        self.connect(self.thread, QtCore.SIGNAL('failed'), self.parent.plugins.notify_critical)
        self.worker_started()
        self.thread.start()

    def targets_sync(self):
        ''' Sync repositories '''
        try:
            m = libspm.Repo(libspm.REPOSITORIES, True, True, False)
            self.worker(m.main)
        except Exception as detail:
            self.parent.plugins.notify_critical(str(detail))

    def targets_update(self):
        ''' Update all installed targets '''
        try:
            targets = database.local_all(basename=True)
            m = libspm.Source(targets, do_clean=True, do_prepare=True,
                do_compile=True, do_check=False, do_install=True, do_merge=True,
                do_remove=False, do_depends=True, do_reverse=True, do_update=True)
            self.worker(m.main)
        except Exception as detail:
            self.parent.plugins.notify_critical(str(detail))

    def targets_build(self):
        ''' Build a target '''
        try:
            targets = [str(self.targetsList.currentItem().text())]
            m = libspm.Source(targets, do_clean=True, do_prepare=True,
                do_compile=True, do_check=False, do_install=True, do_merge=True,
                do_remove=False, do_depends=True, do_reverse=True, do_update=False)
            self.worker(m.main)
        except Exception as detail:
            self.parent.plugins.notify_critical(str(detail))

    def targets_remove(self):
        ''' Remove a target '''
        try:
            targets = [str(self.targetsList.currentItem().text())]
            m = libspm.Source(targets, do_clean=False, do_prepare=False,
                do_compile=False, do_check=False, do_install=False, do_merge=False,
                do_remove=True, do_depends=False, do_reverse=True, do_update=False)
            self.worker(m.main)
        except Exception as detail:
            self.parent.plugins.notify_critical(str(detail))


class Plugin(QtCore.QObject):
    ''' Plugin handler '''
    def __init__(self, parent):
        super(Plugin, self).__init__()
        self.parent = parent
        self.name = 'package'
        self.version = "0.9.33 (f765d0a)"
        self.description = self.tr('Package manager plugin')
        self.icon = general.get_icon('package-x-generic')
        self.widget = None

        self.packageButton = QtGui.QPushButton(self.icon, '')
        self.packageButton.setToolTip(self.description)
        self.packageButton.clicked.connect(self.open)
        self.applicationsLayout = self.parent.toolBox.widget(1).layout()
        self.applicationsLayout.addWidget(self.packageButton)

    def open(self, spath):
        ''' Open path in new tab '''
        index = self.parent.tabWidget.currentIndex()+1
        self.widget = Widget(self.parent, spath)
        self.parent.tabWidget.insertTab(index, self.widget, self.icon, self.tr('Package'))
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
        self.applicationsLayout.removeWidget(self.packageButton)
        self.close()
