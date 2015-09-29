## Status

[ ![Codeship Status for fluxer/bfp](https://codeship.com/projects/123e70d0-af99-0132-594f-5edd39caaea8/status?branch=master)](https://codeship.com/projects/69262)

## Requirements

The following software is required:

### Runtime

[Coreutils](https://www.gnu.org/software/coreutils/) (or [Busybox](http://www.busybox.net/)),
[kmod](https://www.kernel.org/pub/linux/utils/kernel/kmod/) (or [Busybox](http://www.busybox.net/)),
[Findutils](http://www.gnu.org/software/findutils/) (or [Busybox](http://www.busybox.net/)),
[Busybox](http://www.busybox.net/),
[GNU Tar](https://www.gnu.org/software/tar/) (or [Busybox](http://www.busybox.net/)/[libarchive](http://www.libarchive.org/)),
[PaX Utilities](https://wiki.gentoo.org/wiki/Hardened/PaX_Utilities),
[file](http://darwinsys.com/file/),
[GNU Bash](https://www.gnu.org/software/bash/),
[Git](http://git-scm.com/),
[GnuPG](https://www.gnupg.org/),
[Python](https://www.python.org/),
[GNU C Library](http://www.gnu.org/software/libc/) (or [uClibc](http://www.uclibc.org/)/[musl libc](http://www.musl-libc.org/)),
[systemd](http://www.freedesktop.org/wiki/Software/systemd/) (or [eudev](https://github.com/gentoo/eudev))

### Build time

[Perl](https://www.perl.org/),
[Cython](http://cython.org/),
[gettext](https://www.gnu.org/software/gettext/)

How and where from you will obtain those is up to you, altought compatibility
with Busybox, GNU and POSIX tools is prime goal but not guaranteed so for an
example some old versions or even build configuration of those may not support
all required features.

## Building and installing

The build system requires Cython, it translates the Python files into C code
and from which shared modules and binaries are build. To build and install all
sub-projects all you have to do is issue the following command:

```
make
sudo make install
```

Alternatively to build and install against Python 3:

```
make PYTHON=python3
sudo make PYTHON=python3 install
```

## Contributors

### Current contributors

- Ivailo Monev (a.k.a. SmiL3y) <xakepa10@gmail.com>

### Past contributors

- David (a.k.a. Anon KS) <noobanonks@gmail.com>
- pablokal, handy, ArchVortex and other [ArchBang](http://www.archbang.org/)
forums users
- Jubei Mitsuyoshi
- Marcus (a.k.a. artoo/udeved) <udeved@openrc4arch.site40.net>
- Adil Ünal (a.k.a. turkbits) <turkbits@turkbits.net>

If you think you have the right to be mentioned here but you are not feel free
to contact us!
