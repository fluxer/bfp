include ../../Makefile.inc

.py:
	$(NUITKA) $<

all: bump clean
	$(NUITKA) main.py
	$(STRIP) *.exe

cython: clean
	$(CYTHON) --embed main.py
	$(CC) main.c $(shell pkg-config --cflags --libs $(PYTHON)) -o main.exe
	$(STRIP) *.exe

install:
	$(INSTALL) -dm755 $(DESTDIR)$(SBINDIR)
	$(INSTALL) -m755 main.exe $(DESTDIR)$(SBINDIR)/cparted

uninstall:
	$(RM) $(DESTDIR)$(SBINDIR)/cparted

clean:
	$(RM) -r *.build/ *.exe __pycache__ *.c
	$(RM) $(shell $(FIND) . -name '*.pyc' -o -name '*.pyo')

bump:
	$(SED) 's|^app_version.*|app_version = "$(VERSION) ($(GIT_VERSION))"|' -i main.py

.SUFFIXES: .py
.PHONY: all cython install uninstall clean bump
