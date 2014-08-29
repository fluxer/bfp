## NAME

SRCBUILD - Source Package Manager build recipe

## DESCRIPTION

SRCBUILD is used as a script, a set of instructions, how to build software
using Source Package Manager. Its syntax is Shell (Bash), similar to those
used by Pacman's PKGBUILDs and Gentoo's ebuilds. Common things with the
PKGBUILD format are the version, description, depends, makedepends,
checkdepends, sources, options and backup variables. Common things with the
ebuild format is presence of pre/post actions in the SRCBUILD itself. This
means that everything is in one file, unlike the PKGBUILD format.

The metadata defined in the recipes should contain only one function
(src_install) and two (2) variables (version and description). Optionally
two (2) more functions can be specified (src_compile and src_check) and
five (6) more variable (depends, makedepends, checkdepends, sources, options
and backup). Target name is defined by the directory name in which the target
files are placed in the repository.

In addition six (6) more functions (pre/post_install, pre/post_upgrade and
pre/post_remove) can be defined as pre/post actions to be taken when
software is installed, upgraded or removed. Pre-actions are taken before
the actual install/upgrade/remove is done. Post-actions are taken after the
actual install/upgrade/remove is done.

For easy of use SOURCE_DIR and INSTALL_DIR are exported and can be used
inside the SRCBUILD.

## OPTIONS

### version

Variable defining version of software.

### description

Variable defining description of software.

### depends

Variable defining runtime dependencies of software.

### makedepends

Variable defining build dependencies of software.

### checkdepends

Variable defining check dependencies of software.

### sources

Variable defining sources of software. This includes remote files, such as
tarballs or patches, that should be fetched. Note that local files can be
shipped along the SRCBUILD when needed.

### backup

Variable defining additional files to be backed up when merging software.
Note that all files with .conf extension are automatically backed up.

### options

Variable defining options to be used when building software. It is used
to override the install options specified in the SPM configuration file.
Valid options are:

#### binaries

Strip binary files.

#### shared

Strip shared library files.

#### static

Strip static library files.

#### man

Compress manual page files.

#### mirror

Use mirrors.

#### missing

Ignore missing runtime dependencies.

Note that preceding an option with exclamation mark (!) has the opposite
affect.

#### rpath

Fix RPATH in binaries and libraries

### src_compile

Function defining the instructions to compile the software.

### src_check

Function defining the instructions to check (test) the software.

### src_install

Function defining the instructions to install the software. Note that the
software should be installed in the temporary directory INSTALL_DIR using
DESTDIR or other method depending on the software.

### pre_install

Function defining instructions what to do before installing the target.

### post_install

Function defining instructions what to do after installing the target.

### pre_upgrade

Function defining instructions what to do before upgrading the target.

### post_upgrade

Function defining instructions what to do after upgrading the target.

### pre_remove

Function defining instructions what to do before removing the target.

### post_remove

Function defining instructions what to do after removing the target.

## EXAMPLES

    version=5.14
    description="File type identification utility"
    depends=('zlib' 'glibc')
    makedepends('foo' 'bar')
    # variable expansion, must be preseeded with underscore
    _base="file-$version"
    sources=("ftp://ftp.astron.com/pub/file/$_base.tar.gz"
        "dummy.patch")
    options=('!binaries' '!shared' '!static' 'man' 'mirror' 'missing' '!rpath')
    backup=('etc/bar/baz.conf')
    
    src_compile() {
        # working with full path and variable expansion
        cd "$SOURCE_DIR/$_base"
        patch -Np1 -i "$SOURCE_DIR/dummy.patch"
    
        ./configure --prefix=/usr
        make
    }
    
    src_check() {
        # working with full path (recommended)
        cd "$SOURCE_DIR/file-$version"
        make check
    }
    
    src_install() {
        # working with relative paths is possible too
        cd "file-$version"
        make DESTDIR="$INSTALL_DIR" install 
    }
    
    pre_install() {
        true
    }
    
    # you can re-use functions
    post_install() {
        pre_install
    }
    
    pre_upgrade() {
        true
    }
    
    post_upgrade() {
        true
    }
    
    pre_remove() {
        true
    }
    
    post_remove() {
        true
    }

## AUTHOR

Ivailo Monev <xakepa10@gmail.com>

## COPYRIGHT

Copyright (c) 2013-2014 Ivailo Monev licensed through the GPLv2 License

## SEE ALSO

[spm](spm.html) [spm.conf](spm.conf.html) bash
