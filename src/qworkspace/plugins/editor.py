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
        self.secondLayout = QtGui.QHBoxLayout()
        self.openButton = QtGui.QPushButton(general.get_icon('fileopen'), '')
        self.openButton.clicked.connect(self.open_file)
        self.openButton.setShortcut(QtGui.QKeySequence(self.tr('CTRL+O')))
        self.saveButton = QtGui.QPushButton(general.get_icon('filesave'), '')
        self.saveButton.clicked.connect(self.save_file)
        self.saveButton.setShortcut(QtGui.QKeySequence(self.tr('CTRL+S')))
        self.saveButton.setEnabled(False)
        self.saveAsButton = QtGui.QPushButton(general.get_icon('filesaveas'), '')
        self.saveAsButton.clicked.connect(self.save_as_file)
        self.saveAsButton.setEnabled(False)
        self.reloadButton = QtGui.QPushButton(general.get_icon('reload'), '')
        self.reloadButton.clicked.connect(self.reload_file)
        self.reloadButton.setShortcut(QtGui.QKeySequence(self.tr('CTRL+R')))
        self.reloadButton.setEnabled(False)
        self.secondLayout.addWidget(self.openButton)
        self.secondLayout.addWidget(self.saveButton)
        self.secondLayout.addWidget(self.saveAsButton)
        self.secondLayout.addWidget(self.reloadButton)
        self.mainLayout = QtGui.QGridLayout()
        self.textEdit = QtGui.QTextEdit()
        self.mainLayout.addLayout(self.secondLayout, 0, 0)
        self.mainLayout.addWidget(self.textEdit)
        self.setLayout(self.mainLayout)

        #self.actionFind.triggered.connect(find)
        #self.actionUndo.triggered.connect(ui.textEdit.undo)
        #self.actionRedo.triggered.connect(ui.textEdit.redo)
        #self.actionFont.triggered.connect(set_font)
        #self.actionPlain.triggered.connect(highlight_plain)
        #self.actionPython.triggered.connect(highlight_python)
        #self.actionShell.triggered.connect(highlight_shell)
        #self.actionC.triggered.connect(highlight_c)
        if self.sedit:
            self.open_file(self.sedit)

    def open_file(self, sfile):
        if not sfile:
            sfile = QtGui.QFileDialog.getOpenFileName(self, self.tr('Open'), \
                QtCore.QDir.currentPath(), self.tr('All Files (*);;Text Files (*.txt)'))
            if sfile:
                sfile = str(sfile)
                self.textEdit.setText(misc.file_read(sfile))
            else:
                # prevent self.sedit being set to None
                return
        elif os.path.isfile(sfile):
            self.textEdit.setText(misc.file_read(sfile))
        self.sedit = sfile
        self.reloadButton.setEnabled(True)
        self.saveButton.setEnabled(True)
        self.saveAsButton.setEnabled(True)
        smime = misc.file_mime(sfile)
        if smime == 'text/x-python':
            self.highlight_python()
        elif smime == 'text/x-shellscript':
            self.highlight_shell()
        elif smime == 'text/x-c':
            self.highlight_c()
        else:
            self.highlight_plain()

    def save_file(self):
        if self.sedit:
            misc.file_write(os.path.realpath(self.sedit), self.textEdit.toPlainText())

    def save_as_file(self):
        sfile = QtGui.QFileDialog.getSaveFileName(self, self.tr('Save as'), \
            QtCore.QDir.currentPath(), self.tr('All Files (*);;Text Files (*.txt)'))
        if sfile:
            self.sedit = str(sfile)
            self.save_file()

    def find_text(self):
        svar, ok = QtGui.QInputDialog.getText(self, self.tr('Find'), '')
        if ok and svar:
            self.textEdit.find(svar)

    def reload_file(self):
        self.open_file(self.sedit)

    def set_font(self):
        font, ok = QtGui.QFontDialog.getFont(QtGui.QFont(self.textEdit.font))
        if ok:
            self.textEdit.setFont(font)

    def highlight_plain(self):
        try:
            self.highlighter.setDocument(None)
        except AttributeError:
            pass

    def highlight_python(self):
        self.highlighter = libhighlighter.HighlighterPython(self.textEdit.document())

    def highlight_shell(self):
        self.highlighter = libhighlighter.HighlighterShell(self.textEdit.document())

    def highlight_c(self):
        self.highlighter = libhighlighter.HighlighterC(self.textEdit.document())


class Plugin(QtCore.QObject):
    ''' Plugin handler '''
    def __init__(self, parent=None):
        super(Plugin, self).__init__()
        self.parent = parent
        self.name = 'editor'
        self.version = '0.0.1'
        self.description = self.tr('Text editor plugin')
        self.icon = general.get_icon('text-editor')
        self.widget = None

        self.editorButton = QtGui.QPushButton(self.icon, '')
        self.editorButton.clicked.connect(lambda: self.open(None))
        self.applicationsLayout = self.parent.toolBox.widget(1).layout()
        self.applicationsLayout.addWidget(self.editorButton)

        # FIXME: register MIMEs

    def open(self, spath):
        ''' Open path in new tab '''
        self.widget = Widget(self.parent, spath)
        self.index = self.parent.tabWidget.currentIndex()+1
        self.parent.tabWidget.insertTab(self.index, self.widget, self.icon, self.tr('Editor'))
        self.parent.tabWidget.setCurrentIndex(self.index)

    def close(self):
        ''' Close tab '''
        if self.widget:
            self.widget.destroy()
            self.parent.tabWidget.removeTab(self.index)

    def unload(self):
        ''' Unload plugin '''
        self.applicationsLayout.removeWidget(self.editorButton)
        self.close()
