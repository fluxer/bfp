include ../../Makefile.inc

all: clean
	$(NUITKA) --module libarchive.py
	$(NUITKA) --module libmagic.py
	$(NUITKA) --module libmessage.py 
	$(NUITKA) --module libmisc.py
	$(NUITKA) --module libpackage.py
	$(NUITKA) --module libsystem.py
	$(NUITKA) --module libworkspace.py
	$(NUITKA) --module libxlib.py
	$(STRIP) libarchive.so libmagic.so libmessage.so libmisc.so libpackage.so \
		libsystem.so libworkspace.so libxlib.so

check:
	$(PYTHON) test.py

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(SITEDIR)
	$(INSTALL) -vm644 libarchive.so $(DESTDIR)$(SITEDIR)/libarchive.so
	$(INSTALL) -vm644 libmagic.so $(DESTDIR)$(SITEDIR)/libmagic.so
	$(INSTALL) -vm644 libmessage.so $(DESTDIR)$(SITEDIR)/libmessage.so
	$(INSTALL) -vm644 libmisc.so $(DESTDIR)$(SITEDIR)/libmisc.so
	$(INSTALL) -vm644 libpackage.so $(DESTDIR)$(SITEDIR)/libpackage.so
	$(INSTALL) -vm644 libsystem.so $(DESTDIR)$(SITEDIR)/libsystem.so
	$(INSTALL) -vm644 libworkspace.so $(DESTDIR)$(SITEDIR)/libworkspace.so
	$(INSTALL) -vm644 libxlib.so $(DESTDIR)$(SITEDIR)/libxlib.so

uninstall:
	$(RM) $(DESTDIR)$(SITEDIR)/libarchive.so
	$(RM) $(DESTDIR)$(SITEDIR)/libmagic.so
	$(RM) $(DESTDIR)$(SITEDIR)/libmessage.so
	$(RM) $(DESTDIR)$(SITEDIR)/libmisc.so
	$(RM) $(DESTDIR)$(SITEDIR)/libpackage.so
	$(RM) $(DESTDIR)$(SITEDIR)/libsystem.so
	$(RM) $(DESTDIR)$(SITEDIR)/libworkspace.so
	$(RM) $(DESTDIR)$(SITEDIR)/libxlib.so

clean:
	$(RM) -r *.build/ *.so
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo')

.PHONY: all check install uninstall clean
