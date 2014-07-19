#!/bin/python2

import sys, argparse, tempfile, subprocess
import tarfile, zipfile, shutil, os

app_version = "0.9.17 (7c29451)"

tmpdir = None
keep = False
try:
    import libmessage, libmisc
    message = libmessage.Message()
    misc = libmisc.Misc()

    parser = argparse.ArgumentParser(prog='mkinitfs', description='MkInitfs')

    if not os.geteuid() == 0:
        message.critical('You are not root')
        sys.exit(2)

    tmpdir = tempfile.mkdtemp()
    kernel = os.uname()[2]
    busybox = misc.whereis('busybox')
    image = '/boot/initramfs-' + kernel + '.img'
    modules = []
    # FIXME: some modules are virtual???
    for m in os.listdir('/sys/module'):
        if os.path.isdir('/sys/module/' + m + '/sections'):
            modules.append(m)

    parser.add_argument('-t', '--tmp', type=str, default=tmpdir, \
        help='Change temporary directory')
    parser.add_argument('-b', '--busybox', type=str, default=busybox, \
        help='Change busybox binary')
    parser.add_argument('-k', '--kernel', type=str, default=kernel, \
        help='Change kernel version')
    parser.add_argument('-m', '--modules', type=str, nargs='+', default=modules, \
        help='Change modules')
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
        # FIXME: symlinks, force
        if os.path.isdir(src):
            if src in lcopied:
                message.sub_debug('Already copied', src)
                return
            sfixed = src.replace('/etc/mkinitfs/root', '')
            sfixed = sfixed.replace('/etc/mkinitfs/hooks', '/hooks')
            message.sub_debug('Copying', src)
            message.sub_debug('To', ARGS.tmp + '/' + sfixed)
            shutil.copytree(src, ARGS.tmp + '/'+ sfixed)
            lcopied.append(src)
        elif os.path.isfile(src):
            for sfile in misc.system_output((misc.whereis('lddtree'), '-l', src)).split('\n'):
                if sfile in lcopied:
                    message.sub_debug('Already copied', sfile)
                    continue
                sfixed = sfile.replace('/etc/mkinitfs/root', '')
                sfixed = sfixed.replace('/etc/mkinitfs/hooks', '/hooks')
                message.sub_debug('Copying', sfile)
                message.sub_debug('To', ARGS.tmp + '/' + sfixed)
                misc.dir_create(ARGS.tmp + os.path.dirname(sfixed))
                shutil.copy2(sfile, ARGS.tmp + '/' + sfixed)
                lcopied.append(sfile)
                if os.path.islink(sfile):
                    slink = os.readlink(sfile)
                    copy_item(os.path.dirname(sfile) + '/' + slink)
        else:
            message.warning('File or directory does not exist', src)

    # FIXME: support both /lib and /usr/lib at the same time???
    if os.path.isdir('/lib/modules/' + ARGS.kernel):
        modsdir = '/lib/modules/' + ARGS.kernel
    elif os.path.isdir('/usr/lib/modules/' + ARGS.kernel):
        modsdir = '/usr/lib/modules/' + ARGS.kernel
    else:
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
    subprocess.check_call((ARGS.busybox, '--install', '-s', bin_dir))

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

    message.sub_info('Copying hooks')
    if os.path.isdir('/etc/mkinitfs/hooks'):
        for sfile in misc.list_files('/etc/mkinitfs/hooks'):
            copy_item(sfile)

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
                if not line in modules:
                    modules.append(line)

    # FIXME: aliases are not supported, `modprobe -bD <module>` can be used but it is
    #              required to be able to specify the kernel version which it does not support
    #              otherwise it bails when kernel version requested is different from `uname -r`.
    for module in modules:
        found = False
        if ARGS.kernel != kernel:
            for line in misc.file_read(modsdir + '/modules.dep').splitlines():
                base = line.split(':')[0]
                depends = line.split(':')[1]
                if '/' + module + '.ko' in base:
                    found = True
                    copy_item(modsdir + '/' + base)
                    for dep in depends.split():
                        copy_item(modsdir+ '/' + dep)
        else:
            depends = misc.system_output((misc.whereis('modprobe'), '-bD', module))
            if depends:
                found = True
                for line in depends.splitlines():
                    copy_item(line.split()[1])
        if not found:
            message.sub_warning('Module not found', module)

    message.sub_info('Copying module files')
    for sfile in os.listdir(modsdir):
        if sfile.startswith('modules.'):
            sfile = modsdir + '/' + sfile
            copy_item(sfile)

    message.sub_info('Updating module dependencies')
    subprocess.check_call((misc.whereis('depmod'), ARGS.kernel, '-b', ARGS.tmp))

    message.sub_info('Creating shared libraries cache')
    etc_dir = os.path.join(ARGS.tmp, 'etc')
    misc.dir_create(etc_dir)
    # to surpress a warning
    if os.path.isfile('/etc/ld.so.conf'):
        shutil.copy2('/etc/ld.so.conf', os.path.join(etc_dir, 'ld.so.conf'))
    else:
        misc.file_write(os.path.join(etc_dir, 'ld.so.conf'), '')
    subprocess.check_call((misc.whereis('ldconfig'), '-r', ARGS.tmp))

    message.sub_info('Creating image')
    find = misc.whereis('find')
    cpio = misc.whereis('cpio')
    gzip = misc.whereis('gzip')
    os.chdir(ARGS.tmp)
    # subprocess.check_call((find, '.', '|', cpio, '-o', '-H', 'newc', '|', gzip ,'>' , image))
    os.system(find + ' . | ' + cpio + ' -o -H newc | ' + gzip + ' > ' + image)

    if os.path.isdir(tmpdir) and not ARGS.keep:
        message.info('Cleaning up...')
        misc.dir_remove(tmpdir)

except subprocess.CalledProcessError as detail:
    message.critical('SUBPROCESS', detail)
    sys.exit(4)
except tarfile.TarError as detail:
    message.critical('TARFILE', detail)
    sys.exit(6)
except zipfile.BadZipfile as detail:
    message.critical('ZIPFILE', detail)
    sys.exit(7)
except shutil.Error as detail:
    message.critical('SHUTIL', detail)
    sys.exit(8)
except OSError as detail:
    message.critical('OS', detail)
    sys.exit(9)
except IOError as detail:
    message.critical('IO', detail)
    sys.exit(10)
except KeyboardInterrupt:
    message.critical('Interrupt signal received')
    sys.exit(12)
except SystemExit:
    sys.exit(2)
except Exception as detail:
    message.critical('Unexpected error', detail)
    sys.exit(1)
finally:
    if os.path.isdir(tmpdir) and not keep:
        message.info('Cleaning up...')
        misc.dir_remove(tmpdir)
