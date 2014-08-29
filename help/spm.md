## NAME

spm - Source Package Manager

## SYNOPSIS

    spm [-h] [--cache CACHE] [--build BUILD] [--root ROOT]
        [--ignore IGNORE] [--mirror MIRROR] [--timeout TIMEOUT]
        [--external EXTERNAL] [--chost CHOST] [--cflags CFLAGS]
        [--cxxflags CXXFLAGS] [--cppflags CPPFLAGS] [--ldflags LDFLAGS]
        [--makeflags MAKEFLAGS] [--man MAN] [--binaries BINARIES]
        [--shared SHARED] [--static STATIC] [--missing MISSING]
        [--conflicts CONFLICTS] [--backup BACKUP] [--scripts SCRIPTS]
        [--triggers TRIGGERS] [--debug] [--version]
        {repo,remote,source,local,who} ...

## DESCRIPTION

Source Package Manager (SPM) manages targets, or packages, only build from
source code. It fetches, extracts, builds and installs the compiled files
on the system. What it does using different approach is that SPM detects
library dependencies at install time so that dependencies are resolved
in matter of what is needed by the library and binary files of the target
by running `scanelf` on them, checking if the library is in the target itself,
in local (installed) target or doesn't exists. This ensures that all runtime
libraries will be present and the dependencies are not "static", usually
added to metadata file, keeping the system off of broken applications
because of missing runtime dependencies and reducing the work needed on
packaging. Also, it probes for scripting languages such as Bash or Python by
looking for shebangs in the compiled files. Note that extra (runtime time,
as well as make) dependencies can still be specified and are checked for at
the prepare stage. An example is gtk2 - according to Pacman it has the
following dependencies:

	atk pango xorg-libraries cairo gdk-pixbuf

and according to SPM:

	atk pango xorg-libraries cairo gdk-pixbuf bash python2 glib glibc
	fontconfig pixman libpng libxcb libxau libxdmcp harfbuzz libffi pcre
	icu gcc freetype2 zlib bzip2 expat

This ensures that dependencies are utilized at their best for consistency.
Of course this can be achieved with other package managers too but it's
much more work, SPM makes your life easier and keeps your system safe.

All metadata is stored in plain text not database files, while this
increases the disk I/O it makes it possible to easily recover from
disasters and fix issues in cases SPM is not being able to handle such as
missing Python runtime library for whatever the reason.

Remote sources (files, such as tarballs) are being checked after they are
fetched by comparing the remote and local file size instead of using
checksums as most Package Managers do to avoid the need of updating the
checksums in the metadata file (SRCBUILD) whenever a local source file,
shipped with the target files, is updated (makepkg -g >> PKGBUILD anyone?).
Note that security wise this is not a good approach as there is no way to
know whether the remote file size has changed since the last time it was
requested which means an attacker can exploit this and modify the file
content.

Using Source Package Manager and following the LFS/BLFS book you can tailor
a system exactly to your liking without keeping track of what links against
what, and still be able to build, manage and query targets. The only
thing you should know is the order in which targets should be compiled
when doing it from the ground up (as per the LFS book for an example).
Once you have the most essential software on your system and you start
building upon it (following the BLFS book for an example) you rarely will
have to worry about the runtime dependencies as they will be detected for
you. This can reduce the workload when compiling and installing a big stack
of software (X.Org, KDE, GNOME, etc.). However, given the fact that SPM
checks the dependencies, if specified, when doing preparations you can still
order the build process properly by specifying them in the SRCBUILD.

Repositories with target (package) files for the most essential software
are enabled by default but you can maintain your own repositories with Git.

Major libraries version changes will be handled properly too. For an example,
when curl changes the library version and when building curl the reverse
dependencies will be scanned, if SPM is told to, with `scanelf` for 'not found'
which indicates that a runtime library is missing and and the reverse
dependencies of curl will be rebuild if needed automatically for you.
This is done when merging a target/tarball.

On merge, all files with .conf extension will be backed up as
<file>.conf.backup. You can explicitly tell SPM which files to be backed up as
sometimes there are files that need to be backed up, yet they don't have the
.conf extension. Keep in mind that if you merge a target twice the backup files
will be replaced and your custom file will be lost so you have to update the
original or merge the backup with the new file if you want to preserve your
changes.

After compiling and installing the software (to temporary location), a tarball
of the installed files is created. It also contains the information needed for
SPM to know that a target is installed (metadata and footprint). This way if,
for whatever the reason, SPM chokes you can decompress the tarball with:

	tar -xapPhf /var/cache/spm/tarballs/<tarball>

and it will be picked up by SPM as present on the system, no magic tricks needed.
Keep in mind that you may have to execute the following to update the shared
libraries cache:

	ldconfig -r <system_root>

Upon targets merge or removal triggers for updating manual pages, desktop files,
mime and other database will be activated to take care of common actions avoiding
code duplication in pre/post scripts.

Mirrors for sources can be used so that fetching sources is faster and more
reliable, for an example when the upstream servers are down for maintenance.
Several mirrors are enabled by default.

Information about both local and remote targets can be queried with regular
expressions that will match in the target name only, not in the metadata
itself (e.g. in the description). You can also use SPM in your own scripts
by using the plain printing argument which makes it easy to wrap around.

Ignoring missing dependencies, libraries and misc sanity checks fails can
be done by passing the appropriate argument. Check the OPTIONS section
for all options available.

Additional utilities are packed in Source Package Manager Tools to assist in the
system maintenance. You can read more about them in spm-tools(8) manual page.

SPM doesn't implement many features known from other Package Managers such as
target release, home page URL and other common features but some of those may
be implemented later on. 

## OPTIONS

### MAIN

#### positional arguments

    {repo,remote,source,local,who}

#### optional arguments

    -h, --help            Show this help message and exit
    --cache CACHE         Change cache directory
    --build BUILD         Change build directory
    --root ROOT           Change system root directory
    --ignore IGNORE       Change ignored targets
    --mirror MIRROR       Set whether to use mirrors
    --timeout TIMEOUT     Set the connection timeout
    --external EXTERNAL   Set whether to use external fetcher
    --chost CHOST         Change CHOST
    --cflags CFLAGS       Change CFLAGS
    --cxxflags CXXFLAGS   Change CXXFLAGS
    --cppflags CPPFLAGS   Change CPPFLAGS
    --ldflags LDFLAGS     Change LDFLAGS
    --makeflags MAKEFLAGS Change MAKEFLAGS
    --man MAN             Set whether to compress man pages
    --binaries BINARIES   Set whether to strip binaries
    --shared SHARED       Set whether to strip shared libraries
    --static STATIC       Set whether to strip static libraries
    --rpath RPATH         Set whether to strip RPATH
    --missing MISSING     Set whether to ignore missing runtime dependencies
    --conflicts CONFLICTS Set whether to check for conflicts
    --backup BACKUP       Set whether to backup files
    --scripts SCRIPTS     Set whether to execute pre/post script
    --triggers TRIGGERS   Set whether to execute triggers
    --debug               Enable debug messages
    --version             Show SPM version and exit

### REPO MODE

#### optional arguments

    -h, --help            Show this help message and exit
    -c, --clean           Purge repositories
    -s, --sync            Sync repositories
    -p, --prune           Prune old repositories
    -u, --update          Check repositories for updates

### REMOTE MODE

#### positional arguments

    PATTERN               Pattern to search for in remote targets

#### optional arguments

    -h, --help            Show this help message and exit
    -n, --name            Show target name
    -v, --version         Show target version
    -d, --description     Show target description
    -D, --depends         Show target depends
    -m, --makedepends     Show target makedepends
    -c, --checkdepends    Show target checkdepends
    -s, --sources         Show target sources
    -o, --options         Show target options
    -b, --backup          Show target backups
    -p, --plain           Print in plain format

### SOURCE MODE

#### positional arguments

    TARGETS               Targets to apply actions on

#### optional arguments

    -h, --help            Show this help message and exit
    -C, --clean           Purge sources and compiled files of target
    -p, --prepare         Prepare sources of target
    -c, --compile         Compile sources of target
    -k, --check           Check sources of target
    -i, --install         Install compiled files of target
    -m, --merge           Merge compiled files of target to system
    -r, --remove          Remove compiled files of target from system
    -D, --depepnds        Consider dependency targets
    -R, --reverse         Consider reverse dependency targets
    -u, --update          Apply actions only if update is available
    -a, --automake        Short for clean, prepare, compile, install and merge

### LOCAL MODE

#### positional arguments

    PATTERN               Pattern to search for in local targets

#### optional arguments

    -h, --help            Show this help message and exit
    -n, --name            Show target name
    -v, --version         Show target version
    -d, --description     Show target description
    -D, --depends         Show target depends
    -r, --reverse         Show target reverse depends
    -s, --size            Show target size
    -f, --footprint       Show target footprint
    -p, --plain           Print in plain format

### WHO MODE

#### positional arguments
    PATTERN               Pattern to search for in local targets

#### optional arguments

    -h, --help            Show this help message and exit
    -p, --plain           Print in plain format

## EXAMPLES

Clean, sync repositories and check for updates:

	sudo spm repo -csu

Print all remote targets names:

	spm remote -n ^

Clean, prepare, build dependencies, compile, install and merge remote
targets:

	spm source -CpDcim file gawk

Clean, prepare, compile dependencies, compile target, install, merge,
re-compile reverse dependencies if needed of all local targets but only
if outdated and don't execute pre/post actions:

	sudo spm --scripts=False source -aDRu world

Remove grub and the targets that depend on it (reverse dependencies):

	sudo spm source -rR grub

Print bash, glibc and ncurses targets name and version in
plain list format:

	spm local -nvp 'bash$|glibc|ncurses'

Print the owner of 'bin/bash':

	spm who 'bin/bash\b'

Note that all modes, except source which accepts basename and paths, accept
regexp similar to those found in Perl. For more information visit
http://docs.python.org/2/library/re.html.

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

[spm.conf](spm.conf.html) [srcbuild](srcbuild.html) [spm-tools](spm-tools.html) scanelf tar bsdtar xz ldconfig file man-db git
