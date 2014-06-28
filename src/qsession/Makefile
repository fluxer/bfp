include ../../Makefile.inc

all: clean
	$(PYUIC) qsession.ui -o qsession_ui.py
	$(NUITKA) --recurse-to=qsession_ui main.py
	$(STRIP) main.exe

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(SBINDIR)
	$(INSTALL) -vm755 main.exe $(DESTDIR)$(SBINDIR)/qsession

uninstall:
	$(RM) $(DESTDIR)$(BINDIR)/qsession

clean:
	$(RM) -r *.build/ *.exe qsession_ui.py
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo')

.PHONY: all install uninstall clean
