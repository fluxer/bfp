#!/bin/python2

from PyQt4 import QtCore, QtGui
import os, sys
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
libspm.CATCH = True

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
            self.emit(QtCore.SIGNAL('success'))
        except SystemExit:
            pass
        except Exception as detail:
            self.emit(QtCore.SIGNAL('failed'), str(detail))

def MessageInfo(*msg):
    return QtGui.QMessageBox.information(MainWindow, 'Information', \
        misc.string_convert(msg))

def MessageQuestion(*msg):
    return QtGui.QMessageBox.question(MainWindow, 'Question', \
        misc.string_convert(msg), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)

def MessageCritical(msg):
    if len(msg) < 400:
        return QtGui.QMessageBox.critical(MainWindow, 'Critical', misc.string_convert(msg))
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
    ui.SearchEdit.setEnabled(False)
    ui.UpdateButton.setEnabled(False)
    ui.BuildButton.setEnabled(False)
    ui.InstallButton.setEnabled(False)
    ui.RemoveButton.setEnabled(False)
    ui.DetailsButton.setEnabled(False)
    ui.ProgressBar.setRange(0, 0)
    ui.ProgressBar.show()

def EnableWidgets():
    ui.SearchEdit.setEnabled(True)
    ui.UpdateButton.setEnabled(True)
    ui.BuildButton.setEnabled(False)
    ui.InstallButton.setEnabled(True)
    ui.RemoveButton.setEnabled(False)
    ui.DetailsButton.setEnabled(True)
    ui.ProgressBar.setRange(0, 1)
    ui.ProgressBar.hide()

def RefreshTargets():
    ui.SearchTable.clearContents()
    irow = 0
    for target in database.local_all(basename=True):
        ui.SearchTable.setRowCount(irow+1)
        description = database.local_metadata(target, 'description')
        ui.SearchTable.setItem(irow, 0, QtGui.QTableWidgetItem(target))
        ui.SearchTable.setItem(irow, 1, QtGui.QTableWidgetItem(description))
        if not database.local_uptodate(target):
            ui.SearchTable.setItem(irow, 2, QtGui.QTableWidgetItem('Update'))
        else:
            ui.SearchTable.setItem(irow, 2, QtGui.QTableWidgetItem('Installed'))
        irow += 1
    for target in database.remote_all(basename=True):
        if not database.local_search(target):
            ui.SearchTable.setRowCount(irow+1)
            description = database.remote_metadata(target, 'description')
            ui.SearchTable.setItem(irow, 0, QtGui.QTableWidgetItem(target))
            ui.SearchTable.setItem(irow, 1, QtGui.QTableWidgetItem(description))
            ui.SearchTable.setItem(irow, 2, QtGui.QTableWidgetItem('Uninstalled'))
            irow += 1

def RefreshRepos():
    ui.ReposTable.clearContents()
    irow = 0
    for line in misc.file_readlines(libspm.REPOSITORIES_CONF):
        enable = False
        if os.path.exists(line):
            enable = True
        elif line.startswith(('http://', 'https://', 'ftp://', 'ftps://', \
            'git://', 'ssh://', 'rsync://')):
            enable = True
        elif line.startswith(('# http://', '# https://', '# ftp://', \
            '# ftps://', '# git://', '# ssh://', '# rsync://')):
            enable = False
        else:
            continue
        ui.ReposTable.setRowCount(irow+1)
        repoenablebox = QtGui.QCheckBox(ui.ReposTable)
        repoenablebox.setChecked(enable)
        ui.ReposTable.setCellWidget(irow, 0, repoenablebox)
        if enable:
            ui.ReposTable.setItem(irow, 1, QtGui.QTableWidgetItem(line))
        else:
            ui.ReposTable.setItem(irow, 1, QtGui.QTableWidgetItem(line.lstrip('# ')))
        irow += 1

def RefreshMirrors():
    ui.MirrorsTable.clearContents()
    irow = 0
    for line in misc.file_readlines(libspm.MIRRORS_CONF):
        enable = False
        if os.path.exists(line):
            enable = True
        elif line.startswith(('http://', 'https://', 'ftp://', 'ftps://')):
            enable = True
        elif line.startswith(('# http://', '# https://', '# ftp://', \
            '# ftps://')):
            enable = False
        else:
            continue
        ui.MirrorsTable.setRowCount(irow+1)
        repoenablebox = QtGui.QCheckBox(ui.MirrorsTable)
        repoenablebox.setChecked(enable)
        ui.MirrorsTable.setCellWidget(irow, 0, repoenablebox)
        if enable:
            ui.MirrorsTable.setItem(irow, 1, QtGui.QTableWidgetItem(line))
        else:
            ui.MirrorsTable.setItem(irow, 1, QtGui.QTableWidgetItem(line.lstrip('# ')))
        irow += 1

def RefreshSettings():
    ui.IgnoreTargetsEdit.setText(misc.string_convert(libspm.IGNORE))
    ui.ConnectionTimeoutBox.setValue(libspm.TIMEOUT)
    ui.UseMirrorsBox.setCheckState(libspm.MIRROR)
    ui.ConflictsBox.setCheckState(libspm.CONFLICTS)
    ui.BackupBox.setCheckState(libspm.BACKUP)
    ui.ScriptsBox.setCheckState(libspm.SCRIPTS)
    ui.TriggersBox.setCheckState(libspm.TRIGGERS)
    ui.UpdateActionBox.setEnabled(True)
    if str(ui.UpdateTimeBox.currentText()) == 'Never':
        ui.UpdateActionBox.setEnabled(False)

def RefreshWidgets():
    ui.RemoveButton.setEnabled(True)
    ui.DetailsButton.setEnabled(True)
    if not ui.SearchTable.selectedIndexes():
        ui.DetailsButton.setEnabled(False)
    for item in ui.SearchTable.selectedIndexes():
        target = str(ui.SearchTable.item(item.row(), 0).text())
        if not database.local_search(target):
            ui.RemoveButton.setEnabled(False)

def SearchMetadataReal():
    DisableWidgets()
    regexp = str(ui.SearchEdit.text())
    targets = []
    if not regexp:
        RefreshTargets()
        return

    try:
        for index in xrange(ui.SearchTable.rowCount()):
            target = str(ui.SearchTable.item(index, 0).text())
            data = database.local_metadata(target, 'description')
            if not data:
                data = database.remote_metadata(target, 'description')
            if not data:
                continue
            if misc.string_search(regexp, data, escape=False, exact=False):
                targets.append(target)

        ui.SearchTable.clearContents()
        ui.SearchTable.setRowCount(0)
        irow = 0
        for target in targets:
            ui.SearchTable.setRowCount(irow+1)
            description = database.local_metadata(target, 'description')
            status = 'Installed'
            if not description:
                description = database.remote_metadata(target, 'description')
                status = 'Uninstalled'
            ui.SearchTable.setItem(irow, 0, QtGui.QTableWidgetItem(target))
            ui.SearchTable.setItem(irow, 1, QtGui.QTableWidgetItem(description))
            ui.SearchTable.setItem(irow, 2, QtGui.QTableWidgetItem('Update'))
            irow += 1
    except Exception as detail:
        MessageCritical(str(detail))
    finally:
        EnableWidgets()

def SearchMetadata():
    worker = Worker(app, SearchMetadataReal)
    worker.finished.connect(EnableWidgets)
    app.connect(worker, QtCore.SIGNAL('failed'), MessageCritical)
    DisableWidgets()
    worker.start()

def Update():
    build = []
    for target in database.local_all(basename=True):
        if not database.local_uptodate(target):
            build.append(target)
    if not build:
        MessageInfo('System is up-to-date')
        return
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
    app.connect(worker, QtCore.SIGNAL('success'), RefreshTargets)
    app.connect(worker, QtCore.SIGNAL('failed'), MessageCritical)
    DisableWidgets()
    worker.start()

def Build():
    targets = []
    for item in ui.SearchTable.selectedIndexes():
        target = str(ui.SearchTable.item(item.row(), 0).text())
        if target in targets:
            continue
        targets.extend(database.remote_mdepends(target))
        targets.append(target)
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
    app.connect(worker, QtCore.SIGNAL('success'), RefreshTargets)
    app.connect(worker, QtCore.SIGNAL('failed'), MessageCritical)
    DisableWidgets()
    worker.start()

def Install():
    targets = []
    for item in ui.SearchTable.selectedIndexes():
        target = str(ui.SearchTable.item(item.row(), 0).text())
        if target in targets:
            continue
        targets.extend(database.remote_mdepends(target))
        targets.append(target)
    answer = MessageQuestion('The following packages will be installed:\n\n', \
        misc.string_convert(targets), \
        '\n\nAre you sure you want to continue?')
    if not answer == QtGui.QMessageBox.Yes:
        return

    m = libspm.Binary(targets, do_merge=True, do_depends=True, \
        do_reverse=False, do_update=False)
    worker = Worker(app, m.main)
    worker.finished.connect(EnableWidgets)
    worker.finished.connect(RefreshWidgets)
    app.connect(worker, QtCore.SIGNAL('success'), RefreshTargets)
    app.connect(worker, QtCore.SIGNAL('failed'), MessageCritical)
    DisableWidgets()
    worker.start()

def Remove():
    targets = []
    for item in ui.SearchTable.selectedIndexes():
        target = str(ui.SearchTable.item(item.row(), 0).text())
        if target in targets:
            continue
        targets.extend(database.local_rdepends(target))
        targets.append(target)
    answer = MessageQuestion('The following packages will be removed:\n\n', \
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
    app.connect(worker, QtCore.SIGNAL('success'), RefreshTargets)
    app.connect(worker, QtCore.SIGNAL('failed'), MessageCritical)
    DisableWidgets()
    worker.start()

def Details():
    # FIXME: make it a dialog
    targets = []
    for item in ui.SearchTable.selectedIndexes():
        target = str(ui.SearchTable.item(item.row(), 0).text())
        if target in targets:
            continue
        description = str(ui.SearchTable.item(item.row(), 1).text())
        version = database.local_metadata(target, 'version')
        version = database.remote_metadata(target, 'version')
        MessageInfo('Package: %s\nVersion: %s\nDescription: %s\n' % (target, version, description))
        targets.append(target)

def SyncRepos():
    m = libspm.Repo(libspm.REPOSITORIES, do_clean=True, do_sync=True, \
        do_update=False)
    worker = Worker(app, m.main)
    worker.finished.connect(EnableWidgets)
    worker.finished.connect(RefreshWidgets)
    app.connect(worker, QtCore.SIGNAL('success'), RefreshTargets)
    app.connect(worker, QtCore.SIGNAL('failed'), MessageCritical)
    DisableWidgets()
    worker.start()

def ChangeSettings():
    try:
        conf = configparser.SafeConfigParser()
        conf.read('/etc/spm.conf')
        conf.set('prepare', 'MIRROR', str(ui.UseMirrorsBox.isChecked()))
        conf.set('prepare', 'TIMEOUT', str(ui.ConnectionTimeoutBox.value()))
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
    finally:
        ui.UpdateActionBox.setEnabled(True)
        if str(ui.UpdateTimeBox.currentText()) == 'Never':
            ui.UpdateActionBox.setEnabled(False)

# SyncRepos()
RefreshRepos()
RefreshMirrors()
RefreshTargets()
RefreshSettings()

ui.SearchTable.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
ui.SearchTable.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
ui.UpdateButton.clicked.connect(Update)
ui.BuildButton.clicked.connect(Build)
ui.InstallButton.clicked.connect(Install)
ui.RemoveButton.clicked.connect(Remove)
ui.DetailsButton.clicked.connect(Details)
ui.SearchEdit.returnPressed.connect(SearchMetadata)
ui.SearchTable.currentItemChanged.connect(RefreshWidgets)
ui.IgnoreTargetsEdit.textChanged.connect(ChangeSettings)
ui.ConnectionTimeoutBox.valueChanged.connect(ChangeSettings)
ui.UseMirrorsBox.clicked.connect(ChangeSettings)
ui.ConflictsBox.clicked.connect(ChangeSettings)
ui.BackupBox.clicked.connect(ChangeSettings)
ui.ScriptsBox.clicked.connect(ChangeSettings)
ui.TriggersBox.clicked.connect(ChangeSettings)
ui.UpdateTimeBox.currentIndexChanged.connect(ChangeSettings)
ui.UpdateActionBox.currentIndexChanged.connect(ChangeSettings)
ui.ProgressBar.setRange(0, 1)
ui.ProgressBar.hide()

MainWindow.show()
sys.exit(app.exec_())
