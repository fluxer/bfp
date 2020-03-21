include ../Makefile.mk

all: clean
	$(POD2MAN) --release="SPM $(VERSION)" \
		--center="Source Package Manager Manual" \
		--section='8' --utf8 spm.pod spm.8
	$(POD2MAN) --release="SPM $(VERSION)" \
		--center="Source Package Manager Manual" \
		--section='8' --utf8 spm-tools.pod > spm-tools.8
	$(POD2MAN) --release="SPM $(VERSION)" \
		--center="Source Package Manager Manual" \
		--section='5' --utf8 spm.conf.pod spm.conf.5
	$(POD2MAN) --release="SPM $(VERSION)" \
		--center="Source Package Manager Manual" \
		--section='5' --utf8 SRCBUILD.pod SRCBUILD.5
	$(SED) -e 's|@DOCDIR\\fR@|$(DOCDIR)|g' -e 's|@DOCDIR@|$(DOCDIR)|g' -i *.8 *.5
	$(SED) -e 's|@MACHINE\\fR@|$(MACHINE)|g' -e 's|@MACHINE@|$(MACHINE)|g' -i *.8 *.5
	$(SED) -e 's|@ARCH\\fR@|$(ARCH)|g' -e 's|@ARCH@|$(ARCH)|g' -i *.8 *.5
	$(SED) -e 's|@JOBS\\fR@|$(JOBS)|g' -e 's|@JOBS@|$(JOBS)|g' -i *.8 *.5
	for lib in ../src/libs/lib*.py ../src/spm/libspm.py; do \
		PYTHONPATH="$(TOPDIR)/src/libs" $(PYDOC) -w $$lib; \
	done
install:
	$(INSTALL) -vdm755 $(DESTDIR)$(MANDIR)/man8/ \
		$(DESTDIR)$(MANDIR)/man5/ \
		$(DESTDIR)$(DOCDIR)/bfp
	$(INSTALL) -vm644 *.8 $(DESTDIR)$(MANDIR)/man8/
	$(INSTALL) -vm644 *.5 $(DESTDIR)$(MANDIR)/man5/
	$(INSTALL) -vm644 SRCBUILD.txt $(DESTDIR)$(DOCDIR)/bfp/SRCBUILD.txt
	$(INSTALL) -vm644 *.html $(DESTDIR)$(DOCDIR)/bfp/
	$(INSTALL) -vm644 busybox-config $(DESTDIR)$(DOCDIR)/bfp/
	$(INSTALL) -vm644 ../COPYING $(DESTDIR)$(DOCDIR)/bfp/COPYING

uninstall:
	$(RM) $(DESTDIR)$(MANDIR)/man8/spm.8
	$(RM) $(DESTDIR)$(MANDIR)/man8/spm-tools.8
	$(RM) $(DESTDIR)$(MANDIR)/man5/spm.conf.5
	$(RM) $(DESTDIR)$(MANDIR)/man5/SRCBUILD.5
	$(RM) -r $(DESTDIR)$(DOCDIR)/bfp/

clean:
	$(RM) *.1 *.5 *.8 *.html

.PHONY: all install uninstall clean
