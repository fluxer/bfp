include ../../Makefile.inc

all: bump clean
	$(PYUIC) spmqt.ui -o spmqt_ui.py
	$(NUITKA) --recurse-to=spmqt_ui main.py
	$(STRIP) main.exe

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(SBINDIR)
	$(INSTALL) -vm755 main.exe $(DESTDIR)$(SBINDIR)/spm-qt

uninstall:
	$(RM) $(DESTDIR)$(SBINDIR)/spm-qt

clean:
	$(RM) -r *.build *.exe spmqt_ui.py
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo')

bump:
	$(SED) 's|^app_version.*|app_version = "$(VERSION) ($(GIT_VERSION))"|' -i main.py

.PHONY: all install uninstall clean bump
