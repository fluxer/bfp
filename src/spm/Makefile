include ../../Makefile.inc

all: bump clean
	$(PYUIC) gui.ui -o gui_ui.py
	$(NUITKA) --module libspm.py
	$(NUITKA) spm.py
	$(NUITKA) tools.py
	$(NUITKA) --recurse-to=gui_ui gui.py
	$(STRIP) *.exe *.so

install:
	$(INSTALL) -dm755 $(DESTDIR)$(BINDIR) $(DESTDIR)$(SITEDIR)
	$(INSTALL) -m755 spm.exe $(DESTDIR)$(BINDIR)/spm
	$(INSTALL) -m755 tools.exe $(DESTDIR)$(BINDIR)/spm-tools
	$(INSTALL) -m755 gui.exe $(DESTDIR)$(BINDIR)/spm-gui
	$(INSTALL) -m644 libspm.so $(DESTDIR)$(SITEDIR)/libspm.so

uninstall:
	$(RM) $(DESTDIR)$(SITEDIR)/libspm.so
	$(RM) $(DESTDIR)$(BINDIR)/spm
	$(RM) $(DESTDIR)$(BINDIR)/spm-tools
	$(RM) $(DESTDIR)$(BINDIR)/spm-gui

clean:
	$(RM) -r *.build/ *.so *.exe gui_ui.py __pycache__
	$(RM) $(shell $(FIND) . -name '*.pyc' -o -name '*.pyo')

bump:
	$(SED) 's|^app_version.*|app_version = "$(VERSION) ($(GIT_VERSION))"|' -i spm.py tools.py

.PHONY: all check install uninstall clean bump
