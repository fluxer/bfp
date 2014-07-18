#!/bin/python2

from PyQt4 import QtGui
import sys, time, libmisc, libworkspace
app = QtGui.QApplication(sys.argv)
misc = libmisc.Misc()
general = libworkspace.General()


class Widget(QtGui.QWidget):
    ''' Tab widget '''
    def __init__(self, parent, spath=None):
        super(Widget, self).__init__()
        self.parent = parent
        self.spath = spath # FIXME: use for taking screenshot immidiatly
        self.name = 'screenshot'
        self.delayBox = QtGui.QSpinBox()
        self.takeButton = QtGui.QPushButton(general.get_icon('gnome-mime-image'), '')
        self.takeButton.clicked.connect(self.take_screenshot)
        self.mainLayout = QtGui.QGridLayout()
        self.mainLayout.addWidget(self.delayBox)
        self.mainLayout.addWidget(self.takeButton)
        self.setLayout(self.mainLayout)

    def get_filename(self):
        sfile = QtGui.QFileDialog.getSaveFileName(self, 'Save', \
            'screenshot.png', 'Image Files (*.png *.jpg *.jpeg *.svg);;All Files (*)')
        if sfile:
            return str(sfile)
        return None

    def get_extension(self, sfile):
        ext = sfile.split('.')[-1]
        if ext == sfile:
            return 'png'
        return ext

    def take_screenshot(self):
        delay = self.delayBox.value()
        # MainWindow.hide()

        if delay > 0:
            time.sleep(delay)

        sfile = self.get_filename()
        if sfile:
            extension = self.get_extension(sfile)
            if not sfile.endswith(extension):
                sfile = sfile + '.' + extension
            # to avoid the save dialog being captured
            time.sleep(1)
            p = QtGui.QPixmap.grabWindow(app.desktop().winId())
            p.save(sfile, extension)
            # sys.exit()


class Plugin(object):
    ''' Plugin handler '''
    def __init__(self, parent):
        self.parent = parent
        self.name = 'screenshot'
        self.version = '0.0.1'
        self.description = 'Screenshot taking plugin'
        self.icon = general.get_icon('desktop')
        self.widget = None

        self.screenshotButton = QtGui.QPushButton(self.icon, '')
        self.screenshotButton.clicked.connect(lambda: self.open(None))
        self.applicationsLayout = self.parent.toolBox.widget(1).layout()
        self.applicationsLayout.addWidget(self.screenshotButton)

    def open(self, spath=None):
        ''' Open path in new tab '''
        self.index = self.parent.tabWidget.currentIndex()+1
        self.widget = Widget(self.parent, spath)
        self.parent.tabWidget.insertTab(self.index, self.widget, self.icon, 'Screenshot')
        self.parent.tabWidget.setCurrentIndex(self.index)

    def close(self):
        ''' Close tab '''
        if self.widget:
            self.widget.destroy()
            self.parent.tabWidget.removeTab(self.index)

    def unload(self):
        ''' Unload plugin '''
        self.applicationsLayout.removeWidget(self.screenshotButton)
        self.close()

