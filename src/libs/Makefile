include ../../Makefile.mk

.py:
	$(NUITKA) --module $<

all: clean
	$(NUITKA) --module libarchive.py
	$(NUITKA) --module libmessage.py
	$(NUITKA) --module libmisc.py
	$(NUITKA) --module libpackage.py
	$(NUITKA) --module libsystem.py
	$(NUITKA) --module libudev.py
	$(CC) -shared _libudev.c \
		$(shell $(PYTHON)-config --includes --libs) \
		$(shell pkg-config --cflags --libs libudev) \
		-o _libudev.so
	$(STRIP) *.so

cython: clean
	$(CYTHON) libarchive.py libmessage.py libmisc.py libpackage.py libsystem.py libudev.py
	$(CC) -shared libarchive.c $(shell $(PYTHON)-config --includes --libs) -o libarchive.so
	$(CC) -shared libmessage.c $(shell $(PYTHON)-config --includes --libs) -o libmessage.so
	$(CC) -shared libmisc.c $(shell $(PYTHON)-config --includes --libs) -o libmisc.so
	$(CC) -shared libpackage.c $(shell $(PYTHON)-config --includes --libs) -o libpackage.so
	$(CC) -shared libsystem.c $(shell $(PYTHON)-config --includes --libs) -o libsystem.so
	# _libudev WILL NOT WORK!
	$(CC) -shared _libudev.c \
		$(shell $(PYTHON)-config --includes --libs) \
		$(shell pkg-config --cflags --libs libudev) \
		-o _libudev.so
	$(STRIP) *.so

check:
	$(PYTHON) test.py

install:
	$(INSTALL) -dm755 $(DESTDIR)$(SITEDIR)
	$(INSTALL) -m644 *.so $(DESTDIR)$(SITEDIR)/

uninstall:
	$(RM) $(DESTDIR)$(SITEDIR)/libarchive.so
	$(RM) $(DESTDIR)$(SITEDIR)/libmessage.so
	$(RM) $(DESTDIR)$(SITEDIR)/libmisc.so
	$(RM) $(DESTDIR)$(SITEDIR)/libpackage.so
	$(RM) $(DESTDIR)$(SITEDIR)/libsystem.so
	$(RM) $(DESTDIR)$(SITEDIR)/libudev.so
	$(RM) $(DESTDIR)$(SITEDIR)/_libudev.so

clean:
	$(RM) -r *.build/ *.so __pycache__ lib*.c
	$(RM) $(shell $(FIND) . -name '*.pyc' -o -name '*.pyo')

.SUFFIXES: .py
.PHONY: all cython check install uninstall clean
