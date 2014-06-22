include ../../Makefile.inc

all: clean
	mkdir -p build
	pyuic4 qpanel.ui -o qpanel_ui.py
	$(CYTHON) -2 -D -t qpanel_ui.py -o build/qpanel_ui.c
	$(CC) $(CFLAGS) -shared build/qpanel_ui.c -o build/qpanel_ui.so
	$(CYTHON) --embed -2 -D -t main.py -o build/main.c
	$(CC) $(CFLAGS) build/main.c -o build/main
	$(STRIP) build/qpanel_ui.so build/main

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR) $(DESTDIR)$(SITEDIR)
	$(INSTALL) -vm644 build/qpanel_ui.so $(DESTDIR)$(SITEDIR)/qpanel_ui.so
	$(INSTALL) -vm755 build/main $(DESTDIR)$(BINDIR)/qpanel

uninstall:
	$(RM) $(DESTDIR)$(SITEDIR)/qpanel_ui.so
	$(RM) $(DESTDIR)$(BINDIR)/qpanel

clean:
	$(RM) -r build/
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo') qfile_ui.py

.PHONY: all install uninstall clean
