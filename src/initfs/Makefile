include ../../Makefile.mk

all:
	$(SED) 's|^app_version.*|app_version = "$(VERSION) ($(GIT_VERSION))"|' -i lsinitfs.py mkinitfs.py

install:
	$(INSTALL) -dm755 $(DESTDIR)$(BINDIR) $(DESTDIR)$(SBINDIR)
	$(INSTALL) -dm755 $(DESTDIR)/etc/mkinitfs
	$(INSTALL) -m755 mkinitfs.py $(DESTDIR)$(SBINDIR)/mkinitfs
	$(INSTALL) -m755 lsinitfs.py $(DESTDIR)$(BINDIR)/lsinitfs
	$(CP) -r root $(DESTDIR)/etc/mkinitfs/
	$(CP) -r files $(DESTDIR)/etc/mkinitfs/

uninstall:
	$(RM) $(DESTDIR)$(SBINDIR)/mkinitfs
	$(RM) $(DESTDIR)$(BINDIR)/lsinitfs
	$(RM) -r $(DESTDIR)/etc/mkinitfs

clean:
	$(RM) -r __pycache__
	$(RM) $(shell $(FIND) . -name '*.pyc' -o -name '*.pyo')

.PHONY: all install uninstall clean
