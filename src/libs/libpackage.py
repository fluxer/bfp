#!/bin/python2

'''
A module for package management with plain-text format database

Database() is the core of Source Package Manager, it provides various methods
to get information about packages installed and otherwise. The methods prefixed
with "local" deal with metadata of software instaleld on the system, "remote"
methods provide info for software available from repositories with build
recipes in the SRCBUILD format.

SRCBUILD() is Source Package Manager recipes (SRCBUILDs) parser.

'''

import os, sys, re, shlex, types
from distutils.version import LooseVersion

import libmisc
misc = libmisc.Misc()
notify = libmisc.Inotify()


class Database(object):
    ''' Get information about packages '''
    def __init__(self):
        self.ROOT_DIR = '/'
        self.CACHE_DIR = '/var/cache/spm'
        self.REMOTE_CACHE = {}
        self.LOCAL_DIR = self.ROOT_DIR + 'var/local/spm'
        self.LOCAL_CACHE = {}
        self.IGNORE = []

    def local_footprint(self, target):
        ''' DEPRECATED: Returns files of target, use local_metadata(target, 'footprint') '''
        if misc.python2:
            misc.typecheck(target, (types.StringTypes))

        return self.local_metadata(target, 'footprint')

    def remote_groups(self, basename=True):
        ''' DEPRECATED: Returns groups in the repositories '''
        if misc.python2:
            misc.typecheck(basename, (types.BooleanType))

        groups = []
        for sdir in misc.list_dirs(os.path.join(self.CACHE_DIR, \
            'repositories')):
            if not os.path.isfile(os.path.join(sdir, 'SRCBUILD')) \
                and not '/.git/' in sdir and not sdir.endswith('.git'):
                if basename:
                    groups.append(os.path.basename(sdir))
                else:
                    groups.append(sdir)
        return sorted(groups)

    def _notifiers_setup(self):
        ''' Setup inotify watcher for database changes '''
        reposdir = os.path.join(self.CACHE_DIR, 'repositories')
        if os.path.isdir(reposdir):
            notify.watch_add(reposdir)
        if os.path.isdir(self.LOCAL_DIR):
            notify.watch_add(self.LOCAL_DIR)

    def _build_local_cache(self):
        ''' Build internal local database cache '''
        self.LOCAL_CACHE = {}
        for sdir in misc.list_dirs(self.LOCAL_DIR):
            metadata = os.path.join(sdir, 'metadata')
            footprint = os.path.join(sdir, 'footprint')
            if os.path.isfile(metadata) and os.path.isfile(footprint):
                self.LOCAL_CACHE[sdir] = {
                    'version': self._local_metadata(metadata, 'version'),
                    'release': self._local_metadata(metadata, 'release'),
                    'description': self._local_metadata(metadata, 'description'),
                    'depends': self._local_metadata(metadata, 'depends').split(),
                    'size': self._local_metadata(metadata, 'size'),
                    'footprint': misc.file_read(footprint)
                }
        # print(sys.getsizeof(self.LOCAL_CACHE))

    def _build_remote_cache(self):
        ''' Build internal remote database cache '''
        self.REMOTE_CACHE = {}
        for sdir in misc.list_dirs(os.path.join(self.CACHE_DIR, 'repositories')):
            srcbuild = os.path.join(sdir, 'SRCBUILD')
            if os.path.isfile(srcbuild):
                parser = SRCBUILD(srcbuild)
                self.REMOTE_CACHE[sdir] = {
                    'version': parser.version,
                    'release': parser.release,
                    'description': parser.description,
                    'depends': parser.depends,
                    'makedepends': parser.makedepends,
                    'checkdepends': parser.checkdepends,
                    'sources': parser.sources,
                    'pgpkeys': parser.pgpkeys,
                    'options': parser.options,
                    'backup': parser.backup
                }
        # print(sys.getsizeof(self.REMOTE_CACHE))

    def _local_metadata(self, smetadata, skey):
        ''' Returns metadata of local target '''
        if misc.python2:
            misc.typecheck(smetadata, (types.StringTypes))
            misc.typecheck(skey, (types.StringTypes))

        key = misc.string_encode('%s=' % skey)
        for line in misc.file_readlines(smetadata):
            if line.startswith(key):
                return misc.string_encode(line).split('=')[1].strip()
        # for backwards compatibility and making release optional
        if skey == 'release':
            return '1'

    def remote_all(self, basename=False):
        ''' Returns directories of all remote (repository) targets '''
        if misc.python2:
            misc.typecheck(basename, (types.BooleanType))

        # rebuild cache on demand
        recache = False
        for wd, mask, cookie, name in notify.event_read():
            recache = True
        if not self.REMOTE_CACHE or recache:
            self._notifiers_setup()
            self._build_remote_cache()

        if basename:
            lremote = []
            for target in self.REMOTE_CACHE:
                lremote.append(os.path.basename(target))
            return sorted(lremote)
        return sorted(list(self.REMOTE_CACHE.keys()))

    def local_all(self, basename=False):
        ''' Returns directories of all local (installed) targets '''
        if misc.python2:
            misc.typecheck(basename, (types.BooleanType))

        # rebuild cache on demand
        recache = False
        for wd, mask, cookie, name in notify.event_read():
            recache = True
        if not self.LOCAL_CACHE or recache:
            self._notifiers_setup()
            self._build_local_cache()

        if basename:
            llocal = []
            for target in self.LOCAL_CACHE:
                llocal.append(os.path.basename(target))
            return sorted(llocal)
        return sorted(list(self.LOCAL_CACHE.keys()))

    def local_search(self, target):
        ''' Returns full path to directory matching target '''
        if misc.python2:
            misc.typecheck(target, (types.StringTypes))

        for ltarget in self.local_all():
            if ltarget == target or ltarget.endswith('/%s' % target):
                return ltarget
        return None

    def remote_search(self, target):
        ''' Returns full path to directory matching target '''
        if misc.python2:
            misc.typecheck(target, (types.StringTypes))

        if os.path.isfile(os.path.join(target, 'SRCBUILD')):
            return target

        for rtarget in self.remote_all():
            if rtarget == target or rtarget.endswith('/%s' % target):
                return rtarget
        return None

    def local_belongs(self, sfile, exact=False, escape=True, ignore=None):
        ''' Searches for match of file in all local targets '''
        if misc.python2:
            misc.typecheck(sfile, (types.StringTypes))
            misc.typecheck(exact, (types.BooleanType))
            misc.typecheck(escape, (types.BooleanType))
            misc.typecheck(ignore, (types.NoneType, types.StringTypes))

        match = []
        # it may not exists if bootstrapping
        if not os.path.isdir(self.LOCAL_DIR):
            return match

        for local in self.local_all(basename=True):
            if local == ignore:
                continue

            if misc.string_search(sfile, self.local_metadata(local, 'footprint'), \
                exact=exact, escape=escape):
                match.append(local)
        return match

    def remote_mdepends(self, target, checked=None, cdepends=False, mdepends=True):
        ''' Returns missing build dependencies of target '''
        if misc.python2:
            misc.typecheck(target, (types.StringTypes))
            misc.typecheck(checked, (types.NoneType, types.ListType))
            misc.typecheck(cdepends, (types.BooleanType))
            misc.typecheck(mdepends, (types.BooleanType))

        missing = []
        build_depends = []
        if checked is None:
            checked = []

        # respect ignored targets to avoid building
        # dependencies when not needed
        if target in self.IGNORE:
            return missing

        build_depends.extend(self.remote_metadata(target, 'depends'))
        if mdepends:
            build_depends.extend(self.remote_metadata(target, 'makedepends'))
        if cdepends:
            build_depends.extend(self.remote_metadata(target, 'checkdepends'))

        for dependency in build_depends:
            if checked and dependency in checked:
                continue

            if not dependency in missing \
                and not self.local_uptodate(dependency):
                checked.append(target)
                missing.extend(self.remote_mdepends(dependency, checked, cdepends))
                missing.append(dependency)
                checked.append(dependency)
        return missing

    def local_rdepends(self, target, indirect=False, checked=None):
        ''' Returns reverse dependencies of target '''
        if misc.python2:
            misc.typecheck(target, (types.StringTypes))
            misc.typecheck(indirect, (types.BooleanType))
            misc.typecheck(target, (types.NoneType, types.StringTypes))

        reverse = []
        if checked is None:
            checked = []

        basename = os.path.basename(target)
        for installed in self.local_all(basename=True):
            # respect ignored targets
            if installed in self.IGNORE:
                continue

            if checked and installed in checked:
                continue

            if basename in self.local_metadata(installed, 'depends'):
                checked.append(basename)
                if indirect:
                    reverse.extend(self.local_rdepends(installed, \
                        True, checked))
                reverse.append(installed)
                checked.append(installed)
        return reverse

    def local_metadata(self, target, key):
        ''' Returns metadata of local target '''
        if misc.python2:
            misc.typecheck(target, (types.StringTypes))
            misc.typecheck(key, (types.StringTypes))

        match = self.local_search(target)
        if match:
            return self.LOCAL_CACHE[match][key]

    def local_uptodate(self, target):
        ''' Returns True if target is up-to-date and False otherwise '''
        if misc.python2:
            misc.typecheck(target, (types.StringTypes))

        # if remote target is passed and it's a directory not a base name
        # then the local target will be invalid and local_version will equal
        # None, thus the base name is used to find the local target version
        base = os.path.basename(target)
        local_version = self.local_metadata(base, 'version')
        local_release = self.local_metadata(base, 'release')
        remote_version = self.remote_metadata(target, 'version')
        remote_release = self.remote_metadata(target, 'release')

        # LooseVersion does not handle None
        if not remote_version or not local_version:
            return False

        if LooseVersion(local_version) < LooseVersion(remote_version):
            return False
        elif local_release < remote_release:
            return False
        return True

    def remote_metadata(self, target, key):
        ''' Returns metadata of remote target '''
        if misc.python2:
            misc.typecheck(target, (types.StringTypes))
            misc.typecheck(key, (types.StringTypes))

        if os.path.isfile(os.path.join(target, 'SRCBUILD')):
            return getattr(SRCBUILD(os.path.join(target, 'SRCBUILD')), key)
        match = self.remote_search(target)
        if match:
            return self.REMOTE_CACHE[match][key]
        # for consistency
        for k in ('depends', 'makedepends', 'checkdepends', 'sources', \
            'options', 'backup', 'pgpkeys'):
            if key == k:
                return []

    def remote_aliases(self, basename=True):
        ''' Returns basename of all aliases '''
        if misc.python2:
            misc.typecheck(basename, (types.BooleanType))

        aliases = []
        for sfile in misc.list_files(os.path.join(self.CACHE_DIR, \
            'repositories')):
            if sfile.endswith('.alias'):
                if basename:
                    aliases.append(misc.file_name(sfile))
                else:
                    aliases.append(misc.file_name(sfile, False))
        return sorted(aliases)

    def remote_alias(self, target):
        ''' Returns alias for target, if not returns original '''
        if misc.python2:
            misc.typecheck(target, (types.StringTypes))

        for alias in self.remote_aliases(basename=False):
            if os.path.basename(target) == os.path.basename(alias):
                return misc.file_readlines(alias + '.alias')
        # return consistent data
        return [target]


class SRCBUILD(object):
    ''' A SRCBUILD parser '''
    _symbol_regex = re.compile(r'\$(?P<name>{[\w\d_]+}|[\w\d]+)')

    def __init__(self, name):
        self.version = ''
        self.release = '1'
        self.description = ''
        self.depends = []
        self.makedepends = []
        self.checkdepends = []
        self.sources = []
        self.pgpkeys = []
        self.options = []
        self.backup = []

        # Symbol lookup table
        self._var_map = {
            'version': 'version',
            'release': 'release',
            'description': 'description',
            'depends': 'depends',
            'makedepends': 'makedepends',
            'checkdepends': 'checkdepends',
            'sources': 'sources',
            'pgpkeys': 'pgpkeys',
            'options': 'options',
            'backup': 'backup',
        }
        # Symbol table
        self._symbols = {}

        self.fileobj = open(name, 'r')
        self._parse(self.fileobj)
        self.fileobj.close()

    def _handle_assign(self, token):
        ''' Expand non-standard variable as Bash does '''
        var, equals, value = token.strip().partition('=')
        # Is it an array?
        if value[0] == '(' and value[-1] == ')':
            self._symbols[var] = self._clean_array(value)
        else:
            self._symbols[var] = self._clean(value)

    def _parse(self, fileobj):
        ''' Parse SRCBUILD '''
        if hasattr(fileobj, 'seek'):
            fileobj.seek(0)
        parser = shlex.shlex(fileobj, posix=True)
        parser.whitespace_split = True
        in_function = False
        while 1:
            token = parser.get_token()
            if token is None or token == '':
                break
            # Skip escaped newlines and functions
            if token == '\n' or in_function:
                continue
            # Special case:
            # Array elements are dispersed among tokens, we have to join
            # them first
            if token.find('=(') >= 0 and not token.rfind(')') >= 0:
                in_array = True
                elements = []
                while in_array:
                    _token = parser.get_token()
                    if _token == '\n':
                        continue
                    if _token[-1] == ')':
                        _token = '"%s")' % _token.strip(')')
                        token = token.replace('=(', '=("', 1) + '"'
                        token = ' '.join((token, ' '.join(elements), _token))
                        in_array = False
                    else:
                        elements.append('"%s"' % _token.strip())
            # Assignment
            if re.match(r'^[\w\d_]+=', token):
                self._handle_assign(token)
            # Function definitions
            elif token == '{':
                in_function = True
            elif token == '}' and in_function:
                in_function = False
        self._substitute()
        self._assign_local()

    def _clean(self, value):
        ''' Pythonize a bash string '''
        try:
            return ' '.join(shlex.split(value))
        except ValueError:
            # provide a meaningfull message
            raise ValueError('Syntax error in %s' % self.fileobj.name)

    def _clean_array(self, value):
        ''' Pythonize a bash array '''
        return filter(None, shlex.split(value.strip('()')))

    def _replace_symbol(self, matchobj):
        ''' Replace a regex-matched variable with its value '''
        symbol = matchobj.group('name').strip('{}')
        # If the symbol isn't found fallback to an empty string, like bash
        try:
            value = self._symbols[symbol]
        except KeyError:
            value = ''
        # BUG: Might result in an infinite loop, oops!
        return self._symbol_regex.sub(self._replace_symbol, value)

    def _substitute(self):
        ''' Substitute all bash variables within values with their values '''
        for symbol in self._symbols:
            value = self._symbols[symbol]
            # FIXME: This is icky
            if isinstance(value, str):
                result = self._symbol_regex.sub(self._replace_symbol, value)
            else:
                result = [self._symbol_regex.sub(self._replace_symbol, x) \
                    for x in value]
            self._symbols[symbol] = result

    def _assign_local(self):
        ''' Assign values from _symbols to SRCBUILD variables '''
        for var in self._symbols:
            value = self._symbols[var]
            if var in self._var_map:
                var = self._var_map[var]
            setattr(self, var, value)
