include ../../Makefile.inc

all: clean
	mkdir -p build
	$(CYTHON) --embed -2 -D -t powerd.py -o build/powerd.c
	$(CC) $(CFLAGS) build/powerd.c -o build/powerd
	$(CYTHON) --embed -2 -D -t powerctl.py -o build/powerctl.c
	$(CC) $(CFLAGS) build/powerctl.c -o build/powerctl
	$(STRIP) build/powerd build/powerctl

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR)
	$(INSTALL) -vm755 build/powerd $(DESTDIR)$(BINDIR)/powerd
	$(INSTALL) -vm755 build/powerctl $(DESTDIR)$(BINDIR)/powerctl

uninstall:
	$(RM) $(DESTDIR)$(BINDIR)/powerd
	$(RM) $(DESTDIR)$(BINDIR)/powerctl

clean:
	$(RM) -r build/
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo')

.PHONY: all install uninstall clean
