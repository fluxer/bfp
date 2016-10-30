#!/bin/bash

# srcmake - alternative, but with limited functionality, ports builder
# Copyright (C) 2012-2017 Ivailo Monev (a.k.a SmiL3y)


export LANG=C LC_ALL=C
unset ALL_OFF BOLD BLUE GREEN RED YELLOW
if [[ -t 2 ]]; then
    # prefer colored and bold text when tput is supported
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
    printf "${ALL_OFF}${GREEN}*${ALL_OFF}${BOLD} ${*}${ALL_OFF}\n"
}

msg2() {
    printf "${ALL_OFF}${BLUE}   ->${ALL_OFF}${BOLD} ${*}${ALL_OFF}\n"
}

warn() {
    printf "${ALL_OFF}${YELLOW}*${ALL_OFF}${BOLD} ${*}${ALL_OFF}\n" >&2
}

warn2() {
    printf "${ALL_OFF}${YELLOW}   ->${ALL_OFF}${BOLD} ${*}${ALL_OFF}\n" >&2
}

error() {
    printf "${ALL_OFF}${RED}=>${ALL_OFF}${BOLD} ${*}${ALL_OFF}\n" >&2
    return 1
}

error2() {
    printf "${ALL_OFF}${RED}   =>${ALL_OFF}${BOLD} ${*}${ALL_OFF}\n" >&2
    return 1
}

die() {
    printf "${ALL_OFF}${RED}=>${ALL_OFF}${BOLD} Hewston, we have a problem${ALL_OFF}\n" >&2
    exit 1
}

whereis() {
    # check if the binary is not missing runtime dependencies, those usually
    # return exit code of 127 when called
    rv=1
    if which "$1" 1> /dev/null;then
        rv=0
        # if it hangs here then the program takes input via stdin and this
        # function does not handle such behaviour
        $@ &> /dev/null
        [ "$?" = "127" ] && rv=1
    fi
    return $rv
}

startdir="$(dirname $0)"
for src in "${@:-.}";do
    srcbuild="$(realpath $src)/SRCBUILD"

    if ! whereis curl && ! whereis wget ;then
        error "Neither curl or wget is installed"
        exit 1
    elif ! whereis bsdtar && ! whereis tar ;then
        error "Neither bsdtar or tar is installed"
        exit 1
    elif ! whereis git ;then
        # FIXME: error out if there is git URL in sources array
        warn "Git is not installed"
    elif ! whereis grep || ! whereis find || ! whereis cut || ! whereis du ;then
        error "grep, find, cut and/or du are not installed"
        exit 1
    fi

    msg "Checking.."
    if [ ! -f "$srcbuild" ];then
        warn "Give me a directory with SRCBUILD"
        continue
    elif ! grep -q -e '^version=' "$srcbuild";then
        warn "version not defined in $srcbuild"
        continue
    elif ! grep -q -e '^description=' "$srcbuild";then
        warn "description not defined in $srcbuild"
        continue
    elif ! grep -q -e '^src_install()' "$srcbuild";then
        warn "src_install() not defined in $srcbuild"
        continue
    fi

    set -e
    msg "Preparing sources.."
    . "$srcbuild"
    src_real="$(realpath $src)"
    src_name="${src_real##*/}"
    SOURCE_DIR="$src_real/source"
    INSTALL_DIR="$src_real/install"

    missing_depends=""
    for depend in "${depends[@]}" "${makedepends[@]}";do
        if [ ! -d "/var/local/spm/$depend" ];then
            missing_depends="$missing_depends $depend "
        fi
    done
    if [ -n "$missing_depends" ];then
        warn2 "Missing dependencies: ${YELLOW}${missing_depends}${ALL_OFF}"
    fi

    enabled_optdepends=""
    missing_optdepends=""
    for depend in "${optdepends[@]}";do
        fixed_name="$(echo ${depend} | tr '\-\!@#$%^.,[]+><"=()' '_')"
        if [ -d "/var/local/spm/$depend" ];then
            export OPTIONAL_${fixed_name}_BOOL="TRUE"
            export OPTIONAL_${fixed_name}_SWITCH="ON"
            export OPTIONAL_${fixed_name}="yes"
            enabled_optdepends="$enabled_optdepends $depend"
        else
            missing_optdepends="$missing_optdepends $depend"
            export OPTIONAL_${fixed_name}_BOOL="FALSE"
            export OPTIONAL_${fixed_name}_SWITCH="OFF"
            export OPTIONAL_${fixed_name}="no"
        fi
    done
    if [ -n "$missing_optdepends" ];then
        warn2 "Disabling optional: ${YELLOW}${missing_optdepends}${ALL_OFF}"
    fi

    rm -rf "$SOURCE_DIR" "$INSTALL_DIR"
    mkdir -p "$SOURCE_DIR" "$INSTALL_DIR"
    for source in "${sources[@]}";do
        src_base="${source##*/}"

        if [ -f "$src_real/$src_base" ];then
            msg2 "Linking: ${BLUE}${src_base}${ALL_OFF}"
            ln -sf "$src_real/$src_base" "$SOURCE_DIR/$src_base"
        elif [[ $source =~ git:// || $source =~ \.git ]];then
            msg2 "Cloning: ${BLUE}${source}${ALL_OFF}"
            git clone --depth=1 "$source" "$SOURCE_DIR/$src_base"
        elif [ -f "/var/cache/spm/sources/$src_name/$src_base" ];then
            msg2 "Linking: ${BLUE}${src_base}${ALL_OFF}"
            ln -sf "/var/cache/spm/sources/$src_name/$src_base" "$SOURCE_DIR/$src_base"
        else
            msg2 "Fetching: ${BLUE}${source}${ALL_OFF}"
            if whereis curl ;then
                curl -f -L -C - "$source" -o "$src_real/$src_base"
            elif whereis wget ;then
                wget -c "$source" -O "$src_real/$src_base"
            fi
            ln -sf "$src_real/$src_base" "$SOURCE_DIR/$src_base"
        fi

        case "$src_base" in
            *.tar|*.tar.gz|*.tar.Z|*.tgz|*.tar.bz2|*.tbz2|*.tar.xz|*.txz|*.tar.lzma|*.zip|*.rpm)
                msg2 "Extracting: ${BLUE}${src_base}${ALL_OFF}"
                if whereis bsdtar ;then
                    bsdtar -xpf "$SOURCE_DIR/$src_base" -C "$SOURCE_DIR"
                elif whereis tar ;then
                    tar -xpf "$SOURCE_DIR/$src_base" -C "$SOURCE_DIR"
                fi ;;
            *.gz)
                msg2 "Extracting: ${BLUE}${src_base}${ALL_OFF}"
                gunzip "$SOURCE_DIR/$src_base" -c > "$SOURCE_DIR/${src_base//.gz/}" ;;
            *.bz2)
                msg2 "Extracting: ${BLUE}${src_base}${ALL_OFF}"
                bunzip "$SOURCE_DIR/$src_base" -c > "$SOURCE_DIR/${src_base//.bz2/}" ;;
        esac
    done

    cd "$SOURCE_DIR"
    if grep -q -e '^src_prepare()' "$srcbuild";then
        msg "Preparing sources.."
        src_prepare
    fi

    cd "$SOURCE_DIR"
    if grep -q -e '^src_compile()' "$srcbuild";then
        msg "Compiling sources.."
        src_compile
    fi

    msg "Installing sources.."
    cd "$SOURCE_DIR"
    src_install

    msg "Creating metadata and SRCBUILD..."
    localsrcbuild="$INSTALL_DIR/var/local/spm/$src_name/SRCBUILD"
    localmetadata="$INSTALL_DIR/var/local/spm/$src_name/metadata.json"
    mkdir -p "$INSTALL_DIR/var/local/spm/$src_name"

    size="$(du -sb "$INSTALL_DIR" | cut -f1)"
    builddate="$(date)"
    depends_json=""
    for depend in "${depends[@]}";do
        depends_json="$depends_json \"$depend\", "
    done
    optdepends_json=""
    for depend in $enabled_optdepends;do
        optdepends_json="$optdepends_json \"$depend\", "
    done
    # TODO: autodepends_json
    backup_json=""
    for backup in "${backup[@]}";do
        backup_file="$INSTALL_DIR/$backup"
        if [ -e "$backup_file" ];then
            backup_checksum="$(sha256sum "$backup_file" | cut -f1 -d' ')"
            backup_json="$backup_json \"/$backup\": \"$backup_checksum\", "
        fi
    done
    footprint_json=""
    while IFS= read -r -d '' file;do
        footprint_json="$footprint_json \"${file//$INSTALL_DIR}\", "
    done < <(find "$INSTALL_DIR" ! -type d -print0)

    echo "
{
    \"version\": \"$version\",
    \"release\": \"${release:-1}\",
    \"description\": \"$description\",
    \"depends\": [ $depends_json ],
    \"optdepends\": [ $optdepends_json ],
    \"autodepends\": [ $autodepends_json ],
    \"backup\": { $backup_json },
    \"size\": $size,
    \"footprint\": [ $footprint_json ],
    \"builddate\": \"$builddate\"
}" > "$localmetadata"
    cp -f "$srcbuild" "$localsrcbuild"

    msg "Compressing tarball.."
    tarball="${src_name}_${version}.tar.bz2"
    cd "$INSTALL_DIR"
    if whereis bsdtar ;then
        bsdtar -cpaf "$src_real/$tarball" ./*
    elif whereis tar ;then
        tar -cpaf "$src_real/$tarball" ./*
    fi

    cd "$startdir"
    # do not remove the directories when the tarball can not be extracted
    if whereis bsdtar || whereis tar ;then
        msg "Cleaning up.."
        rm -rf "$SOURCE_DIR" "$INSTALL_DIR"
    fi

    if [ "$(id -u)" != "0" ] && ! whereis sudo ;then
        sus="${RED}sudo "
        sue=""
    elif [ "$(id -u)" != "0" ];then
        sus="${RED}su -c '"
        sue="${RED}'"
    fi
    if whereis bsdtar ;then
        msg "To merge it: ${sus}${GREEN}bsdtar -vxpf ${src}/${tarball} -C /${sue}${ALL_OFF}"
    elif whereis tar ;then
        msg "To merge it: ${sus}${GREEN}tar -vxphf ${src}/${tarball} -C /${sue}${ALL_OFF}"
    fi
    set +e
done
