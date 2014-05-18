include ../../Makefile.inc

all: clean
	mkdir -p build
	pyuic4 qfile.ui -o libqfile.py
	$(CYTHON) -2 -D -t libqfile.py -o build/libqfile.c
	$(CC) $(CFLAGS) -shared build/libqfile.c -o build/libqfile.so
	$(CYTHON) --embed -2 -D -t main.py -o build/main.c
	$(CC) $(CFLAGS) build/main.c -o build/main
	$(STRIP) build/libqfile.so build/main

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR) $(DESTDIR)$(SITEDIR)
	$(INSTALL) -vm644 build/libqfile.so $(DESTDIR)$(SITEDIR)/libqfile.so
	$(INSTALL) -vm755 build/main $(DESTDIR)$(BINDIR)/qfile

uninstall:
	$(RM) $(DESTDIR)$(SITEDIR)/libqfile.so
	$(RM) $(DESTDIR)$(BINDIR)/qfile

clean:
	$(RM) -r build/
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo') libqfile.py

.PHONY: all install uninstall clean
