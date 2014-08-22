## NAME

mkinitfs - MkInitfs

## SYNOPSIS

mkinitfs [-h] [-t TMP] [-b BUSYBOX] [-k KERNEL]
    [-m MODULES [MODULES ...]] [-i IMAGE] [--keep] [--debug]
    [--version]

## DESCRIPTION

MkInitfs is a initial RAM filesystem image maker.

## OPTIONS

optional arguments:
  -h, --help            show this help message and exit
  -t TMP, --tmp TMP     Change temporary directory
  -b BUSYBOX, --busybox BUSYBOX
                        Change busybox binary
  -k KERNEL, --kernel KERNEL
                        Change kernel version
  -m MODULES [MODULES ...], --modules MODULES [MODULES ...]
                        Change modules
  -i IMAGE, --image IMAGE
                        Change output image
  --keep                Keep temporary directory
  --debug               Enable debug messages
  --version             Show MkInitfs version and exit

## EXAMPLES

Create image of currently running kernel:

    mkinitfs

Create image of kernel other than the one running:

    mkinitfs -k=3.12.24

## EXIT STATUS

MkInitfs returns 0 on success and other on failure.

### Unexpected error (1)

This is a general error. Triggered, most likely, by something that MkInitfs is
not able to handle.

### Internal error (2)

This error raises when a dependency, library, or other important thing
is missing or failed.

### SUBPROCESS (3)

This error raises when a subprocess, such as cpio, failed to
execute a sub-command.

### SHUTIL (4)

This error raises when the module responsible for shell or system
operations fails badly. Its job usually is to copy or remove files and
directories.

### OS (5)

This error raises when the module responsible for system files and
directories information gathering fails badly. Its job usually is to
check if X is file, symbolic link or directory.

### IO (6)

This error raises when there is something wrong with the file/directory
permissions.

### Interupt signal received (7)

This error raises when the user triggers keyboard interrupt via Ctrl+C key
combination.

## BUGS

### PYTHON MODULES

None

### MKINITFS

None

## AUTHORS

Ivailo Monev (a.k.a. SmiL3y) <xakepa10@gmail.com>

Copyright (c) 2014 Ivailo Monev licensed through the GNU General Public License

## SEE ALSO

lsinitfs lddtree gzip cpio modprobe
