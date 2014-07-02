#!/bin/python2

from PyQt4 import QtGui
import sys, os, libmisc, libdesktop

# prepare for lift-off
app = QtGui.QApplication(sys.argv)
Dialog = QtGui.QProgressDialog() # 'QArchive'
config = libdesktop.Config()
actions = libdesktop.Actions(Dialog, app)
general = libdesktop.General()
icon = QtGui.QIcon()
misc = libmisc.Misc()

def setLook():
    general.set_style(app)
    icon.setThemeName(config.GENERAL_ICONTHEME)
setLook()

if len(sys.argv) < 3:
    QtGui.QMessageBox.critical(Dialog, 'Critical', 'Not enough arguments')
    sys.exit(2)

Dialog.setMaximum(0)

action = sys.argv[1]
variant = sys.argv[2:]
if action == '--gzip':
    try:
        for svar in variant:
            soutput = svar + '.tar.gz'
            # ensure that directory is passed to archive_compress() as chdir argument
            if not os.path.isdir(svar):
                svar = os.path.dirname(svar)
        Dialog.show()
        Dialog.setLabelText('Compressing: <b>' + misc.string_convert(variant) + '</b> To: <b>' + soutput + '</b>')
        misc.archive_compress(variant, soutput, 'gz', svar)
        Dialog.hide()
    except Exception as detail:
        QtGui.QMessageBox.critical(Dialog, 'Critical', str(detail))
    finally:
        sys.exit(0)
elif action == '--bzip2':
    try:
        for svar in variant:
            soutput = svar + '.tar.bz2'
            # ensure that directory is passed to archive_compress() as chir argument
            if not os.path.isdir(svar):
                svar = os.path.dirname(svar)
        Dialog.show()
        Dialog.setLabelText('Compressing: <b>' + misc.string_convert(variant) + '</b> To: <b>' + soutput + '</b>')
        misc.archive_compress(variant, soutput, 'bz2', svar)
        Dialog.hide()
    except Exception as detail:
        QtGui.QMessageBox.critical(Dialog, 'Critical', str(detail))
    finally:
        sys.exit(0)
elif action == '--extract':
    try:
        for svar in variant:
            sdir = os.path.dirname(svar)
            Dialog.show()
            Dialog.setLabelText('Extracting: <b>' + svar + '</b> To: <b>' + sdir + '</b>')
            misc.archive_decompress(svar, sdir)
            Dialog.hide()
    except Exception as detail:
        QtGui.QMessageBox.critical(Dialog, 'Critical', str(detail))
    finally:
        sys.exit(0)
else:
    QtGui.QMessageBox.critical(Dialog, 'Critical','Invalid action, choose from gzip/bzip/extract.')
    sys.exit(3)

sys.exit(app.exec_())
