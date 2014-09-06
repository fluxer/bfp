include ../../Makefile.inc

all: clean
	$(PYUIC) qsession.ui -o qsession_ui.py
	$(NUITKA) --recurse-to=qsession_ui main.py
	$(STRIP) *.exe

install:
	$(INSTALL) -dm755 $(DESTDIR)$(SBINDIR)
	$(INSTALL) -m755 main.exe $(DESTDIR)$(SBINDIR)/qsession

uninstall:
	$(RM) $(DESTDIR)$(SBINDIR)/qsession

clean:
	$(RM) -r *.build/ *.exe qsession_ui.py
	$(RM) $(shell $(FIND) . -name '*.pyc' -o -name '*.pyo')

.PHONY: all install uninstall clean
