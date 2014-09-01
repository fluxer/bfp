#!/bin/pyhton2

from PyQt4 import QtCore, QtGui, QtNetwork
import libworkspace, libmisc
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
        self.addButton.setToolTip(self.tr('Add URL to the download queue'))
        self.addButton.clicked.connect(self.download_add)
        self.abortButton = QtGui.QPushButton(general.get_icon('edit-delete'), '')
        self.abortButton.setToolTip(self.tr('Abort current download'))
        self.abortButton.clicked.connect(self.download_abort)
        self.abortButton.setEnabled(False)
        self.openButton = QtGui.QPushButton(general.get_icon('document-open'), '')
        self.openButton.setToolTip(self.tr('Open downloaded file'))
        self.openButton.clicked.connect(self.download_open)
        self.openButton.setEnabled(False)
        self.openBox = QtGui.QCheckBox(self.tr('Open file on finished'))
        self.closeBox = QtGui.QCheckBox(self.tr('Close plugin on finished'))
        self.secondLayout = QtGui.QHBoxLayout()
        self.secondLayout.addWidget(self.addButton)
        self.secondLayout.addWidget(self.abortButton)
        self.secondLayout.addWidget(self.openButton)
        self.secondLayout.addWidget(self.openBox)
        self.secondLayout.addWidget(self.closeBox)
        self.mainLayout = QtGui.QGridLayout()
        self.downloadLabel = QtGui.QLabel()
        self.progressBar = QtGui.QProgressBar()
        self.mainLayout.addLayout(self.secondLayout, 0, 0)
        self.mainLayout.addWidget(self.downloadLabel)
        self.mainLayout.addWidget(self.progressBar)
        self.setLayout(self.mainLayout)

        self.nam = QtNetwork.QNetworkAccessManager()
        self.download_path = QtCore.QDir.homePath()
        self.request = None
        self.reply = None

        if self.spath:
            self.download(spath)

    def download_add(self):
        ''' Start download '''
        surl, ok = QtGui.QInputDialog.getText(self, \
            self.tr('URL'), self.tr('URL:'), QtGui.QLineEdit.Normal)
        if surl:
            self.download(surl)

    def download_abort(self):
        ''' Download abort '''
        if self.reply:
            reply = QtGui.QMessageBox.question(self, self.tr('Question'), \
                self.tr('Download is in progress, do you want to abort it?'),
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            if not reply == QtGui.QMessageBox.Yes:
                return

        self.reply.abort()
        self.downloadLabel.setText('')
        self.progressBar.setValue(0)
        self.addButton.setEnabled(True)
        self.abortButton.setEnabled(False)
        self.openButton.setEnabled(False)

    def download_open(self):
        ''' Download opener '''
        self.parent.plugins.plugin_open(self.download_path + '/' + \
            misc.url_normalize(self.downloadLabel.text(), True))

    def download(self, surl):
        ''' Main download method '''
        # FIXME: check if file exists
        self.request = QtNetwork.QNetworkRequest(QtCore.QUrl(surl))
        self.reply = self.nam.get(self.request)
        self.reply.downloadProgress.connect(self.download_progress)
        self.reply.readyRead.connect(self.download_read)
        self.reply.finished.connect(self.download_finished)
        self.downloadLabel.setText(surl)
        self.progressBar.setValue(0)
        self.addButton.setEnabled(False)
        self.abortButton.setEnabled(True)
        self.openButton.setEnabled(False)

    def download_progress(self, ireceived, itotal):
        self.progressBar.setMaximum(itotal)
        self.progressBar.setValue(ireceived)

    def download_read(self):
        ''' Download data read slot '''
        surl = str(self.reply.url().toString())
        sfile = self.download_path + '/' + misc.url_normalize(surl, True)
        misc.file_write(sfile, self.reply.readAll(), 'a')

    def download_finished(self):
        ''' Download finished slot '''
        surl = self.reply.url().toString()
        if self.reply.error():
            self.parent.plugins.notify_critical(self.tr('Download of <b>%s</b> failed.') % surl)
        else:
            self.parent.plugins.notify_information(self.tr('Download of <b>%s</b> complete.') % surl)
            self.openButton.setEnabled(True)
            if self.openBox.isChecked():
                self.download_open()
        if self.closeBox.isChecked():
            self.parent.plugins.plugin_close(self.name)
        self.addButton.setEnabled(True)
        self.abortButton.setEnabled(False)
        self.request = None
        self.reply = None


class Plugin(QtCore.QObject):
    ''' Plugin handler '''
    def __init__(self, parent):
        super(Plugin, self).__init__()
        self.parent = parent
        self.name = 'download'
        self.version = "0.9.36 (9197ba8)"
        self.description = self.tr('Download manager plugin')
        self.icon = general.get_icon('document-save-as')
        self.widget = None

        self.downloadButton = QtGui.QPushButton(self.icon, '')
        self.downloadButton.setToolTip(self.description)
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
