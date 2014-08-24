## NAME

spm-tools - Source Package Manager Tools

## SYNOPSIS

    spm-tools [-h] [--debug] [--version]
        {dist,edit,lint,merge,sane,clean,check,which,pack} ...

## DESCRIPTION

Source Package Manager Tools (SPMT) packs additional utilities to assist in the
system maintenance.

With the tools you can distribute tarballs of port(s) and share them with friends
so that other can benefit from your work. Along with the tarballs sources, such
as patches and archives, can be optionally fetched and packed in the tarball.

Runtime dependencies of binaries, libraries and scripts can be checked to ensure
the system consistency which is useful, for an example, when cross-compiling or
when targets where force removed from the system.

Checking for various system issues such as cross-filesystem udev rules and
symbolic links can be perfomed. Also ports sanity can be checked for missing
maintainer, /dev/null output recirections (which is bad and hides problems when
they occure) and more.

Dealing with files backed up by SPM can be done in merge mode, interactively.

Editing SRCBUILD files can easily be done without knowing the exact path in the
repositories directory, the editor is picked for the EDITOR environmental
variable with fallback to Vim.

## OPTIONS

### MAIN

#### positional arguments

    {dist,edit,lint,merge,sane,clean,check}

#### optional arguments

    -h, --help            Show this help message and exit
    --debug               Enable debug messages
    --version             Show SPM Tools version and exits

### DIST MODE

#### positional arguments

    TARGETS               Targets to apply actions on

#### optional arguments

    -h, --help            Show this help message and exit
    -s, --sources         Include all sources in the archive
    -c, --clean           Clean all sources after creating archive
    -d DIRECTORY,
    --directory DIRECTORY Set output directory

### CHECK MODE

#### positional arguments

    TARGETS               Targets to apply actions on

#### optional arguments

    -h, --help            Show this help message and exit
    -f, --fast            Skip some files/links
    -a, --adjust          Adjust target depends
    -D, --depends         Check dependencies of target
    -R, --reverse         Check reverse dependencies of target

### CLEAN MODE

#### optional arguments

    -h, --help            Show this help message and exit

### LINT MODE

#### positional arguments

    TARGETS               Targets to apply actions on

#### optional arguments

    -h, --help            Show this help message and exit
    -m, --man             Check for missing manual page(s)
    -u, --udev            Check for cross-filesystem udev rule(s)
    -s, --symlink         Check for cross-filesystem symlink(s)
    -d, --doc             Check for documentation
    -M, --module          Check for module(s) in non-standard directory
    -f, --footprint       Check for empty footprint
    -b, --builddir        Check for build directory trace(s)
    -a, --all             Perform all checks

### SANE MODE

#### positional arguments

    TARGETS               Targets to apply actions on

#### optional arguments

    -h, --help            Show this help message and exit
    -e, --enable          Check for explicit --enable and --with argument(s)
    -d, --disable         Check for explicit --disable and --without argument(s)
    -n, --null            Check for /dev/null output redirection(s)
    -m, --miantainer      Check for missing maintainer
    -N, --note            Check for FIXME/TODO note(s)
    -v, --variables       Check for essential variables
    -t, --triggers        Check for unnecessary triggers invocation(s)
    -a, --all             Perform all checks

### MERGE MODE

#### optional arguments

    -h, --help            Show this help message and exit

### EDIT MODE

#### positional arguments

    TARGETS               Targets to apply actions on

#### optional arguments

    -h, --help            Show this help message and exit

### WHICH MODE

#### positional arguments

    PATTERN               Pattern to search for in remote targets

#### optional arguments

    -h, --help            Show this help message and exit
    -p, --plain           Print in plain format

### PACK MODE

#### positional arguments

    TARGETS               Targets to apply actions on

#### optional arguments

    -h, --help            Show this help message and exit
    -d DIRECTORY,
    --directory DIRECTORY Set output directory

## EXAMPLES

Create a tarball of all sources, SRCBUILD, patches, etc. of grub and put the
tarball in the current directory:

    sudo spm-tools dist -sc -d=. grub

Run check of runtime dependencies of python, excluding various non-important
files such as headers, and correct them if necessary:

    sudo spm-tools check -faD python

Check for unneeded local targets, in other words - targets that are not required
by other local target:

    spm-tools clean

Run check for possible "bad things" on all local targets to ensure that the
system is in good condition, e.g. no cross-filesystem symlinks which can be
troublesome with a separate /usr partition:

    spm-tools lint -a $(spm local -pn ^)

Run check for possible "bad things" on all remote targets to ensure that the
ports are in good condition, e.g. there are at least 2-variables defined
(version and description):

    spm-tools sane -a $(spm remote -pn ^)

Merge all files backed up by SPM with the original ones:

    sudo spm-tools merge

Edit the glibc SRCBUILD, e.g. to apply some custom configure parameters:

    sudo spm-tools edit glibc

Print full path to vim target:

    spm-tools which -p vim

Backup gcc filese into tarball:

    spm-tools pack gcc

## EXIT STATUS

SPM returns 0 on success and other on failure.

### Unexpected error (1)

This is a general error. Triggered, most likely, by something that SPM is
not able to handle.

### Internal error (2)

This error raises when a dependency, library, or other important thing
is missing or failed.

### CONFIGPARSER (3)

This error raises when, at runtime, the module responsible for parsing the
configuration files fails badly. Its job usually is to parse the main,
repositories and mirrors configuration files.

### SUBPROCESS (4)

This error raises when a subprocess, such as Git or Bash, failed to
execute a sub-command.

### URLLIB (5)

This error raises when, at the prepare stage, the module responsible for
fetching files hits a wall. This can be '404 Not Found' or
'500 Internal Server Error'. For more info visit
http://en.wikipedia.org/wiki/List_of_HTTP_status_codes.

### TARFILE (6)

This error raises when, at the prepare or merge stage, the module
responsible for compressing and decompressing Tar archives fails badly.

### ZIPFILE (7)

This error raises when, at the prepare stage, the module responsible
for compressing and decompressing Zip archives fails badly.

### SHUTIL (8)

This error raises when the module responsible for shell or system
operations fails badly. Its job usually is to copy or remove files and
directories.

### OS (9)

This error raises when the module responsible for system files and
directories information gathering fails badly. Its job usually is to
check if X is file, symbolic link or directory.

### IO (10)

This error raises when there is something wrong with the file/directory
permissions.

### REGEXP (11)

This error raises when the module responsible for regular expressions
matching fails badly. If in doubt you should check the Python Re module
reference at http://docs.python.org/2/library/re.html.

### Interupt signal received (12)

This error raises when the user triggers keyboard interrupt via Ctrl+C key
combination.

## BUGS

### PYTHON MODULES

HTTPS requests do not do any verification of the server's certificate.
For more info visit http://docs.python.org/2/library/urllib2.html. Note that
this concerns only the internal fetcher, thus using external fetcher (curl or
wget) is highly recommended.

There are three tar formats that are supported by the tarfile module. For more
info visit http://docs.python.org/2/library/tarfile.html#supported-tar-formats.
Note that the Zip and XZ formats are supported by SPM, the later via subprocess
calling `tar` or `bsdtar` directly.

### SPM

Single quote inside double quoted text (and vice-versa) in the SRCBUILD variables
break the parser.

## AUTHOR

Ivailo Monev <xakepa10@gmail.com>

## COPYRIGHT

Copyright (c) 2013-2014 Ivailo Monev licensed through the GPLv2 License

## SEE ALSO

spm srcbuild scanelf tar bsdtar xz vim
