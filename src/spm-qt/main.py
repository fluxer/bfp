#!/bin/python2

import spmqt_ui
from PyQt4 import QtGui
import sys, ConfigParser, libmessage, libmisc, libpackage, libspm, libdesktop

# prepare for lift-off
app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()
ui = spmqt_ui.Ui_MainWindow()
ui.setupUi(MainWindow)
message = libmessage.Message()
misc = libmisc.Misc()
database = libpackage.Database()
config = libdesktop.Config()
general = libdesktop.General()
icon = QtGui.QIcon()

def Worker():
    try:
        #ui.UpdateButton.setEnabled(False)
        #ui.BuildButton.setEnabled(False)
        #ui.RemoveButton.setEnabled(False)
        #ui.SyncRepoButton.setEnabled(False)
        ui.OutputText.append('*' * 50)
        m.main()
    except SystemExit:
        pass
    except Exception as detail:
        message.critical(detail)
    finally:
        #ui.UpdateButton.setEnabled(True)
        #ui.BuildButton.setEnabled(True)
        #ui.RemoveButton.setEnabled(True)
        #ui.SyncRepoButton.setEnabled(True)
        ui.tabWidget.setCurrentIndex(1)

def RefreshTargets():
    ui.TargetsList.clear()
    current = str(ui.AliasesList.currentItem().text())
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
        ui.TargetsList.addItem(target)

    ui.TargetsList.setCurrentRow(0)

def Refresh():
    ui.AliasesList.clear()
    ui.TargetsList.clear()
    ui.ReposEdit.clear()
    ui.MirrorsEdit.clear()

    ui.AliasesList.addItem('all')
    ui.AliasesList.addItem('local')
    ui.AliasesList.addItem('unneeded')
    ui.AliasesList.addItem('candidates')
    ui.AliasesList.setCurrentRow(0)
    for alias in database.remote_aliases():
        ui.AliasesList.addItem(alias)

    for target in database.remote_all(basename=True):
        ui.TargetsList.addItem(target)

    ui.ReposEdit.setPlainText(misc.file_read('/etc/spm/repositories.conf'))

    ui.MirrorsEdit.setPlainText(misc.file_read('/etc/spm/mirrors.conf'))

    ui.CacheDirEdit.setText(libspm.CACHE_DIR)
    ui.BuildDirEdit.setText(libspm.BUILD_DIR)
    ui.IgnoreTargetsEdit.setText(libspm.IGNORE)
    ui.ConnectionTimeoutBox.setValue(libspm.TIMEOUT)
    ui.UseMirrorsBox.setCheckState(libspm.MIRROR)
    ui.ExternalFetcherBox.setCheckState(libspm.EXTERNAL)
    ui.CompressManBox.setCheckState(libspm.COMPRESS_MAN)
    ui.StripBinariesBox.setCheckState(libspm.STRIP_BINARIES)
    ui.StripSharedBox.setCheckState(libspm.STRIP_SHARED)
    ui.StripStaticBox.setCheckState(libspm.STRIP_STATIC)
    ui.IgnoreMissingBox.setCheckState(libspm.IGNORE_MISSING)
    ui.ConflictsBox.setCheckState(libspm.CONFLICTS)
    ui.BackupBox.setCheckState(libspm.BACKUP)
    ui.ScriptsBox.setCheckState(libspm.SCRIPTS)

def RefreshWidgets():
    target = str(ui.TargetsList.currentItem().text())

    ui.MetadataText.clear()
    ui.FootprintText.clear()
    if database.local_installed(target):
        ui.RemoveButton.setEnabled(True)
        ui.MetadataText.append('Version: ' + database.local_metadata(target, 'version'))
        ui.MetadataText.append('Description: ' + database.local_metadata(target, 'description'))
        ui.MetadataText.append('Depends: ' + database.local_metadata(target, 'depends'))
        ui.MetadataText.append('Reverse: ' + misc.string_convert(database.local_rdepends(target)))
        ui.MetadataText.append('Size: ' + database.local_metadata(target, 'size'))
        ui.FootprintText.setText(database.local_footprint(target))
    else:
        ui.RemoveButton.setEnabled(False)
        ui.MetadataText.append('Version: ' + database.remote_metadata(target, 'version'))
        ui.MetadataText.append('Description: ' + database.remote_metadata(target, 'description'))
        ui.MetadataText.append('Depends: ' + misc.string_convert(database.remote_metadata(target, 'depends')))
        ui.MetadataText.append('Make depends: ' + misc.string_convert(database.remote_metadata(target, 'makedepends')))
        ui.MetadataText.append('Sources: ' + misc.string_convert(database.remote_metadata(target, 'sources')))
        ui.MetadataText.append('Options: ' + misc.string_convert(database.remote_metadata(target, 'options')))
        ui.MetadataText.append('Backup: ' + misc.string_convert(database.remote_metadata(target, 'backup')))

def Update():
    targets = database.local_all(basename=True)
    global m
    m = libspm.Source(targets, do_clean=True, do_prepare=True,
        do_compile=True, do_check=False, do_install=True, do_merge=True,
        do_remove=False, do_depends=True, do_reverse=True, do_update=True)
    Worker()

def Build():
    targets = [str(ui.TargetsList.currentItem().text())]
    global m
    m = libspm.Source(targets, do_clean=True, do_prepare=True,
        do_compile=True, do_check=False, do_install=True, do_merge=True,
        do_remove=False, do_depends=True, do_reverse=True, do_update=False)
    Worker()
    RefreshWidgets()

def Remove():
    targets = [str(ui.TargetsList.currentItem().text())]
    global m
    m = libspm.Source(targets, do_clean=False, do_prepare=False,
        do_compile=False, do_check=False, do_install=False, do_merge=False,
        do_remove=True, do_depends=False, do_reverse=True, do_update=False)
    Worker()
    RefreshWidgets()

def SyncRepos():
    global m
    m = libspm.Repo(libspm.REPOSITORIES, do_clean=True, do_sync=True, do_update=False)
    Worker()

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

        with open('/etc/spm.conf', 'wb') as configfile:
            conf.write(configfile)
        reload(libspm)
    except SystemExit:
        pass
    except Exception as detail:
        message.critical(detail)

def ChangeRepos():
    try:
        misc.file_write('/etc/spm/repositories.conf', str(ui.ReposEdit.toPlainText()))
        reload(libspm)
    except SystemExit:
        pass
    except Exception as detail:
        message.critical(detail)

def ChangeMirrors():
    try:
        misc.file_write('/etc/spm/mirrors.conf', str(ui.MirrorsEdit.toPlainText()))
        reload(libspm)
    except SystemExit:
        pass
    except Exception as detail:
        message.critical(detail)

def info(msg, marker=None):
    if not marker is None:
        print('[INFO] %s: %s' %(msg, marker))
        ui.OutputText.append('[INFO] %s: %s' %(msg, marker))
    else:
        print('[INFO] %s' % msg)
        ui.OutputText.append('[INFO] %s' % msg)

def warning(msg, marker=None):
    if not marker is None:
        print('[WARNING] %s: %s' %(msg, marker))
        ui.OutputText.append('[WARNING] %s: %s' %(msg, marker))
    else:
        print('[WARNING] %s' % msg)
        ui.OutputText.append('[WARNING] %s' % msg)

def critical(msg, marker=None):
    if not marker is None:
        print('[CRITICAL] %s: %s' %(msg, marker))
        ui.OutputText.append('[CRITICAL] %s: %s' % (msg, marker))
    else:
        print('[CRITICAL] %s' % msg)
        ui.OutputText.append('[CRITICAL] %s' % msg)

message.info = info
message.sub_info = info
message.warning = warning
message.sub_warning = warning
message.critical = critical
message.sub_critical = critical

def setLook():
    general.set_style(app)
    icon.setThemeName(config.GENERAL_ICONTHEME)
setLook()

Refresh()

ui.UpdateButton.clicked.connect(Update)
ui.BuildButton.clicked.connect(Build)
ui.RemoveButton.clicked.connect(Remove)
ui.SyncRepoButton.clicked.connect(SyncRepos)

ui.CacheDirEdit.textChanged.connect(ChangeSettings)
ui.BuildDirEdit.textChanged.connect(ChangeSettings)
ui.IgnoreTargetsEdit.textChanged.connect(ChangeSettings)
ui.ConnectionTimeoutBox.valueChanged.connect(ChangeSettings)
ui.UseMirrorsBox.clicked.connect(ChangeSettings)
ui.ExternalFetcherBox.clicked.connect(ChangeSettings)
ui.CompressManBox.clicked.connect(ChangeSettings)
ui.StripBinariesBox.clicked.connect(ChangeSettings)
ui.StripSharedBox.clicked.connect(ChangeSettings)
ui.StripStaticBox.clicked.connect(ChangeSettings)
ui.IgnoreMissingBox.clicked.connect(ChangeSettings)
ui.ConflictsBox.clicked.connect(ChangeSettings)
ui.BackupBox.clicked.connect(ChangeSettings)
ui.ScriptsBox.clicked.connect(ChangeSettings)

ui.ReposEdit.textChanged.connect(ChangeRepos)
ui.MirrorsEdit.textChanged.connect(ChangeMirrors)

ui.TargetsList.currentItemChanged.connect(RefreshWidgets)
ui.AliasesList.currentItemChanged.connect(RefreshTargets)

ui.TargetsList.setCurrentRow(0)

MainWindow.show()
sys.exit(app.exec_())

