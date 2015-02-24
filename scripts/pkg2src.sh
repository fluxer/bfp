#!/bin/bash

# pkg2src - PKGBUILD to SRCBUILD convertor
# Copyright (C) 2013-2015 Ivailo Monev (a.k.a SmiL3y)

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
    pkgbuild="$pkg/PKGBUILD"

    if [[ ! -f $pkgbuild ]];then
        warn "Give me a directory with PKGBUILD"
        continue
    fi

    msg "Checking $pkgbuild.."
    if [[ -n $(grep -e 'pkgbase=' -e '^package_' "$pkgbuild") ]];then
        warn "Multi-package, I can not handle that"
        continue
    fi

    if [[ $(find "$pkg" -name '*.install' | wc -l) -gt 1 ]];then
        warn "Multi-install files, I can not handle that"
        continue
    fi

    msg "Preparing.."
    pkgname="$(. $pkgbuild && echo $pkgname)"
    if [ -z "$pkgname" ];then
        warn "Sourcing $pkgbuild failed or empty pkgname"
        continue
    fi
    url="$(. $pkgbuild && echo $url)"
    if [ -z "$url" ];then
        warn "Sourcing $pkgbuild failed or empty url"
        continue
    fi
    script=$(find "$pkg" -name '*.install')
    mv "$pkg/PKGBUILD" "$pkg/SRCBUILD" || die

    msg "Adjusting.."
    sed -e "s|\$pkgname|$pkgname|g" -e "s|\${pkgname}|$pkgname|g" \
        -e 's|pkgver=|version=|g' -e 's|$pkgver|$version|g' -e 's|${pkgver}|$version|g' \
        -e 's|$_pkgver|$_version|g' -e 's|${_pkgver}|$_version|g' \
        -e 's|pkgdesc=|description=|g' \
        -e 's|source=(|sources=(|g' \
        -e 's|$srcdir|$SOURCE_DIR|g' -e 's|${srcdir}|$SOURCE_DIR|g' \
        -e 's|$pkgdir|$INSTALL_DIR|g' -e 's|${pkgdir}|$INSTALL_DIR|g' \
        -e 's|build()|src_compile()|g' -e 's|check()|src_check()|g' -e 's|package()|src_install()|g' \
        -e 's|msg |echo |g' -e 's|msg2 |echo -e |g' \
        -e 's|$CARCH|$(uname -m)|g' -e 's|${CARCH}|$(uname -m)|g' \
        -e 's/ || return 1//g' \
        -e 's|$startdir/src|$SOURCE_DIR|g' -e 's|${startdir}/src|$SOURCE_DIR|g' \
        -e 's|$startdir/pkg|$INSTALL_DIR|g' -e 's|${startdir}/pkg|$INSTALL_DIR|g' \
        -e "s|\$pkgbase|$pkgname|g" -e "s|\${pkgbase}|$pkgname|g" \
        -e "s|\$url|$url|g" -e "s|\${url}|$url|g" \
        -e "s|pre_install \$.*|pre_install|g" -e "s|post_install \$.*|post_install|g" \
        -e "s|pre_upgrade \$.*|pre_upgrade|g" -e "s|post_upgrade \$.*|post_upgrade|g" \
        -e "s|pre_remove \$.*|pre_remove|g" -e "s|post_remove \$.*|post_remove|g" \
        -i  "$pkg/SRCBUILD" || die

    msg "Stripping.."
    sed -e "/pkgname=/d" \
        -e "/pkgrel=/d" \
        -e "/epoch=/d" \
        -e "/arch=/d" \
        -e "/license=/d" \
        -e "/changelog=/d" \
        -e "/url=/d" \
        -e "/groups=/d" \
        -e "/replaces=/d" -e "/conflicts=/d" -e "/provides=/d" \
        -e "/install=/d" \
        -i "$pkg/SRCBUILD" || die

    if [[ -f $script ]];then
        msg "Merging.."
        echo -e "\n" >> "$pkg/SRCBUILD" || die
        cat "$script" >> "$pkg/SRCBUILD" || die
        rm -f "$pkg/${script##*/}" || die
    fi
done
