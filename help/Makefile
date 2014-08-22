include ../Makefile.inc

all:
	$(MARKDOWN) about.md -f about.html
	$(MARKDOWN) copying.cparted.md -f copying.cparted.html
	$(MARKDOWN) copying.icons.md -f copying.icons.html
	$(MARKDOWN) copying.md -f copying.html
	$(MARKDOWN) license.magic.md -f license.magic.html
	$(MARKDOWN) todo.md -f todo.html
	$(PYDOC) -w libmagic
	$(PYDOC) -w libmisc
	$(PYDOC) -w libpackage
	$(PYDOC) -w libmessage
	$(PYDOC) -w libworkspace
	$(MARKDOWN) cparted.md -f cparted.html
	$(MARKDOWN) lsinitfs.md -f lsinitfs.html
	$(MARKDOWN) mkinitfs.md -f mkinitfs.html
	$(MARKDOWN) srcbuild.md -f srcbuild.html
	$(MARKDOWN) spm.conf.md -f spm.conf.html
	$(MARKDOWN) spm.md -f spm.html
	$(MARKDOWN) spm-tools.md -f spm-tools.html
	$(SED) 's|#SHAREDIR#|$(SHAREDIR)|g' -i srcbuild.html
	$(SED) -e 's|#MACHINE#|$(MACHINE)|g' -e 's|#ARCH#|$(ARCH)|g' \
		-e 's|#JOBS#|$(JOBS)|g' -i spm.conf.html

install:
	$(INSTALL) -dm755 $(DESTDIR)$(SHAREDIR)/help/
	$(INSTALL) -m644 about.html $(DESTDIR)$(SHAREDIR)/help/
	$(INSTALL) -m644 copying.cparted.html $(DESTDIR)$(SHAREDIR)/help/
	$(INSTALL) -m644 copying.icons.html $(DESTDIR)$(SHAREDIR)/help/
	$(INSTALL) -m644 copying.html $(DESTDIR)$(SHAREDIR)/help/
	$(INSTALL) -m644 license.magic.html $(DESTDIR)$(SHAREDIR)/help/
	$(INSTALL) -m644 todo.html $(DESTDIR)$(SHAREDIR)/help/
	$(INSTALL) -m644 libmagic.html $(DESTDIR)$(SHAREDIR)/help/
	$(INSTALL) -m644 libmisc.html $(DESTDIR)$(SHAREDIR)/help/
	$(INSTALL) -m644 libpackage.html $(DESTDIR)$(SHAREDIR)/help/
	$(INSTALL) -m644 libmessage.html $(DESTDIR)$(SHAREDIR)/help/
	$(INSTALL) -m644 libworkspace.html $(DESTDIR)$(SHAREDIR)/help/

uninstall:
	$(RM) -r $(DESTDIR)$(SHAREDIR)/help/

clean:
	$(RM) *.html

.PHONY: all install uninstall clean
