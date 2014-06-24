include ../Makefile.inc

install:
	$(INSTALL) -vdm755 $(DESTDIR)/etc/spm
	$(INSTALL) -vdm755 $(DESTDIR)$(AUTOSTARTDIR)
	$(INSTALL) -vdm755 $(DESTDIR)$(APPLICATIONSDIR)
	$(INSTALL) -vdm755 $(DESTDIR)$(MENUSDIR)
	$(INSTALL) -vm644 spm.conf $(DESTDIR)/etc/
	$(INSTALL) -vm644 repositories.conf $(DESTDIR)/etc/spm/
	$(INSTALL) -vm644 mirrors.conf $(DESTDIR)/etc/spm/
	sed 's|#MACHINE#|$(MACHINE)|g' -i $(DESTDIR)/etc/spm.conf
	sed 's|#ARCH#|$(ARCH)|g' -i $(DESTDIR)/etc/spm.conf
	sed 's|#JOBS#|$(JOBS)|g' -i $(DESTDIR)/etc/spm.conf
	$(INSTALL) -vm644 system.conf $(DESTDIR)/etc/
	$(INSTALL) -vm644 autostart/*.desktop $(DESTDIR)$(AUTOSTARTDIR)
	$(INSTALL) -vm644 menus/*.menu $(DESTDIR)$(MENUDIR)
	$(INSTALL) -vm644 applications/*.desktop $(DESTDIR)$(APPLICATIONSDIR)

uninstall:
	$(RM) -r $(DESTDIR)/etc/spm/ $(RM) $(DESTDIR)/etc/spm.conf
	$(RM) $(DESTDIR)$(AUTOSTARTDIR)/powertray.desktop
	$(RM) $(DESTDIR)$(APPLICATIONSDIR)/powertray.desktop
	$(RM) $(DESTDIR)$(APPLICATIONSDIR)/mounttray.desktop