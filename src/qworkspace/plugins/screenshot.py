#!/bin/python2

from PyQt4 import QtCore, QtGui
import libmisc, libworkspace
misc = libmisc.Misc()
general = libworkspace.General()


class Widget(QtGui.QWidget):
    ''' Tab widget '''
    def __init__(self, parent, spath=None):
        super(Widget, self).__init__()
        self.parent = parent
        self.spath = spath
        self.name = 'screenshot'

        self.delayBox = QtGui.QSpinBox()
        self.delayBox.setToolTip(self.tr('Set time to wait before taking screenshot'))
        self.takeButton = QtGui.QPushButton(general.get_icon('image-x-generic'), '')
        self.takeButton.setToolTip(self.tr('Take screenshot'))
        self.takeButton.clicked.connect(self.take_screenshot)
        self.mainLayout = QtGui.QGridLayout()
        self.mainLayout.addWidget(self.delayBox)
        self.mainLayout.addWidget(self.takeButton)
        self.setLayout(self.mainLayout)

        if self.spath:
            self.take_screenshot()

    def get_extension(self, sfile):
        ''' Get extension of file, fallback to png '''
        ext = sfile.split('.')[-1]
        if ext == sfile:
            return 'png'
        return ext

    def take_screenshot(self):
        ''' Smart screenshot taking method respecting delay '''
        delay = self.delayBox.value()
        if delay > 0:
            QtCore.QTimer.singleShot(delay * 1000, self.capture_screen)
        else:
            self.capture_screen()

    def capture_screen(self):
        ''' Actual screen capture '''
        p = QtGui.QPixmap.grabWindow(self.parent.app.desktop().winId())
        if self.spath:
            sfile = self.spath
        else:
            sfile = QtGui.QFileDialog.getSaveFileName(self, self.tr('Save'), \
                'screenshot.png', \
                self.tr('Image (*.png *.jpg *.jpeg *.svg);;All (*)'))
        if sfile:
            sfile = str(sfile)
            extension = self.get_extension(sfile)
            if not sfile.endswith(extension):
                sfile = sfile + '.' + extension
            p.save(sfile, extension)


class Plugin(QtCore.QObject):
    ''' Plugin handler '''
    def __init__(self, parent):
        super(Plugin, self).__init__()
        self.parent = parent
        self.name = 'screenshot'
        self.version = "0.9.35 (e77e7e4)"
        self.description = self.tr('Screenshot taking plugin')
        self.icon = general.get_icon('application-x-desktop')
        self.widget = None

        self.screenshotButton = QtGui.QPushButton(self.icon, '')
        self.screenshotButton.setToolTip(self.description)
        self.screenshotButton.clicked.connect(lambda: self.open(None))
        self.applicationsLayout = self.parent.toolBox.widget(1).layout()
        self.applicationsLayout.addWidget(self.screenshotButton)

    def open(self, spath=None):
        ''' Open path in new tab '''
        index = self.parent.tabWidget.currentIndex()+1
        self.widget = Widget(self.parent, spath)
        self.parent.tabWidget.insertTab(index, self.widget, self.icon, self.tr('Screenshot'))
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
        self.applicationsLayout.removeWidget(self.screenshotButton)
        self.close()

