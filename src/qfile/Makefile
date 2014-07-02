include ../../Makefile.inc

all: bump clean
	$(PYUIC) qfile.ui -o qfile_ui.py
	$(NUITKA) --recurse-to=qfile_ui main.py
	$(STRIP) main.exe

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR)
	$(INSTALL) -vm755 main.exe $(DESTDIR)$(BINDIR)/qfile

uninstall:
	$(RM) $(DESTDIR)$(BINDIR)/qfile

clean:
	$(RM) -r *.build/ *.exe qfile_ui.py
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo')

bump:
	$(SED) 's|^app_version.*|app_version = "$(VERSION) ($(GIT_VERSION))"|' -i main.py

.PHONY: all install uninstall clean bump
