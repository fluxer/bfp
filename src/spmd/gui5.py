#!/usr/bin/python2

from PyQt5 import QtCore, QtGui, QtDBus, QtWidgets
import os, sys, re
if sys.version > '2':
    QtCore.QString = str
    QtCore.QStringList = list

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

app = QtWidgets.QApplication(sys.argv)
bus = QtDBus.QDBusConnection.systemBus()
MainWindow = QtWidgets.QMainWindow()
ui = gui_ui.Ui_MainWindow()
ui.setupUi(MainWindow)

class TargetsWorker(QtCore.QThread):
    ''' Threaded method caller '''
    add = QtCore.pyqtSignal(QtCore.QStringList)
    success = QtCore.pyqtSignal()
    failed = QtCore.pyqtSignal(QtCore.QString)

    def __init__(self, parent, targets, search=None):
        super(TargetsWorker, self).__init__(parent)
        self.targets = targets
        self.search = search

    def run(self):
        try:
            for target in self.targets:
                if database.local_search(target):
                    description = database.local_metadata(target, 'description')
                    if not database.remote_search(target):
                        status = 'Not available'
                    elif not database.local_uptodate(target):
                        status = 'Update'
                    else:
                        status = 'Installed'
                else:
                    description = database.remote_metadata(target, 'description')
                    status = 'Uninstalled'

                if self.search:
                    if not description:
                        continue
                    if not re.findall(self.search, description, flags=re.IGNORECASE) \
                        and not re.findall(self.search, target, flags=re.IGNORECASE):
                        continue

                self.add.emit([target, description, status])
            self.success.emit()
        except SystemExit:
            pass
        except Exception as detail:
            self.failed.emit(str(detail))

class Interface(QtDBus.QDBusInterface):
    ''' D-Bus interface handler '''
    def __init__(self, obj, path, interface, connection, parent):
        super(Interface, self).__init__(obj, path, interface, connection, parent)

    @QtCore.pyqtSlot(QtDBus.QDBusPendingCall)
    def CheckCall(self, call):
        reply = QtDBus.QDBusReply(call)
        if not reply.isValid():
            MessageCritical('No valid reply from D-Bus, possibly permissions issue.')
            return
        value = reply.value()
        if not value:
            return
        msg = str(value)
        if not msg == 'Success':
            MessageCritical(msg)

    @QtCore.pyqtSlot(QtCore.QString)
    def Finished(self, msg):
        # gee... the msg is QVariant so here is a _ugly_ workaround
        msg = str(msg)
        if not msg == 'Success':
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
            msg, QtWidgets.QSystemTrayIcon.Warning)

iface = Interface('com.spm.Daemon', '/com/spm/Daemon', \
    'com.spm.Daemon', bus, app)
bus.connect('com.spm.Daemon', '/com/spm/Daemon', 'com.spm.Daemon', \
    'Finished', iface.Finished)
bus.connect('com.spm.Daemon', '/com/spm/Daemon', 'com.spm.Daemon', \
    'Updates', iface.Updates)

def MessageInfo(*msg):
    return QtWidgets.QMessageBox.information(MainWindow, 'Information', \
        misc.string_convert(msg))

def MessageQuestion(*msg):
    return QtWidgets.QMessageBox.question(MainWindow, 'Question', \
        misc.string_convert(msg), QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

def MessageCritical(msg):
    if len(msg) < 400:
        return QtWidgets.QMessageBox.critical(MainWindow, 'Critical', \
            misc.string_convert(msg))
    else:
        msgBox = QtWidgets.QDialog(MainWindow)
        msgBox.setWindowTitle('Critical')
        msgBox.setWindowIcon(QtGui.QIcon.fromTheme('dialog-error'))
        msgBox.resize(400, 0)
        textedit = QtWidgets.QPlainTextEdit()
        textedit.setReadOnly(True)
        textedit.setPlainText(msg)
        okbutton = QtWidgets.QPushButton(QtGui.QIcon.fromTheme('dialog-ok'), \
            'OK', msgBox)
        okbutton.clicked.connect(msgBox.close)
        layout = QtWidgets.QGridLayout(msgBox)
        layout.addWidget(textedit)
        layout.addWidget(okbutton)
        return msgBox.exec_()

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

def TargetAdd(info):
    target, description, status = info
    irow = ui.SearchTable.rowCount()
    ui.SearchTable.setRowCount(irow+1)
    ui.SearchTable.setItem(irow, 0, QtWidgets.QTableWidgetItem(target))
    ui.SearchTable.setItem(irow, 1, QtWidgets.QTableWidgetItem(description))
    ui.SearchTable.setItem(irow, 2, QtWidgets.QTableWidgetItem(status))

def RefreshTargets(targets=None):
    if not targets:
        targets = database.local_all(basename=True)
        for target in database.remote_all(basename=True):
            if not target in targets:
                targets.append(target)

    worker = TargetsWorker(app, targets)
    worker.finished.connect(EnableWidgets)
    worker.add.connect(TargetAdd)
    worker.failed.connect(MessageCritical)
    ui.SearchTable.setRowCount(0)
    ui.SearchTable.clearContents()
    DisableWidgets()
    worker.start()

def RefreshRepos():
    ui.ReposTable.clearContents()
    irow = 0
    for line in misc.file_read(libspm.REPOSITORIES_CONF).splitlines():
        line = str(line)
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
        repoenablebox = QtWidgets.QCheckBox(ui.ReposTable)
        repoenablebox.setChecked(enable)
        ui.ReposTable.setCellWidget(irow, 0, repoenablebox)
        if not enable:
            line = line.lstrip('# ')
        ui.ReposTable.setItem(irow, 1, QtWidgets.QTableWidgetItem(line))
        irow += 1

def RefreshMirrors():
    ui.MirrorsTable.clearContents()
    irow = 0
    for line in misc.file_read(libspm.MIRRORS_CONF).splitlines():
        line = str(line)
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
        repoenablebox = QtWidgets.QCheckBox(ui.MirrorsTable)
        repoenablebox.setChecked(enable)
        ui.MirrorsTable.setCellWidget(irow, 0, repoenablebox)
        if not enable:
            line = line.lstrip('# ')
        ui.MirrorsTable.setItem(irow, 1, QtWidgets.QTableWidgetItem(line))
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
        tableitem = ui.SearchTable.item(item.row(), 0)
        # things happen asyncronsly so it may be gone by the time this block
        # is reached
        if not tableitem:
            continue
        target = str(tableitem.text())
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

def RefreshOptions():
    options = {}
    for t in database.remote_all(True):
        topt = database.remote_metadata(t, 'optdepends')
        if not topt:
            continue
        options[t] = {}
        for opt in topt:
            if opt in database.local_metadata(t, 'optdepends'):
                options[t][opt] = True
            else:
                options[t][opt] = False
    irow = 0
    ui.OptionsTree.clear()
    for target in options:
        description = database.remote_metadata(target, 'description')
        item1 = QtWidgets.QTreeWidgetItem(0)
        item1.setText(0, target)
        item1.setText(1, description)
        for opt in options[target]:
            item2 = QtWidgets.QTreeWidgetItem(1)
            item2.setText(0, opt)
            item2.setText(1, database.remote_metadata(opt, 'description'))
            item2.setCheckState(0, options[target][opt])
            item1.addChild(item2)
        ui.OptionsTree.insertTopLevelItem(irow, item1)
        irow += 1

def RefreshAll():
    EnableWidgets()
    RefreshTargets()
    RefreshWidgets()
    RefreshOptions()

def SearchMetadata():
    regexp = str(ui.SearchEdit.text())
    if not regexp:
        return RefreshTargets()

    targets = database.local_all(basename=True)
    for target in database.remote_all(basename=True):
        if not target in targets:
            targets.append(target)

    worker = TargetsWorker(app, targets, regexp)
    worker.finished.connect(EnableWidgets)
    worker.add.connect(TargetAdd)
    worker.failed.connect(MessageCritical)
    ui.SearchTable.setRowCount(0)
    ui.SearchTable.clearContents()
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
    if not answer == QtWidgets.QMessageBox.Yes:
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
    if not answer == QtWidgets.QMessageBox.Yes:
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
    if not answer == QtWidgets.QMessageBox.Yes:
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
    if not answer == QtWidgets.QMessageBox.Yes:
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
    url, ok = QtWidgets.QInputDialog.getText(MainWindow, 'URL', '')
    if ok and url:
        url = str(url)
        if not misc.url_supported(url):
            MessageCritical('The specified URL is not valid')
            return
        libspm.REPOSITORIES.append(url)
        irow = ui.ReposTable.rowCount()
        ui.ReposTable.setRowCount(irow+1)
        repoenablebox = QtWidgets.QCheckBox(ui.ReposTable)
        repoenablebox.setChecked(False)
        ui.ReposTable.setCellWidget(irow, 0, repoenablebox)
        ui.ReposTable.setItem(irow, 1, QtWidgets.QTableWidgetItem(url))

def AddMirror():
    url, ok = QtWidgets.QInputDialog.getText(MainWindow, 'URL', '')
    if ok and url:
        url = str(url)
        if not misc.url_supported(url, False):
            MessageCritical('The specified URL is not valid')
            return
        libspm.MIRRORS.append(url)
        irow = ui.MirrorsTable.rowCount()
        ui.MirrorsTable.setRowCount(irow+1)
        repoenablebox = QtWidgets.QCheckBox(ui.MirrorsTable)
        repoenablebox.setChecked(False)
        ui.MirrorsTable.setCellWidget(irow, 0, repoenablebox)
        ui.MirrorsTable.setItem(irow, 1, QtWidgets.QTableWidgetItem(url))

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
    call = iface.asyncCall('ReposSet', data)
    iface.CheckCall(call)

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
    call = iface.asyncCall('MirrorsSet', data)
    iface.CheckCall(call)

def ChangeSettings():
    try:
        DisableWidgets()
        call = iface.asyncCallWithArgumentList('ConfSet', ('fetch', 'MIRROR', \
            str(ui.UseMirrorsBox.isChecked())))
        iface.CheckCall(call)
        call = iface.asyncCallWithArgumentList('ConfSet', ('fetch', 'TIMEOUT', \
            str(ui.ConnectionTimeoutBox.value())))
        iface.CheckCall(call)
        call = iface.asyncCallWithArgumentList('ConfSet', ('merge', 'CONFLICTS', \
            str(ui.ConflictsBox.isChecked())))
        iface.CheckCall(call)
        call = iface.asyncCallWithArgumentList('ConfSet', ('merge', 'BACKUP', \
            str(ui.BackupBox.isChecked())))
        iface.CheckCall(call)
        call = iface.asyncCallWithArgumentList('ConfSet', ('merge', 'SCRIPTS', \
            str(ui.ScriptsBox.isChecked())))
        iface.CheckCall(call)
        call = iface.asyncCallWithArgumentList('ConfSet', ('merge', 'TRIGGERS', \
            str(ui.TriggersBox.isChecked())))
        iface.CheckCall(call)
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

ui.SearchTable.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
ui.SearchTable.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
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
    if not reason == QtWidgets.QSystemTrayIcon.Trigger:
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

minimizeAction = QtWidgets.QAction(QtGui.QIcon.fromTheme('view-close'), app.tr("Mi&nimize"), app)
minimizeAction.triggered.connect(MainWindow.hide)
restoreAction = QtWidgets.QAction(QtGui.QIcon.fromTheme('view-restore'), app.tr("&Restore"), app)
restoreAction.triggered.connect(MainWindow.showNormal)
quitAction = QtWidgets.QAction(QtGui.QIcon.fromTheme('application-exit'), app.tr("&Quit"), app)
quitAction.triggered.connect(app.quit)
trayIconMenu = QtWidgets.QMenu(MainWindow)
trayIconMenu.addAction(minimizeAction)
trayIconMenu.addAction(restoreAction)
trayIconMenu.addSeparator()
trayIconMenu.addAction(quitAction)
trayIcon = QtWidgets.QSystemTrayIcon(QtGui.QIcon.fromTheme('package-x-generic'), app)
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
    if not bus.isConnected():
        MessageCritical('Cannot connect to the D-Bus system bus')
    elif not iface.isValid():
        MessageCritical('Daemon is not running')
    MainWindow.show()
elif not bus.isConnected():
    trayIcon.showMessage('Critical', 'Cannot connect to the D-Bus system bus', \
        QtWidgets.QSystemTrayIcon.Critical)
elif not iface.isValid():
    trayIcon.showMessage('Critical', 'The daemon is not running', \
        QtWidgets.QSystemTrayIcon.Critical)

# SyncRepos()
RefreshRepos()
RefreshMirrors()
RefreshSettings()
RefreshWidgets()
RefreshTargets()
RefreshOptions()

sys.exit(app.exec_())
