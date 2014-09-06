include ../../Makefile.inc

all: bump clean
	$(GCC) -shared libudev.c \
		$(shell $(PKGCONFIG) --cflags --libs python) \
		$(shell $(PKGCONFIG) --cflags --libs libudev) \
		-o _libudev.so
	$(NUITKA) --module libudev.py
	# $(NUITKA) main.py
	# $(NUITKA) client.py
	# $(STRIP) main.exe client.exe

install:
	$(INSTALL) -dm755 $(DESTDIR)$(SBINDIR) $(DESTDIR)$(SITEDIR) \
		$(DESTDIR)/etc/dbus-1/system.d/
	# $(INSTALL) -m755 main.exe $(DESTDIR)$(SBINDIR)/blockd
	# $(INSTALL) -m755 client.exe $(DESTDIR)$(SBINDIR)/blockctl
	$(INSTALL) -m755 main.py $(DESTDIR)$(SBINDIR)/blockd
	$(INSTALL) -m755 client.py $(DESTDIR)$(SBINDIR)/blockctl
	$(INSTALL) -m644 libudev.so $(DESTDIR)$(SITEDIR)/libudev.so
	$(INSTALL) -m644 _libudev.so $(DESTDIR)$(SITEDIR)/_libudev.so
	$(INSTALL) -m644 blockd.conf $(DESTDIR)$(DBSYSTEMDIR)/blockd.conf
	$(INSTALL) -m644 blockd.service $(DESTDIR)$(DBSERVICEDIR)/blockd.service

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
