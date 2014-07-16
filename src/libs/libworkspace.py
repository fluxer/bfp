#!/bin/python2

import os, sys
from PyQt4 import QtCore, QtGui

import libmisc, libmessage
misc = libmisc.Misc()
message = libmessage.Message()

class PluginException(Exception): pass


class General(object):
    ''' Common methods '''
    def __init__(self):
        self.settings = Settings()

    def set_style(self, app):
        ''' Style and icon application setup '''
        sstyle = self.settings.get('general/stylesheet', 'qdarkstyle')
        ssheet = '/etc/qdesktop/styles/' + sstyle + '/style.qss'
        if sstyle and os.path.isfile(ssheet):
            app.setStyleSheet(misc.file_read(ssheet))
        else:
            app.setStyleSheet('')
        # icon.setThemeName(self.settings.get('general/icontheme'))

    def get_icon(self, sicon):
        ''' Get icon '''
        for spath in misc.list_files(sys.prefix + 'share/icons/' + self.settings.get('general/icontheme')):
            if spath.startswith(sicon):
                sicon = spath
                break
        return QtGui.QIcon(sicon)

    def execute_program(self, sprogram, sdetached=True, skill=False):
        ''' Execute program from PATH '''
        p = QtCore.QProcess()
        if sdetached:
            p.startDetached(sprogram)
        else:
            p.start(sprogram)
            p.waitForFinished()
        if p.exitCode() > 0:
            p.close()
            raise(Exception(p.errorString()))
        else:
            if skill:
                p.terminate()
            p.close()


class Plugins(object):
    ''' Plugins handler '''
    def __init__(self, parent):
        self.parent = parent
        self.plugins_paths = [str(QtCore.QDir.homePath()) + '/.qworkspace/plugins', \
            '/etc/qworkspace/plugins', str(QtCore.QDir.currentPath()) + '/plugins']
        self.plugins_loaded = []
        self.plugins_all = []
        for spath in self.plugins_paths:
            if os.path.isdir(spath):
                sys.path.insert(0, spath)
                for splugin in os.listdir(spath):
                    sbase = os.path.basename(os.path.splitext(splugin)[0])
                    if not sbase.startswith('_') \
                        and (splugin.endswith('.py') or splugin.endswith('.so')):
                        self.plugins_all.append(sbase)
            else:
                message.warning('Plugins path does not exist', spath)

    def check_valid(self, splugin):
        ''' Check if plugin is valid '''
        for plugin in self.plugins_all:
            if plugin == splugin:
                return True
        return False

    def check_loaded(self, splugin):
        ''' Check if plugin is loaded '''
        for plugin in self.plugins_loaded:
            if plugin.name == splugin:
                return True
        return False

    def get_object(self, splugin):
        ''' Get object of plugin '''
        if not self.check_valid(splugin):
            message.critical('Plugin is not valid', splugin)
            raise(PluginException('Plugin is not valid', splugin))
        elif not self.check_loaded(splugin):
            message.critical('Plugin is not loaded', splugin)
            raise(PluginException('Plugin is not loaded', splugin))

        for plugin in self.plugins_loaded:
            if plugin.name == splugin:
                return plugin

    def load(self, splugin):
        ''' Load plugin '''
        if not self.check_valid(splugin):
            message.critical('Plugin is not valid', splugin)
            raise(PluginException('Plugin is not valid', splugin))
        elif self.check_loaded(splugin):
            message.warning('Plugin is already loaded', splugin)
            return

        try:
            message.info('Loading plugin', splugin)
            sbase = os.path.basename(os.path.splitext(splugin)[0])
            plugin = __import__(sbase).Plugin(self.parent)

            if not hasattr(plugin, 'name') or not hasattr(plugin, 'version') \
                or not hasattr(plugin, 'description')  or not hasattr(plugin, 'icon') \
                or not hasattr(plugin, '__init__') or not hasattr(plugin, 'unload'):
                message.critical('Plugin is not sane', detail)
                raise(PluginException('Plugin is not sane', detail))

            self.plugins_loaded.append(plugin)
            message.debug('Loading of plugin was successfull', splugin)
        except Exception as detail:
            message.critical('Plugin error', detail)
            raise(PluginException('Plugin error', detail))

    def open(self, splugin, spath):
        ''' Open plugin '''
        if not self.check_valid(splugin):
            message.critical('Plugin is not valid', splugin)
            raise(PluginException('Plugin is not valid', splugin))
        elif not self.check_loaded(splugin):
            message.critical('Plugin not is already loaded', splugin)
            raise(PluginException('Plugin not is already loaded', splugin))

        try:
            message.info('Opening plugin', splugin)
            plugin = self.get_object(splugin)

            if not hasattr(plugin, 'open'):
                message.critical('Plugin does not support open', detail)
                raise(PluginException('Plugin does not support open', detail))

            plugin.open(spath)
            message.debug('Opening of plugin was successfull', splugin)
        except Exception as detail:
            message.critical('Plugin error', detail)
            raise(PluginException('Plugin error', detail))


    def close(self, splugin):
        ''' Close plugin '''
        if not self.check_valid(splugin):
            message.critical('Plugin is not valid', splugin)
            raise(PluginException('Plugin is not valid', splugin))
        elif not self.check_loaded(splugin):
            message.critical('Plugin not is already loaded', splugin)
            raise(PluginException('Plugin not is already loaded', splugin))

        try:
            message.info('Closing plugin', splugin)
            plugin = self.get_object(splugin)

            if not hasattr(plugin, 'close'):
                message.critical('Plugin does not support close', detail)
                raise(PluginException('Plugin does not support close', detail))

            plugin.close()
            message.debug('Closing of plugin was successfull', splugin)
        except Exception as detail:
            message.critical('Plugin error', detail)
            raise(PluginException('Plugin error', detail))

    def unload(self, splugin):
        ''' Unload plugin '''
        if not self.check_valid(splugin):
            message.critical('Plugin is not valid', splugin)
            raise(PluginException('Plugin is not valid', splugin))
        elif not self.check_loaded(splugin):
            message.warning('Plugin is not loaded', splugin)
            return

        try:
            message.info('Unloading plugin', splugin)
            plugin = self.get_object(splugin)
            plugin.unload()
            message.debug('Unloading of plugin was successfull', splugin)
        except Exception as detail:
            message.critical('Plugin error', detail)
            raise(PluginException('Plugin error', detail))


class Settings(object):
    ''' Settings handler '''
    def __init__(self, sfile='qworkspace'):
        self.settings = QtCore.QSettings(sfile)

    def get(self, svalue, sfallback=''):
        ''' Get settings value '''
        return str(self.settings.value(svalue, sfallback).toString())

    def set(self, svariable, svalue):
        ''' Write settings value '''
        self.settings.setValue(svariable, svalue)
        self.settings.sync()

    def delete(self, svariable):
        ''' Deelete settings '''
        self.settings.remove(svariable)
        self.settings.sync()


class Recent(object):
    ''' Recent files/directories handler '''
    def __init__(self):
        self.settings = Settings('qrecent')
        # FIXME: load recent files into UI

    def ui_add(self, spath):
        ''' Add recent file/directory to UI '''
        pass

    def ui_remove(self, spath):
        ''' Remove recent file/directory from UI '''
        pass

    def open(self, spath):
        ''' Open file/dir with associated program '''
        Mimes().open(spath)

    def register(self, spath):
        ''' Register file/directory with program '''
        # FIXME: make registration with plugin possible
        self.settings.set('recent', spath)

    def unregister(self, spath):
        ''' Unregister recent file/directory '''
        self.settings.delete('recent/' + spath)

class Mimes(object):
    ''' Simple MIME implementation '''
    def __init__(self, parent=None):
        self.settings = Settings('qmime')
        self.parent = parent

    def get_mime(self, sprogram):
        ''' Get MIME associated with program '''
        for mime in self.get_mimes():
            if self.get_program(mime) == sprogram:
                return mime
        return None

    def get_program(self, smime):
        ''' Get program associated with MIME '''
        return self.settings.get(smime, '')

    def get_mimes(self):
        ''' Get all associated MIMEs '''
        return sorted(self.settings.settings.allKeys())

    def get_programs(self):
        ''' Get all programs '''
        programs = []
        for path in os.environ.get('PATH', '/bin:/usr/bin').split(':'):
            programs.extend(misc.list_files(path))
        return sorted(programs)

    def open(self, spath):
        ''' Open file/dir with associated program '''
        smime = misc.file_mime(spath)
        sprogram = self.get_program(smime)
        if sprogram:
            Plugins(self.parent).open(sprogram, spath)
        else:
            raise(Exception('Unregistered mime', smime))

    def register(self, smime, sprogram):
        ''' Register MIME with program '''
        self.settings.set(smime, sprogram)

    def unregister(self, smime):
        ''' Unregister MIME '''
        self.settings.delete(smime)
