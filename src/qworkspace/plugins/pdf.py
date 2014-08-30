#!/bin/python2

from PyQt4 import QtCore, QtGui
import os, popplerqt4, libmisc, libworkspace
general = libworkspace.General()
misc = libmisc.Misc()


class Widget(QtGui.QWidget):
    ''' Tab widget '''
    def __init__(self, parent, spath=None):
        super(Widget, self).__init__()
        self.parent = parent
        self.spath = spath
        self.name = 'pdf'

        self.printer = QtGui.QPrinter()
        self.imageView = QtGui.QLabel()
        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.imageView)
        self.openButton = QtGui.QPushButton(general.get_icon('document-open'), '')
        self.openButton.setToolTip(self.tr('Open file'))
        self.openButton.clicked.connect(self.open_file)
        self.reloadButton = QtGui.QPushButton(general.get_icon('view-refresh'), '')
        self.reloadButton.setToolTip(self.tr('Reload currently loaded file'))
        self.reloadButton.clicked.connect(self.reload_file)
        self.reloadButton.setEnabled(False)
        self.printButton = QtGui.QPushButton(general.get_icon('document-print'), '')
        self.printButton.setToolTip(self.tr('Print text'))
        self.printButton.clicked.connect(self.print_image)
        self.printButton.setShortcut(QtGui.QKeySequence(self.tr('CTRL+P')))
        self.printButton.setEnabled(False)
        self.secondLayout = QtGui.QHBoxLayout()
        self.secondLayout.addWidget(self.openButton)
        self.secondLayout.addWidget(self.reloadButton)
        self.secondLayout.addWidget(self.printButton)
        self.mainLayout = QtGui.QGridLayout()
        self.mainLayout.addLayout(self.secondLayout, 0, 0)
        self.mainLayout.addWidget(self.scrollArea)
        self.setLayout(self.mainLayout)

        if self.spath:
            self.open_file(spath)

    def set_image(self, sfile):
        ''' Set image view '''
        doc = popplerqt4.Poppler.Document.load(sfile)
        doc.setRenderHint(popplerqt4.Poppler.Document.Antialiasing)
        doc.setRenderHint(popplerqt4.Poppler.Document.TextAntialiasing)

        page = doc.page(0)
        image = page.renderToImage()

        self.imageView.setPixmap(QtGui.QPixmap.fromImage(image))
        self.imageView.fileName = sfile

    def open_file(self, sfile):
        ''' Open image file '''
        if not sfile or not os.path.isfile(sfile):
            sfile = QtGui.QFileDialog.getOpenFileName(self, self.tr('Open'), \
                QtCore.QDir.currentPath(), \
                self.tr('PDF (*.pdf);;All (*)'))
            if not sfile:
                return
        self.set_image(str(sfile))
        self.reloadButton.setEnabled(True)
        self.printButton.setEnabled(True)
        self.parent.plugins.recent_register(str(sfile))

    def reload_file(self):
        ''' Reload currently displayed image '''
        self.set_image(self.imageView.fileName)

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
        self.name = 'pdf'
        self.version = "0.9.35 (9efc4b1)"
        self.description = self.tr('PDF viewer plugin')
        self.icon = general.get_icon('application-pdf')
        self.widget = None

        self.imageButton = QtGui.QPushButton(self.icon, '')
        self.imageButton.setToolTip(self.description)
        self.imageButton.clicked.connect(lambda: self.open(None))
        self.applicationsLayout = self.parent.toolBox.widget(1).layout()
        self.applicationsLayout.addWidget(self.imageButton)

        self.parent.plugins.mime_register('application/x-pdf', self.name)
        self.parent.plugins.mime_register('application/pdf', self.name)

    def open(self, spath):
        ''' Open path in new tab '''
        index = self.parent.tabWidget.currentIndex()+1
        self.widget = Widget(self.parent, spath)
        self.parent.tabWidget.insertTab(index, self.widget, self.icon, self.tr('PDF'))
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

