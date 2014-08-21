include ../Makefile.inc

install:
	$(INSTALL) -dm755 $(DESTDIR)$(SHAREDIR)/icons/tiny
	$(CP) -r actions $(DESTDIR)$(SHAREDIR)/icons/tiny/
	$(CP) -r apps $(DESTDIR)$(SHAREDIR)/icons/tiny/
	$(CP) -r categories $(DESTDIR)$(SHAREDIR)/icons/tiny/
	$(CP) -r devices $(DESTDIR)$(SHAREDIR)/icons/tiny/
	$(CP) -r emblems $(DESTDIR)$(SHAREDIR)/icons/tiny/
	$(CP) -r emotes $(DESTDIR)$(SHAREDIR)/icons/tiny/
	$(CP) -r extra $(DESTDIR)$(SHAREDIR)/icons/tiny/
	$(CP) -r mimes $(DESTDIR)$(SHAREDIR)/icons/tiny/
	$(CP) -r places $(DESTDIR)$(SHAREDIR)/icons/tiny/
	$(CP) -r status $(DESTDIR)$(SHAREDIR)/icons/tiny/
	$(CP) -r symbolic $(DESTDIR)$(SHAREDIR)/icons/tiny/
	$(CP) -r tools $(DESTDIR)$(SHAREDIR)/icons/tiny/

uninstall:
	$(RM) -r $(DESTDIR)$(SHAREDIR)/icons/tiny

.PHONY: install uninstall
