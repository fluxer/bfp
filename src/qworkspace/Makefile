include ../../Makefile.inc

all: clean
	$(SED) 's|^app_version.*|app_version = "$(VERSION) ($(GIT_VERSION))"|' -i main.py
	$(SED) 's|self.version = .*|self.version = "$(VERSION) ($(GIT_VERSION))"|' -i plugins/*.py
	$(PYUIC) qworkspace.ui -o qworkspace_ui.py
	$(PYLUPDATE) main.py plugins/*.py qworkspace_ui.py \
		-ts tr/qworkspace_bg_BG.ts
	$(LRELEASE) tr/qworkspace_bg_BG.ts
	$(NUITKA) --recurse-to=qworkspace_ui main.py
	$(NUITKA) --module plugins/archive.py
	$(NUITKA) --module plugins/calendar.py
	$(NUITKA) --module plugins/download.py
	$(NUITKA) --module plugins/editor.py
	$(NUITKA) --module plugins/help.py
	$(NUITKA) --module plugins/image.py
	$(NUITKA) --module plugins/mail.py
	$(NUITKA) --module plugins/mixer.py
	$(NUITKA) --module plugins/multimedia.py
	$(NUITKA) --module plugins/network.py
	$(NUITKA) --module plugins/package.py
	$(NUITKA) --module plugins/pdf.py
	$(NUITKA) --module plugins/plugins.py
	$(NUITKA) --module plugins/quit.py
	$(NUITKA) --module plugins/screenshot.py
	$(NUITKA) --module plugins/server.py
	$(NUITKA) --module plugins/settings.py
	$(NUITKA) --module plugins/storage.py
	$(NUITKA) --module plugins/terminal.py
	$(NUITKA) --module plugins/tetrix.py
	$(NUITKA) --module plugins/www.py
	$(STRIP) main.exe archive.so calendar.so download.so editor.so \
		help.so image.so mail.so mixer.so multimedia.so network.so \
		package.so pdf.so plugins.so quit.so screenshot.so server.so \
		settings.so storage.so terminal.so tetrix.so www.so

check:
	$(PYUIC) qworkspace.ui -o qworkspace_ui.py
	$(PYTHON) test.py

install:
	$(INSTALL) -dm755 $(DESTDIR)$(BINDIR)
	$(INSTALL) -dm755 $(DESTDIR)/etc/qworkspace/plugins
	$(INSTALL) -dm755 $(DESTDIR)$(TRDIR)/
	$(INSTALL) -m755 main.exe $(DESTDIR)$(BINDIR)/qworkspace
	$(INSTALL) -m644 *.so $(DESTDIR)/etc/qworkspace/plugins/
	$(INSTALL) -m644 tr/*.qm $(DESTDIR)$(TRDIR)/

uninstall:
	$(RM) $(DESTDIR)$(BINDIR)/qworkspace
	$(RM) -r $(DESTDIR)/etc/qworkspace
	$(RM) $(DESTDIR)$(TRDIR)/qworkspace_*.qm

clean:
	$(RM) -r *.build/ *.so *.exe qworkspace_ui.py tr/*.qm
	$(RM) $(shell $(FIND) . -name '*.pyc' -o -name '*.pyo')

.PHONY: all install uninstall clean
