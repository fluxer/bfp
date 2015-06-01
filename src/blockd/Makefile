include ../../Makefile.inc

all: bump clean
	$(NUITKA) daemon.py
	$(NUITKA) client.py
	$(STRIP) *.exe

cython: clean bump
	$(CYTHON) --embed daemon.py
	$(CYTHON) --embed client.py
	$(CC) daemon.c $(shell $(PYTHON)-config --includes --libs) -o daemon.exe
	$(CC) client.c $(shell $(PYTHON)-config --includes --libs) -o client.exe
	$(STRIP) *.exe

install:
	$(INSTALL) -dm755 $(DESTDIR)$(SBINDIR) $(DESTDIR)$(BINDIR) \
		$(DESTDIR)$(DBSYSTEMDIR)/ $(DESTDIR)$(DBSERVICEDIR)/
	$(INSTALL) -m755 daemon.exe $(DESTDIR)$(SBINDIR)/blockd
	$(INSTALL) -m755 client.exe $(DESTDIR)$(SBINDIR)/blockctl
	$(INSTALL) -m644 *.conf $(DESTDIR)$(DBSYSTEMDIR)/
	$(INSTALL) -m644 *.service $(DESTDIR)$(DBSERVICEDIR)/

uninstall:
	$(RM) $(DESTDIR)$(SBINDIR)/blockd
	$(RM) $(DESTDIR)$(BINDIR)/blockctl
	$(RM) $(DESTDIR)$(DBSYSTEMDIR)/blockd.conf
	$(RM) $(DESTDIR)$(DBSERVICEDIR)/blockd.service

clean:
	$(RM) -r *.build/ *.so *.exe __pycache__
	$(RM) $(shell $(FIND) . -name '*.pyc' -o -name '*.pyo')

bump:
	$(SED) 's|^app_version.*|app_version = "$(VERSION) ($(GIT_VERSION))"|' -i client.py

.SUFFIXES: .py
.PHONY: all cython install uninstall clean bump
