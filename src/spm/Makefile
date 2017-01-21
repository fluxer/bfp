include ../../Makefile.mk

all:
	$(SED) 's|^app_version.*|app_version = "$(VERSION) ($(GIT_VERSION))"|' -i spm.py tools.py

check:
	$(BASH) ./autotest.sh $(PYTHON)

install:
	$(INSTALL) -dm755 $(DESTDIR)$(SITEDIR) $(DESTDIR)$(BINDIR) \
		$(DESTDIR)/etc/spm
	$(INSTALL) -m644 libspm.py $(DESTDIR)$(SITEDIR)/libspm.py
	$(INSTALL) -m755 spm.py $(DESTDIR)$(BINDIR)/spm
	$(INSTALL) -m755 tools.py $(DESTDIR)$(BINDIR)/spm-tools
	$(INSTALL) -m644 etc/spm.conf $(DESTDIR)/etc/
	$(INSTALL) -m644 etc/repositories.conf $(DESTDIR)/etc/spm/
	$(INSTALL) -m644 etc/mirrors.conf $(DESTDIR)/etc/spm/
	$(INSTALL) -m644 etc/keyservers.conf $(DESTDIR)/etc/spm/
	$(SED) -e 's|@MACHINE@|$(MACHINE)|g' -e 's|@ARCH@|$(ARCH)|g' \
		-e 's|@JOBS@|$(JOBS)|g' -i $(DESTDIR)/etc/spm.conf

uninstall:
	$(RM) $(DESTDIR)$(SITEDIR)/libspm.py
	$(RM) $(DESTDIR)$(BINDIR)/spm
	$(RM) $(DESTDIR)$(BINDIR)/spm-tools
	$(RM) -r $(DESTDIR)/etc/spm/ $(DESTDIR)/etc/spm.conf

clean:
	$(RM) -r __pycache__ root-*
	$(RM) $(shell $(FIND) . -name '*.pyc' -o -name '*.pyo')

.PHONY: all check install uninstall clean
