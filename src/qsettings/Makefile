include ../../Makefile.inc

all: clean
	mkdir -p build
	pyuic4 qsettings.ui -o qsettings_ui.py
	$(CYTHON) -2 -D -t qsettings_ui.py -o build/qsettings_ui.c
	$(CC) $(CFLAGS) -shared build/qsettings_ui.c -o build/qsettings_ui.so
	$(CYTHON) --embed -2 -D -t main.py -o build/main.c
	$(CC) $(CFLAGS) build/main.c -o build/main
	$(STRIP) build/qsettings_ui.so build/main

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR) $(DESTDIR)$(SITEDIR)
	$(INSTALL) -vm644 build/qsettings_ui.so $(DESTDIR)$(SITEDIR)/qsettings_ui.so
	$(INSTALL) -vm755 build/main $(DESTDIR)$(BINDIR)/qsettings

uninstall:
	$(RM) $(DESTDIR)$(SITEDIR)/qsettings_ui.so
	$(RM) $(DESTDIR)$(BINDIR)/qsettings

clean:
	$(RM) -r build/
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo') qsettings_ui.py

.PHONY: all install uninstall clean
