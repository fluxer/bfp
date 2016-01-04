include Makefile.mk

all:
	$(MAKE) -C doc
	$(MAKE) -C src/ahws
	$(MAKE) -C src/libs
	$(MAKE) -C src/initfs
	$(MAKE) -C src/spm

sources:
	$(MAKE) -C src/ahws sources
	$(MAKE) -C src/libs sources
	$(MAKE) -C src/initfs sources
	$(MAKE) -C src/spm sources

check:
	$(MAKE) -C src/libs check
	$(MAKE) -C src/spm check

install:
	$(MAKE) -C doc install
	$(MAKE) -C misc install
	$(MAKE) -C scripts install
	$(MAKE) -C src/ahws install
	$(MAKE) -C src/initfs install
	$(MAKE) -C src/libs install
	$(MAKE) -C src/spm install

uninstall:
	$(MAKE) -C doc uninstall
	$(MAKE) -C misc uninstall
	$(MAKE) -C scripts uninstall
	$(MAKE) -C src/ahws uninstall
	$(MAKE) -C src/initfs uninstall
	$(MAKE) -C src/libs uninstall
	$(MAKE) -C src/spm uninstall

clean:
	$(MAKE) -C doc clean
	$(MAKE) -C src/ahws clean
	$(MAKE) -C src/libs clean
	$(MAKE) -C src/initfs clean
	$(MAKE) -C src/spm clean
	$(RM) $(shell $(FIND) nuitka -name '*.pyc' -o -name '*.pyo')

changelog:
	$(GIT) log HEAD -n 1 --pretty='%cd %an <%ae> %n%H%d'
	$(GIT) log $(shell $(GIT) tag | tail -n1)..HEAD --no-merges --pretty='    * %s' | $(UNIQ) -u

dist:
	$(GIT) archive HEAD --format=tar --prefix=bfp-$(VERSION)/ | $(XZ) > bfp-$(VERSION).tar.xz
	$(GPG) --sign --detach-sign bfp-$(VERSION).tar.xz

.PHONY: all check install uninstall clean changelog dist
