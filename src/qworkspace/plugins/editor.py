#!/bin/pyhton2

from PyQt4 import QtCore, QtGui
import os, libmisc, libdesktop, libworkspace, libhighlighter

general = libworkspace.General()
misc = libmisc.Misc()
# app = QtGui.QApplication([])
# actions = libdesktop.Actions(None, app)

class Widget(QtGui.QWidget):
    ''' Tab widget '''
    def __init__(self, parent, spath=None):
        super(Widget, self).__init__()
        self.name = 'editor'
        self.sedit = spath
        self.secondLayout = QtGui.QHBoxLayout()
        self.openButton = QtGui.QPushButton(general.get_icon('text-editor'), '')
        self.openButton.clicked.connect(self.open_file)
        self.openButton.setShortcut(QtGui.QKeySequence('CTRL+O'))
        self.secondLayout.addWidget(self.openButton)
        self.mainLayout = QtGui.QGridLayout()
        self.textEdit = QtGui.QTextEdit()
        self.mainLayout.addLayout(self.secondLayout, 0, 0)
        self.mainLayout.addWidget(self.textEdit)
        self.setLayout(self.mainLayout)

        #self.actionNew.triggered.connect(new_file)
        #self.actionSave.triggered.connect(save_file)
        #self.actionSaveAs.triggered.connect(save_as_file)
        #self.actionReload.triggered.connect(reload_file)
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

    def new_file(self):
        sfile = actions.new_file()
        if sfile:
            self.open_file(sfile)

    def open_file(self, sfile):
        if not sfile:
            sfile = QtGui.QFileDialog.getOpenFileName(None, "Open", \
                QtCore.QDir.currentPath(), "All Files (*);;Text Files (*.txt)")
            if sfile:
                sfile = str(sfile)
                self.textEdit.setText(misc.file_read(sfile))
            else:
                # prevent self.sedit being set to None
                return
        elif os.path.isfile(sfile):
            self.textEdit.setText(misc.file_read(sfile))
        self.sedit = sfile
        # self.actionReload.setEnabled(True)
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
        sfile = QtGui.QFileDialog.getSaveFileName(None, "Save as", \
            QtCore.QDir.currentPath(), "All Files (*);;Text Files (*.txt)")
        if sfile:
            self.sedit = str(sfile)
            self.save_file()

    def find_text(self):
        svar, ok = QtGui.QInputDialog.getText(None, 'Find', '')
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


class Plugin(object):
    ''' Plugin handler '''
    def __init__(self, parent=None):
        self.parent = parent
        self.name = 'editor'
        self.version = '0.0.1'
        self.description = 'Text editor plugin'
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
        self.parent.tabWidget.insertTab(self.index, self.widget, self.icon, 'Editor')
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