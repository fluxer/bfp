include ../../Makefile.inc

all: bump clean
	$(NUITKA) --module libspm.py
	$(NUITKA) spm.py
	$(NUITKA) tools.py
	$(STRIP) libspm.so spm.exe tools.exe

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(SBINDIR)
	$(INSTALL) -vm755 spm.exe $(DESTDIR)$(SBINDIR)/spm
	$(INSTALL) -vm755 tools.exe $(DESTDIR)$(SBINDIR)/spm-tools
	$(INSTALL) -vm644 libspm.so $(DESTDIR)$(SITEDIR)/libspm.so

uninstall:
	$(RM) $(DESTDIR)$(SITEDIR)/libspm.so
	$(RM) $(DESTDIR)$(SBINDIR)/spm
	$(RM) $(DESTDIR)$(SBINDIR)/spm-tools

clean:
	$(RM) -r *.build/ *.so *.exe
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo')

bump:
	$(SED) 's|^app_version.*|app_version = "$(VERSION) ($(GIT_VERSION))"|' -i spm.py tools.py

.PHONY: all check install uninstall clean bump
