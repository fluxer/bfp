include ../../Makefile.inc

all: clean bump
	$(CC) -shared _libudev.c \
		$(shell pkg-config --cflags --libs $(PYTHON)) \
		$(shell pkg-config --cflags --libs libudev) \
		-o _libudev.so
	$(NUITKA) --module libudev.py
	$(NUITKA) ahws.py
	$(STRIP) *.exe *.so

cython: clean bump
	# NOTE: _libudev will not work
	$(CC) -shared _libudev.c \
		$(shell pkg-config --cflags --libs $(PYTHON)) \
		$(shell pkg-config --cflags --libs libudev) \
		-o _libudev.so
	$(CYTHON) libudev.py
	$(CYTHON) --embed ahws.py
	$(CC) -shared libudev.c $(shell pkg-config --cflags $(PYTHON)) -o libudev.so
	$(CC) ahws.c $(shell pkg-config --cflags --libs $(PYTHON)) -o ahws.exe
	$(STRIP) *.exe *.so

install:
	$(INSTALL) -dm755 $(DESTDIR)$(SBINDIR)
	$(INSTALL) -m755 ahws.exe $(DESTDIR)$(SBINDIR)/ahws
	$(INSTALL) -m644 *.so $(DESTDIR)$(SITEDIR)/
	$(CP) -r ahws.d/ $(DESTDIR)$(ETCDIR)/

uninstall:
	$(RM) $(DESTDIR)$(SITEDIR)/libudev.so
	$(RM) $(DESTDIR)$(SITEDIR)/_libudev.so
	$(RM) $(DESTDIR)$(SBINDIR)/ahws
	$(RM) $(DESTDIR)$(ETCDIR)/ahws.d

clean:
	$(RM) -r *.build/ *.so *.exe __pycache__
	$(RM) $(shell $(FIND) . -name '*.pyc' -o -name '*.pyo')

bump:
	$(SED) 's|^app_version.*|app_version = "$(VERSION) ($(GIT_VERSION))"|' -i ahws.py
.PHONY: all check install uninstall clean
