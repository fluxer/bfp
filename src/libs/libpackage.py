#!/bin/python2

import os, sys, re, shlex, types
from distutils.version import LooseVersion

import libmisc, libinotify
misc = libmisc.Misc()


class Database(object):
    ''' Get information about packages '''
    def __init__(self):
        self.ROOT_DIR = '/'
        self.CACHE_DIR = '/var/cache/spm'
        self.REMOTE_CACHE = {}
        self.LOCAL_DIR = self.ROOT_DIR + 'var/local/spm'
        self.LOCAL_CACHE = {}
        self.IGNORE = []
        self._notifiers_setup()

    def _notifiers_setup(self):
        # FIXME: should class variables be asigned? non-globals tend to get destroyed
        wm = libinotify.WatchManager()  # Watch Manager
        mask = libinotify.IN_DELETE | libinotify.IN_CREATE | libinotify.IN_MODIFY # watched events
        notifier = libinotify.AsyncNotifier(wm, self._build_remote_cache)
        wdd = wm.add_watch(os.path.join(self.CACHE_DIR, 'repositories'), mask, rec=True)
        notifier2 = libinotify.AsyncNotifier(wm, self._build_local_cache)
        wdd2 = wm.add_watch(self.LOCAL_DIR, mask, rec=True)

    def _notifiers_teardown(self):
        # FIXME: should something be done on class delete?
        pass

    def _build_local_cache(self, event=None):
        # event is only for compat with the notifier
        self.LOCAL_CACHE = {}
        for sdir in misc.list_dirs(self.LOCAL_DIR):
            metadata = os.path.join(sdir, 'metadata')
            footprint = os.path.join(sdir, 'footprint')
            if os.path.isfile(metadata) and os.path.isfile(footprint):
                self.LOCAL_CACHE[sdir] = {
                    'version': self._local_metadata(metadata, 'version'),
                    'description': self._local_metadata(metadata, 'description'),
                    'depends': self._local_metadata(metadata, 'depends').split(),
                    'size': self._local_metadata(metadata, 'size'),
                    'footprint': misc.file_read(footprint)
                }
        # print(sys.getsizeof(self.LOCAL_CACHE))

    def _build_remote_cache(self, event=None):
        # event is only for compat with the notifier
        self.REMOTE_CACHE = {}
        for sdir in misc.list_dirs(os.path.join(self.CACHE_DIR, 'repositories')):
            srcbuild = os.path.join(sdir, 'SRCBUILD')
            if os.path.isfile(srcbuild):
                parser = SRCBUILD(srcbuild)
                self.REMOTE_CACHE[sdir] = {
                    'version': parser.version,
                    'description': parser.description,
                    'depends': parser.depends,
                    'makedepends': parser.makedepends,
                    'checkdepends': parser.checkdepends,
                    'sources': parser.sources,
                    'options': parser.options,
                    'backup': parser.backup
                }
        # print(sys.getsizeof(self.REMOTE_CACHE))

    def _local_metadata(self, smetadata, skey):
        ''' Returns metadata of local target '''
        misc.typecheck(smetadata, (types.StringTypes))
        misc.typecheck(skey, (types.StringTypes))

        for line in misc.file_readlines(smetadata):
            if line.startswith(skey + '='):
                return line.split('=')[1].strip()

    def remote_all(self, basename=False):
        ''' Returns directories of all remote (repository) targets '''
        misc.typecheck(basename, (types.BooleanType))

        # rebuild cache on demand
        if not self.REMOTE_CACHE:
            self._build_remote_cache()

        if basename:
            lremote = []
            for target in self.REMOTE_CACHE.keys():
                lremote.append(os.path.basename(target))
            return sorted(lremote)
        return sorted(self.REMOTE_CACHE.keys())

    def local_all(self, basename=False):
        ''' Returns directories of all local (installed) targets '''
        misc.typecheck(basename, (types.BooleanType))

        # rebuild cache on demand
        if not self.LOCAL_CACHE:
            self._build_local_cache()

        if basename:
            llocal = []
            for target in self.LOCAL_CACHE.keys():
                llocal.append(os.path.basename(target))
            return sorted(llocal)
        return sorted(self.LOCAL_CACHE.keys())

    def local_search(self, target):
        ''' Returns full path to directory matching target '''
        misc.typecheck(target, (types.StringTypes))

        for ltarget in self.local_all():
            if ltarget == target \
                or os.path.basename(ltarget) == os.path.basename(target):
                return ltarget
        return None

    def local_installed(self, target):
        ''' DEPRECATED: use local_search() instead '''
        return self.local_search(target)

    def remote_search(self, target):
        ''' Returns full path to directory matching target '''
        misc.typecheck(target, (types.StringTypes))

        if os.path.isfile(os.path.join(target, 'SRCBUILD')):
            return target

        for rtarget in self.remote_all():
            if rtarget == target \
                or os.path.basename(rtarget) == os.path.basename(target):
                return rtarget
        return None

    def local_belongs(self, sfile, exact=False, escape=True, ignore=None):
        ''' Searches for match of file in all local targets '''
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

            if misc.string_search(sfile, self.local_footprint(local), \
                exact=exact, escape=escape):
                match.append(local)
        return match

    def remote_mdepends(self, target, checked=None, cdepends=False):
        ''' Returns missing build dependencies of target '''
        misc.typecheck(target, (types.StringTypes))
        misc.typecheck(checked, (types.NoneType, types.ListType))
        misc.typecheck(cdepends, (types.BooleanType))

        # depends, {make,check}depends are optional and
        # relying on them to be different than None
        # would break the code, they can not be
        # concentrated nor looped trough
        depends = self.remote_metadata(target, 'depends')
        makedepends = self.remote_metadata(target, 'makedepends')
        checkdepends = self.remote_metadata(target, 'checkdepends')

        missing = []
        build_depends = []
        if checked is None:
            checked = []

        # respect ignored targets to avoid building
        # dependencies when not needed
        if target in self.IGNORE:
            return missing

        if depends:
            build_depends.extend(depends)
        if makedepends:
            build_depends.extend(makedepends)
        if cdepends and checkdepends:
            build_depends.extend(checkdepends)

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

    def local_footprint(self, target):
        ''' Returns files of target '''
        misc.typecheck(target, (types.StringTypes))

        match = self.local_search(target)
        if match:
            return self.LOCAL_CACHE[match]['footprint']

    def local_metadata(self, target, key):
        ''' Returns metadata of local target '''
        misc.typecheck(target, (types.StringTypes))
        misc.typecheck(key, (types.StringTypes))

        match = self.local_search(target)
        if match:
            return self.LOCAL_CACHE[match][key]

    def local_uptodate(self, target):
        ''' Returns True if target is up-to-date and False otherwise '''
        misc.typecheck(target, (types.StringTypes))

        # check if target is installed at all first
        if not self.local_search(target):
            return False

        # if remote target is passed and it's a directory not a base name
        # then the local target will be invalid and local_version will equal
        # None, thus we use the base name to find the local target version
        local_version = self.local_metadata(os.path.basename(target), 'version')
        remote_version = self.remote_metadata(target, 'version')

        # LooseVersion does not handle None which may be the case on invalid
        # remote target so handle that
        if not remote_version:
            return False

        if LooseVersion(local_version) < LooseVersion(remote_version):
            return False
        return True

    def remote_metadata(self, target, key):
        ''' Returns metadata of remote target '''
        misc.typecheck(target, (types.StringTypes))
        misc.typecheck(key, (types.StringTypes))

        if os.path.isfile(os.path.join(target, 'SRCBUILD')):
            return getattr(SRCBUILD(os.path.join(target, 'SRCBUILD')), key)
        match = self.remote_search(target)
        if match:
            return self.REMOTE_CACHE[match][key]

    def remote_aliases(self, basename=True):
        ''' Returns basename of all aliases '''
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
        misc.typecheck(target, (types.StringTypes))

        for alias in self.remote_aliases(basename=False):
            if os.path.basename(target) == os.path.basename(alias):
                return misc.file_readlines(alias + '.alias')
        # return consistent data
        return [target]

    def remote_groups(self, basename=True):
        ''' Returns groups in the repositories '''
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


class SRCBUILD(object):
    ''' A SRCBUILD parser '''
    _symbol_regex = re.compile(r'\$(?P<name>{[\w\d_]+}|[\w\d]+)')

    def __init__(self, name=None, fileobj=None):
        self.version = ''
        self.description = ''
        self.depends = []
        self.makedepends = []
        self.checkdepends = []
        self.sources = []
        self.options = []
        self.backup = []

        # Symbol lookup table
        self._var_map = {
            'version': 'version',
            'description': 'description',
            'depends': 'depends',
            'makedepends': 'makedepends',
            'checkdepends': 'checkdepends',
            'sources': 'sources',
            'options': 'options',
            'backup': 'backup',
        }
        # Symbol table
        self._symbols = {}

        if not name and not fileobj:
            raise ValueError('nothing to open')
        should_close = False
        if not fileobj:
            fileobj = open(name, 'r')
            should_close = True
        self._parse(fileobj)
        if should_close:
            fileobj.close()

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
        return ' '.join(shlex.split(value))

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
