include ../Makefile.inc

all:
	$(MARKDOWN) copying.md -f copying.html
	$(MARKDOWN) todo.md -f todo.html

install:
	$(INSTALL) -dm755 $(DESTDIR)$(SHAREDIR)/help/
	$(INSTALL) -m644 copying.html $(DESTDIR)$(SHAREDIR)/help/
	$(INSTALL) -m644 todo.html $(DESTDIR)$(SHAREDIR)/help/

uninstall:
	$(RM) -r $(DESTDIR)$(SHAREDIR)/help/

clean:
	$(RM) *.html

.PHONY: all install uninstall clean
