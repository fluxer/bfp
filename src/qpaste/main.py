#!/bin/python2

import qpaste_ui
from PyQt4 import QtGui
import sys, os, shutil
import libmisc, libdesktop

# prepare for lift-off
app = QtGui.QApplication(sys.argv)
Dialog = QtGui.QDialog()
ui = qpaste_ui.Ui_Dialog()
ui.setupUi(Dialog)

# FIXME: need 4 on cut/paste
if len(sys.argv) < 3:
    QtGui.QMessageBox.critical(Dialog, 'Critical', 'Not enough arguments')
    sys.exit(2)

config = libdesktop.Config()
actions = libdesktop.Actions(Dialog, app)
general = libdesktop.General()
misc = libmisc.Misc()

def setLook():
    general.set_style(app)
setLook()

Dialog.show()
ui.cancelButton.clicked.connect(sys.exit)

action = sys.argv[1]
if action == '--copy':
    try:
        items = sys.argv[2:]
        step = 100/len(items)
        cur_dir = os.path.realpath(os.curdir)
        for svar in items:
            svar = str(svar)
            svar_basename = os.path.basename(svar)
            if os.path.exists(cur_dir + '/' + svar_basename):
                svar_basename = actions.check_exists(cur_dir + '/' + svar_basename)
                if not svar_basename:
                    continue
            svar_copy = cur_dir + '/' + svar_basename
            ui.TextLabel.setText('Copying: <b>' + svar + '</b> To: <b>' + svar_copy + '</b>')
            if os.path.isdir(svar):
                shutil.copytree(svar, svar_copy)
            else:
                shutil.copy2(svar, svar_copy)
            ui.ProgressBar.setValue(step)
            step = step + step
    except Exception as detail:
        QtGui.QMessageBox.critical(Dialog, 'Critical', str(detail))
        sys.exit(2)
    finally:
        sys.exit(0)
elif action == '--cut':
    try:
        items = sys.argv[2:]
        cur_dir = os.path.realpath(os.curdir)
        step = 100/len(items)
        for svar in items:
            svar = str(svar)
            svar_basename = os.path.basename(svar)
            if os.path.exists(cur_dir + '/' + svar_basename):
                svar_basename = actions.check_exists(cur_dir + '/' + svar_basename)
                if not svar_basename:
                    continue
            svar_copy = cur_dir + '/' + svar_basename
            ui.TextLabel.setText('Moving: <b>' + svar + '</b> To: <b>' + svar_copy + '</b>')
            os.rename(svar, svar_copy)
            ui.ProgressBar.setValue(step)
            step = step + step
    except Exception as detail:
        QtGui.QMessageBox.critical(Dialog, 'Critical', str(detail))
        sys.exit(2)
    finally:
        sys.exit(0)
elif action == '--delete':
    try:
        items = sys.argv[2:]
        ask = True
        step = 100/len(items)
        if step < 100:
            qbuttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.YesToAll | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel
        else:
            qbuttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel
        for svar in items:
            if ask:
                reply = QtGui.QMessageBox.question(Dialog, 'Question', \
                    'Are you sure you want to delete <b>' + svar + '</b>?', qbuttons)
                if reply == QtGui.QMessageBox.Yes:
                    pass
                elif reply == QtGui.QMessageBox.No:
                    continue
                elif reply == QtGui.QMessageBox.YesToAll:
                    ask = False
                else:
                    break
            ui.TextLabel.setText('Removing: <b>' + svar + '</b>')
            if os.path.isdir(svar):
                misc.dir_remove(svar)
            else:
                os.unlink(svar)
            ui.ProgressBar.setValue(step)
            step = step + step
    except Exception as detail:
        QtGui.QMessageBox.critical(Dialog, 'Critical', str(detail))
        sys.exit(2)
    finally:
        sys.exit(0)
elif action == '--rename':
    try:
        items = sys.argv[2:]
        step = 100/len(items)
        for svar in items:
            svar_basename = os.path.basename(svar)
            svar_dirname = os.path.dirname(svar)

            svar_new, ok = QtGui.QInputDialog.getText(Dialog, 'Move', \
                'New name:', QtGui.QLineEdit.Normal, svar_basename)
            if ok and svar_new:
                pass
            else:
                break

            svar_new = str(svar_new)
            if os.path.exists(svar_dirname + '/' + svar_new):
                svar_new = actions.check_exists(svar_dirname + '/' + svar_new)
                if not svar_new:
                    break
            new_name = os.path.join(svar_dirname, str(svar_new))
            ui.TextLabel.setText('Renaming: <b>' + svar + '</b> To: <b>' + new_name + '</b>')
            os.rename(svar, new_name)
            ui.ProgressBar.setValue(step)
            step = step + step
    except Exception as detail:
        QtGui.QMessageBox.critical(Dialog, 'Critical', str(detail))
        sys.exit(2)
    finally:
        sys.exit(0)
else:
    QtGui.QMessageBox.critical(Dialog, 'Critical', 'Invalid action, choose from cut/copy/rename/delete.')
    sys.exit(3)

sys.exit(app.exec_())
