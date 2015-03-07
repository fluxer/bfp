include ../Makefile.inc

all: clean
	$(POD2MAN) --release="SPM $(VERSION)" \
		--center="Source Package Manager Manual" \
		--section='8' --utf8 spm.pod spm.8
	$(POD2MAN) --release="SPM $(VERSION)" \
		--center="Source Package Manager Manual" \
		--section='5' --utf8 spm.conf.pod spm.conf.5
	$(POD2MAN) --release="SPM $(VERSION)" \
		--center="Source Package Manager Manual" \
		--section='5' --utf8 SRCBUILD.pod SRCBUILD.5
	$(POD2MAN) --release="SPM $(VERSION)" \
		--center="Source Package Manager Manual" \
		--section='8' --utf8 spm-tools.pod > spm-tools.8
	$(SED) 's|#DOCDIR#|$(DOCDIR)|g' -i SRCBUILD.5
	$(SED) 's|#MACHINE#|$(MACHINE)|g' -i spm.conf.5
	$(SED) 's|#ARCH#|$(ARCH)|g' -i spm.conf.5
	$(SED) 's|#JOBS#|$(JOBS)|g' -i spm.conf.5

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(MANDIR)/man8/ \
		$(DESTDIR)$(MANDIR)/man5/ \
		$(DESTDIR)$(DOCDIR)/spm
	$(INSTALL) -vm644 spm.8 $(DESTDIR)$(MANDIR)/man8/spm.8
	$(INSTALL) -vm644 spm-tools.8 $(DESTDIR)$(MANDIR)/man8/spm-tools.8
	$(INSTALL) -vm644 spm.conf.5 $(DESTDIR)$(MANDIR)/man5/spm.conf.5
	$(INSTALL) -vm644 SRCBUILD.5 $(DESTDIR)$(MANDIR)/man5/SRCBUILD.5
	$(INSTALL) -vm644 SRCBUILD.txt $(DESTDIR)$(DOCDIR)/spm/SRCBUILD.txt

uninstall:
	$(RM) $(DESTDIR)$(MANDIR)/man8/spm.8
	$(RM) $(DESTDIR)$(MANDIR)/man8/spm-tools.8
	$(RM) $(DESTDIR)$(MANDIR)/man5/spm.conf.5
	$(RM) $(DESTDIR)$(MANDIR)/man5/SRCBUILD.5
	$(RM) -r $(DESTDIR)$(DOCDIR)/spm/

clean:
	$(RM) *.5 *.8

.PHONY: all install uninstall clean
