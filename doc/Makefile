include ../Makefile.inc

all:
	$(POD2MAN) --release="SPM $(VERSION)" --center="Source Package Manager Manual" \
		--section='8' --utf8 spm.pod spm.8
	$(POD2MAN)  --release="SPM $(VERSION)" --center="Source Package Manager Manual" \
		--section='5' --utf8 spm.conf.pod spm.conf.5
	$(POD2MAN)  --release="SPM $(VERSION)" --center="Source Package Manager Manual" \
		--section='5' --utf8 SRCBUILD.pod SRCBUILD.5
	$(POD2MAN)  --release="SPM $(VERSION)" --center="Source Package Manager Manual" \
		--section='8' --utf8 spm-tools.pod > spm-tools.8
	$(POD2MAN)  --release="CPARTED $(VERSION)" --center="Curses Parted Manual" \
		--section='8' --utf8 cparted.pod > cparted.8
	$(POD2MAN)  --release="MKINITFS $(VERSION)" --center="MkInitfs Manual" \
		--section='8' --utf8 mkinitfs.pod > mkinitfs.8
	$(POD2MAN)  --release="LSINITFS $(VERSION)" --center="LsInitfs Manual" \
		--section='8' --utf8 lsinitfs.pod > lsinitfs.8
	$(SED) 's|#SHAREDIR#|$(SHAREDIR)|g' -i SRCBUILD.5
	$(SED) 's|#MACHINE#|$(MACHINE)|g' -i spm.conf.5
	$(SED) 's|#ARCH#|$(ARCH)|g' -i spm.conf.5
	$(SED) 's|#JOBS#|$(JOBS)|g' -i spm.conf.5

install:
	$(INSTALL) -dm755 $(DESTDIR)$(MANDIR)/man8/ $(DESTDIR)$(MANDIR)/man5/
	$(INSTALL) -dm755 $(DESTDIR)$(SHAREDIR)/spm/
	$(INSTALL) -m644 spm.8 $(DESTDIR)$(MANDIR)/man8/spm.8
	$(INSTALL) -m644 spm.conf.5 $(DESTDIR)$(MANDIR)/man5/spm.conf.5
	$(INSTALL) -m644 SRCBUILD.5 $(DESTDIR)$(MANDIR)/man5/SRCBUILD.5
	$(INSTALL) -m644 SRCBUILD.txt $(DESTDIR)$(SHAREDIR)/spm/SRCBUILD.txt
	$(INSTALL) -m644 spm-tools.8 $(DESTDIR)$(MANDIR)/man8/spm-tools.8
	$(INSTALL) -m644 cparted.8 $(DESTDIR)$(MANDIR)/man8/cparted.8
	$(INSTALL) -m644 mkinitfs.8 $(DESTDIR)$(MANDIR)/man8/mkinitfs.8
	$(INSTALL) -m644 lsinitfs.8 $(DESTDIR)$(MANDIR)/man8/lsinitfs.8

uninstall:
	$(RM) $(DESTDIR)$(MANDIR)/man8/spm-tools.8
	$(RM) $(DESTDIR)$(MANDIR)/man8/spm-tools.8
	$(RM) $(DESTDIR)$(MANDIR)/man5/SRCBUILD.5
	$(RM) $(DESTDIR)$(MANDIR)/man5/spm.conf.5
	$(RM) -r $(DESTDIR)$(SHAREDIR)/spm/
	$(RM) $(DESTDIR)$(MANDIR)/man8/cparted.8
	$(RM) $(DESTDIR)$(MANDIR)/man8/mkinitfs.8
	$(RM) $(DESTDIR)$(MANDIR)/man8/lsinitfs.8

clean:
	$(RM) *.8 *.5

.PHONY: all install uninstall clean
