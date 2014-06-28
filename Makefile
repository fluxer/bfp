include Makefile.inc

all:
	make -C doc
	make -C src/libs
	make -C src/initfs
	make -C src/spm
	make -C src/spm-qt
	make -C src/qdesktop
	make -C src/qedit
	make -C src/qfile
	make -C src/qimage
	make -C src/qnetwork
	make -C src/qpaste
	make -C src/qproperties
	make -C src/qresources
	make -C src/qsession
	make -C src/qsettings

check:
	make -C src/libs check

install:
	make -C doc install
	make -C etc install
	make -C src/initfs install
	make -C misc install
	make -C scripts install
	make -C src/libs install
	make -C src/spm install
	make -C src/spm-qt install
	make -C src/qdesktop install
	make -C src/qedit install
	make -C src/qfile install
	make -C src/qimage install
	make -C src/qnetwork install
	make -C src/qpaste install
	make -C src/qproperties install
	make -C src/qresources install
	make -C src/qsession install
	make -C src/qsettings install

uninstall:
	make -C doc uninstall
	make -C etc uninstall
	make -C src/initfs uninstall
	make -C misc uninstall
	make -C scripts uninstall
	make -C src/libs uninstall
	make -C src/spm uninstall
	make -C src/spm-qt uninstall
	make -C src/qdesktop uninstall
	make -C src/qedit uninstall
	make -C src/qfile uninstall
	make -C src/qimage uninstall
	make -C src/qnetwork uninstall
	make -C src/qpaste uninstall
	make -C src/qproperties uninstall
	make -C src/qresources uninstall
	make -C src/qsession uninstall
	make -C src/qsettings uninstall

clean:
	make -C doc clean
	make -C src/libs clean
	make -C src/initfs clean
	make -C src/spm clean
	make -C src/spm-qt clean
	make -C src/qdesktop clean
	make -C src/qedit clean
	make -C src/qfile clean
	make -C src/qimage clean
	make -C src/qnetwork clean
	make -C src/qpaste clean
	make -C src/qproperties clean
	make -C src/qresources clean
	make -C src/qsession clean
	make -C src/qsettings clean

dist:
	git archive HEAD --prefix=alive-$(VERSION)/ | xz > alive-$(VERSION).tar.xz

stat:
	cloc $(shell find src/ -name '*.py') scripts/*.sh

lint:
	pylint $(shell find src/ -name '*.py') | grep -v -e 'Line too long'
