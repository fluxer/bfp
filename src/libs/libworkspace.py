#!/bin/python2

import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

import os, sys
from PyQt4 import QtCore, QtGui
import libmisc, libmessage
misc = libmisc.Misc()
message = libmessage.Message()

class PluginException(Exception):
    ''' Custom exceptions '''
    pass


class Settings(object):
    ''' Settings handler '''
    def __init__(self, sfile='qworkspace'):
        self.settings = QtCore.QSettings(sfile)
        self.settings.setPath(QtCore.QSettings.IniFormat, \
            QtCore.QSettings.SystemScope, '/etc/qworkspace')

    def get(self, svalue, sfallback=''):
        ''' Get settings value '''
        self.settings.sync()
        return str(self.settings.value(svalue, sfallback))

    def set(self, svariable, svalue):
        ''' Write settings value '''
        self.settings.sync()
        self.settings.setValue(svariable, svalue)

    def delete(self, svariable):
        ''' Delete settings '''
        self.settings.sync()
        self.settings.remove(svariable)


class General(object):
    ''' Common methods '''
    def __init__(self):
        self.settings = Settings()

    def set_style(self, app):
        ''' Style and icon application setup '''
        sstyle = self.settings.get('general/stylesheet', 'Plastique')
        ssheet = '/etc/qworkspace/styles/' + sstyle + '/style.qss'
        if sstyle and os.path.isfile(ssheet):
            app.setStyleSheet(misc.file_read(ssheet))
        elif sstyle:
            app.setStyle(sstyle)
        else:
            app.setStyleSheet('')

    def get_icon(self, sicon):
        ''' Get icon '''
        sicons = os.path.join(sys.prefix, 'share/icons')
        scache = str(QtCore.QDir.homePath()) + '/.cache/icons.txt'
        if not os.path.isfile(scache):
            misc.file_write(scache, '\n'.join(misc.list_files(sicons)))
        for spath in misc.file_readlines(scache):
            if misc.file_name(spath) == sicon:
                sicon = spath
                break
        return QtGui.QIcon(sicon)

    def get_pixmap(self, spixmap):
        ''' Get icon '''
        spixmaps = os.path.join(sys.prefix, 'share/icons')
        scache = str(QtCore.QDir.homePath()) + '/.cache/icons.txt'
        if not os.path.isfile(scache):
            misc.file_write(scache, '\n'.join(misc.list_files(sicons)))
        for spath in misc.file_readlines(scache):
            if misc.file_name(spath) == spixmap:
                spixmap = spath
                break
        return QtGui.QPixmap(spixmap)

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
        self.plugins_paths = ['/etc/qworkspace/plugins', \
            str(QtCore.QDir.currentPath()) + '/plugins']
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
        self.plugins_all.sort()
        self.mime_settings = Settings('qmime')
        self.recent_settings = Settings('qrecent')

    def plugin_valid(self, splugin):
        ''' Check if plugin is valid '''
        for plugin in self.plugins_all:
            if plugin == splugin:
                return True
        return False

    def plugin_loaded(self, splugin):
        ''' Check if plugin is loaded '''
        for plugin in self.plugins_loaded:
            if plugin.name == splugin:
                return True
        return False

    def plugin_object(self, splugin):
        ''' Get object of plugin '''
        if not self.plugin_valid(splugin):
            message.critical('Plugin is not valid', splugin)
            raise(PluginException('Plugin is not valid', splugin))
        elif not self.plugin_loaded(splugin):
            message.critical('Plugin is not loaded', splugin)
            raise(PluginException('Plugin is not loaded', splugin))

        for plugin in self.plugins_loaded:
            if plugin.name == splugin:
                return plugin

    def plugin_load(self, splugin):
        ''' Load plugin '''
        if not self.plugin_valid(splugin):
            message.critical('Plugin is not valid', splugin)
            raise(PluginException('Plugin is not valid', splugin))
        elif self.plugin_loaded(splugin):
            message.warning('Plugin is already loaded', splugin)
            return

        try:
            message.info('Loading plugin', splugin)
            sname = misc.file_name(splugin)
            plugin = __import__(sname).Plugin(self.parent)

            if not hasattr(plugin, 'name') or not hasattr(plugin, 'version') \
                or not hasattr(plugin, 'description') or not hasattr(plugin, 'icon') \
                or not hasattr(plugin, '__init__') or not hasattr(plugin, 'unload'):
                message.critical('Plugin is not sane', detail)
                raise(PluginException('Plugin is not sane', detail))

            self.plugins_loaded.append(plugin)
            message.debug('Loading of plugin was successfull', splugin)
        except Exception as detail:
            message.critical('Plugin error', detail)
            raise(PluginException('Plugin error', detail))

    def plugin_open_with(self, splugin, spath, bregister=True):
        ''' Open path with plugin '''
        if not self.plugin_valid(splugin):
            message.critical('Plugin is not valid', splugin)
            raise(PluginException('Plugin is not valid', splugin))
        elif not self.plugin_loaded(splugin):
            message.critical('Plugin is not loaded', splugin)
            raise(PluginException('Plugin is not loaded', splugin))

        try:
            message.info('Opening plugin', splugin)
            plugin = self.plugin_object(splugin)

            if not hasattr(plugin, 'open'):
                message.critical('Plugin does not support open', detail)
                raise(PluginException('Plugin does not support open', detail))

            plugin.open(spath)
            if bregister:
                self.recent_register(spath)
            message.debug('Opening of plugin was successfull', splugin)
        except Exception as detail:
            message.critical('Plugin error', detail)
            raise(PluginException('Plugin error', detail))

    def plugin_open(self, spath, bregister=True):
        ''' Open path with associated plugin '''
        smime = misc.file_mime(spath)
        splugin = self.mime_plugin(smime)

        if not splugin:
            # FIXME: automatically associate?
            message.critical('No plugin associated with mime', smime)
            raise(PluginException('No plugin associated with mime', smime))
        elif not self.plugin_valid(splugin):
            message.critical('Plugin is not valid', splugin)
            raise(PluginException('Plugin is not valid', splugin))
        elif not self.plugin_loaded(splugin):
            message.critical('Plugin is not loaded', splugin)
            raise(PluginException('Plugin is not loaded', splugin))

        try:
            message.info('Opening path with ' + splugin, spath)
            plugin = self.plugin_object(splugin)

            if not hasattr(plugin, 'open'):
                message.critical('Plugin does not support open', detail)
                raise(PluginException('Plugin does not support open', detail))

            plugin.open(spath)
            if bregister:
                self.recent_register(spath)
            message.debug('Opening of plugin was successfull', splugin)
        except Exception as detail:
            message.critical('Plugin error', detail)
            raise(PluginException('Plugin error', detail))

    def plugin_close(self, splugin, sindex=None):
        ''' Close plugin '''
        if not self.plugin_valid(splugin):
            message.critical('Plugin is not valid', splugin)
            raise(PluginException('Plugin is not valid', splugin))
        elif not self.plugin_loaded(splugin):
            message.critical('Plugin is not loaded', splugin)
            raise(PluginException('Plugin is not loaded', splugin))

        try:
            message.info('Closing plugin', splugin)
            plugin = self.plugin_object(splugin)

            if not hasattr(plugin, 'close'):
                message.critical('Plugin does not support close', detail)
                raise(PluginException('Plugin does not support close', detail))

            plugin.close(sindex)
            message.debug('Closing of plugin was successfull', splugin)
        except Exception as detail:
            message.critical('Plugin error', detail)
            raise(PluginException('Plugin error', detail))

    def plugin_unload(self, splugin):
        ''' Unload plugin '''
        if not self.plugin_valid(splugin):
            message.critical('Plugin is not valid', splugin)
            raise(PluginException('Plugin is not valid', splugin))
        elif not self.plugin_loaded(splugin):
            message.warning('Plugin is not loaded', splugin)
            return

        try:
            message.info('Unloading plugin', splugin)
            plugin = self.plugin_object(splugin)
            plugin.unload()
            message.debug('Unloading of plugin was successfull', splugin)
        except Exception as detail:
            message.critical('Plugin error', detail)
            raise(PluginException('Plugin error', detail))

    def recent_restore(self):
        message.info('Restoring recent files')
        for key in self.recent_settings.settings.allKeys():
            self.recent_register(str(key))

    def recent_register(self, spath):
        ''' Register recent path '''
        # limit to 30
        keys = self.recent_settings.settings.allKeys()
        if len(keys) > 29:
            pass
            # self.recent_unregister('recent/30')

        for key in keys:
            if self.recent_settings.get(key) == spath:
                message.sub_warning('Recent already registered', key)
                self.recent_unregister(key)

        if not os.path.exists('/' + spath):
            message.warning('Recent path does not exist', '/' + spath)
            self.recent_unregister(spath)
            return

        message.info('Registering recent path', spath)
        button = QtGui.QPushButton(general.get_icon('document-open-recent'), \
            os.path.basename(spath))
        button.clicked.connect(lambda: self.plugin_open('/' + spath, False))
        self.parent.toolBox.widget(0).layout().addWidget(button)
        self.recent_settings.set(spath, '')

    def recent_unregister(self, spath):
        ''' Unregister recent path '''
        message.info('Unregistering recent path', spath)
        self.recent_settings.delete(spath)

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
        return sorted(self.mime_settings.settings.allKeys())

    def mime_plugins(self):
        ''' Get all programs '''
        return Plugins(None).plugins_all

    def mime_register(self, smime, splugin):
        ''' Register MIME with plugin '''
        message.info('Registering MIME ' + smime, splugin)
        self.mime_settings.set(smime, splugin)

    def mime_unregister(self, smime):
        ''' Unregister MIME '''
        message.info('Unregistering MIME', smime)
        self.mime_settings.delete(smime)

    def notify_widget(self, stype, msg, timeout):
        nframe = QtGui.QGroupBox(stype)
        nicon = QtGui.QLabel()
        if stype == 'Information':
            nicon.setPixmap(general.get_pixmap('help-info'))
        elif stype == 'Warning':
            nicon.setPixmap(general.get_pixmap('dialog-warning'))
        elif stype == 'Critical':
            nicon.setPixmap(general.get_pixmap('dialog-critical'))
        nlabel = QtGui.QLabel(msg)
        nbutton = QtGui.QPushButton(general.get_icon('window-close'), 'OK')
        nbutton.clicked.connect(nframe.deleteLater)
        nlayout = QtGui.QGridLayout()
        nlayout.addWidget(nicon)
        nlayout.addWidget(nlabel)
        nlayout.addWidget(nbutton)
        nframe.setLayout(nlayout)
        if timeout:
            QtCore.QTimer.singleShot(timeout * 1000, nframe.deleteLater)
        return nframe

    def notify_information(self, msg, timeout=False):
        ''' Notify with information status '''
        nwidget = self.notify_widget('Information', msg, timeout)
        self.parent.toolBox.widget(2).layout().addWidget(nwidget)

    def notify_warning(self, msg, timeout=False):
        ''' Notify with warning status '''
        nwidget = self.notify_widget('Warning', msg, timeout)
        self.parent.toolBox.widget(2).layout().addWidget(nwidget)

    def notify_critical(self, msg, timeout=False):
        ''' Notify with critical status '''
        nwidget = self.notify_widget('Critical', msg, timeout)
        self.parent.toolBox.widget(2).layout().addWidget(nwidget)
