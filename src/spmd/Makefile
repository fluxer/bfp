include ../../Makefile.inc

PYUIC = pyuic4
DBSYSTEMDIR = /etc/dbus-1/system.d/
DBSERVICEDIR = /share/dbus-1/system-services/

all: bump clean
	$(PYUIC) gui.ui -o gui_ui.py
	$(NUITKA) daemon.py
	$(NUITKA) client.py
	$(NUITKA) --recurse-to=gui_ui gui.py
	$(STRIP) *.exe

cython: clean bump
	# THE GUI WILL NOT WORK!
	$(CYTHON) --embed daemon.py
	$(CYTHON) --embed client.py
	$(CYTHON) --embed gui.py
	$(CC) daemon.c $(shell pkg-config --cflags --libs $(PYTHON)) -o daemon.exe
	$(CC) client.c $(shell pkg-config --cflags --libs $(PYTHON)) -o client.exe
	$(CC) gui.c $(shell pkg-config --cflags --libs $(PYTHON)) -o gui.exe
	$(STRIP) *.exe

install:
	$(INSTALL) -dm755 $(DESTDIR)$(SBINDIR) $(DESTDIR)$(BINDIR) \
		$(DESTDIR)$(SITEDIR) $(DESTDIR)$(DBSYSTEMDIR)/ \
		$(DESTDIR)$(DBSERVICEDIR)/
	$(INSTALL) -m755 daemon.exe $(DESTDIR)$(SBINDIR)/spmd
	$(INSTALL) -m755 client.exe $(DESTDIR)$(BINDIR)/spmctl
	$(INSTALL) -m755 gui.exe $(DESTDIR)$(BINDIR)/spm-gui
	$(INSTALL) -m644 *.conf $(DESTDIR)$(DBSYSTEMDIR)/
	$(INSTALL) -m644 *.service $(DESTDIR)$(DBSERVICEDIR)/

uninstall:
	$(RM) $(DESTDIR)$(SBINDIR)/spmd
	$(RM) $(DESTDIR)$(BINDIR)/spmctl
	$(RM) $(DESTDIR)$(BINDIR)/spm-gui
	$(RM) $(DESTDIR)$(DBSYSTEMDIR)/com.spm.Daemon.conf
	$(RM) $(DESTDIR)$(DBSERVICEDIR)/com.spm.Daemon.service

clean:
	$(RM) -r *.build/ *.so *.exe __pycache__ *.c gui_ui.py
	$(RM) $(shell $(FIND) . -name '*.pyc' -o -name '*.pyo')

bump:
	$(SED) 's|^app_version.*|app_version = "$(VERSION) ($(GIT_VERSION))"|' -i client.py

.PHONY: all check install uninstall clean bump
