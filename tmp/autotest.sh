#!/bin/bash

# this script is ment to run all possible modes of SPM/SPMT with the interpreter
# passed to this script to check if they (at least) they do not trow some
# runtime exception, poor man test-suite. SPM/SPMT do not have to be installed
# but their runtime dependencies must be. if it fails it does no cleanup! all
# short arguments are used instead of shortcuts (such as -a/--automake) on
# purpose as the tests are selective due to some restrictions and in addition
# it ensures that on arguments change the tests fail.

set -e

uid="$(id -u)"
curdir="$(dirname $0)"
rootdir="$curdir/root"
cachedir="$rootdir/cache"
builddir="$rootdir/build"
gpgdir="$rootdir/gpg"
spmargs="--root $rootdir --cache $cachedir --build $builddir --gpg $gpgdir --missing=True"
spmtargs=""

case "$1" in
    *python*) true ;;
    *) echo "Invalid interpreter: $1"
       exit 1
esac

mkdir -pv "$rootdir"
touch "$rootdir/testrun"
# to avoid requirement of installing the libs
ln -svf "$curdir/../libs/libmisc.py" .
ln -svf "$curdir/../libs/libpackage.py" .
# to ensure that no stray files from previous run are left
make -C "$curdir" clean

if ! grep -q "SPM REPO" "$rootdir/testrun" ;then
    echo "=== RUNNING SPM REPO TEST ==="
    "$1" "$curdir/spm.py" $spmargs repo -a
    echo "SPM REPO" >> "$rootdir/testrun"
else
    echo "=== SKIPPING SPM REPO TEST ==="
fi

if ! grep -q "SPM REMOTE" "$rootdir/testrun" ;then
    echo "=== RUNNING SPM REMOTE TEST ==="
    "$1" "$curdir/spm.py" $spmargs remote -pnvrdDmcskob zlib
    echo "SPM REMOTE" >> "$rootdir/testrun"
else
    echo "=== SKIPPING SPM REMOTE TEST ==="
fi

if ! grep -q "SPM SOURCE" "$rootdir/testrun" ;then
    echo "=== RUNNING SPM SOURCE TEST ==="
    # --depends, --reverse and --remove are not tested!
    "$1" "$curdir/spm.py" $spmargs source -Cpckima zlib
    echo "SPM SOURCE" >> "$rootdir/testrun"
else
    echo "=== SKIPPING SPM SOURCE TEST ==="
fi

# binary mode ain't much due to single mirror

if ! grep -q "SPM LOCAL" "$rootdir/testrun" ;then
    echo "=== RUNNING SPM LOCAL TEST ==="
    "$1" "$curdir/spm.py" $spmargs local -pnvRdDrsf zlib
    echo "SPM LOCAL" >> "$rootdir/testrun"
else
    echo "=== SKIPPING SPM LOCAL TEST ==="
fi

if ! grep -q "SPM WHO" "$rootdir/testrun" ;then
    echo "=== RUNNING SPM WHO TEST ==="
    "$1" "$curdir/spm.py" $spmargs who -p zlib
    echo "SPM WHO" >> "$rootdir/testrun"
else
    echo "=== SKIPPING SPM WHO TEST ==="
fi

if [ "$uid" != "0" ];then
    echo "=== SKIPPING SPMT DIST TEST (REQUIRES ROOT) ==="
elif ! grep -q "SPMT DIST" "$rootdir/testrun" ;then
    echo "=== RUNNING SPMT DIST TEST (ROOT) ==="
    "$1" "$curdir/tools.py" dist -scd "$rootdir" zlib
    echo "SPMT DIST" >> "$rootdir/testrun"
else
    echo "=== SKIPPING SPMT DIST TEST (ROOT) ==="
fi

if ! grep -q "SPMT CHECK" "$rootdir/testrun" ;then
    echo "=== RUNNING SPMT CHECK TEST ==="
    # --adjust, --depends and --reverse are not tested!
    "$1" "$curdir/tools.py" check -f zlib
    echo "SPMT CHECK" >> "$rootdir/testrun"
else
    echo "=== SKIPPING SPMT CHECK TEST ==="
fi

if ! grep -q "SPMT CLEAN" "$rootdir/testrun" ;then
    echo "=== RUNNING SPMT CLEAN TEST ==="
    "$1" "$curdir/tools.py" clean
    echo "SPMT CLEAN" >> "$rootdir/testrun"
else
    echo "=== SKIPPING SPMT CLEAN TEST ==="
fi

if ! grep -q "SPMT LINT" "$rootdir/testrun" ;then
    echo "=== RUNNING SPMT LINT TEST ==="
    "$1" "$curdir/tools.py" lint -musdMfboepnkcD zlib
    echo "SPMT LINT" >> "$rootdir/testrun"
else
    echo "=== SKIPPING SPMT LINT TEST ==="
fi

if ! grep -q "SPMT SANE" "$rootdir/testrun" ;then
    echo "=== RUNNING SPMT SANE TEST ==="
    "$1" "$curdir/tools.py" sane -ednmNvtugs zlib
    echo "SPMT SANE" >> "$rootdir/testrun"
else
    echo "=== SKIPPING SPMT SANE TEST ==="
fi

# TODO: merge, edit

if ! grep -q "SPMT WHICH" "$rootdir/testrun" ;then
    echo "=== RUNNING SPMT WHICH TEST ==="
    "$1" "$curdir/tools.py" which -cp zlib
    echo "SPMT WHICH" >> "$rootdir/testrun"
else
    echo "=== SKIPPING SPMT WHICH TEST ==="
fi

if ! grep -q "SPMT PACK" "$rootdir/testrun" ;then
    echo "=== RUNNING SPMT PACK TEST ==="
    "$1" "$curdir/tools.py" pack -d "$rootdir" zlib
    echo "SPMT PACK" >> "$rootdir/testrun"
else
    echo "=== SKIPPING SPMT PACK TEST ==="
fi

if ! grep -q "SPMT PKG" "$rootdir/testrun" ;then
    echo "=== RUNNING SPMT PKG TEST ==="
    "$1" "$curdir/tools.py" pkg -d "$rootdir" zlib
    echo "SPMT PKG" >> "$rootdir/testrun"
else
    echo "=== SKIPPING SPMT PKG TEST ==="
fi

# serve is a blocking and dengerous to run

if ! grep -q "SPMT DISOWNED" "$rootdir/testrun" ;then
    echo "=== RUNNING SPMT DISOWNED TEST ==="
    "$1" "$curdir/tools.py" disowned -cpd "$rootdir"
    echo "SPMT DISOWNED" >> "$rootdir/testrun"
else
    echo "=== SKIPPING SPMT DISOWNED TEST ==="
fi

# TODO: upload