include ../../Makefile.inc

all: clean
	mkdir -p build
	pyuic4 qfile.ui -o qfile.py
	pyrcc4 qfile.qrc -o qfile_rc.py
	$(CYTHON) -2 -D -t qfile.py -o build/qfile.c
	$(CC) $(CFLAGS) -shared build/qfile.c -o build/qfile.so
	$(CYTHON) -2 -D -t qfile_rc.py -o build/qfile_rc.c
	$(CC) $(CFLAGS) -shared build/qfile_rc.c -o build/qfile_rc.so
	$(CYTHON) --embed -2 -D -t main.py -o build/main.c
	$(CC) $(CFLAGS) build/main.c -o build/main
	$(STRIP) build/qfile.so build/qfile_rc.so build/main

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
