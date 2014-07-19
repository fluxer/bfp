include ../Makefile.inc

install:
	$(INSTALL) -vdm755 $(DESTDIR)/etc/spm
	$(INSTALL) -vdm755 $(DESTDIR)/etc/qworkspace
	$(INSTALL) -vm644 spm.conf $(DESTDIR)/etc/
	$(INSTALL) -vm644 repositories.conf $(DESTDIR)/etc/spm/
	$(INSTALL) -vm644 mirrors.conf $(DESTDIR)/etc/spm/
	$(SED) 's|#MACHINE#|$(MACHINE)|g' -i $(DESTDIR)/etc/spm.conf
	$(SED) 's|#ARCH#|$(ARCH)|g' -i $(DESTDIR)/etc/spm.conf
	$(SED) 's|#JOBS#|$(JOBS)|g' -i $(DESTDIR)/etc/spm.conf
	$(CP) -vr styles $(DESTDIR)/etc/qworkspace/

uninstall:
	$(RM) -r $(DESTDIR)/etc/spm/ $(DESTDIR)/etc/spm.conf
	$(RM) -r $(DESTDIR)/etc/qworkspace/
