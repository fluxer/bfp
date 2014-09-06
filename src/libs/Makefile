include ../../Makefile.inc

all: clean
	$(NUITKA) --module libarchive.py
	$(NUITKA) --module libmagic.py
	$(NUITKA) --module libmessage.py 
	$(NUITKA) --module libmisc.py
	$(NUITKA) --module libpackage.py
	$(NUITKA) --module libsystem.py
	# $(NUITKA) --module libxlib.py
	$(STRIP) *.so

check:
	$(PYTHON) test.py

install:
	$(INSTALL) -dm755 $(DESTDIR)$(SITEDIR)
	$(INSTALL) -m644 *.so $(DESTDIR)$(SITEDIR)/

uninstall:
	$(RM) $(DESTDIR)$(SITEDIR)/libarchive.so
	$(RM) $(DESTDIR)$(SITEDIR)/libmagic.so
	$(RM) $(DESTDIR)$(SITEDIR)/libmessage.so
	$(RM) $(DESTDIR)$(SITEDIR)/libmisc.so
	$(RM) $(DESTDIR)$(SITEDIR)/libpackage.so
	$(RM) $(DESTDIR)$(SITEDIR)/libsystem.so
	$(RM) $(DESTDIR)$(SITEDIR)/libxlib.so

clean:
	$(RM) -r *.build/ *.so
	$(RM) $(shell $(FIND) . -name '*.pyc' -o -name '*.pyo')

.PHONY: all check install uninstall clean
