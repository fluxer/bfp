include ../../Makefile.inc

all: clean
	mkdir -p build
	$(CYTHON) --embed -2 -D -t mounttray.py -o build/mounttray.c
	$(CC) $(CFLAGS) build/mounttray.c -o build/mounttray
	$(STRIP) build/mounttray

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR)
	$(INSTALL) -vm755 build/mounttray $(DESTDIR)$(BINDIR)/mounttray

uninstall:
	$(RM) $(DESTDIR)$(BINDIR)/mounttray

clean:
	$(RM) -r build/
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo')

.PHONY: all install uninstall clean
