include ../../Makefile.inc

all: clean
	$(PYUIC) qopen.ui -o qopen_ui.py
	$(NUITKA) --recurse-to=qopen_ui main.py
	$(STRIP) main.exe

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR)
	$(INSTALL) -vm755 main.exe $(DESTDIR)$(BINDIR)/qopen

uninstall:
	$(RM) $(DESTDIR)$(BINDIR)/qopen

clean:
	$(RM) -r *.build/ *.exe qopen_ui.py
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo')

.PHONY: all install uninstall clean
