include ../../Makefile.inc

all: clean
	$(PYRCC) libqresources.qrc -o libqresources_rc.py
	$(NUITKA) --module libqresources_rc.py
	$(STRIP) libqresources_rc.so

install:
	$(INSTALL) -vdm755 $(DESTDIR)$(SITEDIR) $(DESTDIR)$(SHAREDIR)/qresources
	$(INSTALL) -vm644 libqresources_rc.so $(DESTDIR)$(SITEDIR)/libqresources_rc.so
	$(CP) -vr resources $(DESTDIR)$(SHAREDIR)/qresources/

uninstall:
	$(RM) $(DESTDIR)$(SITEDIR)/libqresources_rc.so
	$(RM) -r $(DESTDIR)$(SHAREDIR)/qresources/

clean:
	$(RM) -r *.build/ *.so libqresources_rc.py
	$(RM) $(shell find . -name '*.pyc' -o -name '*.pyo')

.PHONY: all install uninstall clean
