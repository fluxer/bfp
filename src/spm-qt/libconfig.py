#!/usr/bin/python2

import os
import sys
import ConfigParser

import libmessage
message = libmessage.Message()


MAIN_CONF = '/etc/spm.conf'
REPOSITORIES_CONF = '/etc/spm/repositories.conf'
MIRRORS_CONF = '/etc/spm/mirrors.conf'

if not os.path.isfile(MAIN_CONF):
    message.warning('Configuration file does not exist', MAIN_CONF)

    CACHE_DIR = '/var/cache/spm'
    BUILD_DIR = '/var/tmp/spm'
    ROOT_DIR = '/'
    LOCAL_DIR = ROOT_DIR + 'var/local/spm'
    MIRROR = False
    TIMEOUT = 30
    EXTERNAL = False
    IGNORE = ''
    CHOST = ''
    CFLAGS = ''
    CXXFLAGS = ''
    CPPFLAGS = ''
    LDFLAGS = ''
    MAKEFLAGS = ''
    COMPRESS_MAN = False
    STRIP_BINARIES = False
    STRIP_SHARED = False
    STRIP_STATIC = False
    STRIP_RPATH = False
    IGNORE_MISSING = True
    CONFLICTS = False
    BACKUP = False
    SCRIPTS = False
    TRIGGERS = False
else:
    conf = ConfigParser.SafeConfigParser()
    conf.read(MAIN_CONF)

    CACHE_DIR = conf.get('spm', 'CACHE_DIR')
    BUILD_DIR = conf.get('spm', 'BUILD_DIR')
    ROOT_DIR = conf.get('spm', 'ROOT_DIR')
    LOCAL_DIR = ROOT_DIR + 'var/local/spm'
    IGNORE = conf.get('spm', 'IGNORE')
    MIRROR = conf.getboolean('prepare', 'MIRROR')
    TIMEOUT = conf.getint('prepare', 'TIMEOUT')
    EXTERNAL = conf.getboolean('prepare', 'EXTERNAL')
    CHOST = conf.get('compile', 'CHOST')
    CFLAGS = conf.get('compile', 'CFLAGS')
    CXXFLAGS = conf.get('compile', 'CXXFLAGS')
    CPPFLAGS = conf.get('compile', 'CPPFLAGS')
    LDFLAGS = conf.get('compile', 'LDFLAGS')
    MAKEFLAGS = conf.get('compile', 'MAKEFLAGS')
    COMPRESS_MAN = conf.getboolean('install', 'COMPRESS_MAN')
    STRIP_BINARIES = conf.getboolean('install', 'STRIP_BINARIES')
    STRIP_SHARED = conf.getboolean('install', 'STRIP_SHARED')
    STRIP_STATIC = conf.getboolean('install', 'STRIP_STATIC')
    STRIP_RPATH = conf.getboolean('install', 'STRIP_RPATH')
    IGNORE_MISSING = conf.getboolean('install', 'IGNORE_MISSING')
    CONFLICTS = conf.getboolean('merge', 'CONFLICTS')
    BACKUP = conf.getboolean('merge', 'BACKUP')
    SCRIPTS = conf.getboolean('merge', 'SCRIPTS')
    TRIGGERS = conf.getboolean('merge', 'TRIGGERS')

if not os.path.isfile(REPOSITORIES_CONF):
    message.warning('Repositories file does not exist', REPOSITORIES_CONF)
    REPOSITORIES = ['https://bitbucket.org/lsd-developers/stable.git']
else:
    REPOSITORIES = []
    repositories_conf = open(REPOSITORIES_CONF, 'r')
    for line in repositories_conf.readlines():
        line = line.strip()
        if line.startswith('http://') or line.startswith('https://') \
            or line.startswith('ftp://') or line.startswith('ftps://') \
            or line.startswith('git://') or line.startswith('ssh://') \
            or line.startswith('rsync://'):
            REPOSITORIES.append(line)
    repositories_conf.close()

    if not REPOSITORIES:
        message.critical('Repositories configuration file is empty')
        sys.exit(2)

if not os.path.isfile(MIRRORS_CONF):
    message.warning('Mirrors file does not exist', MIRRORS_CONF)
    MIRRORS = ['http://lsdlinux.org/public/distfiles', 'http://distfiles.gentoo.org/distfiles']
else:
    MIRRORS = []
    mirrors_conf = open(MIRRORS_CONF, 'r')
    for line in mirrors_conf.readlines():
        line = line.strip()
        if line.startswith('http://') or line.startswith('https://') \
            or line.startswith('ftp://') or line.startswith('ftps://'):
            MIRRORS.append(line)
    mirrors_conf.close()

    if not MIRRORS and MIRROR:
        message.critical('Mirrors configuration file is empty')
        sys.exit(2)
