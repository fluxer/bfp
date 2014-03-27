include ../../Makefile.inc

all: clean
	mkdir -p build
	$(CYTHON) --embed -2 -D -t shell.py -o build/shell.c
	$(CC) $(CFLAGS) build/shell.c -o build/shell
	$(STRIP) build/shell

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR)
	$(INSTALL) -vm755 build/shell $(DESTDIR)$(BINDIR)/shell

uninstall:
	$(RM) $(DESTDIR)$(BINDIR)/shell

clean:
	$(RM) -r build/
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo')

.PHONY: all install uninstall clean
