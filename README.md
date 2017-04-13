## Status

[ ![Codeship Status for fluxer/bfp](https://codeship.com/projects/123e70d0-af99-0132-594f-5edd39caaea8/status?branch=master)](https://codeship.com/projects/69262)

## About

The BFP project started as a tool set for a custom distribution that was
supposed to be as close to as possbile to
[LFS](http://www.linuxfromscratch.org/lfs/)/
[BLFS](http://www.linuxfromscratch.org/blfs/) the only difference being
automation on per-software bases and filling some gaps like updating caches
and databases based on the installed software content without any interaction
from the user nor knowledge about such from the so called packagers. If you are
a thinkerer who likes to play with Linux then you are most likely going to find
use for what it can offer.

It is split into libraries and frontends to allow people to use it the way they
see fit. The project has evolved much over the years but simplicity and tasks
automation is and always will ramain prime goals of the project.

The Package Manager is (or was) one of a kind - it does much more then it
should do but there are good reasons for doing so. Simply put it is a mix of
features and ideas from [Dpkg](https://en.wikipedia.org/wiki/Dpkg),
[Pacman](https://www.archlinux.org/pacman/) and
[Portage](https://wiki.gentoo.org/wiki/Portage) with its own twist.

The [Initial RAM filesystem](https://en.wikipedia.org/wiki/Initramfs) tools are
intended to make small and fast booting [Linux kernel](https://www.kernel.org/)
images fuzz free given the current state of the system. For that it uses only
Busybox and does as little as possible when the system is initialized from the
generated kernel images.

The manul pages for the related tools, formats, etc. go into deatils about what,
how and why they do so. If you have read so far you should probably read them
too.

During its course of history this project has included other tools and ideas
such as Live CD/DVD build tool, Qt/GTK+/curses interfaces for SPM, software
build bot, hardware events handler, partitions manager, verbose errors
reporting from libraries/frontends and other stuff that have been prototyped,
implemented and dropped off intirely. Some ideas have been forged into
sub-projects, some have not even been made public but what you see is what you
get.

## Requirements

The following software is required:

### Runtime

[Coreutils](https://www.gnu.org/software/coreutils/) (or [Busybox](http://www.busybox.net/)),
[kmod](https://www.kernel.org/pub/linux/utils/kernel/kmod/) (or [Busybox](http://www.busybox.net/)),
[Findutils](http://www.gnu.org/software/findutils/) (or [Busybox](http://www.busybox.net/)),
[Busybox](http://www.busybox.net/),
[GNU Tar](https://www.gnu.org/software/tar/) (or [Busybox](http://www.busybox.net/)/[libarchive](http://www.libarchive.org/)),
[GNU Binutils](https://www.gnu.org/software/binutils/) (or [elfutils](https://fedorahosted.org/elfutils/)),
[file](http://darwinsys.com/file/),
[GNU Bash](https://www.gnu.org/software/bash/) (or [MirBSD Korn Shell](https://www.mirbsd.org/mksh.htm)),
[Git](http://git-scm.com/),
[GnuPG](https://www.gnupg.org/),
[Python](https://www.python.org/),
[GNU C Library](http://www.gnu.org/software/libc/) (or [uClibc](http://www.uclibc.org/)/[musl libc](http://www.musl-libc.org/)),

WARNING: gzip/bzip2 archives compression and decompression with Busybox is not
supported because `-k` and `--keep` are ommited in the respective applets
implementations.

### Build time

[Perl](https://www.perl.org/)

How and where from you will obtain those is up to you, altought compatibility
with Busybox, GNU and POSIX tools is prime goal but not guaranteed so for an
example some old versions or even build configuration of those may not support
all required features.

## Building and installing

To build and install all sub-projects all you have to do is issue the following
command:

```
make
sudo make install
```

Alternatively to build and install against Python 3:

```
make PYTHON=python3
sudo make PYTHON=python3 install
```

If you did change the .py files do the following prior to building and
installing:

```
make sources
```

## Contributors

### Current contributors

- Ivailo Monev (a.k.a. SmiL3y) <xakepa10@laimg.moc>

### Past contributors

- David (a.k.a. Anon KS) <noobanonks@gmail.com>
- pablokal, handy, ArchVortex and other [ArchBang](http://www.archbang.org/)
forums users
- Jubei Mitsuyoshi
- Marcus (a.k.a. artoo/udeved) <udeved@openrc4arch.site40.net>
- Adil Ünal (a.k.a. turkbits) <turkbits@turkbits.net>

If you think you have the right to be mentioned here but you are not feel free
to contact us!
