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
        self.spath = spath
        self.name = 'image'

        self.printer = QtGui.QPrinter()
        self.imageView = QtGui.QLabel()
        self.imageView.setText('')
        self.imageView.setScaledContents(True)
        self.openButton = QtGui.QPushButton(general.get_icon('document-open'), '')
        self.openButton.setToolTip(self.tr('Open file'))
        self.openButton.clicked.connect(self.open_file)
        self.nextButton = QtGui.QPushButton(general.get_icon('go-next'), '')
        self.nextButton.setToolTip(self.tr('Next file'))
        self.nextButton.clicked.connect(self.next_image)
        self.nextButton.setEnabled(False)
        self.previousButton = QtGui.QPushButton(general.get_icon('go-previous'), '')
        self.previousButton.setToolTip(self.tr('Previous file'))
        self.previousButton.clicked.connect(self.previous_image)
        self.previousButton.setEnabled(False)
        self.reloadButton = QtGui.QPushButton(general.get_icon('view-refresh'), '')
        self.reloadButton.setToolTip(self.tr('Reload currently loaded file'))
        self.reloadButton.clicked.connect(self.reload_file)
        self.reloadButton.setEnabled(False)
        self.printButton = QtGui.QPushButton(general.get_icon('document-print'), '')
        self.printButton.setToolTip(self.tr('Print image'))
        self.printButton.clicked.connect(self.print_image)
        self.printButton.setShortcut(QtGui.QKeySequence(self.tr('CTRL+P')))
        self.printButton.setEnabled(False)
        self.secondLayout = QtGui.QHBoxLayout()
        self.secondLayout.addWidget(self.openButton)
        self.secondLayout.addWidget(self.previousButton)
        self.secondLayout.addWidget(self.nextButton)
        self.secondLayout.addWidget(self.reloadButton)
        self.secondLayout.addWidget(self.printButton)
        self.mainLayout = QtGui.QGridLayout()
        self.mainLayout.addLayout(self.secondLayout, 0, 0)
        self.mainLayout.addWidget(self.imageView)
        self.setLayout(self.mainLayout)

        if self.spath:
            self.open_file(spath)

    def set_image(self, sfile):
        ''' Set image view and setup previous/next buttons '''
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
        ''' Open image file '''
        if not sfile or not os.path.isfile(sfile):
            sfile = QtGui.QFileDialog.getOpenFileName(self, self.tr('Open'), \
                QtCore.QDir.currentPath(), \
                self.tr('Image (*.png *.jpg *.jpeg *.svg);;All (*)'))
            if not sfile:
                return
        self.set_image(str(sfile))
        self.reloadButton.setEnabled(True)
        self.printButton.setEnabled(True)
        self.parent.plugins.recent_register(str(sfile))

    def reload_file(self):
        ''' Reload currently displayed image '''
        self.set_image(self.imageView.fileName)

    def images_list(self):
        ''' Get list of images in directory '''
        slist = []
        scurrent = self.imageView.fileName
        sdir = os.path.dirname(scurrent)
        if not os.path.isdir(sdir):
            self.previousButton.setEnabled(False)
            self.nextButton.setEnabled(False)
            return slist

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
        ''' Display previous image from the list '''
        slist = self.images_list()
        if self.imageView.fileName in slist:
            self.set_image(slist[slist.index(self.imageView.fileName) - 1])

    def next_image(self):
        ''' Display Next image from the list '''
        slist = self.images_list()
        if self.imageView.fileName in slist:
            self.set_image(slist[slist.index(self.imageView.fileName) + 1])

    def print_image(self):
        dialog = QtGui.QPrintDialog(self.printer, self)
        if dialog.exec_():
            painter = QtGui.QPainter(self.printer)
            rect = painter.viewport()
            size = self.imageView.pixmap().size()
            size.scale(rect.size(), QtCore.Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(self.imageView.pixmap().rect())
            painter.drawPixmap(0, 0, self.imageView.pixmap())


class Plugin(QtCore.QObject):
    ''' Plugin handler '''
    def __init__(self, parent):
        super(Plugin, self).__init__()
        self.parent = parent
        self.name = 'image'
        self.version = "0.9.35 (44cf21d)"
        self.description = self.tr('Image viewer plugin')
        self.icon = general.get_icon('image-x-generic')
        self.widget = None

        self.imageButton = QtGui.QPushButton(self.icon, '')
        self.imageButton.setToolTip(self.description)
        self.imageButton.clicked.connect(lambda: self.open(None))
        self.applicationsLayout = self.parent.toolBox.widget(1).layout()
        self.applicationsLayout.addWidget(self.imageButton)

        self.parent.plugins.mime_register('image/x-ms-bmp', self.name)
        self.parent.plugins.mime_register('image/bmp', self.name)
        self.parent.plugins.mime_register('image/png', self.name)
        self.parent.plugins.mime_register('image/jpeg', self.name)
        self.parent.plugins.mime_register('image/svg+html', self.name)

    def open(self, spath):
        ''' Open path in new tab '''
        index = self.parent.tabWidget.currentIndex()+1
        self.widget = Widget(self.parent, spath)
        self.parent.tabWidget.insertTab(index, self.widget, self.icon, self.tr('Image'))
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
        self.applicationsLayout.removeWidget(self.imageButton)
        self.close()

