#!/bin/bash

set -e

for i in /var/local/spm/*;do
    if [ ! -f "$i/SRCBUILD" ];then
        echo " > Adding local SRCBUILD for $i"
        remote=$(spm-tools which -p "/$(basename ${i})$")
        if [ -n "$remote" ];then
            cp -v "$remote/SRCBUILD" "$i/SRCBUILD"
        else
            echo " >> No remote alternative of $i"
        fi
    fi
    if [ -f "$i/metadata" ];then
        if ! grep -q 'release=' "$i/metadata" ;then
            echo " > Adding release for $i"
            echo 'release=1' >> "$i/metadata"
        fi
    else
        echo " >> No metadata file for $i"
    fi
done
