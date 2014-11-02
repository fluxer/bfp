include ../Makefile.inc

install:
	$(INSTALL) -dm755 $(DESTDIR)$(BASHCOMPLETIONDIR) \
		$(DESTDIR)$(APPLICATIONSDIR) \
		$(DESTDIR)$(PIXMAPSDIR)
	$(INSTALL) -m644 spm.bash $(DESTDIR)$(BASHCOMPLETIONDIR)/spm
	$(INSTALL) -m644 spm-tools.bash $(DESTDIR)$(BASHCOMPLETIONDIR)/spm-tools
	$(INSTALL) -m644 spm-gui.desktop $(DESTDIR)$(APPLICATIONSDIR)/spm-gui.desktop
	$(INSTALL) -m644 spm.png $(DESTDIR)$(PIXMAPSDIR)/spm-gui.png

uninstall:
	$(RM) $(DESTDIR)$(BASHCOMPLETIONDIR)/spm
	$(RM) $(DESTDIR)$(BASHCOMPLETIONDIR)/spm-tools
	$(RM) $(DESTDIR)$(APPLICATIONSDIR)/spm-gui.desktop
	$(RM) $(DESTDIR)$(PIXMAPSDIR)/spm-gui.desktop

.PHONY: install uninstall
