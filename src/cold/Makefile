include ../../Makefile.mk

.py:
	$(NUITKA) $<

all: clean bump
	$(NUITKA) cold.py
	$(STRIP) *.exe

cython: clean bump
	$(CYTHON) --embed cold.py
	$(CC) cold.c $(shell $(PYTHON)-config --includes --libs) -o cold.exe
	$(STRIP) *.exe

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
.PHONY: all cython install uninstall clean bump
