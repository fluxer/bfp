include ../../Makefile.inc

all: clean bump
	$(NUITKA) ahws.py
	$(STRIP) *.exe

cython: clean bump
	$(CYTHON) --embed ahws.py
	$(CC) ahws.c $(shell $(PYTHON)-config --includes --libs $(PYTHON)) -o ahws.exe
	$(STRIP) *.exe

install:
	$(INSTALL) -dm755 $(DESTDIR)$(SBINDIR) $(DESTDIR)/etc/
	$(INSTALL) -m755 ahws.exe $(DESTDIR)$(SBINDIR)/ahws
	$(CP) -r ahws.d/ $(DESTDIR)/etc/

uninstall:
	$(RM) $(DESTDIR)$(SBINDIR)/ahws
	$(RM) $(DESTDIR)/etc/ahws.d

clean:
	$(RM) -r *.build/ *.so *.exe __pycache__
	$(RM) $(shell $(FIND) . -name '*.pyc' -o -name '*.pyo')

bump:
	$(SED) 's|^app_version.*|app_version = "$(VERSION) ($(GIT_VERSION))"|' -i ahws.py
.PHONY: all cython install uninstall clean
