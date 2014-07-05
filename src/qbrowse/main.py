#!/bin/python2

import qbrowse_ui
from PyQt4 import QtCore, QtGui, QtWebKit, QtNetwork
import sys, os, gc, libdesktop, libmisc

# prepare for lift-off
app_version = "0.9.8 (77fbb86)"
app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()
ui = qbrowse_ui.Ui_MainWindow()
ui.setupUi(MainWindow)
config = libdesktop.Config()
general = libdesktop.General()
misc = libmisc.Misc()
icon = QtGui.QIcon()
home_page = 'http://google.com'

def setLook():
    general.set_style(app)
    icon.setThemeName(config.GENERAL_ICONTHEME)
setLook()

def run_about():
    QtGui.QMessageBox.about(MainWindow, 'About', \
        '<b>QBrowse v' + app_version + '</b> by SmiL3y - xakepa10@gmail.com - under GPLv2')

## @brief The CookieJar class inherits QNetworkCookieJar to make a couple of functions public.
class CookieJar(QtNetwork.QNetworkCookieJar):
    def __init__(self, parent=None):
        QtNetwork.QNetworkCookieJar.__init__(self, parent)

    def allCookies(self):
        return QtNetwork.QNetworkCookieJar.allCookies(self)

    def setAllCookies(self, cookieList):
        QtNetwork.QNetworkCookieJar.setAllCookies(self, cookieList)

disk_cache = QtNetwork.QNetworkDiskCache()
home_path = str(QtCore.QDir.homePath())
misc.dir_create(home_path + '/.cache/qbrowse/cache')
disk_cache.setCacheDirectory(home_path + '/.cache/qbrowse/cache')
disk_cache.setMaximumCacheSize(50000000)

class NewTab(QtGui.QWidget):
    ''' Tab constructor '''
    def __init__(self, url='', parent=None, nam=QtNetwork.QNetworkAccessManager()):
        ''' Tab initialiser '''
        super(NewTab, self).__init__(parent)
        # set variables
        self.url = url
        self.tab_index = ui.tabWidget.currentIndex()+1
        self.nam = nam
        self.bookmarks = ('google.com', 'bitbucket.org', 'youtube.com', 'phoronix.com')
        self.icon_back = general.get_icon('back')
        self.icon_next = general.get_icon('forward')
        self.icon_reload = general.get_icon('reload')
        self.icon_stop = general.get_icon('exit')
        self.icon_new = general.get_icon('stock_new-tab')

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
        self.urlBox.currentIndexChanged.connect(self.url_changed)
        self.backButton.setEnabled(False)
        self.backButton.setIcon(self.icon_back)
        self.backButton.clicked.connect(self.back)
        self.backButton.setShortcut(QtGui.QKeySequence('CTRL+B'))
        self.nextButton.setEnabled(False)
        self.nextButton.setIcon(self.icon_next)
        self.nextButton.clicked.connect(self.next)
        self.nextButton.setShortcut(QtGui.QKeySequence('CTRL+N'))
        self.reloadStopButton.clicked.connect(self.reload_stop_page)
        self.reloadStopButton.setShortcut(QtGui.QKeySequence('CTRL+R'))
        self.newButton.setIcon(self.icon_new)
        self.newButton.clicked.connect(self.new_tab)
        self.newButton.setShortcut(QtGui.QKeySequence('CTRL+T'))
        self.webView.linkClicked.connect(self.link_clicked)
        self.webView.urlChanged.connect(self.link_clicked)
        self.webView.loadProgress.connect(self.load_progress)
        self.webView.titleChanged.connect(self.title_changed)
        ui.actionFind.triggered.disconnect()
        ui.actionFind.triggered.connect(self.action_find)
        ui.actionSearch.triggered.disconnect()
        ui.actionSearch.triggered.connect(self.action_search)

        ui.menuBookmarks.clear()
        for mark in self.bookmarks:
            e = ui.menuBookmarks.addAction(general.get_icon('stock_bookmark'), mark)
            ui.menuBookmarks.connect(e, QtCore.SIGNAL('triggered()'), \
                lambda url=mark: self.new_tab(url))

        # advanced funcitonality
        self.webView.page().setForwardUnsupportedContent(True)
        self.webView.page().unsupportedContent.connect(self.download)
        self.nam.setCache(disk_cache)

        self.webView.settings().setAttribute(QtWebKit.QWebSettings.PluginsEnabled, \
            ui.actionPlugins.isChecked())
        self.webView.settings().setAttribute(QtWebKit.QWebSettings.JavascriptEnabled, \
            ui.actionJavascript.isChecked())
        if ui.actionAccessManager.isChecked():
            self.webView.page().setNetworkAccessManager(self.nam)
            self.cookieJar = CookieJar()
            self.nam.setCookieJar(self.cookieJar)

        #self.webView.settings().setMaximumPagesInCache(0)
        #self.webView.settings().setObjectCacheCapacities(0, 0, 0)

        # load page
        self.check_url()
        self.webView.setUrl(QtCore.QUrl(self.url))

    def check_url(self):
        ''' Check if URL is sane '''
        self.url = str(self.url)
        if not os.path.isfile(self.url) and not self.url.startswith('http://') \
            and not self.url.startswith('https://') and not self.url.startswith('ftp://') \
            and not self.url.startswith('ftps://'):
            self.url = 'http://' + self.url

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
        self.check_url()
        self.webView.setUrl(QtCore.QUrl(self.url))

    def title_changed(self, title):
        '''  Web page title changed - change the tab name '''
        MainWindow.setWindowTitle(title)
        ui.tabWidget.setTabText(self.tab_index, title[:20])

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
            ui.tabWidget.setTabIcon(self.tab_index, self.webView.icon())
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

    def new_tab(self, url=None):
        ''' Create a new tab '''
        if not url:
            url = home_page
        index = self.tab_index + 1
        MainWindow.setWindowTitle('New tab')
        ui.tabWidget.insertTab(index, NewTab(url, nam=self.nam), 'New tab')
        ui.tabWidget.setCurrentIndex(index)

    def action_find(self):
        ''' Find text in current page '''
        svar, ok = QtGui.QInputDialog.getText(MainWindow, 'Find', '')
        if ok and svar:
            self.webView.findText(svar)

    def action_search(self):
        ''' Search the internet '''
        svar, ok = QtGui.QInputDialog.getText(MainWindow, 'Search', '')
        if ok and svar:
            self.new_tab('duckduckgo.com/?q=' + svar)

    def download(self, reply):
        ''' Download a URL '''
        sfile = str(reply.url().toString())
        sdir = str(QtGui.QFileDialog.getSaveFileName(MainWindow, 'Save', os.path.basename(sfile)))
        if sdir:
            try:
                misc.fetch(sfile, sdir)
                QtGui.QMessageBox.information(MainWindow, 'Info', \
                    'Dowload of <b>' + sfile + '</b> complete.')
            except Exception as detail:
                QtGui.QMessageBox.critical(MainWindow, 'Critical', str(detail))

def remove_tab():
    ''' Remove tab from UI '''
    ui.tabWidget.removeTab(ui.tabWidget.currentIndex())
    gc.collect()

ui.tabWidget.tabCloseRequested.connect(remove_tab)
ui.actionQuit.triggered.connect(sys.exit)
ui.actionAbout.triggered.connect(run_about)

# initialise
ui.tabWidget.removeTab(0)
NewTab().new_tab(home_page)

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
