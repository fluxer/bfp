include ../../Makefile.inc

all: clean
	mkdir -p build
	pyuic4 qedit.ui -o qedit_ui.py
	$(CYTHON) -2 -D -t qedit_ui.py -o build/qedit_ui.c
	$(CC) $(CFLAGS) -shared build/qedit_ui.c -o build/qedit_ui.so
	$(CYTHON) --embed -2 -D -t main.py -o build/main.c
	$(CC) $(CFLAGS) build/main.c -o build/main
	$(STRIP) build/qedit_ui.so build/main

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR) $(DESTDIR)$(SITEDIR)
	$(INSTALL) -vm644 build/qedit_ui.so $(DESTDIR)$(SITEDIR)/qedit_ui.so
	$(INSTALL) -vm755 build/main $(DESTDIR)$(BINDIR)/qedit

uninstall:
	$(RM) $(DESTDIR)$(SITEDIR)/qedit_ui.so
	$(RM) $(DESTDIR)$(BINDIR)/qedit

clean:
	$(RM) -r build/
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo') qedit_ui.py

.PHONY: all install uninstall clean
