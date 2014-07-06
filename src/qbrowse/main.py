#!/bin/python2

import qbrowse_ui
from PyQt4 import QtCore, QtGui, QtWebKit, QtNetwork
import sys, os, gc, libdesktop, libmisc

# prepare for lift-off
app_version = "0.9.8 (666119f)"
app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()
ui = qbrowse_ui.Ui_MainWindow()
ui.setupUi(MainWindow)
config = libdesktop.Config()
general = libdesktop.General()
misc = libmisc.Misc()
home_page = 'http://google.com'

def setLook():
    general.set_style(app)
setLook()

def run_about():
    QtGui.QMessageBox.about(MainWindow, 'About', \
        '<b>QBrowse v' + app_version + '</b> by SmiL3y - xakepa10@gmail.com - under GPLv2')

class CookieJar(QtNetwork.QNetworkCookieJar):
    ''' Cookie jar to save cookies to disk if desired '''
    def __init__(self, parent=None):
        super(CookieJar, self).__init__(parent)
        cookies = []
        for line in misc.file_readlines(home_path + '/.cache/qbrowse/cookies.txt'):
            cookies += QtNetwork.QNetworkCookie.parseCookies(line.encode('utf-8'))
        self.setAllCookies(cookies)

    def purge_old_cookies(self):
        ''' Purge expired cookies from the cookie jar '''
        now = QtCore.QDateTime.currentDateTime()
        cookies = [c for c in self.allCookies()
                   if c.isSessionCookie() or c.expirationDate() >= now]
        self.setAllCookies(cookies)

    def setCookiesFromUrl(self, cookies, url):
        ''' Add the cookies in the cookies list to this cookie jar '''
        return super(CookieJar, self).setCookiesFromUrl(cookies, url)

    def save(self):
        ''' Save cookies to disk '''
        self.purge_old_cookies()
        lines = ''
        for cookie in self.allCookies():
            if not cookie.isSessionCookie():
                lines += (bytes(cookie.toRawForm()).decode('utf-8')) + '\n'
        misc.file_write(home_path + '/.cache/qbrowse/cookies.txt', lines)


class NewTab(QtGui.QWidget):
    ''' Tab constructor '''
    def __init__(self, url='', parent=None):
        ''' Tab initialiser '''
        super(NewTab, self).__init__(parent)
        # set variables
        self.tab_index = ui.tabWidget.currentIndex()+1
        self.nam = manager
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
        self.urlBox.setEditText(url)
        policy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        self.urlBox.setSizePolicy(policy)
        self.urlBox.setInsertPolicy(1)
        self.urlBox.currentIndexChanged.connect(self.path_changed)
        self.backButton.setEnabled(False)
        self.backButton.setIcon(self.icon_back)
        self.backButton.clicked.connect(self.page_back)
        self.backButton.setShortcut(QtGui.QKeySequence('CTRL+B'))
        self.nextButton.setEnabled(False)
        self.nextButton.setIcon(self.icon_next)
        self.nextButton.clicked.connect(self.page_next)
        self.nextButton.setShortcut(QtGui.QKeySequence('CTRL+N'))
        self.reloadStopButton.clicked.connect(self.page_reload_stop)
        self.reloadStopButton.setShortcut(QtGui.QKeySequence('CTRL+R'))
        self.newButton.setIcon(self.icon_new)
        self.newButton.clicked.connect(self.tab_new)
        self.newButton.setShortcut(QtGui.QKeySequence('CTRL+T'))
        self.webView.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)
        self.webView.linkClicked.connect(self.link_clicked)
        self.webView.urlChanged.connect(self.url_changed)
        self.webView.loadProgress.connect(self.load_progress)
        self.webView.titleChanged.connect(self.title_changed)
        ui.actionFind.triggered.disconnect()
        ui.actionFind.triggered.connect(self.action_find)
        ui.actionSearch.triggered.disconnect()
        ui.actionSearch.triggered.connect(self.action_search)

        # advanced funcitonality
        self.webView.page().setForwardUnsupportedContent(True)
        self.webView.page().unsupportedContent.connect(self.download)

        self.webView.settings().setAttribute(QtWebKit.QWebSettings.PluginsEnabled, \
            ui.actionPlugins.isChecked())
        self.webView.settings().setAttribute(QtWebKit.QWebSettings.JavascriptEnabled, \
            ui.actionJavascript.isChecked())
        if ui.actionAccessManager.isChecked():
            self.webView.page().setNetworkAccessManager(self.nam)
            self.webView.loadFinished.connect(cookie_jar.save)

        #self.webView.settings().setMaximumPagesInCache(0)
        #self.webView.settings().setObjectCacheCapacities(0, 0, 0)
        #self.webView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        #self.webView.customContextMenuRequested.connect(self.context_menu)

        # load page
        self.webView.setUrl(QtCore.QUrl(url))

    def path_changed(self):
        ''' Check if URL is sane '''
        url = str(self.urlBox.currentText())
        if not os.path.isfile(url) and not url.startswith('http://') \
            and not url.startswith('https://') and not url.startswith('ftp://') \
            and not url.startswith('ftps://'):
            url = 'http://' + url
        self.webView.setUrl(QtCore.QUrl(url))

    # basic functionality methods
    def url_changed(self, url):
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
        self.urlBox.setEditText(url.toString())


    def title_changed(self, title):
        '''  Web page title changed - change the tab name '''
        MainWindow.setWindowTitle(title)
        ui.tabWidget.setTabText(self.tab_index, title[:20])

    def page_reload_stop(self):
        ''' Reload/stop loading the web page '''
        if self.progressBar.isHidden():
            self.reloadStopButton.setIcon(self.icon_stop)
            self.webView.setUrl(QtCore.QUrl(self.urlBox.currentText()))
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
        self.webView.setUrl(QtCore.QUrl(url))

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

    def page_back(self):
        ''' Back button clicked, go one page back '''
        history = self.webView.page().history()
        history.back()
        if history.canGoBack():
            self.backButton.setEnabled(True)
        else:
            self.backButton.setEnabled(False)

    def page_next(self):
        ''' Next button clicked, go to next page '''
        history = self.webView.page().history()
        history.forward()
        if history.canGoForward():
            self.nextButton.setEnabled(True)
        else:
            self.nextButton.setEnabled(False)

    def tab_new(self, url):
        ''' Create a new tab '''
        if not url:
            url = home_page
        index = self.tab_index+1
        MainWindow.setWindowTitle('New tab')
        ui.tabWidget.insertTab(index, NewTab(url), 'New tab')
        ui.tabWidget.setCurrentIndex(index)
        check_closable()

    def action_find(self):
        ''' Find text in current page '''
        svar, ok = QtGui.QInputDialog.getText(MainWindow, 'Find', '')
        if ok and svar:
            self.webView.findText(svar, self.webView.page().HighlightAllOccurrences)

    def action_search(self):
        ''' Search the internet '''
        svar, ok = QtGui.QInputDialog.getText(MainWindow, 'Search', '')
        if ok and svar:
            self.tab_new('duckduckgo.com/?q=' + svar)

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

    def context_menu(self):
        # FIXME: enable actions depending on what is possible
        menu = QtGui.QMenu()
        menu.addAction(self.icon_back, 'Back', self.page_back)
        menu.addAction(self.icon_next, 'Next', self.page_next)
        menu.addAction(self.icon_reload, 'Reload', self.page_reload_stop)
        menu.addAction(self.icon_new, 'Open in new tab', \
            lambda url=self.webView.page().selectedText(): self.tab_new(url))
        menu.popup(QtGui.QCursor.pos())

def check_closable():
    if ui.tabWidget.count() == 1:
        ui.tabWidget.setTabsClosable(False)
    else:
        ui.tabWidget.setTabsClosable(True)

def tab_remove(index=ui.tabWidget.currentIndex()):
    ''' Remove tab from UI '''
    ui.tabWidget.removeTab(index)
    check_closable()
    gc.collect()

ui.tabWidget.tabCloseRequested.connect(tab_remove)
ui.actionQuit.triggered.connect(sys.exit)
ui.actionAbout.triggered.connect(run_about)

# initialise
disk_cache = QtNetwork.QNetworkDiskCache()
home_path = str(QtCore.QDir.homePath())
misc.dir_create(home_path + '/.cache/qbrowse/cache')
disk_cache.setCacheDirectory(home_path + '/.cache/qbrowse/cache')
disk_cache.setMaximumCacheSize(50000000)
manager = QtNetwork.QNetworkAccessManager()
manager.setCache(disk_cache)
cookie_jar = CookieJar()
manager.setCookieJar(cookie_jar)
NewTab().tab_new(home_page)

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
