#!/usr/bin/python2

import sys, argparse, tempfile, shutil, os

app_version = "1.8.2 (8552bb1)"

tmpdir = None
keep = False
try:
    import libmessage, libmisc
    message = libmessage.Message()
    misc = libmisc.Misc()

    tmpdir = tempfile.mkdtemp()
    interpreter = misc.whereis('python')
    output = '%s/myapp' % misc.dir_current()

    parser = argparse.ArgumentParser(prog='cold', description='Python bundle creator')
    parser.add_argument('-t', '--tmp', type=str, default=tmpdir, \
        help='Change temporary directory')
    parser.add_argument('-i', '--interpreter', type=str, default=interpreter, \
        help='Change interpreter')
    parser.add_argument('-o', '--output', type=str, default=output, \
        help='Change output file')
    parser.add_argument('PATH', nargs='+', type=str, \
        help='Files/directories to pack')
    parser.add_argument('--keep', action='store_true', \
        help='Keep temporary directory')
    parser.add_argument('--debug', action='store_true', \
        help='Enable debug messages')
    parser.add_argument('--version', action='version', \
        version='Cold v' + app_version, \
        help='Show Cold version and exit')
    ARGS = parser.parse_args()

    if ARGS.keep:
        keep = True

    if ARGS.debug:
        message.DEBUG = True

    message.info('Runtime information')
    message.sub_info('TMP', ARGS.tmp)
    message.sub_info('INTERPRETER', ARGS.interpreter)
    message.sub_info('OUTPUT', ARGS.output)
    message.sub_info('PATH', ARGS.PATH)

    message.info('Creating', ARGS.output)
    for spath in ARGS.PATH:
        spath = os.path.realpath(spath)
        message.sub_info('Copying', spath)
        scopy = '%s/%s' % (ARGS.tmp, os.path.basename(spath))
        if not os.path.isdir(spath):
            shutil.copy2(spath, scopy)
        else:
            shutil.copytree(spath, scopy)
    shebang = '#!%s\n' % ARGS.interpreter
    maindata = '%sif __name__ == "__main__": import %s' % (shebang, misc.file_name(ARGS.PATH[0]))
    mainfile = '%s/__main__.py' % ARGS.tmp
    message.sub_info('Writing __main__')
    misc.file_write(mainfile, maindata)
    message.sub_info('Compressing bundle')
    tmpout = '%s/app.zip' % ARGS.tmp
    misc.archive_compress(misc.list_files(ARGS.tmp), tmpout, ARGS.tmp)
    message.sub_info('Creating finall app')
    fullout = os.path.realpath(ARGS.output)
    misc.file_write(fullout, '%s%s' % (shebang, misc.file_read(tmpout)))
    message.sub_info('Making the app executable')
    os.chmod(fullout, 0o755)

except shutil.Error as detail:
    message.critical('SHUTIL', detail)
    sys.exit(3)
except OSError as detail:
    message.critical('OS', detail)
    sys.exit(4)
except IOError as detail:
    message.critical('IO', detail)
    sys.exit(5)
except KeyboardInterrupt:
    message.critical('Interrupt signal received')
    sys.exit(6)
except SystemExit:
    sys.exit(2)
except Exception as detail:
    message.critical('Unexpected error', detail)
    sys.exit(1)
finally:
    if tmpdir and os.path.isdir(tmpdir) and not keep:
        message.info('Cleaning up...')
        misc.dir_remove(tmpdir)
    if not 'stable' in app_version and sys.exc_info()[0]:
        raise

