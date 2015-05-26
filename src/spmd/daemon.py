#!/bin/python2

import sys, os, time, threading, dbus, dbus.service, dbus.mainloop.qt
from PyQt4 import QtCore
if sys.version < '3':
    import ConfigParser as configparser
else:
    import configparser
import libmessage, libmisc, libpackage, libspm
message = libmessage.Message()
message.DEBUG = True
misc = libmisc.Misc()
remote_notify = libmisc.Inotify()
local_notify = libmisc.Inotify()
slave_notify = libmisc.Inotify()
database = libpackage.Database()
misc.CATCH = True
libspm.CATCH = True

app = QtCore.QCoreApplication(sys.argv)
dbus.mainloop.qt.DBusQtMainLoop(set_as_default=True)
systembus = dbus.SystemBus()

class SPMD(dbus.service.Object):
    def __init__(self, conn, object_path='/com/spm/Daemon'):
        dbus.service.Object.__init__(self, conn, object_path)
        self.working = False

    def _AsyncCall(self, function, callback):
        try:
            function()
        except Exception as detail:
            callback(str(detail))
        else:
            callback('Success')

    def _GetUpdates(self, basename=False):
        targets = []
        for target in database.local_all(basename):
            # local targets can not be verified against invalid remote
            if not database.local_uptodate(target) \
                and database.remote_search(target):
                targets.append(target)
        return targets

    @dbus.service.signal('com.spm.Daemon')
    def Installed(self, target):
        ''' Emit that target was installed '''
        message.info('Installed', target)
        return target

    @dbus.service.signal('com.spm.Daemon')
    def Uninstalled(self, target):
        ''' Emit that target was removed '''
        message.info('Uninstalled', target)
        return target

    @dbus.service.signal('com.spm.Daemon')
    def Added(self, target):
        ''' Emit that target was added '''
        message.info('Added', target)
        return target

    @dbus.service.signal('com.spm.Daemon')
    def Removed(self, target):
        ''' Emit that target was removed '''
        message.info('Removed', target)
        return target

    @dbus.service.signal('com.spm.Daemon')
    def Updates(self, targets):
        ''' Emit that updates are available '''
        message.info('Updates', targets)
        return targets

    @dbus.service.signal('com.spm.Daemon')
    def Configs(self):
        ''' Emit that configs have changed '''
        message.info('Configs')
        return

    @dbus.service.signal('com.spm.Daemon')
    def Working(self):
        ''' Emit that the deamon is working '''
        message.debug('Working')
        self.working = True
        return

    @dbus.service.signal('com.spm.Daemon', signature='s')
    def Finished(self, msg):
        ''' Emit that the deamon has finished working '''
        message.debug('Finished', msg)
        self.working = False
        return str(msg)

    @dbus.service.method('com.spm.Daemon', out_signature='b')
    def isWorking(self):
        return self.working

    @dbus.service.method('com.spm.Daemon', in_signature='sss', \
        out_signature='s')
    def ConfSet(self, section, variable, value):
        ''' Set spm config variable to value '''
        message.info('Main config change requested')
        try:
            conf = configparser.SafeConfigParser()
            conf.read(libspm.MAIN_CONF)
            conf.set(section, variable, value)
            libspmconf = open(libspm.MAIN_CONF, 'wb')
            try:
                conf.write(libspmconf)
            finally:
                libspmconf.close()
            reload(libspm)
        except Exception as detail:
            message.critical(str(detail))
            return str(detail)
        self.Configs()
        return 'Success'

    @dbus.service.method('com.spm.Daemon', in_signature='s', \
        out_signature='s')
    def ReposSet(self, data):
        ''' Set repositories '''
        message.info('Repositories config change requested')
        try:
            misc.file_write(libspm.REPOSITORIES_CONF, data)
            reload(libspm)
        except Exception as detail:
            message.critical(str(detail))
            return str(detail)
        self.Configs()
        return 'Success'

    @dbus.service.method('com.spm.Daemon', in_signature='s', \
        out_signature='s')
    def MirrorsSet(self, data):
        ''' Set mirrors '''
        message.info('Mirrors config change requested')
        try:
            misc.file_write(libspm.MIRRORS_CONF, data)
            reload(libspm)
        except Exception as detail:
            message.critical(str(detail))
            return str(detail)
        self.Configs()
        return 'Success'

    @dbus.service.method('com.spm.Daemon', in_signature='s', \
        out_signature='s')
    def KeyServersSet(self, data):
        ''' Set key servers '''
        message.info('Key servers config change requested')
        try:
            misc.file_write(libspm.KEYSERVERS_CONF, data)
            reload(libspm)
        except Exception as detail:
            message.critical(str(detail))
            return str(detail)
        self.Configs()
        return 'Success'

    @dbus.service.method('com.spm.Daemon', in_signature='b', \
        out_signature='v')
    def RemoteAll(self, basename=False):
        ''' Get a list of all remote targets '''
        message.info('All remote targets requested')
        try:
            allremote = database.remote_all(bool(basename))
        except Exception as detail:
            message.critical(str(detail))
            return str(detail)
        return allremote

    @dbus.service.method('com.spm.Daemon', in_signature='s', \
        out_signature='v')
    def RemoteInfo(self, target):
        ''' Get property of a remote target '''
        message.info('Metadata requested for (remote)', target)
        try:
            match = database.remote_search(target)
            if not match:
                message.critical('%s is not valid' % target)
                return '%s is not valid' % target
            version = database.remote_metadata(match, 'version')
            release = database.remote_metadata(match, 'release')
            description = database.remote_metadata(match, 'description')
            depends = database.remote_metadata(match, 'depends') or ['']
            makedepends = database.remote_metadata(match, 'makedepends') or ['']
            checkdepends = database.remote_metadata(match, 'checkdepends') or ['']
            sources = database.remote_metadata(match, 'sources') or ['']
            pgpkeys = database.remote_metadata(match, 'pgpkeys') or ['']
            options = database.remote_metadata(match, 'options') or ['']
            backup = database.remote_metadata(match, 'backup') or ['']
        except Exception as detail:
            message.critical(str(detail))
            return str(detail)
        return (version, release, description, depends, makedepends, \
            checkdepends, sources, pgpkeys, options, backup)

    @dbus.service.method('com.spm.Daemon', in_signature='b', \
        out_signature='v')
    def LocalAll(self, basename=False):
        ''' Get a list of all local targets '''
        message.info('All local targets requested')
        try:
            alllocal = database.local_all(bool(basename))
        except Exception as detail:
            message.critical(str(detail))
            return str(detail)
        return alllocal

    @dbus.service.method('com.spm.Daemon', in_signature='s', \
        out_signature='v')
    def LocalInfo(self, target):
        ''' Get property of a local target '''
        message.info('Metadata requested for (local)', target)
        try:
            match = database.local_search(target)
            if not match:
                message.critical('%s is not valid' % target)
                return '%s is not valid' % target
            version = database.local_metadata(match, 'version')
            release = database.local_metadata(match, 'release')
            description = database.local_metadata(match, 'description')
            depends = database.local_metadata(match, 'depends') or ['']
            size = database.local_metadata(match, 'size')
            footprint = database.local_metadata(match, 'footprint')
        except Exception as detail:
            message.critical(str(detail))
            return str(detail)
        return (version, release, description, depends, size, footprint)

    @dbus.service.method('com.spm.Daemon')
    def Sync(self):
        ''' Syncronize repositories '''
        message.info('Syncing')
        try:
            self.Working()
            m = libspm.Repo(libspm.REPOSITORIES, do_sync=True, do_cache=True, do_prune=True)
            mthread = threading.Thread(target=self._AsyncCall, args=(m.main, self.Finished,))
            mthread.start()
        except Exception as detail:
            message.critical(str(detail))
            self.Finished(str(detail))

    @dbus.service.method('com.spm.Daemon', in_signature='b')
    def Update(self, fromsource=False):
        ''' Update system packages either from source or pre-build tarballs '''
        message.info('Updating system', time.ctime())
        try:
            self.Working()
            updates = self._GetUpdates()
            if not updates:
                message.sub_info('Nothing to do, system is up-to-date')
                self.Finished('Success')
            elif fromsource:
                self.Build(updates)
            else:
                self.Install(updates)
        except Exception as detail:
            message.critical(str(detail))
            self.Finished(str(detail))

    @dbus.service.method('com.spm.Daemon', in_signature='as')
    def Build(self, targets):
        ''' Build a package '''
        message.info('Building', targets)
        try:
            self.Working()
            m = libspm.Source(targets, do_clean=True, do_fetch=True, \
                do_prepare=True, do_compile=True, do_install=True, \
                do_merge=True)
            mthread = threading.Thread(target=self._AsyncCall, args=(m.main, self.Finished,))
            mthread.start()
        except Exception as detail:
            message.critical(str(detail))
            self.Finished(str(detail))

    @dbus.service.method('com.spm.Daemon', in_signature='as')
    def Install(self, targets):
        ''' Install a package '''
        message.info('Installing', targets)
        try:
            self.Working()
            m = libspm.Binary(targets, do_fetch=True, do_prepare=True, \
                do_merge=True, do_depends=True)
            mthread = threading.Thread(target=self._AsyncCall, args=(m.main, self.Finished,))
            mthread.start()
        except Exception as detail:
            message.critical(str(detail))
            self.Finished(str(detail))

    @dbus.service.method('com.spm.Daemon', in_signature='asb')
    def Remove(self, targets, recursive=False):
        ''' Install a package '''
        message.info('Removing', targets)
        try:
            self.Working()
            if recursive:
                # oh, boy! do not pass glibc here!
                m = libspm.Binary(targets, autoremove=True)
            else:
                m = libspm.Binary(targets, do_remove=True)
            mthread = threading.Thread(target=self._AsyncCall, args=(m.main, self.Finished,))
            mthread.start()
        except Exception as detail:
            message.critical(str(detail))
            self.Finished(str(detail))

    def LocalWatcher(self):
        ''' Installed software watcher '''
        try:
            message.info('Enetering local watch loop')
            if os.path.isdir(database.LOCAL_DIR):
                local_notify.watch_add(database.LOCAL_DIR)
            else:
                message.warning('Local directory non-existent', database.LOCAL_DIR)
            while True:
                for wd, mask, cookie, name in local_notify.event_read():
                    for watch in local_notify.watched:
                        desc = local_notify.watched[watch]
                        if desc == wd:
                            path = watch
                            break
                    if not path:
                        message.critical('Watch descriptor not found! Error, error, err...')
                        continue
                    if mask == local_notify.DELETE:
                        self.Uninstalled(path)
                    elif mask == local_notify.CREATE:
                        self.Installed(path)
                time.sleep(1)
        except Exception as detail:
            message.critical(str(detail))
        finally:
            pass

    def RemoteWatcher(self):
        ''' Repositories watcher '''
        try:
            message.info('Enetering remote watch loop')
            reposdir = os.path.join(database.CACHE_DIR, 'repositories')
            if os.path.isdir(reposdir):
                remote_notify.watch_add(reposdir, ignore=('.git',))
            else:
                message.warning('Remote directory non-existent', reposdir)
            while True:
                for wd, mask, cookie, name in remote_notify.event_read():
                    for watch in remote_notify.watched:
                        desc = remote_notify.watched[watch]
                        if desc == wd:
                            path = watch
                            break
                    if not path:
                        message.critical('Watch descriptor not found! Error, error, err...')
                        continue
                    if mask == remote_notify.DELETE:
                        self.Removed(path)
                    elif mask == remote_notify.CREATE:
                        self.Added(path)
                time.sleep(1)
        except Exception as detail:
            message.critical(str(detail))
        finally:
            pass

    def Slave(self):
        ''' Does update and whatnot '''
        global database
        # FIXME: make them configurable via spmd.conf
        ACTION = None # 'silent'
        UPDATE = 'minute' # 'never'
        FROMSOURCE = False
        try:
            message.info('Enetering slave loop')
            for conf in (libspm.MAIN_CONF, libspm.REPOSITORIES_CONF, \
                libspm.MIRRORS_CONF, libspm.KEYSERVERS_CONF):
                if os.path.isfile(conf):
                    slave_notify.watch_add(conf)
                else:
                    message.warning('Config non-existent', conf)

            currenttime = time.strftime('%s')
            timelock = os.path.join(database.CACHE_DIR, 'spmd.time')
            if os.path.isfile(timelock):
                lasttime = misc.file_read(timelock)
                if not lasttime:
                    lasttime = currenttime
            else:
                lasttime = currenttime
                misc.file_write(timelock, currenttime)
            message.info('Time of entrance', currenttime)
            message.info('Last entrance', lasttime)
            message.info('Update on', UPDATE)

            while True:
                update = False
                for wd, mask, cookie, name in slave_notify.event_read():
                    self.Configs()
                    reload(libspm)
                    reload(libpackage)
                    # TODO: does this even work? that's another thread this is running in...
                    database = libpackage.Database()
                currenttime = time.strftime('%s')
                result = (int(currenttime) - int(lasttime))
                if (result >= 60) and UPDATE == 'minute':
                    lasttime = currenttime
                    misc.file_write(timelock, str(currenttime))
                    update = True
                elif (result >= 3600) and UPDATE == 'hourly':
                    lasttime = currenttime
                    misc.file_write(timelock, str(currenttime))
                    update = True
                elif (result >= 86400) and UPDATE == 'daily':
                    lasttime = currenttime
                    misc.file_write(timelock, str(currenttime))
                    update = True
                elif (result >= 604800) and UPDATE == 'weekly':
                    lasttime = currenttime
                    misc.file_write(timelock, str(currenttime))
                    update = True
                elif (result >= 18144000) and UPDATE == 'monthly':
                    lasttime = currenttime
                    misc.file_write(timelock, str(currenttime))
                    update = True
                if update and ACTION == 'silent':
                    self.Sync()
                    self.Update(FROMSOURCE)
                elif update:
                    # emmiting with empty list can not guess the signature
                    updates = self._GetUpdates(True)
                    if updates:
                        self.Updates(updates)
                time.sleep(1)
        except Exception as detail:
            message.critical(str(detail))
        finally:
            pass

try:
    if not os.geteuid() == 0:
        message.critical('Attempting to run as non-root will bring you no good, the opposite is true too.')
        sys.exit(1)

    object = SPMD(systembus)
    lthread = threading.Thread(target=object.LocalWatcher)
    rthread = threading.Thread(target=object.RemoteWatcher)
    sthread = threading.Thread(target=object.Slave)
    lthread.start()
    rthread.start()
    sthread.start()
    name = dbus.service.BusName('com.spm.Daemon', systembus)
    message.info('Pumping up your system')
    sys.exit(app.exec_())
except KeyboardInterrupt:
    message.critical('Keyboard interrupt')
finally:
    pass
