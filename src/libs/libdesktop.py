#!/bin/python2

from PyQt4 import QtGui
import os, libmisc, libworkspace
misc = libmisc.Misc()
general = libworkspace.General()


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
        else:
            # FIXME: it will break on paths with spaces,
            #        is it OK to use \n in the clipboard content to solve this?
            for svar in self.clipboard.text().split(' '):
                sitems += '"' + str(svar) + '" '
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
