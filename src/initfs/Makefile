include ../../Makefile.inc

all: bump clean
	$(NUITKA) mkinitfs.py
	$(NUITKA) lsinitfs.py
	$(STRIP) mkinitfs.exe lsinitfs.exe

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR) $(DESTDIR)$(SBINDIR)
	$(INSTALL) -vdm755 $(DESTDIR)$(ETCDIR)
	$(INSTALL) -vm755 mkinitfs.exe $(DESTDIR)$(SBINDIR)/mkinitfs
	$(INSTALL) -vm755 lsinitfs.exe $(DESTDIR)$(BINDIR)/lsinitfs
	$(CP) -a root $(DESTDIR)$(ETCDIR)/mkinitfs
	$(CP) -a files $(DESTDIR)$(ETCDIR)/mkinitfs

uninstall:
	$(RM) $(DESTDIR)$(SBINDIR)/mkinitfs
	$(RM) $(DESTDIR)$(BINDIR)/lsinitfs
	$(RM) -r $(DESTDIR)$(ETCDIR)/mkinitfs

clean:
	$(RM) -r *.build/ *.exe
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo')

bump:
	$(SED) 's|^app_version.*|app_version = "$(VERSION) ($(GIT_VERSION))"|' -i lsinitfs.py mkinitfs.py

.PHONY: all install uninstall clean bump
