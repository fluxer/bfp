#!/bin/python2

import sys
import argparse
import ast
import ConfigParser
import subprocess
import tarfile
import zipfile
import urllib2
import shutil
import os
import re


app_version = "0.9.35 (b97a719)"

try:
    import libmessage
    message = libmessage.Message()
    import libmisc
    misc = libmisc.Misc()
    import libpackage
    database = libpackage.Database()
    import libspm

    EUID = os.geteuid()

    class OverrideCacheDir(argparse.Action):
        ''' Override cache directory '''
        def __call__(self, parser, namespace, values, option_string=None):
            libspm.CACHE_DIR = os.path.abspath(values)
            setattr(namespace, self.dest, values)

    class OverrideBuildDir(argparse.Action):
        ''' Override build directory '''
        def __call__(self, parser, namespace, values, option_string=None):
            libspm.BUILD_DIR = os.path.abspath(values)
            setattr(namespace, self.dest, values)

    class OverrideRootDir(argparse.Action):
        ''' Override system root directory '''
        def __call__(self, parser, namespace, values, option_string=None):
            full_path = os.path.abspath(values) + '/'
            libspm.ROOT_DIR = full_path
            libspm.LOCAL_DIR = full_path + 'var/local/spm'
            setattr(namespace, self.dest, values)

    class OverrideIgnore(argparse.Action):
        ''' Override ignored targets '''
        def __call__(self, parser, namespace, values, option_string=None):
            libspm.IGNORE = values.split(' ')
            setattr(namespace, self.dest, values)

    class OverrideMirror(argparse.Action):
        ''' Override usage of mirrors '''
        def __call__(self, parser, namespace, values, option_string=None):
            libspm.MIRROR = values
            setattr(namespace, self.dest, values)

    class OverrideExternal(argparse.Action):
        ''' Override usage of external fetchers '''
        def __call__(self, parser, namespace, values, option_string=None):
            libspm.EXTERNAL = values
            setattr(namespace, self.dest, values)

    class OverrideTimeout(argparse.Action):
        ''' Override connection timeout '''
        def __call__(self, parser, namespace, values, option_string=None):
            libspm.TIMEOUT = values
            setattr(namespace, self.dest, values)

    class OverrideChost(argparse.Action):
        ''' override CHOST '''
        def __call__(self, parser, namespace, values, option_string=None):
            libspm.CHOST = values
            setattr(namespace, self.dest, values)

    class OverrideCflags(argparse.Action):
        ''' Override CFLAGS '''
        def __call__(self, parser, namespace, values, option_string=None):
            libspm.CFLAGS = values
            setattr(namespace, self.dest, values)

    class OverrideCxxflags(argparse.Action):
        ''' Override CXXFLAGS '''
        def __call__(self, parser, namespace, values, option_string=None):
            libspm.CXXFLAGS = values
            setattr(namespace, self.dest, values)

    class OverrideCppflags(argparse.Action):
        ''' Override CPPFLAGS '''
        def __call__(self, parser, namespace, values, option_string=None):
            libspm.CPPFLAGS = values
            setattr(namespace, self.dest, values)

    class OverrideLdflags(argparse.Action):
        ''' Override LDFLAGS '''
        def __call__(self, parser, namespace, values, option_string=None):
            libspm.LDFLAGS = values
            setattr(namespace, self.dest, values)

    class OverrideMakeflags(argparse.Action):
        ''' Override MAKEFLAGS '''
        def __call__(self, parser, namespace, values, option_string=None):
            libspm.MAKEFLAGS = values
            setattr(namespace, self.dest, values)

    class OverrideMan(argparse.Action):
        ''' Override compression of manual pages '''
        def __call__(self, parser, namespace, values, option_string=None):
            libspm.COMPRESS_MAN = values
            setattr(namespace, self.dest, values)

    class OverrideBinaries(argparse.Action):
        ''' Override stripping of binaries '''
        def __call__(self, parser, namespace, values, option_string=None):
            libspm.STRIP_BINARIES = values
            setattr(namespace, self.dest, values)

    class OverrideShared(argparse.Action):
        ''' Override stripping of shared libraries '''
        def __call__(self, parser, namespace, values, option_string=None):
            libspm.STRIP_SHARED = values
            setattr(namespace, self.dest, values)

    class OverrideStatic(argparse.Action):
        ''' Override stripping of static libraries '''
        def __call__(self, parser, namespace, values, option_string=None):
            libspm.STRIP_STATIC = values
            setattr(namespace, self.dest, values)

    class OverrideRpath(argparse.Action):
        ''' Override stripping of RPATH '''
        def __call__(self, parser, namespace, values, option_string=None):
            libspm.STRIP_RPATH = values
            setattr(namespace, self.dest, values)

    class OverrideMissing(argparse.Action):
        ''' Override missing runtime dependencies failure '''
        def __call__(self, parser, namespace, values, option_string=None):
            libspm.IGNORE_MISSING = values
            setattr(namespace, self.dest, values)

    class OverrideConflicts(argparse.Action):
        ''' Override check for conflicts '''
        def __call__(self, parser, namespace, values, option_string=None):
            libspm.CONFLICTS = values
            setattr(namespace, self.dest, values)

    class OverrideBackup(argparse.Action):
        ''' Override backup of files '''
        def __call__(self, parser, namespace, values, option_string=None):
            libspm.BACKUP = values
            setattr(namespace, self.dest, values)

    class OverrideScripts(argparse.Action):
        ''' Override execution of pre/post scripts '''
        def __call__(self, parser, namespace, values, option_string=None):
            libspm.SCRIPTS = values
            setattr(namespace, self.dest, values)

    class OverrideTriggers(argparse.Action):
        ''' Override execution of triggers '''
        def __call__(self, parser, namespace, values, option_string=None):
            libspm.TRIGGERS = values
            setattr(namespace, self.dest, values)

    class OverrideOffline(argparse.Action):
        ''' Override offline mode '''
        def __call__(self, parser, namespace, values, option_string=None):
            libmisc.OFFLINE = True
            libspm.libmisc.OFFLINE = True
            libpackage.libmisc.OFFLINE = True
            libspm.libpackage.libmisc.OFFLINE = True
            setattr(namespace, self.dest, values)

    class OverrideDebug(argparse.Action):
        ''' Override printing of debug messages '''
        def __call__(self, parser, namespace, values, option_string=None):
            libmessage.DEBUG = True
            libspm.message.DEBUG = True
            setattr(namespace, self.dest, values)

    parser = argparse.ArgumentParser(prog='spm', \
        description='Source Package Manager')
    subparsers = parser.add_subparsers(dest='mode')

    if EUID == 0:
        repo_parser = subparsers.add_parser('repo')
        repo_parser.add_argument('-c', '--clean', action='store_true', \
            help='Purge repositories')
        repo_parser.add_argument('-s', '--sync', action='store_true', \
            help='Sync repositories')
        repo_parser.add_argument('-p', '--prune', action='store_true', \
            help='Prune old repositories')
        repo_parser.add_argument('-u', '--update', action='store_true', \
            help='Check repositories for updates')

    remote_parser = subparsers.add_parser('remote')
    remote_parser.add_argument('-n', '--name', action='store_true', \
        help='Show target name')
    remote_parser.add_argument('-v', '--version', action='store_true', \
        help='Show target version')
    remote_parser.add_argument('-d', '--description', action='store_true', \
        help='Show target description')
    remote_parser.add_argument('-D', '--depends', action='store_true', \
        help='Show target depends')
    remote_parser.add_argument('-m', '--makedepends', action='store_true', \
        help='Show target makedepends')
    remote_parser.add_argument('-c', '--checkdepends', action='store_true', \
        help='Show target checkdepends')
    remote_parser.add_argument('-s', '--sources', action='store_true', \
        help='Show target sources')
    remote_parser.add_argument('-o', '--options', action='store_true', \
        help='Show target options')
    remote_parser.add_argument('-b', '--backup', action='store_true', \
        help='Show target backups')
    remote_parser.add_argument('-p', '--plain', action='store_true', \
        help='Print in plain format')
    remote_parser.add_argument('PATTERN', type=str, \
        help='Pattern to search for in remote targets')

    if EUID == 0:
        source_parser = subparsers.add_parser('source')
        source_parser.add_argument('-C', '--clean', action='store_true', \
            help='Purge sources and compiled files of target')
        source_parser.add_argument('-p', '--prepare', action='store_true', \
            help='Prepare sources of target')
        source_parser.add_argument('-c', '--compile', action='store_true', \
            help='Compile sources of target')
        source_parser.add_argument('-k', '--check', action='store_true', \
            help='Check sources of target')
        source_parser.add_argument('-i', '--install', action='store_true', \
            help='Install compiled files of target')
        source_parser.add_argument('-m', '--merge', action='store_true', \
            help='Merge compiled files of target to system')
        source_parser.add_argument('-r', '--remove', action='store_true', \
            help='Remove compiled files of target from system')
        source_parser.add_argument('-D', '--depends', action='store_true', \
            help='Consider dependency targets')
        source_parser.add_argument('-R', '--reverse', action='store_true', \
            help='Consider reverse dependency targets')
        source_parser.add_argument('-u', '--update', action='store_true', \
            help='Apply actions only if update is available')
        source_parser.add_argument('-a', '--automake', action='store_true', \
            help='Short for clean, prepare, compile, install and merge')
        source_parser.add_argument('TARGETS', nargs='+', type=str, \
            help='Targets to apply actions on')

    local_parser = subparsers.add_parser('local')
    local_parser.add_argument('-n', '--name', action='store_true', \
        help='Show target name')
    local_parser.add_argument('-v', '--version', action='store_true', \
        help='Show target version')
    local_parser.add_argument('-d', '--description', action='store_true', \
        help='Show target description')
    local_parser.add_argument('-D', '--depends', action='store_true', \
        help='Show target depends')
    local_parser.add_argument('-r', '--reverse', action='store_true', \
        help='Show target reverse depends')
    local_parser.add_argument('-s', '--size', action='store_true', \
        help='Show target size')
    local_parser.add_argument('-f', '--footprint', action='store_true', \
        help='Show target footprint')
    local_parser.add_argument('-p', '--plain', action='store_true', \
        help='Print in plain format')
    local_parser.add_argument('PATTERN', type=str, \
        help='Pattern to search for in local targets')

    who_parser = subparsers.add_parser('who')
    who_parser.add_argument('-p', '--plain', action='store_true', \
        help='Print in plain format')
    who_parser.add_argument('PATTERN', type=str, \
        help='Pattern to search for in local targets')

    parser.add_argument('--cache', type=str, action=OverrideCacheDir, \
        help='Change cache directory')
    parser.add_argument('--build', type=str, action=OverrideBuildDir, \
        help='Change build directory')
    parser.add_argument('--root', type=str, action=OverrideRootDir, \
        help='Change system root directory')
    parser.add_argument('--ignore', type=str, action=OverrideIgnore, \
        help='Change ignored targets')
    parser.add_argument('--mirror', type=ast.literal_eval, \
        action=OverrideMirror, help='Set whether to use mirrors')
    parser.add_argument('--timeout', type=int, action=OverrideTimeout, \
        help='Set the connection timeout')
    parser.add_argument('--external', type=ast.literal_eval, \
        action=OverrideExternal, help='Set whether to use external fetcher')
    parser.add_argument('--chost', type=str, action=OverrideChost, \
        help='Change CHOST')
    parser.add_argument('--cflags', type=str, action=OverrideCflags, \
        help='Change CFLAGS')
    parser.add_argument('--cxxflags', type=str, action=OverrideCxxflags, \
        help='Change CXXFLAGS')
    parser.add_argument('--cppflags', type=str, action=OverrideCppflags, \
        help='Change CPPFLAGS')
    parser.add_argument('--ldflags', type=str, action=OverrideLdflags, \
        help='Change LDFLAGS')
    parser.add_argument('--makeflags', type=str, action=OverrideMakeflags, \
        help='Change MAKEFLAGS')
    parser.add_argument('--man', type=ast.literal_eval, action=OverrideMan, \
        help='Set whether to compress man pages')
    parser.add_argument('--binaries', type=ast.literal_eval, \
        action=OverrideBinaries, help='Set whether to strip binaries')
    parser.add_argument('--shared', type=ast.literal_eval, \
        action=OverrideShared, help='Set whether to strip shared libraries')
    parser.add_argument('--static', type=ast.literal_eval, \
        action=OverrideStatic, help='Set whether to strip static libraries')
    parser.add_argument('--rpath', type=ast.literal_eval, \
        action=OverrideRpath, help='Set whether to strip RPATH')
    parser.add_argument('--missing', type=ast.literal_eval, \
        action=OverrideMissing, \
        help='Set whether to ignore missing runtime dependencies')
    parser.add_argument('--conflicts', type=ast.literal_eval, \
        action=OverrideConflicts, help='Set whether to check for conflicts')
    parser.add_argument('--backup', type=ast.literal_eval, \
        action=OverrideBackup, help='Set whether to backup files')
    parser.add_argument('--scripts', type=ast.literal_eval, \
        action=OverrideScripts, help='Set whether to execute pre/post script')
    parser.add_argument('--triggers', type=ast.literal_eval, \
        action=OverrideTriggers, help='Set whether to execute triggers')
    parser.add_argument('--offline', nargs=0, action=OverrideOffline, \
        help='Enable offline mode')
    parser.add_argument('--debug', nargs=0, action=OverrideDebug, \
        help='Enable debug messages')
    parser.add_argument('--version', action='version', \
        version='Source Package Manager v' + app_version, \
        help='Show SPM version and exit')

    ARGS = parser.parse_args()

    if ARGS.mode == 'repo':
        message.info('Runtime information')
        message.sub_info('CACHE_DIR', libspm.CACHE_DIR)
        for repository in libspm.REPOSITORIES:
            message.sub_info('REPOSITORY', repository)
        message.info('Poking repositories...')
        m = libspm.Repo(libspm.REPOSITORIES, ARGS.clean, \
                ARGS.sync, ARGS.update, ARGS.prune)
        m.main()

    elif ARGS.mode == 'remote':
        if not ARGS.plain:
            message.info('Runtime information')
            message.sub_info('PATTERN', ARGS.PATTERN)
            message.info('Poking remotes...')
        m = libspm.Remote(ARGS.PATTERN, ARGS.name, ARGS.version, \
                ARGS.description, ARGS.depends, ARGS.makedepends, \
                ARGS.checkdepends, ARGS.sources, ARGS.options, \
                ARGS.backup, ARGS.plain)
        m.main()

    elif ARGS.mode == 'source':
        if 'world' in ARGS.TARGETS:
            position = ARGS.TARGETS.index('world')
            ARGS.TARGETS[position:position+1] = \
                database.local_all(basename=True)

        for alias in database.remote_aliases():
            if alias in ARGS.TARGETS:
                position = ARGS.TARGETS.index(alias)
                ARGS.TARGETS[position:position+1] = \
                    database.remote_alias(alias)

        message.info('Runtime information')
        message.sub_info('CACHE_DIR', libspm.CACHE_DIR)
        message.sub_info('BUILD_DIR', libspm.BUILD_DIR)
        message.sub_info('ROOT_DIR', libspm.ROOT_DIR)
        message.sub_info('IGNORE', libspm.IGNORE)
        message.sub_info('MIRROR', libspm.MIRROR)
        message.sub_info('TIMEOUT', libspm.TIMEOUT)
        message.sub_info('EXTERNAL', libspm.EXTERNAL)
        message.sub_info('CHOST', libspm.CHOST)
        message.sub_info('CFLAGS', libspm.CFLAGS)
        message.sub_info('CXXFLAGS', libspm.CXXFLAGS)
        message.sub_info('CPPFLAGS', libspm.CPPFLAGS)
        message.sub_info('LDFLAGS', libspm.LDFLAGS)
        message.sub_info('MAKEFLAGS', libspm.MAKEFLAGS)
        message.sub_info('COMPRESS_MAN', libspm.COMPRESS_MAN)
        message.sub_info('STRIP_BINARIES', libspm.STRIP_BINARIES)
        message.sub_info('STRIP_SHARED', libspm.STRIP_SHARED)
        message.sub_info('STRIP_STATIC', libspm.STRIP_STATIC)
        message.sub_info('STRIP_RPATH', libspm.STRIP_RPATH)
        message.sub_info('IGNORE_MISSING', libspm.IGNORE_MISSING)
        message.sub_info('CONFLICTS', libspm.CONFLICTS)
        message.sub_info('BACKUP', libspm.BACKUP)
        message.sub_info('SCRIPTS', libspm.SCRIPTS)
        message.sub_info('TARGETS', ARGS.TARGETS)
        message.info('Poking sources...')
        if ARGS.automake:
            ARGS.clean = True
            ARGS.prepare = True
            ARGS.compile = True
            ARGS.install = True
            ARGS.merge = True
        m = libspm.Source(ARGS.TARGETS, ARGS.clean, ARGS.prepare, \
                ARGS.compile, ARGS.check, ARGS.install, ARGS.merge, \
                ARGS.remove, ARGS.depends, ARGS.reverse, ARGS.update)
        m.main()

    elif ARGS.mode == 'local':
        if not ARGS.plain:
            message.info('Runtime information')
            message.sub_info('PATTERN', ARGS.PATTERN)
            message.info('Poking locals...')
        m = libspm.Local(ARGS.PATTERN, ARGS.name, ARGS.version, \
                ARGS.description, ARGS.depends, ARGS.reverse, \
                ARGS.size, ARGS.footprint, ARGS.plain)
        m.main()

    elif ARGS.mode == 'who':
        if not ARGS.plain:
            message.info('Runtime information')
            message.sub_info('PATTERN', ARGS.PATTERN)
            message.info('Poking databases...')
        m = libspm.Who(ARGS.PATTERN, ARGS.plain)
        m.main()

except ConfigParser.Error as detail:
    message.critical('CONFIGPARSER', detail)
    sys.exit(3)
except subprocess.CalledProcessError as detail:
    message.critical('SUBPROCESS', detail)
    sys.exit(4)
except urllib2.HTTPError as detail:
    message.critical('URLLIB', detail)
    sys.exit(5)
except tarfile.TarError as detail:
    message.critical('TARFILE', detail)
    sys.exit(6)
except zipfile.BadZipfile as detail:
    message.critical('ZIPFILE', detail)
    sys.exit(7)
except shutil.Error as detail:
    message.critical('SHUTIL', detail)
    sys.exit(8)
except OSError as detail:
    message.critical('OS', detail)
    sys.exit(9)
except IOError as detail:
    message.critical('IO', detail)
    sys.exit(10)
except re.error as detail:
    message.critical('REGEXP', detail)
    sys.exit(11)
except KeyboardInterrupt:
    message.critical('Interrupt signal received')
    sys.exit(12)
except SystemExit:
    sys.exit(2)
except Exception as detail:
    message.critical('Unexpected error', detail)
    sys.exit(1)
#finally:
#    raise
