include ../../Makefile.inc

all: clean
	mkdir -p build
	pyuic4 qdesktop.ui -o qdesktop_ui.py
	$(CYTHON) -2 -D -t qdesktop_ui.py -o build/qdesktop_ui.c
	$(CC) $(CFLAGS) -shared build/qdesktop_ui.c -o build/qdesktop_ui.so
	$(CYTHON) --embed -2 -D -t main.py -o build/main.c
	$(CC) $(CFLAGS) build/main.c -o build/main
	$(STRIP) build/qdesktop_ui.so build/main

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR) $(DESTDIR)$(SITEDIR)
	$(INSTALL) -vm644 build/qdesktop_ui.so $(DESTDIR)$(SITEDIR)/qdesktop_ui.so
	$(INSTALL) -vm755 build/main $(DESTDIR)$(BINDIR)/qdesktop

uninstall:
	$(RM) $(DESTDIR)$(SITEDIR)/qdesktop_ui.so
	$(RM) $(DESTDIR)$(BINDIR)/qdesktop

clean:
	$(RM) -r build/
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo') qdesktop_ui.py

.PHONY: all install uninstall clean
