include ../../Makefile.inc

all: clean
	$(NUITKA) puzzle.py
	$(NUITKA) analogclock.py
	$(STRIP) puzzle.exe analogclock.exe

install:
	$(INSTALL) -dm755 $(DESTDIR)$(BINDIR)
	$(INSTALL) -m755 puzzle.exe $(DESTDIR)$(BINDIR)/qpuzzle
	$(INSTALL) -m755 analogclock.exe $(DESTDIR)$(BINDIR)/qanalogclock

uninstall:
	$(RM) $(DESTDIR)$(BINDIR)/qpuzzle
	$(RM) $(DESTDIR)$(BINDIR)/qanalogclock

clean:
	$(RM) -r *.build/ *.exe
	$(RM) $(shell $(FIND) . -name '*.pyc' -o -name '*.pyo')

.PHONY: all install uninstall clean
