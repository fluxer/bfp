#!/bin/python2

# This is only needed for Python v2 but is harmless for Python v3.
import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

import os, xdg.Menu, xdg.DesktopEntry, xdg.IconTheme
from PyQt4 import QtCore, QtGui

import libmisc, libsystem
misc = libmisc.Misc()
system = libsystem.System()


class General(object):
    ''' Common methods '''
    def set_style(self, app):
        ''' Style and icon application setup '''
        config.read()
        ssheet = '/etc/qdesktop/styles/' + config.GENERAL_STYLESHEET + '/style.qss'
        if config.GENERAL_STYLESHEET and os.path.isfile(ssheet):
            app.setStyleSheet(misc.file_read(ssheet))
        else:
            app.setStyleSheet('')
        # icon.setThemeName(config.GENERAL_ICONTHEME)

    def execute_program(self, sprogram, sdetached=True, skill=False):
        ''' Execute program from PATH '''
        p = QtCore.QProcess()
        if sdetached:
            p.startDetached(sprogram)
        else:
            p.start(sprogram)
        if p.exitCode() > 0:
            p.close()
            raise(Exception(p.errorString()))
        else:
            if skill:
                p.kill()
            p.close()

    def system_suspend(self, window):
        ''' Ask if system should suspend '''
        reply = QtGui.QMessageBox.question(window, 'Suspend', \
            'Are you sure you want to suspend the system?', \
            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            try:
                system.SUSPEND_DISK = config.SUSPEND_DISK
                system.SUSPEND_STATE = config.SUSPEND_STATE
                system.do_suspend()
            except Exception as detail:
                QtGui.QMessageBox.critical(window, 'Critical', str(detail))

    def system_shutdown(self, window):
        ''' Ask if system should shutdown '''
        reply = QtGui.QMessageBox.question(window, 'Shutdown', \
            'Are you sure you want to shutdown the system?', \
            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            try:
                system.do_shutdown()
            except Exception as detail:
                QtGui.QMessageBox.critical(window, 'Critical', str(detail))

    def system_reboot(self, window):
        ''' Ask if system should rebooted '''
        reply = QtGui.QMessageBox.question(window, 'Reboot', \
            'Are you sure you want to reboot the system?', \
            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            try:
                system.do_reboot()
            except Exception as detail:
                QtGui.QMessageBox.critical(window, 'Critical', str(detail))

general = General()


class Config(object):
    ''' Configuration handler '''
    def __init__(self):
        self.settings = QtCore.QSettings('qdesktop')
        self.read()

    def read(self):
        ''' Read config file '''
        self.GENERAL_STYLESHEET = str(self.settings.value('general/stylesheet', 'qdarkstyle'))
        self.GENERAL_ICONTHEME = str(self.settings.value('general/icontheme', ''))
        self.GENERAL_MENU = str(self.settings.value('general/menu', '/etc/xdg/menus/applications.menu'))
        self.WALLPAPER_IMAGE = str(self.settings.value('wallpaper/image', ''))
        self.WALLPAPER_STYLE = str(self.settings.value('wallpaper/style', 'stretch'))
        self.WALLPAPER_COLOR = str(self.settings.value('wallpaper/color', '#b4b4b4'))
        self.DEFAULT_TERMINAL = str(self.settings.value('default/terminal', 'xterm'))
        self.DEFAULT_FILEMANAGER = str(self.settings.value('default/filemanager', 'qfile'))
        self.DEFAULT_WEBBROWSER = str(self.settings.value('default/webbrowser', 'qbrowse'))

        self.SUSPEND_DISK = str(self.settings.value('suspend/disk', 'suspend'))
        self.SUSPEND_STATE = str(self.settings.value('suspend/state', 'mem'))
        self.CPU_POWER = str(self.settings.value('cpu/power', 'performance'))
        self.CPU_BATTERY = str(self.settings.value('cpu/battery', 'ondemand'))
        self.BACKLIGHT_POWER = str(self.settings.value('backlight/power', '15'))
        self.BACKLIGHT_BATTERY = str(self.settings.value('backlight/battery', '10'))
        self.LID_POWER = str(self.settings.value('lid/power', 'suspend'))
        self.LID_BATTERY = str(self.settings.value('lid/battery', 'shutdown'))
        self.LOW_BATTERY = str(self.settings.value('battery/low', 'suspend'))

    def write(self, variable, value):
        ''' Write config file '''
        self.settings.setValue(variable, value)
        self.settings.sync()
        self.read()

config = Config()


class Menu(object):
    ''' Menu related methods '''
    def __init__(self, app, widget):
        self.app = app
        self.widget = widget
        self.xdg = xdg.Menu

    def execute_desktop(self, sfile, args=''):
        ''' Execute program from .desktop file '''
        x = self.xdg.MenuEntry(sfile)
        tryExec = x.DesktopEntry.getTryExec()
        Exec = x.DesktopEntry.getExec()
        if x.DesktopEntry.getTerminal():
            Exec = config.DEFAULT_TERMINAL + ' -e ' + Exec

        # if TryExec is set in .desktop execute it first
        if tryExec and not tryExec == Exec:
            general.execute_program(tryExec, False, True)
        # if it gets here fire up the program
        print(Exec +' ' + args)
        general.execute_program(Exec + ' ' + args)

    def dynamic_menu(self, menu, depth=0, widget=None):
        ''' Setup dynamic applications menu '''
        if not widget:
            widget = self.widget
        depth += 1
        for entry in menu.getEntries():
            if isinstance(entry, self.xdg.Menu):
                # FIXME: it seems that on elementary-usu category icons begin with "applications-",
                #              is that by the specs??
                # FIXME: support translated entries
                dicon = xdg.IconTheme.getIconPath('applications-' + str(entry).lower())
                if dicon:
                    self.dynamic_menu(entry, depth, widget.addMenu(QtGui.QIcon(dicon), str(entry)))
                else:
                    self.dynamic_menu(entry, depth, widget.addMenu(str(entry)))
            elif isinstance(entry, self.xdg.MenuEntry):
                dicon = xdg.IconTheme.getIconPath(entry.DesktopEntry.getIcon())
                name = entry.DesktopEntry.getName()
                if dicon:
                    e = widget.addAction(QtGui.QIcon(dicon), name)
                else:
                    e = widget.addAction(name)
                widget.connect(e, QtCore.SIGNAL('triggered()'), \
                    lambda sfile=entry.DesktopEntry.getFileName(): self.execute_desktop(sfile))
            elif isinstance(entry, self.xdg.Separator):
                self.widget.addSeparator()
            #elif isinstance(entry, self.xdg.Header):
            #    pass
        depth -= 1

    def build(self):
        ''' Build applications menu '''
        if not os.path.isfile(config.GENERAL_MENU):
            return
        self.widget.clear()
        xdg.Config.icon_theme = config.GENERAL_ICONTHEME
        return self.dynamic_menu(self.xdg.parse(config.GENERAL_MENU))


class Actions(object):
    ''' Mostly menu action shortcuts '''
    def __init__(self, window, app):
        self.window = window
        self.app = app
        self.clipboard = self.app.clipboard()
        self.cut = None
        self.copy = None
        self.thread = None

    def check_exists(self, sfile):
        ''' Check if file/dir exists and offer to rename '''
        sfile_basename = os.path.basename(sfile)
        sfile_dirname = os.path.dirname(sfile)
        sfile_basename, ok = QtGui.QInputDialog.getText(self.window, 'File/directory exists', \
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

    def open_items(self, variant):
        ''' Open files/directories with a software of choise '''
        sitems = ''
        for svar in variant:
            sitems += '"' + svar + '" '
        general.execute_program('qopen ' + sitems)

    def rename_items(self, variant):
        ''' Rename files/directories '''
        sitems = ''
        for svar in variant:
            sitems += '"' + svar + '" '
        general.execute_program('qpaste --rename ' + sitems)

    def cut_items(self, slist):
        ''' Cut files/directories for future paste '''
        sitems = misc.string_convert(slist)
        self.clipboard.setText(sitems)
        self.cut = slist
        self.copy = None

    def copy_items(self, slist):
        ''' Copy files/directories for future paste '''
        sitems = misc.string_convert(slist)
        self.clipboard.setText(sitems)
        self.cut = None
        self.copy = slist

    def paste_items(self):
        ''' Paste files/directories '''
        sitems = ''
        if self.cut:
            for svar in self.cut:
                sitems += '"' + svar + '" '
            general.execute_program('qpaste --cut ' + sitems)
        elif self.copy:
            for svar in self.copy:
                sitems += '"' + svar + '" '
            general.execute_program('qpaste --copy ' + sitems)

    def delete_items(self, variant):
        ''' Delete files/directories '''
        sitems = ''
        for svar in variant:
            sitems += '"' + svar + '" '
        general.execute_program('qpaste --delete ' + sitems)

    def extract_items(self, variant):
        ''' Extract archives '''
        for sfile in variant:
            if misc.archive_supported(sfile):
                general.execute_program('qarchive --extract ' + '"' + sfile + '" ')

    def gzip_items(self, variant):
        ''' Gzip files/directories into archive '''
        sitems = ''
        for svar in variant:
            sitems += '"' + svar + '" '
        general.execute_program('qarchive --gzip ' + sitems)

    def bzip2_items(self, variant):
        ''' BZip2 files/directories into archive '''
        sitems = ''
        for svar in variant:
            sitems += '"' + svar + '" '
        general.execute_program('qarchive --bzip2 ' + sitems)

    def new_file(self):
        ''' Create a new file '''
        svar, ok = QtGui.QInputDialog.getText(self.window, 'New file', \
            'Name:', QtGui.QLineEdit.Normal)
        svar = os.path.realpath(str(svar))
        if ok and svar:
            if os.path.exists(svar):
                svar = self.check_exists(svar)
                if not svar:
                    return
            svar = str(svar)
            misc.file_write(os.path.realpath(svar), '')
            return svar

    def new_directory(self):
        ''' Create a new directory '''
        svar, ok = QtGui.QInputDialog.getText(self.window, 'New directory', \
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

    def properties_items(self, variant):
        ''' View properties of files/directories '''
        for svar in variant:
            general.execute_program('qproperties "' + svar + '"')


class Mime(object):
    ''' Simple MIME implementation '''
    def __init__(self):
        self.settings = QtCore.QSettings('qmime')

    def get_mime(self, sprogram):
        ''' Get MIME associated with program '''
        for mime in self.get_mimes():
            if self.get_program(mime) == sprogram:
                return mime
        return None

    def get_program(self, smime):
        ''' Get program associated with MIME '''
        self.settings.sync()
        return str(self.settings.value(smime, '').toString())

    def get_mimes(self):
        ''' Get all associated MIMEs '''
        return sorted(self.settings.allKeys())

    def get_programs(self):
        ''' Get all programs '''
        programs = []
        for path in os.environ.get('PATH', '/bin:/usr/bin').split(':'):
            programs.extend(misc.list_files(path))
        return sorted(programs)

    def open(self, svar):
        ''' Open file/dir with associated program '''
        smime = misc.file_mime(svar)
        sprogram = self.get_program(smime)
        if sprogram:
            general.execute_program(sprogram + ' "' + svar + '"')
        else:
            raise(Exception('Unregistered mime', smime))

    def register(self, smime, sprogram):
        ''' Register MIME with program and icon '''
        self.settings.setValue(smime, sprogram)
        self.settings.sync()

    def unregister(self, smime):
        ''' Unregister MIME '''
        self.settings.remove(smime)
        self.settings.sync()
