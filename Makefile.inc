VERSION = 0.9.4
GIT_VERSION = $(shell git rev-parse --short HEAD || echo stable)

DESTDIR = 
ETCDIR = /etc
PREFIX = 
BINDIR = $(PREFIX)/bin
SBINDIR = $(PREFIX)/sbin
SHAREDIR = $(PREFIX)/share
MANDIR = $(SHAREDIR)/man
AUTOSTARTDIR = $(ETCDIR)/xdg/autostart
MENUSDIR = $(ETCDIR)/xdg/menus
APPLICATIONSDIR = $(PREFIX)/share/applications
PYTHON_VERSION = $(shell python2 -c "import sys; print sys.version[:3]")
SITEDIR = $(PREFIX)/lib/python$(PYTHON_VERSION)/site-packages

MACHINE = $(shell gcc -dumpmachine)
ARCH = $(shell uname -m | sed 's|_|-|')
JOBS = $(shell echo $$((`nproc || echo 1`+1)))

POD2MAN = pod2man
PYUIC = pyuic4
PYRCC = pyrcc4
NUITKA = ../../nuitka/bin/nuitka --recurse-not-to=PyQt4,xdg,parted
# NUITKA = nuitka --clang --recurse-not-to=PyQt4,xdg,parted
SED = sed
STRIP = strip
INSTALL = install
RM = rm -f
CP = cp -f
