#!/bin/python2

import os
import xdg.Menu, xdg.DesktopEntry, xdg.IconTheme
from PyQt4 import QtCore, QtGui

import libmisc, libsystem
misc = libmisc.Misc()
system = libsystem.System()


class General(object):
    ''' Common methods '''
    def set_style(self):
        ''' Style and icon application setup '''
        # FIXME: set stylesheet and icon theme
        pass

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
                QtGui.QMessageBox.critical(window, 'Error', str(detail))

    def system_shutdown(self, window):
        ''' Ask if system should shutdown '''
        reply = QtGui.QMessageBox.question(window, 'Shutdown', \
            'Are you sure you want to shutdown the system?', \
            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            try:
                system.do_shutdown()
            except Exception as detail:
                QtGui.QMessageBox.critical(window, 'Error', str(detail))

    def system_reboot(self, window):
        ''' Ask if system should rebooted '''
        reply = QtGui.QMessageBox.question(window, 'Reboot', \
            'Are you sure you want to reboot the system?', \
            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            try:
                system.do_reboot()
            except Exception as detail:
                QtGui.QMessageBox.critical(window, 'Error', str(detail))

general = General()


class Config(object):
    ''' Configuration handler '''
    def __init__(self):
        self.settings = QtCore.QSettings('qdesktop')
        self.read()

    def read(self):
        ''' Read config file '''
        self.GENERAL_STYLESHEET = str(self.settings.value('general/stylesheet', 'qdarkstyle').toString())
        self.GENERAL_ICONTHEME = str(self.settings.value('general/icontheme', '').toString())
        self.GENERAL_MENU = str(self.settings.value('general/menu', '/etc/xdg/menus/applications.menu').toString())
        self.WALLPAPER_IMAGE = str(self.settings.value('wallpaper/image', '').toString())
        self.WALLPAPER_STYLE = str(self.settings.value('wallpaper/style', 'stretch').toString())
        self.WALLPAPER_COLOR = str(self.settings.value('wallpaper/color', '#b4b4b4').toString())
        self.DEFAULT_TERMINAL = str(self.settings.value('default/terminal', 'xterm').toString())
        self.DEFAULT_FILEMANAGER = str(self.settings.value('default/filemanager', 'qfile').toString())
        self.DEFAULT_WEBBROWSER = str(self.settings.value('default/webbrowser', 'qupzilla').toString())

        self.SUSPEND_DISK = str(self.settings.value('suspend/disk', 'suspend').toString())
        self.SUSPEND_STATE = str(self.settings.value('suspend/state', 'mem').toString())
        self.CPU_POWER = str(self.settings.value('cpu/power', 'performance').toString())
        self.CPU_BATTERY = str(self.settings.value('cpu/battery', 'ondemand').toString())
        self.BACKLIGHT_POWER = str(self.settings.value('backlight/power', '15').toString())
        self.BACKLIGHT_BATTERY = str(self.settings.value('backlight/battery', '10').toString())
        self.LID_POWER = str(self.settings.value('lid/power', 'suspend').toString())
        self.LID_BATTERY = str(self.settings.value('lid/battery', 'shutdown').toString())
        self.LOW_BATTERY = str(self.settings.value('battery/low', 'suspend').toString())

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
        pbar = QtGui.QProgressDialog(self.window)
        pbar.setMaximum(0)
        # pbar.canceled.connect(return)
        for sfile in variant:
            if misc.archive_supported(sfile):
                sfile_dirname = os.path.dirname(sfile)
                pbar.show()
                pbar.setLabelText('Extracting: <b>' + sfile + '</b> To: <b>' + sfile_dirname + '</b>')
                misc.archive_decompress(sfile, sfile_dirname)
                pbar.hide()

    def gzip_items(self, variant, soutput=None):
        ''' Gzip files/directories into archive '''
        pbar = QtGui.QProgressDialog(self.window)
        pbar.setMaximum(0)
        if not soutput:
            for svar in variant:
                soutput = svar + '.tar.gz'
                # ensure that directory is passed to archive_compress() as chdir argument
                if not os.path.isdir(svar):
                    svar = os.path.dirname(svar)
        pbar.show()
        pbar.setLabelText('Compressing: <b>' + misc.string_convert(variant) + '</b> To: <b>' + soutput + '</b>')
        misc.archive_compress(variant, soutput, 'gz', svar)
        pbar.hide()

    def bzip2_items(self, variant, soutput=None):
        ''' BZip2 files/directories into archive '''
        pbar = QtGui.QProgressDialog(self.window)
        pbar.setMaximum(0)
        if not soutput:
            for svar in variant:
                soutput = svar + '.tar.bz2'
                # ensure that directory is passed to archive_compress() as chir argument
                if not os.path.isdir(svar):
                    svar = os.path.dirname(svar)
        pbar.show()
        pbar.setLabelText('Compressing: <b>' + misc.string_convert(variant) + '</b> To: <b>' + soutput + '</b>')
        misc.archive_compress(variant, soutput, 'bz2', svar)
        pbar.hide()

    def new_file(self):
        ''' Create a new file '''
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
        ''' Create a new directory '''
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
