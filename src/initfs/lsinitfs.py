#!/usr/bin/python2

import sys, argparse, tempfile, subprocess, shutil, os

app_version = "1.11.0 (21bf1817)"

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

    parser = argparse.ArgumentParser(prog='lsinitfs', description='LsInitfs')
    parser.add_argument('-t', '--tmp', type=str, default=tmpdir, \
        help='Change temporary directory')
    parser.add_argument('-b', '--busybox', type=str, default=busybox, \
        help='Change busybox binary')
    parser.add_argument('-k', '--kernel', type=str, default=kernel, \
        help='Change kernel version')
    parser.add_argument('-i', '--image', type=str, default=image, \
        help='Change output image')
    parser.add_argument('--keep', action='store_true', \
        help='Keep temporary directory')
    parser.add_argument('--debug', action='store_true', \
        help='Enable debug messages')
    parser.add_argument('--version', action='version', \
        version='LsInitfs v' + app_version, \
        help='Show LsInitfs version and exit')
    ARGS = parser.parse_args()

    # if cross-building and no custom image is set update ARGS.image
    if ARGS.kernel != kernel and ARGS.image == image:
        ARGS.image = '/boot/initramfs-%s.img' % ARGS.kernel

    if ARGS.keep:
        keep = True

    if ARGS.debug:
        message.DEBUG = True

    message.info('Runtime information')
    message.sub_info('TMP', ARGS.tmp)
    message.sub_info('KERNEL', ARGS.kernel)
    message.sub_info('BUSYBOX', ARGS.busybox)
    message.sub_info('IMAGE', ARGS.image)

    if not os.path.isfile(ARGS.image):
        message.critical('Image does not exist', ARGS.image)
        sys.exit(2)

    message.info('Listing initial RAM image...')
    smime = misc.file_mime(ARGS.image)
    if smime in misc.gzipmimes:
        new_image = '%s/%s.gz' % (ARGS.tmp, os.path.basename(ARGS.image))
    elif smime in misc.bzip2mimes:
        new_image = '%s/%s.bz2' % (ARGS.tmp, os.path.basename(ARGS.image))
    else:
        new_image = '%s/%s' % (ARGS.tmp, os.path.basename(ARGS.image))
    message.sub_info('Copying image')
    misc.dir_create(ARGS.tmp)
    shutil.copyfile(ARGS.image, new_image)

    if misc.archive_supported(new_image):
        message.sub_info('Decompressing image')
        misc.archive_decompress(new_image, ARGS.tmp)

    message.sub_info('Listing image')
    print(misc.system_communicate((ARGS.busybox, 'cpio', '-tF', \
        misc.file_name(new_image, False))))

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
