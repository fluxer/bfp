include ../Makefile.inc

install:
	$(INSTALL) -dm755 $(DESTDIR)$(BINDIR)
	$(INSTALL) -m755 pkg2src.sh $(DESTDIR)$(BINDIR)/pkg2src
	$(INSTALL) -m755 snail.sh $(DESTDIR)$(BINDIR)/snail
	$(INSTALL) -m755 srcmake.sh $(DESTDIR)$(BINDIR)/srcmake

uninstall:
	$(RM) $(DESTDIR)$(BINDIR)/pkg2src
	$(RM) $(DESTDIR)$(BINDIR)/snail
	$(RM) $(DESTDIR)$(BINDIR)/srcmake

.PHONY: install uninstall
