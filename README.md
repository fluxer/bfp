## Status

[ ![Codeship Status for fluxer/bfp](https://codeship.com/projects/123e70d0-af99-0132-594f-5edd39caaea8/status?branch=master)](https://codeship.com/projects/69262)

## Requirements

The following software is required:

### Runtime

GNU Parted,
pyparted,
Coreutils,
kmod (or Busybox),
Findutils (or Busybox),
Busybox,
GNU Tar (or Busybox/LibArchive),
PaX Utilities,
file,
GNU Bash,
Git,
GnuPG,
Python,
GNU C Library (alternatively uClibc, musl, etc.)

### Build time

Perl
Cython

How and where from you will obtain those is up to you, altought compatibility
with Busybox, GNU and POSIX tools is prime goal but not guaranteed so for an
example some old versions or even build configuration of those may not support
all required features.

## Building and installing

The build system supports two type of builds - with Cython and with Nuitka.
By default Nuitka is used, it translates the Python files into C/C++ code and
it builds that into modules/executables. It can be significantly slower,
especially if LLVM's clang/clang++ is used. To avoid slow build times or
requirement of C++ compiler Cython can be used.

If you want to build with Cython instead of Nuitka then use the cython target:

```
make cython
sudo make install
```

else:

```
make
sudo make install
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
