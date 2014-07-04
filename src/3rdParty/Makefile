include ../../Makefile.inc

all: clean
	$(NUITKA) puzzle.py
	$(NUITKA) tetrix.py
	$(NUITKA) analogclock.py
	$(STRIP) puzzle.exe tetrix.exe analogclock.exe

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR)
	$(INSTALL) -vm755 puzzle.exe $(DESTDIR)$(BINDIR)/qpuzzle
	$(INSTALL) -vm755 tetrix.exe $(DESTDIR)$(BINDIR)/qtetrix
	$(INSTALL) -vm755 analogclock.exe $(DESTDIR)$(BINDIR)/qanalogclock

uninstall:
	$(RM) $(DESTDIR)$(BINDIR)/qpuzzle
	$(RM) $(DESTDIR)$(BINDIR)/qtetrix
	$(RM) $(DESTDIR)$(BINDIR)/qanalogclock

clean:
	$(RM) -r *.build/ *.exe
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo')

.PHONY: all install uninstall clean
