#!/bin/python2

from PyQt4 import QtCore, QtGui, QtDBus
import os, sys, time
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
bus = QtDBus.QDBusConnection.systemBus()
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

class Interface(QtCore.QObject):
    ''' Tab widget '''
    def __init__(self, parent):
        super(Interface, self).__init__()

    @QtCore.pyqtSlot(QtCore.QString)
    def MessageInfo(*msg):
        MessageInfo(str(msg[1]))

    @QtCore.pyqtSlot()
    def RefreshAll(*msg):
        RefreshAll()

face = Interface(app)
iface = QtDBus.QDBusInterface('com.spm.Daemon', '/com/spm/Daemon', \
    'com.spm.Daemon', bus)
bus.connect('com.spm.Daemon', '/com/spm/Daemon', 'com.spm.Daemon', \
    'Finished', face.MessageInfo)
bus.connect('com.spm.Daemon', '/com/spm/Daemon', 'com.spm.Daemon', \
    'Finished', face.RefreshAll)

def MessageInfo(*msg):
    return QtGui.QMessageBox.information(MainWindow, 'Information', misc.string_convert(msg))

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

if not bus.isConnected():
    MessageCritical('Cannot connect to the D-Bus system bus')
    sys.exit(1)

def DisableWidgets():
    ui.SearchEdit.setEnabled(False)
    ui.SyncButton.setEnabled(False)
    ui.UpdateButton.setEnabled(False)
    ui.BuildButton.setEnabled(False)
    ui.InstallButton.setEnabled(False)
    ui.RemoveButton.setEnabled(False)
    ui.DetailsButton.setEnabled(False)
    ui.RepoSaveButton.setEnabled(False)
    ui.MirrorSaveButton.setEnabled(False)
    ui.ProgressBar.setRange(0, 0)
    ui.ProgressBar.show()

def EnableWidgets():
    ui.SearchEdit.setEnabled(True)
    ui.SyncButton.setEnabled(True)
    ui.UpdateButton.setEnabled(True)
    ui.BuildButton.setEnabled(True)
    ui.InstallButton.setEnabled(True)
    ui.RemoveButton.setEnabled(False)
    ui.DetailsButton.setEnabled(True)
    ui.RepoSaveButton.setEnabled(True)
    ui.MirrorSaveButton.setEnabled(True)
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

def RefreshWidgets():
    ui.RemoveButton.setEnabled(True)
    ui.DetailsButton.setEnabled(True)
    if not ui.SearchTable.selectedIndexes():
        ui.DetailsButton.setEnabled(False)
    for item in ui.SearchTable.selectedIndexes():
        target = str(ui.SearchTable.item(item.row(), 0).text())
        if not database.local_search(target):
            ui.RemoveButton.setEnabled(False)
    ui.RepoRemoveButton.setEnabled(False)
    ui.RepoUpButton.setEnabled(False)
    ui.RepoDownButton.setEnabled(False)
    for item in ui.ReposTable.selectedIndexes():
        ui.RepoRemoveButton.setEnabled(True)
        ui.RepoUpButton.setEnabled(True)
        ui.RepoDownButton.setEnabled(True)
    ui.MirrorRemoveButton.setEnabled(False)
    ui.MirrorUpButton.setEnabled(False)
    ui.MirrorDownButton.setEnabled(False)
    for item in ui.MirrorsTable.selectedIndexes():
        ui.MirrorRemoveButton.setEnabled(True)
        ui.MirrorUpButton.setEnabled(True)
        ui.MirrorDownButton.setEnabled(True)
    ui.UpdateActionBox.setEnabled(True)
    if str(ui.UpdateTimeBox.currentText()) == 'Never':
        ui.UpdateActionBox.setEnabled(False)

def RefreshAll():
    EnableWidgets()
    RefreshTargets()
    RefreshWidgets()

def SearchMetadataReal():
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
            if not database.local_uptodate(target):
                status = 'Update'
            if not description:
                description = database.remote_metadata(target, 'description')
                status = 'Uninstalled'
            ui.SearchTable.setItem(irow, 0, QtGui.QTableWidgetItem(target))
            ui.SearchTable.setItem(irow, 1, QtGui.QTableWidgetItem(description))
            ui.SearchTable.setItem(irow, 2, QtGui.QTableWidgetItem(status))
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

def Sync():
    DisableWidgets()
    async = iface.asyncCall('Sync')

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
    DisableWidgets()
    iface.asyncCall('Update')

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
    DisableWidgets()
    iface.asyncCall('Build', targets)

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
    DisableWidgets()
    iface.asyncCall('Install', targets)

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
    iface.asyncCallWithArgumentList('Remove', (targets, True))

def Details():
    # TODO: make it a dialog?
    targets = []
    for item in ui.SearchTable.selectedIndexes():
        target = str(ui.SearchTable.item(item.row(), 0).text())
        if target in targets:
            continue
        description = str(ui.SearchTable.item(item.row(), 1).text())
        lversion = database.local_metadata(target, 'version')
        lrelease = database.local_metadata(target, 'release')
        rversion = database.remote_metadata(target, 'version')
        rrelease = database.remote_metadata(target, 'release')
        if database.local_search(target):
            depends = database.local_metadata(target, 'depends')
        else:
            depends = database.remote_mdepends(target)
        options = database.remote_metadata(target, 'options')
        data = 'Package: %s\nInstalled version: %s (%s)\n' % (target, lversion, lrelease)
        data += 'Available version: %s (%s)\nDescription: %s\n' % (rversion, rrelease, description)
        data += 'Dependencies: %s\nOptions: %s\n' % (depends, options)
        MessageInfo(data)
        targets.append(target)

def AddRepo():
    # TODO: replace with dialog that has enable checkbox?
    url, ok = QtGui.QInputDialog.getText(MainWindow, 'URL', '')
    if ok and url:
        url = str(url)
        if not url.startswith(('http://', 'https://', 'ftp://', 'ftps://')):
            MessageCritical('The specified URL is not valid')
            return
        libspm.REPOSITORIES.append(url)
        irow = ui.ReposTable.rowCount()
        ui.ReposTable.setRowCount(irow+1)
        repoenablebox = QtGui.QCheckBox(ui.ReposTable)
        repoenablebox.setChecked(False)
        ui.ReposTable.setCellWidget(irow, 0, repoenablebox)
        ui.ReposTable.setItem(irow, 1, QtGui.QTableWidgetItem(url))

def AddMirror():
    # TODO: replace with dialog that has enable checkbox?
    url, ok = QtGui.QInputDialog.getText(MainWindow, 'URL', '')
    if ok and url:
        url = str(url)
        if not url.startswith(('http://', 'https://', 'ftp://', 'ftps://')):
            MessageCritical('The specified URL is not valid')
            return
        libspm.MIRRORS.append(url)
        irow = ui.MirrorsTable.rowCount()
        ui.MirrorsTable.setRowCount(irow+1)
        repoenablebox = QtGui.QCheckBox(ui.MirrorsTable)
        repoenablebox.setChecked(False)
        ui.MirrorsTable.setCellWidget(irow, 0, repoenablebox)
        ui.MirrorsTable.setItem(irow, 1, QtGui.QTableWidgetItem(url))

def RemoveRepo():
    for item in ui.ReposTable.selectedIndexes():
        ui.ReposTable.removeRow(item.row())

def RemoveMirror():
    for item in ui.MirrorsTable.selectedIndexes():
        ui.MirrorsTable.removeRow(item.row())

def UpRepo():
    # FIXME: implement
    MessageCritical('Not implement')

def UpMirror():
    # FIXME: implement
    MessageCritical('Not implement')

def DownRepo():
    # FIXME: implement
    MessageCritical('Not implement')

def DownMirror():
    # FIXME: implement
    MessageCritical('Not implement')

def ChangeRepos():
    data = ''
    atleastone = False
    for index in xrange(ui.ReposTable.rowCount()):
        enable = ui.ReposTable.cellWidget(index, 0).isChecked()
        url = str(ui.ReposTable.item(index, 1).text())
        if enable:
            atleastone = True
            data += '%s\n' % url
        else:
            data += '# %s\n' % url
    if not atleastone:
        MessageCritical('At least one repository must be enabled')
        return
    iface.asyncCall('ReposSet', data)

def ChangeMirrors():
    data = ''
    atleastone = False
    for index in xrange(ui.MirrorsTable.rowCount()):
        enable = ui.MirrorsTable.cellWidget(index, 0).isChecked()
        url = str(ui.MirrorsTable.item(index, 1).text())
        if enable:
            atleastone = True
            data += '%s\n' % url
        else:
            data += '# %s\n' % url
    if not atleastone:
        MessageCritical('At least one mirror must be enabled')
        return
    iface.asyncCall('MirrorsSet', data)

def ChangeSettings():
    try:
        DisableWidgets()
        iface.asyncCallWithArgumentList('ConfSet', ('fetch', 'MIRROR', str(ui.UseMirrorsBox.isChecked())))
        iface.asyncCallWithArgumentList('ConfSet', ('fetch', 'TIMEOUT', str(ui.ConnectionTimeoutBox.value())))
        iface.asyncCallWithArgumentList('ConfSet', ('merge', 'CONFLICTS', str(ui.ConflictsBox.isChecked())))
        iface.asyncCallWithArgumentList('ConfSet', ('merge', 'BACKUP', str(ui.BackupBox.isChecked())))
        iface.asyncCallWithArgumentList('ConfSet', ('merge', 'SCRIPTS', str(ui.ScriptsBox.isChecked())))
        iface.asyncCallWithArgumentList('ConfSet', ('merge', 'TRIGGERS', str(ui.TriggersBox.isChecked())))
        RefreshAll()
        reload(libspm)
    except SystemExit:
        pass
    except Exception as detail:
        MessageCritical(str(detail))
        # FIXME: RefreshSettings()

ui.SearchTable.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
ui.SearchTable.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
ui.SyncButton.clicked.connect(Sync)
ui.UpdateButton.clicked.connect(Update)
ui.BuildButton.clicked.connect(Build)
ui.InstallButton.clicked.connect(Install)
ui.RemoveButton.clicked.connect(Remove)
ui.DetailsButton.clicked.connect(Details)
ui.SearchEdit.returnPressed.connect(SearchMetadata)
ui.SearchTable.itemSelectionChanged.connect(RefreshWidgets)

ui.RepoAddButton.clicked.connect(AddRepo)
ui.RepoUpButton.clicked.connect(UpRepo)
ui.RepoSaveButton.clicked.connect(ChangeRepos)
ui.RepoDownButton.clicked.connect(DownRepo)
ui.RepoRemoveButton.clicked.connect(RemoveRepo)
ui.ReposTable.itemSelectionChanged.connect(RefreshWidgets)

ui.MirrorAddButton.clicked.connect(AddMirror)
ui.MirrorUpButton.clicked.connect(UpMirror)
ui.MirrorSaveButton.clicked.connect(ChangeMirrors)
ui.MirrorDownButton.clicked.connect(DownMirror)
ui.MirrorRemoveButton.clicked.connect(RemoveMirror)
ui.MirrorsTable.itemSelectionChanged.connect(RefreshWidgets)

ui.PrefSaveButton.clicked.connect(ChangeSettings)
ui.UpdateTimeBox.currentIndexChanged.connect(RefreshWidgets)

ui.ProgressBar.setRange(0, 1)
ui.ProgressBar.hide()

MainWindow.show()

# SyncRepos()
RefreshRepos()
RefreshMirrors()
RefreshSettings()
RefreshWidgets()
QtCore.QTimer.singleShot(1000, RefreshTargets)

sys.exit(app.exec_())
