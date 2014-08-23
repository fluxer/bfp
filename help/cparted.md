## NAME

cparted - Curses based disk partition manipulation program

## SYNOPSIS

**cparted** *[options] [device]*

## DESCRIPTION

**cparted** is a curses based disk partition manipulation program that aims to
replace cfdisk by providing a friendly curses interface with the partition
manipulation power of libparted. B<cparted> is written in Python, and thus
makes use of libparted through pyparted.

## OPTIONS

+ *--debug*

Start B<cparted> in debug mode. This causes B<cparted> to display extended,
metadata, and protected partitions, and sets the default unit to sectors.
This will also prevent the hiding of small unusable regions created from
aligning the partitions.

## BUGS

Warning: this software has not been widely tested and has a least a few issues.

Sometimes, when adding a logical partition, two regions of free space will
appear next to each other. This is bad. Do not write to disk if this happens.
If you do, the partition table will probably be corrupted, and you will have
to create a new one. One sure way to trigger this bug seems to be creating a
logical partition on a disk without any primary partitions.

## SEE ALSO

parted

## AUTHOR

David Campbell <davekong@archlinux.us>

Ivailo Monev <xakepa10@gmail.com>