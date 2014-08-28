#!/bin/python2

from PyQt4 import QtCore, QtGui, QtWebKit, QtNetwork
import os, libworkspace, libmisc

general = libworkspace.General()
misc = libmisc.Misc()

home_path = str(QtCore.QDir.homePath())
cache_path = home_path + '/.cache/www/cache'
cookies_path = home_path + '/.cache/www/cookies.txt'
misc.dir_create(cache_path)
misc.file_touch(cookies_path)

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
        self.icon_back = general.get_icon('go-previous')
        self.icon_next = general.get_icon('go-next')
        self.icon_reload = general.get_icon('view-refresh')
        self.icon_stop = general.get_icon('process-stop')
        self.icon_find = general.get_icon('edit-find')
        self.icon_search = general.get_icon('system-search')
        self.icon_bookmark = general.get_icon('bookmark')
        self.disk_cache = QtNetwork.QNetworkDiskCache()
        self.disk_cache.setCacheDirectory(cache_path)
        self.disk_cache.setMaximumCacheSize(50000000)
        self.cookie_jar = CookieJar()
        self.nam = QtNetwork.QNetworkAccessManager()
        self.nam.setCache(self.disk_cache)
        self.nam.setCookieJar(self.cookie_jar)

        # add widgets
        self.mainLayout = QtGui.QGridLayout()
        self.secondLayout = QtGui.QHBoxLayout()
        self.thirdLayout = QtGui.QHBoxLayout()
        self.fourthLayout = QtGui.QHBoxLayout()
        self.backButton = QtGui.QPushButton(self.icon_back, '')
        self.nextButton = QtGui.QPushButton(self.icon_next, '')
        self.reloadStopButton = QtGui.QPushButton(self.icon_reload, '')
        self.findButton = QtGui.QPushButton(self.icon_find, '')
        self.searchButton = QtGui.QPushButton(self.icon_search, '')
        self.urlBox = QtGui.QComboBox()
        self.webView = QtWebKit.QWebView()
        self.statusLabel = QtGui.QLabel()
        self.statusLabel.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        self.progressBar = QtGui.QProgressBar()
        self.secondLayout.addWidget(self.backButton)
        self.secondLayout.addWidget(self.nextButton)
        self.secondLayout.addWidget(self.reloadStopButton)
        self.secondLayout.addWidget(self.findButton)
        self.secondLayout.addWidget(self.searchButton)
        self.secondLayout.addWidget(self.urlBox)
        for b in ('github.com', 'bitbucket.org', \
            'gmail.com', 'youtube.com', 'zamunda.net', \
            'archlinux.org', 'phoronix.com', 'html5test.com'):
            self.thirdLayout.addWidget(self.bookmark(b))
        self.fourthLayout.addWidget(self.statusLabel)
        self.fourthLayout.addWidget(self.progressBar)
        self.mainLayout.addLayout(self.secondLayout, 0, 0)
        self.mainLayout.addLayout(self.thirdLayout, 60, 0)
        self.mainLayout.addWidget(self.webView)
        self.mainLayout.addLayout(self.fourthLayout, QtCore.Qt.AlignBottom, 0)
        self.setLayout(self.mainLayout)

        # setup widgets
        self.urlBox.setEditable(True)
        self.urlBox.setEditText(url)
        self.urlBox.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        self.urlBox.setInsertPolicy(1)
        self.urlBox.setToolTip(self.tr('Current page URL'))
        self.urlBox.currentIndexChanged.connect(self.path_changed)
        self.backButton.setEnabled(False)
        self.backButton.setToolTip(self.tr('Go to previous page'))
        self.backButton.clicked.connect(self.page_back)
        self.backButton.setShortcut(QtGui.QKeySequence(self.tr('CTRL+B')))
        self.nextButton.setEnabled(False)
        self.nextButton.setToolTip(self.tr('Go to next page'))
        self.nextButton.clicked.connect(self.page_next)
        self.nextButton.setShortcut(QtGui.QKeySequence(self.tr('CTRL+N')))
        self.reloadStopButton.clicked.connect(self.page_reload_stop)
        self.reloadStopButton.setShortcut(QtGui.QKeySequence(self.tr('CTRL+R')))
        self.findButton.setToolTip(self.tr('Find text in currently loaded page'))
        self.findButton.clicked.connect(self.action_find)
        self.findButton.setShortcut(QtGui.QKeySequence(self.tr('CTRL+F')))
        self.searchButton.setToolTip(self.tr('Search the internet for keyword'))
        self.searchButton.clicked.connect(self.action_search)
        self.searchButton.setShortcut(QtGui.QKeySequence(self.tr('CTRL+S')))
        self.webView.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)
        self.webView.linkClicked.connect(self.link_clicked)
        self.webView.urlChanged.connect(self.url_changed)
        self.webView.loadStarted.connect(self.load_started)
        self.webView.loadProgress.connect(self.load_progress)
        self.webView.loadFinished.connect(self.load_finished)

        # advanced funcitonality
        self.webView.page().setForwardUnsupportedContent(True)
        self.webView.page().downloadRequested.connect(self.download)
        self.webView.page().unsupportedContent.connect(self.unsupported)

        self.webView.settings().setAttribute(QtWebKit.QWebSettings.PluginsEnabled, True)
        self.webView.settings().setAttribute(QtWebKit.QWebSettings.JavascriptEnabled, True)
        self.webView.page().setNetworkAccessManager(self.nam)
        self.webView.loadFinished.connect(self.cookie_jar.saveCookies)
        self.nam.finished.connect(self.page_error)
        self.nam.sslErrors.connect(self.page_ssl_errors)

        # http://qt-project.org/doc/qt-4.8/qwebsettings.html#WebAttribute-enum
        self.webView.settings().setAttribute(QtWebKit.QWebSettings.DnsPrefetchEnabled, True)
        self.webView.settings().setAttribute(QtWebKit.QWebSettings.DeveloperExtrasEnabled, True)
        self.webView.settings().setAttribute(QtWebKit.QWebSettings.LocalStorageEnabled, True)
        self.webView.settings().setAttribute(QtWebKit.QWebSettings.LocalStorageDatabaseEnabled, True)
        self.webView.settings().setAttribute(QtWebKit.QWebSettings.LocalContentCanAccessRemoteUrls, True)
        self.webView.settings().setAttribute(QtWebKit.QWebSettings.LocalContentCanAccessFileUrls, True)


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
        self.statusLabel.setText('')
        self.webView.setUrl(QtCore.QUrl(url))

    # basic functionality methods
    def url_changed(self, url):
        ''' Url have been changed by user '''
        self.urlBox.setEditText(url.toString())

    def link_clicked(self, url):
        ''' Update the URL if a link on a web page is clicked '''
        if url.toString().startswith('mailto:'):
            self.parent.plugins.plugin_open_with('mail', \
                url.toString().replace('mailto:', ''))
            return
        if '#' in url.toString():
            print('Warning, possible hashtag URL: ' + url.toString())
        self.webView.setUrl(QtCore.QUrl(url))

    def load_started(self):
        ''' Page load started '''
        self.reloadStopButton.setIcon(self.icon_stop)
        self.reloadStopButton.setToolTip(self.tr('Stop loading the page'))
        self.progressBar.show()

    def load_progress(self, load):
        ''' Page load progress '''
        self.progressBar.setValue(load)

    def load_finished(self):
        ''' Page load finished '''
        self.reloadStopButton.setIcon(self.icon_reload)
        self.reloadStopButton.setToolTip(self.tr('Reload currently loaded page'))
        self.progressBar.hide()
        self.progressBar.setValue(0)
        history = self.webView.page().history()
        if history.canGoBack():
            self.backButton.setEnabled(True)
        else:
            self.backButton.setEnabled(False)
        if history.canGoForward():
            self.nextButton.setEnabled(True)
        else:
            self.nextButton.setEnabled(False)

        # load JavaScript user script (http://jquery.com/)
        # self.webView.page().mainFrame().evaluateJavaScript(misc.file_read('jquery.js'))

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
        if self.progressBar.isHidden():
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
            1: self.tr('the remote server refused the connection (the server is not accepting requests)'),
            2: self.tr('the remote server closed the connection prematurely, before the entire reply was received and processed'),
            3: self.tr('the remote host name was not found (invalid hostname)'),
            4: self.tr('the connection to the remote server timed out'),
            5: self.tr('the operation was canceled via calls to abort() or close() before it was finished.'),
            6: self.tr('the SSL/TLS handshake failed and the encrypted channel could not be established. The sslErrors() signal should have been emitted.'),
            7: self.tr('the connection was broken due to disconnection from the network, however the system has initiated roaming to another acess point. The request should be resubmitted and will be processed as soon as the connection is re-established.'),
            101: self.tr('the connection to the proxy server was refused (the proxy server is not accepting requests)'),
            102: self.tr('the proxy server closed the connection prematurely, before the entire reply was received and processed'),
            103: self.tr('the proxy host name was not found (invalid proxy hostname)'),
            104: self.tr('the connection to the proxy timed out or the proxy did not reply in time to the request sent'),
            105: self.tr('the proxy requires authentication in order to honour the request but did not accept any credentials offered (if any)'),
            201: self.tr('the access to the remote content was denied (similar to HTTP error 401)'),
            202: self.tr('the operation requested on the remote content is not permitted'),
            203: self.tr('the remote content was not found at the server (similar to HTTP error 404)'),
            204: self.tr('the remote server requires authentication to serve the content but the credentials provided were not accepted (if any)'),
            205: self.tr('the request needed to be sent again, but this failed for example because the upload data could not be read a second time.'),
            301: self.tr('the Network Access API cannot honor the request because the protocol is not known'),
            302: self.tr('the requested operation is invalid for this protocol'),
            99: self.tr('an unknown network-related error was detected'),
            199: self.tr('an unknown proxy-related error was detected'),
            299: self.tr('an unknown error related to the remote content was detected'),
            399: self.tr('a breakdown in protocol was detected (parsing error, invalid or unexpected responses, etc.)'),
        }
        if eid in errors:
            self.statusLabel.setText(errors.get(eid, self.tr('unknown error')))
            if eid == 5:
                self.progressBar.hide()
                self.progressBar.setValue(0)

    def page_ssl_errors(self, reply, errors):
        ''' SSL error handler '''
        reply.ignoreSslErrors()
        self.statusLabel.setText(self.tr('SSL errors ignored: %s, %s') % (reply.url().toString(), errors))

    def action_find(self):
        ''' Find text in current page '''
        svar, ok = QtGui.QInputDialog.getText(self, self.tr('Find'), '')
        if ok and svar:
            self.webView.findText(svar, self.webView.page().HighlightAllOccurrences)

    def action_search(self):
        ''' Search the internet '''
        svar, ok = QtGui.QInputDialog.getText(self, self.tr('Search'), '')
        if ok and svar:
            self.webView.setUrl(QtCore.QUrl('https://duckduckgo.com/?q=' + svar))

    def download(self, request):
        ''' Download a URL '''
        self.unsupported(self.nam.get(request))

    def unsupported(self, reply):
        ''' Download a unsupported URL '''
        self.parent.plugins.plugin_open_with('download', reply.url().toString())

    def bookmark_open(self, url):
        ''' Open a bookmark '''
        self.urlBox.setEditText(url)
        self.path_changed()

    def bookmark(self, url):
        ''' Bookmark button creator, separate to preserve url connection '''
        button = QtGui.QPushButton(self.icon_bookmark, url)
        button.clicked.connect(lambda: self.bookmark_open(url))
        return button

    def context_menu(self):
        ''' Custom context menu '''
        # FIXME: enable actions depending on what is possible
        menu = QtGui.QMenu()
        menu.addAction(self.icon_back, self.tr('Back'), self.page_back)
        menu.addAction(self.icon_next, self.tr('Next'), self.page_next)
        menu.addAction(self.icon_reload, self.tr('Reload'), self.page_reload_stop)
        menu.popup(QtGui.QCursor.pos())



class Plugin(QtCore.QObject):
    ''' Plugin handler '''
    def __init__(self, parent):
        super(Plugin, self).__init__()
        self.parent = parent
        self.name = 'www'
        self.version = "0.9.34 (5f8499a)"
        self.description = self.tr('World Wide Web browser plugin')
        self.icon = general.get_icon('internet-web-browser')
        self.widget = None

        self.wwwButton = QtGui.QPushButton(self.icon, '')
        self.wwwButton.setToolTip(self.description)
        self.wwwButton.clicked.connect(lambda: self.open('http://www.google.com'))
        self.applicationsLayout = self.parent.toolBox.widget(1).layout()
        self.applicationsLayout.addWidget(self.wwwButton)

    def open(self, spath):
        ''' Open path in new tab '''
        index = self.parent.tabWidget.currentIndex()+1
        self.widget = Widget(self.parent, spath)
        self.parent.tabWidget.insertTab(index, self.widget, self.icon, self.tr('WWW'))
        self.parent.tabWidget.setCurrentIndex(index)

    def close(self, index=None):
        ''' Close tab '''
        if not index:
            index = self.parent.tabWidget.currentIndex()
        if self.widget:
            self.widget.webView.stop()
            self.widget.deleteLater()
            self.widget = None
            self.parent.tabWidget.removeTab(index)

    def unload(self):
        ''' Unload plugin '''
        self.applicationsLayout.removeWidget(self.wwwButton)
        self.close()

