#!/usr/bin/python2

'''
A module for package management with database in JSON format

Database() is the core of Source Package Manager, it provides various methods
to get information about packages installed and otherwise. The methods prefixed
with "local" deal with metadata of software installed on the system, "remote"
methods provide info for software available from repositories with build
recipes in the SRCBUILD format.

SRCBUILD() is Source Package Manager recipes (SRCBUILDs) parser.

'''

import os, re, types
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
        self.NOTIFY = True

    def _build_local_cache(self):
        ''' Build internal local database cache '''
        self.LOCAL_CACHE = {}

        if not os.path.isdir(self.LOCAL_DIR):
            return
        for sdir in misc.list_dirs(self.LOCAL_DIR):
            metadata = '%s/metadata.json' % sdir
            srcbuild = '%s/SRCBUILD' % sdir
            if os.path.isfile(srcbuild) and os.path.isfile(metadata):
                self.LOCAL_CACHE[sdir] = misc.json_read(metadata)
            if self.NOTIFY:
                notify.watch_add(sdir)
        if self.NOTIFY:
            notify.watch_add(self.LOCAL_DIR)
        # print(sys.getsizeof(self.LOCAL_CACHE))

    def _build_remote_cache(self):
        ''' Build internal remote database cache '''
        self.REMOTE_CACHE = {}

        metadir = '%s/repositories' % self.CACHE_DIR
        if not os.path.isdir(metadir):
            return
        parser = SRCBUILD()
        for sdir in misc.list_dirs(metadir):
            srcbuild = '%s/SRCBUILD' % sdir
            if os.path.isfile(srcbuild):
                parser.parse(srcbuild)
                self.REMOTE_CACHE[sdir] = {
                    'version': parser.version,
                    'release': parser.release,
                    'description': parser.description,
                    'depends': parser.depends,
                    'makedepends': parser.makedepends,
                    'optdepends': parser.optdepends,
                    'checkdepends': parser.checkdepends,
                    'sources': parser.sources,
                    'pgpkeys': parser.pgpkeys,
                    'options': parser.options,
                    'backup': parser.backup
                }
            if self.NOTIFY and not sdir.endswith('/.git'):
                notify.watch_add(sdir)
        if self.NOTIFY:
            notify.watch_add(metadir)
        # print(sys.getsizeof(self.REMOTE_CACHE))

    def remote_all(self, basename=False):
        ''' Returns directories of all remote (repository) targets '''
        if misc.python2:
            misc.typecheck(basename, (types.BooleanType))

        # rebuild cache on demand
        recache = False
        for wd, mask, cookie, name in notify.event_read():
            recache = True
        if not self.REMOTE_CACHE or recache:
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

    def remote_search(self, target):
        ''' Returns full path to directory matching target '''
        if misc.python2:
            misc.typecheck(target, (types.StringTypes))

        for rtarget in self.remote_all():
            if rtarget == target or rtarget.endswith('/%s' % target):
                return rtarget
        if os.path.isfile('%s/SRCBUILD' % target):
            return target

    def local_belongs(self, sfile, exact=False, escape=True, ignore=None):
        ''' Searches for match of file in all local targets '''
        if misc.python2:
            misc.typecheck(sfile, (types.StringTypes))
            misc.typecheck(exact, (types.BooleanType))
            misc.typecheck(escape, (types.BooleanType))
            misc.typecheck(ignore, (types.NoneType, types.StringTypes))

        match = []
        for local in self.local_all(basename=True):
            if local == ignore:
                continue

            if misc.string_search(sfile, self.local_metadata(local, 'footprint'), \
                exact=exact, escape=escape):
                match.append(local)
        return match

    def remote_mdepends(self, target, checked=None, cdepends=False, \
        mdepends=True, odepends=False):
        ''' Returns missing build dependencies of target '''
        if misc.python2:
            misc.typecheck(target, (types.StringTypes))
            misc.typecheck(checked, (types.NoneType, types.ListType))
            misc.typecheck(cdepends, (types.BooleanType))
            misc.typecheck(mdepends, (types.BooleanType))
            misc.typecheck(odepends, (types.BooleanType))

        missing = []
        build_depends = []
        if checked is None:
            checked = []

        # respect ignored targets to avoid building dependencies when not needed
        if target in self.IGNORE:
            return missing

        build_depends.extend(self.remote_metadata(target, 'depends'))
        if mdepends:
            build_depends.extend(self.remote_metadata(target, 'makedepends'))
        if odepends:
            build_depends.extend(self.remote_metadata(target, 'optdepends'))
        if cdepends:
            build_depends.extend(self.remote_metadata(target, 'checkdepends'))

        for dependency in build_depends:
            if checked and dependency in checked:
                continue

            if not dependency in missing \
                and not self.local_uptodate(dependency):
                checked.append(target)
                missing.extend(self.remote_mdepends(dependency, checked, \
                    cdepends, mdepends, odepends))
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
        # for consistency
        if key in ('depends', 'optdepends', 'backup', 'footprint'):
            return []

    def local_uptodate(self, target):
        ''' Returns True if target is up-to-date and False otherwise '''
        if misc.python2:
            misc.typecheck(target, (types.StringTypes))

        # if remote target is passed and it's a directory not a base name
        # then the local target will be invalid and local_version will equal
        # None, thus the base name is used to get the local target metadata
        base = os.path.basename(target)
        local_version = self.local_metadata(base, 'version')
        local_release = self.local_metadata(base, 'release')
        local_optional = self.local_metadata(base, 'optdepends')
        remote_version = self.remote_metadata(target, 'version')
        remote_release = self.remote_metadata(target, 'release')

        # LooseVersion does not handle None
        if not remote_version or not local_version:
            return False

        if LooseVersion(local_version) < LooseVersion(remote_version):
            return False
        elif local_release < remote_release:
            return False
        else:
            for optional in self.remote_metadata(target, 'optdepends'):
                # FIXME: recursion bug
                if self.local_uptodate(optional) \
                    and not optional in local_optional:
                    return False
        return True

    def remote_metadata(self, target, key):
        ''' Returns metadata of remote target '''
        if misc.python2:
            misc.typecheck(target, (types.StringTypes))
            misc.typecheck(key, (types.StringTypes))

        srcbuild = '%s/SRCBUILD' % target
        match = self.remote_search(target)
        if match and match in self.REMOTE_CACHE:
            return self.REMOTE_CACHE[match][key]
        elif os.path.isfile(srcbuild):
            return getattr(SRCBUILD(srcbuild), key)
        # for consistency
        if key in ('depends', 'makedepends', 'optdepends', 'checkdepends', \
            'sources', 'options', 'backup', 'pgpkeys'):
            return []

    def remote_aliases(self, basename=True):
        ''' Returns basename of all aliases '''
        if misc.python2:
            misc.typecheck(basename, (types.BooleanType))

        aliases = []
        for sfile in misc.list_files('%s/repositories' % self.CACHE_DIR):
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
                return misc.file_readsmart('%s.alias' % alias)
        # return consistent data
        return [target]


class SRCBUILD(object):
    ''' A (new) SRCBUILD parser '''
    def __init__(self, sfile=None):
        if misc.python2:
            misc.typecheck(sfile, (types.NoneType, types.StringTypes))

        self.string_regex = re.compile('(?:^|\n)([\w]+)=([^\(].*)')
        self.array_regex = re.compile('(?:^|\n)([\w]+)=\(([^\)]+)', re.MULTILINE)

        self.prepare()
        if sfile:
            self.parse(sfile)

    def prepare(self):
        self.version = ''
        self.release = '1'
        self.description = ''
        self.depends = []
        self.makedepends = []
        self.optdepends = []
        self.checkdepends = []
        self.sources = []
        self.pgpkeys = []
        self.options = []
        self.backup = []

    def parse(self, sfile):
        if misc.python2:
            misc.typecheck(sfile, (types.StringTypes))

        self.prepare()
        _stringmap = {}
        _arraymap = {}

        content = misc.file_read(sfile)
        for var, value in re.findall(self.string_regex, content):
            _stringmap[var] = value.strip('"').strip("'")
        for var, value in re.findall(self.array_regex, content):
            arrayval = []
            for val in value.split():
                for string in _stringmap:
                    val = val.replace('$%s' % string, _stringmap[string])
                    val = val.replace('${%s}' % string, _stringmap[string])
                arrayval.append(val.strip('"').strip("'"))
            _arraymap[var] = arrayval
        for string in _stringmap:
            val = _stringmap[string]
            val = val.replace('$%s' % string, _stringmap[string])
            val = val.replace('${%s}' % string, _stringmap[string])
            _stringmap[string] = val

        for string in ('version', 'release', 'description'):
            if string in _stringmap:
                setattr(self, string, _stringmap[string])
        for array in ('depends', 'makedepends', 'optdepends', 'checkdepends', \
            'sources', 'pgpkeys', 'options', 'backup'):
            if array in _arraymap:
                setattr(self, array, _arraymap[array])
