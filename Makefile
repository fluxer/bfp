include Makefile.inc

all:
	$(MAKE) -C doc
	$(MAKE) -C src/ahws
	$(MAKE) -C src/cparted
	$(MAKE) -C src/libs
	$(MAKE) -C src/initfs
	$(MAKE) -C src/spm
	$(MAKE) -C src/spmd

cython:
	$(MAKE) -C doc
	$(MAKE) -C src/ahws cython
	$(MAKE) -C src/cparted cython
	$(MAKE) -C src/libs cython
	$(MAKE) -C src/initfs cython
	$(MAKE) -C src/spm cython
	$(MAKE) -C src/spmd cython

check:
	$(MAKE) -C src/libs check

install:
	$(MAKE) -C doc install
	$(MAKE) -C etc install
	$(MAKE) -C misc install
	$(MAKE) -C scripts install
	$(MAKE) -C src/ahws install
	$(MAKE) -C src/cparted install
	$(MAKE) -C src/initfs install
	$(MAKE) -C src/libs install
	$(MAKE) -C src/spm install
	$(MAKE) -C src/spmd install

uninstall:
	$(MAKE) -C doc uninstall
	$(MAKE) -C etc uninstall
	$(MAKE) -C misc uninstall
	$(MAKE) -C scripts uninstall
	$(MAKE) -C src/ahws uninstall
	$(MAKE) -C src/cparted uninstall
	$(MAKE) -C src/initfs uninstall
	$(MAKE) -C src/libs uninstall
	$(MAKE) -C src/spm uninstall
	$(MAKE) -C src/spmd uninstall

clean:
	$(MAKE) -C doc clean
	$(MAKE) -C src/ahws clean
	$(MAKE) -C src/cparted clean
	$(MAKE) -C src/libs clean
	$(MAKE) -C src/initfs clean
	$(MAKE) -C src/spm clean
	$(MAKE) -C src/spmd clean
	$(RM) $(shell $(FIND) nuitka -name '*.pyc' -o -name '*.pyo')

changelog:
	$(GIT) log HEAD -n 1 --pretty='%cd %an <%ae> %n%H%d'
	$(GIT) log $(shell $(GIT) tag | tail -n1)..HEAD --no-merges --pretty='    * %s'

dist:
	$(GIT) archive HEAD --prefix=bfp-$(VERSION)/ | $(XZ) > bfp-$(VERSION).tar.xz
	$(GPG) --sign --detach-sign bfp-$(VERSION).tar.xz

.PHONY: all cython check install uninstall clean changelog dist
