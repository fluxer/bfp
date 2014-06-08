# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt.ui'
#
# Created: Sun Jun  8 21:49:59 2014
#      by: PyQt4 UI code generator 4.10.4
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
        MainWindow.resize(376, 341)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("system-software-update"))
        MainWindow.setWindowIcon(icon)
        MainWindow.setLocale(QtCore.QLocale(QtCore.QLocale.C, QtCore.QLocale.AnyCountry))
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 381, 351))
        self.tabWidget.setLocale(QtCore.QLocale(QtCore.QLocale.C, QtCore.QLocale.AnyCountry))
        self.tabWidget.setTabShape(QtGui.QTabWidget.Rounded)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.RemoveButton = QtGui.QPushButton(self.tab)
        self.RemoveButton.setEnabled(False)
        self.RemoveButton.setGeometry(QtCore.QRect(270, 70, 85, 27))
        self.RemoveButton.setObjectName(_fromUtf8("RemoveButton"))
        self.BuildButton = QtGui.QPushButton(self.tab)
        self.BuildButton.setEnabled(True)
        self.BuildButton.setGeometry(QtCore.QRect(270, 40, 85, 27))
        self.BuildButton.setObjectName(_fromUtf8("BuildButton"))
        self.TargetsList = QtGui.QListWidget(self.tab)
        self.TargetsList.setGeometry(QtCore.QRect(10, 10, 251, 141))
        self.TargetsList.setObjectName(_fromUtf8("TargetsList"))
        self.UpdateButton = QtGui.QPushButton(self.tab)
        self.UpdateButton.setEnabled(True)
        self.UpdateButton.setGeometry(QtCore.QRect(270, 10, 85, 27))
        self.UpdateButton.setObjectName(_fromUtf8("UpdateButton"))
        self.AliasesList = QtGui.QListWidget(self.tab)
        self.AliasesList.setGeometry(QtCore.QRect(275, 111, 81, 191))
        self.AliasesList.setObjectName(_fromUtf8("AliasesList"))
        self.tabWidget_2 = QtGui.QTabWidget(self.tab)
        self.tabWidget_2.setGeometry(QtCore.QRect(10, 160, 251, 141))
        self.tabWidget_2.setObjectName(_fromUtf8("tabWidget_2"))
        self.tab_8 = QtGui.QWidget()
        self.tab_8.setObjectName(_fromUtf8("tab_8"))
        self.MetadataText = QtGui.QTextEdit(self.tab_8)
        self.MetadataText.setGeometry(QtCore.QRect(10, 10, 231, 91))
        self.MetadataText.setReadOnly(True)
        self.MetadataText.setObjectName(_fromUtf8("MetadataText"))
        self.tabWidget_2.addTab(self.tab_8, _fromUtf8(""))
        self.tab_7 = QtGui.QWidget()
        self.tab_7.setObjectName(_fromUtf8("tab_7"))
        self.FootprintText = QtGui.QTextEdit(self.tab_7)
        self.FootprintText.setGeometry(QtCore.QRect(0, 0, 241, 121))
        self.FootprintText.setReadOnly(True)
        self.FootprintText.setObjectName(_fromUtf8("FootprintText"))
        self.tabWidget_2.addTab(self.tab_7, _fromUtf8(""))
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.OutputText = QtGui.QTextEdit(self.tab_2)
        self.OutputText.setGeometry(QtCore.QRect(10, 10, 351, 291))
        self.OutputText.setReadOnly(True)
        self.OutputText.setObjectName(_fromUtf8("OutputText"))
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName(_fromUtf8("tab_3"))
        self.CacheDirEdit = QtGui.QLineEdit(self.tab_3)
        self.CacheDirEdit.setGeometry(QtCore.QRect(10, 30, 161, 22))
        self.CacheDirEdit.setObjectName(_fromUtf8("CacheDirEdit"))
        self.BuildDirEdit = QtGui.QLineEdit(self.tab_3)
        self.BuildDirEdit.setGeometry(QtCore.QRect(10, 80, 161, 22))
        self.BuildDirEdit.setObjectName(_fromUtf8("BuildDirEdit"))
        self.label = QtGui.QLabel(self.tab_3)
        self.label.setGeometry(QtCore.QRect(10, 10, 161, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(self.tab_3)
        self.label_2.setGeometry(QtCore.QRect(10, 60, 161, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.IgnoreTargetsEdit = QtGui.QLineEdit(self.tab_3)
        self.IgnoreTargetsEdit.setGeometry(QtCore.QRect(10, 130, 161, 22))
        self.IgnoreTargetsEdit.setText(_fromUtf8(""))
        self.IgnoreTargetsEdit.setObjectName(_fromUtf8("IgnoreTargetsEdit"))
        self.label_4 = QtGui.QLabel(self.tab_3)
        self.label_4.setGeometry(QtCore.QRect(10, 110, 161, 16))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.ConnectionTimeoutBox = QtGui.QSpinBox(self.tab_3)
        self.ConnectionTimeoutBox.setGeometry(QtCore.QRect(10, 180, 161, 22))
        self.ConnectionTimeoutBox.setObjectName(_fromUtf8("ConnectionTimeoutBox"))
        self.label_5 = QtGui.QLabel(self.tab_3)
        self.label_5.setGeometry(QtCore.QRect(10, 160, 161, 16))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.StripSharedBox = QtGui.QCheckBox(self.tab_3)
        self.StripSharedBox.setGeometry(QtCore.QRect(190, 10, 161, 19))
        self.StripSharedBox.setTristate(False)
        self.StripSharedBox.setObjectName(_fromUtf8("StripSharedBox"))
        self.StripStaticBox = QtGui.QCheckBox(self.tab_3)
        self.StripStaticBox.setGeometry(QtCore.QRect(190, 30, 161, 19))
        self.StripStaticBox.setObjectName(_fromUtf8("StripStaticBox"))
        self.IgnoreMissingBox = QtGui.QCheckBox(self.tab_3)
        self.IgnoreMissingBox.setGeometry(QtCore.QRect(190, 50, 161, 19))
        self.IgnoreMissingBox.setObjectName(_fromUtf8("IgnoreMissingBox"))
        self.ConflictsBox = QtGui.QCheckBox(self.tab_3)
        self.ConflictsBox.setGeometry(QtCore.QRect(190, 70, 161, 19))
        self.ConflictsBox.setObjectName(_fromUtf8("ConflictsBox"))
        self.BackupBox = QtGui.QCheckBox(self.tab_3)
        self.BackupBox.setGeometry(QtCore.QRect(190, 90, 161, 19))
        self.BackupBox.setObjectName(_fromUtf8("BackupBox"))
        self.ScriptsBox = QtGui.QCheckBox(self.tab_3)
        self.ScriptsBox.setGeometry(QtCore.QRect(190, 110, 161, 19))
        self.ScriptsBox.setObjectName(_fromUtf8("ScriptsBox"))
        self.ExternalFetcherBox = QtGui.QCheckBox(self.tab_3)
        self.ExternalFetcherBox.setGeometry(QtCore.QRect(190, 150, 161, 19))
        self.ExternalFetcherBox.setObjectName(_fromUtf8("ExternalFetcherBox"))
        self.UseMirrorsBox = QtGui.QCheckBox(self.tab_3)
        self.UseMirrorsBox.setGeometry(QtCore.QRect(190, 130, 161, 19))
        self.UseMirrorsBox.setObjectName(_fromUtf8("UseMirrorsBox"))
        self.StripBinariesBox = QtGui.QCheckBox(self.tab_3)
        self.StripBinariesBox.setGeometry(QtCore.QRect(190, 190, 161, 19))
        self.StripBinariesBox.setObjectName(_fromUtf8("StripBinariesBox"))
        self.CompressManBox = QtGui.QCheckBox(self.tab_3)
        self.CompressManBox.setGeometry(QtCore.QRect(190, 170, 161, 19))
        self.CompressManBox.setObjectName(_fromUtf8("CompressManBox"))
        self.tabWidget.addTab(self.tab_3, _fromUtf8(""))
        self.tab_4 = QtGui.QWidget()
        self.tab_4.setObjectName(_fromUtf8("tab_4"))
        self.SyncRepoButton = QtGui.QPushButton(self.tab_4)
        self.SyncRepoButton.setGeometry(QtCore.QRect(140, 280, 85, 27))
        self.SyncRepoButton.setObjectName(_fromUtf8("SyncRepoButton"))
        self.ReposEdit = QtGui.QTextEdit(self.tab_4)
        self.ReposEdit.setGeometry(QtCore.QRect(10, 10, 351, 261))
        self.ReposEdit.setObjectName(_fromUtf8("ReposEdit"))
        self.tabWidget.addTab(self.tab_4, _fromUtf8(""))
        self.tab_5 = QtGui.QWidget()
        self.tab_5.setObjectName(_fromUtf8("tab_5"))
        self.MirrorsEdit = QtGui.QTextEdit(self.tab_5)
        self.MirrorsEdit.setGeometry(QtCore.QRect(10, 10, 351, 291))
        self.MirrorsEdit.setObjectName(_fromUtf8("MirrorsEdit"))
        self.tabWidget.addTab(self.tab_5, _fromUtf8(""))
        self.tab_6 = QtGui.QWidget()
        self.tab_6.setObjectName(_fromUtf8("tab_6"))
        self.AboutText = QtGui.QPlainTextEdit(self.tab_6)
        self.AboutText.setGeometry(QtCore.QRect(10, 40, 351, 261))
        self.AboutText.setReadOnly(True)
        self.AboutText.setObjectName(_fromUtf8("AboutText"))
        self.AboutLabel = QtGui.QLabel(self.tab_6)
        self.AboutLabel.setGeometry(QtCore.QRect(10, 10, 351, 16))
        self.AboutLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.AboutLabel.setObjectName(_fromUtf8("AboutLabel"))
        self.tabWidget.addTab(self.tab_6, _fromUtf8(""))
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        self.tabWidget_2.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Source Package Manager Qt GUI", None))
        self.RemoveButton.setText(_translate("MainWindow", "Remove", None))
        self.BuildButton.setText(_translate("MainWindow", "Build", None))
        self.UpdateButton.setText(_translate("MainWindow", "Update", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_8), _translate("MainWindow", "Metadata", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_7), _translate("MainWindow", "Footprint", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Targets", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Log", None))
        self.label.setText(_translate("MainWindow", "Cache directory", None))
        self.label_2.setText(_translate("MainWindow", "Build directory", None))
        self.label_4.setText(_translate("MainWindow", "Ignore targets", None))
        self.label_5.setText(_translate("MainWindow", "Connection timeout", None))
        self.StripSharedBox.setText(_translate("MainWindow", "Strip shared", None))
        self.StripStaticBox.setText(_translate("MainWindow", "Strip static", None))
        self.IgnoreMissingBox.setText(_translate("MainWindow", "Ignore missing", None))
        self.ConflictsBox.setText(_translate("MainWindow", "Check for conflicts", None))
        self.BackupBox.setText(_translate("MainWindow", "Backup files", None))
        self.ScriptsBox.setText(_translate("MainWindow", "Execute scripts", None))
        self.ExternalFetcherBox.setText(_translate("MainWindow", "External fetcher", None))
        self.UseMirrorsBox.setText(_translate("MainWindow", "Use mirrors", None))
        self.StripBinariesBox.setText(_translate("MainWindow", "Strip binaries", None))
        self.CompressManBox.setText(_translate("MainWindow", "Compress manuals", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("MainWindow", "Settings", None))
        self.SyncRepoButton.setText(_translate("MainWindow", "Sync", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), _translate("MainWindow", "Repositories", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), _translate("MainWindow", "Mirrors", None))
        self.AboutText.setPlainText(_translate("MainWindow", "Source Package Manager Qt frontend\n"
"Copyright (C) 2013-2014 Ivailo Monev <xakepa10@gmail.com>\n"
"\n"
"This program is free software; you can redistribute\n"
"it and/or modify it under the terms of the GNU\n"
"General Public License as published by the Free\n"
"Software Foundation; either version 2 of the License,\n"
"or (at your option) any later version.\n"
"\n"
"This program is distributed in the hope that it will\n"
"be useful, but WITHOUT ANY WARRANTY; without even the\n"
"implied warranty of MERCHANTABILITY or FITNESS FOR A\n"
"PARTICULAR PURPOSE. See the GNU General Public\n"
"License for more details.\n"
"\n"
"You should have received a copy of the GNU General\n"
"Public License along with this program; if not, write\n"
"to the Free Software Foundation, Inc., 59 Temple Place,\n"
"Suite 330, Boston, MA 02111-1307 USA", None))
        self.AboutLabel.setText(_translate("MainWindow", "Source Package Manager Qt frontend v1.2", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_6), _translate("MainWindow", "About", None))

