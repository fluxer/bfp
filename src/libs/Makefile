include ../../Makefile.mk

all: clean
	$(CC) -shared libarchive.c $(shell $(PYTHON)-config --includes --libs) $(CFLAGS) -o libarchive.so
	$(CC) -shared libmessage.c $(shell $(PYTHON)-config --includes --libs) $(CFLAGS) -o libmessage.so
	$(CC) -shared libmisc.c $(shell $(PYTHON)-config --includes --libs) $(CFLAGS) -o libmisc.so
	$(CC) -shared libpackage.c $(shell $(PYTHON)-config --includes --libs) $(CFLAGS) -o libpackage.so
	$(CC) -shared libsystem.c $(shell $(PYTHON)-config --includes --libs) $(CFLAGS) -o libsystem.so
	$(STRIP) *.so

sources:
	$(RM) lib*.c
	$(CYTHON) libarchive.py libmessage.py libmisc.py libpackage.py libsystem.py

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

clean:
	$(RM) -r *.build/ *.so __pycache__
	$(RM) $(shell $(FIND) . -name '*.pyc' -o -name '*.pyo')

.PHONY: all sources check install uninstall clean
