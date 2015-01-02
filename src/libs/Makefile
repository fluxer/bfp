include ../../Makefile.inc

all: clean
	$(NUITKA) --module libmagic.py
	$(NUITKA) --module libmessage.py
	$(NUITKA) --module libmisc.py
	$(NUITKA) --module libpackage.py
	$(STRIP) *.so

check:
	$(PYTHON) test.py

install:
	$(INSTALL) -dm755 $(DESTDIR)$(SITEDIR)
	$(INSTALL) -m644 *.so $(DESTDIR)$(SITEDIR)/

uninstall:
	$(RM) $(DESTDIR)$(SITEDIR)/libmagic.so
	$(RM) $(DESTDIR)$(SITEDIR)/libmessage.so
	$(RM) $(DESTDIR)$(SITEDIR)/libmisc.so
	$(RM) $(DESTDIR)$(SITEDIR)/libpackage.so

clean:
	$(RM) -r *.build/ *.so __pycache__
	$(RM) $(shell $(FIND) . -name '*.pyc' -o -name '*.pyo')

.PHONY: all check install uninstall clean
