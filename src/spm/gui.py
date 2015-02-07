#!/bin/python2

from PyQt4 import QtCore, QtGui
import sys, pwd
if sys.version < '3':
    import ConfigParser as configparser
else:
    import configparser

# handle keyboard interrupt
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

import gui_ui
import libspm
import libmisc, libmessage, libpackage
database = libpackage.Database()
message = libmessage.Message()
misc = libmisc.Misc()
misc.CATCH = True
libspm.misc.CATCH = True

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

def MessageQuestion(*msg):
    return QtGui.QMessageBox.question(MainWindow, 'Question', \
        misc.string_convert(msg), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)

def MessageCritical(msg):
    if len(msg) < 400:
        return QtGui.QMessageBox.critical(MainWindow, 'Critical', msg)
    else:
        # FIXME: can not close with WM
        msgBox = QtGui.QMessageBox(MainWindow)
        msgBox.setWindowTitle('Critical')
        msgBox.setText('An error occured.')
        msgBox.setDetailedText(msg)
        # HACK!!! the size of the dialog is too small and setFixedHeight()
        # does not seem to work as it should, add a dummy space to force
        # the dialog to resize to a lenght of 400
        spacer = QtGui.QSpacerItem(400, 0, QtGui.QSizePolicy.Minimum, \
            QtGui.QSizePolicy.Expanding)
        layout = msgBox.layout()
        layout.addItem(spacer, layout.rowCount(), 0, 1, layout.columnCount())
        return msgBox.exec_()

def DisableWidgets():
    ui.searchEdit.setEnabled(False)
    ui.filtersBox.setEnabled(False)
    ui.updateButton.setEnabled(False)
    ui.buildButton.setEnabled(False)
    ui.mergeButton.setEnabled(False)
    ui.removeButton.setEnabled(False)
    ui.syncButton.setEnabled(False)
    ui.progressBar.setRange(0, 0)
    ui.progressBar.show()

def EnableWidgets():
    ui.searchEdit.setEnabled(True)
    ui.filtersBox.setEnabled(True)
    ui.updateButton.setEnabled(True)
    ui.buildButton.setEnabled(True)
    ui.mergeButton.setEnabled(True)
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

def RefreshTargetsReal():
    ui.targetsView.clear()
    current = str(ui.filtersBox.currentText())
    targets = []
    if current == 'all':
        targets = database.local_all(basename=True)
        for target in database.remote_all(basename=True):
            if not target in targets:
                targets.append(target)
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

    ui.targetsView.addItems(targets)
    RefreshSearch()
    ui.targetsView.setCurrentRow(0)

def RefreshTargets():
    worker = Worker(app, RefreshTargetsReal)
    worker.finished.connect(EnableWidgets)
    app.connect(worker, QtCore.SIGNAL('failed'), MessageCritical)
    DisableWidgets()
    worker.start()

def RefreshFiltersReal():
    ui.filtersBox.clear()
    ui.filtersBox.addItems(('all', 'updates', 'local', 'unneeded', 'candidates'))
    ui.filtersBox.setCurrentIndex(0)
    ui.filtersBox.addItems(database.remote_aliases())

def RefreshFilters():
    worker = Worker(app, RefreshFiltersReal)
    worker.finished.connect(EnableWidgets)
    worker.finished.connect(RefreshTargets)
    app.connect(worker, QtCore.SIGNAL('failed'), MessageCritical)
    DisableWidgets()
    worker.start()

def RefreshSettings():
    ui.repositoriesText.clear()
    ui.mirrorsText.clear()
    ui.repositoriesText.setPlainText(misc.file_read('/etc/spm/repositories.conf'))
    ui.mirrorsText.setPlainText(misc.file_read('/etc/spm/mirrors.conf'))

    ui.CacheDirEdit.setText(libspm.CACHE_DIR)
    ui.BuildDirEdit.setText(libspm.BUILD_DIR)
    ui.IgnoreTargetsEdit.setText(misc.string_convert(libspm.IGNORE))
    ui.ConnectionTimeoutBox.setValue(libspm.TIMEOUT)
    ui.UseMirrorsBox.setCheckState(libspm.MIRROR)
    ui.CompressManBox.setCheckState(libspm.COMPRESS_MAN)
    ui.StripBinariesBox.setCheckState(libspm.STRIP_BINARIES)
    ui.StripSharedBox.setCheckState(libspm.STRIP_SHARED)
    ui.StripStaticBox.setCheckState(libspm.STRIP_STATIC)
    ui.StripRPATHBox.setCheckState(libspm.STRIP_RPATH)
    ui.PythonCompileBox.setCheckState(libspm.PYTHON_COMPILE)
    ui.IgnoreMissingBox.setCheckState(libspm.IGNORE_MISSING)
    ui.ConflictsBox.setCheckState(libspm.CONFLICTS)
    ui.BackupBox.setCheckState(libspm.BACKUP)
    ui.ScriptsBox.setCheckState(libspm.SCRIPTS)
    ui.TriggersBox.setCheckState(libspm.TRIGGERS)

    for user in pwd.getpwall():
        ui.DemoteBox.addItem(user.pw_name)
    index = ui.DemoteBox.findText(libspm.DEMOTE)
    ui.DemoteBox.setCurrentIndex(index)

def SearchMetadata():
    current = str(ui.filtersBox.currentText())
    field = str(ui.searchBox.currentText())
    regexp = str(ui.searchEdit.text())
    targets = []
    if not regexp:
        RefreshTargets()
        return

    try:
        for index in xrange(ui.targetsView.count()):
            target = str(ui.targetsView.item(index).text())
            if field == 'name':
                if misc.string_search(regexp, target, escape=False, exact=False):
                    targets.append(target)
            elif current == 'local' or current == 'unneeded':
                data = database.local_metadata(target, field)
                if not data:
                    continue
                if misc.string_search(regexp, data, escape=False, exact=False):
                    targets.append(target)
            else:
                data = database.remote_metadata(target, field)
                if not data:
                    continue
                if misc.string_search(regexp, data, escape=False, exact=False):
                    targets.append(target)

        ui.targetsView.clear()
        ui.targetsView.addItems(sorted(targets))
        ui.targetsView.setCurrentRow(0)
    except Exception as detail:
        MessageCritical(str(detail))

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
        ui.metadataText.append('Reverse: ' + str(database.local_rdepends(target)))
        ui.metadataText.append('Size: ' + database.local_metadata(target, 'size'))
        ui.footprintText.setPlainText(database.local_footprint(target))
        ui.metadataText.append('Make depends: ' + str(database.remote_metadata(target, 'makedepends')))
        ui.metadataText.append('Check depends: ' + str(database.remote_metadata(target, 'checkdepends')))
        ui.metadataText.append('Sources: ' + str(database.remote_metadata(target, 'sources')))
        ui.metadataText.append('Options: ' + str(database.remote_metadata(target, 'options')))
        ui.metadataText.append('Backup: ' + str(database.remote_metadata(target, 'backup')))
    else:
        ui.removeButton.setEnabled(False)
        ui.metadataText.append('Version: ' + database.remote_metadata(target, 'version'))
        ui.metadataText.append('Description: ' + database.remote_metadata(target, 'description'))
        ui.metadataText.append('Depends: ' + str(database.remote_metadata(target, 'depends')))
        ui.metadataText.append('Make depends: ' + str(database.remote_metadata(target, 'makedepends')))
        ui.metadataText.append('Check depends: ' + str(database.remote_metadata(target, 'checkdepends')))
        ui.metadataText.append('Sources: ' + str(database.remote_metadata(target, 'sources')))
        ui.metadataText.append('Options: ' + str(database.remote_metadata(target, 'options')))
        ui.metadataText.append('Backup: ' + str(database.remote_metadata(target, 'backup')))

def Update():
    build = []
    targets = database.local_all(basename=True)
    for target in targets:
        if not database.local_uptodate(target):
            build.append(target)
    answer = MessageQuestion('The following targets will be updated:\n\n', \
        misc.string_convert(build), \
        '\n\nAre you sure you want to continue?')
    if not answer == QtGui.QMessageBox.Yes:
        return

    m = libspm.Source(build, do_clean=True, do_prepare=True, \
        do_compile=True, do_check=False, do_install=True, do_merge=True, \
        do_remove=False, do_depends=True, do_reverse=True, do_update=True)
    worker = Worker(app, m.main)
    worker.finished.connect(EnableWidgets)
    worker.finished.connect(RefreshTargets)
    app.connect(worker, QtCore.SIGNAL('failed'), MessageCritical)
    DisableWidgets()
    worker.start()

def Build():
    targets = []
    for s in ui.targetsView.selectedItems():
        item = str(s.text())
        targets.extend(database.remote_mdepends(item))
        targets.append(item)
    answer = MessageQuestion('The following targets will be build:\n\n', \
        misc.string_convert(targets), \
        '\n\nAre you sure you want to continue?')
    if not answer == QtGui.QMessageBox.Yes:
        return

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

def Install():
    targets = []
    for s in ui.targetsView.selectedItems():
        item = str(s.text())
        targets.extend(database.remote_mdepends(item))
        targets.append(item)
    answer = MessageQuestion('The following targets will be installed:\n\n', \
        misc.string_convert(targets), \
        '\n\nAre you sure you want to continue?')
    if not answer == QtGui.QMessageBox.Yes:
        return

    m = libspm.Binary(targets, do_merge=True, do_depends=True, \
        do_reverse=False, do_update=False)
    worker = Worker(app, m.main)
    worker.finished.connect(EnableWidgets)
    worker.finished.connect(RefreshWidgets)
    worker.finished.connect(RefreshTargets)
    app.connect(worker, QtCore.SIGNAL('failed'), MessageCritical)
    DisableWidgets()
    worker.start()

def Remove():
    targets = []
    for s in ui.targetsView.selectedItems():
        item = str(s.text())
        targets.extend(database.local_rdepends(item))
        targets.append(item)
    answer = MessageQuestion('The following targets will be removed:\n\n', \
        misc.string_convert(targets), \
        '\n\nAre you sure you want to continue?')
    if not answer == QtGui.QMessageBox.Yes:
        return

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


def ChangeCacheDir():
    spath = QtGui.QFileDialog.getExistingDirectory(MainWindow, 'Open', \
        libspm.CACHE_DIR)
    if not spath:
        return
    ui.CacheDirEdit.setText(spath)

def ChangeBuildDir():
    spath = QtGui.QFileDialog.getExistingDirectory(MainWindow, 'Open', \
        libspm.BUILD_DIR)
    if not spath:
        return
    ui.BuildDirEdit.setText(spath)

def ChangeSettings():
    try:
        conf = configparser.SafeConfigParser()
        conf.read('/etc/spm.conf')
        conf.set('spm', 'CACHE_DIR', str(ui.CacheDirEdit.text()))
        conf.set('spm', 'BUILD_DIR', str(ui.BuildDirEdit.text()))
        conf.set('spm', 'IGNORE', str(ui.IgnoreTargetsEdit.text()))
        conf.set('spm', 'DEMOTE', str(ui.DemoteBox.currentText()))
        conf.set('prepare', 'MIRROR', str(ui.UseMirrorsBox.isChecked()))
        conf.set('prepare', 'TIMEOUT', str(ui.ConnectionTimeoutBox.value()))
        conf.set('install', 'COMPRESS_MAN', str(ui.CompressManBox.isChecked()))
        conf.set('install', 'STRIP_BINARIES', str(ui.StripBinariesBox.isChecked()))
        conf.set('install', 'STRIP_SHARED', str(ui.StripSharedBox.isChecked()))
        conf.set('install', 'STRIP_STATIC', str(ui.StripStaticBox.isChecked()))
        conf.set('install', 'STRIP_RPATH', str(ui.StripRPATHBox.isChecked()))
        conf.set('install', 'PYTHON_COMPILE', str(ui.PythonCompileBox.isChecked()))
        conf.set('install', 'IGNORE_MISSING', str(ui.IgnoreMissingBox.isChecked()))
        conf.set('merge', 'CONFLICTS', str(ui.ConflictsBox.isChecked()))
        conf.set('merge', 'BACKUP', str(ui.BackupBox.isChecked()))
        conf.set('merge', 'SCRIPTS', str(ui.ScriptsBox.isChecked()))
        conf.set('merge', 'TRIGGERS', str(ui.TriggersBox.isChecked()))

        with open('/etc/spm.conf', 'wb') as libspmfile:
            conf.write(libspmfile)
        reload(libspm)
    except SystemExit:
        pass
    except Exception as detail:
        MessageCritical(str(detail))
        # FIXME: RefreshSettings()

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

RefreshFilters()
RefreshSettings()
RefreshSearch()

ui.updateButton.clicked.connect(Update)
ui.buildButton.clicked.connect(Build)
ui.mergeButton.clicked.connect(Install)
ui.removeButton.clicked.connect(Remove)
ui.syncButton.clicked.connect(SyncRepos)
ui.CacheDirEdit.textChanged.connect(ChangeSettings)
ui.CacheDirButton.clicked.connect(ChangeCacheDir)
ui.BuildDirEdit.textChanged.connect(ChangeSettings)
ui.BuildDirButton.clicked.connect(ChangeBuildDir)
ui.IgnoreTargetsEdit.textChanged.connect(ChangeSettings)
ui.DemoteBox.currentIndexChanged.connect(ChangeSettings)
ui.ConnectionTimeoutBox.valueChanged.connect(ChangeSettings)
ui.UseMirrorsBox.clicked.connect(ChangeSettings)
ui.CompressManBox.clicked.connect(ChangeSettings)
ui.StripBinariesBox.clicked.connect(ChangeSettings)
ui.StripSharedBox.clicked.connect(ChangeSettings)
ui.StripStaticBox.clicked.connect(ChangeSettings)
ui.StripRPATHBox.clicked.connect(ChangeSettings)
ui.PythonCompileBox.clicked.connect(ChangeSettings)
ui.IgnoreMissingBox.clicked.connect(ChangeSettings)
ui.ConflictsBox.clicked.connect(ChangeSettings)
ui.BackupBox.clicked.connect(ChangeSettings)
ui.ScriptsBox.clicked.connect(ChangeSettings)
ui.TriggersBox.clicked.connect(ChangeSettings)
ui.searchEdit.returnPressed.connect(SearchMetadata)
ui.repositoriesText.textChanged.connect(ChangeRepos)
ui.mirrorsText.textChanged.connect(ChangeMirrors)
ui.targetsView.currentItemChanged.connect(RefreshWidgets)
ui.filtersBox.currentIndexChanged.connect(RefreshTargets)
ui.targetsView.setCurrentRow(0)
ui.progressBar.setRange(0, 1)
ui.progressBar.hide()

MainWindow.show()
sys.exit(app.exec_())
