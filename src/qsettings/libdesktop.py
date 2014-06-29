#!/bin/python2

# This is only needed for Python v2 but is harmless for Python v3.
import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

import os
import xdg.Menu, xdg.DesktopEntry, xdg.IconTheme
from PyQt4 import QtCore, QtGui

import libmisc, libsystem
misc = libmisc.Misc()
system = libsystem.System()


class General(object):
    ''' Common methods '''
    def set_style(self):
        # FIXME: set stylesheet and icon theme
        pass

    def execute_program(self, sprogram):
        ''' Execute program from PATH '''
        p = QtCore.QProcess()
        if not p.startDetached(sprogram):
            p.close()
            raise(Exception(p.errorString()))
        else:
            p.close()

    def system_suspend(self, window):
        reply = QtGui.QMessageBox.question(window, 'Suspend', \
            'Are you sure you want to suspend the system?', \
            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            system.do_suspend()

    def system_shutdown(self, window):
        reply = QtGui.QMessageBox.question(window, 'Shutdown', \
            'Are you sure you want to shutdown the system?', \
            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            system.do_shutdown()

    def system_reboot(self, window):
        reply = QtGui.QMessageBox.question(window, 'Reboot', \
            'Are you sure you want to reboot the system?', \
            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            system.do_reboot()

general = General()


class Config(object):
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
        self.DEFAULT_WEBBROWSER = str(self.settings.value('default/webbrowser', 'qupzilla'))

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
        self.read()

config = Config()


class Menu(object):
    ''' Menu related methods '''
    def __init__(self, app, widget):
        self.app = app
        self.widget = widget
        self.xdg = xdg.Menu

    def execute_desktop(self, sfile):
        ''' Execute program from .desktop file '''
        x = self.xdg.MenuEntry(sfile)
        tryExec = x.DesktopEntry.getTryExec()
        Exec = x.DesktopEntry.getExec()
        if x.DesktopEntry.getTerminal():
            Exec = config.DEFAULT_TERMINAL + ' -e ' + Exec

        # if TryExec is set in .desktop execute it first
        if tryExec and not tryExec == Exec:
            general.execute_program(tryExec)
        # if it gets here fire up the program
        general.execute_program(Exec)

    def dynamic_menu(self, menu, depth=0, widget=None):
        ''' Setup dynamic applications menu '''
        if not widget:
            widget = self.widget
        depth += 1
        for entry in menu.getEntries():
            if isinstance(entry, self.xdg.Menu):
                # FIXME: it seems that on elementary-usu category icons begin with "applications-",
                #              is that by the specs??
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
            #elif isinstance(entry, self.xdg.Separator):
            #    self.widget.addSeparator()
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
        sfile_basename = os.path.basename(sfile)
        sfile_dirname = os.path.dirname(sfile)
        sfile_basename, ok = QtGui.QInputDialog.getText(self.window, "File/directory exists", \
                "File/directory exists, new name:", QtGui.QLineEdit.Normal, sfile_basename)
        sfile_basename = str(sfile_basename)
        if ok and sfile_basename:
            if not os.path.exists(sfile_dirname + '/' + sfile_basename):
                return sfile_basename
            else:
                return self.check_exists(sfile)
        elif not ok:
            return

    def rename_items(self, variant):
        general.execute_program('qpaste --rename ' + misc.string_convert(variant))

    def cut_items(self, slist):
        sitems = misc.string_convert(slist)
        self.clipboard.setText(sitems)
        self.cut = slist
        self.copy = None

    def copy_items(self, slist):
        sitems = misc.string_convert(slist)
        self.clipboard.setText(sitems)
        self.cut = None
        self.copy = slist

    def paste_items(self):
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
        sitems = ''
        for svar in variant:
            sitems += '"' + svar + '" '
        general.execute_program('qpaste --delete ' + sitems)

    def extract_items(self, variant):
        # FIXME: implement please wait???
        for sfile in variant:
            if misc.archive_supported(sfile):
                sfile_dirname = os.path.dirname(sfile)
                print('Extracting: ', sfile, 'To: ', sfile_dirname)
                misc.archive_decompress(sfile, sfile_dirname)

    def gzip_items(self, variant, soutput=None):
        # FIXME: implement please wait???
        if not soutput:
            for svar in variant:
                soutput = svar + '.tar.gz'
                # ensure that directory is passed to archive_compress() as chdir argument
                if not os.path.isdir(svar):
                    svar = os.path.dirname(svar)
        print('Compressing: ', variant, 'To: ', soutput)
        misc.archive_compress(variant, soutput, 'gz', svar)

    def bzip2_items(self, variant, soutput=None):
        # FIXME: implement please wait???
        if not soutput:
            for svar in variant:
                soutput = svar + '.tar.bz2'
                # ensure that directory is passed to archive_compress() as chir argument
                if not os.path.isdir(svar):
                    svar = os.path.dirname(svar)
        print('Compressing: ', variant, 'To: ', soutput)
        misc.archive_compress(variant, soutput, 'bz2', svar)

    def new_file(self):
        svar, ok = QtGui.QInputDialog.getText(self.window, "New file", \
            "Name:", QtGui.QLineEdit.Normal)
        svar = os.path.realpath(str(svar))
        if ok and svar:
            if os.path.exists(svar):
                svar = self.check_exists(svar)
                if not svar:
                    return
            svar = str(svar)
            print('New file: ', svar)
            misc.file_write(os.path.realpath(svar), '')
            return svar

    def new_directory(self):
        svar, ok = QtGui.QInputDialog.getText(self.window, "New directory", \
            "Name:", QtGui.QLineEdit.Normal)
        svar = os.path.realpath(str(svar))
        if ok and svar:
            if os.path.isdir(svar):
                svar = self.check_exists(svar)
                if not svar:
                    return
            svar = str(svar)
            print('New directory: ', svar)
            misc.dir_create(svar)
            return svar

    def properties_items(self, variant):
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
        return str(self.settings.value(smime, ''))

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

    def register(self, smime, sprogram, sicon=''):
        ''' Register MIME with program and icon '''
        self.settings.setValue(smime, sprogram)
        self.settings.sync()

    def unregister(self, smime):
        ''' Unregister MIME '''
        self.settings.remove(smime)
        self.settings.sync()
