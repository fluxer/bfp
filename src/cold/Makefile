include ../../Makefile.inc

.py:
	$(NUITKA) $<

all: clean bump
	$(NUITKA) cold.py
	$(STRIP) *.exe

cython: clean bump
	$(CYTHON) --embed cold.py
	$(CC) cold.c $(shell pkg-config --cflags --libs $(PYTHON)) -o cold.exe
	$(STRIP) *.exe *.so

install:
	$(INSTALL) -dm755 $(DESTDIR)$(BINDIR)
	$(INSTALL) -m755 cold.exe $(DESTDIR)$(BINDIR)/cold

uninstall:
	$(RM) $(DESTDIR)$(BINDIR)/cold

clean:
	$(RM) -r *.build/ *.exe __pycache__ *.c
	$(RM) $(shell $(FIND) . -name '*.pyc' -o -name '*.pyo')

bump:
	$(SED) 's|^app_version.*|app_version = "$(VERSION) ($(GIT_VERSION))"|' -i cold.py

.SUFFIXES: .py
.PHONY: all cython check install uninstall clean bump
