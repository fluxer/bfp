include ../Makefile.inc

all:
	$(MARKDOWN) about.md -f about.html
	$(MARKDOWN) copying.cparted.md -f copying.cparted.html
	$(MARKDOWN) copying.icons.md -f copying.icons.html
	$(MARKDOWN) copying.md -f copying.html
	$(MARKDOWN) license.magic.md -f license.magic.html
	$(MARKDOWN) todo.md -f todo.html

install:
	$(INSTALL) -dm755 $(DESTDIR)$(SHAREDIR)/help/
	$(INSTALL) -m644 about.html $(DESTDIR)$(SHAREDIR)/help/
	$(INSTALL) -m644 copying.cparted.html $(DESTDIR)$(SHAREDIR)/help/
	$(INSTALL) -m644 copying.icons.html $(DESTDIR)$(SHAREDIR)/help/
	$(INSTALL) -m644 copying.html $(DESTDIR)$(SHAREDIR)/help/
	$(INSTALL) -m644 license.magic.html $(DESTDIR)$(SHAREDIR)/help/
	$(INSTALL) -m644 todo.html $(DESTDIR)$(SHAREDIR)/help/

uninstall:
	$(RM) -r $(DESTDIR)$(SHAREDIR)/help/

clean:
	$(RM) *.html

.PHONY: all install uninstall clean
