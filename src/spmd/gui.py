#!/bin/python2

from PyQt4 import QtCore, QtGui, QtDBus
import os, sys, time, re
if sys.version < '3':
    import ConfigParser as configparser
else:
    import configparser

# handle keyboard interrupt
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

import gui_ui
import libspm
database = libspm.database
message = libspm.message
misc = libspm.misc
misc.CATCH = True
libspm.CATCH = True

app = QtGui.QApplication(sys.argv)
bus = QtDBus.QDBusConnection.systemBus()
MainWindow = QtGui.QMainWindow()
ui = gui_ui.Ui_MainWindow()
ui.setupUi(MainWindow)

class Worker(QtCore.QThread):
    ''' Threaded method caller '''
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

class Interface(QtDBus.QDBusInterface):
    ''' D-Bus interface handler '''
    def __init__(self, obj, path, interface, connection, parent):
        super(Interface, self).__init__(obj, path, interface, connection, parent)

    @QtCore.pyqtSlot(QtCore.QString)
    def Finished(self, *msg):
        # gee... the msg is QVariant but a slot with QVariant does not work
        # so here is a _ugly_ workaround
        msg = str(QtCore.QString(msg[0]))
        if msg == 'Success':
            MessageInfo(msg)
        else:
            MessageCritical(msg)
        RefreshAll()

    @QtCore.pyqtSlot(QtCore.QStringList)
    def Updates(self, targets):
        # convert to something without PyQt4.QtCore.QString prefix
        updates = []
        for target in targets:
            updates.append(str(target))
        upicon = QtGui.QIcon.fromTheme('software-update-available')
        if upicon.isNull():
            QtGui.QIcon.fromTheme('system-software-update')
        trayIcon.setIcon(upicon)
        msg = 'Updates available: %s' % updates
        trayIcon.showMessage('Warning', \
            msg, QtGui.QSystemTrayIcon.Warning)

iface = Interface('com.spm.Daemon', '/com/spm/Daemon', \
    'com.spm.Daemon', bus, app)
bus.connect('com.spm.Daemon', '/com/spm/Daemon', 'com.spm.Daemon', \
    'Finished', iface.Finished)
bus.connect('com.spm.Daemon', '/com/spm/Daemon', 'com.spm.Daemon', \
    'Updates', iface.Updates)

def MessageInfo(*msg):
    return QtGui.QMessageBox.information(MainWindow, 'Information', \
        misc.string_convert(msg))

def MessageQuestion(*msg):
    return QtGui.QMessageBox.question(MainWindow, 'Question', \
        misc.string_convert(msg), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)

def MessageCritical(msg):
    if len(msg) < 400:
        return QtGui.QMessageBox.critical(MainWindow, 'Critical', \
            misc.string_convert(msg))
    else:
        msgBox = QtGui.QDialog(MainWindow)
        msgBox.setWindowTitle('Critical')
        msgBox.setWindowIcon(QtGui.QIcon.fromTheme('dialog-error'))
        msgBox.resize(400, 0)
        textedit = QtGui.QPlainTextEdit()
        textedit.setReadOnly(True)
        textedit.setPlainText(msg)
        okbutton = QtGui.QPushButton(QtGui.QIcon.fromTheme('dialog-ok'), \
            'OK', msgBox)
        okbutton.clicked.connect(msgBox.close)
        layout = QtGui.QGridLayout(msgBox)
        layout.addWidget(textedit)
        layout.addWidget(okbutton)
        return msgBox.exec_()

if not bus.isConnected():
    MessageCritical('Cannot connect to the D-Bus system bus')
    sys.exit(1)

def DisableWidgets():
    ui.SearchTable.setEnabled(False)
    ui.SearchEdit.setEnabled(False)
    ui.SyncButton.setEnabled(False)
    ui.UpdateButton.setEnabled(False)
    ui.BuildButton.setEnabled(False)
    ui.InstallButton.setEnabled(False)
    ui.RemoveButton.setEnabled(False)
    ui.DetailsButton.setEnabled(False)
    ui.RepoSaveButton.setEnabled(False)
    ui.MirrorSaveButton.setEnabled(False)
    ui.PrefSaveButton.setEnabled(False)
    ui.ProgressBar.setRange(0, 0)
    ui.ProgressBar.show()

def EnableWidgets():
    # TODO: many other widgets are useless without a running daemon
    ifacevalid = iface.isValid()
    ui.SearchTable.setEnabled(True)
    ui.SearchEdit.setEnabled(True)
    ui.SyncButton.setEnabled(ifacevalid)
    ui.UpdateButton.setEnabled(ifacevalid)
    ui.BuildButton.setEnabled(ifacevalid)
    ui.InstallButton.setEnabled(ifacevalid)
    ui.RemoveButton.setEnabled(False)
    ui.DetailsButton.setEnabled(False)
    ui.RepoSaveButton.setEnabled(ifacevalid)
    ui.MirrorSaveButton.setEnabled(ifacevalid)
    ui.PrefSaveButton.setEnabled(ifacevalid)
    ui.ProgressBar.setRange(0, 1)
    ui.ProgressBar.hide()

def RefreshTargetsReal(targets=None):
    ui.SearchTable.clearContents()
    irow = 0
    if not targets:
        targets = database.local_all(basename=True)
        for target in database.remote_all(basename=True):
            if not target in targets:
                targets.append(target)

    for target in targets:
        ui.SearchTable.setRowCount(irow+1)
        ui.SearchTable.setItem(irow, 0, QtGui.QTableWidgetItem(target))
        if database.local_search(target):
            description = database.local_metadata(target, 'description')
            ui.SearchTable.setItem(irow, 1, QtGui.QTableWidgetItem(description))
            if not database.remote_search(target):
                ui.SearchTable.setItem(irow, 2, QtGui.QTableWidgetItem('Not available'))
            elif not database.local_uptodate(target):
                ui.SearchTable.setItem(irow, 2, QtGui.QTableWidgetItem('Update'))
            else:
                ui.SearchTable.setItem(irow, 2, QtGui.QTableWidgetItem('Installed'))
        else:
            description = database.remote_metadata(target, 'description')
            ui.SearchTable.setItem(irow, 1, QtGui.QTableWidgetItem(description))
            ui.SearchTable.setItem(irow, 2, QtGui.QTableWidgetItem('Uninstalled'))
        irow += 1

def RefreshTargets():
    worker = Worker(app, RefreshTargetsReal)
    worker.finished.connect(EnableWidgets)
    app.connect(worker, QtCore.SIGNAL('failed'), MessageCritical)
    DisableWidgets()
    worker.start()

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
        if not enable:
            line = line.lstrip('# ')
        ui.ReposTable.setItem(irow, 1, QtGui.QTableWidgetItem(line))
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
        if not enable:
            line = line.lstrip('# ')
        ui.MirrorsTable.setItem(irow, 1, QtGui.QTableWidgetItem(line))
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
    ui.RemoveButton.setEnabled(iface.isValid())
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
    matches = []
    if not regexp:
        return RefreshTargetsReal()

    targets = database.local_all(basename=True)
    for target in database.remote_all(basename=True):
        if not target in targets:
            targets.append(target)

    for target in targets:
        description = database.local_metadata(target, 'description')
        if not description:
            description = database.remote_metadata(target, 'description')
        if not description:
            continue
        if re.findall(regexp, description, flags=re.IGNORECASE):
            matches.append(target)
        if re.findall(regexp, target, flags=re.IGNORECASE):
            matches.append(target)

    if matches:
        # calling it with null matches will add all
        RefreshTargetsReal(matches)
    else:
        ui.SearchTable.clearContents()
        ui.SearchTable.setRowCount(0)

def SearchMetadata():
    worker = Worker(app, SearchMetadataReal)
    worker.finished.connect(EnableWidgets)
    app.connect(worker, QtCore.SIGNAL('failed'), MessageCritical)
    DisableWidgets()
    worker.start()

def Sync():
    DisableWidgets()
    iface.asyncCall('Sync')

def Update():
    build = []
    for target in database.local_all(basename=True):
        if not database.local_uptodate(target) \
            and database.remote_search(target):
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
    # TODO: make it a dialog? when multiple targets are selected one may want
    # to compare their metadata in visually pleasant way
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
        backup = database.remote_metadata(target, 'backup')
        data = 'Package: %s\n' % target
        data += 'Installed version: %s (%s)\n' % (lversion, lrelease)
        data += 'Available version: %s (%s)\n' % (rversion, rrelease)
        data += 'Description: %s\n' % description
        data += 'Dependencies: %s\n' % depends
        data += 'Options: %s\n' % options
        data += 'Backup: %s\n' % backup
        MessageInfo(data)
        targets.append(target)

def AddRepo():
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
        iface.asyncCallWithArgumentList('ConfSet', ('fetch', 'MIRROR', \
            str(ui.UseMirrorsBox.isChecked())))
        iface.asyncCallWithArgumentList('ConfSet', ('fetch', 'TIMEOUT', \
            str(ui.ConnectionTimeoutBox.value())))
        iface.asyncCallWithArgumentList('ConfSet', ('merge', 'CONFLICTS', \
            str(ui.ConflictsBox.isChecked())))
        iface.asyncCallWithArgumentList('ConfSet', ('merge', 'BACKUP', \
            str(ui.BackupBox.isChecked())))
        iface.asyncCallWithArgumentList('ConfSet', ('merge', 'SCRIPTS', \
            str(ui.ScriptsBox.isChecked())))
        iface.asyncCallWithArgumentList('ConfSet', ('merge', 'TRIGGERS', \
            str(ui.TriggersBox.isChecked())))
        RefreshAll()
        reload(libspm)
    except SystemExit:
        pass
    except Exception as detail:
        MessageCritical(str(detail))
        # FIXME: RefreshSettings()
    finally:
        # TODO: should the daemon emit finished?
        EnableWidgets()

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

def restoreEvent(reason):
    if not reason == QtGui.QSystemTrayIcon.Trigger:
        return
    elif MainWindow.isVisible():
        MainWindow.hide()
    else:
        MainWindow.showNormal()

def updateEvent():
    # FIXME: raising the main window should not be needed to show the message,
    # a dialog without parent will kill the main window upon "close"!?!
    MainWindow.showNormal()
    Update()

minimizeAction = QtGui.QAction(QtGui.QIcon.fromTheme('view-close'), app.tr("Mi&nimize"), app)
minimizeAction.triggered.connect(MainWindow.hide)
restoreAction = QtGui.QAction(QtGui.QIcon.fromTheme('view-restore'), app.tr("&Restore"), app);
restoreAction.triggered.connect(MainWindow.showNormal)
quitAction = QtGui.QAction(QtGui.QIcon.fromTheme('application-exit'), app.tr("&Quit"), app)
quitAction.triggered.connect(app.quit)
trayIconMenu = QtGui.QMenu(MainWindow)
trayIconMenu.addAction(minimizeAction)
trayIconMenu.addAction(restoreAction)
trayIconMenu.addSeparator()
trayIconMenu.addAction(quitAction)
trayIcon = QtGui.QSystemTrayIcon(QtGui.QIcon.fromTheme('package-x-generic'), app)
trayIcon.setContextMenu(trayIconMenu)
trayIcon.messageClicked.connect(updateEvent)
trayIcon.activated.connect(restoreEvent)
trayIcon.show()

def closeEvent(event):
    if trayIcon.isVisible():
         MainWindow.hide()
         event.ignore()

MainWindow.closeEvent = closeEvent

if not '--tray' in sys.argv:
    if not iface.isValid():
        MessageCritical('Daemon is not running')
    MainWindow.show()
elif not iface.isValid():
    trayIcon.showMessage('Critical', 'The daemon is not running', \
        QtGui.QSystemTrayIcon.Critical)

# SyncRepos()
RefreshRepos()
RefreshMirrors()
RefreshSettings()
RefreshWidgets()
RefreshTargets()

sys.exit(app.exec_())
