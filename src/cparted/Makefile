include ../../Makefile.inc

all: bump clean
	$(NUITKA) main.py
	$(STRIP) main.exe

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(SBINDIR)
	$(INSTALL) -vm755 main.exe $(DESTDIR)$(SBINDIR)/cparted

uninstall:
	$(RM) $(DESTDIR)$(SBINDIR)/cparted

clean:
	$(RM) -r *.build/ *.exe
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo')

bump:
	$(SED) 's|^app_version.*|app_version = "$(VERSION) ($(GIT_VERSION))"|' -i main.py

.PHONY: all install uninstall clean bump
