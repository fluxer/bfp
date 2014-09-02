#!/bin/pyhton2

from PyQt4 import QtCore, QtGui
import libworkspace, libmisc
general = libworkspace.General()
misc = libmisc.Misc()

class Widget(QtGui.QWidget):
    ''' Tab widget '''
    def __init__(self, parent, spath=None):
        super(Widget, self).__init__()
        self.parent = parent
        self.spath = spath
        self.name = 'terminal'

        self.mainLayout = QtGui.QGridLayout()
        self.container = QtGui.QX11EmbedWidget(self)
        self.mainLayout.addWidget(self.container)
        self.setLayout(self.mainLayout)

        self.process = QtCore.QProcess(self.container)
        args = ['-into', str(self.container.winId()), \
            '-geometry', str(self.width()) + 'x' + str(self.height())]
        if spath:
            args.extend(('-e', spath))
        self.process.start(misc.whereis('xterm'), args)
        self.process.waitForStarted()


class Plugin(QtCore.QObject):
    ''' Plugin handler '''
    def __init__(self, parent=None):
        super(Plugin, self).__init__()
        self.parent = parent
        self.name = 'terminal'
        self.version = "0.9.36 (1c351eb)"
        self.description = self.tr('Embed terminal plugin')
        self.icon = general.get_icon('utilities-terminal')
        self.widget = None

        self.embedButton = QtGui.QPushButton(self.icon, '')
        self.embedButton.setToolTip(self.description)
        self.embedButton.clicked.connect(self.open)
        self.applicationsLayout = self.parent.toolBox.widget(1).layout()
        self.applicationsLayout.addWidget(self.embedButton)

    def open(self, spath):
        ''' Open path in new tab '''
        index = self.parent.tabWidget.currentIndex()+1
        self.widget = Widget(self.parent, spath)
        self.parent.tabWidget.insertTab(index, self.widget, self.icon, self.tr('Terminal'))
        self.parent.tabWidget.setCurrentIndex(index)
        self.widget.process.finished.connect(self.close)

    def close(self, index=None):
        ''' Close tab '''
        if not index:
            index = self.parent.tabWidget.currentIndex()
        if self.widget:
            # self.widget.container.discardClient()
            self.widget.process.terminate()
            self.widget.process.close()
            # self.widget.deleteLater()
            self.widget = None
            self.parent.tabWidget.removeTab(index)

    def unload(self):
        ''' Unload plugin '''
        self.applicationsLayout.removeWidget(self.embedButton)
        self.close()
