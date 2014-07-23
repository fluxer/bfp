include ../../Makefile.inc

all: bump clean
	$(PYUIC) qworkspace.ui -o qworkspace_ui.py
	$(NUITKA) --recurse-to=qworkspace_ui main.py
	$(NUITKA) --module plugins/editor.py
	$(NUITKA) --module plugins/image.py
	$(NUITKA) --module plugins/multimedia.py
	$(NUITKA) --module plugins/quit.py
	$(NUITKA) --module plugins/screenshot.py
	$(NUITKA) --module plugins/storage.py
	$(NUITKA) --module plugins/terminal.py
	$(NUITKA) --module plugins/www.py
	$(STRIP) main.exe editor.so image.so multimedia.so quit.so screenshot.so \
		storage.so terminal.so www.so

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR)
	$(INSTALL) -vdm755 $(DESTDIR)$(ETCDIR)/qworkspace/plugins
	$(INSTALL) -vm755 main.exe $(DESTDIR)$(BINDIR)/qworkspace
	$(INSTALL) -vm644 editor.so $(DESTDIR)$(ETCDIR)/qworkspace/plugins
	$(INSTALL) -vm644 image.so $(DESTDIR)$(ETCDIR)/qworkspace/plugins
	$(INSTALL) -vm644 multimedia.so $(DESTDIR)$(ETCDIR)/qworkspace/plugins
	$(INSTALL) -vm644 quit.so $(DESTDIR)$(ETCDIR)/qworkspace/plugins
	$(INSTALL) -vm644 screenshot.so $(DESTDIR)$(ETCDIR)/qworkspace/plugins
	$(INSTALL) -vm644 storage.so $(DESTDIR)$(ETCDIR)/qworkspace/plugins
	$(INSTALL) -vm644 terminal.so $(DESTDIR)$(ETCDIR)/qworkspace/plugins
	$(INSTALL) -vm644 www.so $(DESTDIR)$(ETCDIR)/qworkspace/plugins

uninstall:
	$(RM) $(DESTDIR)$(BINDIR)/qworkspace
	$(RM) -r $(DESTDIR)$(ETCDIR)/qworkspace

clean:
	$(RM) -r *.build/ *.so *.exe qworkspace_ui.py
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo')

bump:
	$(SED) 's|^app_version.*|app_version = "$(VERSION) ($(GIT_VERSION))"|' -i main.py

.PHONY: all install uninstall clean bump
