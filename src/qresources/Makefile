include ../../Makefile.inc

all: clean
	mkdir -p build
	pyrcc4 libqresources.qrc -o libqresources_rc.py
	$(CYTHON) -2 -D -t libqresources_rc.py -o build/libqresources_rc.c
	$(CC) $(CFLAGS) -shared build/libqresources_rc.c -o build/libqresources_rc.so
	$(STRIP) build/libqresources_rc.so

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR) $(DESTDIR)$(SITEDIR)
	$(INSTALL) -vm644 build/libqresources_rc.so $(DESTDIR)$(SITEDIR)/libqresources_rc.so

uninstall:
	$(RM) $(DESTDIR)$(SITEDIR)/libqresources_rc.so

clean:
	$(RM) -r build/
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo') libqresources_rc.py

.PHONY: all install uninstall clean
