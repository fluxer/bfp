VERSION = 1.9.1
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
BASHCOMPLETIONDIR = /etc/bash_completion.d
LOCALEDIR = $(SHAREDIR)/locale
INITDIR = /etc/init.d

PYTHON_VERSION = $(shell $(PYTHON) -c "import sys; print(sys.version[:3])")
MACHINE = $(shell $(CC) -dumpmachine)
ARCH = $(shell uname -m | $(SED) 's|_|-|')
JOBS = $(shell echo $$((`getconf _NPROCESSORS_CONF || echo 1`+1)))

GIT = git
BASH = bash
GREP = grep
FIND = find
SED = sed
UNIQ = uniq
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
XGETTEXT = xgettext
MSGMERGE = msgmerge
MSGATTRIB = msgattrib
MSGFMT = msgfmt
POD2MAN = pod2man
CLOC = cloc

ifneq ($(shell which python2.7),)
	PYTHON = python2.7
else
	PYTHON = python2
endif
ifneq ($(shell which pydoc2),)
	PYDOC = pydoc2
else
	PYDOC = pydoc
endif
ifneq ($(shell which cython2),)
	CYTHON = cython2 --verbose
else
	CYTHON = cython --verbose
endif
ifneq ($(shell which pep8),)
	PYLINT = pep8 --config="$(TOPDIR)/pep8.conf"
else ifneq ($(shell which pylint2),)
	PYLINT = pylint2 --rcfile="$(TOPDIR)/pylint.conf"
else
	PYLINT = pylint --rcfile="$(TOPDIR)/pylint.conf"
endif
ifneq ($(shell which gpg2),)
	GPG = gpg2
else
	GPG = gpg
endif

all:

stat:
	$(CLOC) $(shell $(FIND) -type f -name '*.py' -o -name '*.sh')

lint:
	$(PYLINT) $(shell $(FIND) -type f -name '*.py' | \
		$(GREP) -v -e libudev.py -e gui_ui.py)

.PHONY: all stat lint
