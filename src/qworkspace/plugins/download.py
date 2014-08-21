#!/bin/pyhton2

from PyQt4 import QtCore, QtGui, QtNetwork
import os, libworkspace, libmisc
general = libworkspace.General()
misc = libmisc.Misc()

class Widget(QtGui.QWidget):
    ''' Tab widget '''
    def __init__(self, parent, spath=None):
        super(Widget, self).__init__()
        self.parent = parent
        self.spath = spath
        self.name = 'download'

        self.addButton = QtGui.QPushButton(general.get_icon('list-add'), '')
        self.addButton.clicked.connect(self.download_add)
        self.removeButton = QtGui.QPushButton(general.get_icon('list-remove'), '')
        self.startButton = QtGui.QPushButton(general.get_icon('media-playback-start'), '')
        self.stopButton = QtGui.QPushButton(general.get_icon('process-stop'), '')
        self.secondLayout = QtGui.QHBoxLayout()
        self.secondLayout.addWidget(self.addButton)
        self.secondLayout.addWidget(self.removeButton)
        self.secondLayout.addWidget(self.startButton)
        self.secondLayout.addWidget(self.stopButton)
        self.mainLayout = QtGui.QGridLayout()
        self.downloadView = QtGui.QTableWidget()
        self.downloadView.setColumnCount(3)
        self.downloadView.setHorizontalHeaderLabels(('#', 'URL', 'Complete'))
        self.mainLayout.addLayout(self.secondLayout, 0, 0)
        self.mainLayout.addWidget(self.downloadView)
        self.setLayout(self.mainLayout)

        self.nam = QtNetwork.QNetworkAccessManager()
        self.download_path = QtCore.QDir.homePath()

        print self.spath
        if self.spath:
            self.download(spath)

    def download_add(self):
        surl, ok = QtGui.QInputDialog.getText(self, \
            self.tr('URL'), self.tr('URL:'), QtGui.QLineEdit.Normal)
        if surl:
            self.download(surl)

    def download_remove(self):
        pass

    def download(self, surl):
        request = QtNetwork.QNetworkRequest(QtCore.QUrl(surl))
        reply = self.nam.get(request)
        reply.readyRead.connect(lambda reply=reply: self.download_start(reply))
        reply.finished.connect(lambda reply=reply: self.download_finished(reply))

    def download_start(self, reply):
        surl = str(reply.url().toString())
        sfile = self.download_path + '/' + os.path.basename(surl)
        misc.file_write(sfile, reply.readAll(), 'a')

    def download_finished(self, reply):
        surl = reply.url().toString()
        if reply.error():
            QtGui.QMessageBox.critical(self, self.tr('Critical'), \
                self.tr('Download of <b>%s</b> failed.') % surl)
        else:
            QtGui.QMessageBox.information(self, self.tr('Info'), \
                self.tr('Download of <b>%s</b> complete.') % surl)


class Plugin(QtCore.QObject):
    ''' Plugin handler '''
    def __init__(self, parent):
        super(Plugin, self).__init__()
        self.parent = parent
        self.name = 'download'
        self.version = '0.0.1'
        self.description = self.tr('Download manager plugin')
        self.icon = general.get_icon('document-save-as')
        self.widget = None

        self.downloadButton = QtGui.QPushButton(self.icon, '')
        self.downloadButton.clicked.connect(lambda: self.open(None))
        self.applicationsLayout = self.parent.toolBox.widget(1).layout()
        self.applicationsLayout.addWidget(self.downloadButton)

        self.parent.plugins.mime_register('application/x-bittorrent', self.name)

    def open(self, spath):
        ''' Open path in new tab '''
        index = self.parent.tabWidget.currentIndex()+1
        self.widget = Widget(self.parent, spath)
        self.parent.tabWidget.insertTab(index, self.widget, self.icon, self.tr('Download'))
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
        self.applicationsLayout.removeWidget(self.downloadButton)
        self.close()
