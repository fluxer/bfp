include ../../Makefile.inc

all: bump clean
	$(PYUIC) qimage.ui -o qimage_ui.py
	$(NUITKA) --recurse-to=qimage_ui main.py
	$(STRIP) main.exe

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR)
	$(INSTALL) -vm755 main.exe $(DESTDIR)$(BINDIR)/qimage

uninstall:
	$(RM) $(DESTDIR)$(BINDIR)/qimage

clean:
	$(RM) -r *.build/ *.exe qimage_ui.py
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo')

bump:
	$(SED) 's|^app_version.*|app_version = "$(VERSION) ($(GIT_VERSION))"|' -i main.py

.PHONY: all install uninstall clean bump
