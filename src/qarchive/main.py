#!/bin/python2

from PyQt4 import QtGui
import sys, os, tempfile, libmisc, libdesktop, libarchive

# prepare for lift-off
app = QtGui.QApplication(sys.argv)
Dialog = QtGui.QProgressDialog() # 'QArchive'
config = libdesktop.Config()
actions = libdesktop.Actions(Dialog, app)
general = libdesktop.General()
misc = libmisc.Misc()
archive = libarchive.Libarchive()

def setLook():
    general.set_style(app)
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
            # ensure that directory is passed to archive_compress() as chdir argument
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
elif action == '--browse':
    for svar in variant:
        try:
            if os.path.isfile(svar) and archive.supportedArchive(svar):
                stmp = tempfile.mkdtemp()
                Dialog.show()
                Dialog.setLabelText('Reading: <b>' + svar + '</b>')
                archive.extractArchive(svar, stmp)
                Dialog.hide()
                general.execute_program('qfile ' + stmp, False)
                Dialog.show()
                Dialog.setLabelText('Saving: <b>' + svar + '</b>')
                archive.createArchive(stmp, svar)
                Dialog.hide()
        except Exception as detail:
            QtGui.QMessageBox.critical(Dialog, 'Critical', str(detail))
        finally:
            if os.path.isdir(stmp):
                misc.dir_remove(stmp)
            sys.exit(0)
else:
    QtGui.QMessageBox.critical(Dialog, 'Critical', 'Invalid action, choose from gzip/bzip/extract/browse.')
    sys.exit(3)

sys.exit(app.exec_())
