include ../../Makefile.inc

all: clean
	$(NUITKA) main.py
	$(STRIP) main.exe

install:
	$(INSTALL) -dm755 $(DESTDIR)$(BINDIR)
	$(INSTALL) -m755 main.exe $(DESTDIR)$(BINDIR)/pman

uninstall:
	$(RM) $(DESTDIR)$(BINDIR)/pman

clean:
	$(RM) -r *.build/ *.exe
	$(RM) $(shell $(FIND) . -name '*.pyc' -o -name '*.pyo')

.PHONY: all install uninstall clean
