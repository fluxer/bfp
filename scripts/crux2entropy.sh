#!/bin/bash

set -e

for repo in $@;do
    rm -rf "$repo"
    git clone "git://crux.nu/ports/$repo.git"
    for pkgfile in $(find "$repo" -name Pkgfile);do
        basedir="$(dirname "$pkgfile")"
        pkg2src "$basedir"
    done
done