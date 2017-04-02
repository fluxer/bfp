include ../../Makefile.mk

check:
	$(PYTHON) test.py

install:
	$(INSTALL) -dm755 $(DESTDIR)$(SITEDIR)
	$(INSTALL) -m644 lib*.py $(DESTDIR)$(SITEDIR)/

uninstall:
	$(RM) $(DESTDIR)$(SITEDIR)/libmessage.py*
	$(RM) $(DESTDIR)$(SITEDIR)/libmisc.py*
	$(RM) $(DESTDIR)$(SITEDIR)/libpackage.py*
	$(SED) -e 's|/bin/python2|/bin/$(PYTHON)|g' \
		-i $(DESTDIR)$(SITEDIR)/libmessage.py \
		-i $(DESTDIR)$(SITEDIR)/libmisc.py \
		-i $(DESTDIR)$(SITEDIR)/libpackage.py

clean:
	$(RM) -r __pycache__
	$(RM) $(shell $(FIND) . -name '*.pyc' -o -name '*.pyo')

.PHONY: check install uninstall clean
