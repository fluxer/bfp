include Makefile.inc

all:
	$(MAKE) -C help
	$(MAKE) -C src/cparted
	$(MAKE) -C src/blockd
	$(MAKE) -C src/libs
	$(MAKE) -C src/initfs
	$(MAKE) -C src/spm
	$(MAKE) -C src/qsession
	$(MAKE) -C src/qworkspace

check:
	$(MAKE) -C src/libs check
	$(MAKE) -C src/qworkspace check

install:
	$(MAKE) -C etc install
	$(MAKE) -C icons install
	$(MAKE) -C help install
	$(MAKE) -C misc install
	$(MAKE) -C scripts install
	$(MAKE) -C src/blockd install
	$(MAKE) -C src/cparted install
	$(MAKE) -C src/initfs install
	$(MAKE) -C src/libs install
	$(MAKE) -C src/spm install
	$(MAKE) -C src/qsession install
	$(MAKE) -C src/qworkspace install

uninstall:
	$(MAKE) -C etc uninstall
	$(MAKE) -C icons uninstall
	$(MAKE) -C help uninstall
	$(MAKE) -C misc uninstall
	$(MAKE) -C scripts uninstall
	$(MAKE) -C src/blockd uninstall
	$(MAKE) -C src/cparted uninstall
	$(MAKE) -C src/initfs uninstall
	$(MAKE) -C src/libs uninstall
	$(MAKE) -C src/spm uninstall
	$(MAKE) -C src/qsession uninstall
	$(MAKE) -C src/qworkspace uninstall

clean:
	$(MAKE) -C help clean
	$(MAKE) -C src/blockd clean
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

.PHONY: all check install uninstall clean changelog dist
