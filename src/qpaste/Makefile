include ../../Makefile.inc

all: clean
	mkdir -p build
	pyuic4 qpaste.ui -o qpaste_ui.py
	$(CYTHON) -2 -D -t qpaste_ui.py -o build/qpaste_ui.c
	$(CC) $(CFLAGS) -shared build/qpaste_ui.c -o build/qpaste_ui.so
	$(CYTHON) --embed -2 -D -t main.py -o build/main.c
	$(CC) $(CFLAGS) build/main.c -o build/main
	$(STRIP) build/qpaste_ui.so build/main

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR) $(DESTDIR)$(SITEDIR)
	$(INSTALL) -vm644 build/qpaste_ui.so $(DESTDIR)$(SITEDIR)/qpaste_ui.so
	$(INSTALL) -vm755 build/main $(DESTDIR)$(BINDIR)/qpaste

uninstall:
	$(RM) $(DESTDIR)$(SITEDIR)/qpaste_ui.so
	$(RM) $(DESTDIR)$(BINDIR)/qpaste

clean:
	$(RM) -r build/
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo') qpaste_ui.py

.PHONY: all install uninstall clean
