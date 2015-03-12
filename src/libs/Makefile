include ../../Makefile.inc

.py:
	$(NUITKA) --module $<

all: clean
	$(NUITKA) --module libinotify.py
	$(NUITKA) --module libmagic.py
	$(NUITKA) --module libmessage.py
	$(NUITKA) --module libmisc.py
	$(NUITKA) --module libpackage.py
	$(STRIP) *.so

cython: clean
	$(CYTHON)  --lenient libinotify.py
	$(CYTHON) libmagic.py libmessage.py libmisc.py libpackage.py
	$(CC) -shared libinotify.c $(shell pkg-config --cflags $(PYTHON)) -o libinotify.so
	$(CC) -shared libmagic.c $(shell pkg-config --cflags $(PYTHON)) -o libmagic.so
	$(CC) -shared libmessage.c $(shell pkg-config --cflags $(PYTHON)) -o libmessage.so
	$(CC) -shared libmisc.c $(shell pkg-config --cflags $(PYTHON)) -o libmisc.so
	$(CC) -shared libpackage.c $(shell pkg-config --cflags $(PYTHON)) -o libpackage.so
	$(STRIP) *.so

check:
	$(PYTHON) test.py

install:
	$(INSTALL) -dm755 $(DESTDIR)$(SITEDIR)
	$(INSTALL) -m644 *.so $(DESTDIR)$(SITEDIR)/

uninstall:
	$(RM) $(DESTDIR)$(SITEDIR)/libdialog.so
	$(RM) $(DESTDIR)$(SITEDIR)/libinotify.so
	$(RM) $(DESTDIR)$(SITEDIR)/libmagic.so
	$(RM) $(DESTDIR)$(SITEDIR)/libmessage.so
	$(RM) $(DESTDIR)$(SITEDIR)/libmisc.so
	$(RM) $(DESTDIR)$(SITEDIR)/libpackage.so

clean:
	$(RM) -r *.build/ *.so __pycache__ *.c
	$(RM) $(shell $(FIND) . -name '*.pyc' -o -name '*.pyo')

.SUFFIXES: .py
.PHONY: all cython check install uninstall clean
