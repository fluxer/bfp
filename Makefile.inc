VERSION = 0.0.1
GIT_VERSION = $(shell git rev-parse --short HEAD || echo stable)

DESTDIR = 
ETCDIR = /etc
PREFIX = 
BINDIR = $(PREFIX)/bin
SBINDIR = $(PREFIX)/sbin
SHAREDIR = $(PREFIX)/share
MANDIR = $(SHAREDIR)/man
AUTOSTARTDIR = $(ETCDIR)/xdg/autostart
APPLICATIONSDIR = $(PREFIX)/share/applications
PYTHON_VERSION = $(shell python2 -c "import sys; print sys.version[:3]")
SITEDIR = $(PREFIX)/lib/python$(PYTHON_VERSION)/site-packages

CFLAGS = -I$(PREFIX)/include/python$(PYTHON_VERSION) -lpython$(PYTHON_VERSION)
MACHINE = $(shell gcc -dumpmachine)
ARCH = $(shell uname -m | sed 's|_|-|')
JOBS = $(shell echo $$((`nproc`+1)))

CYTHON = cython
CC = gcc
INSTALL = install
STRIP = strip
RM = rm -f
CP = cp -f
PYUIC = pyuic4
