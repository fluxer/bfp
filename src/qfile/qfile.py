# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qfile.ui'
#
# Created: Sun May 18 00:54:47 2014
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(663, 470)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/usr/share/pfm/resources/computer.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.MountsWidget = QtGui.QListView(self.centralwidget)
        self.MountsWidget.setGeometry(QtCore.QRect(10, 60, 141, 361))
        self.MountsWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.MountsWidget.setObjectName(_fromUtf8("MountsWidget"))
        self.ViewWidget = QtGui.QListView(self.centralwidget)
        self.ViewWidget.setGeometry(QtCore.QRect(170, 60, 481, 361))
        self.ViewWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ViewWidget.setAcceptDrops(True)
        self.ViewWidget.setDragEnabled(True)
        self.ViewWidget.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
        self.ViewWidget.setDefaultDropAction(QtCore.Qt.CopyAction)
        self.ViewWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.ViewWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        self.ViewWidget.setMovement(QtGui.QListView.Snap)
        self.ViewWidget.setResizeMode(QtGui.QListView.Adjust)
        self.ViewWidget.setViewMode(QtGui.QListView.IconMode)
        self.ViewWidget.setObjectName(_fromUtf8("ViewWidget"))
        self.BackButton = QtGui.QCommandLinkButton(self.centralwidget)
        self.BackButton.setGeometry(QtCore.QRect(10, 10, 41, 41))
        self.BackButton.setText(_fromUtf8(""))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/usr/share/pfm/resources/back.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.BackButton.setIcon(icon1)
        self.BackButton.setObjectName(_fromUtf8("BackButton"))
        self.TerminalButton = QtGui.QCommandLinkButton(self.centralwidget)
        self.TerminalButton.setGeometry(QtCore.QRect(110, 10, 41, 41))
        self.TerminalButton.setText(_fromUtf8(""))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/usr/share/pfm/resources/utilities-terminal.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.TerminalButton.setIcon(icon2)
        self.TerminalButton.setObjectName(_fromUtf8("TerminalButton"))
        self.HomeButton = QtGui.QCommandLinkButton(self.centralwidget)
        self.HomeButton.setGeometry(QtCore.QRect(60, 10, 41, 41))
        self.HomeButton.setText(_fromUtf8(""))
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/usr/share/pfm/resources/go-home.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.HomeButton.setIcon(icon3)
        self.HomeButton.setObjectName(_fromUtf8("HomeButton"))
        self.AddressBar = QtGui.QLineEdit(self.centralwidget)
        self.AddressBar.setGeometry(QtCore.QRect(170, 20, 481, 23))
        self.AddressBar.setReadOnly(True)
        self.AddressBar.setObjectName(_fromUtf8("AddressBar"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 663, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuMain = QtGui.QMenu(self.menubar)
        self.menuMain.setObjectName(_fromUtf8("menuMain"))
        self.menuActions = QtGui.QMenu(self.menubar)
        self.menuActions.setObjectName(_fromUtf8("menuActions"))
        self.menuNew = QtGui.QMenu(self.menuActions)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(_fromUtf8(":/usr/share/pfm/resources/add.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.menuNew.setIcon(icon4)
        self.menuNew.setObjectName(_fromUtf8("menuNew"))
        self.menuArchive = QtGui.QMenu(self.menuActions)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(_fromUtf8(":/usr/share/pfm/resources/application-x-compress.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.menuArchive.setIcon(icon5)
        self.menuArchive.setObjectName(_fromUtf8("menuArchive"))
        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menuHelp.setObjectName(_fromUtf8("menuHelp"))
        self.menuOptions = QtGui.QMenu(self.menubar)
        self.menuOptions.setObjectName(_fromUtf8("menuOptions"))
        self.menuView = QtGui.QMenu(self.menuOptions)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(_fromUtf8(":/usr/share/pfm/resources/gnome-settings-ui-behavior.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.menuView.setIcon(icon6)
        self.menuView.setObjectName(_fromUtf8("menuView"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.actionQuit = QtGui.QAction(MainWindow)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(_fromUtf8(":/usr/share/pfm/resources/exit.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionQuit.setIcon(icon7)
        self.actionQuit.setObjectName(_fromUtf8("actionQuit"))
        self.actionTerminal = QtGui.QAction(MainWindow)
        self.actionTerminal.setIcon(icon2)
        self.actionTerminal.setObjectName(_fromUtf8("actionTerminal"))
        self.actionCopy = QtGui.QAction(MainWindow)
        self.actionCopy.setEnabled(False)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(_fromUtf8(":/usr/share/pfm/resources/edit-copy.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionCopy.setIcon(icon8)
        self.actionCopy.setObjectName(_fromUtf8("actionCopy"))
        self.actionPaste = QtGui.QAction(MainWindow)
        self.actionPaste.setEnabled(False)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(_fromUtf8(":/usr/share/pfm/resources/gtk-paste.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionPaste.setIcon(icon9)
        self.actionPaste.setObjectName(_fromUtf8("actionPaste"))
        self.actionCut = QtGui.QAction(MainWindow)
        self.actionCut.setEnabled(False)
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap(_fromUtf8(":/usr/share/pfm/resources/editcut.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionCut.setIcon(icon10)
        self.actionCut.setObjectName(_fromUtf8("actionCut"))
        self.actionAbout = QtGui.QAction(MainWindow)
        icon11 = QtGui.QIcon()
        icon11.addPixmap(QtGui.QPixmap(_fromUtf8(":/usr/share/pfm/resources/stock_view-details.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionAbout.setIcon(icon11)
        self.actionAbout.setObjectName(_fromUtf8("actionAbout"))
        self.actionDelete = QtGui.QAction(MainWindow)
        self.actionDelete.setEnabled(False)
        icon12 = QtGui.QIcon()
        icon12.addPixmap(QtGui.QPixmap(_fromUtf8(":/usr/share/pfm/resources/editdelete.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionDelete.setIcon(icon12)
        self.actionDelete.setObjectName(_fromUtf8("actionDelete"))
        self.actionProperties = QtGui.QAction(MainWindow)
        self.actionProperties.setEnabled(False)
        icon13 = QtGui.QIcon()
        icon13.addPixmap(QtGui.QPixmap(_fromUtf8(":/usr/share/pfm/resources/stock_properties.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionProperties.setIcon(icon13)
        self.actionProperties.setObjectName(_fromUtf8("actionProperties"))
        self.actionCompress = QtGui.QAction(MainWindow)
        self.actionCompress.setEnabled(False)
        icon14 = QtGui.QIcon()
        icon14.addPixmap(QtGui.QPixmap(_fromUtf8(":/usr/share/pfm/resources/application-x-gzip.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionCompress.setIcon(icon14)
        self.actionCompress.setObjectName(_fromUtf8("actionCompress"))
        self.actionDecompress = QtGui.QAction(MainWindow)
        self.actionDecompress.setEnabled(False)
        icon15 = QtGui.QIcon()
        icon15.addPixmap(QtGui.QPixmap(_fromUtf8(":/usr/share/pfm/resources/cab_extract.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionDecompress.setIcon(icon15)
        self.actionDecompress.setObjectName(_fromUtf8("actionDecompress"))
        self.actionIcons = QtGui.QAction(MainWindow)
        icon16 = QtGui.QIcon()
        icon16.addPixmap(QtGui.QPixmap(_fromUtf8(":/usr/share/pfm/resources/plugin-scale.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionIcons.setIcon(icon16)
        self.actionIcons.setObjectName(_fromUtf8("actionIcons"))
        self.actionList = QtGui.QAction(MainWindow)
        icon17 = QtGui.QIcon()
        icon17.addPixmap(QtGui.QPixmap(_fromUtf8(":/usr/share/pfm/resources/edit-select-all.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionList.setIcon(icon17)
        self.actionList.setObjectName(_fromUtf8("actionList"))
        self.actionPreferences = QtGui.QAction(MainWindow)
        icon18 = QtGui.QIcon()
        icon18.addPixmap(QtGui.QPixmap(_fromUtf8(":/usr/share/pfm/resources/redhat-tools.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionPreferences.setIcon(icon18)
        self.actionPreferences.setObjectName(_fromUtf8("actionPreferences"))
        self.actionRename = QtGui.QAction(MainWindow)
        self.actionRename.setEnabled(False)
        icon19 = QtGui.QIcon()
        icon19.addPixmap(QtGui.QPixmap(_fromUtf8(":/usr/share/pfm/resources/edit-rename.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionRename.setIcon(icon19)
        self.actionRename.setObjectName(_fromUtf8("actionRename"))
        self.actionMimes = QtGui.QAction(MainWindow)
        self.actionMimes.setObjectName(_fromUtf8("actionMimes"))
        self.actionOpen = QtGui.QAction(MainWindow)
        icon20 = QtGui.QIcon()
        icon20.addPixmap(QtGui.QPixmap(_fromUtf8(":/usr/share/pfm/resources/fileopen.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionOpen.setIcon(icon20)
        self.actionOpen.setObjectName(_fromUtf8("actionOpen"))
        self.actionFolder = QtGui.QAction(MainWindow)
        icon21 = QtGui.QIcon()
        icon21.addPixmap(QtGui.QPixmap(_fromUtf8(":/usr/share/pfm/resources/folder_new.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionFolder.setIcon(icon21)
        self.actionFolder.setObjectName(_fromUtf8("actionFolder"))
        self.actionFile = QtGui.QAction(MainWindow)
        icon22 = QtGui.QIcon()
        icon22.addPixmap(QtGui.QPixmap(_fromUtf8(":/usr/share/pfm/resources/filenew.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionFile.setIcon(icon22)
        self.actionFile.setObjectName(_fromUtf8("actionFile"))
        self.actionAsd = QtGui.QAction(MainWindow)
        self.actionAsd.setObjectName(_fromUtf8("actionAsd"))
        self.actionCompress_xz = QtGui.QAction(MainWindow)
        self.actionCompress_xz.setEnabled(False)
        self.actionCompress_xz.setIcon(icon5)
        self.actionCompress_xz.setObjectName(_fromUtf8("actionCompress_xz"))
        self.actionCompress_bzip2 = QtGui.QAction(MainWindow)
        self.actionCompress_bzip2.setEnabled(False)
        icon23 = QtGui.QIcon()
        icon23.addPixmap(QtGui.QPixmap(_fromUtf8(":/usr/share/pfm/resources/application-x-bzip.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionCompress_bzip2.setIcon(icon23)
        self.actionCompress_bzip2.setObjectName(_fromUtf8("actionCompress_bzip2"))
        self.menuMain.addAction(self.actionQuit)
        self.menuNew.addAction(self.actionFile)
        self.menuNew.addAction(self.actionFolder)
        self.menuArchive.addAction(self.actionDecompress)
        self.menuArchive.addAction(self.actionCompress)
        self.menuArchive.addAction(self.actionCompress_bzip2)
        self.menuArchive.addAction(self.actionCompress_xz)
        self.menuActions.addAction(self.actionOpen)
        self.menuActions.addSeparator()
        self.menuActions.addAction(self.actionCut)
        self.menuActions.addAction(self.actionCopy)
        self.menuActions.addAction(self.actionPaste)
        self.menuActions.addAction(self.actionRename)
        self.menuActions.addAction(self.actionDelete)
        self.menuActions.addAction(self.actionProperties)
        self.menuActions.addSeparator()
        self.menuActions.addAction(self.menuNew.menuAction())
        self.menuActions.addAction(self.menuArchive.menuAction())
        self.menuHelp.addAction(self.actionAbout)
        self.menuView.addAction(self.actionIcons)
        self.menuView.addAction(self.actionList)
        self.menuOptions.addAction(self.menuView.menuAction())
        self.menuOptions.addSeparator()
        self.menuOptions.addAction(self.actionPreferences)
        self.menubar.addAction(self.menuMain.menuAction())
        self.menubar.addAction(self.menuActions.menuAction())
        self.menubar.addAction(self.menuOptions.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "File Manager", None))
        self.menuMain.setTitle(_translate("MainWindow", "Main", None))
        self.menuActions.setTitle(_translate("MainWindow", "Actions", None))
        self.menuNew.setTitle(_translate("MainWindow", "New", None))
        self.menuArchive.setTitle(_translate("MainWindow", "Archive", None))
        self.menuHelp.setTitle(_translate("MainWindow", "Help", None))
        self.menuOptions.setTitle(_translate("MainWindow", "Options", None))
        self.menuView.setTitle(_translate("MainWindow", "View", None))
        self.actionQuit.setText(_translate("MainWindow", "Quit", None))
        self.actionQuit.setToolTip(_translate("MainWindow", "Quit application", None))
        self.actionQuit.setShortcut(_translate("MainWindow", "Ctrl+Q", None))
        self.actionTerminal.setText(_translate("MainWindow", "Terminal", None))
        self.actionTerminal.setToolTip(_translate("MainWindow", "Run Terminal", None))
        self.actionTerminal.setShortcut(_translate("MainWindow", "Ctrl+T", None))
        self.actionCopy.setText(_translate("MainWindow", "Copy", None))
        self.actionCopy.setShortcut(_translate("MainWindow", "Ctrl+C", None))
        self.actionPaste.setText(_translate("MainWindow", "Paste", None))
        self.actionPaste.setShortcut(_translate("MainWindow", "Ctrl+V", None))
        self.actionCut.setText(_translate("MainWindow", "Cut", None))
        self.actionCut.setShortcut(_translate("MainWindow", "Ctrl+X", None))
        self.actionAbout.setText(_translate("MainWindow", "About", None))
        self.actionDelete.setText(_translate("MainWindow", "Delete", None))
        self.actionDelete.setShortcut(_translate("MainWindow", "Ctrl+D", None))
        self.actionProperties.setText(_translate("MainWindow", "Properties", None))
        self.actionProperties.setShortcut(_translate("MainWindow", "Ctrl+P", None))
        self.actionCompress.setText(_translate("MainWindow", "Compress (gzip)", None))
        self.actionCompress.setToolTip(_translate("MainWindow", "Compress dirs/files", None))
        self.actionCompress.setShortcut(_translate("MainWindow", "Alt+C", None))
        self.actionDecompress.setText(_translate("MainWindow", "Decompress", None))
        self.actionDecompress.setToolTip(_translate("MainWindow", "Decompress archive", None))
        self.actionDecompress.setShortcut(_translate("MainWindow", "Alt+D", None))
        self.actionIcons.setText(_translate("MainWindow", "Icons", None))
        self.actionList.setText(_translate("MainWindow", "List", None))
        self.actionPreferences.setText(_translate("MainWindow", "Preferences", None))
        self.actionRename.setText(_translate("MainWindow", "Rename", None))
        self.actionMimes.setText(_translate("MainWindow", "Mimes", None))
        self.actionOpen.setText(_translate("MainWindow", "Open", None))
        self.actionFolder.setText(_translate("MainWindow", "Folder", None))
        self.actionFile.setText(_translate("MainWindow", "File", None))
        self.actionAsd.setText(_translate("MainWindow", "asd", None))
        self.actionCompress_xz.setText(_translate("MainWindow", "Compress (xz)", None))
        self.actionCompress_bzip2.setText(_translate("MainWindow", "Compress (bzip2)", None))

import qfile_rc
