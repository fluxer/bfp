include ../Makefile.inc

all:
	$(MARKDOWN) about.md -f about.html
	$(MARKDOWN) contributors.md -f contributors.html
	$(MARKDOWN) copying.cparted.md -f copying.cparted.html
	$(MARKDOWN) copying.icons.md -f copying.icons.html
	$(MARKDOWN) copying.md -f copying.html
	$(MARKDOWN) initscripts.md -f initscripts.html
	$(MARKDOWN) inittab.md -f inittab.html
	$(MARKDOWN) license.magic.md -f license.magic.html
	$(MARKDOWN) lsinitfs.md -f lsinitfs.html
	$(MARKDOWN) mkinitfs.md -f mkinitfs.html
	$(MARKDOWN) porting_software.md -f porting_software.html
	$(MARKDOWN) rc.d.md -f rc.d.html
	$(MARKDOWN) rc.conf.md -f rc.conf.html
	$(MARKDOWN) spm-tools.md -f spm-tools.html
	$(MARKDOWN) spm.conf.md -f spm.conf.html
	$(MARKDOWN) spm.md -f spm.html
	$(MARKDOWN) srcbuild.md -f srcbuild.html
	$(MARKDOWN) system_maintenance.md -f system_maintenance.html
	$(MARKDOWN) tmpfiles.md -f tmpfiles.html
	$(MARKDOWN) tmpfiles.d.md -f tmpfiles.d.html
	$(MARKDOWN) todo.md -f todo.html
	$(MARKDOWN) useful_links.md -f useful_links.html
	$(MARKDOWN) users_and_groups.md -f users_and_groups.html
	$(SED) 's|#SHAREDIR#|$(SHAREDIR)|g' -i srcbuild.html
	$(SED) -e 's|#MACHINE#|$(MACHINE)|g' -e 's|#ARCH#|$(ARCH)|g' \
		-e 's|#JOBS#|$(JOBS)|g' -i spm.conf.html
	$(PYDOC) -w libmagic
	$(PYDOC) -w libmisc
	$(PYDOC) -w libpackage
	$(PYDOC) -w libmessage

install:
	$(INSTALL) -dm755 $(DESTDIR)$(SHAREDIR)/help/
	$(INSTALL) -m644 *.html $(DESTDIR)$(SHAREDIR)/help/

uninstall:
	$(RM) -r $(DESTDIR)$(SHAREDIR)/help/

clean:
	$(RM) *.html

.PHONY: all install uninstall clean
