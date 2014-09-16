## NAME

spm.conf - Source Package Manager configuration file

## DESCRIPTION

spm.conf is the configuration file used by Source Package Manager. It is
divided into sections - spm, prepare, compile, install and merge. These
sections represent options used at different stage of the software
building process.

## OPTIONS

### CACHE_DIR

Set the directory where the repositories, sources and tarballs will be
placed. The repositories directory holds all recipes (SRCBUILD) to build
targets. The sources directory is the place where all source tarballs are
fetched. The tarballs directory holds all compressed archives which are
ready to be merged.

Default: /var/cache/spm

### BUILD_DIR

Set the directory where the sources should be prepared and compiled. This
directory may consume a lot of space over time so you may want to change it.

Default: /var/tmp/spm

### ROOT_DIR

Set the system root directory. Unless you want to bootstrap a system with
SPM it should not be changed. ROOT_DIR must include backslash at the end
of the string, e.g. /home/joe/bootstrap/.

Default: /

### IGNORE

Set targets to be ignored when building and removing.

Default: filesystem

### OFFLINE

Set whether to use internet or not. If set to true sources will be fetched
from internet, otherwise local sources (if they exist) will be used. This
Option is meaningfull only in cases when the internet connection is
not good and it takes a lot of time to ping the servers and you know
that this is not required.

Default: False

### MIRROR

Set whether to use mirrors or not. If set to true mirrors will be pinged
and sources fetched from them if available. As fallback is used the
original source defined in the build script (SRCBUILD). 

Default: True

### TIMEOUT

Set the time in seconds to wait before bailing out when mirrors and
internet connection are checked.

Default: 30

### EXTERNAL

Set whether to use external sources fetcher or not. If set to true `curl`
or `wget` will be used. As fallback is used built-in urllib implementation
which does not support resuming. 

Default: True

### CHOST

Set the environmental variable CHOST when building software. The CHOST
flag specifies the target hardware platform, (ppc, i386, i586 etc), so
that the code is compiled with the right instruction set.

Default: #MACHINE#

### CFLAGS

Set the environmental variable CFLAGS when building software. The CFLAGS
flag specifies desired optimization/CPU instruction for C code.

Default: -march=#ARCH# -mtune=native -O2 -pipe -fstack-protector --param=ssp-buffer-size=4

### CXXFLAGS

Set the environmental variable CXXFLAGS when building software. The CXXFLAGS
flag specifies desired optimization/CPU instruction for C++ code.

Default: -march=#ARCH# -mtune=native -O2 -pipe -fstack-protector --param=ssp-buffer-size=4

### CPPFLAGS

Set the environmental variable CPPFLAGS when building software. The CPPFLAGS
flag specifies desired C PreProcessor instruction for C code.

Default: -Wformat -Werror=format-security -D_FORTIFY_SOURCE=2


### LDFLAGS

Set the environmental variable LDFLAGS when building software. The LDFLAGS
flag specifies desired linker options.

Default: -Wl,--hash-style=gnu -Wl,--as-needed

### MAKEFLAGS

Set the environmental variable MAKEFLAGS when building software. The MAKEFLAGS
flag specifies desired `make` options.

Default: -j#JOBS#

### COMPRESS_MAN

Set whether to compress manual pages. Doing so will save you some space.

Default: True

### STRIP_BINARIES

Set whether to strip all symbols from binaries. This reduces the size of
the binaries but it may corrupt some of them.

Default: True

### STRIP_SHARED

Set whether to strip all symbols that are not needed for relocation
processing from shared libraries. This reduces the size of the shared
libraries but it may corrupt some of them.

Default: True

### STRIP_STATIC

Set whether to strip debugging symbols from static libraries. This reduces
the size of the static libraries but it may corrupt some of them.

Default: True

### STRIP_RPATH

Set whether to strip insecure RPATH from binaries and libraries. This reduces
the chance for exploiting them but it may corrupt some of them.

Default: True

### PYTHON_COMPILE

Set whether to compile Python files into cached byte-code. This ensures
consistency that SPM keeps track of .pyc/.pyo files and removes then when
the target they are owned by is removed from the system as well as speeds up
initial usage of Python modules.

Default: True

### IGNORE_MISSING

Set whether to ignore missing runtime dependencies. This is used only as a
workaround for false positives.

Default: False

### CONFLICTS

Set whether to check for conflicting files/links when merging targets.

Default: True

### BACKUP

Set whether to backup files when merging targets.

Default: True

### SCRIPTS

Set whether to execute pre/post script actions when merging targets.

Default: True

### TRIGGERS

Set whether to execute triggers when merging targets.

Default: True

## EXAMPLES

[spm]

CACHE_DIR = /var/cache/spm

BUILD_DIR = /var/tmp/spm

ROOT_DIR = /

IGNORE = glibc zlib bash

## FILES

/etc/spm.conf

/etc/spm/repositories.conf

/etc/spm/mirrors.conf

## AUTHOR

Ivailo Monev <xakepa10@gmail.com>

## COPYRIGHT

Copyright (c) 2013-2014 Ivailo Monev licensed through custom License

## SEE ALSO

[spm](spm.html) [srcbuild](srcbuild.html) curl wget gcc ld make strip
