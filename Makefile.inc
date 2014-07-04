VERSION = 0.9.7

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
PYTHON = python2
PYTHON_VERSION = $(shell $(PYTHON) -c "import sys; print(sys.version[:3])")
SITEDIR = $(PREFIX)/lib/python$(PYTHON_VERSION)/site-packages
GIT = git
GIT_VERSION = $(shell $(GIT) rev-parse --short HEAD || echo stable)

SED = sed
GCC= gcc
STRIP = strip
INSTALL = install
RM = rm -f
CP = cp -f

MACHINE = $(shell $(GCC) -dumpmachine)
ARCH = $(shell uname -m | $(SED) 's|_|-|')
JOBS = $(shell echo $$((`nproc || echo 1`+1)))

POD2MAN = pod2man
PYUIC = pyuic4
PYRCC = pyrcc4
NUITKA = ../../nuitka/bin/nuitka --recurse-not-to=PyQt4,xdg,parted \
	--python-version=$(PYTHON_VERSION)
