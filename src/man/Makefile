include ../../Makefile.inc

all: clean
	$(NUITKA) main.py
	$(STRIP) main.exe

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR)
	$(INSTALL) -vm755 main.exe $(DESTDIR)$(BINDIR)/pman

uninstall:
	$(RM) $(DESTDIR)$(BINDIR)/pman

clean:
	$(RM) -r *.build/ *.exe
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo')

.PHONY: all install uninstall clean
