#!/bin/python2

from PyQt4 import QtCore, QtGui
import os, libmisc, libworkspace
general = libworkspace.General()
misc = libmisc.Misc()


class Widget(QtGui.QWidget):
    ''' Tab widget '''
    def __init__(self, parent, spath=None):
        super(Widget, self).__init__()
        self.parent = parent
        self.name = 'image'

        self.imageView = QtGui.QLabel()
        self.imageView.setText('')
        self.imageView.setScaledContents(True)
        self.nextButton = QtGui.QPushButton(general.get_icon('next'), '')
        self.nextButton.clicked.connect(self.next_image)
        self.nextButton.setEnabled(False)
        self.previousButton = QtGui.QPushButton(general.get_icon('previous'), '')
        self.previousButton.clicked.connect(self.previous_image)
        self.previousButton.setEnabled(False)
        self.reloadButton = QtGui.QPushButton(general.get_icon('reload'), '')
        self.reloadButton.clicked.connect(self.reload_file)
        self.reloadButton.setEnabled(False)
        self.openButton = QtGui.QPushButton(general.get_icon('openfile'), '')
        self.openButton.clicked.connect(self.open_file)
        self.secondLayout = QtGui.QHBoxLayout()
        self.secondLayout.addWidget(self.previousButton)
        self.secondLayout.addWidget(self.nextButton)
        self.secondLayout.addWidget(self.reloadButton)
        self.secondLayout.addWidget(self.openButton)
        self.mainLayout = QtGui.QGridLayout()
        self.mainLayout.addLayout(self.secondLayout, 0, 0)
        self.mainLayout.addWidget(self.imageView)
        self.setLayout(self.mainLayout)

        if spath:
            self.open_file(spath)

    def set_image(self, sfile):
        image = QtGui.QImage(sfile)
        self.imageView.setPixmap(QtGui.QPixmap.fromImage(image))
        self.imageView.fileName = sfile

        slist = self.images_list()
        for simage in slist:
            if simage == sfile:
                sindex = slist.index(sfile)
                if len(slist) == 1:
                    self.previousButton.setEnabled(False)
                    self.nextButton.setEnabled(False)
                elif sindex == 0:
                    self.previousButton.setEnabled(False)
                    self.nextButton.setEnabled(True)
                elif sindex+1 == len(slist):
                    self.previousButton.setEnabled(True)
                    self.nextButton.setEnabled(False)
                else:
                    self.previousButton.setEnabled(True)
                    self.nextButton.setEnabled(True)
                break

    def open_file(self, sfile):
        if not sfile or not os.path.isfile(sfile):
            sfile = QtGui.QFileDialog.getOpenFileName(None, 'Open', \
                QtCore.QDir.currentPath(), 'Image Files (*.png *.jpg *.jpeg *.svg);;All Files (*)')
            if not sfile:
                return
        self.set_image(str(sfile))
        self.reloadButton.setEnabled(True)

    def reload_file(self):
        self.set_image(self.imageView.fileName)

    def images_list(self):
        scurrent = self.imageView.fileName
        sdir = os.path.dirname(scurrent)
        if not os.path.isdir(sdir):
            self.previousButton.setEnabaled(False)
            self.nextButton.setEnabled(False)
            return

        slist = []
        for sfile in os.listdir(sdir):
            sfull = sdir + '/' + sfile
            if os.path.isfile(sfull):
                smime = misc.file_mime(sfull)
                if smime == 'image/png' or smime == 'image/jpeg' \
                    or smime == 'image/x-ms-bmp' or smime == 'image/bmp' \
                    or smime == 'image/svg+xml':
                    slist.append(sdir + '/' + sfile)
        return slist

    def previous_image(self):
        slist = self.images_list()
        if self.imageView.fileName in slist:
            self.set_image(slist[slist.index(self.imageView.fileName) - 1])

    def next_image(self):
        slist = self.images_list()
        if self.imageView.fileName in slist:
            self.set_image(slist[slist.index(self.imageView.fileName) + 1])


class Plugin(object):
    ''' Plugin handler '''
    def __init__(self, parent):
        self.parent = parent
        self.name = 'image'
        self.version = '0.0.1'
        self.description = 'Image viewer plugin'
        self.icon = general.get_icon('image-viewer')
        self.widget = None

        self.imageButton = QtGui.QPushButton(self.icon, '')
        self.imageButton.clicked.connect(lambda: self.open(None))
        self.applicationsLayout = self.parent.toolBox.widget(1).layout()
        self.applicationsLayout.addWidget(self.imageButton)

    def open(self, spath):
        ''' Open path in new tab '''
        self.index = self.parent.tabWidget.currentIndex()+1
        self.widget = Widget(self.parent, spath)
        self.parent.tabWidget.insertTab(self.index, self.widget, self.icon, 'Image')
        self.parent.tabWidget.setCurrentIndex(self.index)
        
    def close(self):
        ''' Close tab '''
        if self.widget:
            self.widget.destroy()
            self.parent.tabWidget.removeTab(self.index)

    def unload(self):
        ''' Unload plugin '''
        self.applicationsLayout.removeWidget(self.imageButton)
        self.close()






