include ../../Makefile.inc

all: clean
	mkdir -p build
	pyuic4 qnetwork.ui -o qnetwork_ui.py
	$(CYTHON) -2 -D -t qnetwork_ui.py -o build/qnetwork_ui.c
	$(CC) $(CFLAGS) -shared build/qnetwork_ui.c -o build/qnetwork_ui.so
	$(CYTHON) --embed -2 -D -t main.py -o build/main.c
	$(CC) $(CFLAGS) build/main.c -o build/main
	$(STRIP) build/qnetwork_ui.so build/main

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR) $(DESTDIR)$(SITEDIR)
	$(INSTALL) -vm644 build/qnetwork_ui.so $(DESTDIR)$(SITEDIR)/qnetwork_ui.so
	$(INSTALL) -vm755 build/main $(DESTDIR)$(BINDIR)/qnetwork

uninstall:
	$(RM) $(DESTDIR)$(SITEDIR)/qnetwork_ui.so
	$(RM) $(DESTDIR)$(BINDIR)/qnetwork

clean:
	$(RM) -r build/
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo') qnetwork_ui.py

.PHONY: all install uninstall clean
