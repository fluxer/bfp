include ../../Makefile.mk

all: clean
	$(CC) cold.c $(shell $(PYTHON)-config --includes --libs) -o cold.exe
	$(STRIP) *.exe

sources: bump
	$(RM) *.c
	$(CYTHON) --embed cold.py

install:
	$(INSTALL) -dm755 $(DESTDIR)$(BINDIR)
	$(INSTALL) -m755 cold.exe $(DESTDIR)$(BINDIR)/cold

uninstall:
	$(RM) $(DESTDIR)$(BINDIR)/cold

clean:
	$(RM) -r *.build/ *.exe __pycache__
	$(RM) $(shell $(FIND) . -name '*.pyc' -o -name '*.pyo')

bump:
	$(SED) 's|^app_version.*|app_version = "$(VERSION) ($(GIT_VERSION))"|' -i cold.py

.PHONY: all sources install uninstall clean bump
