## NAME

cparted - Curses based disk partition manipulation program

## SYNOPSIS

    cparted [--debug] [DEVICE]

## DESCRIPTION

cparted is a [curses](http://en.wikipedia.org/wiki/Curses_(programming_library))
based disk partition manipulation program that aims to replace
[cfdisk](http://en.wikipedia.org/wiki/Cfdisk) by providing a friendly curses
interface with the partition manipulation power of
[parted](http://www.gnu.org/software/parted/). **cparted** is written in
[Python](https://www.python.org/), and thus makes use of parted through
[pyparted](https://fedorahosted.org/pyparted/).

Starting **cparted** in debug mode causes it to display extended, metadata and
protected partitions, and sets the default unit to sectors. This will also
prevent the hiding of small unusable regions created from aligning the
partitions.

## OPTIONS

#### positional arguments

    DEVICE               Disk device to modify

### optional arguments

    --debug              Start cparted in debug mode

## BUGS

**Warning**: this software has not been widely tested and has at least a few issues.

Sometimes, when adding a [logical partition](http://en.wikipedia.org/wiki/Logical_partition_(virtual_computing_platform)),
two regions of free space will appear next to each other. This is bad. Do not
write to disk if this happens. If you do, the
[partition table](http://en.wikipedia.org/wiki/Partition_table) will probably
be corrupted, and you will have to create a new one. One sure way to trigger
this bug seems to be creating a logical partition on a disk without any
[primary partitions](http://en.wikipedia.org/wiki/Disk_partitioning#Primary_partition).

## AUTHOR

David Campbell <davekong@archlinux.us>

Ivailo Monev <xakepa10@gmail.com>

## COPYRIGHT

Copyright (c) 2011 David Campbell licensed through the GPLv3 License

Copyright (c) 2014 Ivailo Monev licensed through the GPLv3 License

## SEE ALSO

parted
