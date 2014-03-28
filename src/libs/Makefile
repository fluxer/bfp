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
	$(CYTHON) -2 libpower.py -o build/libpower.c
	$(CC) $(CFLAGS) -shared build/libpower.c -o build/libpower.so
	$(CYTHON) -2 libnetwork.py -o build/libnetwork.c
	$(CC) $(CFLAGS) -shared build/libnetwork.c -o build/libnetwork.so
	$(CYTHON) -2 libservice.py -o build/libservice.c
	$(CC) $(CFLAGS) -shared build/libservice.c -o build/libservice.so
	$(CYTHON) -2 libdevice.py -o build/libdevice.c
	$(CC) $(CFLAGS) -shared build/libdevice.c -o build/libdevice.so
	$(CYTHON) -2 libsh.py -o build/libsh.c
	$(CC) $(CFLAGS) -shared build/libsh.c -o build/libsh.so
	$(STRIP) build/libmagic.so build/libmisc.so build/libpackage.so \
		build/libpower.so build/libnetwork.so build/libservice.so \
		build/libdevice.so build/libsh.so

check:
	python test.py

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(SITEDIR)
	$(INSTALL) -vm644 build/libmagic.so $(DESTDIR)$(SITEDIR)/libmagic.so
	$(INSTALL) -vm644 build/libmessage.so $(DESTDIR)$(SITEDIR)/libmessage.so
	$(INSTALL) -vm644 build/libmisc.so $(DESTDIR)$(SITEDIR)/libmisc.so
	$(INSTALL) -vm644 build/libpackage.so $(DESTDIR)$(SITEDIR)/libpackage.so
	$(INSTALL) -vm644 build/libpower.so $(DESTDIR)$(SITEDIR)/libpower.so
	$(INSTALL) -vm644 build/libnetwork.so $(DESTDIR)$(SITEDIR)/libnetwork.so
	$(INSTALL) -vm644 build/libservice.so $(DESTDIR)$(SITEDIR)/libservice.so
	$(INSTALL) -vm644 build/libdevice.so $(DESTDIR)$(SITEDIR)/libdevice.so
	$(INSTALL) -vm644 build/libsh.so $(DESTDIR)$(SITEDIR)/libsh.so

uninstall:
	$(RM) $(DESTDIR)$(SITEDIR)/libmagic.so
	$(RM) $(DESTDIR)$(SITEDIR)/libmessage.so
	$(RM) $(DESTDIR)$(SITEDIR)/libmisc.so
	$(RM) $(DESTDIR)$(SITEDIR)/libpackage.so
	$(RM) $(DESTDIR)$(SITEDIR)/libpower.so
	$(RM) $(DESTDIR)$(SITEDIR)/libnetwork.so
	$(RM) $(DESTDIR)$(SITEDIR)/libservice.so
	$(RM) $(DESTDIR)$(SITEDIR)/libdevice.so
	$(RM) $(DESTDIR)$(SITEDIR)/libsh.so

clean:
	$(RM) -r build/
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo')

.PHONY: all check install uninstall clean
