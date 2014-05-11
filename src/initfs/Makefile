include ../../Makefile.inc

all: clean
	mkdir -p build
	$(CYTHON) --embed -2 -D -t mkinitfs.py -o build/mkinitfs.c
	$(CC) $(CFLAGS) build/mkinitfs.c -o build/mkinitfs
	$(CYTHON) --embed -2 -D -t lsinitfs.py -o build/lsinitfs.c
	$(CC) $(CFLAGS) build/lsinitfs.c -o build/lsinitfs
	$(STRIP) build/mkinitfs build/lsinitfs

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR) $(DESTDIR)$(SBINDIR) $(DESTDIR)$(ETCDIR)
	$(INSTALL) -vm755 build/mkinitfs $(DESTDIR)$(SBINDIR)/mkinitfs
	$(INSTALL) -vm755 build/lsinitfs $(DESTDIR)$(BINDIR)/lsinitfs
	cp -a root $(DESTDIR)$(ETCDIR)/mkinitfs
	cp -a files $(DESTDIR)$(ETCDIR)/mkinitfs

uninstall:
	$(RM) $(DESTDIR)$(SBINDIR)/mkinitfs
	$(RM) $(DESTDIR)$(BINDIR)/lsinitfs
	$(RM) -r $(DESTDIR)$(ETCDIR)/mkinitfs

clean:
	$(RM) -r build/
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo')

.PHONY: all install uninstall clean
