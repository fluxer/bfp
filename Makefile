include Makefile.mk

all:
	$(MAKE) -C doc
	$(MAKE) -C src/ahws
	$(MAKE) -C src/cold
	$(MAKE) -C src/libs
	$(MAKE) -C src/initfs
	$(MAKE) -C src/spm
	# $(MAKE) -C src/spmd

check:
	$(MAKE) -C src/libs check
	$(MAKE) -C src/spm check

install:
	$(MAKE) -C doc install
	$(MAKE) -C misc install
	$(MAKE) -C scripts install
	$(MAKE) -C src/ahws install
	$(MAKE) -C src/cold install
	$(MAKE) -C src/initfs install
	$(MAKE) -C src/libs install
	$(MAKE) -C src/spm install
	# $(MAKE) -C src/spmd install

uninstall:
	$(MAKE) -C doc uninstall
	$(MAKE) -C misc uninstall
	$(MAKE) -C scripts uninstall
	$(MAKE) -C src/ahws uninstall
	$(MAKE) -C src/cold uninstall
	$(MAKE) -C src/initfs uninstall
	$(MAKE) -C src/libs uninstall
	$(MAKE) -C src/spm uninstall
	# $(MAKE) -C src/spmd uninstall

clean:
	$(MAKE) -C doc clean
	$(MAKE) -C src/ahws clean
	$(MAKE) -C src/cold clean
	$(MAKE) -C src/libs clean
	$(MAKE) -C src/initfs clean
	$(MAKE) -C src/spm clean
	# $(MAKE) -C src/spmd clean
	$(RM) $(shell $(FIND) nuitka -name '*.pyc' -o -name '*.pyo')

changelog:
	$(GIT) log HEAD -n 1 --pretty='%cd %an <%ae> %n%H%d'
	$(GIT) log $(shell $(GIT) tag | tail -n1)..HEAD --no-merges --pretty='    * %s' | uniq -u

dist:
	$(GIT) archive HEAD --prefix=bfp-$(VERSION)/ | $(XZ) > bfp-$(VERSION).tar.xz
	$(GPG) --sign --detach-sign bfp-$(VERSION).tar.xz

.PHONY: all check install uninstall clean changelog dist
