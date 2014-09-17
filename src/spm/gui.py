#!/usr/bin/python2

from PyQt4 import QtCore, QtGui
import sys
import ConfigParser

import gui_ui
import libspm
import libmisc, libmessage, libpackage
database = libpackage.Database()
message = libmessage.Message()
misc = libmisc.Misc()

app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()
ui = gui_ui.Ui_MainWindow()
ui.setupUi(MainWindow)

class Worker(QtCore.QThread):
    def __init__(self, parent=None, func=None):
        super(Worker, self).__init__(parent)
        self.func = func

    def run(self):
        try:
            self.func()
        except SystemExit:
            pass
        except Exception as detail:
            self.emit(QtCore.SIGNAL('failed'), str(detail))

def MessageCritical(msg):
    QtGui.QMessageBox.critical(MainWindow, 'Critical', msg)

def DisableWidgets():
    ui.updateButton.setEnabled(False)
    ui.buildButton.setEnabled(False)
    ui.removeButton.setEnabled(False)
    ui.syncButton.setEnabled(False)
    ui.progressBar.setRange(0, 0)
    ui.progressBar.show()

def EnableWidgets():
    ui.updateButton.setEnabled(True)
    ui.buildButton.setEnabled(True)
    ui.removeButton.setEnabled(True)
    ui.syncButton.setEnabled(True)
    ui.progressBar.setRange(0, 1)
    ui.progressBar.hide()

def RefreshSearch():
    ui.searchBox.clear()
    ui.searchEdit.clear()
    current = str(ui.filtersBox.currentText())
    if current == 'local' or current == 'unneeded' or current == 'updates':
        ui.searchBox.addItems(('name', 'version', 'description', 'depends', \
            'reverse'))
    else:
        ui.searchBox.addItems(('name', 'version', 'description', 'depends', \
            'makedepends', 'checkdepends', 'sources', 'options', 'backup'))

def RefreshTargets():
    ui.targetsView.clear()
    current = str(ui.filtersBox.currentText())
    targets = []
    if current == 'all':
        targets = database.remote_all(basename=True)
    elif current == 'updates':
        for target in database.local_all(basename=True):
            if not database.local_uptodate(target):
                targets.append(target)
    elif current == 'local':
        targets = database.local_all(basename=True)
    elif current == 'unneeded':
        for target in database.local_all(basename=True):
            if not database.local_rdepends(target):
                targets.append(target)
    elif current == 'candidates':
        for target in database.remote_all(basename=True):
            if not database.local_installed(target):
                targets.append(target)
    else:
        targets = database.remote_alias(current)

    for target in targets:
        ui.targetsView.addItem(target)
    RefreshSearch()
    ui.targetsView.setCurrentRow(0)

def Refresh():
    ui.filtersBox.clear()
    ui.targetsView.clear()
    ui.repositoriesText.clear()
    ui.mirrorsText.clear()

    ui.filtersBox.addItem('all')
    ui.filtersBox.addItem('updates')
    ui.filtersBox.addItem('local')
    ui.filtersBox.addItem('unneeded')
    ui.filtersBox.addItem('candidates')
    ui.filtersBox.setCurrentIndex(0)
    for alias in database.remote_aliases():
        ui.filtersBox.addItem(alias)

    for target in database.remote_all(basename=True):
        ui.targetsView.addItem(target)

    ui.repositoriesText.setPlainText(misc.file_read('/etc/spm/repositories.conf'))
    ui.mirrorsText.setPlainText(misc.file_read('/etc/spm/mirrors.conf'))

    #ui.CacheDirEdit.setText(libspm.CACHE_DIR)
    #ui.BuildDirEdit.setText(libspm.BUILD_DIR)
    #ui.IgnoreTargetsEdit.setText(libspm.IGNORE)
    #ui.ConnectionTimeoutBox.setValue(libspm.TIMEOUT)
    #ui.UseMirrorsBox.setCheckState(libspm.MIRROR)
    #ui.ExternalFetcherBox.setCheckState(libspm.EXTERNAL)
    #ui.CompressManBox.setCheckState(libspm.COMPRESS_MAN)
    #ui.StripBinariesBox.setCheckState(libspm.STRIP_BINARIES)
    #ui.StripSharedBox.setCheckState(libspm.STRIP_SHARED)
    #ui.StripStaticBox.setCheckState(libspm.STRIP_STATIC)
    #ui.IgnoreMissingBox.setCheckState(libspm.IGNORE_MISSING)
    #ui.ConflictsBox.setCheckState(libspm.CONFLICTS)
    #ui.BackupBox.setCheckState(libspm.BACKUP)
    #ui.ScriptsBox.setCheckState(libspm.SCRIPTS)

def SearchMetadata():
    field = str(ui.searchBox.currentText())
    regexp = str(ui.searchEdit.text())
    targets = []
    if not regexp:
        RefreshTargets()
        return

    for index in xrange(ui.targetsView.count()):
        target = str(ui.targetsView.item(index).text())
        if field == 'name':
            if misc.string_search(regexp, target, escape=False, exact=False):
                targets.append(target)
        elif database.local_installed(target):
            if misc.string_search(regexp, \
                database.local_metadata(target, field), \
                escape=False, exact=False):
                targets.append(target)
        else:
            if misc.string_search(regexp, \
                database.remote_metadata(target, field), \
                escape=False, exact=False):
                targets.append(target)

    ui.targetsView.clear()
    for target in targets:
        ui.targetsView.addItem(target)
    ui.targetsView.setCurrentRow(0)

def RefreshWidgets():
    current = ui.targetsView.currentItem()
    if not current:
        return
    target = str(current.text())

    ui.metadataText.clear()
    ui.footprintText.clear()
    if database.local_installed(target):
        ui.removeButton.setEnabled(True)
        ui.metadataText.append('Version: ' + database.local_metadata(target, 'version'))
        ui.metadataText.append('Description: ' + database.local_metadata(target, 'description'))
        ui.metadataText.append('Depends: ' + str(database.local_metadata(target, 'depends')))
        ui.metadataText.append('Reverse: ' + misc.string_convert(database.local_rdepends(target)))
        ui.metadataText.append('Size: ' + database.local_metadata(target, 'size'))
        ui.footprintText.setPlainText(database.local_footprint(target))
    else:
        ui.removeButton.setEnabled(False)
        ui.metadataText.append('Version: ' + database.remote_metadata(target, 'version'))
        ui.metadataText.append('Description: ' + database.remote_metadata(target, 'description'))
        ui.metadataText.append('Depends: ' + misc.string_convert(database.remote_metadata(target, 'depends')))
        ui.metadataText.append('Make depends: ' + misc.string_convert(database.remote_metadata(target, 'makedepends')))
        ui.metadataText.append('Check depends: ' + misc.string_convert(database.remote_metadata(target, 'checkdepends')))
        ui.metadataText.append('Sources: ' + misc.string_convert(database.remote_metadata(target, 'sources')))
        ui.metadataText.append('Options: ' + misc.string_convert(database.remote_metadata(target, 'options')))
        ui.metadataText.append('Backup: ' + misc.string_convert(database.remote_metadata(target, 'backup')))

def Update():
    targets = database.local_all(basename=True)
    m = libspm.Source(targets, do_clean=True, do_prepare=True, \
        do_compile=True, do_check=False, do_install=True, do_merge=True, \
        do_remove=False, do_depends=True, do_reverse=True, do_update=True)
    worker = Worker(app, m.main)
    worker.finished.connect(EnableWidgets)
    worker.finished.connect(RefreshTargets)
    app.connect(worker, QtCore.SIGNAL('failed'), MessageCritical)
    DisableWidgets()
    worker.start()

def Build():
    targets = [str(ui.targetsView.currentItem().text())]
    m = libspm.Source(targets, do_clean=True, do_prepare=True, \
        do_compile=True, do_check=False, do_install=True, do_merge=True, \
        do_remove=False, do_depends=True, do_reverse=True, do_update=False)
    worker = Worker(app, m.main)
    worker.finished.connect(EnableWidgets)
    worker.finished.connect(RefreshWidgets)
    worker.finished.connect(RefreshTargets)
    app.connect(worker, QtCore.SIGNAL('failed'), MessageCritical)
    DisableWidgets()
    worker.start()

def Remove():
    targets = [str(ui.targetsView.currentItem().text())]
    m = libspm.Source(targets, do_clean=False, do_prepare=False, \
        do_compile=False, do_check=False, do_install=False, do_merge=False, \
        do_remove=True, do_depends=False, do_reverse=True, do_update=False)
    worker = Worker(app, m.main)
    worker.finished.connect(EnableWidgets)
    worker.finished.connect(RefreshWidgets)
    worker.finished.connect(RefreshTargets)
    app.connect(worker, QtCore.SIGNAL('failed'), MessageCritical)
    DisableWidgets()
    worker.start()

def SyncRepos():
    m = libspm.Repo(libspm.REPOSITORIES, do_clean=True, do_sync=True, \
        do_update=False)
    worker = Worker(app, m.main)
    worker.finished.connect(EnableWidgets)
    worker.finished.connect(RefreshWidgets)
    worker.finished.connect(RefreshTargets)
    app.connect(worker, QtCore.SIGNAL('failed'), MessageCritical)
    DisableWidgets()
    worker.start()


def ChangeSettings():
    try:
        conf = ConfigParser.SafeConfigParser()
        conf.read('/etc/spm.conf')
        conf.set('spm', 'CACHE_DIR', str(ui.CacheDirEdit.text()))
        conf.set('spm', 'BUILD_DIR', str(ui.BuildDirEdit.text()))
        conf.set('spm', 'IGNORE', str(ui.IgnoreTargetsEdit.text()))
        conf.set('prepare', 'MIRROR', str(ui.UseMirrorsBox.isChecked()))
        conf.set('prepare', 'TIMEOUT', str(ui.ConnectionTimeoutBox.value()))
        conf.set('prepare', 'EXTERNAL', str(ui.ExternalFetcherBox.isChecked()))
        conf.set('install', 'COMPRESS_MAN', str(ui.CompressManBox.isChecked()))
        conf.set('install', 'STRIP_BINARIES', str(ui.StripBinariesBox.isChecked()))
        conf.set('install', 'STRIP_SHARED', str(ui.StripSharedBox.isChecked()))
        conf.set('install', 'STRIP_STATIC', str(ui.StripStaticBox.isChecked()))
        conf.set('install', 'IGNORE_MISSING', str(ui.IgnoreMissingBox.isChecked()))
        conf.set('merge', 'CONFLICTS', str(ui.ConflictsBox.isChecked()))
        conf.set('merge', 'BACKUP', str(ui.BackupBox.isChecked()))
        conf.set('merge', 'SCRIPTS', str(ui.ScriptsBox.isChecked()))

        with open('/etc/spm.conf', 'wb') as libspmfile:
            conf.write(libspmfile)
        reload(libspm)
    except SystemExit:
        pass
    except Exception as detail:
        MessageCritical(str(detail))

def ChangeRepos():
    try:
        misc.file_write('/etc/spm/repositories.conf', str(ui.repositoriesText.toPlainText()))
        reload(libspm)
    except SystemExit:
        pass
    except Exception as detail:
        MessageCritical(str(detail))

def ChangeMirrors():
    try:
        misc.file_write('/etc/spm/mirrors.conf', str(ui.mirrorsText.toPlainText()))
        reload(libspm)
    except SystemExit:
        pass
    except Exception as detail:
        MessageCritical(str(detail))

Refresh()

ui.updateButton.clicked.connect(Update)
ui.buildButton.clicked.connect(Build)
ui.removeButton.clicked.connect(Remove)
ui.syncButton.clicked.connect(SyncRepos)

#ui.CacheDirEdit.textChanged.connect(ChangeSettings)
#ui.BuildDirEdit.textChanged.connect(ChangeSettings)
#ui.IgnoreTargetsEdit.textChanged.connect(ChangeSettings)
#ui.ConnectionTimeoutBox.valueChanged.connect(ChangeSettings)
#ui.UseMirrorsBox.clicked.connect(ChangeSettings)
#ui.ExternalFetcherBox.clicked.connect(ChangeSettings)
#ui.CompressManBox.clicked.connect(ChangeSettings)
#ui.StripBinariesBox.clicked.connect(ChangeSettings)
#ui.StripSharedBox.clicked.connect(ChangeSettings)
#ui.StripStaticBox.clicked.connect(ChangeSettings)
#ui.IgnoreMissingBox.clicked.connect(ChangeSettings)
#ui.ConflictsBox.clicked.connect(ChangeSettings)
#ui.BackupBox.clicked.connect(ChangeSettings)
#ui.ScriptsBox.clicked.connect(ChangeSettings)

ui.searchEdit.returnPressed.connect(SearchMetadata)
ui.repositoriesText.textChanged.connect(ChangeRepos)
ui.mirrorsText.textChanged.connect(ChangeMirrors)

ui.targetsView.currentItemChanged.connect(RefreshWidgets)
ui.filtersBox.currentIndexChanged.connect(RefreshTargets)

RefreshSearch()
ui.targetsView.setCurrentRow(0)
ui.progressBar.setRange(0, 1)
ui.progressBar.hide()

MainWindow.show()
sys.exit(app.exec_())
