include ../../Makefile.inc

PYUIC = pyuic4
DBSYSTEMDIR = /etc/dbus-1/system.d/
DBSERVICEDIR = $(SHAREDIR)/dbus-1/system-services/
APPLICATIONSDIR = $(SHAREDIR)/applications
AUTOSTARTDIR = /etc/xdg/autostart

all: bump clean
	$(SED) -e 's|@BINDIR@|$(BINDIR)|' -e 's|@VERSION@|$(VERSION)|' \
		spm-gui.desktop.in > spm-gui.desktop
	$(SED) -e 's|@BINDIR@|$(BINDIR)|' -e 's|@VERSION@|$(VERSION)|' \
		spm-autostart.desktop.in > spm-autostart.desktop
	$(PYUIC) gui.ui -o gui_ui.py
	# THE GUI WILL NOT WORK!
	$(NUITKA) daemon.py
	$(NUITKA) client.py
	$(NUITKA) --recurse-to=gui_ui gui.py
	$(STRIP) *.exe

cython: clean bump
	$(SED) -e 's|@BINDIR@|$(BINDIR)|' -e 's|@VERSION@|$(VERSION)|' \
		spm-gui.desktop.in > spm-gui.desktop
	$(SED) -e 's|@BINDIR@|$(BINDIR)|' -e 's|@VERSION@|$(VERSION)|' \
		spm-autostart.desktop.in > spm-autostart.desktop
	$(PYUIC) gui.ui -o gui_ui.py
	# THE GUI WILL NOT WORK!
	$(CYTHON) --embed daemon.py
	$(CYTHON) --embed client.py
	$(CYTHON) --embed gui.py
	$(CC) daemon.c $(shell pkg-config --cflags --libs $(PYTHON)) -o daemon.exe
	$(CC) client.c $(shell pkg-config --cflags --libs $(PYTHON)) -o client.exe
	$(CC) gui.c $(shell pkg-config --cflags --libs $(PYTHON)) -o gui.exe
	$(STRIP) *.exe

cold: clean bump
	$(SED) -e 's|@BINDIR@|$(BINDIR)|' -e 's|@VERSION@|$(VERSION)|' \
		spm-gui.desktop.in > spm-gui.desktop
	$(SED) -e 's|@BINDIR@|$(BINDIR)|' -e 's|@VERSION@|$(VERSION)|' \
		spm-autostart.desktop.in > spm-autostart.desktop
	$(PYUIC) gui.ui -o gui_ui.py
	$(NUITKA) daemon.py
	$(NUITKA) client.py
	$(STRIP) *.exe
	# REQUIRES INSTALLED LIBS!
	../cold/cold.py gui.py gui_ui.py -o ./spm-gui.exe

install:
	$(INSTALL) -dm755 $(DESTDIR)$(SBINDIR) $(DESTDIR)$(BINDIR) \
		$(DESTDIR)$(DBSYSTEMDIR)/ $(DESTDIR)$(DBSERVICEDIR)/ \
		$(DESTDIR)$(APPLICATIONSDIR)/ $(DESTDIR)$(AUTOSTARTDIR)/
	$(INSTALL) -m755 daemon.exe $(DESTDIR)$(SBINDIR)/spmd
	$(INSTALL) -m755 client.exe $(DESTDIR)$(BINDIR)/spmctl
	$(INSTALL) -m755 gui.exe $(DESTDIR)$(BINDIR)/spm-gui
	$(INSTALL) -m644 *.conf $(DESTDIR)$(DBSYSTEMDIR)/
	$(INSTALL) -m644 *.service $(DESTDIR)$(DBSERVICEDIR)/
	$(INSTALL) -m644 spm-gui.desktop $(DESTDIR)$(APPLICATIONSDIR)/
	$(INSTALL) -m644 spm-autostart.desktop $(DESTDIR)$(AUTOSTARTDIR)/

uninstall:
	$(RM) $(DESTDIR)$(SBINDIR)/spmd
	$(RM) $(DESTDIR)$(BINDIR)/spmctl
	$(RM) $(DESTDIR)$(BINDIR)/spm-gui
	$(RM) $(DESTDIR)$(DBSYSTEMDIR)/com.spm.Daemon.conf
	$(RM) $(DESTDIR)$(DBSERVICEDIR)/com.spm.Daemon.service
	$(RM) $(DESTDIR)$(APPLICATIONSDIR)/spm-gui.desktop
	$(RM) $(DESTDIR)$(AUTOSTARTDIR)/spm-autostart.desktop

clean:
	$(RM) -r *.build/ *.so *.exe __pycache__ *.c gui_ui.py
	$(RM) $(shell $(FIND) . -name '*.pyc' -o -name '*.pyo')

bump:
	$(SED) 's|^app_version.*|app_version = "$(VERSION) ($(GIT_VERSION))"|' -i client.py

.PHONY: all check install uninstall clean bump
