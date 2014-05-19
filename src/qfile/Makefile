include ../../Makefile.inc

all: clean
	mkdir -p build
	pyuic4 qfile.ui -o qfile_ui.py
	$(CYTHON) -2 -D -t qfile_ui.py -o build/qfile_ui.c
	$(CC) $(CFLAGS) -shared build/qfile_ui.c -o build/qfile_ui.so
	$(CYTHON) --embed -2 -D -t main.py -o build/main.c
	$(CC) $(CFLAGS) build/main.c -o build/main
	$(STRIP) build/qfile_ui.so build/main

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR) $(DESTDIR)$(SITEDIR)
	$(INSTALL) -vm644 build/qfile_ui.so $(DESTDIR)$(SITEDIR)/qfile_ui.so
	$(INSTALL) -vm755 build/main $(DESTDIR)$(BINDIR)/qfile

uninstall:
	$(RM) $(DESTDIR)$(SITEDIR)/qfile_ui.so
	$(RM) $(DESTDIR)$(BINDIR)/qfile

clean:
	$(RM) -r build/
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo') qfile_ui.py

.PHONY: all install uninstall clean
