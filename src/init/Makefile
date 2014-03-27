include ../../Makefile.inc

all: clean
	mkdir -p build
	$(CYTHON) --embed -2 -D -t init.py -o build/init.c
	$(CC) $(CFLAGS) build/init.c -o build/init
	$(CYTHON) --embed -2 -D -t initctl.py -o build/initctl.c
	$(CC) $(CFLAGS) build/initctl.c -o build/initctl
	$(STRIP) build/init build/initctl

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR)
	$(INSTALL) -vm755 build/init $(DESTDIR)$(BINDIR)/init
	$(INSTALL) -vm755 build/initctl $(DESTDIR)$(BINDIR)/initctl

uninstall:
	$(RM) $(DESTDIR)$(BINDIR)/init
	$(RM) $(DESTDIR)$(BINDIR)/init

clean:
	$(RM) -r build/
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo')

.PHONY: all install uninstall clean
