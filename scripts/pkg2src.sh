#!/bin/bash

# pkg2src - Pkgfile to SRCBUILD convertor
# Copyright (C) 2012-2017 Ivailo Monev (a.k.a SmiL3y)

export LANG=C LC_ALL=C
unset ALL_OFF BOLD BLUE GREEN RED YELLOW
if [[ -t 2 ]]; then
    # prefer terminal safe colored and bold text when tput is supported
    if tput setaf 0 &>/dev/null; then
        ALL_OFF="$(tput sgr0)"
        BOLD="$(tput bold)"
        BLUE="${BOLD}$(tput setaf 4)"
        GREEN="${BOLD}$(tput setaf 2)"
        RED="${BOLD}$(tput setaf 1)"
        YELLOW="${BOLD}$(tput setaf 3)"
    else
        ALL_OFF="\e[1;0m"
        BOLD="\e[1;1m"
        BLUE="${BOLD}\e[1;34m"
        GREEN="${BOLD}\e[1;32m"
        RED="${BOLD}\e[1;31m"
        YELLOW="${BOLD}\e[1;33m"
    fi
fi
readonly ALL_OFF BOLD BLUE GREEN RED YELLOW

msg() {
    printf "${ALL_OFF}${GREEN}=>${ALL_OFF}${BOLD} ${@}${ALL_OFF}\n"
}

warn() {
    printf "${ALL_OFF}${YELLOW}=>${ALL_OFF}${BOLD} ${@}${ALL_OFF}\n" >&2
}

error() {
    printf "${ALL_OFF}${RED}=>${ALL_OFF}${BOLD} ${@}${ALL_OFF}\n" >&2
    return 1
}

die() {
    printf "${ALL_OFF}${RED}=>${ALL_OFF}${BOLD} Hewston, we have a problem${ALL_OFF}\n" >&2
    exit 1
}


for pkg in "${@:-.}";do
    pkgfile="$pkg/Pkgfile"
    srcbuild="$pkg/SRCBUILD"

    if [ ! -f "$pkgfile" ];then
        warn "Give me a directory with Pkgfile"
        continue
    fi

    msg "Preparing.."
    name="$(. $pkgfile && echo $name)"
    if [ -z "$name" ];then
        warn "Sourcing $pkgfile failed or empty name"
        continue
    fi
    cp "$pkgfile" "$srcbuild" || die

    msg "Adjusting.."
    sed -e "s|\$name|$name|g" -e "s|\${name}|$name|g" \
        -e 's|source=(|sources=(|g' \
        -e 's|$SRC|$SOURCE_DIR|g' -e 's|${SRC}|$SOURCE_DIR|g' \
        -e 's|$PKG|$INSTALL_DIR|g' -e 's|${PKG}|$INSTALL_DIR|g' \
        -e 's|build()|src_install()|g' -e 's|build ()|src_install()|g' \
        -e 's/ || return 1//g' \
        -i  "$srcbuild" || die
    description="$(grep '# Description: ' "$srcbuild" | sed 's|# Description: ||')"
    depends="$(grep '# Depends on: ' "$srcbuild" | sed 's|# Depends on: ||;s|, | |g')"
    sed "/release=.*/a description=\"$description\"" -i "$srcbuild" || die
    if [ -n "$depends" ];then
        sed "/description=.*/a makedepends=\($depends\)" -i "$srcbuild" || die
    fi
    sed '/name=/d;/# Description: /d;/Depends on: /d' -i "$srcbuild" || die
    if [ -f "$pkg/.nostrip" ];then
        sed "release=.*/a options=\(debug\)" -i "$srcbuild" || die
    fi

    msg "Cleaning up.."
    rm -f "$pkgfile" "$pkg/"{.footprint,.md5sum,.nostrip,*.last} || die
done
