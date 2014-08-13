#!/bin/pyhton2

from PyQt4 import QtCore, QtGui
import libworkspace, libpackage, libspm
general = libworkspace.General()
database = libpackage.Database()

class Widget(QtGui.QWidget):
    ''' Tab widget '''
    def __init__(self, parent, spath=None):
        super(Widget, self).__init__()
        self.parent = parent
        self.spath = spath
        self.name = 'package'

        mainLayout = QtGui.QGridLayout()
        self.targetsList = QtGui.QListWidget()
        self.targetsList.currentItemChanged.connect(self.refresh_buttons)
        self.targetsFilter = QtGui.QComboBox()
        self.targetsFilter.addItem('all')
        self.targetsFilter.addItem('local')
        self.targetsFilter.addItem('unneeded')
        self.targetsFilter.addItem('candidates')
        self.targetsFilter.currentIndexChanged.connect(self.refresh_targets)
        self.infoTab = QtGui.QTabWidget()
        self.footprintEdit = QtGui.QTextEdit()
        self.footprintEdit.setReadOnly(True)
        self.infoTab.insertTab(0, self.footprintEdit, 'Footprint')
        self.metadataEdit = QtGui.QTextEdit()
        self.footprintEdit.setReadOnly(True)
        self.infoTab.insertTab(0, self.metadataEdit, 'Metadata')
        secondLayout = QtGui.QHBoxLayout()
        self.syncButton = QtGui.QPushButton(general.get_icon('reload'), '')
        self.syncButton.clicked.connect(self.targets_sync)
        self.updateButton = QtGui.QPushButton(general.get_icon('system-software-update'), '')
        self.updateButton.clicked.connect(self.targets_update)
        self.buildButton = QtGui.QPushButton(general.get_icon('system-run'), '')
        self.buildButton.clicked.connect(self.targets_build)
        self.removeButton = QtGui.QPushButton(general.get_icon('remove'), '')
        self.removeButton.clicked.connect(self.targets_remove)
        secondLayout.addWidget(self.syncButton)
        secondLayout.addWidget(self.updateButton)
        secondLayout.addWidget(self.buildButton)
        secondLayout.addWidget(self.removeButton)
        mainLayout.addWidget(self.targetsList)
        mainLayout.addWidget(self.targetsFilter)
        mainLayout.addWidget(self.infoTab)
        mainLayout.addLayout(secondLayout, QtCore.Qt.AlignBottom, 0)
        self.setLayout(mainLayout)

        self.refresh_all()

    def refresh_targets(self):
        self.targetsList.clear()
        current = str(self.targetsFilter.currentText())
        if current == 'all':
            targets = database.remote_all(basename=True)
        elif current == 'local':
            targets = database.local_all(basename=True)
        elif current == 'unneeded':
            targets = []
            for target in database.local_all(basename=True):
                if not database.local_rdepends(target):
                    targets.append(target)
        elif current == 'candidates':
            targets = []
            for target in database.remote_all(basename=True):
                if not database.local_installed(target):
                    targets.append(target)
        else:
            targets = database.remote_alias(current)

        for target in targets:
            self.targetsList.addItem(target)

        self.targetsList.setCurrentRow(0)

    def refresh_buttons(self):
        item = self.targetsList.currentItem()
        if not item:
            return
        current = str(item.text())
        self.metadataEdit.setText('')
        self.footprintEdit.setText('')
        if database.local_installed(current):
            self.removeButton.setEnabled(False)
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

    def refresh_all(self):
        self.refresh_targets()
        self.refresh_buttons()

    def targets_sync(self):
        try:
            m = libspm.Repo(libspm.REPOSITORIES, True, True, False)
            m.main()
        except Exception as detail:
            QtGui.QMessageBox.critical(self, self.tr('Critical'), str(detail))
        finally:
            self.refresh_all()

    def targets_update(self):
        try:
            targets = database.local_all(basename=True)
            m = libspm.Source(targets, do_clean=True, do_prepare=True,
                do_compile=True, do_check=False, do_install=True, do_merge=True,
                do_remove=False, do_depends=True, do_reverse=True, do_update=True)
            m.main()
        except Exception as detail:
            QtGui.QMessageBox.critical(self, self.tr('Critical'), str(detail))
        finally:
            self.refresh_all()

    def targets_build(self):
        try:
            targets = [str(self.targetsList.currentItem().text())]
            m = libspm.Source(targets, do_clean=True, do_prepare=True,
                do_compile=True, do_check=False, do_install=True, do_merge=True,
                do_remove=False, do_depends=True, do_reverse=True, do_update=False)
            m.main()
        except Exception as detail:
            QtGui.QMessageBox.critical(self, self.tr('Critical'), str(detail))
        finally:
            self.refresh_all()

    def targets_remove(self):
        try:
            targets = [str(self.targetsList.currentItem().text())]
            m = libspm.Source(targets, do_clean=False, do_prepare=False,
                do_compile=False, do_check=False, do_install=False, do_merge=False,
                do_remove=True, do_depends=False, do_reverse=True, do_update=False)
            m.main()
        except Exception as detail:
            QtGui.QMessageBox.critical(self, self.tr('Critical'), str(detail))
        finally:
            self.refresh_all()

class Plugin(QtCore.QObject):
    ''' Plugin handler '''
    def __init__(self, parent):
        super(Plugin, self).__init__()
        self.parent = parent
        self.name = 'package'
        self.version = '0.0.1'
        self.description = self.tr('Package manager plugin')
        self.icon = general.get_icon('package')
        self.widget = None

        self.packageButton = QtGui.QPushButton(general.get_icon('package'), '')
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
            self.widget.destroy()
            self.parent.tabWidget.removeTab(index)

    def unload(self):
        ''' Unload plugin '''
        self.close()
