include ../../Makefile.inc

all: clean
	$(PYUIC) qnetwork.ui -o qnetwork_ui.py
	$(NUITKA) --recurse-to=libdesktop --recurse-to=qnetwork_ui main.py
	$(STRIP) main.exe

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR)
	$(INSTALL) -vm755 main.exe $(DESTDIR)$(BINDIR)/qnetwork

uninstall:
	$(RM) $(DESTDIR)$(BINDIR)/qnetwork

clean:
	$(RM) -r *.build/ *.exe qnetwork_ui.py
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo')

.PHONY: all install uninstall clean
