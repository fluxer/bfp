include ../../Makefile.inc

all: clean
	$(PYUIC) qproperties.ui -o qproperties_ui.py
	$(NUITKA) --recurse-to=qproperties_ui main.py
	$(STRIP) main.exe

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR)
	$(INSTALL) -vm755 main.exe $(DESTDIR)$(BINDIR)/qproperties

uninstall:
	$(RM) $(DESTDIR)$(BINDIR)/qproperties

clean:
	$(RM) -r *.build/ *.exe qproperties_ui.py
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo')

.PHONY: all install uninstall clean
