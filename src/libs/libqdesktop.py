#!/usr/bin/python

import os, shutil
import xdg.Menu, xdg.DesktopEntry
from PyQt4 import QtCore, QtGui
import libmisc
misc = libmisc.Misc()

class General(object):
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

general = General()

class Config(object):
    def __init__(self):
        self.settings = QtCore.QSettings('qdesktop')
        self.read()

    def read(self):
        self.GENERAL_STYLESHEET = str(self.settings.value('general/stylesheet', '').toString())
        self.GENERAL_ICONTHEME = str(self.settings.value('general/icontheme', '').toString())
        self.GENERAL_MENU = str(self.settings.value('general/menu', '/etc/xdg/menus/applications.menu').toString())
        self.WALLPAPER_IMAGE = str(self.settings.value('wallpaper/image', '').toString())
        self.WALLPAPER_STYLE = str(self.settings.value('wallpaper/style', 'stretch').toString())
        self.WALLPAPER_COLOR = str(self.settings.value('wallpaper/color', '#b4b4b4').toString())
        self.DEFAULT_TERMINAL = str(self.settings.value('default/terminal', 'xterm').toString())
        self.DEFAULT_FILEMANAGER = str(self.settings.value('default/filemanager', 'qfile').toString())
        self.DEFAULT_WEBBROWSER = str(self.settings.value('default/webbrowser', 'qupzilla').toString())

    def write(self, variable, value):
        self.settings.setValue(variable, value)

config = Config()

class Menu(object):
    def __init__(self, app, widget):
        self.app = app
        self.widget = widget
        self.xdg = xdg.Menu
        self.menu = config.GENERAL_MENU

    def execute_desktop(self, sfile):
        ''' Execute program from .desktop file '''
        x = self.xdg.MenuEntry(sfile)
        tryExec = x.DesktopEntry.getTryExec()
        Exec = x.DesktopEntry.getExec()

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
                self.dynamic_menu(entry, depth, widget.addMenu(str(entry)))
            elif isinstance(entry, self.xdg.MenuEntry):
                icon = QtGui.QIcon.fromTheme(entry.DesktopEntry.getIcon())
                name = entry.DesktopEntry.getName()
                e = widget.addAction(icon, name)
                widget.connect(e, QtCore.SIGNAL('triggered()'),
                    lambda sfile=entry.DesktopEntry.getFileName(): self.execute_desktop(sfile))
            #elif isinstance(entry, self.xdg.Separator):
            #    self.widget.addSeparator()
            #elif isinstance(entry, self.xdg.Header):
            #    pass
        depth -= 1

    def build(self):
        if not os.path.isfile(self.menu):
            return
        self.widget.clear()
        return self.dynamic_menu(self.xdg.parse(self.menu))

class Actions(object):
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
        sfile_basename, ok = QtGui.QInputDialog.getText(self.window, "File/directory exists",
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
        # FIXME: implement properly
        for svar in variant:
            svar_basename = os.path.basename(svar)
            svar_dirname = os.path.dirname(svar)

            svar_new, ok = QtGui.QInputDialog.getText(self.window, "Move",
                "New name:", QtGui.QLineEdit.Normal, svar_basename)
            if ok and svar_new:
                pass
            else:
                return

            svar_new = str(svar_new)
            if os.path.exists(svar_dirname + '/' + svar_new):
                svar_new = self.check_exists(svar_dirname + '/' + svar_new)
                if not svar_new:
                    return
            new_name = os.path.join(svar_dirname, str(svar_new))
            print('Renaming: ', svar, ' To: ', new_name)
            os.rename(svar, new_name)

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

    def paste_items(self, window):
        # FIXME: implement cancel
        progress = QtGui.QProgressDialog(window)
        progress.setMinimum(0)
        progress.setMaximum(0)
        cur_dir = os.path.realpath(os.curdir)
        if self.cut:
            progress.show()
            for svar in self.cut:
                svar = str(svar)
                svar_basename = os.path.basename(svar)
                if os.path.exists(cur_dir + '/' + svar_basename):
                    svar_basename = self.check_exists(cur_dir + '/' + svar_basename)
                    if not svar_basename:
                        continue
                svar_copy = cur_dir + '/' + svar_basename
                progress.setLabelText('Moving: <b>' + svar + '</b> To: <b>' + svar_copy + '</b>')
                os.rename(svar, svar_copy)
        elif self.copy:
            progress.show()
            for svar in self.copy:
                svar = str(svar)
                svar_basename = os.path.basename(svar)
                if os.path.exists(cur_dir + '/' + svar_basename):
                    svar_basename = self.check_exists(cur_dir + '/' + svar_basename)
                    if not svar_basename:
                        continue
                svar_copy = cur_dir + '/' + svar_basename
                progress.setLabelText('Copying: <b>' + svar + '</b> To: <b>' + svar_copy + '</b>')
                if os.path.isdir(svar):
                    shutil.copytree(svar, svar_copy)
                else:
                    shutil.copy2(svar, svar_copy)
        progress.close()

    def delete_items(self, variant, ask=True):
        for svar in variant:
            if ask:
                reply = QtGui.QMessageBox.question(self.window, "Delete",
                    "Are you sure you want to delete <b>" + svar + "</b>? ", QtGui.QMessageBox.Yes | QtGui.QMessageBox.YesToAll | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel)
                if reply == QtGui.QMessageBox.Yes:
                    pass
                elif reply == QtGui.QMessageBox.No:
                    continue
                elif reply == QtGui.QMessageBox.YesToAll:
                    ask = False
                else:
                    return

            print('Removing: ', svar)
            if os.path.isdir(svar):
                misc.dir_remove(svar)
            else:
                os.unlink(svar)

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
                # ensure that directory is passed to archive_compress() as chir argument
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
        svar, ok = QtGui.QInputDialog.getText(self.window, "New file",
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

    def new_directory(self):
        svar, ok = QtGui.QInputDialog.getText(self.window, "New directory",
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

    def properties_items(self, variant):
        for svar in variant:
            general.execute_program('qproperties ' + svar)
