#!/bin/pyhton2

from PyQt4 import QtCore, QtGui
import pyalsa.alsamixer as alsamixer
import libworkspace
general = libworkspace.General()

class Widget(QtGui.QWidget):
    ''' Tab widget '''
    def __init__(self, parent, spath=None):
        super(Widget, self).__init__()
        self.parent = parent
        self.spath = spath
        self.name = 'mixer'

        self.mixer = alsamixer.Mixer()
        self.mixer.attach()
        self.mixer.load()
        self.element = alsamixer.Element(self.mixer, 'Master')

        self.mainLayout = QtGui.QGridLayout()
        self.volumeSlider = QtGui.QSlider()
        self.volumeSlider.valueChanged.connect(self.change_volume)
        self.volumeSlider.setMaximum(self.element.get_volume_range()[1])
        self.volumeSlider.setValue(self.element.get_volume())
        self.mainLayout.addWidget(self.volumeSlider)
        self.setLayout(self.mainLayout)

        if self.spath:
            self.set_volume(self.spath)

    def set_volume(self, ivalue):
        ''' Actually set the volume '''
        # self.element.set_volume_array([value, value])
        # self.element.set_volume_tuple([value, value])
        self.element.set_volume_all(ivalue)

    def change_volume(self):
        ''' Change volume upon slider event '''
        ivalue = self.volumeSlider.value()
        self.set_volume(ivalue)


class Plugin(QtCore.QObject):
    ''' Plugin handler '''
    def __init__(self, parent):
        super(Plugin, self).__init__()
        self.parent = parent
        self.name = 'mixer'
        self.version = "0.9.31 (37a0285)"
        self.description = self.tr('Sound mixer manager plugin')
        self.icon = general.get_icon('audio-volume-high')
        self.widget = None

        self.mixerButton = QtGui.QPushButton(self.icon, '')
        self.mixerButton.clicked.connect(lambda: self.open(None))
        self.applicationsLayout = self.parent.toolBox.widget(1).layout()
        self.applicationsLayout.addWidget(self.mixerButton)

    def open(self, spath):
        ''' Open path in new tab '''
        index = self.parent.tabWidget.currentIndex()+1
        self.widget = Widget(self.parent, spath)
        self.parent.tabWidget.insertTab(index, self.widget, self.icon, self.tr('Mixer'))
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
        self.applicationsLayout.removeWidget(self.mixerButton)
        self.close()
