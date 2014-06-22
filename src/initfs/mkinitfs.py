#!/usr/bin/python2

import sys
import argparse
import tempfile
import subprocess
import tarfile
import zipfile
import shutil
import os

app_version = "0.0.1 (61914bd)"

try:
    import libmessage
    message = libmessage.Message()
    import libmisc
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

    if ARGS.debug:
        message.DEBUG = True

    def copy_item(src):
        # FIXME: symlinks, force
        if os.path.isdir(src):
            for f in misc.list_files(src):
                sfixed = f.replace('/etc/mkinitfs/root', '')
                sfixed = sfixed.replace('/etc/mkinitfs/hooks', 'hooks')
                message.sub_debug('Copying', f)
                message.sub_debug('To', ARGS.tmp + '/' + f)
                misc.dir_create(ARGS.tmp + '/' + os.path.dirname(f))
                shutil.copy2(f, ARGS.tmp + '/'+ f)
        elif os.path.isfile(src):
            for dep in misc.system_output((misc.whereis('lddtree'), '-l', src)).split('\n'):
                sfixed = dep.replace('/etc/mkinitfs/root', '')
                sfixed = sfixed.replace('/etc/mkinitfs/hooks', 'hooks')
                message.sub_debug('Copying', dep)
                message.sub_debug('To', ARGS.tmp + '/' + sfixed)
                sdir = os.path.dirname(sfixed)
                misc.dir_create(ARGS.tmp + sdir)
                shutil.copy2(dep, ARGS.tmp + '/' + sfixed)
                if os.path.islink(dep):
                    slink = os.readlink(dep)
                    copy_item(os.path.dirname(dep) + '/' + slink)
        else:
            message.warning('File or directory does not exist', src)

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
                if not line in modules:
                    modules.append(line)

    # FIXME: aliases are not supported, `modprobe -bD <module>` can be used but it is
    #              required to be able to specify the kernel version which it does not support
    #              otherwise it bails when kernel version requested is different from `uname -r`.
    for module in modules:
        found = False
        if ARGS.kernel != kernel:
            for line in misc.file_read('/lib/modules/' + ARGS.kernel + '/modules.dep').splitlines():
                base = line.split(':')[0]
                depends = line.split(':')[1]
                if '/' + module + '.ko' in base:
                    found = True
                    copy_item('/lib/modules/' + ARGS.kernel + '/' + base)
                    for dep in depends.split():
                        copy_item('/lib/modules/' + ARGS.kernel + '/' + dep)
        else:
            depends = misc.system_output((misc.whereis('modprobe'), '-bD', module))
            if depends:
                found = True
                for line in depends.splitlines():
                    copy_item(line.split()[1])
        if not found:
            message.sub_warning('Module not found', module)

    message.sub_info('Copying module files')
    for sfile in os.listdir('/lib/modules/' + ARGS.kernel):
        if sfile.startswith('modules.'):
            sfile = '/lib/modules/' + ARGS.kernel + '/' + sfile
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
#finally:
#    raise
