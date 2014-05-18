include ../Makefile.inc

install:
	$(INSTALL) -vdm755 $(DESTDIR)/etc/bash_completion.d $(DESTDIR)/etc/logrotate.d
	$(INSTALL) -vm644 spm.bash $(DESTDIR)/etc/bash_completion.d/spm
	$(INSTALL) -vm644 spm-tools.bash $(DESTDIR)/etc/bash_completion.d/spm-tools
	$(INSTALL) -vm644 spm.logrotate $(DESTDIR)/etc/logrotate.d/spm
	$(INSTALL) -vm644 qfile.desktop $(DESTDIR)/$(APPLICATIONSDIR)/qfile.desktop


uninstall:
	$(RM) $(DESTDIR)/etc/bash_completion.d/spm
	$(RM) $(DESTDIR)/etc/bash_completion.d/spm-tools
	$(RM) $(DESTDIR)/etc/logrotate.d/spm
	$(RM) $(DESTDIR)/$(APPLICATIONSDIR)/qfile.desktop
