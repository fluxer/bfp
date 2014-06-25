include ../../Makefile.inc

all: clean
	$(PYUIC) qpanel.ui -o qpanel_ui.py
	$(NUITKA) --recurse-to=qpanel_ui main.py
	$(STRIP) main.exe

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR)
	$(INSTALL) -vm755 main.exe $(DESTDIR)$(BINDIR)/qpanel

uninstall:
	$(RM) $(DESTDIR)$(BINDIR)/qpanel

clean:
	$(RM) -r *.build/ *.exe qpanel_ui.py
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo')

.PHONY: all install uninstall clean
