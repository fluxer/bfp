include ../../Makefile.inc

all: bump clean
	$(NUITKA) --module libspm.py
	$(NUITKA) spm.py
	$(NUITKA) tools.py
	$(STRIP) libspm.so spm.exe tools.exe

install:
	$(INSTALL) -dm755 $(DESTDIR)$(SBINDIR) $(DESTDIR)$(SITEDIR)
	$(INSTALL) -m755 spm.exe $(DESTDIR)$(SBINDIR)/spm
	$(INSTALL) -m755 tools.exe $(DESTDIR)$(SBINDIR)/spm-tools
	$(INSTALL) -m644 libspm.so $(DESTDIR)$(SITEDIR)/libspm.so

uninstall:
	$(RM) $(DESTDIR)$(SITEDIR)/libspm.so
	$(RM) $(DESTDIR)$(SBINDIR)/spm
	$(RM) $(DESTDIR)$(SBINDIR)/spm-tools

clean:
	$(RM) -r *.build/ *.so *.exe
	$(RM) $(shell $(FIND) . -name '*.pyc' -o -name '*.pyo')

bump:
	$(SED) 's|^app_version.*|app_version = "$(VERSION) ($(GIT_VERSION))"|' -i spm.py tools.py

.PHONY: all check install uninstall clean bump
