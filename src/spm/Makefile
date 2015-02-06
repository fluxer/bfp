include ../../Makefile.inc

all: bump clean
	$(XGETTEXT) --language=Python -o spm.pot libspm.py spm.py tools.py
	for trans in bg; do \
		$(MSGMERGE) --update --no-fuzzy-matching po/$$trans/spm.po spm.pot; \
		$(MSGATTRIB) --no-obsolete po/$$trans/spm.po --output-file=po/$$trans/spm.po; \
		$(MSGFMT) po/$$trans/spm.po --output-file=po/$$trans/spm.mo; \
	done
	$(PYUIC) gui.ui -o gui_ui.py
	$(NUITKA) --module libspm.py
	$(NUITKA) spm.py
	$(NUITKA) tools.py
	$(NUITKA) --recurse-to=gui_ui gui.py
	$(STRIP) *.exe *.so

install:
	$(INSTALL) -dm755 $(DESTDIR)$(SITEDIR) $(DESTDIR)$(BINDIR) \
		$(DESTDIR)$(LOCALEDIR)/
	for trans in bg; do \
		$(INSTALL) -mD644 po/$$trans/spm.mo \
			$(DESTDIR)$(LOCALEDIR)/$$trans/LC_MESSAGES/spm.mo; \
	done
	$(INSTALL) -m644 libspm.so $(DESTDIR)$(SITEDIR)/libspm.so
	$(INSTALL) -m755 spm.exe $(DESTDIR)$(BINDIR)/spm
	$(INSTALL) -m755 tools.exe $(DESTDIR)$(BINDIR)/spm-tools
	$(INSTALL) -m755 gui.exe $(DESTDIR)$(BINDIR)/spm-gui


uninstall:
	$(RM) $(DESTDIR)$(SITEDIR)/libspm.so
	$(RM) $(DESTDIR)$(BINDIR)/spm
	$(RM) $(DESTDIR)$(BINDIR)/spm-tools
	$(RM) $(DESTDIR)$(BINDIR)/spm-gui

clean:
	$(RM) -r *.build/ *.so *.exe gui_ui.py __pycache__ spm.pot po/*/*.mo po/*/*.mo~
	$(RM) $(shell $(FIND) . -name '*.pyc' -o -name '*.pyo')

bump:
	$(SED) 's|^app_version.*|app_version = "$(VERSION) ($(GIT_VERSION))"|' -i spm.py tools.py

.PHONY: all check install uninstall clean bump
