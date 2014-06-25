include ../../Makefile.inc

all: clean
	$(PYUIC) qsettings.ui -o qsettings_ui.py
	$(NUITKA) --recurse-to=libqdesktop --recurse-to=qsettings_ui main.py
	$(STRIP) main.exe

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR)
	$(INSTALL) -vm755 main.exe $(DESTDIR)$(BINDIR)/qsettings

uninstall:
	$(RM) $(DESTDIR)$(BINDIR)/qsettings

clean:
	$(RM) -r *.build/ *.exe qsettings_ui.py
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo')

.PHONY: all install uninstall clean
