#!/bin/bash

# srcmake - alternative ports builder
# Copyright (C) 2013-2014 Ivailo Monev (a.k.a SmiL3y)
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

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

msg2() {
	printf "${ALL_OFF}${BLUE}   =>${ALL_OFF}${BOLD} ${@}${ALL_OFF}\n"
}

warn() {
	printf "${ALL_OFF}${YELLOW}=>${ALL_OFF}${BOLD} ${@}${ALL_OFF}\n" >&2
}

warn2() {
	printf "${ALL_OFF}${YELLOW}   =>${ALL_OFF}${BOLD} ${@}${ALL_OFF}\n" >&2
}

error() {
	printf "${ALL_OFF}${RED}=>${ALL_OFF}${BOLD} ${@}${ALL_OFF}\n" >&2
	return 1
}

error2() {
	printf "${ALL_OFF}${RED}   =>${ALL_OFF}${BOLD} ${@}${ALL_OFF}\n" >&2
	return 1
}

die() {
	printf "${ALL_OFF}${RED}=>${ALL_OFF}${BOLD} Hewston, we have a problem${ALL_OFF}\n" >&2
	exit 1
}

for src in "${@:-.}";do
	srcbuild="$src/SRCBUILD"

	if [[ -z $(which curl) && -z $(which wget) ]];then
		error "Neither curl or wget is installed"
		exit 1
	elif [[ -z $(which bsdtar) && -z $(which tar) ]];then
		error "Neither bsdtar or tar is installed"
		exit 1
	fi

	if [[ ! -f $srcbuild ]];then
		warn "Give me a directory with SRCBUILD"
		continue
	fi

	msg "Checking $srcbuild.."
	if [[ -z $(grep -e '^version=' "$srcbuild") ]];then
		warn "version not defined in $srcbuild"
		continue
	elif [[ -z $(grep -e '^description=' "$srcbuild") ]];then
		warn "description not defined in $srcbuild"
		continue
	elif [[ -z $(grep -e '^src_install()' "$srcbuild") ]];then
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

	rm -rf --one-file-system "$SOURCE_DIR"
	mkdir -p "$SOURCE_DIR"
	for source in "${sources[@]}";do
		src_base="${source##*/}"

		if [ -f "$src_real/$src_base" ];then
			msg2 "Linking: ${BLUE}${src_base}${ALL_OFF}"
			ln -sf "$src_real/$src_base" "$SOURCE_DIR/$src_base"
		elif [[ $source =~ git:// || $source =~ .git ]];then
			msg2 "Cloning: ${BLUE}${source}${ALL_OFF}"
			git clone --depth=1 "$source" "$SOURCE_DIR/$src_base"
		elif [ -f "/var/cache/spm/sources/$src_name/$src_base" ];then
			msg2 "Linking: ${BLUE}${src_base}${ALL_OFF}"
			ln -sf "/var/cache/spm/sources/$src_name/$src_base" "$SOURCE_DIR/$src_base"
		elif [ ! -f "$SOURCE_DIR/$src_base" ];then
			msg2 "Fetching: ${BLUE}${source}${ALL_OFF}"
			if [ -n "$(which curl)" ];then
				curl -f -L -C - "$source" -o "$SOURCE_DIR/$src_base"
			elif [ -n "$(which wget)" ];then
				wget -c "$source" -O "$SOURCE_DIR/$src_base"
			fi
		fi

		case "$src_base" in
			*.tar|*.tar.gz|*.tar.Z|*.tgz|*.tar.bz2|*.tbz2|*.tar.xz|*.txz|*.tar.lzma|*.zip|*.rpm)
				msg2 "Extracting: ${BLUE}${src_base}${ALL_OFF}"
				if [ -n "$(which bsdtar)" ];then
					bsdtar -xpf "$SOURCE_DIR/$src_base" -C "$SOURCE_DIR"
				elif [ -n "$(which tar)" ];then
					tar -xpf "$SOURCE_DIR/$src_base" -C "$SOURCE_DIR"
				fi ;;
		esac		
	done
	
	cd "$SOURCE_DIR"
	if [[ -n $(grep -e '^src_compile()' "$srcbuild") ]];then
		msg "Compiling sources.."
		src_compile
	fi
	
	
	
	msg "Installing sources.."
	rm -rf --one-file-system "$INSTALL_DIR"
	mkdir -p "$INSTALL_DIR"
	cd "$INSTALL_DIR"
	src_install
	
	msg "Creating footprint and metadata.."
	mkdir -p "$INSTALL_DIR/var/local/spm/$src_name"
	find "$INSTALL_DIR" ! -type d -printf '%P\n' > "$INSTALL_DIR/var/local/spm/$src_name/footprint"
	echo "version=$version" > "$INSTALL_DIR/var/local/spm/$src_name/metadata"
	echo "description=$description" >> "$INSTALL_DIR/var/local/spm/$src_name/metadata"
	echo "depends=${depends[@]}" >> "$INSTALL_DIR/var/local/spm/$src_name/metadata"
	echo "size=$(du -s $INSTALL_DIR | awk '{print $1}')" >> "$INSTALL_DIR/var/local/spm/$src_name/metadata"

	msg "Compressing tarball.."
	tarball="${src_name}_${version}.tar.bz2"
	cd "$INSTALL_DIR"
	tar -caf "$src_real/$tarball" *

	msg "Cleaning up.."
	rm -rf --one-file-system "$SOURCE_DIR" "$INSTALL_DIR"

	msg "To merge it: ${GREEN}tar -vxapPhf ${src}/${tarball} -C /${ALL_OFF}"
	set +e
done
