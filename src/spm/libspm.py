#!/bin/python2

import gettext
_ = gettext.translation('spm', fallback=True).gettext

import sys, os, shutil, re, compileall, site
from datetime import datetime
if sys.version < '3':
    import ConfigParser as configparser
else:
    import configparser

import libmessage, libmisc, libpackage
message = libmessage.Message()
misc = libmisc.Misc()
database = libpackage.Database()


CATCH = False
MAIN_CONF = '/etc/spm.conf'
REPOSITORIES_CONF = '/etc/spm/repositories.conf'
MIRRORS_CONF = '/etc/spm/mirrors.conf'
KEYSERVERS_CONF = '/etc/spm/keyservers.conf'
DEFAULTS = {
    'CACHE_DIR': '/var/cache/spm',
    'BUILD_DIR': '/var/tmp/spm',
    'ROOT_DIR': '/',
    'LOCAL_DIR': '/var/local/spm',
    'GPG_DIR': '/etc/spm/gpg',
    'IGNORE': '',
    'DEMOTE': '',
    'SIGN': '',
    'OFFLINE': 'False',
    'MIRROR': 'False',
    'TIMEOUT': '30',
    'VERIFY': 'False',
    'CHOST': '',
    'CFLAGS': '',
    'CXXFLAGS': '',
    'CPPFLAGS': '',
    'LDFLAGS': '',
    'MAKEFLAGS': '',
    'COMPRESS_MAN': 'False',
    'SPLIT_DEBUG': 'False',
    'STRIP_BINARIES': 'False',
    'STRIP_SHARED': 'False',
    'STRIP_STATIC': 'False',
    'STRIP_RPATH': 'False',
    'PYTHON_COMPILE': 'False',
    'IGNORE_MISSING': 'False',
    'CONFLICTS': 'False',
    'BACKUP': 'False',
    'SCRIPTS': 'False',
    'TRIGGERS': 'False',
}

if not os.path.isfile(MAIN_CONF):
    message.warning(_('Configuration file does not exist'), MAIN_CONF)

conf = configparser.SafeConfigParser(DEFAULTS)
conf.read(MAIN_CONF)
# section are hardcore-required, to avoid failures on get() add them to the
# conf object but do notice that changes are not written to config on purpose
for section in ('spm', 'prepare', 'compile', 'install', 'merge'):
    if not conf.has_section(section):
        conf.add_section(section)

CACHE_DIR = conf.get('spm', 'CACHE_DIR')
BUILD_DIR = conf.get('spm', 'BUILD_DIR')
ROOT_DIR = conf.get('spm', 'ROOT_DIR')
LOCAL_DIR = ROOT_DIR + 'var/local/spm'
GPG_DIR = conf.get('spm', 'GPG_DIR')
IGNORE = conf.get('spm', 'IGNORE').split(' ')
DEMOTE = conf.get('spm', 'DEMOTE')
SIGN = conf.get('spm', 'SIGN')
OFFLINE = conf.getboolean('prepare', 'OFFLINE')
MIRROR = conf.getboolean('prepare', 'MIRROR')
TIMEOUT = conf.getint('prepare', 'TIMEOUT')
VERIFY = conf.getboolean('prepare', 'VERIFY')
CHOST = conf.get('compile', 'CHOST')
CFLAGS = conf.get('compile', 'CFLAGS')
CXXFLAGS = conf.get('compile', 'CXXFLAGS')
CPPFLAGS = conf.get('compile', 'CPPFLAGS')
LDFLAGS = conf.get('compile', 'LDFLAGS')
MAKEFLAGS = conf.get('compile', 'MAKEFLAGS')
COMPRESS_MAN = conf.getboolean('install', 'COMPRESS_MAN')
SPLIT_DEBUG = conf.getboolean('install', 'SPLIT_DEBUG')
STRIP_BINARIES = conf.getboolean('install', 'STRIP_BINARIES')
STRIP_SHARED = conf.getboolean('install', 'STRIP_SHARED')
STRIP_STATIC = conf.getboolean('install', 'STRIP_STATIC')
STRIP_RPATH = conf.getboolean('install', 'STRIP_RPATH')
PYTHON_COMPILE = conf.getboolean('install', 'PYTHON_COMPILE')
IGNORE_MISSING = conf.getboolean('install', 'IGNORE_MISSING')
CONFLICTS = conf.getboolean('merge', 'CONFLICTS')
BACKUP = conf.getboolean('merge', 'BACKUP')
SCRIPTS = conf.getboolean('merge', 'SCRIPTS')
TRIGGERS = conf.getboolean('merge', 'TRIGGERS')

# parse repositories configuration file
if not os.path.isfile(REPOSITORIES_CONF):
    message.warning(_('Repositories configuration file does not exist'), \
        REPOSITORIES_CONF)
    REPOSITORIES = ['https://bitbucket.org/smil3y/mini.git']
else:
    REPOSITORIES = []
    repositories_conf = open(REPOSITORIES_CONF, 'r')
    for line in repositories_conf.readlines():
        line = line.strip()
        if line.startswith(('http://', 'https://', 'ftp://', 'ftps://', \
            'git://', 'ssh://', 'rsync://')) or os.path.exists(line):
            REPOSITORIES.append(line)
    repositories_conf.close()

    if not REPOSITORIES:
        message.critical(_('Repositories configuration file is empty'))
        sys.exit(2)

# parse mirrors configuration file
if not os.path.isfile(MIRRORS_CONF):
    message.warning(_('Mirrors configuration file does not exist'), \
        MIRRORS_CONF)
    MIRRORS = ['http://distfiles.gentoo.org/distfiles']
else:
    MIRRORS = []
    mirrors_conf = open(MIRRORS_CONF, 'r')
    for line in mirrors_conf.readlines():
        line = line.strip()
        if line.startswith(('http://', 'https://', 'ftp://', 'ftps://')):
            MIRRORS.append(line)
    mirrors_conf.close()

    if not MIRRORS and MIRROR:
        message.critical(_('Mirrors configuration file is empty'))
        sys.exit(2)

# parse PGP keys servers configuration file
if not os.path.isfile(KEYSERVERS_CONF):
    message.warning(_('PGP keys servers configuration file does not exist'), \
        KEYSERVERS_CONF)
    KEYSERVERS = ['pool.sks-keyservers.net']
else:
    KEYSERVERS = []
    mirrors_conf = open(KEYSERVERS_CONF, 'r')
    for line in mirrors_conf.readlines():
        line = line.strip()
        if line:
            KEYSERVERS.append(line)
    mirrors_conf.close()

    if not KEYSERVERS and VERIFY:
        message.critical(_('PGP keys servers configuration file is empty'))
        sys.exit(2)

# override module variables from configuration
message.CATCH = CATCH
misc.CATCH = CATCH
misc.OFFLINE = OFFLINE
misc.TIMEOUT = TIMEOUT
misc.ROOT_DIR = ROOT_DIR
misc.GPG_DIR = GPG_DIR
database.ROOT_DIR = ROOT_DIR
database.CACHE_DIR = CACHE_DIR
database.LOCAL_DIR = LOCAL_DIR
database.IGNORE = IGNORE

class Local(object):
    ''' Class for printing local targets metadata '''
    def __init__(self, pattern, do_name=False, do_version=False, \
        do_release=False, do_description=False, do_depends=False, \
        do_reverse=False, do_size=False, do_footprint=False, plain=False):
        self.pattern = pattern
        self.do_name = do_name
        self.do_version = do_version
        self.do_release = do_release
        self.do_description = do_description
        self.do_depends = do_depends
        self.do_reverse = do_reverse
        self.do_size = do_size
        self.do_footprint = do_footprint
        self.plain = plain
        message.CATCH = CATCH
        misc.OFFLINE = OFFLINE
        misc.TIMEOUT = TIMEOUT
        misc.ROOT_DIR = ROOT_DIR
        misc.GPG_DIR = GPG_DIR
        misc.CATCH = CATCH
        database.ROOT_DIR = ROOT_DIR
        database.CACHE_DIR = CACHE_DIR
        database.LOCAL_DIR = LOCAL_DIR
        database.IGNORE = IGNORE

    def main(self):
        ''' Print local target metadata for every match '''
        for target in database.local_all(basename=True):
            if re.search(self.pattern, target):
                if self.do_name and self.plain:
                    print(target)
                elif self.do_name:
                    message.sub_info(_('Name'), target)

                if self.do_version:
                    data = database.local_metadata(target, 'version')
                    if self.plain:
                        print(data)
                    else:
                        message.sub_info(_('Version'), data)

                if self.do_release:
                    data = database.local_metadata(target, 'release')
                    if self.plain:
                        print(data)
                    else:
                        message.sub_info(_('Release'), data)

                if self.do_description:
                    data = database.local_metadata(target, 'description')
                    if self.plain:
                        print(data)
                    else:
                        message.sub_info(_('Description'), data)

                if self.do_depends:
                    data = database.local_metadata(target, 'depends')
                    if self.plain:
                        print(misc.string_convert(data))
                    else:
                        message.sub_info(_('Depends'), data)

                if self.do_reverse:
                    data = database.local_rdepends(target)
                    if self.plain:
                        print(misc.string_convert(data))
                    else:
                        message.sub_info(_('Reverse depends'), data)

                if self.do_size:
                    data = database.local_metadata(target, 'size')
                    if self.plain:
                        print(data)
                    else:
                        message.sub_info(_('Size'), data)

                if self.do_footprint:
                    data = database.local_metadata(target, 'footprint')
                    if self.plain:
                        print(data)
                    else:
                        message.sub_info(_('Footprint'), data)


class Remote(object):
    ''' Class for printing remote targets metadata '''
    def __init__(self, pattern, do_name=False, do_version=False, \
        do_release=False, do_description=False, do_depends=False, \
        do_makedepends=False, do_checkdepends=False, do_sources=False, \
        do_pgpkeys=False, do_options=False, do_backup=False, plain=False):
        self.pattern = pattern
        self.do_name = do_name
        self.do_version = do_version
        self.do_release = do_release
        self.do_description = do_description
        self.do_depends = do_depends
        self.do_makedepends = do_makedepends
        self.do_checkdepends = do_checkdepends
        self.do_sources = do_sources
        self.do_pgpkeys = do_pgpkeys
        self.do_options = do_options
        self.do_backup = do_backup
        self.plain = plain
        message.CATCH = CATCH
        misc.OFFLINE = OFFLINE
        misc.TIMEOUT = TIMEOUT
        misc.ROOT_DIR = ROOT_DIR
        misc.GPG_DIR = GPG_DIR
        misc.CATCH = CATCH
        database.ROOT_DIR = ROOT_DIR
        database.CACHE_DIR = CACHE_DIR
        database.LOCAL_DIR = LOCAL_DIR
        database.IGNORE = IGNORE

    def main(self):
        ''' Print remote target metadata for every match '''
        for target in database.remote_all(basename=True):
            if re.search(self.pattern, target):
                if self.do_name and self.plain:
                    print(target)
                elif self.do_name:
                    message.sub_info(_('Name'), target)

                # asigning data variable only for the sake of readability
                if self.do_version:
                    data = database.remote_metadata(target, 'version')
                    if self.plain:
                        print(data)
                    else:
                        message.sub_info(_('Version'), data)

                if self.do_release:
                    data = database.remote_metadata(target, 'release')
                    if self.plain:
                        print(data)
                    else:
                        message.sub_info(_('Release'), data)

                if self.do_description:
                    data = database.remote_metadata(target, 'description')
                    if self.plain:
                        print(data)
                    else:
                        message.sub_info(_('Description'), data)

                if self.do_depends:
                    data = database.remote_metadata(target, 'depends')
                    if self.plain:
                        print(misc.string_convert(data))
                    else:
                        message.sub_info(_('Depends'), data)

                if self.do_makedepends:
                    data = database.remote_metadata(target, 'makedepends')
                    if self.plain:
                        print(misc.string_convert(data))
                    else:
                        message.sub_info(_('Make depends'), data)

                if self.do_checkdepends:
                    data = database.remote_metadata(target, 'checkdepends')
                    if self.plain:
                        print(misc.string_convert(data))
                    else:
                        message.sub_info(_('Check depends'), data)

                if self.do_sources:
                    data = database.remote_metadata(target, 'sources')
                    if self.plain:
                        print(misc.string_convert(data))
                    else:
                        message.sub_info(_('Sources'), data)

                if self.do_pgpkeys:
                    data = database.remote_metadata(target, 'pgpkeys')
                    if self.plain:
                        print(misc.string_convert(data))
                    else:
                        message.sub_info(_('PGP keys'), data)

                if self.do_options:
                    data = database.remote_metadata(target, 'options')
                    if self.plain:
                        print(misc.string_convert(data))
                    else:
                        message.sub_info(_('Options'), data)

                if self.do_backup:
                    data = database.remote_metadata(target, 'backup')
                    if self.plain:
                        print(misc.string_convert(data))
                    else:
                        message.sub_info(_('Backup'), data)


class Repo(object):
    ''' Class for dealing with repositories '''
    def __init__(self, repositories_urls, do_clean=False, do_sync=False, \
        do_update=False, do_prune=False):
        self.repositories_urls = repositories_urls
        self.do_clean = do_clean
        self.do_sync = do_sync
        self.do_prune = do_prune
        self.do_update = do_update
        message.CATCH = CATCH
        misc.OFFLINE = OFFLINE
        misc.TIMEOUT = TIMEOUT
        misc.ROOT_DIR = ROOT_DIR
        misc.GPG_DIR = GPG_DIR
        misc.CATCH = CATCH
        database.ROOT_DIR = ROOT_DIR
        database.CACHE_DIR = CACHE_DIR
        database.LOCAL_DIR = LOCAL_DIR
        database.IGNORE = IGNORE

    def clean(self):
        ''' Clean repository '''
        if os.path.isdir(self.repository_dir):
            message.sub_info(_('Removing'), self.repository_dir)
            misc.dir_remove(self.repository_dir)
        else:
            message.sub_debug(_('Dirctory is OK'), self.repository_dir)

    def sync(self):
        ''' Sync repository '''
        rdir = os.path.join(CACHE_DIR, 'repositories')
        misc.dir_create(rdir, DEMOTE)

        if os.path.exists(self.repository_url):
            # repository is local path, create a copy of it
            message.sub_info(_('Cloning local'), self.repository_name)
            shutil.copytree(self.repository_url, self.repository_dir)
        else:
            message.sub_info(_('Cloning/pulling remote'), self.repository_name)
            misc.fetch(self.repository_url, self.repository_dir)

    def prune(self):
        ''' Remove repositories that are no longer in the config '''
        rdir = os.path.join(CACHE_DIR, 'repositories')
        if not os.path.exists(rdir):
            return

        for sdir in os.listdir(rdir):
            valid = False
            for line in misc.file_readlines('/etc/spm/repositories.conf'):
                line = misc.string_encode(line.strip())
                if not line or line.startswith('#'):
                    continue

                if os.path.basename(line) == sdir:
                    valid = True

            if not valid:
                repo_dir = os.path.join(rdir, sdir)
                message.sub_warning(_('Removing'), repo_dir)
                misc.dir_remove(repo_dir)

    def update(self):
        ''' Check repositories for updates '''
        message.sub_info(_('Checking for updates'))
        for target in database.local_all(basename=True):
            if not database.remote_search(target):
                message.sub_warning(_('Target not in any repository'), target)
                continue

            message.sub_debug(_('Checking'), target)
            latest = database.local_uptodate(target)
            if not latest and target in IGNORE:
                message.sub_warning(_('New version of %s (ignored) available') % target, \
                    database.remote_metadata(target, 'version'))
            elif not latest:
                message.sub_warning(_('New version of %s available') % target, \
                    database.remote_metadata(target, 'version'))

    def main(self):
        ''' Execute action for every repository '''
        for repository in self.repositories_urls:
            # compute only once by asigning class variables, in cases when
            # clean and sync is done this is more optimal but triggers
            # http://pylint-messages.wikidot.com/messages:w0201
            self.repository_url = repository
            self.repository_name = os.path.basename(self.repository_url)
            self.repository_dir = os.path.join(CACHE_DIR, 'repositories', \
                self.repository_name)

            if self.do_clean:
                message.sub_info(_('Starting cleanup at'), datetime.today())
                self.clean()

            if self.do_sync:
                message.sub_info(_('Starting sync at'), datetime.today())
                self.sync()

        if self.do_prune:
            message.sub_info(_('Starting prune at'), datetime.today())
            self.prune()

        if self.do_update:
            message.sub_info(_('Starting update at'), datetime.today())
            self.update()


class Source(object):
    ''' Class for dealing with sources '''
    def __init__(self, targets, do_clean=False, do_prepare=False, \
        do_compile=False, do_check=False, do_install=False, do_merge=False, \
        do_remove=False, do_depends=False, do_reverse=False, do_update=False, \
        autoremove=False):
        self.targets = targets
        self.do_clean = do_clean
        self.do_prepare = do_prepare
        self.do_compile = do_compile
        self.do_check = do_check
        self.do_install = do_install
        self.do_merge = do_merge
        self.do_remove = do_remove
        self.do_depends = do_depends
        self.do_reverse = do_reverse
        self.do_update = do_update
        self.autoremove = autoremove
        self.verify = VERIFY
        self.mirror = MIRROR
        self.split_debug = SPLIT_DEBUG
        self.strip_binaries = STRIP_BINARIES
        self.strip_shared = STRIP_SHARED
        self.strip_static = STRIP_STATIC
        self.strip_rpath = STRIP_RPATH
        self.compress_man = COMPRESS_MAN
        self.ignore_missing = IGNORE_MISSING
        self.python_compile = PYTHON_COMPILE
        message.CATCH = CATCH
        misc.OFFLINE = OFFLINE
        misc.TIMEOUT = TIMEOUT
        misc.ROOT_DIR = ROOT_DIR
        misc.GPG_DIR = GPG_DIR
        misc.CATCH = CATCH
        database.ROOT_DIR = ROOT_DIR
        database.CACHE_DIR = CACHE_DIR
        database.LOCAL_DIR = LOCAL_DIR
        database.IGNORE = IGNORE

    def autosource(self, targets, automake=False, autoremove=False):
        ''' Handle targets build/remove without affecting current object '''
        if automake:
            obj = Source(targets, do_clean=True, do_prepare=True, \
                do_compile=True, do_check=False, do_install=True, \
                do_merge=True, do_depends=True, do_reverse=self.do_reverse, \
                do_update=False)
        else:
            obj = Source(targets, do_reverse=self.do_reverse, \
                autoremove=autoremove)
        obj.main()

    def split_debug_symbols(self, sfile):
        if not self.split_debug:
            return
        # avoid actions on debug files, do not rely on .debug suffix
        if '/lib/debug/' in sfile:
            return
        # FIXME: do not run on hardlinks, it will fail with binutils <=2.23.2
        # https://sourceware.org/gdb/onlinedocs/gdb/Separate-Debug-Files.html
        sdebug = sfile.replace(self.install_dir, self.install_dir + \
            sys.prefix + '/lib/debug') + '.debug'
        misc.dir_create(os.path.dirname(sdebug))
        objcopy = misc.whereis('objcopy')
        message.sub_debug(_('Creating debug file'), sdebug)
        misc.system_command((objcopy, '--only-keep-debug', \
            '--compress-debug-sections', sfile, sdebug))
        misc.system_command((objcopy, '--add-gnu-debuglink', sdebug, sfile))

    def update_databases(self, content, action):
        ''' DEPRECATED: use post_update_databases() instead '''
        self.post_update_databases(content, action)

    def pre_update_databases(self, content, action):
        ''' Update common databases before merge '''
        if not TRIGGERS:
            return

        adjcontent = '\n'.join(content)
        install_info = misc.whereis('install-info', False, True)
        install_info_regex = '(?:^|\\s)(.*share/info/.*)(?:$|\\s)'
        message.sub_debug('install-info', install_info or '')
        match = misc.string_search(install_info_regex, adjcontent, escape=False)
        if match and install_info:
            message.sub_debug(match)
            for m in match:
                if not os.path.exists(ROOT_DIR + m):
                    message.sub_warning('File does not exist', m)
                    continue
                infodir = sys.prefix + '/share/info/dir'
                message.sub_info(_('Deleting info page'), m)
                misc.system_trigger((install_info, '--delete', m, infodir))

        xdg_mime = misc.whereis('xdg-mime', False, True)
        xdg_mime_regex = '(?:^|\\s)(.*/mime/packages/.*\\.xml)(?:$|\\s)'
        message.sub_debug('xdg-mime', xdg_mime or '')
        match = misc.string_search(xdg_mime_regex, adjcontent, escape=False)
        if match and xdg_mime:
            done = []
            for m in match:
                if m in done:
                    continue
                elif action == 'remove':
                    message.sub_info(_('Uninstalling XDG MIMEs'), m)
                    misc.system_trigger((xdg_mime, 'uninstall', m))

    def post_update_databases(self, content, action):
        ''' Update common databases after merge'''
        if not TRIGGERS:
            return

        adjcontent = '\n/'.join(content)
        ldconfig = misc.whereis('ldconfig', False, True)
        ldconfig_regex = '(.*\\.so)(?:$|\\s)'
        message.sub_debug('ldconfig', ldconfig or '')
        match = misc.string_search(ldconfig_regex, adjcontent, escape=False)
        if match and ldconfig:
            message.sub_info(_('Updating shared libraries cache'))
            message.sub_debug(match)
            misc.system_trigger((ldconfig))

        mandb = misc.whereis('mandb', False, True)
        mandb_regex = '(.*share/man.*)(?:$|\\s)'
        message.sub_debug('mandb', mandb or '')
        match = misc.string_search(mandb_regex, adjcontent, escape=False)
        if match and mandb:
            message.sub_info(_('Updating manual pages database'))
            message.sub_debug(match)
            misc.system_trigger((mandb, '--quiet'))

        desktop_database = misc.whereis('update-desktop-database', False, True)
        desktop_database_regex = '(.*share/applications/.*)(?:$|\\s)'
        message.sub_debug('update-desktop-database', desktop_database or '')
        match = misc.string_search(desktop_database_regex, adjcontent, escape=False)
        if match and desktop_database:
            message.sub_info(_('Updating desktop database'))
            message.sub_debug(match)
            misc.system_trigger((desktop_database, sys.prefix + '/share/applications'))

        mime_database = misc.whereis('update-mime-database', False, True)
        mime_database_regex = '(.*share/mime.*)(?:$|\\s)'
        message.sub_debug('update-mime-database', mime_database or '')
        match = misc.string_search(mime_database_regex, adjcontent, escape=False)
        if match and mime_database:
            message.sub_info(_('Updating MIME database'))
            message.sub_debug(match)
            misc.system_trigger((mime_database, sys.prefix + '/share/mime'))

        icon_resources = misc.whereis('xdg-icon-resource', False, True)
        message.sub_debug('xdg-icon-resources', icon_resources or '')
        icon_cache = misc.whereis('gtk-update-icon-cache', False, True)
        message.sub_debug('gtk-update-icon-cache', icon_cache or '')
        icons_regex = '(?:^|\\s)(.*share/icons/(?:[^/]+))/.*(?:$|\\s)'
        match = misc.string_search(icons_regex, adjcontent, escape=False)
        if match and (icon_resources or icon_cache):
            done = []
            for m in match:
                if m in done:
                    continue
                base = os.path.basename(m)
                if icon_resources:
                    message.sub_info(_('Updating icon resources'), base)
                    misc.system_trigger((icon_resources, 'forceupdate', '--theme', base))
                if (action == 'merge' or action == 'upgrade') \
                    and os.path.isfile(ROOT_DIR + m + '/index.theme') and icon_cache:
                    message.sub_info(_('Updating icons cache'), base)
                    misc.system_trigger((icon_cache, '-q', '-t', '-i', '-f', m))
                done.append(m)

        xdg_mime = misc.whereis('xdg-mime', False, True)
        xdg_mime_regex = '(?:^|\\s)(.*/mime/packages/.*\\.xml)(?:$|\\s)'
        message.sub_debug('xdg-mime', xdg_mime or '')
        match = misc.string_search(xdg_mime_regex, adjcontent, escape=False)
        if match and xdg_mime:
            done = []
            for m in match:
                if m in done:
                    continue
                if action == 'merge':
                    message.sub_info(_('Installing XDG MIMEs'), m)
                    misc.system_trigger((xdg_mime, 'install', '--novendor', m))
                elif action == 'upgrade':
                    message.sub_info(_('Updating XDG MIMEs'), m)
                    misc.system_trigger((xdg_mime, 'install', '--novendor', m))
                done.append(m)

        gio_querymodules = misc.whereis('gio-querymodules', False, True)
        gio_querymodules_regex = '(?:^|\\s)(.*/gio/modules/.*)(?:$|\\s)'
        message.sub_debug('gio-querymodules', gio_querymodules or '')
        match = misc.string_search(gio_querymodules_regex, adjcontent, escape=False)
        if match and gio_querymodules:
            message.sub_info(_('Updating GIO modules cache'))
            message.sub_debug(match)
            misc.system_trigger((gio_querymodules, os.path.dirname(match[0])))

        pango_querymodules = misc.whereis('pango-querymodules', False, True)
        pango_querymodules_regex = '(?:^|\\s)(.*/pango/.*/modules/.*)(?:$|\\s)'
        message.sub_debug('pango-querymodules', pango_querymodules or '')
        match = misc.string_search(pango_querymodules_regex, adjcontent, escape=False)
        if match and pango_querymodules:
            message.sub_info(_('Updating pango modules cache'))
            message.sub_debug(match)
            misc.system_trigger((pango_querymodules, '--update-cache'))

        gtk2_immodules = misc.whereis('gtk-query-immodules-2.0', False, True)
        gtk2_immodules_regex = '(?:^|\\s)(.*/gtk-2.0/.*/immodules/.*)(?:$|\\s)'
        message.sub_debug('gtk-query-imodules-2.0', gtk2_immodules or '')
        match = misc.string_search(gtk2_immodules_regex, adjcontent, escape=False)
        if match and gtk2_immodules:
            message.sub_info(_('Updating GTK-2.0 imodules cache'))
            message.sub_debug(match)
            misc.dir_create(ROOT_DIR + '/etc/gtk-2.0')
            misc.system_trigger(gtk2_immodules + \
                ' > /etc/gtk-2.0/gtk.immodules', shell=True)

        gtk3_immodules = misc.whereis('gtk-query-immodules-3.0', False, True)
        gtk3_immodules_regex = '(?:^|\\s)(.*/gtk-3.0/.*/immodules/.*)(?:$|\\s)'
        message.sub_debug('gtk-query-imodules-3.0', gtk3_immodules or '')
        match = misc.string_search(gtk3_immodules_regex, adjcontent, escape=False)
        if match and gtk3_immodules:
            message.sub_info(_('Updating GTK-3.0 imodules cache'))
            message.sub_debug(match)
            misc.dir_create(ROOT_DIR + '/etc/gtk-3.0')
            misc.system_trigger(gtk3_immodules + \
                ' > /etc/gtk-3.0/gtk.immodules', shell=True)

        gdk_pixbuf = misc.whereis('gdk-pixbuf-query-loaders', False, True)
        gdk_pixbuf_regex = '(?:^|\\s)(.*/gdk-pixbuf.*)(?:$|\\s)'
        message.sub_debug('gdk-pixbuf-query-loaders', gdk_pixbuf or '')
        match = misc.string_search(gdk_pixbuf_regex, adjcontent, escape=False)
        if match and gdk_pixbuf:
            message.sub_info(_('Updating gdk pixbuffer loaders'))
            message.sub_debug(match)
            misc.system_trigger((gdk_pixbuf, '--update-cache'))

        glib_schemas = misc.whereis('glib-compile-schemas', False, True)
        glib_schemas_regex = '(?:^|\\s)(.*/schemas)/.*(?:$|\\s)'
        message.sub_debug('glib-compile-schemas', glib_schemas or '')
        match = misc.string_search(glib_schemas_regex, adjcontent, escape=False)
        if match and glib_schemas:
            message.sub_info(_('Updating GSettings schemas'))
            message.sub_debug(match)
            misc.system_trigger((glib_schemas, match[0]))

        install_info = misc.whereis('install-info', False, True)
        install_info_regex = '(?:^|\\s)(.*share/info/.*)(?:$|\\s)'
        message.sub_debug('install-info', install_info or '')
        match = misc.string_search(install_info_regex, adjcontent, escape=False)
        if match and install_info:
            message.sub_debug(match)
            for m in match:
                infodir = sys.prefix + '/share/info/dir'
                message.sub_info(_('Installing info page'), m)
                misc.system_trigger((install_info, m, infodir))

        udevadm = misc.whereis('udevadm', False, True)
        udevadm_regex = '(?:^|\\s)(.*/udev/rules.d/.*)(?:$|\\s)'
        message.sub_debug('udevadm', udevadm or '')
        match = misc.string_search(udevadm_regex, adjcontent, escape=False)
        if match and udevadm:
            if os.path.exists(ROOT_DIR + 'run/udev/control') \
            or os.path.exists(ROOT_DIR + 'var/run/udev/control'):
                message.sub_info(_('Reloading udev rules and hwdb'))
                message.sub_debug(match)
                misc.system_trigger((udevadm, 'control', '--reload'))

        mkinitfs_run = False
        depmod = misc.whereis('depmod', False, True)
        depmod_regex = '(?:^|\\s)(?:/)?(?:usr/?)?lib/modules/(.*?)/.*(?:$|\\s)'
        message.sub_debug('depmod', depmod or '')
        match = misc.string_search(depmod_regex, adjcontent, escape=False)
        if match and depmod:
            message.sub_info(_('Updating module dependencies'))
            message.sub_debug(match)
            misc.system_trigger((depmod, match[0]))
            mkinitfs_run = True

        # distribution specifiec
        mkinitfs = misc.whereis('mkinitfs', False, True)
        mkinitfs_regex = '(?:^|\\s)(?:/)?(boot/vmlinuz-(.*)|etc/mkinitfs/.*)(?:$|\\s)'
        message.sub_debug('mkinitfs', mkinitfs or '')
        match = misc.string_search(mkinitfs_regex, adjcontent, escape=False)
        if (match or mkinitfs_run) and mkinitfs:
            message.sub_info(_('Updating initramfs image'))
            message.sub_debug(match or mkinitfs_run)
            if match and match[0][1]:
                # new kernel being installed
                misc.system_trigger((mkinitfs, '-k', match[0][1]))
            else:
                misc.system_trigger((mkinitfs))

        grub_mkconfig = misc.whereis('grub-mkconfig', False, True)
        grub_mkconfig_regex = '(?:^|\\s)(?:/)?(boot/.*|etc/grub.d/.*)(?:$|\\s)'
        message.sub_debug('grub-mkconfig', grub_mkconfig or '')
        match = misc.string_search(grub_mkconfig_regex, adjcontent, escape=False)
        if match and grub_mkconfig:
            message.sub_info(_('Updating GRUB configuration'))
            message.sub_debug(match)
            misc.dir_create(ROOT_DIR + '/boot/grub')
            misc.system_trigger((grub_mkconfig, '-o', '/boot/grub/grub.cfg'))

    def remove_target_file(self, sfile):
        ''' Remove target file '''
        sfull = ROOT_DIR + sfile
        if os.path.isfile(sfull):
            message.sub_debug(_('Removing'), sfull)
            os.unlink(sfull)

    def remove_target_dir(self, sdir):
        ''' Remove target directory '''
        sfull = ROOT_DIR + sdir
        if os.path.isdir(sfull) and not os.listdir(sfull):
            message.sub_debug(_('Removing'), sfull)
            if os.path.islink(sfull):
                os.unlink(sfull)
            else:
                os.rmdir(sfull)
            self.remove_target_dir(os.path.dirname(sdir))

    def remove_target_link(self, slink):
        ''' Remove target symlink '''
        sfull = ROOT_DIR + slink
        if os.path.islink(sfull) and \
            not os.path.exists(ROOT_DIR + '/' + os.readlink(sfull)):
            message.sub_debug(_('Removing'), sfull)
            os.unlink(sfull)

    def clean(self):
        ''' Clean target files '''
        if os.path.isdir(self.install_dir) and self.do_install:
            message.sub_info(_('Removing'), self.install_dir)
            misc.dir_remove(self.install_dir)
        elif os.path.isdir(self.install_dir) and not self.do_prepare:
            message.sub_info(_('Removing'), self.install_dir)
            misc.dir_remove(self.install_dir)
        else:
            message.sub_debug(_('Dirctory is OK'), self.install_dir)

        if os.path.isdir(self.source_dir) and self.do_prepare:
            message.sub_info(_('Removing'), self.source_dir)
            misc.dir_remove(self.source_dir)
        elif os.path.isdir(self.source_dir) and not self.do_install:
            message.sub_info(_('Removing'), self.source_dir)
            misc.dir_remove(self.source_dir)
        else:
            message.sub_debug(_('Dirctory is OK'), self.source_dir)

    def prepare(self):
        ''' Prepare target sources '''
        message.sub_info(_('Checking dependencies'))
        dependencies = database.remote_mdepends(self.target, \
            cdepends=self.do_check)

        if dependencies and self.do_depends:
            message.sub_info(_('Building dependencies'), dependencies)
            self.autosource(dependencies, automake=True)
            message.sub_info(_('Resuming %s preparations at') % \
                os.path.basename(self.target), datetime.today())
        elif dependencies:
            message.sub_warning(_('Dependencies missing'), dependencies)

        misc.dir_create(self.source_dir, DEMOTE)
        misc.dir_create(self.sources_dir, DEMOTE)

        message.sub_info(_('Preparing PGP keys'))
        if self.target_pgpkeys and self.verify:
            misc.gpg_receive(self.target_pgpkeys, KEYSERVERS)

        message.sub_info(_('Preparing sources'))
        for src_url in self.target_sources:
            src_base = os.path.basename(src_url)
            local_file = os.path.join(self.sources_dir, src_base)
            src_file = os.path.join(self.target_dir, src_base)
            link_file = os.path.join(self.source_dir, src_base)

            if not os.path.isfile(src_file):
                message.sub_debug(_('Fetching'), src_url)
                if self.mirror:
                    misc.fetch(src_url, local_file, MIRRORS, 'distfiles/')
                else:
                    misc.fetch(src_url, local_file)

            if os.path.islink(link_file):
                message.sub_debug(_('Already linked'), src_file)
            elif os.path.isdir('%s/.git' % local_file):
                message.sub_debug(_('Copying'), src_file)
                shutil.copytree(local_file, link_file, True)
            elif os.path.isfile(src_file):
                message.sub_debug(_('Linking'), src_file)
                os.symlink(src_file, link_file)
            elif os.path.isfile(local_file):
                message.sub_debug(_('Linking'), local_file)
                os.symlink(local_file, link_file)

            if src_url.endswith(('.asc', '.sig')) and self.verify:
                message.sub_debug(_('Verifying'), src_url)
                misc.gpg_verify(link_file)

            if misc.archive_supported(link_file):
                message.sub_debug(_('Extracting'), link_file)
                misc.archive_decompress(link_file, self.source_dir, DEMOTE)

    def compile(self):
        ''' Compile target sources '''
        misc.system_command((misc.whereis('bash'), '-e', '-c', 'source ' + \
            self.srcbuild + ' && umask 0022 && src_compile'), \
            cwd=self.source_dir, demote=DEMOTE)

    def check(self):
        ''' Check target sources '''
        misc.system_command((misc.whereis('bash'), '-e', '-c', 'source ' + \
            self.srcbuild + ' && umask 0022 && src_check'), \
            cwd=self.source_dir, demote=DEMOTE)

    def install(self):
        ''' Install targets files '''
        misc.dir_create(self.install_dir, DEMOTE)

        # re-create host system symlinks to prevent mismatch of entries in the
        # footprint and ld.so.cache for libraries leading to undetectable
        # runtime dependencies
        for libdir in ('/lib64', '/usr/lib64'):
            realdir = os.path.realpath(libdir)
            instsym = '%s%s' % (self.install_dir, libdir)
            instreal = '%s%s' % (self.install_dir, realdir)
            if not realdir == libdir:
                misc.dir_create(instreal)
                os.symlink(os.path.basename(instreal), instsym)

        misc.system_command((misc.whereis('bash'), '-e', '-c', 'source ' + \
            self.srcbuild + ' && umask 0022 && src_install'), \
            cwd=self.source_dir)

        for libdir in ('/lib64', '/usr/lib64'):
            realdir = os.path.realpath(libdir)
            instsym = '%s%s' % (self.install_dir, libdir)
            instreal = '%s%s' % (self.install_dir, realdir)
            if os.path.exists(instreal) and not os.listdir(instreal):
                os.unlink(instsym)
                os.rmdir(instreal)

        if self.compress_man:
            message.sub_info(_('Compressing manual pages'))
            manpath = misc.whereis('manpath', fallback=False)
            # if manpath (provided by man-db) is not present fallback to
            # something sane
            if not manpath:
                mpaths = ('/usr/local/share/man', '/local/share/man', \
                    '/usr/share/man', '/share/man', '/usr/man', '/man')
            else:
                mpaths = misc.system_output((manpath, '--global')).split(':')

            for sdir in mpaths:
                for sfile in misc.list_files(self.install_dir + sdir):
                    if not sfile.endswith('.gz') and os.path.isfile(sfile):
                        message.sub_debug(_('Compressing'), sfile)
                        misc.archive_compress((sfile,), sfile + '.gz', '')
                        os.unlink(sfile)
                    elif os.path.islink(sfile) and \
                        not os.path.isfile(os.path.realpath(sfile)):
                        message.sub_debug(_('Adjusting link'), sfile)
                        link = os.readlink(sfile)
                        if not sfile.endswith('.gz'):
                            os.unlink(sfile)
                            os.symlink(link + '.gz', sfile)
                        else:
                            os.unlink(sfile)
                            os.symlink(link, sfile)

        message.sub_info(_('Indexing content'))
        target_content = {}
        for sfile in misc.list_files(self.install_dir):
            if sfile.endswith((self.target_footprint, self.target_metadata)):
                continue
            # remove common conflict files/directories
            elif sfile.endswith('/.packlist') \
                or sfile.endswith('/perllocal.pod') \
                or sfile.endswith('/share/info/dir'):
                os.unlink(sfile)
                continue
            target_content[sfile] = misc.file_mime(sfile)

        if self.strip_binaries or self.strip_shared or \
            self.strip_static or self.strip_rpath:
            message.sub_info(_('Stripping binaries and libraries'))
            strip = misc.whereis('strip')
            scanelf = misc.whereis('scanelf')
            for sfile in target_content:
                smime = target_content[sfile]
                if os.path.islink(sfile):
                    continue

                if smime == 'application/x-executable' and self.strip_binaries:
                    self.split_debug_symbols(sfile)
                    message.sub_debug(_('Stripping executable'), sfile)
                    misc.system_command((strip, '--strip-all', sfile))
                elif smime == 'application/x-sharedlib' and self.strip_shared:
                    self.split_debug_symbols(sfile)
                    message.sub_debug(_('Stripping shared library'), sfile)
                    misc.system_command((strip, '--strip-unneeded', sfile))
                elif smime == 'application/x-archive' and self.strip_static:
                    self.split_debug_symbols(sfile)
                    message.sub_debug(_('Stripping static library'), sfile)
                    misc.system_command((strip, '--strip-debug', sfile))

                if (smime == 'application/x-executable' or \
                    smime == 'application/x-sharedlib' \
                    or smime == 'application/x-archive') and self.strip_rpath:
                    # do not check if RPATH is present at all to avoid
                    # spawning scanelf twice
                    message.sub_debug(_('Stripping RPATH'), sfile)
                    misc.system_command((scanelf, '-CBXrq', sfile))

        message.sub_info(_('Checking runtime dependencies'))
        missing_detected = False
        required = []
        for sfile in target_content:
            if os.path.islink(sfile):
                continue

            smime = target_content[sfile]
            if smime == 'application/x-executable' or \
                smime == 'application/x-sharedlib':
                libraries = misc.system_scanelf(sfile, sflags='-L')
                if not libraries:
                    continue # static binary
                required.extend(libraries.split(','))

            elif smime == 'text/plain' or smime == 'text/x-shellscript' \
                or smime == 'text/x-python' or smime == 'text/x-perl' \
                or smime == 'text/x-php' or smime == 'text/x-ruby' \
                or smime == 'text/x-lua' or smime == 'text/x-tcl' \
                or smime == 'text/x-awk' or smime == 'text/x-gawk':
                # https://en.wikipedia.org/wiki/Comparison_of_command_shells
                bang_regexp = 'sh|bash|dash|ksh|csh|tcsh|tclsh|scsh|fish|zsh'
                bang_regexp += '|ash|python|perl|php|ruby|lua|wish|(?:g)?awk'
                bang_regexp += '|gbr2|gbr3'
                # parse the shebang and split it to 2 groups:
                # 1. full match, used to replace it with something that will work
                # 2. base of the interpreter (e.g. bash), used to find match in the target or host
                omatch = misc.file_search('(^#!.*(?: |\\t|/)((?:' + bang_regexp + ')(.* |.*\\t)?))(?:.*\\s)', \
                    sfile, exact=False, escape=False)
                if omatch:
                    sfull = omatch[0][0].strip()
                    sbase = omatch[0][1].strip()
                    smatch = False
                    # now look for the interpreter in the target
                    for s in target_content:
                        if s.endswith('/' + sbase) and os.access(s, os.X_OK):
                            smatch = s.replace(self.install_dir, '')
                            break
                    # if that fails look for the interpreter on the host
                    # FIXME: if the interpreter found by misc.whereis() is not
                    # ownded by a local target try to find interpreter that is
                    if not smatch:
                        smatch = misc.whereis(sbase, False)

                    # now update the shebang if possible
                    if smatch:
                        message.sub_debug(_('Attempting shebang correction on'), sfile)
                        misc.file_substitute('^' + sfull, '#!' + smatch, sfile)
                        required.append(smatch)
                    else:
                        required.append(sbase) # fake non-existing match

        checked = []
        for req in required:
            # checking req being '' is neccessary because a bug in scanelf that
            # produces a list with empty entry, it happens when '-L' is used
            if req in checked or not req:
                continue
            rreq = req
            if os.path.exists(req):
                rreq = os.path.realpath(req)
            match = database.local_belongs('(?:^|\\s)%s(?:$|\\s)' % re.escape(rreq), escape=False)
            if match and len(match) > 1:
                message.sub_warning(_('Multiple providers for %s') % rreq, match)
                if self.target_name in match:
                    match = self.target_name
                else:
                    match = match[0]
            match = misc.string_convert(match)

            if match == self.target_name \
                or '%s%s' % (self.install_dir, rreq) in target_content:
                message.sub_debug(_('Dependency needed but in target'), rreq)
            elif match and match in self.target_depends:
                message.sub_debug(_('Dependency needed but in dependencies'), match)
            elif match and not match in self.target_depends:
                message.sub_debug(_('Dependency needed but in local'), match)
                self.target_depends.append(match)
            elif self.ignore_missing:
                message.sub_warning(_('Dependency needed, not in any local'), rreq)
            else:
                message.sub_critical(_('Dependency needed, not in any local'), rreq)
                missing_detected = True
            checked.append(req)

        if missing_detected:
            sys.exit(2)

        if self.python_compile:
            message.sub_info(_('Byte-compiling Python modules'))
            for sfile in target_content:
                for spath in site.getsitepackages():
                    if not spath in sfile:
                        continue
                    message.sub_debug(_('Compiling Python file'), sfile)
                    # force build the caches to prevent access time issues with
                    # .pyc files being older that .py files because .py files
                    # where modified after the usual installation procedure
                    compileall.compile_file(sfile, force=True, quiet=True)

        message.sub_info(_('Assembling metadata'))
        misc.dir_create(os.path.join(self.install_dir, 'var/local/spm', self.target_name))
        metadata = open(os.path.join(self.install_dir, self.target_metadata), 'w')
        metadata.write('version=%s\n' % self.target_version)
        metadata.write('release=%s\n' % self.target_release)
        metadata.write('description=%s\n' % self.target_description)
        metadata.write('depends=%s\n' % misc.string_convert(self.target_depends))
        metadata.write('size=%d\n' % misc.dir_size(self.install_dir))
        metadata.close()

        message.sub_info(_('Assembling footprint'))
        # due to creations and deletions of files, when byte-compiling
        # Python modules for an example, do not re-use target_content
        footprint = misc.list_files(self.install_dir)
        for sfile in footprint:
            # remove footprint and metadata, they are not wanted in the footprint
            if sfile.endswith((self.target_footprint, self.target_metadata)):
                footprint.remove(sfile)
        misc.file_write(os.path.join(self.install_dir, self.target_footprint), \
            '\n'.join(sorted(footprint)).replace(self.install_dir, ''))

        message.sub_info(_('Assembling depends'))
        misc.file_write('%s.depends' % self.target_tarball, \
            misc.string_convert(self.target_depends))

        message.sub_info(_('Compressing tarball'))
        misc.dir_create(os.path.dirname(self.target_tarball))
        misc.archive_compress((self.install_dir,), self.target_tarball, \
            self.install_dir)
        if SIGN:
            message.sub_info(_('Signing tarball'))
            misc.gpg_sign(self.target_tarball, SIGN)

    def merge(self):
        ''' Merget target to system '''
        message.sub_info(_('Indexing content'))
        new_content = misc.archive_list(self.target_tarball)
        old_content = database.local_metadata(self.target_name, 'footprint')

        if CONFLICTS:
            conflict_detected = False
            message.sub_info(_('Checking for conflicts'))
            for target in database.local_all(basename=True):
                if target == self.target_name:
                    continue

                message.sub_debug(_('Checking against'), target)
                footprint = database.local_metadata(target, 'footprint').splitlines()
                for sfile in new_content:
                    sfull = '/' + sfile
                    if sfull in footprint:
                        message.sub_critical(_('File/link conflict with %s') % target, sfull)
                        conflict_detected = True

            if conflict_detected:
                sys.exit(2)

        # store state installed or not, it must be done before the decompression
        target_upgrade = database.local_search(self.target_name)

        if target_upgrade and SCRIPTS \
            and misc.file_search('\npre_upgrade()', self.srcbuild, escape=False):
            message.sub_info(_('Executing pre_upgrade()'))
            misc.system_script(self.srcbuild, 'pre_upgrade')
        elif misc.file_search('\npre_install()', self.srcbuild, escape=False) \
            and SCRIPTS:
            message.sub_info(_('Executing pre_install()'))
            misc.system_script(self.srcbuild, 'pre_install')

        if target_upgrade:
            if old_content:
                self.pre_update_databases(old_content.splitlines(), 'upgrade')
        else:
            if old_content:
                self.pre_update_databases(old_content.splitlines(), 'merge')

        if BACKUP:
            message.sub_info(_('Creating backup files'))
            check = []
            for sfile in new_content:
                sfull = os.path.join(ROOT_DIR, sfile)
                if not os.path.isfile(sfull) or os.path.islink(sfull):
                    continue
                if sfile.endswith('.conf') or sfile in self.target_backup:
                    check.append(sfile)

            if check:
                content = misc.archive_content(self.target_tarball, check)
                counter = 0
                for sfile in check:
                    sfull = os.path.join(ROOT_DIR, sfile)
                    if not misc.file_read(sfull) == content[counter]:
                        message.sub_debug(_('Backing up'), sfull)
                        shutil.copy2(sfull, sfull + '.backup')
                    counter += 1

        message.sub_info(_('Decompressing tarball'))
        misc.archive_decompress(self.target_tarball, ROOT_DIR)

        if target_upgrade:
            message.sub_info(_('Removing obsolete files and directories'))
            remove_content = []
            for sfile in old_content.splitlines():
                sfull = ROOT_DIR + sfile
                sresolved = os.path.realpath(sfull).replace(ROOT_DIR, '')
                if sresolved in new_content:
                    continue
                elif sfile.lstrip('/') in new_content:
                    continue
                # the footprint and metadata files will be deleted otherwise,
                # also making sure ROOT_DIR different than / is respected
                if LOCAL_DIR in sfull:
                    continue
                # never delete files in the pseudo filesystems
                elif sfile.startswith(('/dev/', '/sys/', '/proc/')):
                    continue
                remove_content.append(sfile)

            for sfile in remove_content:
                self.remove_target_file(sfile)
            for sfile in reversed(remove_content):
                self.remove_target_dir(os.path.dirname(sfile))
            for sfile in reversed(remove_content):
                self.remove_target_link(sfile)

            if misc.file_search('\npost_upgrade()', self.srcbuild, escape=False) \
                and SCRIPTS:
                message.sub_info(_('Executing post_upgrade()'))
                misc.system_script(self.srcbuild, 'post_upgrade')
        elif misc.file_search('\npost_install()', self.srcbuild, escape=False) \
            and SCRIPTS:
            message.sub_info(_('Executing post_install()'))
            misc.system_script(self.srcbuild, 'post_install')

        if target_upgrade:
            self.post_update_databases(new_content, 'upgrade')
        else:
            self.post_update_databases(new_content, 'merge')

        if target_upgrade:
            message.sub_info(_('Checking reverse dependencies'))
            needs_rebuild = database.local_rdepends(self.target_name)

            if needs_rebuild and self.do_reverse:
                for target in needs_rebuild:
                    break_free = False
                    message.sub_debug(_('Checking'), target)
                    for sfile in database.local_metadata(target, 'footprint').split():
                        # looping trough files will continue otherwise
                        if break_free:
                            break
                        elif not os.path.exists(sfile) or os.path.isdir(sfile):
                            continue
                        smime = misc.file_mime(sfile)
                        if smime == 'application/x-executable' or \
                            smime == 'application/x-sharedlib':
                            libraries = misc.system_scanelf(sfile)
                            if not libraries:
                                continue # static binary
                            for lib in libraries.split(','):
                                if not database.local_belongs(lib):
                                    self.autosource([target], automake=True)
                                    break_free = True
                                    break
            elif needs_rebuild:
                message.sub_warning(_('Targets may need rebuild'), needs_rebuild)

        # do not wait for the cache notifier to kick in
        database.LOCAL_CACHE = {}

    def remove(self):
        ''' Remove target files from system '''
        if not database.local_search(self.target_name):
            message.sub_critical(_('Already removed'), self.target_name)
            sys.exit(2)

        message.sub_info(_('Checking dependencies'))
        depends_detected = database.local_rdepends(self.target_name, indirect=True)
        # on autoremove ignore reverse dependencies asuming they have been
        # processed already and passed to the class initializer in proper order
        # by the initial checker with indirect reverse dependencies on
        if depends_detected and self.do_reverse and not self.autoremove:
            message.sub_info(_('Removing reverse dependencies'), depends_detected)
            self.autosource(depends_detected, autoremove=True)
            message.sub_info(_('Resuming %s removing at') % \
                os.path.basename(self.target), datetime.today())
        elif depends_detected and not self.autoremove:
            message.sub_critical(_('Other targets depend on %s') % \
                self.target_name, depends_detected)
            sys.exit(2)

        if misc.file_search('\npre_remove()', self.srcbuild, escape=False) \
            and SCRIPTS:
            message.sub_info(_('Executing pre_remove()'))
            misc.system_script(self.srcbuild, 'pre_remove')

        target_content = []
        footprint = os.path.join(ROOT_DIR, self.target_footprint)
        if os.path.isfile(footprint):
            message.sub_info(_('Indexing content'))
            target_content = misc.file_readlines(footprint)

        if target_content:
            self.pre_update_databases(target_content, 'remove')

            message.sub_info(_('Removing files'))
            for sfile in target_content:
                self.remove_target_file(sfile)

            message.sub_info(_('Removing directories'))
            for sfile in reversed(target_content):
                self.remove_target_dir(os.path.dirname(sfile))

            message.sub_info(_('Removing links'))
            for sfile in reversed(target_content):
                self.remove_target_link(sfile)

        if database.local_search(self.target_name):
            message.sub_info(_('Removing footprint and metadata'))
            misc.dir_remove(os.path.join(LOCAL_DIR, self.target_name))

        if misc.file_search('\npost_remove()', self.srcbuild, escape=False) \
            and SCRIPTS:
            message.sub_info(_('Executing post_remove()'))
            misc.system_script(self.srcbuild, 'post_remove')

        if target_content:
            self.post_update_databases(target_content, 'remove')

        # do not wait for the cache notifier to kick in
        database.LOCAL_CACHE = {}

    def main(self):
        ''' Execute action for every target '''
        # resolve aliases and meta groups
        if 'world' in self.targets:
            position = self.targets.index('world')
            self.targets[position:position+1] = \
                database.local_all(basename=True)

        for alias in database.remote_aliases():
            if alias in self.targets:
                position = self.targets.index(alias)
                self.targets[position:position+1] = \
                    database.remote_alias(alias)

        for target in self.targets:
            # make sure target is absolute path
            if os.path.isdir(target):
                target = os.path.abspath(target)

            target_name = os.path.basename(target)
            if target_name in IGNORE:
                message.sub_warning(_('Ignoring target'), target_name)
                continue

            if not database.remote_search(target):
                message.sub_critical(_('Invalid target'), target)
                sys.exit(2)

            # set target properties
            self.target = target
            self.target_name = os.path.basename(target)
            self.target_dir = database.remote_search(target)
            self.srcbuild = os.path.join(self.target_dir, 'SRCBUILD')
            self.source_dir = os.path.join(BUILD_DIR, self.target_name, 'source')
            self.install_dir = os.path.join(BUILD_DIR, self.target_name, 'install')
            self.target_version = database.remote_metadata(self.target_dir, 'version')
            self.target_release = database.remote_metadata(self.target_dir, 'release')
            self.target_description = database.remote_metadata(self.target_dir, 'description')
            self.target_depends = database.remote_metadata(self.target_dir, 'depends')
            self.target_makedepends = database.remote_metadata(self.target_dir, 'makedepends')
            self.target_sources = database.remote_metadata(self.target_dir, 'sources')
            self.target_pgpkeys = database.remote_metadata(self.target_dir, 'pgpkeys')
            self.target_options = database.remote_metadata(self.target_dir, 'options')
            self.target_backup = database.remote_metadata(self.target_dir, 'backup')
            self.target_footprint = os.path.join('var/local/spm', self.target_name, 'footprint')
            self.target_metadata = os.path.join('var/local/spm', self.target_name, 'metadata')
            self.sources_dir = os.path.join(CACHE_DIR, 'sources', self.target_name)
            self.target_tarball = os.path.join(CACHE_DIR, 'tarballs/' + os.uname()[4], \
            self.target_name + '_' + self.target_version + '.tar.bz2')

            if database.local_uptodate(self.target) and self.do_update:
                message.sub_warning(_('Target is up-to-date'), self.target)
                continue

            for option in self.target_options:
                if option == 'verify' and not self.verify:
                    message.sub_warning(_('Overriding VERIFY to'), _('True'))
                    self.verify = True
                elif option == '!verify' and self.verify:
                    message.sub_warning(_('Overriding VERIFY to'), _('False'))
                    self.verify = False

                if option == 'mirror' and not self.mirror:
                    message.sub_warning(_('Overriding MIRROR to'), _('True'))
                    self.mirror = True
                elif option == '!mirror' and self.mirror:
                    message.sub_warning(_('Overriding MIRROR to'), _('False'))
                    self.mirror = False

                if option == 'debug' and not self.split_debug:
                    message.sub_warning(_('Overriding SPLIT_DEBUG to'), _('True'))
                    self.split_debug = True
                elif option == '!debug' and self.split_debug:
                    message.sub_warning(_('Overriding SPLIT_DEBUG to'), _('False'))
                    self.split_debug = False

                if option == 'binaries' and not self.strip_binaries:
                    message.sub_warning(_('Overriding STRIP_BINARIES to'), _('True'))
                    self.strip_binaries = True
                elif option == '!binaries' and self.strip_binaries:
                    message.sub_warning(_('Overriding STRIP_BINARIES to'), _('False'))
                    self.strip_binaries = False

                if option == 'shared' and not self.strip_shared:
                    message.sub_warning(_('Overriding STRIP_SHARED to'), _('True'))
                    self.strip_shared = True
                elif option == '!shared' and self.strip_shared:
                    message.sub_warning(_('Overriding STRIP_SHARED to'), _('False'))
                    self.strip_shared = False

                if option == 'static' and not self.strip_static:
                    message.sub_warning(_('Overriding STRIP_STATIC to'), _('True'))
                    self.strip_static = True
                elif option == '!static' and self.strip_static:
                    message.sub_warning(_('Overriding STRIP_STATIC to'), _('False'))
                    self.strip_static = False

                if option == 'rpath' and not self.strip_rpath:
                    message.sub_warning(_('Overriding STRIP_RPATH to'), _('True'))
                    self.strip_rpath = True
                elif option == '!rpath' and self.strip_rpath:
                    message.sub_warning(_('Overriding STRIP_RPATH to'), _('False'))
                    self.strip_rpath = False

                if option == 'man' and not self.compress_man:
                    message.sub_warning(_('Overriding COMPRESS_MAN to'), _('True'))
                    self.compress_man = True
                elif option == '!man' and self.compress_man:
                    message.sub_warning(_('Overriding COMPRESS_MAN to'), _('False'))
                    self.compress_man = False

                if option == 'missing' and not self.ignore_missing:
                    message.sub_warning(_('Overriding IGNORE_MISSING to'), _('True'))
                    self.ignore_missing = True
                elif option == '!missing' and self.ignore_missing:
                    message.sub_warning(_('Overriding IGNORE_MISSING to'), _('False'))
                    self.ignore_missing = False

                if option == 'pycompile' and not self.python_compile:
                    message.sub_warning(_('Overriding PYTHON_COMPILE to'), _('True'))
                    self.python_compile = True
                elif option == '!pycompile' and self.python_compile:
                    message.sub_warning(_('Overriding PYTHON_COMPILE to'), _('False'))
                    self.python_compile = False

            if self.do_clean:
                message.sub_info(_('Starting %s cleanup at') % \
                    self.target_name, datetime.today())
                self.clean()

            if self.do_prepare:
                message.sub_info(_('Starting %s preparations at') % \
                    self.target_name, datetime.today())
                self.prepare()

            if self.do_compile:
                if not misc.file_search('\nsrc_compile()', \
                    self.srcbuild, escape=False):
                    message.sub_warning(_('src_compile() not defined'))
                else:
                    message.sub_info(_('Starting %s compile at') % \
                        self.target_name, datetime.today())
                    os.putenv('SOURCE_DIR', self.source_dir)
                    os.putenv('INSTALL_DIR', self.install_dir)
                    os.putenv('CHOST', CHOST)
                    os.putenv('CFLAGS', CFLAGS)
                    os.putenv('CXXFLAGS', CXXFLAGS)
                    os.putenv('CPPFLAGS', CPPFLAGS)
                    os.putenv('LDFLAGS', LDFLAGS)
                    os.putenv('MAKEFLAGS', MAKEFLAGS)
                    self.compile()

            if self.do_check:
                if not misc.file_search('\nsrc_check()', \
                    self.srcbuild, escape=False):
                    message.sub_warning(_('src_check() not defined'))
                else:
                    message.sub_info(_('Starting %s check at') % \
                        self.target_name, datetime.today())
                    os.putenv('SOURCE_DIR', self.source_dir)
                    os.putenv('INSTALL_DIR', self.install_dir)
                    os.putenv('CHOST', CHOST)
                    os.putenv('CFLAGS', CFLAGS)
                    os.putenv('CXXFLAGS', CXXFLAGS)
                    os.putenv('CPPFLAGS', CPPFLAGS)
                    os.putenv('LDFLAGS', LDFLAGS)
                    os.putenv('MAKEFLAGS', MAKEFLAGS)
                    self.check()

            if self.do_install:
                if not misc.file_search('\nsrc_install()', \
                    self.srcbuild, escape=False):
                    message.sub_critical(_('src_install() not defined'))
                    sys.exit(2)

                message.sub_info(_('Starting %s install at') % \
                    self.target_name, datetime.today())
                os.putenv('SOURCE_DIR', self.source_dir)
                os.putenv('INSTALL_DIR', self.install_dir)
                os.putenv('CHOST', CHOST)
                os.putenv('CFLAGS', CFLAGS)
                os.putenv('CXXFLAGS', CXXFLAGS)
                os.putenv('CPPFLAGS', CPPFLAGS)
                os.putenv('LDFLAGS', LDFLAGS)
                os.putenv('MAKEFLAGS', MAKEFLAGS)
                self.install()

            if self.do_merge:
                message.sub_info(_('Starting %s merge at') % self.target_name, datetime.today())
                self.merge()

            if self.do_remove or self.autoremove:
                message.sub_info(_('Starting %s remove at') % self.target_name, datetime.today())
                self.remove()

            # reset values so that overrides apply only to single target
            self.verify = VERIFY
            self.mirror = MIRROR
            self.split_debug = SPLIT_DEBUG
            self.strip_binaries = STRIP_BINARIES
            self.strip_shared = STRIP_SHARED
            self.strip_static = STRIP_STATIC
            self.strip_rpath = STRIP_RPATH
            self.python_compile = PYTHON_COMPILE
            self.compress_man = COMPRESS_MAN
            self.ignore_missing = IGNORE_MISSING

wantscookie = '''
                       _           |
      -*~*-          _|_|_         |.===.       `  _ ,  '        ()_()
      (o o)          (o o)         {}o o{}     -  (o)o)  -       (o o)
--ooO--(_)--Ooo--ooO--(_)--Ooo--ooO--(_)--Ooo--ooO'(_)--Ooo--ooO--`o'--Ooo--
'''

class Binary(Source):
    ''' Class to handle binary tarballs '''
    def __init__(self, targets, do_merge=False, do_remove=False, \
        do_depends=False, do_reverse=False, do_update=False, autoremove=False):
        super(Binary, self).__init__(Source)
        self.targets = targets
        self.do_merge = do_merge
        self.do_remove = do_remove
        self.do_depends = do_depends
        self.do_reverse = do_reverse
        self.do_update = do_update
        self.autoremove = autoremove
        message.CATCH = CATCH
        misc.OFFLINE = OFFLINE
        misc.TIMEOUT = TIMEOUT
        misc.ROOT_DIR = ROOT_DIR
        misc.GPG_DIR = GPG_DIR
        misc.CATCH = CATCH
        database.ROOT_DIR = ROOT_DIR
        database.CACHE_DIR = CACHE_DIR
        database.LOCAL_DIR = LOCAL_DIR
        database.IGNORE = IGNORE

    def autobinary(self, targets, automake=False, autoremove=False):
        ''' Handle targets build/remove without affecting current object '''
        if automake:
            obj = Binary(targets, do_merge=True, do_depends=True, \
                do_reverse=self.do_reverse, do_update=False)
        else:
            obj = Binary(targets, do_reverse=self.do_reverse, \
                autoremove=autoremove)
        obj.main()

    def prepare(self):
        ''' Prepare target tarballs '''
        message.sub_info(_('Preparing tarballs'))
        src_base = self.target_name + '_' + self.target_version + '.tar.bz2'
        local_file = self.target_tarball

        message.sub_debug(_('Checking mirrors for'), src_base)
        found = False
        # usually that would not happend (see the mirrors config parser) but
        # since that's a module one can temper with MIRRORS
        if len(MIRRORS) < 1:
            message.sub_critical(_('At least one mirror is required'))
            sys.exit(2)
        sprefix = 'tarballs/%s/' % os.uname()[4]
        surl = '%s/%s/%s' % (MIRRORS[0], sprefix, src_base)
        sdepends = '%s.depends' % local_file
        if misc.url_ping(surl, MIRRORS, sprefix):
            found = True
            message.sub_debug(_('Fetching'), surl)
            misc.fetch(surl, local_file, MIRRORS, sprefix)
            misc.fetch('%s.depends' % surl, sdepends, MIRRORS, sprefix)
            if VERIFY:
                sigurl = '%s.sig' % surl
                sigfile = '%s.sig' % local_file
                message.sub_debug(_('Fetching'), sigurl)
                misc.fetch(sigurl, sigfile, MIRRORS, sprefix)
                message.sub_debug(_('Verifying'), local_file)
                misc.gpg_verify(local_file)

        if not found:
            message.sub_critical(_('Binary tarball not available available for'), self.target_name)
            sys.exit(2)

        message.sub_info(_('Checking dependencies'))
        missing = []
        depends = misc.file_read(sdepends).split()
        message.sub_debug(_('Dependencies'), depends)
        for m in depends:
            if not database.local_uptodate(m):
                missing.append(m)
        if missing and self.do_depends:
            message.sub_info(_('Fetching dependencies'), missing)
            self.autobinary(missing, automake=True)
            message.sub_info(_('Resuming %s preparations at') % \
                os.path.basename(self.target), datetime.today())
        elif missing:
            message.sub_warning(_('Dependencies missing'), missing)

    def main(self):
        ''' Execute action for every target '''
        # resolve aliases and meta groups
        if 'world' in self.targets:
            position = self.targets.index('world')
            self.targets[position:position+1] = \
                database.local_all(basename=True)

        for alias in database.remote_aliases():
            if alias in self.targets:
                position = self.targets.index(alias)
                self.targets[position:position+1] = \
                    database.remote_alias(alias)

        for target in self.targets:
            # make sure target is absolute path
            if os.path.isdir(target):
                target = os.path.abspath(target)

            target_name = os.path.basename(target)
            if target_name in IGNORE:
                message.sub_warning(_('Ignoring target'), target_name)
                continue

            if not database.remote_search(target):
                message.sub_critical(_('Invalid target'), target)
                sys.exit(2)

            # set target properties
            self.target = target
            self.target_name = os.path.basename(target)
            self.target_dir = database.remote_search(target)
            self.srcbuild = os.path.join(self.target_dir, 'SRCBUILD')
            self.source_dir = os.path.join(BUILD_DIR, self.target_name, 'source')
            self.install_dir = os.path.join(BUILD_DIR, self.target_name, 'install')
            self.target_version = database.remote_metadata(self.target_dir, 'version')
            self.target_release = database.remote_metadata(self.target_dir, 'release')
            self.target_description = database.remote_metadata(self.target_dir, 'description')
            self.target_depends = database.remote_metadata(self.target_dir, 'depends')
            self.target_makedepends = database.remote_metadata(self.target_dir, 'makedepends')
            self.target_sources = database.remote_metadata(self.target_dir, 'sources')
            self.target_pgpkeys = database.remote_metadata(self.target_dir, 'pgpkeys')
            self.target_options = database.remote_metadata(self.target_dir, 'options')
            self.target_backup = database.remote_metadata(self.target_dir, 'backup')
            self.target_footprint = os.path.join('var/local/spm', self.target_name, 'footprint')
            self.target_metadata = os.path.join('var/local/spm', self.target_name, 'metadata')
            self.sources_dir = os.path.join(CACHE_DIR, 'sources', self.target_name)
            self.target_tarball = os.path.join(CACHE_DIR, 'tarballs/' + os.uname()[4], \
            self.target_name + '_' + self.target_version + '.tar.bz2')

            if database.local_uptodate(self.target) and self.do_update:
                message.sub_warning(_('Target is up-to-date'), self.target)
                continue

            if self.do_merge:
                message.sub_info(_('Starting %s preparations at') % \
                    self.target_name, datetime.today())
                self.prepare()
                message.sub_info(_('Starting %s merge at') % \
                    self.target_name, datetime.today())
                self.merge()

            if self.do_remove or self.autoremove:
                message.sub_info(_('Starting %s remove at') % \
                    self.target_name, datetime.today())
                self.remove()


class Who(object):
    ''' Class for printing file owner '''
    def __init__(self, pattern, plain=False):
        self.pattern = pattern
        self.plain = plain
        message.CATCH = CATCH
        misc.OFFLINE = OFFLINE
        misc.TIMEOUT = TIMEOUT
        misc.ROOT_DIR = ROOT_DIR
        misc.GPG_DIR = GPG_DIR
        misc.CATCH = CATCH
        database.ROOT_DIR = ROOT_DIR
        database.CACHE_DIR = CACHE_DIR
        database.LOCAL_DIR = LOCAL_DIR
        database.IGNORE = IGNORE

    def main(self):
        ''' Print owner of match '''
        for target in database.local_belongs(self.pattern, escape=False):
            if self.plain:
                print(target)
            else:
                message.sub_info(_('Match in'), target)
