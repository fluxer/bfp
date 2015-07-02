include ../../Makefile.mk

all: clean bump
	$(SED) -e 's|@BINDIR@|$(BINDIR)|' -e 's|@VERSION@|$(VERSION)|' \
		spm-gui.desktop.in > spm-gui.desktop
	$(SED) -e 's|@BINDIR@|$(BINDIR)|' -e 's|@VERSION@|$(VERSION)|' \
		spm-autostart.desktop.in > spm-autostart.desktop
	$(SED) -e 's|@SBINDIR@|$(SBINDIR)|' \
		com.spm.Daemon.service.in > com.spm.Daemon.service
	$(PYUIC) gui.ui -o gui_ui.py
	# REQUIRES INSTALLED LIBS!
	$(PYTHON) ../cold/cold.py ./gui.py ./gui_ui.py -o ./gui.exe

clean:
	$(RM) -r *.build/ *.so *.exe __pycache__ *_ui.py *.desktop *.service
	$(RM) $(shell $(FIND) . -name '*.pyc' -o -name '*.pyo')

install:
	$(INSTALL) -dm755 $(DESTDIR)$(SBINDIR) $(DESTDIR)$(BINDIR) \
		$(DESTDIR)$(DBSYSTEMDIR)/ $(DESTDIR)$(DBSERVICEDIR)/ \
		$(DESTDIR)$(APPLICATIONSDIR)/ $(DESTDIR)$(AUTOSTARTDIR)/ \
		$(DESTDIR)$(INITDIR)/
	$(INSTALL) -m755 daemon.py $(DESTDIR)$(SBINDIR)/spmd
	$(INSTALL) -m755 client.py $(DESTDIR)$(BINDIR)/spmctl
	$(INSTALL) -m755 gui.exe $(DESTDIR)$(BINDIR)/spm-gui
	$(INSTALL) -m644 *.conf $(DESTDIR)$(DBSYSTEMDIR)/
	$(INSTALL) -m644 *.service $(DESTDIR)$(DBSERVICEDIR)/
	$(INSTALL) -m644 spm-gui.desktop $(DESTDIR)$(APPLICATIONSDIR)/
	$(INSTALL) -m644 spm-autostart.desktop $(DESTDIR)$(AUTOSTARTDIR)/
	$(INSTALL) -m744 spmd.init $(DESTDIR)$(INITDIR)/spmd

uninstall:
	$(RM) $(DESTDIR)$(SBINDIR)/spmd
	$(RM) $(DESTDIR)$(BINDIR)/spmctl
	$(RM) $(DESTDIR)$(BINDIR)/spm-gui
	$(RM) $(DESTDIR)$(DBSYSTEMDIR)/com.spm.Daemon.conf
	$(RM) $(DESTDIR)$(DBSERVICEDIR)/com.spm.Daemon.service
	$(RM) $(DESTDIR)$(APPLICATIONSDIR)/spm-gui.desktop
	$(RM) $(DESTDIR)$(AUTOSTARTDIR)/spm-autostart.desktop
	$(RM) $(DESTDIR)$(INITDIR)/ahws

bump:
	$(SED) 's|^app_version.*|app_version = "$(VERSION) ($(GIT_VERSION))"|' -i client.py

.PHONY: all cython check install uninstall clean bump
