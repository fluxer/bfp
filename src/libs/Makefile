include ../../Makefile.inc

all: clean
	mkdir -p build/
	$(CYTHON) -2 libmagic.py -o build/libmagic.c
	$(CC) $(CFLAGS) -shared build/libmagic.c -o build/libmagic.so
	$(CYTHON) -2 libmessage.py -o build/libmessage.c
	$(CC) $(CFLAGS) -shared build/libmessage.c -o build/libmessage.so
	$(CYTHON) -2 libmisc.py -o build/libmisc.c
	$(CC) $(CFLAGS) -shared build/libmisc.c -o build/libmisc.so
	$(CYTHON) -2 libpackage.py -o build/libpackage.c
	$(CC) $(CFLAGS) -shared build/libpackage.c -o build/libpackage.so
	$(CYTHON) -2 libnetwork.py -o build/libnetwork.c
	$(CC) $(CFLAGS) -shared build/libnetwork.c -o build/libnetwork.so
	$(CYTHON) -2 libsystem.py -o build/libsystem.c
	$(CC) $(CFLAGS) -shared build/libsystem.c -o build/libsystem.so
	$(CYTHON) -2 libqdesktop.py -o build/libqdesktop.c
	$(CC) $(CFLAGS) -shared build/libqdesktop.c -o build/libqdesktop.so
	$(STRIP) build/libmagic.so build/libmessage.so build/libmisc.so \
		build/libpackage.so build/libnetwork.so build/libsystem.so \
		build/libqdesktop.so

check:
	python test.py

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(SITEDIR)
	$(INSTALL) -vm644 build/libmagic.so $(DESTDIR)$(SITEDIR)/libmagic.so
	$(INSTALL) -vm644 build/libmessage.so $(DESTDIR)$(SITEDIR)/libmessage.so
	$(INSTALL) -vm644 build/libmisc.so $(DESTDIR)$(SITEDIR)/libmisc.so
	$(INSTALL) -vm644 build/libpackage.so $(DESTDIR)$(SITEDIR)/libpackage.so
	$(INSTALL) -vm644 build/libnetwork.so $(DESTDIR)$(SITEDIR)/libnetwork.so
	$(INSTALL) -vm644 build/libsystem.so $(DESTDIR)$(SITEDIR)/libsystem.so
	$(INSTALL) -vm644 build/libqdesktop.so $(DESTDIR)$(SITEDIR)/libqdesktop.so

uninstall:
	$(RM) $(DESTDIR)$(SITEDIR)/libmagic.so
	$(RM) $(DESTDIR)$(SITEDIR)/libmessage.so
	$(RM) $(DESTDIR)$(SITEDIR)/libmisc.so
	$(RM) $(DESTDIR)$(SITEDIR)/libpackage.so
	$(RM) $(DESTDIR)$(SITEDIR)/libnetwork.so
	$(RM) $(DESTDIR)$(SITEDIR)/libsystem.so
	$(RM) $(DESTDIR)$(SITEDIR)/libqdesktop.so

clean:
	$(RM) -r build/
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo')

.PHONY: all check install uninstall clean
