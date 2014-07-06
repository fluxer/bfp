include ../../Makefile.inc

all: clean
	$(NUITKA) main.py
	$(STRIP) main.exe

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(SBINDIR)
	$(INSTALL) -vm755 main.exe $(DESTDIR)$(SBINDIR)/qmanager

uninstall:
	$(RM) $(DESTDIR)$(SBINDIR)/qmanager

clean:
	$(RM) -r *.build/ *.exe
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo')

.PHONY: all install uninstall clean
