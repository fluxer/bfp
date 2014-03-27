include ../../Makefile.inc

all: clean
	mkdir -p build
	$(CYTHON) --embed -2 -D -t mountd.py -o build/mountd.c
	$(CC) $(CFLAGS) build/mountd.c -o build/mountd
	$(CYTHON) --embed -2 -D -t mountctl.py -o build/mountctl.c
	$(CC) $(CFLAGS) build/mountctl.c -o build/mountctl
	$(STRIP) build/mountctl build/mountctl

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR)
	$(INSTALL) -vm755 build/mountd $(DESTDIR)$(BINDIR)/mountd
	$(INSTALL) -vm755 build/mountctl $(DESTDIR)$(BINDIR)/mountctl

uninstall:
	$(RM) $(DESTDIR)$(BINDIR)/mountd
	$(RM) $(DESTDIR)$(BINDIR)/mountctl

clean:
	$(RM) -r build/
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo')

.PHONY: all install uninstall clean
