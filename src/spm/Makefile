include ../../Makefile.inc

all: bump clean
	mkdir -p build
	$(CYTHON) -2 libconfig.py -o build/libconfig.c
	$(CC) $(CFLAGS) -shared build/libconfig.c -o build/libconfig.so
	$(CYTHON) -2 libmode.py -o build/libmode.c
	$(CC) $(CFLAGS) -shared build/libmode.c -o build/libmode.so
	$(CYTHON) -2 --embed -I. spm.py -o build/spm.c
	$(CC) $(CFLAGS) build/spm.c -o build/spm
	$(CYTHON) -2 --embed -I. tools.py -o build/tools.c
	$(CC) $(CFLAGS) build/tools.c -o build/spm-tools
	$(STRIP) build/libconfig.so build/libmode.so build/spm build/spm-tools

check:
	python2 test.py

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(BINDIR)
	$(INSTALL) -vm755 build/spm $(DESTDIR)$(BINDIR)/spm
	$(INSTALL) -vm755 build/spm-tools $(DESTDIR)$(BINDIR)/spm-tools
	$(INSTALL) -vm644 build/libconfig.so $(DESTDIR)$(SITEDIR)/libconfig.so
	$(INSTALL) -vm644 build/libmode.so $(DESTDIR)$(SITEDIR)/libmode.so

uninstall:
	$(RM) $(DESTDIR)$(BINDIR)/spm
	$(RM) $(DESTDIR)$(BINDIR)/spm-tools
	$(RM) $(DESTDIR)$(SITEDIR)/libconfig.so
	$(RM) $(DESTDIR)$(SITEDIR)/libmode.so

clean:
	$(RM) -r build
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo')

bump:
	sed 's|^app_version.*|app_version = "$(VERSION) ($(GIT_VERSION))"|' -i spm.py tools.py

.PHONY: all check install uninstall clean bump
