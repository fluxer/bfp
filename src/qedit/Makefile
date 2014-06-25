include ../../Makefile.inc

all: clean
	$(PYUIC) qedit.ui -o qedit_ui.py
	$(NUITKA) --recurse-to=qedit_ui main.py
	$(STRIP) main.exe

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR)
	$(INSTALL) -vm755 main.exe $(DESTDIR)$(BINDIR)/qedit

uninstall:
	$(RM) $(DESTDIR)$(BINDIR)/qedit

clean:
	$(RM) -r *.build/ *.exe qedit_ui.py
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo')

.PHONY: all install uninstall clean
