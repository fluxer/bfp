include ../Makefile.inc

install:
	$(INSTALL) -vdm755 $(DESTDIR)/etc/spm $(DESTDIR)/etc/services.d
	$(INSTALL) -vdm755 $(DESTDIR)$(SYSTEMDIR)
	$(INSTALL) -vdm755 $(DESTDIR)$(SERVICEDIR)
	$(INSTALL) -vdm755 $(DESTDIR)$(AUTOSTARTDIR)
	$(INSTALL) -vdm755 $(DESTDIR)$(APPLICATIONSDIR)
	$(INSTALL) -vm644 spm.conf $(DESTDIR)/etc/
	$(INSTALL) -vm644 repositories.conf $(DESTDIR)/etc/spm/
	$(INSTALL) -vm644 mirrors.conf $(DESTDIR)/etc/spm/
	sed 's|#MACHINE#|$(MACHINE)|g' -i $(DESTDIR)/etc/spm.conf
	sed 's|#ARCH#|$(ARCH)|g' -i $(DESTDIR)/etc/spm.conf
	sed 's|#JOBS#|$(JOBS)|g' -i $(DESTDIR)/etc/spm.conf
	$(INSTALL) -vm644 powerd.conf $(DESTDIR)/etc/
	$(INSTALL) -vm644 mountd.conf $(DESTDIR)/etc/
	$(INSTALL) -vm644 dbus/*.conf $(DESTDIR)$(SYSTEMDIR)
	$(INSTALL) -vm644 dbus/*.service $(DESTDIR)$(SERVICEDIR)
	$(INSTALL) -vm644 autostart/*.desktop $(DESTDIR)$(AUTOSTARTDIR)
	$(INSTALL) -vm644 applications/*.desktop $(DESTDIR)$(APPLICATIONSDIR)
	$(INSTALL) -vm644 services/*.conf $(DESTDIR)/etc/services.d

uninstall:
	$(RM) -r $(DESTDIR)/etc/spm/ $(DESTDIR)/etc/services.d
	$(RM) $(DESTDIR)/etc/spm.conf
	$(RM) $(DESTDIR)/etc/powerd.conf
	$(RM) $(DESTDIR)/etc/mountd.conf
	$(RM) $(DESTDIR)$(SYSTEMDIR)/org.powerd.PowerD.conf
	$(RM) $(DESTDIR)$(SYSTEMDIR)/org.mountd.MountD.conf
	$(RM) $(DESTDIR)$(SERVICEDIR)/org.powerd.PowerD.service
	$(RM) $(DESTDIR)$(SERVICEDIR)/org.mountd.MountD.service
	$(RM) $(DESTDIR)$(AUTOSTARTDIR)/powerd.desktop
	$(RM) $(DESTDIR)$(AUTOSTARTDIR)/powertray.desktop
	$(RM) $(DESTDIR)$(APPLICATIONSDIR)/powertray.desktop