## NAME

lsinitfs - LsInitfs

## SYNOPSIS

    lsinitfs [-h] [-t TMP] [-k KERNEL] [-i IMAGE] [--keep] [--debug]
        [--version]

## DESCRIPTION

LsInitfs is a [initial RAM filesystem](http://en.wikipedia.org/wiki/Initrd)
image content lister.

## OPTIONS

### optional arguments

    -h, --help            Show this help message and exit
    -t TMP, --tmp TMP     Change temporary directory
    -k KERNEL, --kernel KERNEL
                          Change kernel version
    -i IMAGE, --image IMAGE
                          Change output image
    --keep                Keep temporary directory
    --debug               Enable debug messages
    --version             Show LsInitfs version and exit

## EXAMPLES

List image of currently running kernel:

    lsinitfs

List image of kernel other than the one running:

    lsinitfs -k=3.12.24

## EXIT STATUS

LsInitfs returns 0 on success and other on failure.

### Unexpected error (1)

This is a general error. Triggered, most likely, by something that LsInitfs is
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

None

## AUTHOR

Ivailo Monev <xakepa10@gmail.com>

## COPYRIGHT

Copyright (c) 2014 Ivailo Monev licensed through custom License

## SEE ALSO

[mkinitfs](mkinitfs.html) gunzip cpio
