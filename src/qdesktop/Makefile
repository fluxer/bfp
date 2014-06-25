include ../../Makefile.inc

all: clean
	$(PYUIC) qdesktop.ui -o qdesktop_ui.py
	$(NUITKA) --recurse-to=qdesktop_ui main.py
	$(STRIP) main.exe

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR)
	$(INSTALL) -vm755 main.exe $(DESTDIR)$(BINDIR)/qdesktop

uninstall:
	$(RM) $(DESTDIR)$(BINDIR)/qdesktop

clean:
	$(RM) -r *.build/ *.exe qdesktop_ui.py
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo')

.PHONY: all install uninstall clean
