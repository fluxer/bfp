#!/bin/python2

import sys, argparse, tempfile, subprocess, shutil, os, gzip, bz2, glob

app_version = "1.7.2 (5a7ac08)"

tmpdir = None
keep = False
try:
    import libmessage, libmisc
    message = libmessage.Message()
    misc = libmisc.Misc()

    tmpdir = tempfile.mkdtemp()
    kernel = os.uname()[2]
    busybox = misc.whereis('busybox')
    image = '/boot/initramfs-%s.img' % kernel
    compression = 'gzip'
    modules = []
    for m in os.listdir('/sys/module'):
        if os.path.isdir('/sys/module/%s/sections' % m):
            modules.append(m)

    parser = argparse.ArgumentParser(prog='mkinitfs', description='MkInitfs')
    parser.add_argument('-t', '--tmp', type=str, default=tmpdir, \
        help='Change temporary directory')
    parser.add_argument('-b', '--busybox', type=str, default=busybox, \
        help='Change busybox binary')
    parser.add_argument('-k', '--kernel', type=str, default=kernel, \
        help='Change kernel version')
    parser.add_argument('-m', '--modules', type=str, nargs='+', \
        default=modules, help='Change modules')
    parser.add_argument('-i', '--image', type=str, default=image, \
        help='Change output image')
    parser.add_argument('-c', '--compression', type=str, default=compression, \
        choices=('gzip', 'cat', 'bzip2'), help='Change image compression method')
    parser.add_argument('--keep', action='store_true', \
        help='Keep temporary directory')
    parser.add_argument('--debug', action='store_true', \
        help='Enable debug messages')
    parser.add_argument('--version', action='version', \
        version='MkInitfs v' + app_version, \
        help='Show MkInitfs version and exit')
    ARGS = parser.parse_args()

    # if cross-building and no custom image is set update ARGS.image
    if ARGS.kernel != kernel and ARGS.image == image:
        ARGS.image = '/boot/initramfs-%s.img' % ARGS.kernel

    if ARGS.keep:
        keep = True

    if ARGS.debug:
        message.DEBUG = True

    lcopied = []
    def copy_item(src):
        ''' Copy method that handles binaries, symlinks and whatnot '''
        sdir = os.path.dirname(src)
        if os.path.islink(sdir):
            copy_item(sdir)
            misc.dir_create(ARGS.tmp + '/' + \
                os.path.dirname(os.path.realpath(src)))
        else:
            misc.dir_create(ARGS.tmp + '/' + sdir)
        if os.path.islink(src):
            if src in lcopied:
                message.sub_debug('Already linked', src)
                return
            sreal = os.readlink(src)
            sfixed = src.replace('/etc/mkinitfs/root', '')
            sdest = ARGS.tmp + sfixed
            if os.path.islink(sdest):
                message.sub_debug('Already exists', src)
                return
            message.sub_debug('Linking', sreal)
            message.sub_debug('To', sdest)
            os.symlink(sreal, sdest)
            lcopied.append(src)
        elif os.path.isdir(src):
            if src in lcopied:
                message.sub_debug('Already copied', src)
                return
            sfixed = src.replace('/etc/mkinitfs/root', '')
            sdest = ARGS.tmp + '/' + sfixed
            if os.path.isdir(sdest):
                message.sub_debug('Already exists', src)
                for sfile in os.listdir(src):
                    copy_item(os.path.join(src, sfile))
                return
            message.sub_debug('Copying', src)
            message.sub_debug('To', sdest)
            shutil.copytree(src, sdest)
            lcopied.append(src)
        elif os.path.isfile(src):
            ltocopy = misc.system_scanelf(src, sflags='-L').split(',')
            ltocopy.append(src)
            for sfile in ltocopy:
                if sfile in lcopied:
                    message.sub_debug('Already copied', sfile)
                    continue
                elif not sfile:
                    continue
                sfixed = sfile.replace('/etc/mkinitfs/root', '')
                if os.path.islink(sfile):
                    copy_item(sfile)
                    sfile = os.path.dirname(sfile) + '/' + os.readlink(sfile)
                sdest = ARGS.tmp + '/' + sfixed
                if os.path.isfile(sdest):
                    message.sub_debug('Already exists', src)
                    return
                message.sub_debug('Copying', sfile)
                message.sub_debug('To', sdest)
                shutil.copy2(sfile, sdest)
                lcopied.append(sfile)
                copy_item(sfile)
        else:
            message.warning('File or directory does not exist', src)

    # FIXME: support both /lib and /usr/lib at the same time???
    modsdir = None
    moddirs = ('/lib', '/lib32', '/lib64', '/usr/lib', '/usr/lib32', \
        '/usr/lib64')
    for moddir in moddirs:
        if os.path.islink(moddir):
            continue
        kerndir = '%s/modules/%s' % (moddir, ARGS.kernel)
        if os.path.isfile('%s/modules.dep' % kerndir) and \
            os.path.isfile('%s/modules.builtin' % kerndir):
            modsdir = kerndir
            break
    # if the above fails, attempt to guess the kernel installed
    if not modsdir:
        for sdir in moddirs:
            if not os.path.exists(sdir) or os.path.islink(sdir):
                continue
            for k in os.listdir(sdir + '/modules'):
                if os.path.isfile(sdir + '/modules/' + k + '/modules.dep') and \
                    os.path.isfile(sdir + '/modules/' + k + '/modules.builtin'):
                    message.sub_warning('Last resort kernel detected', k)
                    modsdir = sdir + '/modules/' + k
                    ARGS.kernel = k
                    ARGS.image = '/boot/initramfs-%s.img' % k
                    break
    if not modsdir:
        message.critical('Unable to find modules directory')
        sys.exit(2)

    message.info('Runtime information')
    message.sub_info('TMP', ARGS.tmp)
    message.sub_info('BUSYBOX', ARGS.busybox)
    message.sub_info('KERNEL', ARGS.kernel)
    message.sub_info('MODULES', ARGS.modules)
    message.sub_info('IMAGE', ARGS.image)
    message.sub_info('COMPRESSION', ARGS.compression)

    message.sub_info('Installing Busybox')
    bin_dir = os.path.join(ARGS.tmp, 'bin')
    misc.dir_create(bin_dir)
    message.sub_debug('Installing binary')
    copy_item(ARGS.busybox)
    message.sub_debug('Creating symlinks')
    misc.system_command((ARGS.busybox, '--install', '-s', bin_dir))

    message.sub_info('Copying root overlay')
    if os.path.isdir('/etc/mkinitfs/root'):
        for spath in misc.list_all('/etc/mkinitfs/root'):
            copy_item(spath)

    message.sub_info('Copying files')
    if os.path.isdir('/etc/mkinitfs/files'):
        for sfile in misc.list_files('/etc/mkinitfs/files'):
            if not sfile.endswith('.conf'):
                message.sub_debug('Skipping', sfile)
                continue
            message.sub_debug('Reading', sfile)
            for line in misc.file_readlines(sfile):
                if not line or line.startswith('#'):
                    continue
                items = glob.glob(line)
                # glob returns null and the warning in copy_item() may not be
                # reached if iterating directly over the value fom glob.glob()
                if not items:
                    message.warning('File or directory does not exist', line)
                    continue
                for item in items:
                    copy_item(item)

    message.sub_info('Copying modules')
    if os.path.isdir('/etc/mkinitfs/modules'):
        for sfile in misc.list_files('/etc/mkinitfs/modules'):
            if not sfile.endswith('.conf'):
                message.sub_debug('Skipping', sfile)
                continue
            message.sub_debug('Reading', sfile)
            for line in misc.file_readlines(sfile):
                if not line or line.startswith('#'):
                    continue
                if not line in ARGS.modules:
                    ARGS.modules.append(line)

    for module in ARGS.modules:
        # in case ARGS.modules equals ''
        if not module:
            continue
        found = False
        for line in misc.file_readlines(modsdir + '/modules.dep'):
            base = line.split(':')[0]
            depends = line.split(':')[1].split()
            if '/%s.ko' % module in base \
                or '/%s.ko' % module.replace('_', '-') in base:
                found = True
                copy_item(modsdir + '/' + base.strip())
                for dep in depends:
                    copy_item(modsdir + '/' + dep.strip())
        if not found:
            for line in misc.file_readlines(modsdir + '/modules.builtin'):
                if '/%s.ko' % module in line \
                    or '/%s.ko' % module.replace('_', '-') in line:
                    message.sub_debug('Module is builtin', module)
                    found = True
        if not found:
            message.sub_warning('Module not found', module)

    message.sub_info('Copying module files')
    for sfile in os.listdir(modsdir):
        if sfile.startswith('modules.'):
            copy_item(modsdir + '/' + sfile)

    message.sub_info('Updating module dependencies')
    misc.system_command((misc.whereis('depmod'), ARGS.kernel, '-b', ARGS.tmp))

    message.sub_info('Creating shared libraries cache')
    etc_dir = os.path.join(ARGS.tmp, 'etc')
    misc.dir_create(etc_dir)
    # to surpress a warning
    misc.file_touch(os.path.join(etc_dir, 'ld.so.conf'))
    misc.system_command((misc.whereis('ldconfig'), '-r', ARGS.tmp))

    message.sub_info('Creating image')
    find = misc.whereis('find')
    cpio = misc.whereis('cpio')
    data = misc.system_output('%s . | %s -o -H newc' % \
        (find, cpio), shell=True, cwd=ARGS.tmp)
    if ARGS.compression == 'gzip':
        gzipf = gzip.GzipFile(ARGS.image, 'wb')
        gzipf.write(data)
        gzipf.close()
    elif ARGS.compression == 'bzip2':
        bzipf = bz2.BZ2File(ARGS.image, 'wb')
        bzipf.write(data)
        bzipf.close()
    else:
        misc.file_write(ARGS.image, data)

except subprocess.CalledProcessError as detail:
    message.critical('SUBPROCESS', detail)
    sys.exit(3)
except shutil.Error as detail:
    message.critical('SHUTIL', detail)
    sys.exit(4)
except OSError as detail:
    message.critical('OS', detail)
    sys.exit(5)
except IOError as detail:
    message.critical('IO', detail)
    sys.exit(6)
except KeyboardInterrupt:
    message.critical('Interrupt signal received')
    sys.exit(7)
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
