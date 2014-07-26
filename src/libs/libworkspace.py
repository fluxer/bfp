#!/bin/python2

import os, sys, shutil
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
        self.settings.setPath(QtCore.QSettings.IniFormat, QtCore.QSettings.SystemScope, '/etc/qworkspace')

    def get(self, svalue, sfallback=''):
        ''' Get settings value '''
        self.settings.sync()
        return str(self.settings.value(svalue, sfallback).toString())

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


class Actions(object):
    ''' Mostly menu action shortcuts '''
    def __init__(self, parent=None):
        super(Actions, self).__init__()
        self.parent = parent
        #self.app = QtGui.QApplication([])
        #self.clipboard = self.app.clipboard()
        self.cut = None
        self.copy = None
        self.thread = None

    def check_exists(self, sfile):
        ''' Check if file/dir exists and offer to rename '''
        sfile_basename = os.path.basename(sfile)
        sfile_dirname = os.path.dirname(sfile)
        sfile_basename, ok = QtGui.QInputDialog.getText(self, 'File/directory exists', \
                'File/directory exists, new name:', QtGui.QLineEdit.Normal, sfile_basename)
        sfile_basename = str(sfile_basename)
        if ok and sfile_basename:
            if not os.path.exists(sfile_dirname + '/' + sfile_basename):
                return sfile_basename
            else:
                return self.check_exists(sfile)
        elif not ok:
            return

    def execute_items(self, variant):
        ''' Execute files with default software '''
        for svar in variant:
            if os.path.isfile(svar):
                general.execute_program(svar)

    def cut_items(self, slist):
        ''' Cut files/directories for future paste '''
        self.clipboard.setText(misc.string_convert(slist))
        self.cut = slist
        self.copy = None

    def copy_items(self, slist):
        ''' Copy files/directories for future paste '''
        self.clipboard.setText(misc.string_convert(slist))
        self.cut = None
        self.copy = slist

    def paste_items(self, sdest=os.curdir):
        ''' Paste files/directories '''
        sitems = ''
        if self.cut:
            for svar in self.cut:
                if os.path.isdir(svar):
                    shutil.copytree(svar, sdest)
                    misc.dir_remove(svar)
                else:
                    shutil.copy2(svar, sdest)
                    os.unlink(svar)
        elif self.copy:
            for svar in self.copy:
                if os.path.isdir(svar):
                    shutil.copytree(svar, sdest)
                else:
                    shutil.copy2(svar, sdest)
        else:
            # FIXME: it will break on paths with spaces,
            #        is it OK to use \n in the clipboard content to solve this?
            for svar in self.clipboard.text().split(' '):
                if os.path.isdir(svar):
                    shutil.copytree(svar, sdest)
                else:
                    shutil.copy2(svar, sdest)

    def delete_items(self, variant):
        ''' Delete files/directories '''
        for svar in variant:
            if os.path.isdir(svar):
                misc.dir_remove(svar)
            else:
                os.unlink(svar)

    def new_file(self):
        ''' Create a new file '''
        svar, ok = QtGui.QInputDialog.getText(self, 'New file', \
            'Name:', QtGui.QLineEdit.Normal)
        svar = os.path.realpath(str(svar))
        if ok and svar:
            if os.path.exists(svar):
                svar = self.check_exists(svar)
                if not svar:
                    return
            svar = str(svar)
            misc.file_touch(os.path.realpath(svar))
            return svar

    def new_directory(self):
        ''' Create a new directory '''
        svar, ok = QtGui.QInputDialog.getText(self, 'New directory', \
            'Name:', QtGui.QLineEdit.Normal)
        svar = os.path.realpath(str(svar))
        if ok and svar:
            if os.path.isdir(svar):
                svar = self.check_exists(svar)
                if not svar:
                    return
            svar = str(svar)
            misc.dir_create(svar)
            return svar

    def rename_items(self, variant):
        ''' Rename files/directories '''
        pass

    def properties_items(self, variant):
        ''' View properties of files/directories '''
        pass

    def extract_items(self, variant):
        ''' Extract archives '''
        pass

    def gzip_items(self, variant):
        ''' Gzip files/directories into archive '''
        pass

    def bzip2_items(self, variant):
        ''' BZip2 files/directories into archive '''
        pass



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
                or not hasattr(plugin, 'description')  or not hasattr(plugin, 'icon') \
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

        message.info('Registering recent path', spath)
        button = QtGui.QPushButton(general.get_icon('document-open-recent'), os.path.basename(spath))
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
        return sorted(Plugins(None).plugins_all)

    def mime_register(self, smime, splugin):
        ''' Register MIME with plugin '''
        message.info('Registering MIME ' + smime, splugin)
        self.mime_settings.set(smime, splugin)

    def mime_unregister(self, smime):
        ''' Unregister MIME '''
        message.info('Unregistering MIME', smime)
        self.mime_settings.delete(smime)
