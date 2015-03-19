include ../Makefile.inc

install:
	$(INSTALL) -dm755 $(DESTDIR)/etc/spm
	$(INSTALL) -m644 spm.conf $(DESTDIR)/etc/
	$(INSTALL) -m644 repositories.conf $(DESTDIR)/etc/spm/
	$(INSTALL) -m644 mirrors.conf $(DESTDIR)/etc/spm/
	$(INSTALL) -m644 keyservers.conf $(DESTDIR)/etc/spm/
	$(SED) 's|#MACHINE#|$(MACHINE)|g' -i $(DESTDIR)/etc/spm.conf
	$(SED) 's|#ARCH#|$(ARCH)|g' -i $(DESTDIR)/etc/spm.conf
	$(SED) 's|#JOBS#|$(JOBS)|g' -i $(DESTDIR)/etc/spm.conf

uninstall:
	$(RM) -r $(DESTDIR)/etc/spm/ $(DESTDIR)/etc/spm.conf

.PHONY: install uninstall
