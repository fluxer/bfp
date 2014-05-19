include ../../Makefile.inc

all: clean
	mkdir -p build
	pyuic4 qproperties.ui -o qproperties_ui.py
	$(CYTHON) -2 -D -t qproperties_ui.py -o build/qproperties_ui.c
	$(CC) $(CFLAGS) -shared build/qproperties_ui.c -o build/qproperties_ui.so
	$(CYTHON) --embed -2 -D -t main.py -o build/main.c
	$(CC) $(CFLAGS) build/main.c -o build/main
	$(STRIP) build/qproperties_ui.so build/main

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR) $(DESTDIR)$(SITEDIR)
	$(INSTALL) -vm644 build/qproperties_ui.so $(DESTDIR)$(SITEDIR)/qproperties_ui.so
	$(INSTALL) -vm755 build/main $(DESTDIR)$(BINDIR)/qproperties

uninstall:
	$(RM) $(DESTDIR)$(SITEDIR)/qproperties_ui.so
	$(RM) $(DESTDIR)$(BINDIR)/qproperties

clean:
	$(RM) -r build/
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo') qproperties_ui.py

.PHONY: all install uninstall clean
