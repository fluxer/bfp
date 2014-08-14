include ../Makefile.inc

install:
	$(INSTALL) -dm755 $(DESTDIR)/etc/bash_completion.d $(DESTDIR)/etc/logrotate.d
	$(INSTALL) -m644 spm.bash $(DESTDIR)/etc/bash_completion.d/spm
	$(INSTALL) -m644 spm-tools.bash $(DESTDIR)/etc/bash_completion.d/spm-tools
	$(INSTALL) -m644 spm.logrotate $(DESTDIR)/etc/logrotate.d/spm

uninstall:
	$(RM) $(DESTDIR)/etc/bash_completion.d/spm
	$(RM) $(DESTDIR)/etc/bash_completion.d/spm-tools
	$(RM) $(DESTDIR)/etc/logrotate.d/spm
