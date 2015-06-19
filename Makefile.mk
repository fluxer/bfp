VERSION = 1.8.1
GIT_VERSION = $(shell $(GIT) rev-parse --short HEAD || echo stable)

TOPDIR = $(dir $(lastword $(MAKEFILE_LIST)))
DESTDIR = 
PREFIX = $(shell $(PYTHON)-config --prefix)
BINDIR = $(PREFIX)/bin
SBINDIR = $(PREFIX)/sbin
SHAREDIR = $(PREFIX)/share
MANDIR = $(SHAREDIR)/man
DOCDIR = $(SHAREDIR)/doc
SITEDIR = $(shell $(PYTHON) -c "import site; print(site.getsitepackages()[0])")
BASHCOMPLETIONDIR = /etc/bash_completion.d/
LOCALEDIR = $(SHAREDIR)/locale
DBSYSTEMDIR = /etc/dbus-1/system.d/
DBSERVICEDIR = $(SHAREDIR)/dbus-1/system-services/
APPLICATIONSDIR = $(SHAREDIR)/applications
AUTOSTARTDIR = /etc/xdg/autostart

MACHINE = $(shell $(CC) -dumpmachine)
ARCH = $(shell uname -m | $(SED) 's|_|-|')
JOBS = $(shell echo $$((`getconf _NPROCESSORS_CONF || echo 1`+1)))

GIT = git
BASH = bash
PYTHON = python2
PYTHON_VERSION = $(shell $(PYTHON) -c "import sys; print(sys.version[:3])")
GREP = grep
FIND = find
SED = sed
CC ?= gcc
ifeq ($(GIT_VERSION),stable)
    STRIP = echo "Strip ignored on stable build, "
else
    STRIP = strip
endif
INSTALL = install -v
RM = rm -vf
CP = cp -vf
XZ = xz -v
GPG = gpg2
NUITKA = $(PYTHON) $(TOPDIR)/nuitka/bin/nuitka --recurse-none \
	--python-version=$(PYTHON_VERSION)
CYTHON = cython --verbose
PYLINT = pylint --rcfile=$(TOPDIR)/pylint.conf
XGETTEXT = xgettext
MSGMERGE = msgmerge
MSGATTRIB = msgattrib
MSGFMT = msgfmt
POD2MAN = pod2man
PYDOC = pydoc
PYUIC = pyuic4

all:

stat:
	cloc $(shell $(FIND) -name '*.py' -o -name '*.sh')

lint:
	$(PYLINT) $(shell $(FIND) -name '*.py' | $(GREP) -v libudev.py)

.PHONY: all stat lint
