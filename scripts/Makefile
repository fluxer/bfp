include ../Makefile.inc

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR)
	$(INSTALL) -vm755 pkg2src.sh $(DESTDIR)$(BINDIR)/pkg2src
	$(INSTALL) -vm755 snail.sh $(DESTDIR)$(BINDIR)/snail
	$(INSTALL) -vm755 srcmake.sh $(DESTDIR)$(BINDIR)/srcmake

uninstall:
	$(RM) $(DESTDIR)$(BINDIR)/pkg2src
	$(RM) $(DESTDIR)$(BINDIR)/snail
	$(RM) $(DESTDIR)$(BINDIR)/srcmake
