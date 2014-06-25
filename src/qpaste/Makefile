include ../../Makefile.inc

all: clean
	$(PYUIC) qpaste.ui -o qpaste_ui.py
	$(NUITKA) --recurse-to=qpaste_ui main.py
	$(STRIP) main.exe

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR)
	$(INSTALL) -vm755 main.exe $(DESTDIR)$(BINDIR)/qpaste

uninstall:
	$(RM) $(DESTDIR)$(BINDIR)/qpaste

clean:
	$(RM) -r *.build/ *.exe qpaste_ui.py
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo')

.PHONY: all install uninstall clean
