include ../../Makefile.inc

all: bump clean
	mkdir -p build
	$(PYUIC) qt.ui -o libqt4.py
	$(CYTHON) -2 libqt4.py -o build/libqt4.c
	$(CC) $(CFLAGS) -shared build/libqt4.c -o build/libqt4.so
	$(CYTHON) -2 libconfig.py -o build/libconfig.c
	$(CC) $(CFLAGS) -shared build/libconfig.c -o build/libconfig.so
	$(CYTHON) -2 libmode.py -o build/libmode.c
	$(CC) $(CFLAGS) -shared build/libmode.c -o build/libmode.so
	$(CYTHON) -2 --embed -I. qt.py -o build/qt.c
	$(CC) $(CFLAGS) build/qt.c -o build/spm-qt
	$(STRIP) build/libqt4.so build/libconfig.so build/libmode.so build/spm-qt

check:
	python2 test.py

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR)
	$(INSTALL) -vm755 build/spm-qt $(DESTDIR)$(BINDIR)/spm-qt
	$(INSTALL) -vm644 build/libqt4.so $(DESTDIR)$(SITEDIR)/libqt4.so
	$(INSTALL) -vm644 build/libconfig.so $(DESTDIR)$(SITEDIR)/libconfig.so
	$(INSTALL) -vm644 build/libmode.so $(DESTDIR)$(SITEDIR)/libmode.so

uninstall:
	$(RM) $(DESTDIR)$(BINDIR)/spm-qt
	$(RM) $(DESTDIR)$(SITEDIR)/libqt4.so
	$(RM) $(DESTDIR)$(SITEDIR)/libconfig.so
	$(RM) $(DESTDIR)$(SITEDIR)/libmode.so

clean:
	$(RM) -r build
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo')

bump:
	sed 's|^app_version.*|app_version = "$(VERSION) ($(GIT_VERSION))"|' -i qt.py

.PHONY: all check install uninstall clean bump
