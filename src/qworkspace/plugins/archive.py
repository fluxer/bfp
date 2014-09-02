#!/bin/pyhton2

from PyQt4 import QtCore, QtGui
import os, tempfile, libworkspace, libmisc, libarchive
general = libworkspace.General()
misc = libmisc.Misc()
archive = libarchive.Libarchive()

class Widget(QtGui.QWidget):
    ''' Tab widget '''
    def __init__(self, parent, spath=None):
        super(Widget, self).__init__()
        self.parent = parent
        self.spath = spath
        self.name = 'archive'

        if os.path.exists(spath):
            self.archive_open(spath)

    def archive_open(self, spath):
        ''' Open and show archive content '''
        stmp = None
        try:
            if archive.supportedArchive(spath):
                stmp = tempfile.mkdtemp()
                archive.extractArchive(spath, stmp)
                self.parent.plugins.plugin_open(stmp) # FIXME: this is non-blocking
                archive.createArchive(stmp, spath)
            else:
                QtGui.QMessageBox.critical(self, self.tr('Critical'), \
                    self.tr('Unsupported format'))
        except Exception as detail:
            QtGui.QMessageBox.critical(self, self.tr('Critical'), str(detail))
        finally:
            if stmp and os.path.isdir(stmp):
                misc.dir_remove(stmp)


class Plugin(QtCore.QObject):
    ''' Plugin handler '''
    def __init__(self, parent):
        super(Plugin, self).__init__()
        self.parent = parent
        self.name = 'archive'
        self.version = "0.9.36 (1c351eb)"
        self.description = self.tr('Archive manager plugin')
        self.icon = general.get_icon('archive')
        self.widget = None

        self.parent.plugins.mime_register('application/x-gzip', self.name)
        self.parent.plugins.mime_register('application/gzip', self.name)
        self.parent.plugins.mime_register('application/x-bzip2', self.name)
        self.parent.plugins.mime_register('application/x-lzma', self.name)
        self.parent.plugins.mime_register('application/x-xz', self.name)
        self.parent.plugins.mime_register('application/x-tar', self.name)
        self.parent.plugins.mime_register('application/x-gtar', self.name)
        self.parent.plugins.mime_register('application/x-pax', self.name)
        self.parent.plugins.mime_register('application/x-cpio', self.name)
        self.parent.plugins.mime_register('application/zip', self.name)
        # FIXME: iso9660 mime (octet-stream)

    def open(self, spath):
        ''' Open path in new tab '''
        index = self.parent.tabWidget.currentIndex()+1
        self.widget = Widget(self.parent, spath)
        self.parent.tabWidget.insertTab(index, self.widget, self.icon, self.tr('Archive'))
        self.parent.tabWidget.setCurrentIndex(index)

    def close(self, index=None):
        ''' Close tab '''
        if not index:
            index = self.parent.tabWidget.currentIndex()
        if self.widget:
            self.widget.deleteLater()
            self.widget = None
            self.parent.tabWidget.removeTab(index)

    def unload(self):
        ''' Unload plugin '''
        self.close()
