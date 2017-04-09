include ../Makefile.mk

install:
	$(INSTALL) -dm755 $(DESTDIR)$(BINDIR)
	$(INSTALL) -m755 snail.sh $(DESTDIR)$(BINDIR)/snail
	$(INSTALL) -m755 srcmake.sh $(DESTDIR)$(BINDIR)/srcmake

uninstall:
	$(RM) $(DESTDIR)$(BINDIR)/snail
	$(RM) $(DESTDIR)$(BINDIR)/srcmake

.PHONY: install uninstall
