include ../../Makefile.inc

all: clean
	mkdir -p build
	pyuic4 qproperties.ui -o libqproperties.py
	$(CYTHON) -2 -D -t libqproperties.py -o build/libqproperties.c
	$(CC) $(CFLAGS) -shared build/libqproperties.c -o build/libqproperties.so
	$(CYTHON) --embed -2 -D -t main.py -o build/main.c
	$(CC) $(CFLAGS) build/main.c -o build/main
	$(STRIP) build/libqproperties.so build/main

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR) $(DESTDIR)$(SITEDIR)
	$(INSTALL) -vm644 build/libqproperties.so $(DESTDIR)$(SITEDIR)/libqproperties.so
	$(INSTALL) -vm755 build/main $(DESTDIR)$(BINDIR)/qproperties

uninstall:
	$(RM) $(DESTDIR)$(SITEDIR)/libqproperties.so
	$(RM) $(DESTDIR)$(BINDIR)/qproperties

clean:
	$(RM) -r build/
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo') libqfile.py

.PHONY: all install uninstall clean
