#!/bin/python2

import qbrowse_ui
from PyQt4 import QtCore, QtGui
import sys, os
import libmisc, libdesktop

# prepare for lift-off
app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()
ui = qbrowse_ui.Ui_MainWindow()
ui.setupUi(MainWindow)

# some variables
actions = libdesktop.Actions(MainWindow, app)
config = libdesktop.Config()
misc = libmisc.Misc()
icon = QtGui.QIcon()

def setLook():
    config.read()
    ssheet = '/etc/qdesktop/styles/' + config.GENERAL_STYLESHEET + '/style.qss'
    if config.GENERAL_STYLESHEET and os.path.isfile(ssheet):
        app.setStyleSheet(misc.file_read(ssheet))
    else:
        app.setStyleSheet('')
    icon.setThemeName(config.GENERAL_ICONTHEME)
setLook()

def url_changed():
    ''' Url have been changed by user '''
    page = ui.webView.page()
    history = page.history()
    if history.canGoBack():
        ui.back.setEnabled(True)
    else:
        ui.back.setEnabled(False)
    if history.canGoForward():
        ui.next.setEnabled(True)
    else:
        ui.next.setEnabled(False)

    url = str(ui.url.text())
    if not url.startswith('http://') and not url.startswith('https://') \
        and not url.startswith('ftp://') and not url.startswith('ftps://'):
        url = 'http://' + url
    ui.webView.setUrl(QtCore.QUrl(url))

def stop_page():
    ''' Stop loading the page '''
    ui.webView.stop()

def title_changed(title):
    '''  Web page title changed - change the tab name '''
    MainWindow.setWindowTitle(title)

def reload_page():
    ''' Reload the web page '''
    ui.webView.setUrl(QtCore.QUrl(ui.url.text()))

def link_clicked(url):
    ''' Update the URL if a link on a web page is clicked '''
    page = ui.webView.page()
    history = page.history()
    if history.canGoBack():
        ui.back.setEnabled(True)
    else:
        ui.back.setEnabled(False)
    if history.canGoForward():
        ui.next.setEnabled(True)
    else:
        ui.next.setEnabled(False)

    ui.url.setText(url.toString())

def load_progress(load):
    ''' Page load progress '''
    if load == 100:
        ui.stop.setEnabled(False)
    else:
        ui.stop.setEnabled(True)

def back():
    ''' Back button clicked, go one page back '''
    page = ui.webView.page()
    history = page.history()
    history.back()
    if history.canGoBack():
        ui.back.setEnabled(True)
    else:
        ui.back.setEnabled(False)

def next():
    ''' Next button clicked, go to next page '''
    page = ui.webView.page()
    history = page.history()
    history.forward()
    if history.canGoForward():
        ui.next.setEnabled(True)
    else:
        ui.next.setEnabled(False)

# set the default
url = 'http://google.co.uk'
ui.url.setText(url)

# history buttons:
ui.back.setEnabled(False)
ui.next.setEnabled(False)

# ui.webView.settings()

ui.back.clicked.connect(back)
ui.next.clicked.connect(next)
ui.url.returnPressed.connect(url_changed)
ui.webView.linkClicked.connect(link_clicked)
ui.webView.urlChanged.connect(link_clicked)
ui.webView.loadProgress.connect(load_progress)
ui.webView.titleChanged.connect(title_changed)
ui.reload.clicked.connect(reload_page)
ui.stop.clicked.connect(stop_page)
ui.actionQuit.triggered.connect(sys.exit)

# load page
ui.webView.setUrl(QtCore.QUrl(url))

app = QtGui.QApplication(sys.argv)
MainWindow.show()
sys.exit(app.exec_())
