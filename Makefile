include Makefile.inc

all:
	make -C doc
	make -C src/cparted
	make -C src/libs
	make -C src/initfs
	make -C src/spm
	make -C src/qsession
	make -C src/qworkspace

check:
	make -C src/libs check

install:
	make -C doc install
	make -C etc install
	make -C misc install
	make -C scripts install
	make -C src/cparted install
	make -C src/initfs install
	make -C src/icons install
	make -C src/libs install
	make -C src/spm install
	make -C src/qsession install
	make -C src/qworkspace install

uninstall:
	make -C doc uninstall
	make -C etc uninstall
	make -C misc uninstall
	make -C scripts uninstall
	make -C src/cparted  uninstall
	make -C src/initfs uninstall
	make -C src/icons uninstall
	make -C src/libs uninstall
	make -C src/spm uninstall
	make -C src/qsession uninstall
	make -C src/qworkspace uninstall

clean:
	make -C doc clean
	make -C src/cparted clean
	make -C src/libs clean
	make -C src/initfs clean
	make -C src/spm clean
	make -C src/qsession clean
	make -C src/qworkspace clean

changelog:
	$(GIT) log HEAD -n 1 --pretty='%cd %an <%ae> %n%H%d'
	$(GIT) log $(shell $(GIT) tag | tail -n1)..HEAD --no-merges --pretty='    * %s'

dist:
	$(GIT) archive HEAD --prefix=bfp-$(VERSION)/ | $(XZ) > bfp-$(VERSION).tar.xz

stat:
	cloc $(shell $(FIND) src/ -name '*.py') scripts/*.sh

lint:
	$(PYLINT) $(shell $(FIND) src/ -name '*.py') | $(GREP) -v -e 'Line too long'

.PHONY: all check install uninstall clean changelog dist stat lint
