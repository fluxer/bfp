#!/usr/bin/python

import qpaste_ui
from PyQt4 import QtGui
import sys, os, shutil
import libqdesktop
import libmisc
misc = libmisc.Misc()

# prepare for lift-off
app = QtGui.QApplication(sys.argv)
Dialog = QtGui.QDialog()
ui = qpaste_ui.Ui_Dialog()
ui.setupUi(Dialog)

# FIXME: need 4 on cut/paste
if len(sys.argv) < 3:
    print('Not enough arguments')
    sys.exit(2)

config = libqdesktop.Config()
actions = libqdesktop.Actions(Dialog, app)
icon = QtGui.QIcon()

def setLook():
    config.read()
    if config.GENERAL_STYLESHEET:
        Dialog.setStyle(config.GENERAL_STYLESHEET)
    else:
        Dialog.setStyleSheet('')
    icon.setThemeName(config.GENERAL_ICONTHEME)
    import qdarkstyle
    Dialog.setStyleSheet(qdarkstyle.load_stylesheet(pyside=False))
setLook()

Dialog.show()
ui.cancelButton.clicked.connect(sys.exit)

action = sys.argv[1]
if action == '--copy':
    try:
        items = sys.argv[2:]
        step = 100/len(items)
        print ('Initial', step, len(items))
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
            print ('Copy', step)
            ui.ProgressBar.setValue(step)
            step = step + step
    except Exception as detail:
        QtGui.QMessageBox.critical(Dialog, 'Properties', str(detail))
    finally:
        sys.exit(0)
elif action == '--cut':
    try:
        items = sys.argv[2:]
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
        QtGui.QMessageBox.critical(Dialog, 'Properties', str(detail))
    finally:
        sys.exit(0)
elif action == '--delete':
    try:
        items = sys.argv[2:]
        ask = True
        step = 100/len(items)
        for svar in items:
            if ask:
                reply = QtGui.QMessageBox.question(Dialog, "Delete",
                    "Are you sure you want to delete <b>" + svar + "</b>? ", QtGui.QMessageBox.Yes | QtGui.QMessageBox.YesToAll | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel)
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
        QtGui.QMessageBox.critical(Dialog, 'Properties', str(detail))
    finally:
        sys.exit(0)
elif action == '--rename':
    try:
        items = sys.argv[1:]
        step = 100/len(items)
        for svar in items:
            svar_basename = os.path.basename(svar)
            svar_dirname = os.path.dirname(svar)

            svar_new, ok = QtGui.QInputDialog.getText(Dialog, "Move",
                "New name:", QtGui.QLineEdit.Normal, svar_basename)
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
        QtGui.QMessageBox.critical(Dialog, 'Properties', str(detail))
    finally:
        sys.exit(0)
else:
    print('Invalid action, choose from cut/copy/rename/delete.')

sys.exit(app.exec_())
