VERSION = 1.2.1

TOPDIR = $(dir $(lastword $(MAKEFILE_LIST)))
DESTDIR = 
PREFIX = $(shell $(PYTHON) -c "import sys; print(sys.prefix)")
BINDIR = $(PREFIX)/bin
SBINDIR = $(PREFIX)/sbin
SHAREDIR = $(PREFIX)/share
MANDIR = $(SHAREDIR)/man
PYTHON = python2
PYTHON_VERSION = $(shell $(PYTHON) -c "import sys; print(sys.version[:3])")
SITEDIR = $(shell $(PYTHON) -c "import site; print(site.getsitepackages()[0])")
TRDIR =$(shell $(PYTHON) -c "from PyQt4.QtCore import QLibraryInfo; \
	print(QLibraryInfo.location(QLibraryInfo.TranslationsPath))")
DBSYSTEMDIR = /etc/dbus-1/system.d/
DBSERVICEDIR = $(PREFIX)/share/dbus-1/system-services/
APPLICATIONSDIR = $(PREFIX)/share/applications
PIXMAPSDIR = $(PREFIX)/share/pixmaps
BASHCOMPLETIONDIR = /etc/bash_completion.d/
GIT = git
GIT_VERSION = $(shell $(GIT) rev-parse --short HEAD || echo stable)

MACHINE = $(shell $(GCC) -dumpmachine)
ARCH = $(shell uname -m | $(SED) 's|_|-|')
JOBS = $(shell echo $$((`$(GREP) -c ^processor /proc/cpuinfo || echo 1`+1)))

GREP = grep
FIND = find
SED = sed
GCC= gcc
PKGCONFIG = pkg-config
STRIP = strip
INSTALL = install -v
RM = rm -vf
CP = cp -vf
XZ = xz -v

POOLE = $(PYTHON) $(TOPDIR)/poole/poole.py
PYUIC = pyuic4
PYRCC = pyrcc4
PYLUPDATE = pylupdate4 -noobsolete
LRELEASE = lrelease
NUITKA = $(PYTHON) $(TOPDIR)/nuitka/bin/nuitka --recurse-not-to=PyQt4,parted \
	--python-version=$(PYTHON_VERSION)
PYLINT = pylint --rcfile=$(TOPDIR)/pylint.conf

all:

stat:
	cloc $(shell $(FIND) -name '*.py' -o -name '*.sh')

lint:
	$(PYLINT) $(shell $(FIND) -name '*.py') | $(GREP) -v -e 'Line too long'

.PHONY: all stat lint
