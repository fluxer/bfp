include ../../Makefile.mk

all: clean
	$(CC) ahws.c $(shell $(PYTHON)-config --includes --libs) $(CFLAGS) -o ahws.exe
	$(STRIP) *.exe

sources: bump
	$(RM) *.c
	$(CYTHON) --embed ahws.py

install:
	$(INSTALL) -dm755 $(DESTDIR)$(SBINDIR) $(DESTDIR)/etc/ \
		$(DESTDIR)$(INITDIR)/
	$(INSTALL) -m755 ahws.exe $(DESTDIR)$(SBINDIR)/ahws
	$(CP) -r ahws.d/ $(DESTDIR)/etc/
	$(INSTALL) -m744 ahws.init $(DESTDIR)$(INITDIR)/ahws

uninstall:
	$(RM) $(DESTDIR)$(SBINDIR)/ahws
	$(RM) $(DESTDIR)$(INITDIR)/ahws
	$(RM) $(DESTDIR)/etc/ahws.d

clean:
	$(RM) -r *.build/ *.so *.exe __pycache__
	$(RM) $(shell $(FIND) . -name '*.pyc' -o -name '*.pyo')

bump:
	$(SED) 's|^app_version.*|app_version = "$(VERSION) ($(GIT_VERSION))"|' -i ahws.py

.PHONY: all sources install uninstall clean bump
