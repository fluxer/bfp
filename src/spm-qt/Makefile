include ../../Makefile.inc

all: bump clean
	$(PYUIC) spmqt.ui -o spmqt_ui.py
	$(NUITKA) --recurse-to=spmqt_ui qt.py
	$(STRIP) qt.exe

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(SBINDIR)
	$(INSTALL) -vm755 qt.exe $(DESTDIR)$(SBINDIR)/spm-qt

uninstall:
	$(RM) $(DESTDIR)$(BINDIR)/spm-qt

clean:
	$(RM) -r *.build *.exe spmqt_ui.py
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo')

bump:
	sed 's|^app_version.*|app_version = "$(VERSION) ($(GIT_VERSION))"|' -i qt.py

.PHONY: all install uninstall clean bump
