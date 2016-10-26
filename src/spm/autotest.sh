#!/bin/bash

# this script is ment to run all possible modes of SPM/SPMT with the
# interpreter passed to this script to check if they (at least) do not trow
# some runtime exception, poor man test-suite. SPM/SPMT do not have to be
# installed but their runtime dependencies must be. if it fails it does no
# cleanup! all short arguments are used instead of shortcuts (such as
# -a/--automake) on purpose as the tests are selective due to some restrictions
# and in addition it ensures that on arguments change the tests fail.

set -e

uid="$(id -u)"
curdir="$(dirname $0)"
rootdir="$curdir/root-$1"
cachedir="$rootdir/cache"
builddir="$rootdir/build"
gpgdir="$rootdir/gpg"
spmargs="--root $rootdir --cache $cachedir --build $builddir --gpg $gpgdir --missing=True --notify=True --scripts=False --ownership=True --debug"
spmtargs="--root $rootdir --debug"
statefile="$rootdir/testrun-$1"

case "$1" in
    *python*) true ;;
    *) echo "Invalid interpreter: $1"
       exit 1 ;;
esac

expectedfailure() {
    if [ "$?" != "$1" ];then
        exit $?
    fi
}

# to ensure that no stray files from previous run are left
make -C "$curdir" clean
mkdir -pv "$rootdir"
touch "$statefile"
# to avoid requirement of installing the libs
ln -svf "$curdir/../libs/libmessage.py" .
ln -svf "$curdir/../libs/libmisc.py" .
ln -svf "$curdir/../libs/libpackage.py" .

# let me build that for ya :)
if ! which scanelf ;then
    "$1" "$curdir/spm.py" $spmargs repo -a
    paxver=$("$1" "$curdir/spm.py" $spmargs remote -pv pax-utils)
    "$1" "$curdir/spm.py" $spmargs source -Cfpc pax-utils
    export PATH="$PATH:$builddir/pax-utils/source/pax-utils-$paxver"
fi

if ! grep -q "SPM REPO" "$statefile" ;then
    echo "=== RUNNING SPM REPO TEST ==="
    "$1" "$curdir/spm.py" $spmargs repo -cspu
    echo "SPM REPO" >> "$statefile"
else
    echo "=== SKIPPING SPM REPO TEST ==="
fi

if ! grep -q "SPM REMOTE" "$statefile" ;then
    echo "=== RUNNING SPM REMOTE TEST ==="
    "$1" "$curdir/spm.py" $spmargs remote -pnvrdDOmcskob ca-certificates
    echo "SPM REMOTE" >> "$statefile"
else
    echo "=== SKIPPING SPM REMOTE TEST ==="
fi

if ! grep -q "SPM SOURCE" "$statefile" ;then
    echo "=== RUNNING SPM SOURCE TEST ==="
    # --depends, --reverse and --remove are not tested!
    "$1" "$curdir/spm.py" $spmargs source -Cfpckim ca-certificates
    echo "SPM SOURCE" >> "$statefile"
else
    echo "=== SKIPPING SPM SOURCE TEST ==="
fi

if ! grep -q "SPM LOCAL" "$statefile" ;then
    echo "=== RUNNING SPM LOCAL TEST ==="
    "$1" "$curdir/spm.py" $spmargs local -pnvRdDOArsf ca-certificates
    echo "SPM LOCAL" >> "$statefile"
else
    echo "=== SKIPPING SPM LOCAL TEST ==="
fi

if ! grep -q "SPM WHO" "$statefile" ;then
    echo "=== RUNNING SPM WHO TEST ==="
    "$1" "$curdir/spm.py" $spmargs who -p ca-certificates
    echo "SPM WHO" >> "$statefile"
else
    echo "=== SKIPPING SPM WHO TEST ==="
fi

if [ "$uid" != "0" ];then
    echo "=== SKIPPING SPMT DIST TEST (REQUIRES ROOT) ==="
elif ! grep -q "SPMT DIST" "$statefile" ;then
    echo "=== RUNNING SPMT DIST TEST (ROOT) ==="
    "$1" "$curdir/tools.py" $spmtargs dist -scd "$rootdir" ca-certificates
    echo "SPMT DIST" >> "$statefile"
else
    echo "=== SKIPPING SPMT DIST TEST (ROOT) ==="
fi

if ! grep -q "SPMT CHECK" "$statefile" ;then
    echo "=== RUNNING SPMT CHECK TEST ==="
    # --depends and --reverse are not tested!
    "$1" "$curdir/tools.py" $spmtargs check ca-certificates || expectedfailure 2
    echo "SPMT CHECK" >> "$statefile"
else
    echo "=== SKIPPING SPMT CHECK TEST ==="
fi

if ! grep -q "SPMT CLEAN" "$statefile" ;then
    echo "=== RUNNING SPMT CLEAN TEST ==="
    "$1" "$curdir/tools.py" $spmtargs clean
    echo "SPMT CLEAN" >> "$statefile"
else
    echo "=== SKIPPING SPMT CLEAN TEST ==="
fi

if ! grep -q "SPMT LINT" "$statefile" ;then
    echo "=== RUNNING SPMT LINT TEST ==="
    "$1" "$curdir/tools.py" $spmtargs lint -musPMfboepnkcD ca-certificates
    echo "SPMT LINT" >> "$statefile"
else
    echo "=== SKIPPING SPMT LINT TEST ==="
fi

if ! grep -q "SPMT SANE" "$statefile" ;then
    echo "=== RUNNING SPMT SANE TEST ==="
    "$1" "$curdir/tools.py" $spmtargs sane -ednmNvtugs ca-certificates
    echo "SPMT SANE" >> "$statefile"
else
    echo "=== SKIPPING SPMT SANE TEST ==="
fi

# TODO: merge, edit

if ! grep -q "SPMT WHICH" "$statefile" ;then
    echo "=== RUNNING SPMT WHICH TEST ==="
    "$1" "$curdir/tools.py" $spmtargs which -cp ca-certificates
    echo "SPMT WHICH" >> "$statefile"
else
    echo "=== SKIPPING SPMT WHICH TEST ==="
fi

if [ "$uid" != "0" ];then
    echo "=== SKIPPING SPMT PACK TEST (REQUIRES ROOT) ==="
elif [ ! -d "$rootdir/var/local/spm/ca-certificates" ];then
    echo "=== SKIPPING SPMT PACK TEST (CA-CERTIFICATES NOT INSTALLED) ==="
elif ! grep -q "SPMT PACK" "$statefile" ;then
    echo "=== RUNNING SPMT PACK TEST ==="
    "$1" "$curdir/tools.py" $spmtargs pack -d "$rootdir" ca-certificates
    echo "SPMT PACK" >> "$statefile"
else
    echo "=== SKIPPING SPMT PACK TEST ==="
fi

if ! "$1" "$curdir/tools.py" online -u 'https://crux.nu/ports/crux-3.2'; then
    echo "=== SKIPPING SPMT PKG TEST (REQUIRES ACCESS TO CRUX SERVER) ==="
elif ! grep -q "SPMT PKG" "$statefile" ;then
    echo "=== RUNNING SPMT PKG TEST ==="
    "$1" "$curdir/tools.py" $spmtargs pkg -d "$rootdir" ca-certificates
    echo "SPMT PKG" >> "$statefile"
else
    echo "=== SKIPPING SPMT PKG TEST ==="
fi

# serve is a blocking and dengerous to run

if ! grep -q "SPMT DISOWNED" "$statefile" ;then
    echo "=== RUNNING SPMT DISOWNED TEST ==="
    "$1" "$curdir/tools.py" $spmtargs disowned -cpd "$rootdir"
    echo "SPMT DISOWNED" >> "$statefile"
else
    echo "=== SKIPPING SPMT DISOWNED TEST ==="
fi

if ! grep -q "SPMT ONLINE" "$statefile" ;then
    echo "=== RUNNING SPMT ONLINE TEST ==="
    "$1" "$curdir/tools.py" $spmtargs online -u https://google.com
    echo "SPMT ONLINE" >> "$statefile"
else
    echo "=== SKIPPING SPMT ONLINE TEST ==="
fi

if [ "$uid" != "0" ];then
    echo "=== SKIPPING SPMT UPGRADE TEST (REQUIRES ROOT) ==="
elif ! grep -q "SPMT UPGRADE" "$statefile" ;then
    echo "=== RUNNING SPMT UPGRADE TEST ==="
    "$1" "$curdir/tools.py" $spmtargs upgrade
    echo "SPMT UPGRADE" >> "$statefile"
else
    echo "=== SKIPPING SPMT UPGRADE TEST ==="
fi

if [ ! -d "$rootdir/var/local/spm/ca-certificates" ];then
    echo "=== SKIPPING SPMT DIGEST TEST (CA-CERTIFICATES NOT INSTALLED) ==="
elif ! grep -q "SPMT DIGEST" "$statefile" ;then
    echo "=== RUNNING SPMT DIGEST TEST ==="
    "$1" "$curdir/tools.py" $spmtargs digest -cvk ca-certificates -d "$rootdir"
    echo "SPMT DIGEST" >> "$statefile"
else
    echo "=== SKIPPING SPMT DIGEST TEST ==="
fi

if [ "$uid" != "0" ];then
    echo "=== SKIPPING SPMT PORTABLE TEST (REQUIRES ROOT) ==="
elif [ ! -d "$rootdir/var/local/spm/ca-certificates" ];then
    echo "=== SKIPPING SPMT PORTABLE TEST (CA-CERTIFICATES NOT INSTALLED) ==="
elif ! grep -q "SPMT PORTABLE" "$statefile" ;then
    echo "=== RUNNING SPMT PORTABLE TEST ==="
    "$1" "$curdir/tools.py" $spmtargs portable ca-certificates -d "$rootdir" || expectedfailure 1
    echo "SPMT PORTABLE" >> "$statefile"
else
    echo "=== SKIPPING SPMT PORTABLE TEST ==="
fi