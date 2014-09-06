#!/bin/pyhton2

from PyQt4 import QtCore, QtGui
import smtplib, libworkspace
general = libworkspace.General()

class Widget(QtGui.QWidget):
    ''' Tab widget '''
    def __init__(self, parent, spath=None):
        super(Widget, self).__init__()
        self.parent = parent
        self.spath = spath
        self.name = 'mail'

        self.mainLayout = QtGui.QGridLayout()
        self.serverEdit = QtGui.QLineEdit()
        self.serverEdit.setToolTip('Server')
        self.serverEdit.setPlaceholderText('Server')
        self.portBox = QtGui.QSpinBox()
        self.portBox.setToolTip('Port')
        self.loginEdit = QtGui.QLineEdit()
        self.loginEdit.setToolTip('Login')
        self.loginEdit.setPlaceholderText('Login')
        self.passwordEdit = QtGui.QLineEdit()
        self.passwordEdit.setEchoMode(QtGui.QLineEdit.Password)
        self.passwordEdit.setToolTip('Password')
        self.passwordEdit.setPlaceholderText('Password')
        self.receiverEdit = QtGui.QLineEdit()
        self.receiverEdit.setToolTip('Receiver')
        self.receiverEdit.setPlaceholderText('Receiver')
        self.subjectEdit = QtGui.QLineEdit()
        self.subjectEdit.setToolTip('Subject')
        self.subjectEdit.setPlaceholderText('Subject')
        self.sendButton = QtGui.QPushButton(general.get_icon('mail-reply-sender'), '')
        self.sendButton.setToolTip('Send mail')
        self.sendButton.clicked.connect(self.mail_send)
        self.messageEdit = QtGui.QTextEdit()
        self.messageEdit.setToolTip('Message')
        self.mainLayout.addWidget(self.serverEdit)
        self.mainLayout.addWidget(self.portBox)
        self.mainLayout.addWidget(self.loginEdit)
        self.mainLayout.addWidget(self.passwordEdit)
        self.mainLayout.addWidget(self.receiverEdit)
        self.mainLayout.addWidget(self.subjectEdit)
        self.mainLayout.addWidget(self.sendButton)
        self.mainLayout.addWidget(self.messageEdit)
        self.setLayout(self.mainLayout)

        if self.spath:
            self.receiverEdit.setText(self.spath)

    def mail_send(self):
        if not self.serverEdit.text():
            QtGui.QMessageBox.critical(self, self.tr('Critical'), \
                self.tr('No server entered'))
            return
        elif not self.loginEdit.text():
            QtGui.QMessageBox.critical(self, self.tr('Critical'), \
                self.tr('No login entered'))
            return
        elif not self.passwordEdit.text():
            QtGui.QMessageBox.critical(self, self.tr('Critical'), \
                self.tr('No password entered'))
            return
        elif not self.subjectEdit.text():
            QtGui.QMessageBox.critical(self, self.tr('Critical'), \
                self.tr('No subject entered'))
            return
        elif not self.receiverEdit.text():
            QtGui.QMessageBox.critical(self, self.tr('Critical'), \
                self.tr('No receiver entered'))
            return
        elif not self.messageEdit.toPlainText():
            QtGui.QMessageBox.critical(self, self.tr('Critical'), \
                self.tr('No message entered'))
            return
        try:
            handle = smtplib.SMTP(self.serverEdit.text(), self.portBox.value())
            handle.login(self.loginEdit.text(), self.passwordEdit.text())
            msg = 'To:' + self.receiverEdit.text() + '\r\nFrom:' + self.loginEdit.text() + \
                '\r\nSubject:' + self.subjectEdit.text() + '\r\n' + self.messageEdit.toPlainText()
            handle.sendmail(self.loginEdit.text(), self.receiverEdit.text(), msg)
            handle.close()
        except Exception as detail:
            self.parent.plugins.notify_critical(str(detail))

class Plugin(QtCore.QObject):
    ''' Plugin handler '''
    def __init__(self, parent):
        super(Plugin, self).__init__()
        self.parent = parent
        self.name = 'mail'
        self.version = "0.9.37 (1db7d9d)"
        self.description = self.tr('Mail manager plugin')
        self.icon = general.get_icon('internet-mail')
        self.widget = None

        self.mailButton = QtGui.QPushButton(self.icon, '')
        self.mailButton.setToolTip(self.description)
        self.mailButton.clicked.connect(lambda: self.open(None))
        self.applicationsLayout = self.parent.toolBox.widget(1).layout()
        self.applicationsLayout.addWidget(self.mailButton)

    def open(self, spath):
        ''' Open path in new tab '''
        index = self.parent.tabWidget.currentIndex()+1
        self.widget = Widget(self.parent, spath)
        self.parent.tabWidget.insertTab(index, self.widget, self.icon, self.tr('Mail'))
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
        self.applicationsLayout.removeWidget(self.mailButton)
        self.close()
