include ../../Makefile.inc

all: bump clean
	$(NUITKA) main.py
	$(STRIP) *.exe

install:
	$(INSTALL) -dm755 $(DESTDIR)$(SBINDIR)
	$(INSTALL) -m755 main.exe $(DESTDIR)$(SBINDIR)/cparted

uninstall:
	$(RM) $(DESTDIR)$(SBINDIR)/cparted

clean:
	$(RM) -r *.build/ *.exe __pycache__
	$(RM) $(shell $(FIND) . -name '*.pyc' -o -name '*.pyo')

bump:
	$(SED) 's|^app_version.*|app_version = "$(VERSION) ($(GIT_VERSION))"|' -i main.py

.PHONY: all install uninstall clean bump
