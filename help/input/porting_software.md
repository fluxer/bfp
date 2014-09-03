## Things you should know before getting started

You will have to keep in mind the following hints before diving into software
porting:

- some ports are bundled in a multi-port, xorg-libraries is a good example
- don't build documentation except man pages and in some cases example files
- if software offers check via test suite use it
- don't put ports from the base group in the makedepend array
- install software to */* not */usr*
- glibc supports Linux Kernel version greater or equal to 3.12.0

## Toolchain build order

- linux

- glibc

- binutils

- gcc

- binutils

- glibc

**Tip:** There is an alias named *toolchain* which you can make use of

## Tools of the trade

Source Package Manager is the package manager that Tiny GNU/Linux uses. If you
are not familiar with it read [this](spm.html) and [this](srcbuild.html) page.

## Getting your hands dirty

### Porting software

Porting software that is not maintained in the official repositories can be
hard for new-commers but essentially you should just know the dependencies
needed for the software to build, you can search the
[LFS](http://www.linuxfromscratch.org/lfs/view/development/) or
[BLFS](http://www.linuxfromscratch.org/blfs/view/svn/) books for instructions.
Also see how the Tiny GNU/Linux ports are named and what they provide as the
multi-ports ship different software all-together such as xorg-fonts.

The easiest way to port software is to download package files from
[Arch Linux](https://www.archlinux.org/) and adjust them properly. First step
is fetch the packages files, [spm-tools](spm-tools.html) can help you with the
task. For converting them a script is provided with SPM - pkg2src - which you
should point to the directory with the downloaded files. It does most of the
dirty work but you may want to review the resulting [SRCBUILD](srcbuild.html).

Next satisfy the dependencies by searching what is available in the
repositories and what the software needs, porting more packages to satisfy them
may be needed too. Check if the software offers test suite, if yes add
src_check() function if not present.

Finally build the software and test how it works, if all goes well you can send
your port to the ports and repository maintainers, just take a look at the
[contributors](contributors.html).

### Tracking dependencies

If you find that a package fails to compile with a message like this:

> *** The required package exo-1 was not found on your system.
> *** Please install exo-1 (atleast version 0.7.1) or adjust
> *** the PKG_CONFIG_PATH environment variable if you
> *** installed the package in a nonstandard prefix so that
> *** pkg-config is able to find it.

even tought you know that the package is installed you can use this:

    pkg-config --cflags exo-1

and will get something like this:

> Package xproto was not found in the pkg-config search path.
> Perhaps you should add the directory containing `xproto.pc'
> to the PKG_CONFIG_PATH environment variable
> Package 'xproto', required by 'xau', not found

In this case the xorg-protocol-headers package is missing which provides
xproto. Adding xorg-protocol-headers to the makedepends array will fix that.
If everything is fine you will get something like the following output:

> -pthread -I/include/exo-1 -I/include/gtk-2.0 -I/lib/gtk-2.0/include
> -I/include/pango-1.0 -I/include/atk-1.0 -I/include/cairo
> -I/include/pixman-1 -I/include/libpng15 -I/include/gdk-pixbuf-2.0
> -I/include/libpng15 -I/include/pango-1.0 -I/include/harfbuzz
> -I/include/pango-1.0 -I/include/freetype2 -I/include/xfce4
> -I/include/glib-2.0 -I/lib/glib-2.0/include

by running a pkg-config check again.

### Checking for conf files

Config files of packages need to be backed up on upgrade and since SPM has this
feature we should make use of it. To search for configs you can use the
following command:

    spm local -fp package_name | grep conf

The output of this command should be only config files and those should go to
the backup array in the SRCBUILD of the port. If you get lots of output you
can strip it a little bit:

    spm local -fp package_name | grep conf | grep etc

or:

    spm local -fp package_name | grep conf | grep -v -e pkgconfig -e locale -e bin -e sbin

But keep in mind that conf files should be backed up **only** if there is no
way to override the behavior of the main conf file except editing it, i.e.
there is no */etc/foo.d*.

### Checking for manual pages

Shipping [manual pages](http://en.wikipedia.org/wiki/Man_page) is important but
sometimes they are not generated because libxml2, docbook-xml, docbook-xsl,
asciidoc or other software is missing. To make sure that manual pages are
installed you can use this:

    spm local -fp package_name | grep share/man

If there is not output you should check if the software has the options to
generate manual pages, if there is but they are not generated at compile time
make sure that the dependencies are satisfied and optionally check for
"--enable-doc" or "--enable-man" in the configure script output of the software.

### Sources

Short URLs for Sourceforge.net downloads as follows:

> http://prdownloads.sourceforge.net/project/file
>
> http://downloads.sourceforge.net/project/file

Example:

> http://prdownloads.sourceforge.net/lxde/gpicview-0.2.3.tar.gz

Prefering [XZ](http://tukaani.org/xz/) and [Bzip2](http://www.bzip.org/)
tarballs over [gzip](http://www.gzip.org/) is recommended to reduce the
bandwidth required for fetching sources.
