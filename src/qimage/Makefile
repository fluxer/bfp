include ../../Makefile.inc

all: clean
	mkdir -p build
	pyuic4 qimage.ui -o qimage_ui.py
	$(CYTHON) -2 -D -t qimage_ui.py -o build/qimage_ui.c
	$(CC) $(CFLAGS) -shared build/qimage_ui.c -o build/qimage_ui.so
	$(CYTHON) --embed -2 -D -t main.py -o build/main.c
	$(CC) $(CFLAGS) build/main.c -o build/main
	$(STRIP) build/qimage_ui.so build/main

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR) $(DESTDIR)$(SITEDIR)
	$(INSTALL) -vm644 build/qimage_ui.so $(DESTDIR)$(SITEDIR)/qimage_ui.so
	$(INSTALL) -vm755 build/main $(DESTDIR)$(BINDIR)/qimage

uninstall:
	$(RM) $(DESTDIR)$(SITEDIR)/qimage_ui.so
	$(RM) $(DESTDIR)$(BINDIR)/qimage

clean:
	$(RM) -r build/
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo') qimage_ui.py

.PHONY: all install uninstall clean
