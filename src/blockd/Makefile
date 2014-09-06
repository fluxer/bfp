include ../../Makefile.inc

all: bump clean
	$(GCC) -shared libudev.c \
		$(shell $(PKGCONFIG) --cflags --libs python) \
		$(shell $(PKGCONFIG) --cflags --libs libudev) \
		-o _libudev.so
	$(NUITKA) --module libudev.py
	# $(NUITKA) main.py
	# $(NUITKA) client.py
	# $(STRIP) *.exe *.so

install:
	$(INSTALL) -dm755 $(DESTDIR)$(SBINDIR) $(DESTDIR)$(SITEDIR) \
		$(DESTDIR)$(DBSYSTEMDIR)/ $(DESTDIR)$(DBSERVICEDIR)/
	# $(INSTALL) -m755 main.exe $(DESTDIR)$(SBINDIR)/blockd
	# $(INSTALL) -m755 client.exe $(DESTDIR)$(SBINDIR)/blockctl
	$(INSTALL) -m755 main.py $(DESTDIR)$(SBINDIR)/blockd
	$(INSTALL) -m755 client.py $(DESTDIR)$(SBINDIR)/blockctl
	$(INSTALL) -m644 *.so $(DESTDIR)$(SITEDIR)/
	$(INSTALL) -m644 *.conf $(DESTDIR)$(DBSYSTEMDIR)/
	$(INSTALL) -m644 *.service $(DESTDIR)$(DBSERVICEDIR)/

uninstall:
	$(RM) $(DESTDIR)$(SITEDIR)/libudev.so
	$(RM) $(DESTDIR)$(SITEDIR)/_libudev.so
	$(RM) $(DESTDIR)$(SBINDIR)/blockd
	$(RM) $(DESTDIR)$(DBSYSTEMDIR)/blockd.conf
	$(RM) $(DESTDIR)$(DBSERVICEDIR)/blockd.service

clean:
	$(RM) -r *.build/ *.so *.exe
	$(RM) $(shell $(FIND) . -name '*.pyc' -o -name '*.pyo')

bump:
	# $(SED) 's|^app_version.*|app_version = "$(VERSION) ($(GIT_VERSION))"|' -i main.py

.PHONY: all check install uninstall clean bump
