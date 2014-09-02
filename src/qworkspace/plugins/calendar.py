#!/bin/pyhton2

from PyQt4 import QtCore, QtGui
import libworkspace
general = libworkspace.General()

class Widget(QtGui.QWidget):
    ''' Tab widget '''
    def __init__(self, parent, spath=None):
        super(Widget, self).__init__()
        self.parent = parent
        self.spath = spath
        self.name = 'calendar'

        self.firstDay = QtGui.QComboBox()
        self.firstDay.addItem(self.tr('Sunday'), QtCore.Qt.Sunday)
        self.firstDay.addItem(self.tr('Monday'), QtCore.Qt.Monday)
        self.firstDay.addItem(self.tr('Tuesday'), QtCore.Qt.Tuesday)
        self.firstDay.addItem(self.tr('Wednesday'), QtCore.Qt.Wednesday)
        self.firstDay.addItem(self.tr('Thursday'), QtCore.Qt.Thursday)
        self.firstDay.addItem(self.tr('Friday'), QtCore.Qt.Friday)
        self.firstDay.addItem(self.tr('Saturday'), QtCore.Qt.Saturday)
        self.firstDay.currentIndexChanged.connect(self.change_first_day)
        self.firstDay.setToolTip(self.tr('Set first day of the week'))
        self.calendar = QtGui.QCalendarWidget()
        self.mainLayout = QtGui.QGridLayout()
        self.mainLayout.addWidget(self.firstDay)
        self.mainLayout.addWidget(self.calendar)
        self.setLayout(self.mainLayout)

    def change_first_day(self, index):
        self.calendar.setFirstDayOfWeek(self.firstDay.currentIndex())


class Plugin(QtCore.QObject):
    ''' Plugin handler '''
    def __init__(self, parent):
        super(Plugin, self).__init__()
        self.parent = parent
        self.name = 'calendar'
        self.version = "0.9.36 (1c351eb)"
        self.description = self.tr('Calendar plugin')
        self.icon = general.get_icon('office-calendar')
        self.widget = None

        self.calendarButton = QtGui.QPushButton(self.icon, '')
        self.calendarButton.setToolTip(self.description)
        self.calendarButton.clicked.connect(lambda: self.open(None))
        self.applicationsLayout = self.parent.toolBox.widget(1).layout()
        self.applicationsLayout.addWidget(self.calendarButton)

    def open(self, spath):
        ''' Open path in new tab '''
        index = self.parent.tabWidget.currentIndex()+1
        self.widget = Widget(self.parent, spath)
        self.parent.tabWidget.insertTab(index, self.widget, self.icon, self.tr('Calendar'))
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
        self.applicationsLayout.removeWidget(self.calendarButton)
        self.close()
