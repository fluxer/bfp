## Requirements

The following table illustrates the software requirements:

| binary/library |     origin    |  alternative  |        required by       |           required at          |
|:--------------:|:-------------:|:-------------:|--------------------------|:------------------------------:|
|     parted     |   GNU Parted  |               |          cparted         |             runtime            |
|    pyparted    |    pyparted   |               |          cparted         |             runtime            |
|      cpio      |   Coreutils   |    Busybox    |     lsinitfs/mkinitfs    |             runtime            |
|     depmod     |      kmod     |    Busybox    |         mkinitfs         |             runtime            |
|    ldconfig    | GNU C Library | uClibc, musl? |                          |             runtime            |
|      find      |   Findutils   |    Busybox    |         mkinitfs         |             runtime            |
|     lddtree    | PaX Utilities |               |         mkinitfs         |             runtime            |
|     busybox    |    Busybox    |               |         mkinitfs         |             runtime            |
|       tar      |    GNU Tar    |    Busybox    |          libmisc         | runtime, alternative ot bsdtar |
|     bsdtar     |   LibArchive  |               |          libmisc         |   runtime, alternative ot tar  |
|     scanelf    | PaX Utilities |               |          libmisc         |             runtime            |
|      mount     |   util-linux  |    Busybox    |          libmisc         |             runtime            |
|     umount     |   util-linux  |    Busybox    |          libmisc         |             runtime            |
|    libmagic    |      file     |               |         libmagic         |             runtime            |
|      bash      |    GNU Bash   |               | libmisc, libspm, srcmake |             runtime            |
|       git      |      Git      |               |     libspm, spm-tools    |             runtime            |

NOTE: it currently lacks optional and build time software dependencies

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
contact us!
