#!/usr/bin/python2

import sys, os, argparse, ast, subprocess, tarfile, zipfile, shutil, re
if sys.version < '3':
    import ConfigParser as configparser
    from urllib2 import HTTPError
    from urllib2 import URLError
else:
    import configparser
    from urllib.error import HTTPError
    from urllib.error import URLError

import libmessage
message = libmessage.Message()

app_version = "1.10.1 (8303906)"


retvalue = 0
try:
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

    class OverrideGpgDir(argparse.Action):
        ''' Override gpg home directory '''
        def __call__(self, parser, namespace, values, option_string=None):
            libspm.GPG_DIR = values
            setattr(namespace, self.dest, values)

    class OverrideShell(argparse.Action):
        ''' Override which shell to use '''
        def __call__(self, parser, namespace, values, option_string=None):
            libspm.SHELL = values
            setattr(namespace, self.dest, values)

    class OverrideIgnore(argparse.Action):
        ''' Override ignored targets '''
        def __call__(self, parser, namespace, values, option_string=None):
            libspm.IGNORE = values.split(' ')
            setattr(namespace, self.dest, values)

    class OverrideNotify(argparse.Action):
        ''' Override database watching '''
        def __call__(self, parser, namespace, values, option_string=None):
            libspm.NOTIFY = values
            setattr(namespace, self.dest, values)

    class OverrideOffline(argparse.Action):
        ''' Override offline mode '''
        def __call__(self, parser, namespace, values, option_string=None):
            libspm.OFFLINE = values
            setattr(namespace, self.dest, values)

    class OverrideMirror(argparse.Action):
        ''' Override usage of mirrors '''
        def __call__(self, parser, namespace, values, option_string=None):
            libspm.MIRROR = values
            setattr(namespace, self.dest, values)

    class OverrideTimeout(argparse.Action):
        ''' Override connection timeout '''
        def __call__(self, parser, namespace, values, option_string=None):
            libspm.TIMEOUT = values
            setattr(namespace, self.dest, values)

    class OverrideVerify(argparse.Action):
        ''' Override signature verification of downloads '''
        def __call__(self, parser, namespace, values, option_string=None):
            libspm.VERIFY = values
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

    class OverridePurge(argparse.Action):
        ''' Override paths to be purged '''
        def __call__(self, parser, namespace, values, option_string=None):
            libspm.PURGE_PATHS = values
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

    class OverrideMissing(argparse.Action):
        ''' Override missing runtime dependencies failure '''
        def __call__(self, parser, namespace, values, option_string=None):
            libspm.IGNORE_MISSING = values
            setattr(namespace, self.dest, values)

    class OverridePermissions(argparse.Action):
        ''' Override permissions check '''
        def __call__(self, parser, namespace, values, option_string=None):
            libspm.IGNORE_PERMISSIONS = values
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

    class OverrideDebug(argparse.Action):
        ''' Override printing of debug messages '''
        def __call__(self, parser, namespace, values, option_string=None):
            message.DEBUG = True
            libspm.message.DEBUG = True
            setattr(namespace, self.dest, values)

    parser = argparse.ArgumentParser(prog='spm', \
        description='Source Package Manager', \
        epilog='NOTE: Some features are available only to the root user.')
    subparsers = parser.add_subparsers(dest='mode')

    repo_parser = subparsers.add_parser('repo', \
        help='Clean, sync, prune and/or check repositories for updates')
    repo_parser.add_argument('-c', '--clean', action='store_true', \
        help='Purge repositories')
    repo_parser.add_argument('-s', '--sync', action='store_true', \
        help='Sync repositories')
    repo_parser.add_argument('-p', '--prune', action='store_true', \
        help='Prune old repositories')
    repo_parser.add_argument('-u', '--update', action='store_true', \
        help='Check repositories for updates')
    repo_parser.add_argument('-a', '--all', action='store_true', \
        help='Short for clean, sync, prune and update')

    remote_parser = subparsers.add_parser('remote', \
        help='Get remote targets metadata')
    remote_parser.add_argument('-n', '--name', action='store_true', \
        help='Show target name')
    remote_parser.add_argument('-v', '--version', action='store_true', \
        help='Show target version')
    remote_parser.add_argument('-r', '--release', action='store_true', \
        help='Show target release')
    remote_parser.add_argument('-d', '--description', action='store_true', \
        help='Show target description')
    remote_parser.add_argument('-D', '--depends', action='store_true', \
        help='Show target depends')
    remote_parser.add_argument('-m', '--makedepends', action='store_true', \
        help='Show target makedepends')
    remote_parser.add_argument('-O', '--optdepends', action='store_true', \
        help='Show target optdepends')
    remote_parser.add_argument('-c', '--checkdepends', action='store_true', \
        help='Show target checkdepends')
    remote_parser.add_argument('-s', '--sources', action='store_true', \
        help='Show target sources')
    remote_parser.add_argument('-k', '--pgpkeys', action='store_true', \
        help='Show target PGP keys')
    remote_parser.add_argument('-o', '--options', action='store_true', \
        help='Show target options')
    remote_parser.add_argument('-b', '--backup', dest='remote_backup', \
        action='store_true', help='Show target backups')
    remote_parser.add_argument('-p', '--plain', action='store_true', \
        help='Print in plain format')
    remote_parser.add_argument('PATTERN', type=str, \
        help='Pattern to search for in remote targets')

    source_parser = subparsers.add_parser('source', \
        help='Build software from source code')
    source_parser.add_argument('-C', '--clean', action='store_true', \
        help='Purge sources and compiled files of target')
    source_parser.add_argument('-f', '--fetch', action='store_true', \
        help='Fetch sources of target')
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
        help='Short for clean, fetch, prepare, compile, install and merge')
    source_parser.add_argument('TARGETS', nargs='+', type=str, \
        help='Targets to apply actions on')

    local_parser = subparsers.add_parser('local', \
        help='Get local targets metadata')
    local_parser.add_argument('-n', '--name', action='store_true', \
        help='Show target name')
    local_parser.add_argument('-v', '--version', action='store_true', \
        help='Show target version')
    # FIXME: on the next major release swap -R and -r
    local_parser.add_argument('-R', '--release', action='store_true', \
        help='Show target release')
    local_parser.add_argument('-d', '--description', action='store_true', \
        help='Show target description')
    local_parser.add_argument('-D', '--depends', action='store_true', \
        help='Show target depends')
    local_parser.add_argument('-O', '--optdepends', action='store_true', \
        help='Show target optdepends')
    local_parser.add_argument('-A', '--autodepends', action='store_true', \
        help='Show target autodepends')
    local_parser.add_argument('-r', '--reverse', action='store_true', \
        help='Show target reverse depends')
    local_parser.add_argument('-s', '--size', action='store_true', \
        help='Show target size')
    local_parser.add_argument('-f', '--footprint', action='store_true', \
        help='Show target footprint')
    local_parser.add_argument('-b', '--backup', action='store_true', \
        help='Show target backup')
    local_parser.add_argument('-p', '--plain', action='store_true', \
        help='Print in plain format')
    local_parser.add_argument('PATTERN', type=str, \
        help='Pattern to search for in local targets')

    who_parser = subparsers.add_parser('who', \
        help='Get owner of files via regular expression')
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
    parser.add_argument('--gpg', type=str, action=OverrideGpgDir, \
        help='Change GnuPG home directory')
    parser.add_argument('--shell', type=str, action=OverrideShell, \
        help='Change which shell to use')
    parser.add_argument('--ignore', type=str, action=OverrideIgnore, \
        help='Change ignored targets')
    parser.add_argument('--notify', type=ast.literal_eval, \
        action=OverrideNotify, choices=[True, False], \
        help='Set whether to use inotify to monitor databases')
    parser.add_argument('--offline', type=ast.literal_eval, \
        action=OverrideOffline, choices=[True, False], \
        help='Set whether to use offline mode')
    parser.add_argument('--mirror', type=ast.literal_eval, \
        action=OverrideMirror, choices=[True, False], \
        help='Set whether to use mirrors')
    parser.add_argument('--timeout', type=int, action=OverrideTimeout, \
        help='Set the connection timeout')
    parser.add_argument('--verify', type=ast.literal_eval, \
        action=OverrideVerify, choices=[True, False], \
        help='Set whether to verify downloads')
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
    parser.add_argument('--purge', type=str, action=OverridePurge, \
        help='Change PURGE_PATHS')
    parser.add_argument('--man', type=ast.literal_eval, action=OverrideMan, \
        choices=[True, False], help='Set whether to compress man pages')
    parser.add_argument('--binaries', type=ast.literal_eval, \
        action=OverrideBinaries, choices=[True, False], \
        help='Set whether to strip binaries')
    parser.add_argument('--shared', type=ast.literal_eval, \
        action=OverrideShared, choices=[True, False], \
        help='Set whether to strip shared libraries')
    parser.add_argument('--static', type=ast.literal_eval, \
        action=OverrideStatic, choices=[True, False], \
        help='Set whether to strip static libraries')
    parser.add_argument('--missing', type=ast.literal_eval, \
        action=OverrideMissing, choices=[True, False], \
        help='Set whether to ignore missing runtime dependencies')
    parser.add_argument('--permissions', type=ast.literal_eval, \
        action=OverridePermissions, choices=[True, False], \
        help='Set whether to ignore permissions of files')
    parser.add_argument('--conflicts', type=ast.literal_eval, \
        action=OverrideConflicts, choices=[True, False], \
        help='Set whether to check for conflicts')
    parser.add_argument('--backup', type=ast.literal_eval, \
        action=OverrideBackup, choices=[True, False], \
        help='Set whether to backup files')
    parser.add_argument('--scripts', type=ast.literal_eval, \
        action=OverrideScripts, choices=[True, False], \
        help='Set whether to execute pre/post script')
    parser.add_argument('--triggers', type=ast.literal_eval, \
        action=OverrideTriggers, choices=[True, False], \
        help='Set whether to execute triggers')
    parser.add_argument('--debug', nargs=0, action=OverrideDebug, \
        help='Enable debug messages')
    parser.add_argument('--version', action='version', \
        version='Source Package Manager v%s' % app_version, \
        help='Show SPM version and exit')

    ARGS = parser.parse_args()
    if not sys.stdin.isatty() and ARGS.TARGETS == ['-']:
        ARGS.TARGETS = sys.stdin.read().split()

    if ARGS.mode == 'repo':
        if ARGS.all:
            ARGS.clean = True
            ARGS.sync = True
            ARGS.update = True
            ARGS.prune = True

        message.info('Runtime information')
        message.sub_info('CLEAN', ARGS.clean)
        message.sub_info('SYNC', ARGS.sync)
        message.sub_info('UPDATE', ARGS.update)
        message.sub_info('PRUNE', ARGS.prune)
        message.sub_info('CACHE_DIR', libspm.CACHE_DIR)
        message.sub_info('REPOSITORIES', libspm.REPOSITORIES)
        message.info('Poking repositories...')
        m = libspm.Repo(libspm.REPOSITORIES, ARGS.clean, \
                ARGS.sync, ARGS.update, ARGS.prune)
        m.main()

    elif ARGS.mode == 'remote':
        if not ARGS.plain:
            message.info('Runtime information')
            message.sub_info('NAME', ARGS.name)
            message.sub_info('VERSION', ARGS.version)
            message.sub_info('RELEASE', ARGS.release)
            message.sub_info('DESCRIPTION', ARGS.description)
            message.sub_info('DEPENDS', ARGS.depends)
            message.sub_info('MAKEDEPENDS', ARGS.makedepends)
            message.sub_info('OPTDEPENDS', ARGS.optdepends)
            message.sub_info('CHECKDEPENDS', ARGS.checkdepends)
            message.sub_info('SOURCES', ARGS.sources)
            message.sub_info('PGPKEYS', ARGS.pgpkeys)
            message.sub_info('OPTIONS', ARGS.options)
            message.sub_info('BACKUP', ARGS.remote_backup)
            message.sub_info('PATTERN', ARGS.PATTERN)
            message.info('Poking remotes...')
        m = libspm.Remote(ARGS.PATTERN, ARGS.name, ARGS.version, \
                ARGS.release, ARGS.description, ARGS.depends, \
                ARGS.makedepends, ARGS.optdepends, ARGS.checkdepends, \
                ARGS.sources, ARGS.pgpkeys, ARGS.options, \
                ARGS.remote_backup, ARGS.plain)
        m.main()

    elif ARGS.mode == 'source':
        message.info('Runtime information')
        message.sub_info('CACHE_DIR', libspm.CACHE_DIR)
        message.sub_info('BUILD_DIR', libspm.BUILD_DIR)
        message.sub_info('ROOT_DIR', libspm.ROOT_DIR)
        message.sub_info('GPG_DIR', libspm.GPG_DIR)
        message.sub_info('SHELL', libspm.SHELL)
        message.sub_info('IGNORE', libspm.IGNORE)
        message.sub_info('NOTIFY', libspm.NOTIFY)
        message.sub_info('OFFLINE', libspm.OFFLINE)
        message.sub_info('MIRROR', libspm.MIRROR)
        message.sub_info('TIMEOUT', libspm.TIMEOUT)
        message.sub_info('VERIFY', libspm.VERIFY)
        message.sub_info('CHOST', libspm.CHOST)
        message.sub_info('CFLAGS', libspm.CFLAGS)
        message.sub_info('CXXFLAGS', libspm.CXXFLAGS)
        message.sub_info('CPPFLAGS', libspm.CPPFLAGS)
        message.sub_info('LDFLAGS', libspm.LDFLAGS)
        message.sub_info('MAKEFLAGS', libspm.MAKEFLAGS)
        message.sub_info('PURGE_PATHS', libspm.PURGE_PATHS)
        message.sub_info('COMPRESS_MAN', libspm.COMPRESS_MAN)
        message.sub_info('STRIP_BINARIES', libspm.STRIP_BINARIES)
        message.sub_info('STRIP_SHARED', libspm.STRIP_SHARED)
        message.sub_info('STRIP_STATIC', libspm.STRIP_STATIC)
        message.sub_info('IGNORE_MISSING', libspm.IGNORE_MISSING)
        message.sub_info('IGNORE_PERMISSIONS', libspm.IGNORE_PERMISSIONS)
        message.sub_info('CONFLICTS', libspm.CONFLICTS)
        message.sub_info('BACKUP', libspm.BACKUP)
        message.sub_info('SCRIPTS', libspm.SCRIPTS)
        message.sub_info('TARGETS', ARGS.TARGETS)
        message.info('Poking sources...')
        if ARGS.automake:
            ARGS.clean = True
            ARGS.fetch = True
            ARGS.prepare = True
            ARGS.compile = True
            ARGS.install = True
            ARGS.merge = True
        m = libspm.Source(ARGS.TARGETS, ARGS.clean, ARGS.fetch, \
                ARGS.prepare, ARGS.compile, ARGS.check, ARGS.install, \
                ARGS.merge, ARGS.remove, ARGS.depends, ARGS.reverse, \
                ARGS.update)
        m.main()

    elif ARGS.mode == 'local':
        if not ARGS.plain:
            message.info('Runtime information')
            message.sub_info('NAME', ARGS.name)
            message.sub_info('VERSION', ARGS.version)
            message.sub_info('RELEASE', ARGS.release)
            message.sub_info('DESCRIPTION', ARGS.description)
            message.sub_info('DEPENDS', ARGS.depends)
            message.sub_info('OPTDEPENDS', ARGS.optdepends)
            message.sub_info('AUTODEPENDS', ARGS.autodepends)
            message.sub_info('REVERSE', ARGS.reverse)
            message.sub_info('SIZE', ARGS.size)
            message.sub_info('FOOTPRINT', ARGS.footprint)
            message.sub_info('BACKUP', ARGS.backup)
            message.sub_info('PATTERN', ARGS.PATTERN)
            message.info('Poking locals...')
        m = libspm.Local(ARGS.PATTERN, ARGS.name, ARGS.version, \
                ARGS.release, ARGS.description, ARGS.depends, \
                ARGS.optdepends, ARGS.autodepends, ARGS.reverse, \
                ARGS.size, ARGS.footprint, ARGS.backup, ARGS.plain)
        m.main()

    elif ARGS.mode == 'who':
        if 'wantscookie' in sys.argv:
            print(libspm.wantscookie)
            sys.exit(2)
        if not ARGS.plain:
            message.info('Runtime information')
            message.sub_info('PATTERN', ARGS.PATTERN)
            message.info('Poking local...')
        m = libspm.Who(ARGS.PATTERN, ARGS.plain)
        m.main()

    if not ARGS.mode and sys.version > '2':
        parser.print_help()

except configparser.Error as detail:
    message.critical('CONFIGPARSER', detail)
    retvalue = 3
except subprocess.CalledProcessError as detail:
    message.critical('SUBPROCESS', detail)
    retvalue = 4
except (HTTPError, URLError) as detail:
    if hasattr(detail, 'url') and hasattr(detail, 'code'):
        # misc.fetch() provides the URL, HTTPError provides the code
        message.critical('URLLIB', "%s: '%s' (%s)" % (detail.reason, detail.url, \
            detail.code))
    elif hasattr(detail, 'url'):
        message.critical('URLLIB', "%s: '%s'" % (detail.reason, detail.url))
    else:
        message.critical('URLLIB', detail)
    retvalue = 5
except tarfile.TarError as detail:
    message.critical('TARFILE', detail)
    retvalue = 6
except zipfile.BadZipfile as detail:
    message.critical('ZIPFILE', detail)
    retvalue = 7
except shutil.Error as detail:
    message.critical('SHUTIL', detail)
    retvalue = 8
except OSError as detail:
    message.critical('OS', detail)
    retvalue = 9
except IOError as detail:
    message.critical('IO', detail)
    retvalue = 10
except re.error as detail:
    message.critical('REGEXP', detail)
    retvalue = 11
except KeyboardInterrupt:
    message.critical('Interrupt signal received')
    retvalue = 12
except SystemExit:
    retvalue = 2
except Exception as detail:
    message.critical('Unexpected error', detail)
    retvalue = 1
finally:
    sys.exit(retvalue)
