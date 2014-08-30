#!/bin/python2

from PyQt4 import QtCore, QtGui, QtWebKit
import sys, os, libworkspace, libmisc
general = libworkspace.General()
misc = libmisc.Misc()


class Widget(QtGui.QWidget):
    ''' Tab constructor '''
    def __init__(self, parent, spage=None):
        ''' Tab initialiser '''
        super(Widget, self).__init__()
        self.parent = parent
        self.spage = spage
        self.name = 'help'
        self.icon_find = general.get_icon('edit-find')

        self.help_path = os.path.join(sys.prefix, 'share/help')
        # for testing purpose only!
        # self.help_path = os.path.realpath('../../help/output')
        self.mainLayout = QtGui.QGridLayout()
        self.secondLayout = QtGui.QHBoxLayout()
        self.findButton = QtGui.QPushButton(self.icon_find, '')
        self.findButton.setToolTip(self.tr('Find text in currently loaded page'))
        self.findButton.clicked.connect(self.action_find)
        self.findButton.setShortcut(QtGui.QKeySequence(self.tr('CTRL+F')))
        self.helpBox = QtGui.QComboBox()
        for spath in sorted(misc.list_files(self.help_path)):
            if spath.endswith('.html'):
                self.helpBox.addItem(os.path.basename(spath))
        self.helpBox.setToolTip(self.tr('Set page to be displayed'))
        self.helpBox.currentIndexChanged.connect(self.help_change)
        self.webView = QtWebKit.QWebView()
        self.webView.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)
        self.webView.linkClicked.connect(self.link_clicked)
        self.secondLayout.addWidget(self.findButton)
        self.secondLayout.addWidget(self.helpBox)
        self.mainLayout.addLayout(self.secondLayout, 0, 0)
        self.mainLayout.addWidget(self.webView)
        self.setLayout(self.mainLayout)

        if self.spage:
            self.help_open(self.spage)
        else:
            self.help_open(self.helpBox.currentText())

    def help_open(self, spage):
        ''' Open local URL '''
        for spath in misc.list_files(self.help_path):
            if spath.endswith('/' + spage):
                index = self.helpBox.findText(spage)
                self.helpBox.setCurrentIndex(index)
                return self.webView.setUrl(QtCore.QUrl.fromLocalFile(spath))
        QtGui.QMessageBox.critical(self, self.tr('Critical'), \
            self.tr('Help page not found: %s' % spage))

    def help_change(self):
        ''' Change currently displayed help page '''
        self.help_open(self.helpBox.currentText())

    def link_clicked(self, url):
        ''' Update the URL if a link on a web page is clicked '''
        surl = url.toString()
        if surl.startswith('mailto:'):
            return self.parent.plugins.plugin_open_with('mail', \
                surl.replace('mailto:', ''))
        elif surl.startswith('file:///'):
            return self.help_open(surl.replace('file:///', ''))

        self.webView.setUrl(url)

    def action_find(self):
        ''' Find text in current page '''
        svar, ok = QtGui.QInputDialog.getText(self, self.tr('Find'), '')
        if ok and svar:
            self.webView.findText(svar, \
                self.webView.page().HighlightAllOccurrences)


class Plugin(QtCore.QObject):
    ''' Plugin handler '''
    def __init__(self, parent):
        super(Plugin, self).__init__()
        self.parent = parent
        self.name = 'help'
        self.version = "0.9.35 (9efc4b1)"
        self.description = self.tr('Help reader plugin')
        self.icon = general.get_icon('help-contents')
        self.widget = None

        self.helpButton = QtGui.QPushButton(self.icon, '')
        self.helpButton.setToolTip(self.description)
        self.helpButton.clicked.connect(self.open)
        self.applicationsLayout = self.parent.toolBox.widget(1).layout()
        self.applicationsLayout.addWidget(self.helpButton)

    def open(self, spath):
        ''' Open path in new tab '''
        index = self.parent.tabWidget.currentIndex()+1
        self.widget = Widget(self.parent, spath)
        self.parent.tabWidget.insertTab(index, self.widget, self.icon, self.tr('Help'))
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
        self.applicationsLayout.removeWidget(self.helpButton)
        self.close()

