include ../Makefile.inc

all:
	pod2man --release="PowerD $(VERSION)" --center="Power Daemon Manual" \
		--section='8' --utf8 powerd.pod > powerd.8
	pod2man --release="PowerD $(VERSION)" --center="Power Daemon Manual" \
		--section='8' --utf8 powerctl.pod > powerctl.8
	pod2man --release="PowerD $(VERSION)" --center="Power Daemon Manual" \
		--section='5' --utf8 powerd.conf.pod > powerd.conf.5
	pod2man --release="SPM $(VERSION)" --center="Source Package Manager Manual" \
		--section='8' --utf8 spm.pod spm.8
	pod2man --release="SPM $(VERSION)" --center="Source Package Manager Manual" \
		--section='5' --utf8 spm.conf.pod spm.conf.5
	pod2man --release="SPM $(VERSION)" --center="Source Package Manager Manual" \
		--section='5' --utf8 SRCBUILD.pod SRCBUILD.5
	pod2man --release="SPM $(VERSION)" --center="Source Package Manager Manual" \
		--section='8' --utf8 spm-tools.pod > spm-tools.8
	sed 's|#SHAREDIR#|$(SHAREDIR)|g' -i SRCBUILD.5
	sed 's|#MACHINE#|$(MACHINE)|g' -i spm.conf.5
	sed 's|#ARCH#|$(ARCH)|g' -i spm.conf.5
	sed 's|#JOBS#|$(JOBS)|g' -i spm.conf.5

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(MANDIR)/man8/ $(DESTDIR)$(MANDIR)/man5/
	$(INSTALL) -vdm755 $(DESTDIR)$(SHAREDIR)/spm/
	$(INSTALL) -vm644 spm.8 $(DESTDIR)$(MANDIR)/man8/spm.8
	$(INSTALL) -vm644 spm.conf.5 $(DESTDIR)$(MANDIR)/man5/spm.conf.5
	$(INSTALL) -vm644 SRCBUILD.5 $(DESTDIR)$(MANDIR)/man5/SRCBUILD.5
	$(INSTALL) -vm644 SRCBUILD.txt $(DESTDIR)$(SHAREDIR)/spm/SRCBUILD.txt
	$(INSTALL) -vm644 spm-tools.8 $(DESTDIR)$(MANDIR)/man8/spm-tools.8
	$(INSTALL) -vm644 powerd.8 $(DESTDIR)$(MANDIR)/man8/powerd.8
	$(INSTALL) -vm644 powerctl.8 $(DESTDIR)$(MANDIR)/man8/powerctl.8
	$(INSTALL) -vm644 powerd.conf.5 $(DESTDIR)$(MANDIR)/man5/powerd.conf.5

uninstall:
	$(RM) $(DESTDIR)$(MANDIR)/man8/powerd.8
	$(RM) $(DESTDIR)$(MANDIR)/man8/powerctl.8
	$(RM) $(DESTDIR)$(MANDIR)/man5/powerd.conf.5


clean:
	$(RM) *.8 *.5