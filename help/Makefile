include ../Makefile.inc

all:
	$(POOLE) --build
	$(SED) 's|#SHAREDIR#|$(SHAREDIR)|g' -i output/srcbuild.html
	$(SED) -e 's|#MACHINE#|$(MACHINE)|g' -e 's|#ARCH#|$(ARCH)|g' \
		-e 's|#JOBS#|$(JOBS)|g' -i output/spm.conf.html

install:
	$(INSTALL) -dm755 $(DESTDIR)$(SHAREDIR)/help/
	$(INSTALL) -m644 output/*.html $(DESTDIR)$(SHAREDIR)/help/

check:
	$(POOLE) --serve

uninstall:
	$(RM) -r $(DESTDIR)$(SHAREDIR)/help/

clean:
	$(RM) output/*.html

.PHONY: all install check uninstall clean