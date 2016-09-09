include ../../Makefile.mk

all: clean bump
	$(CC) -shared libspm.c $(shell $(PYTHON)-config --includes --libs) $(CFLAGS) -o libspm.so
	$(CC) spm.c $(shell $(PYTHON)-config --includes --libs)  $(CFLAGS) -o spm.exe
	$(CC) tools.c $(shell $(PYTHON)-config --includes --libs)  $(CFLAGS) -o tools.exe
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
	$(RM) -r *.build/ *.so *.exe __pycache__ root-*
	$(RM) $(shell $(FIND) . -name '*.pyc' -o -name '*.pyo')

bump:
	$(SED) 's|^app_version.*|app_version = "$(VERSION) ($(GIT_VERSION))"|' -i spm.py tools.py

.PHONY: all sources check install uninstall clean bump
