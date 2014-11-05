#!/bin/python2

import sys, argparse, tempfile, subprocess, shutil, os

app_version = "1.2.1 (b308d5d)"

tmpdir = None
keep = False
try:
    import libmessage, libmisc
    message = libmessage.Message()
    misc = libmisc.Misc()

    tmpdir = tempfile.mkdtemp()
    kernel = os.uname()[2]
    busybox = misc.whereis('busybox')
    image = '/boot/initramfs-' + kernel + '.img'
    modules = []
    for m in os.listdir('/sys/module'):
        if os.path.isdir('/sys/module/' + m + '/sections'):
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
        ARGS.image = '/boot/initramfs-' + ARGS.kernel + '.img'

    if ARGS.keep:
        keep = True

    if ARGS.debug:
        message.DEBUG = True

    lcopied = []
    def copy_item(src):
        ''' Copy method that handles binaries, symlinks and whatnot '''
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
            misc.dir_create(os.path.dirname(sdest))
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
                return
            message.sub_debug('Copying', src)
            message.sub_debug('To', sdest)
            shutil.copytree(src, sdest)
            lcopied.append(src)
        elif os.path.isfile(src):
            for sfile in misc.system_output((misc.whereis('lddtree'), \
                '-l', src)).split('\n'):
                if sfile in lcopied:
                    message.sub_debug('Already copied', sfile)
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
                misc.dir_create(os.path.dirname(sdest))
                shutil.copy2(sfile, sdest)
                lcopied.append(sfile)
        else:
            message.warning('File or directory does not exist', src)

    # FIXME: support both /lib and /usr/lib at the same time???
    modsdir = None
    moddirs = ('/lib', '/lib32', '/lib64', '/usr/lib', '/usr/lib32', \
        '/usr/lib64')
    for sdir in moddirs:
        if os.path.isdir(sdir + '/modules/' + ARGS.kernel):
            modsdir = sdir + '/modules/' + ARGS.kernel
    # if the above fails, attempt to guess the kernel installed
    if not modsdir:
        for sdir in moddirs:
            for k in os.listdir(sdir + '/modules'):
                if os.path.isfile(sdir + '/modules/' + k + '/modules.dep') and \
                    os.path.isfile(sdir + '/modules/' + k + '/modules.builtin'):
                    message.sub_warning('Last resort kernel detected', k)
                    modsdir = sdir + '/modules/' + k
                    ARGS.kernel = k
                    ARGS.image = '/boot/initramfs-' + k + '.img'
    if not modsdir:
        message.critical('Unable to find modules directory')
        sys.exit(2)

    message.info('Runtime information')
    message.sub_info('TMP', ARGS.tmp)
    message.sub_info('BUSYBOX', ARGS.busybox)
    message.sub_info('KERNEL', ARGS.kernel)
    message.sub_info('MODULES', ARGS.modules)
    message.sub_info('IMAGE', ARGS.image)

    message.sub_info('Installing Busybox')
    bin_dir = os.path.join(ARGS.tmp, 'bin')
    misc.dir_create(bin_dir)
    message.sub_debug('Installing binary')
    copy_item(ARGS.busybox)
    message.sub_debug('Creating symlinks')
    misc.system_command((ARGS.busybox, '--install', '-s', bin_dir))

    message.sub_info('Copying root overlay')
    if os.path.isdir('/etc/mkinitfs/root'):
        for sdir in misc.list_dirs('/etc/mkinitfs/root'):
            fixed_sdir = sdir.replace('/etc/mkinitfs/root', '')
            message.sub_debug('Creating', fixed_sdir)
            misc.dir_create(ARGS.tmp + fixed_sdir)
        for sfile in misc.list_files('/etc/mkinitfs/root'):
            message.sub_debug('Copying', sfile)
            copy_item(sfile)

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
                copy_item(line)

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
            # depends = line.split(':')[1]
            if '/' + module + '.ko' in base \
                or '/' + module.replace('_', '-') + '.ko' in base:
                found = True
                copy_item(modsdir + '/' + base.strip())
        if not found:
            for line in misc.file_readlines(modsdir + '/modules.builtin'):
                if '/' + module + '.ko' in line \
                    or '/' + module.replace('_', '-') + '.ko' in line:
                    found = True
        if not found:
            message.sub_warning('Module not found', module)

    message.sub_info('Copying module files')
    for sfile in os.listdir(modsdir):
        if sfile.startswith('modules.'):
            sfile = modsdir + '/' + sfile
            copy_item(sfile)

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
    gzip = misc.whereis('gzip')
    misc.system_command( \
        find + ' . | ' + cpio + ' -o -H newc | ' + gzip + ' > ' + ARGS.image, \
        shell=True, cwd=ARGS.tmp)

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
