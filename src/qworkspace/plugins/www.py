#!/bin/python2

from PyQt4 import QtCore, QtGui, QtWebKit, QtNetwork
import sys, os, libworkspace, libmisc

general = libworkspace.General()
misc = libmisc.Misc()

class CookieJar(QtNetwork.QNetworkCookieJar):
    ''' Cookie jar to save cookies to disk if desired '''
    def __init__(self, parent=None):
        super(CookieJar, self).__init__(parent)
        cookies = []
        for line in misc.file_readlines(cookies_path):
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

    def saveCookies(self):
        ''' Save cookies to disk '''
        self.purge_old_cookies()
        lines = ''
        for cookie in self.allCookies():
            if not cookie.isSessionCookie():
                lines += (bytes(cookie.toRawForm()).decode('utf-8')) + '\n'
        misc.file_write(cookies_path, lines)

class Widget(QtGui.QWidget):
    ''' Tab constructor '''
    def __init__(self, parent, url=''):
        ''' Tab initialiser '''
        super(Widget, self).__init__()
        self.parent = parent
        self.name = 'www'
        self.tab_index = self.parent.tabWidget.currentIndex()+1
        self.nam = manager
        self.icon_back = general.get_icon('back')
        self.icon_next = general.get_icon('forward')
        self.icon_reload = general.get_icon('reload')
        self.icon_stop = general.get_icon('exit')
        self.icon_bookmark = general.get_icon('user-bookmarks')

        # add widgets
        mainLayout = QtGui.QGridLayout()
        secondLayout = QtGui.QHBoxLayout()
        self.thirdLayout = QtGui.QHBoxLayout()
        self.backButton = QtGui.QPushButton()
        self.nextButton = QtGui.QPushButton()
        self.reloadStopButton = QtGui.QPushButton()
        self.urlBox = QtGui.QComboBox()
        self.webView = QtWebKit.QWebView()
        secondLayout.addWidget(self.backButton)
        secondLayout.addWidget(self.nextButton)
        secondLayout.addWidget(self.reloadStopButton)
        secondLayout.addWidget(self.urlBox)
        for b in ('http://github.com', 'http://bitbucket.org', \
            'http://gmail.com', 'http://youtube.com', 'http://zamunda.net',
            'http://archlinux.org', 'http://phoronix.com'):
            self.thirdLayout.addWidget(self.bookmark(b))
        mainLayout.addLayout(secondLayout, 0, 0)
        mainLayout.addLayout(self.thirdLayout, 30, 0)
        mainLayout.addWidget(self.webView)
        self.parent.statusBar.addPermanentWidget(progressBar, 0)
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
        self.webView.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)
        self.webView.linkClicked.connect(self.link_clicked)
        self.webView.urlChanged.connect(self.url_changed)
        self.webView.loadProgress.connect(self.load_progress)
        self.webView.titleChanged.connect(self.title_changed)
        self.webView.iconChanged.connect(self.icon_changed)
        #ui.actionFind.triggered.disconnect()
        #ui.actionFind.triggered.connect(self.action_find)
        #ui.actionSearch.triggered.disconnect()
        #ui.actionSearch.triggered.connect(self.action_search)

        # advanced funcitonality
        self.webView.page().setForwardUnsupportedContent(True)
        self.webView.page().downloadRequested.connect(self.download)
        self.webView.page().unsupportedContent.connect(self.unsupported)

        self.webView.settings().setAttribute(QtWebKit.QWebSettings.PluginsEnabled, \
            True) #ui.actionPlugins.isChecked())
        self.webView.settings().setAttribute(QtWebKit.QWebSettings.JavascriptEnabled, \
            True) #ui.actionJavascript.isChecked())
        if True: #ui.actionAccessManager.isChecked():
            self.webView.page().setNetworkAccessManager(self.nam)
            self.webView.loadFinished.connect(cookie_jar.saveCookies)
            self.nam.finished.connect(self.page_error)
            self.nam.sslErrors.connect(self.page_ssl_errors)

        #self.webView.settings().setMaximumPagesInCache(0)
        #self.webView.settings().setObjectCacheCapacities(0, 0, 0)
        #self.webView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        #self.webView.customContextMenuRequested.connect(self.context_menu)

        # load page
        self.path_changed()

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
        # for some reaons some web-pages do not set or have title
        if not title:
            title = 'Untitled'
        #MainWindow.setWindowTitle(title)
        self.parent.tabWidget.setTabText(self.tab_index, title[:20])

    def icon_changed(self, icon):
        self.parent.tabWidget.setTabIcon(self.tab_index, icon)

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
            progressBar.hide()
            progressBar.setValue(0)
            self.icon_changed(self.webView.icon())

            # load JavaScript user script (http://jquery.com/)
            #if ui.actionJavascript.isChecked():
            #    self.webView.page().mainFrame().evaluateJavaScript(misc.file_read('jquery.js'))
        else:
            progressBar.show()
            progressBar.setValue(load)
            progressBar.setStatusTip(self.webView.statusTip())
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

    def page_reload_stop(self):
        ''' Reload/stop loading the web page '''
        if progressBar.isHidden():
            self.reloadStopButton.setIcon(self.icon_stop)
            self.webView.setUrl(QtCore.QUrl(self.urlBox.currentText()))
        else:
            self.reloadStopButton.setIcon(self.icon_reload)
            self.webView.stop()

    def page_error(self, reply):
        '''Interpret the HTTP error ID received '''
        eid = reply.error()
        # http://pyqt.sourceforge.net/Docs/PyQt4/qnetworkreply.html#error
        errors = {
            1: 'the remote server refused the connection (the server is not accepting requests)',
            2: 'the remote server closed the connection prematurely, before the entire reply was received and processed',
            3: 'the remote host name was not found (invalid hostname)',
            4: 'the connection to the remote server timed out',
            5: 'the operation was canceled via calls to abort() or close() before it was finished.',
            6: 'the SSL/TLS handshake failed and the encrypted channel could not be established. The sslErrors() signal should have been emitted.',
            7: 'the connection was broken due to disconnection from the network, however the system has initiated roaming to another acess point. The request should be resubmitted and will be processed as soon as the connection is re-established.',
            101: 'the connection to the proxy server was refused (the proxy server is not accepting requests)',
            102: 'the proxy server closed the connection prematurely, before the entire reply was received and processed',
            103: 'the proxy host name was not found (invalid proxy hostname)',
            104: 'the connection to the proxy timed out or the proxy did not reply in time to the request sent',
            105: 'the proxy requires authentication in order to honour the request but did not accept any credentials offered (if any)',
            201: 'the access to the remote content was denied (similar to HTTP error 401)',
            202: 'the operation requested on the remote content is not permitted',
            203: 'the remote content was not found at the server (similar to HTTP error 404)',
            204: 'the remote server requires authentication to serve the content but the credentials provided were not accepted (if any)',
            205: 'the request needed to be sent again, but this failed for example because the upload data could not be read a second time.',
            301: 'the Network Access API cannot honor the request because the protocol is not known',
            302: 'the requested operation is invalid for this protocol',
            99: 'an unknown network-related error was detected',
            199: 'an unknown proxy-related error was detected',
            299: 'an unknown error related to the remote content was detected',
            399: 'a breakdown in protocol was detected (parsing error, invalid or unexpected responses, etc.)',
        }
        if eid in errors:
            self.parent.statusBar.showMessage(errors.get(eid, 'unknown error'))
            if eid == 5:
                progressBar.hide()
                progressBar.setValue(0)

    def page_ssl_errors(self, reply, errors):
        reply.ignoreSslErrors()
        self.parent.statusBar.showMessage('SSL errors ignored: ' + str(reply.url().toString()) + ', ' + str(errors))

    def action_find(self):
        ''' Find text in current page '''
        svar, ok = QtGui.QInputDialog.getText(self, 'Find', '')
        if ok and svar:
            self.webView.findText(svar, self.webView.page().HighlightAllOccurrences)

    def action_search(self):
        ''' Search the internet '''
        svar, ok = QtGui.QInputDialog.getText(self, 'Search', '')
        if ok and svar:
            self.webView.setUrl(QtCore.QUrl('duckduckgo.com/?q=' + svar))

    def download(self, request):
        ''' Download a URL '''
        self.unsupported(self.nam.get(request))

    def unsupported(self, reply):
        ''' Download a unsupported URL '''
        # sfile = str(QtGui.QFileDialog.getSaveFileName(self, 'Save', os.path.basename(surl)))
        reply.readyRead.connect(lambda reply=reply: self.download_start(reply))
        reply.finished.connect(lambda reply=reply: self.download_finished(reply))

    def download_start(self, reply):
        surl = str(reply.url().toString())
        sfile = home_path + '/' + os.path.basename(surl)
        misc.file_write(sfile, reply.readAll(), 'a')

    def download_finished(self, reply):
        surl = str(reply.url().toString())
        if reply.error():
            QtGui.QMessageBox.critical(self, 'Critical', \
                'Dowload of <b>' + surl + '</b> failed.')
        else:
            QtGui.QMessageBox.information(self, 'Info', \
                'Dowload of <b>' + surl + '</b> complete.')

    def bookmark(self, url):
        button = QtGui.QPushButton(self.icon_bookmark, url)
        button.clicked.connect(lambda: self.webView.setUrl(QtCore.QUrl(url)))
        return button

    def context_menu(self):
        # FIXME: enable actions depending on what is possible
        menu = QtGui.QMenu()
        menu.addAction(self.icon_back, 'Back', self.page_back)
        menu.addAction(self.icon_next, 'Next', self.page_next)
        menu.addAction(self.icon_reload, 'Reload', self.page_reload_stop)
        menu.popup(QtGui.QCursor.pos())


class Plugin(object):
    def __init__(self, parent=None):
        self.parent = parent
        self.name = 'www'
        self.version = '0.0.1'
        self.description = 'World Wide Web browser'
        self.icon = general.get_icon('web-browser')
        self.widget = None

        self.wwwButton = QtGui.QPushButton(general.get_icon('web-browser'), '')
        self.wwwButton.clicked.connect(lambda: self.open('http://www.google.com'))
        self.applicationsLayout = self.parent.toolBox.widget(1).layout()
        self.applicationsLayout.addWidget(self.wwwButton)

    def open(self, spath):
        ''' Open path in new tab '''
        self.widget = Widget(self.parent, spath)
        self.index = self.parent.tabWidget.currentIndex()+1
        self.parent.tabWidget.insertTab(self.index, self.widget, self.icon, 'WWW')
        self.parent.tabWidget.setCurrentIndex(self.index)

    def close(self):
        ''' Close tab '''
        if self.widget:
            self.widget.destroy()
            self.parent.tabWidget.removeTab(self.index)

    def unload(self):
        ''' Unload plugin '''
        self.applicationsLayout.removeWidget(self.wwwButton)
        self.close()

# initialise
home_path = str(QtCore.QDir.homePath())
cache_path = home_path + '/.cache/qbrowse/cache'
cookies_path = home_path + '/.cache/qbrowse/cookies.txt'
misc.dir_create(cache_path)
misc.file_touch(cookies_path)
disk_cache = QtNetwork.QNetworkDiskCache()
disk_cache.setCacheDirectory(cache_path)
disk_cache.setMaximumCacheSize(50000000)
cookie_jar = CookieJar()
manager = QtNetwork.QNetworkAccessManager()
manager.setCache(disk_cache)
manager.setCookieJar(cookie_jar)
progressBar = QtGui.QProgressBar()

