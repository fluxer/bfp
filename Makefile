include Makefile.inc

all:
	$(MAKE) -C doc
	$(MAKE) -C src/cparted
	$(MAKE) -C src/libs
	$(MAKE) -C src/initfs
	$(MAKE) -C src/spm
	$(MAKE) -C src/qsession
	$(MAKE) -C src/qworkspace

check:
	$(MAKE) -C src/libs check

install:
	$(MAKE) -C doc install
	$(MAKE) -C etc install
	$(MAKE) -C misc install
	$(MAKE) -C scripts install
	$(MAKE) -C src/cparted install
	$(MAKE) -C src/initfs install
	$(MAKE) -C src/icons install
	$(MAKE) -C src/libs install
	$(MAKE) -C src/spm install
	$(MAKE) -C src/qsession install
	$(MAKE) -C src/qworkspace install

uninstall:
	$(MAKE) -C doc uninstall
	$(MAKE) -C etc uninstall
	$(MAKE) -C misc uninstall
	$(MAKE) -C scripts uninstall
	$(MAKE) -C src/cparted  uninstall
	$(MAKE) -C src/initfs uninstall
	$(MAKE) -C src/icons uninstall
	$(MAKE) -C src/libs uninstall
	$(MAKE) -C src/spm uninstall
	$(MAKE) -C src/qsession uninstall
	$(MAKE) -C src/qworkspace uninstall

clean:
	$(MAKE) -C doc clean
	$(MAKE) -C src/cparted clean
	$(MAKE) -C src/libs clean
	$(MAKE) -C src/initfs clean
	$(MAKE) -C src/spm clean
	$(MAKE) -C src/qsession clean
	$(MAKE) -C src/qworkspace clean

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
