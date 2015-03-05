include ../../Makefile.inc

.py:
	$(NUITKA) $<

all: bump clean
	$(NUITKA) mkinitfs.py
	$(NUITKA) lsinitfs.py
	$(STRIP) *.exe

install:
	$(INSTALL) -dm755 $(DESTDIR)$(BINDIR) $(DESTDIR)$(SBINDIR)
	$(INSTALL) -dm755 $(DESTDIR)/etc/mkinitfs
	$(INSTALL) -m755 mkinitfs.exe $(DESTDIR)$(SBINDIR)/mkinitfs
	$(INSTALL) -m755 lsinitfs.exe $(DESTDIR)$(BINDIR)/lsinitfs
	$(CP) -a root $(DESTDIR)/etc/mkinitfs/
	$(CP) -a files $(DESTDIR)/etc/mkinitfs/

uninstall:
	$(RM) $(DESTDIR)$(SBINDIR)/mkinitfs
	$(RM) $(DESTDIR)$(BINDIR)/lsinitfs
	$(RM) -r $(DESTDIR)/etc/mkinitfs

clean:
	$(RM) -r *.build/ *.exe __pycache__
	$(RM) $(shell $(FIND) . -name '*.pyc' -o -name '*.pyo')

bump:
	$(SED) 's|^app_version.*|app_version = "$(VERSION) ($(GIT_VERSION))"|' -i lsinitfs.py mkinitfs.py

.SUFFIXES: .py
.PHONY: all install uninstall clean bump
