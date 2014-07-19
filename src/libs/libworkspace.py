#!/bin/python2

import os, sys
from PyQt4 import QtCore, QtGui

import libmisc, libmessage
misc = libmisc.Misc()
message = libmessage.Message()

class PluginException(Exception):
    pass


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


class General(object):
    ''' Common methods '''
    def __init__(self):
        self.settings = Settings()

    def set_style(self, app):
        ''' Style and icon application setup '''
        sstyle = self.settings.get('general/stylesheet', 'qdarkstyle')
        ssheet = '/etc/qworkspace/styles/' + sstyle + '/style.qss'
        if sstyle and os.path.isfile(ssheet):
            app.setStyleSheet(misc.file_read(ssheet))
        else:
            app.setStyleSheet('')
        # icon.setThemeName(self.settings.get('general/icontheme'))

    def get_icon(self, sicon):
        ''' Get icon '''
        lpaths = misc.list_files(sys.prefix + 'share/icons/' + self.settings.get('general/icontheme'))
        lpaths.extend(misc.list_files(sys.prefix + 'share/pixmaps'))
        for spath in lpaths:
            if misc.file_name(spath) == sicon:
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
general = General()

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
                    sname = misc.file_name(splugin)
                    if not sname in self.plugins_all and not sname.startswith('_') \
                        and (splugin.endswith('.py') or splugin.endswith('.so')):
                        self.plugins_all.append(sname)
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
            sname = misc.file_name(splugin)
            plugin = __import__(sname).Plugin(self.parent)

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

    def open_with(self, splugin, spath):
        ''' Open path with plugin '''
        if not self.check_valid(splugin):
            message.critical('Plugin is not valid', splugin)
            raise(PluginException('Plugin is not valid', splugin))
        elif not self.check_loaded(splugin):
            message.critical('Plugin is not loaded', splugin)
            raise(PluginException('Plugin is not loaded', splugin))

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


    def open(self, spath):
        ''' Open path with associated plugin '''
        smime = misc.file_mime(spath)
        splugin = API(self.parent).mime_plugin(smime)

        if not splugin:
            # FIXME: automatically associate?
            message.critical('No plugin associated with mime', smime)
            raise(PluginException('No plugin associated with mime', smime))
        elif not self.check_valid(splugin):
            message.critical('Plugin is not valid', splugin)
            raise(PluginException('Plugin is not valid', splugin))
        elif not self.check_loaded(splugin):
            message.critical('Plugin is not loaded', splugin)
            raise(PluginException('Plugin is not loaded', splugin))

        try:
            message.info('Opening path with ' + splugin, spath)
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
            message.critical('Plugin is not loaded', splugin)
            raise(PluginException('Plugin is not loaded', splugin))

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


class API(object):
    ''' Recent, Application, Notifiaction and MIME implementation '''
    def __init__(self, parent):
        self.parent = parent
        self.mime_settings = Settings('qmime')
        self.recent_settings = Settings('recent')
        self.plugins = Plugins(self.parent)

    def recent_restore(self):
        message.info('Restoring recent files')
        for recent in self.recent_settings.allKeys():
            self.recent_register(recent.value())

    def recent_register(self, spath):
        ''' Register recent path '''
        # FIXME: limit to 30?
        button = QtGui.QPushButton(general.get_icon('documetn-open-recent'), misc.file_name(spath))
        button.clicked.connect(lambda: self.plugins.open(spath))
        self.parent.toolBox.widget(0).addWidget(button)
        self.recent_settings.set('recent', spath)

    def recent_unregister(self, spath):
        ''' Unregister recent path '''
        self.recent_settings.delete('recent/' + spath)

    def mime_mime(self, splugin):
        ''' Get MIME associated with program '''
        for mime in self.mime_mimes():
            if self.mime_plugin(mime) == splugin:
                return mime
        return

    def mime_plugin(self, smime):
        ''' Get plugin associated with MIME '''
        return self.mime_settings.get(smime, '')

    def mime_mimes(self):
        ''' Get all associated MIMEs '''
        return sorted(self.mime_settings.allKeys())

    def mime_plugins(self):
        ''' Get all programs '''
        return sorted(Plugins(None).plugins_all)

    def mime_register(self, smime, splugin):
        ''' Register MIME with plugin '''
        self.mime_settings.set(smime, splugin)

    def mime_unregister(self, smime):
        ''' Unregister MIME '''
        self.mime_settings.delete(smime)
