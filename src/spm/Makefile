include ../../Makefile.mk

all: clean
	$(CC) -shared libspm.c $(shell $(PYTHON)-config --includes --libs) -o libspm.so
	$(CC) spm.c $(shell $(PYTHON)-config --includes --libs) -o spm.exe
	$(CC) tools.c $(shell $(PYTHON)-config --includes --libs) -o tools.exe
	$(STRIP) *.exe *.so

sources: bump
	$(RM) *.c
	$(CYTHON) libspm.py
	$(CYTHON) --embed spm.py
	$(CYTHON) --embed tools.py

check:
	$(BASH) ./autotest.sh $(PYTHON)

install:
	$(INSTALL) -dm755 $(DESTDIR)$(SITEDIR) $(DESTDIR)$(BINDIR) \
		$(DESTDIR)/etc/spm
	for trans in bg; do \
		$(INSTALL) -Dm644 po/$$trans/spm.mo \
			$(DESTDIR)$(LOCALEDIR)/$$trans/LC_MESSAGES/spm.mo; \
	done
	$(INSTALL) -m644 libspm.so $(DESTDIR)$(SITEDIR)/libspm.so
	$(INSTALL) -m755 spm.exe $(DESTDIR)$(BINDIR)/spm
	$(INSTALL) -m755 tools.exe $(DESTDIR)$(BINDIR)/spm-tools
	$(INSTALL) -m644 etc/spm.conf $(DESTDIR)/etc/
	$(INSTALL) -m644 etc/repositories.conf $(DESTDIR)/etc/spm/
	$(INSTALL) -m644 etc/mirrors.conf $(DESTDIR)/etc/spm/
	$(INSTALL) -m644 etc/keyservers.conf $(DESTDIR)/etc/spm/
	$(SED) -e 's|@MACHINE@|$(MACHINE)|g' -e 's|@ARCH@|$(ARCH)|g' \
		-e 's|@JOBS@|$(JOBS)|g' -i $(DESTDIR)/etc/spm.conf

uninstall:
	$(RM) $(DESTDIR)$(SITEDIR)/libspm.so
	$(RM) $(DESTDIR)$(BINDIR)/spm
	$(RM) $(DESTDIR)$(BINDIR)/spm-tools
	$(RM) -r $(DESTDIR)/etc/spm/ $(DESTDIR)/etc/spm.conf

clean:
	$(RM) -r *.build/ *.so *.exe __pycache__ spm.pot po/*/*.mo po/*/*.mo~ root-*
	$(RM) $(shell $(FIND) . -name '*.pyc' -o -name '*.pyo')

bump:
	$(SED) 's|^app_version.*|app_version = "$(VERSION) ($(GIT_VERSION))"|' -i spm.py tools.py
	$(XGETTEXT) --language=Python -o spm.pot libspm.py spm.py tools.py
	for trans in bg; do \
		$(MSGMERGE) --update --no-fuzzy-matching po/$$trans/spm.po spm.pot; \
		$(MSGATTRIB) --no-obsolete po/$$trans/spm.po --output-file=po/$$trans/spm.po; \
		$(MSGFMT) po/$$trans/spm.po --output-file=po/$$trans/spm.mo; \
	done

.PHONY: all sources check install uninstall clean bump
