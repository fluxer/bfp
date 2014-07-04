#!/bin/python2

import qbrowse_ui
from PyQt4 import QtCore, QtGui, QtWebKit
import sys, os, libmisc, libdesktop

# prepare for lift-off
app_version = "0.9.7 (9a4aba9)"
app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()
ui = qbrowse_ui.Ui_MainWindow()
ui.setupUi(MainWindow)
actions = libdesktop.Actions(MainWindow, app)
config = libdesktop.Config()
general = libdesktop.General()
misc = libmisc.Misc()
icon = QtGui.QIcon()

def setLook():
    general.set_style(app)
    icon.setThemeName(config.GENERAL_ICONTHEME)
setLook()

def run_about():
    QtGui.QMessageBox.about(MainWindow, 'About', \
        '<b>QBrowse v' + app_version + '</b> by SmiL3y - xakepa10@gmail.com - under GPLv2')

class NewTab(QtGui.QWidget):
    ''' Tab constructor '''
    def __init__(self, url='http://google.com', parent=None):
        ''' Tab initialiser '''
        super(NewTab, self).__init__(parent)
        # set variables
        self.url = url
        self.bookmarks = ('google.com', 'bitbucket.org', 'youtube.com')
        self.icon_back = general.get_icon('back')
        self.icon_next = general.get_icon('forward')
        self.icon_reload = general.get_icon('reload')
        self.icon_stop = general.get_icon('exit')
        self.icon_new = general.get_icon('add')

        # add widgets
        mainLayout = QtGui.QVBoxLayout()
        secondLayout = QtGui.QHBoxLayout()
        self.backButton = QtGui.QPushButton()
        self.nextButton = QtGui.QPushButton()
        self.reloadStopButton = QtGui.QPushButton()
        self.newButton = QtGui.QPushButton()
        self.urlBox = QtGui.QComboBox()
        self.webView = QtWebKit.QWebView()
        self.progressBar = QtGui.QProgressBar()
        secondLayout.addWidget(self.backButton)
        secondLayout.addWidget(self.nextButton)
        secondLayout.addWidget(self.reloadStopButton)
        secondLayout.addWidget(self.newButton)
        secondLayout.addWidget(self.urlBox)
        mainLayout.addLayout(secondLayout)
        mainLayout.addWidget(self.webView)
        mainLayout.addWidget(self.progressBar)
        mainLayout.addStretch(1)
        self.setLayout(mainLayout)

        # setup widgets
        self.urlBox.setEditable(True)
        self.urlBox.setEditText(self.url)
        policy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        self.urlBox.setSizePolicy(policy)
        self.urlBox.setInsertPolicy(1)
        self.backButton.setEnabled(False)
        self.backButton.setIcon(self.icon_back)
        self.nextButton.setEnabled(False)
        self.nextButton.setIcon(self.icon_next)
        self.newButton.setIcon(self.icon_new)
        self.webView.settings().setAttribute(QtWebKit.QWebSettings.PluginsEnabled, \
            ui.actionPlugins.isChecked())
        self.webView.settings().setAttribute(QtWebKit.QWebSettings.JavascriptEnabled, \
            ui.actionJavascript.isChecked())

        # connect widgets
        self.backButton.clicked.connect(self.back)
        self.nextButton.clicked.connect(self.next)
        self.urlBox.currentIndexChanged.connect(self.url_changed)
        self.reloadStopButton.clicked.connect(self.reload_stop_page)
        self.newButton.clicked.connect(self.new_tab)
        self.webView.linkClicked.connect(self.link_clicked)
        self.webView.urlChanged.connect(self.link_clicked)
        self.webView.loadProgress.connect(self.load_progress)
        self.webView.titleChanged.connect(self.title_changed)
        ui.actionFind.triggered.disconnect()
        ui.actionFind.triggered.connect(self.action_find)

        widget = ui.menuBookmarks
        widget.clear()
        for mark in (self.bookmarks):
            e = widget.addAction(general.get_icon('stock_bookmark'), mark)
            widget.connect(e, QtCore.SIGNAL('triggered()'), \
                lambda url=mark: self.action_bookmark(url))

        # load page
        self.webView.setUrl(QtCore.QUrl(self.url))

    # basic functionality methods
    def url_changed(self):
        ''' Url have been changed by user '''
        history = self.webView.page().history()
        if history.canGoBack():
            self.backButton.setEnabled(True)
        else:
            self.backButton.setEnabled(False)
        if history.canGoForward():
            self.nextButton.setEnabled(True)
        else:
            self.nextButton.setEnabled(False)

        self.url = str(self.urlBox.currentText())
        if not os.path.isfile(self.url) and not self.url.startswith('http://') \
            and not self.url.startswith('https://') and not self.url.startswith('ftp://') \
            and not self.url.startswith('ftps://'):
            self.url = 'http://' + self.url
        self.webView.setUrl(QtCore.QUrl(self.url))

    def title_changed(self, title):
        '''  Web page title changed - change the tab name '''
        MainWindow.setWindowTitle(title)
        ui.tabWidget.setTabText(ui.tabWidget.currentIndex(), title[:20])

    def reload_stop_page(self):
        ''' Reload/stop loading the web page '''
        if self.progressBar.isHidden():
            self.reloadStopButton.setIcon(self.icon_stop)
            self.webView.setUrl(QtCore.QUrl(self.url))
        else:
            self.reloadStopButton.setIcon(self.icon_reload)
            self.webView.stop()

    def link_clicked(self, url):
        ''' Update the URL if a link on a web page is clicked '''
        history = self.webView.page().history()
        if history.canGoBack():
            self.backButton.setEnabled(True)
        else:
            self.backButton.setEnabled(False)
        if history.canGoForward():
            self.nextButton.setEnabled(True)
        else:
            self.nextButton.setEnabled(False)

        self.urlBox.setEditText(url.toString())

    def load_progress(self, load):
        ''' Page load progress '''
        if load == 100:
            self.reloadStopButton.setIcon(self.icon_reload)
            self.progressBar.hide()
            self.progressBar.setValue(0)
            ui.tabWidget.setTabIcon(ui.tabWidget.currentIndex(), self.webView.icon())
        else:
            self.progressBar.show()
            self.progressBar.setValue(load)
            self.progressBar.setStatusTip(self.webView.statusTip())
            self.reloadStopButton.setIcon(self.icon_stop)

    def back(self):
        ''' Back button clicked, go one page back '''
        history = self.webView.page().history()
        history.back()
        if history.canGoBack():
            self.backButton.setEnabled(True)
        else:
            self.backButton.setEnabled(False)

    def next(self):
        ''' Next button clicked, go to next page '''
        history = self.webView.page().history()
        history.forward()
        if history.canGoForward():
            self.nextButton.setEnabled(True)
        else:
            self.nextButton.setEnabled(False)

    def new_tab(self):
        ''' Create a new tab '''
        index = ui.tabWidget.currentIndex()+1
        MainWindow.setWindowTitle('New tab')
        ui.tabWidget.insertTab(index, NewTab(), 'New tab')
        ui.tabWidget.setCurrentIndex(index)

    def action_find(self):
        svar, ok = QtGui.QInputDialog.getText(MainWindow, 'Find', '')
        if ok and svar:
            self.webView.findText(svar)

    def action_bookmark(self, url):
        self.urlBox.setEditText(url)
        self.url_changed()

def remove_tab():
    ''' Remove tab from UI '''
    ui.tabWidget.removeTab(ui.tabWidget.currentIndex())

ui.tabWidget.tabCloseRequested.connect(remove_tab)
ui.actionQuit.triggered.connect(sys.exit)
ui.actionAbout.triggered.connect(run_about)

# initialise
ui.tabWidget.removeTab(0)
NewTab().new_tab()

# watch configs for changes
def reload_browser():
    global config
    reload(libdesktop)
    config = libdesktop.Config()
    setLook()

watcher1 = QtCore.QFileSystemWatcher()
watcher1.addPath(config.settings.fileName())
watcher1.fileChanged.connect(reload_browser)

MainWindow.showMaximized()
sys.exit(app.exec_())
