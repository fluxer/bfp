include ../../Makefile.inc

all: clean
	mkdir -p build
	pyuic4 qdesktop.ui -o libqdesktop.py
	$(CYTHON) -2 -D -t libqdesktop.py -o build/libqdesktop.c
	$(CC) $(CFLAGS) -shared build/libqdesktop.c -o build/libqdesktop.so
	$(CYTHON) --embed -2 -D -t main.py -o build/main.c
	$(CC) $(CFLAGS) build/main.c -o build/main
	$(STRIP) build/libqdesktop.so build/main

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR) $(DESTDIR)$(SITEDIR)
	$(INSTALL) -vm644 build/libqdesktop.so $(DESTDIR)$(SITEDIR)/libqdesktop.so
	$(INSTALL) -vm755 build/main $(DESTDIR)$(BINDIR)/qdesktop

uninstall:
	$(RM) $(DESTDIR)$(SITEDIR)/libqdesktop.so
	$(RM) $(DESTDIR)$(BINDIR)/qdesktop

clean:
	$(RM) -r build/
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo') libqdesktop.py

.PHONY: all install uninstall clean
