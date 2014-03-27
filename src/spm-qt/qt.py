#!/usr/bin/python2

from PyQt4 import QtGui
import sys
import ConfigParser

import libqt4
import libmessage
message = libmessage.Message()
import libmisc
misc = libmisc.Misc()
import libpackage
database = libpackage.Database()
import libconfig
import libmode


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

    ui.CacheDirEdit.setText(libconfig.CACHE_DIR)
    ui.BuildDirEdit.setText(libconfig.BUILD_DIR)
    ui.IgnoreTargetsEdit.setText(libconfig.IGNORE)
    ui.ConnectionTimeoutBox.setValue(libconfig.TIMEOUT)
    ui.UseMirrorsBox.setCheckState(libconfig.MIRROR)
    ui.ExternalFetcherBox.setCheckState(libconfig.EXTERNAL)
    ui.CompressManBox.setCheckState(libconfig.COMPRESS_MAN)
    ui.StripBinariesBox.setCheckState(libconfig.STRIP_BINARIES)
    ui.StripSharedBox.setCheckState(libconfig.STRIP_SHARED)
    ui.StripStaticBox.setCheckState(libconfig.STRIP_STATIC)
    ui.IgnoreMissingBox.setCheckState(libconfig.IGNORE_MISSING)
    ui.ConflictsBox.setCheckState(libconfig.CONFLICTS)
    ui.BackupBox.setCheckState(libconfig.BACKUP)
    ui.ScriptsBox.setCheckState(libconfig.SCRIPTS)





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
    m = libmode.Source(targets, do_clean=True, do_prepare=True,
        do_compile=True, do_check=False, do_install=True, do_merge=True,
        do_remove=False, do_depends=True, do_reverse=True, do_update=True)
    Worker()

def Build():
    targets = [str(ui.TargetsList.currentItem().text())]
    global m
    m = libmode.Source(targets, do_clean=True, do_prepare=True,
        do_compile=True, do_check=False, do_install=True, do_merge=True,
        do_remove=False, do_depends=True, do_reverse=True, do_update=False)
    Worker()
    RefreshWidgets()

def Remove():
    targets = [str(ui.TargetsList.currentItem().text())]
    global m
    m = libmode.Source(targets, do_clean=False, do_prepare=False,
        do_compile=False, do_check=False, do_install=False, do_merge=False,
        do_remove=True, do_depends=False, do_reverse=True, do_update=False)
    Worker()
    RefreshWidgets()

def SyncRepos():
    global m
    m = libmode.Repo(libconfig.REPOSITORIES, do_clean=True, do_sync=True, do_update=False)
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
        reload(libconfig)
    except SystemExit:
        pass
    except Exception as detail:
        message.critical(detail)

def ChangeRepos():
    try:
        misc.file_write('/etc/spm/repositories.conf', str(ui.ReposEdit.toPlainText()))
        reload(libconfig)
    except SystemExit:
        pass
    except Exception as detail:
        message.critical(detail)

def ChangeMirrors():
    try:
        misc.file_write('/etc/spm/mirrors.conf', str(ui.MirrorsEdit.toPlainText()))
        reload(libconfig)
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

app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()
ui = libqt4.Ui_MainWindow()
ui.setupUi(MainWindow)

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

