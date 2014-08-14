include ../../Makefile.inc

all: clean
	$(NUITKA) puzzle.py
	$(NUITKA) tetrix.py
	$(NUITKA) analogclock.py
	$(STRIP) puzzle.exe tetrix.exe analogclock.exe

install:
	$(INSTALL) -dm755 $(DESTDIR)$(BINDIR)
	$(INSTALL) -m755 puzzle.exe $(DESTDIR)$(BINDIR)/qpuzzle
	$(INSTALL) -m755 tetrix.exe $(DESTDIR)$(BINDIR)/qtetrix
	$(INSTALL) -m755 analogclock.exe $(DESTDIR)$(BINDIR)/qanalogclock

uninstall:
	$(RM) $(DESTDIR)$(BINDIR)/qpuzzle
	$(RM) $(DESTDIR)$(BINDIR)/qtetrix
	$(RM) $(DESTDIR)$(BINDIR)/qanalogclock

clean:
	$(RM) -r *.build/ *.exe
	$(RM) $(shell $(FIND) . -name '*.pyc' -o -name '*.pyo')

.PHONY: all install uninstall clean
