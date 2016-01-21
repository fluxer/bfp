include ../../Makefile.mk

all: clean
	$(CC) mkinitfs.c $(shell $(PYTHON)-config --includes --libs) $(CFLAGS) -o mkinitfs.exe
	$(CC) lsinitfs.c $(shell $(PYTHON)-config --includes --libs) $(CFLAGS) -o lsinitfs.exe
	$(STRIP) *.exe

sources: bump
	$(RM) *.c
	$(CYTHON) --embed mkinitfs.py
	$(CYTHON) --embed lsinitfs.py

install:
	$(INSTALL) -dm755 $(DESTDIR)$(BINDIR) $(DESTDIR)$(SBINDIR)
	$(INSTALL) -dm755 $(DESTDIR)/etc/mkinitfs
	$(INSTALL) -m755 mkinitfs.exe $(DESTDIR)$(SBINDIR)/mkinitfs
	$(INSTALL) -m755 lsinitfs.exe $(DESTDIR)$(BINDIR)/lsinitfs
	$(CP) -r root $(DESTDIR)/etc/mkinitfs/
	$(CP) -r files $(DESTDIR)/etc/mkinitfs/

uninstall:
	$(RM) $(DESTDIR)$(SBINDIR)/mkinitfs
	$(RM) $(DESTDIR)$(BINDIR)/lsinitfs
	$(RM) -r $(DESTDIR)/etc/mkinitfs

clean:
	$(RM) -r *.build/ *.exe __pycache__
	$(RM) $(shell $(FIND) . -name '*.pyc' -o -name '*.pyo')

bump:
	$(SED) 's|^app_version.*|app_version = "$(VERSION) ($(GIT_VERSION))"|' -i lsinitfs.py mkinitfs.py

.PHONY: all sources install uninstall clean bump
