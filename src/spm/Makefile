include ../../Makefile.inc

.py:
	$(NUITKA) $<

libspm:
	$(NUITKA) --module libspm.py

all: clean bump
	$(NUITKA) --module libspm.py
	$(NUITKA) spm.py
	$(NUITKA) tools.py
	$(STRIP) *.exe *.so

cython: clean bump
	$(CYTHON) libspm.py
	$(CYTHON) --embed spm.py
	$(CYTHON) --embed tools.py
	$(CC) -shared libspm.c $(shell pkg-config --cflags $(PYTHON)) -o libspm.so
	$(CC) spm.c $(shell pkg-config --cflags --libs $(PYTHON)) -o spm.exe
	$(CC) tools.c $(shell pkg-config --cflags --libs $(PYTHON)) -o tools.exe
	$(STRIP) *.exe *.so

install:
	$(INSTALL) -dm755 $(DESTDIR)$(SITEDIR) $(DESTDIR)$(BINDIR)
	for trans in bg; do \
		$(INSTALL) -Dm644 po/$$trans/spm.mo \
			$(DESTDIR)$(LOCALEDIR)/$$trans/LC_MESSAGES/spm.mo; \
	done
	$(INSTALL) -m644 libspm.so $(DESTDIR)$(SITEDIR)/libspm.so
	$(INSTALL) -m755 spm.exe $(DESTDIR)$(BINDIR)/spm
	$(INSTALL) -m755 tools.exe $(DESTDIR)$(BINDIR)/spm-tools

uninstall:
	$(RM) $(DESTDIR)$(SITEDIR)/libspm.so
	$(RM) $(DESTDIR)$(BINDIR)/spm
	$(RM) $(DESTDIR)$(BINDIR)/spm-tools

clean:
	$(RM) -r *.build/ *.so *.exe __pycache__ spm.pot po/*/*.mo po/*/*.mo~ *.c
	$(RM) $(shell $(FIND) . -name '*.pyc' -o -name '*.pyo')

bump:
	$(SED) 's|^app_version.*|app_version = "$(VERSION) ($(GIT_VERSION))"|' -i spm.py tools.py
	$(XGETTEXT) --language=Python -o spm.pot libspm.py spm.py tools.py
	for trans in bg; do \
		$(MSGMERGE) --update --no-fuzzy-matching po/$$trans/spm.po spm.pot; \
		$(MSGATTRIB) --no-obsolete po/$$trans/spm.po --output-file=po/$$trans/spm.po; \
		$(MSGFMT) po/$$trans/spm.po --output-file=po/$$trans/spm.mo; \
	done

.SUFFIXES: .py
.PHONY: all cython check install uninstall clean bump
