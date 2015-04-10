include ../Makefile.inc

install:
	$(INSTALL) -dm755 $(DESTDIR)$(BASHCOMPLETIONDIR)
	$(INSTALL) -m644 spm.bash $(DESTDIR)$(BASHCOMPLETIONDIR)/spm
	$(INSTALL) -m644 spm-tools.bash $(DESTDIR)$(BASHCOMPLETIONDIR)/spm-tools

uninstall:
	$(RM) $(DESTDIR)$(BASHCOMPLETIONDIR)/spm
	$(RM) $(DESTDIR)$(BASHCOMPLETIONDIR)/spm-tools

.PHONY: install uninstall
