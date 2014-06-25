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
	$(INSTALL) -vm644 menus/*.menu $(DESTDIR)$(MENUSDIR)
	$(INSTALL) -vm644 applications/*.desktop $(DESTDIR)$(APPLICATIONSDIR)

uninstall:
	$(RM) -r $(DESTDIR)/etc/spm/ $(DESTDIR)/etc/spm.conf
	$(RM) $(DESTDIR)/etc/system.conf
	$(RM) $(DESTDIR)$(AUTOSTARTDIR)/dummy.desktop
	$(RM) $(DESTDIR)$(APPLICATIONSDIR)/qedt.desktop
	$(RM) $(DESTDIR)$(APPLICATIONSDIR)/qfile.desktop
	$(RM) $(DESTDIR)$(APPLICATIONSDIR)/qnetwork.desktop
	$(RM) $(DESTDIR)$(APPLICATIONSDIR)/qsettings.desktop
	$(RM) $(DESTDIR)$(APPLICATIONSDIR)/spm-qt.desktop
	$(RM) $(DESTDIR)$(MENUSDIR)/applications.menu