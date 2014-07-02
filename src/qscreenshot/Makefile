include ../../Makefile.inc

all: clean
	$(PYUIC) qscreenshot.ui -o qscreenshot_ui.py
	$(NUITKA) --recurse-to=qscreenshot_ui main.py
	$(STRIP) main.exe

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR)
	$(INSTALL) -vm755 main.exe $(DESTDIR)$(BINDIR)/qscreenshot

uninstall:
	$(RM) $(DESTDIR)$(BINDIR)/qscreenshot

clean:
	$(RM) -r *.build/ *.exe qscreenshot_ui.py
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo')

.PHONY: all install uninstall clean
