include ../../Makefile.inc

all: clean
	mkdir -p build
	$(CYTHON) --embed -2 -D -t powertray.py -o build/powertray.c
	$(CC) $(CFLAGS) build/powertray.c -o build/powertray
	$(STRIP) build/powertray

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR)
	$(INSTALL) -vm755 build/powertray $(DESTDIR)$(BINDIR)/powertray

uninstall:
	$(RM) $(DESTDIR)$(BINDIR)/powertray

clean:
	$(RM) -r build/
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo')

.PHONY: all install uninstall clean
