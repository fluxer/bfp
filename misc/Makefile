include ../Makefile.inc

install:
	$(INSTALL) -vdm755 $(DESTDIR)/etc/bash_completion.d $(DESTDIR)/etc/logrotate.d
	$(INSTALL) -vm644 spm.bash $(DESTDIR)/etc/bash_completion.d/spm
	$(INSTALL) -vm644 spm-tools.bash $(DESTDIR)/etc/bash_completion.d/spm-tools
	$(INSTALL) -vm644 spm.logrotate $(DESTDIR)/etc/logrotate.d/spm


uninstall:
	$(RM) $(DESTDIR)$(SBINDIR)/powerd
	$(RM) $(DESTDIR)$(BINDIR)/powerctl
	$(RM) $(DESTDIR)$(BINDIR)/powertray
	$(RM) $(DESTDIR)/etc/powerd.conf
	
	$(RM) $(DESTDIR)$(MANDIR)/man8/powerd.8
	$(RM) $(DESTDIR)$(MANDIR)/man8/powerctl.8
	$(RM) $(DESTDIR)$(MANDIR)/man5/powerd.conf.5
	
	$(RM) $(DESTDIR)$(SYSTEMDIR)/org.powerd.PowerD.conf
	$(RM) $(DESTDIR)$(SERVICEDIR)/org.powerd.PowerD.service
	
	$(RM) $(DESTDIR)$(AUTOSTARTDIR)/powerd.desktop
	
	$(RM) $(DESTDIR)$(APPLICATIONSDIR)/powertray
