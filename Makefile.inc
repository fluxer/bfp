VERSION = 0.9.35

DESTDIR = 
PREFIX = $(shell $(PYTHON) -c "import sys; print(sys.prefix)")
BINDIR = $(PREFIX)/bin
SBINDIR = $(PREFIX)/sbin
SHAREDIR = $(PREFIX)/share
MANDIR = $(SHAREDIR)/man
PYTHON = python2
PYTHON_VERSION = $(shell $(PYTHON) -c "import sys; print(sys.version[:3])")
# Debian and derivatives use dist-packages - how glorious!
SITEDIR = $(PREFIX)/lib/python$(PYTHON_VERSION)/site-packages
TRDIR =$(shell $(PYTHON) -c "from PyQt4.QtCore import QLibraryInfo; \
	print(QLibraryInfo.location(QLibraryInfo.TranslationsPath))")
GIT = git
GIT_VERSION = $(shell $(GIT) rev-parse --short HEAD || echo stable)

MACHINE = $(shell $(GCC) -dumpmachine)
ARCH = $(shell uname -m | $(SED) 's|_|-|')
JOBS = $(shell echo $$((`nproc || echo 1`+1)))

GREP = grep
FIND = find
SED = sed
GCC= gcc
STRIP = strip
INSTALL = install -v
RM = rm -vf
CP = cp -vf
XZ = xz -v

MARKDOWN = markdown_py -v
PYDOC = pydoc
POD2MAN = pod2man
PYUIC = pyuic4
PYRCC = pyrcc4
PYLUPDATE = pylupdate4 -noobsolete
LRELEASE = lrelease
NUITKA = $(PYTHON) ../../nuitka/bin/nuitka --recurse-not-to=PyQt4,parted,Xlib \
	--python-version=$(PYTHON_VERSION)
PYLINT = pylint

all:

stat:
	cloc $(shell $(FIND) -name '*.py' -o -name '*.sh')

lint:
	$(PYLINT) $(shell $(FIND) -name '*.py') | $(GREP) -v -e 'Line too long'

.PHONY: all stat lint
