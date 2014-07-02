include ../../Makefile.inc

all: bump clean
	$(PYUIC) qedit.ui -o qedit_ui.py
	$(NUITKA) --recurse-to=qedit_ui,libhighlighter main.py
	$(STRIP) main.exe

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR)
	$(INSTALL) -vm755 main.exe $(DESTDIR)$(BINDIR)/qedit

uninstall:
	$(RM) $(DESTDIR)$(BINDIR)/qedit

clean:
	$(RM) -r *.build/ *.exe qedit_ui.py
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo')

bump:
	$(SED) 's|^app_version.*|app_version = "$(VERSION) ($(GIT_VERSION))"|' -i main.py

.PHONY: all install uninstall clean bump
