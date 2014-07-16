include ../../Makefile.inc

all: bump clean
	$(PYUIC) qworkspace.ui -o qworkspace_ui.py
	$(NUITKA) --recurse-to=qworkspace_ui main.py
	$(STRIP) main.exe

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR)
	$(INSTALL) -vm755 main.exe $(DESTDIR)$(BINDIR)/qworkspace

uninstall:
	$(RM) $(DESTDIR)$(BINDIR)/qworkspace

clean:
	$(RM) -r *.build/ *.exe qworkspace_ui.py
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo')

bump:
	$(SED) 's|^app_version.*|app_version = "$(VERSION) ($(GIT_VERSION))"|' -i main.py

.PHONY: all install uninstall clean bump
