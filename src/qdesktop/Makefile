include ../../Makefile.inc

all: clean
	mkdir -p build
	pyuic4 qdesktop.ui -o qdesktop.py
	pyrcc4 qdesktop.qrc -o qdesktop_rc.py
	$(CYTHON) -2 -D -t qdesktop.py -o build/qdesktop.c
	$(CC) $(CFLAGS) -shared build/qdesktop.c -o build/qdesktop.so
	$(CYTHON) -2 -D -t qdesktop_rc.py -o build/qdesktop_rc.c
	$(CC) $(CFLAGS) -shared build/qdesktop_rc.c -o build/qdesktop_rc.so
	$(CYTHON) --embed -2 -D -t main.py -o build/main.c
	$(CC) $(CFLAGS) build/main.c -o build/main
	$(STRIP) build/qdesktop.so build/qdesktop_rc.so build/main

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
