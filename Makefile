include Makefile.inc

all:
	make -C doc
	make -C src/libs
	make -C src/initfs
	make -C src/mounttray
	make -C src/powertray
	make -C src/shell
	make -C src/spm
	make -C src/spm-qt
	make -C src/qfile
	make -C src/qdesktop
	make -C src/qresources

check:
	make -C src/libs check
	make -C src/spm check
	make -C src/spm-qt check

install:
	make -C doc install
	make -C etc install
	make -C src/initfs install
	make -C misc install
	make -C scripts install
	make -C src/libs install
	make -C src/mounttray install
	make -C src/powertray install
	make -C src/shell install
	make -C src/spm install
	make -C src/spm-qt install
	make -C src/qfile install
	make -C src/qdesktop install
	make -C src/qresources install

uninstall:
	make -C doc uninstall
	make -C etc uninstall
	make -C src/initfs uninstall
	make -C misc uninstall
	make -C scripts uninstall
	make -C src/libs uninstall
	make -C src/mounttray uninstall
	make -C src/powertray uninstall
	make -C src/shell uninstall
	make -C src/spm uninstall
	make -C src/spm-qt uninstall
	make -C src/qfile uninstall
	make -C src/qdesktop uninstall
	make -C src/qresources uninstall

clean:
	make -C doc clean
	make -C src/init clean
	make -C src/libs clean
	make -C src/initfs clean
	make -C src/mounttray clean
	make -C src/powertray clean
	make -C src/shell clean
	make -C src/spm clean
	make -C src/spm-qt clean
	make -C src/qfile clean
	make -C src/qdesktop clean
	make -C src/qresources clean

dist:
	git archive HEAD --prefix=alive-$(VERSION)/ | xz > alive-$(VERSION).tar.xz

stat:
	cloc $(shell find src/ -name '*.py') scripts/*.sh

lint:
	pylint $(shell find src/ -name '*.py') | grep -v -e 'Line too long'
