#!/bin/python2

import sys, argparse, tempfile, subprocess, shutil, os

app_version = "0.9.31 (63c68ab)"

tmpdir = None
keep = False
try:
    import libmessage, libmisc
    message = libmessage.Message()
    misc = libmisc.Misc()

    parser = argparse.ArgumentParser(prog='lsinitfs', description='LsInitfs')

    tmpdir = tempfile.mkdtemp()
    kernel = os.uname()[2]
    image = '/boot/initramfs-' + kernel + '.img'

    parser.add_argument('-t', '--tmp', type=str, default=tmpdir, \
        help='Change temporary directory')
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
        ARGS.image = '/boot/initramfs-' + ARGS.kernel + '.img'

    if ARGS.keep:
        keep = True

    if ARGS.debug:
        message.DEBUG = True

    message.info('Runtime information')
    message.sub_info('TMP', ARGS.tmp)
    message.sub_info('KERNEL', ARGS.kernel)
    message.sub_info('IMAGE', ARGS.image)

    if not os.path.isfile(ARGS.image):
        message.critical('Image does not exist', ARGS.image)
        sys.exit(2)

    message.info('Listing initial RAM image...')
    base = os.path.basename(ARGS.image)
    new_image = os.path.join(ARGS.tmp, base.replace('.img', '.gz'))
    message.sub_info('Copying image')
    misc.dir_create(ARGS.tmp)
    shutil.copyfile(ARGS.image, new_image)

    message.sub_info('Decompressing image')
    gunzip = misc.whereis('gunzip')
    os.system(gunzip + ' ' + new_image)

    message.sub_info('Listing image')
    cpio = misc.whereis('cpio')
    print os.system(cpio + ' -tF ' + new_image.replace('.gz', ''))

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
    if os.path.isdir(tmpdir) and not keep:
        message.info('Cleaning up...')
        misc.dir_remove(tmpdir)

