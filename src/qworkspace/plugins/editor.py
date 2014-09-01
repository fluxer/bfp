#!/bin/pyhton2

from PyQt4 import QtCore, QtGui
import os, libmisc, libworkspace, libhighlighter
general = libworkspace.General()
misc = libmisc.Misc()


class Widget(QtGui.QWidget):
    ''' Tab widget '''
    def __init__(self, parent, spath=None):
        super(Widget, self).__init__()
        self.parent = parent
        self.name = 'editor'
        self.sedit = spath

        self.printer = QtGui.QPrinter()
        self.secondLayout = QtGui.QHBoxLayout()
        self.openButton = QtGui.QPushButton(general.get_icon('document-open'), '')
        self.openButton.setToolTip(self.tr('Open file'))
        self.openButton.clicked.connect(self.open_file)
        self.openButton.setShortcut(QtGui.QKeySequence(self.tr('CTRL+O')))
        self.saveButton = QtGui.QPushButton(general.get_icon('document-save'), '')
        self.saveButton.setToolTip(self.tr('Save file'))
        self.saveButton.clicked.connect(self.save_file)
        self.saveButton.setShortcut(QtGui.QKeySequence(self.tr('CTRL+S')))
        self.saveButton.setEnabled(False)
        self.saveAsButton = QtGui.QPushButton(general.get_icon('document-save-as'), '')
        self.saveAsButton.setToolTip(self.tr('Save file as'))
        self.saveAsButton.clicked.connect(self.save_as_file)
        self.reloadButton = QtGui.QPushButton(general.get_icon('view-refresh'), '')
        self.reloadButton.setToolTip(self.tr('Reload currently loaded file'))
        self.reloadButton.clicked.connect(self.reload_file)
        self.reloadButton.setShortcut(QtGui.QKeySequence(self.tr('CTRL+R')))
        self.reloadButton.setEnabled(False)
        self.findButton = QtGui.QPushButton(general.get_icon('edit-find'), '')
        self.findButton.setToolTip(self.tr('Find text in currently loaded file'))
        self.findButton.clicked.connect(self.find_text)
        self.findButton.setShortcut(QtGui.QKeySequence(self.tr('CTRL+F')))
        self.findButton.setEnabled(False)
        self.fontButton = QtGui.QPushButton(general.get_icon('applications-fonts'), '')
        self.fontButton.setToolTip(self.tr('Change font in use'))
        self.fontButton.clicked.connect(self.set_font)
        self.fontButton.setShortcut(QtGui.QKeySequence(self.tr('CTRL+N')))
        self.printButton = QtGui.QPushButton(general.get_icon('document-print'), '')
        self.printButton.setToolTip(self.tr('Print text'))
        self.printButton.clicked.connect(self.print_text)
        self.printButton.setShortcut(QtGui.QKeySequence(self.tr('CTRL+P')))
        self.printButton.setEnabled(False)
        self.previewButton = QtGui.QPushButton(general.get_icon('document-print-preview'), '')
        self.previewButton.setToolTip(self.tr('Preview print'))
        self.previewButton.clicked.connect(self.print_preview)
        self.previewButton.setShortcut(QtGui.QKeySequence(self.tr('CTRL+H')))
        self.previewButton.setEnabled(False)
        self.highlighterBox = QtGui.QComboBox()
        self.highlighterBox.addItems(('None', 'Python', 'Shell', 'C'))
        self.highlighterBox.setToolTip(self.tr('Set syntax highlighter'))
        self.highlighterBox.currentIndexChanged.connect(self.set_highlighter)
        self.secondLayout.addWidget(self.openButton)
        self.secondLayout.addWidget(self.saveButton)
        self.secondLayout.addWidget(self.saveAsButton)
        self.secondLayout.addWidget(self.reloadButton)
        self.secondLayout.addWidget(self.findButton)
        self.secondLayout.addWidget(self.fontButton)
        self.secondLayout.addWidget(self.highlighterBox)
        self.secondLayout.addWidget(self.printButton)
        self.secondLayout.addWidget(self.previewButton)
        self.mainLayout = QtGui.QGridLayout()
        self.textEdit = QtGui.QTextEdit()
        self.mainLayout.addLayout(self.secondLayout, 0, 0)
        self.mainLayout.addWidget(self.textEdit)
        self.setLayout(self.mainLayout)

        if self.sedit:
            self.open_file(self.sedit)

    def open_file(self, sfile):
        sdir = QtCore.QDir.currentPath()
        if self.sedit and os.path.exists(self.sedit):
            sdirname = os.path.dirname(self.sedit)
            if os.path.isdir(sdirname):
                sdir = sdirname

        if not sfile:
            sfile = QtGui.QFileDialog.getOpenFileName(self, self.tr('Open'), \
                sdir, \
                self.tr('Text (*.txt *.sh *.bash *.diff *.patch *.py *c *.h *.cpp *.hpp *.html *.pl);;All (*)'))
            if sfile:
                sfile = str(sfile)
                self.textEdit.setText(misc.file_read(sfile))
            else:
                # prevent self.sedit being set to None
                return
        elif os.path.isfile(sfile):
            self.textEdit.setText(misc.file_read(sfile))
        self.sedit = sfile
        self.saveButton.setEnabled(True)
        self.reloadButton.setEnabled(True)
        self.findButton.setEnabled(True)
        self.printButton.setEnabled(True)
        self.previewButton.setEnabled(True)
        smime = misc.file_mime(sfile)
        if smime == 'text/x-python':
            shighlither = 'Python'
        elif smime == 'text/x-shellscript':
            shighlither = 'Shell'
        elif smime == 'text/x-c':
            shighlither = 'C'
        else:
            shighlither = 'None'
        index = self.highlighterBox.findText(shighlither)
        self.highlighterBox.setCurrentIndex(index)
        self.parent.plugins.recent_register(sfile)

    def save_file(self):
        if self.sedit:
            misc.file_write(os.path.realpath(self.sedit), self.textEdit.toPlainText())

    def save_as_file(self):
        sfile = QtGui.QFileDialog.getSaveFileName(self, self.tr('Save as'), \
            QtCore.QDir.currentPath(), \
            self.tr('Text (*.txt *.sh *.bash *.diff *.patch *.py *c *.h *.cpp *.hpp *.html *.pl);;All (*)'))
        if sfile:
            self.sedit = str(sfile)
            self.save_file()
            self.saveButton.setEnabled(True)
            self.reloadButton.setEnabled(True)
            self.findButton.setEnabled(True)

    def reload_file(self):
        self.open_file(self.sedit)

    def find_text(self):
        svar, ok = QtGui.QInputDialog.getText(self, self.tr('Find'), '')
        if ok and svar:
            self.textEdit.find(svar)

    def set_font(self):
        font, ok = QtGui.QFontDialog.getFont(QtGui.QFont(self.textEdit.font), self)
        if ok:
            self.textEdit.setFont(font)

    def set_highlighter(self):
        shighlither = str(self.highlighterBox.currentText())
        if shighlither == 'None':
            try:
                self.highlighter.setDocument(None)
            except AttributeError:
                pass
        elif shighlither == 'Python':
            self.highlighter = libhighlighter.HighlighterPython(self.textEdit.document())
        elif shighlither == 'Shell':
            self.highlighter = libhighlighter.HighlighterShell(self.textEdit.document())
        elif shighlither == 'C':
            self.highlighter = libhighlighter.HighlighterC(self.textEdit.document())

    def print_text(self):
        dialog = QtGui.QPrintDialog(self.printer, self)
        if dialog.exec_() == QtGui.QDialog.Accepted:
            self.textEdit.document().print_(dialog.printer())

    def print_preview(self):
        dialog = QtGui.QPrintPreviewDialog(self.printer, self)
        dialog.paintRequested.connect(self.textEdit.print_)
        dialog.exec_()


class Plugin(QtCore.QObject):
    ''' Plugin handler '''
    def __init__(self, parent=None):
        super(Plugin, self).__init__()
        self.parent = parent
        self.name = 'editor'
        self.version = "0.9.36 (9197ba8)"
        self.description = self.tr('Text editor plugin')
        self.icon = general.get_icon('accessories-text-editor')
        self.widget = None

        self.editorButton = QtGui.QPushButton(self.icon, '')
        self.editorButton.setToolTip(self.description)
        self.editorButton.clicked.connect(lambda: self.open(None))
        self.applicationsLayout = self.parent.toolBox.widget(1).layout()
        self.applicationsLayout.addWidget(self.editorButton)

        self.parent.plugins.mime_register('text/plain', self.name)
        self.parent.plugins.mime_register('text/x-shellscript', self.name)
        self.parent.plugins.mime_register('text/x-perl', self.name)
        self.parent.plugins.mime_register('text/x-diff', self.name)
        self.parent.plugins.mime_register('text/x-makefile', self.name)
        self.parent.plugins.mime_register('text/x-awk', self.name)
        self.parent.plugins.mime_register('text/x-pascal', self.name)
        self.parent.plugins.mime_register('text/x-python', self.name)
        self.parent.plugins.mime_register('text/x-c', self.name)
        self.parent.plugins.mime_register('text/x-c++', self.name)
        self.parent.plugins.mime_register('text/html', self.name)
        self.parent.plugins.mime_register('inode/x-empty', self.name)

    def open(self, spath):
        ''' Open path in new tab '''
        index = self.parent.tabWidget.currentIndex()+1
        self.widget = Widget(self.parent, spath)
        self.parent.tabWidget.insertTab(index, self.widget, self.icon, \
            self.tr('Editor'))
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
        self.applicationsLayout.removeWidget(self.editorButton)
        self.close()
