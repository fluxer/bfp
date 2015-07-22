#!/usr/bin/python2

'''
A module for package management with database in JSON format

Database() is the core of Source Package Manager, it provides various methods
to get information about packages installed and otherwise. The methods prefixed
with "local" deal with metadata of software installed on the system, "remote"
methods provide info for software available from repositories with build
recipes in the SRCBUILD format.

'''

import os, re, types, glob
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
        self.LOCAL_DIR = '/var/local/spm'
        self.LOCAL_CACHE = {}
        self.IGNORE = []
        self.NOTIFY = True
        self._stringx = re.compile('(?:^|\n)([\w]+)=([^\(].*)')
        self._arrayx = re.compile('(?:^|\n)([\w]+)=\(([^\)]+)', re.MULTILINE)

    def _build_local_cache(self):
        ''' Build internal local database cache '''
        self.LOCAL_CACHE = {}

        for sfile in glob.glob('%s/*/metadata.json' % self.LOCAL_DIR):
            sdir = os.path.dirname(sfile)
            if os.path.isfile('%s/SRCBUILD' % sdir):
                self.LOCAL_CACHE[sdir] = misc.json_read(sfile)
            if self.NOTIFY:
                notify.watch_add(sdir)
        if self.NOTIFY and os.path.isdir(self.LOCAL_DIR):
            notify.watch_add(self.LOCAL_DIR)
        # print(sys.getsizeof(self.LOCAL_CACHE))

    def _build_remote_cache(self):
        ''' Build internal remote database cache '''
        self.REMOTE_CACHE = {}

        metadir = '%s/repositories' % self.CACHE_DIR
        if not os.path.isdir(metadir):
            return
        for sdir in misc.list_dirs(metadir):
            srcbuild = '%s/SRCBUILD' % sdir
            if os.path.isfile(srcbuild):
                self.REMOTE_CACHE[sdir] = self.srcbuild_parse(srcbuild)
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

        lremote = []
        for target in self.REMOTE_CACHE:
            if basename:
                lremote.append(os.path.basename(target))
            else:
                lremote.append(target)
        return sorted(lremote)

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

        llocal = []
        for target in self.LOCAL_CACHE:
            if basename:
                llocal.append(os.path.basename(target))
            else:
                llocal.append(target)
        return sorted(llocal)

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
        ''' Searches for file match in all local targets '''
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

    def remote_mdepends(self, target, cdepends=False, mdepends=True, \
        odepends=False, checked=None):
        ''' Returns missing build dependencies of target '''
        if misc.python2:
            misc.typecheck(target, (types.StringTypes))
            misc.typecheck(cdepends, (types.BooleanType))
            misc.typecheck(mdepends, (types.BooleanType))
            misc.typecheck(odepends, (types.BooleanType))
            misc.typecheck(checked, (types.NoneType, types.ListType))

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
            build_depends.append(self.remote_metadata(target, 'optdepends'))
        if cdepends:
            build_depends.extend(self.remote_metadata(target, 'checkdepends'))

        for dependency in build_depends:
            if dependency in checked:
                continue
            if not dependency in missing \
                and not self.local_uptodate(dependency):
                checked.append(target)
                missing.extend(self.remote_mdepends(dependency, cdepends, \
                    mdepends, odepends, checked))
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

        for installed in self.local_all(basename=True):
            if installed in self.IGNORE or installed in checked:
                continue
            basename = os.path.basename(target)
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
            for optional in local_optional:
                if self.local_search(optional) \
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
            return self.srcbuild_parse(srcbuild)[key]
        # for consistency
        if key in ('depends', 'makedepends', 'optdepends', 'checkdepends', \
            'sources', 'options', 'backup', 'pgpkeys'):
            return []

    def remote_aliases(self, basename=True):
        ''' Returns list of targets representing a single one '''
        if misc.python2:
            misc.typecheck(basename, (types.BooleanType))

        aliases = ['world', 'system']
        for sfile in misc.list_files('%s/repositories' % self.CACHE_DIR):
            if sfile.endswith('.alias'):
                aliases.append(misc.file_name(sfile, basename))
        return sorted(aliases)

    def remote_alias(self, target):
        ''' Returns alias for target, if not returns original '''
        if misc.python2:
            misc.typecheck(target, (types.StringTypes))

        if target == 'world':
            return self.remote_all(basename=True)
        elif target == 'system':
            return self.local_all(basename=True)
        for alias in self.remote_aliases(basename=False):
            if os.path.basename(target) == os.path.basename(alias):
                return misc.file_readsmart('%s.alias' % alias)
        # return consistent data
        return [target]

    def srcbuild_parse(self, sfile):
        ''' Parse variables in SRCBUILD, returns dictionary '''
        if misc.python2:
            misc.typecheck(sfile, (types.StringTypes))

        _stringmap = {}
        _arraymap = {}
        _varmap = {
            'version': '',
            'release': '1',
            'description': '',
            'depends': [],
            'makedepends': [],
            'optdepends': [],
            'checkdepends': [],
            'sources': [],
            'pgpkeys': [],
            'options': [], 
            'backup': []
        }

        content = misc.file_read(sfile)
        for var, value in re.findall(self._stringx, content):
            _stringmap[var] = value.strip('"').strip("'")
        for var, value in re.findall(self._arrayx, content):
            arrayval = []
            for val in value.split():
                for string in _stringmap:
                    val = val.replace('$%s' % string, _stringmap[string])
                    val = val.replace('${%s}' % string, _stringmap[string])
                arrayval.append(val.strip('"').strip("'"))
            _arraymap[var] = arrayval
            if var in ('depends', 'makedepends', 'optdepends', \
                'checkdepends', 'sources', 'pgpkeys', 'options', 'backup'):
                _varmap[var] = arrayval
        for string in _stringmap:
            val = _stringmap[string]
            val = val.replace('$%s' % string, _stringmap[string])
            val = val.replace('${%s}' % string, _stringmap[string])
            _stringmap[string] = val
            if string in ('version', 'release', 'description'):
                _varmap[string] = val

        return _varmap