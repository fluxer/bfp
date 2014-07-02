include ../../Makefile.inc

all: bump clean
	$(PYUIC) qbrowse.ui -o qbrowse_ui.py
	$(NUITKA) --recurse-to=qbrowse_ui main.py
	$(STRIP) main.exe

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR)
	$(INSTALL) -vm755 main.exe $(DESTDIR)$(BINDIR)/qbrowse

uninstall:
	$(RM) $(DESTDIR)$(BINDIR)/qbrowse

clean:
	$(RM) -r *.build/ *.exe qbrowse_ui.py
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo')

bump:
	$(SED) 's|^app_version.*|app_version = "$(VERSION) ($(GIT_VERSION))"|' -i main.py

.PHONY: all install uninstall clean bump
