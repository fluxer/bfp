#!/usr/bin/python2

import sys, os, shutil, re, time, syslog, glob, pwd, grp
from collections import OrderedDict
if sys.version < '3':
    import ConfigParser as configparser
else:
    import configparser

import libmessage, libpackage
message = libmessage.Message()
misc = libpackage.misc
database = libpackage.Database()


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
    'SHELL': 'bash',
    'IGNORE': '',
    'NOTIFY': 'False',
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
    'PURGE_PATHS': '.*/.packlist|.*/perllocal.pod|.*/share/info/dir',
    'COMPRESS_MAN': 'False',
    'STRIP_BINARIES': 'False',
    'STRIP_SHARED': 'False',
    'STRIP_STATIC': 'False',
    'IGNORE_MISSING': 'False',
    'IGNORE_OWNERSHIP': 'False',
    'CONFLICTS': 'False',
    'BACKUP': 'False',
    'SCRIPTS': 'False',
    'TRIGGERS': 'False',
}

if not os.path.isfile(MAIN_CONF):
    message.warning('Configuration file does not exist', MAIN_CONF)

mainconf = configparser.SafeConfigParser(DEFAULTS)
mainconf.read(MAIN_CONF)
# at least the sections are required by the config parser, otherwise get()
# fails. notice that changes are not written to config on purpose since it
# may be read-only or even non-existent
for section in ('spm', 'fetch', 'compile', 'install', 'merge'):
    if not mainconf.has_section(section):
        mainconf.add_section(section)

CACHE_DIR = mainconf.get('spm', 'CACHE_DIR')
BUILD_DIR = mainconf.get('spm', 'BUILD_DIR')
ROOT_DIR = mainconf.get('spm', 'ROOT_DIR')
LOCAL_DIR = ROOT_DIR + 'var/local/spm'
GPG_DIR = mainconf.get('spm', 'GPG_DIR')
IGNORE = mainconf.get('spm', 'IGNORE').split(' ')
NOTIFY = mainconf.getboolean('spm', 'NOTIFY')
SHELL = mainconf.get('spm', 'SHELL')
OFFLINE = mainconf.getboolean('fetch', 'OFFLINE')
MIRROR = mainconf.getboolean('fetch', 'MIRROR')
TIMEOUT = mainconf.getint('fetch', 'TIMEOUT')
VERIFY = mainconf.getboolean('fetch', 'VERIFY')
CHOST = mainconf.get('compile', 'CHOST')
CFLAGS = mainconf.get('compile', 'CFLAGS')
CXXFLAGS = mainconf.get('compile', 'CXXFLAGS')
CPPFLAGS = mainconf.get('compile', 'CPPFLAGS')
LDFLAGS = mainconf.get('compile', 'LDFLAGS')
MAKEFLAGS = mainconf.get('compile', 'MAKEFLAGS')
PURGE_PATHS = mainconf.get('install', 'PURGE_PATHS')
COMPRESS_MAN = mainconf.getboolean('install', 'COMPRESS_MAN')
STRIP_BINARIES = mainconf.getboolean('install', 'STRIP_BINARIES')
STRIP_SHARED = mainconf.getboolean('install', 'STRIP_SHARED')
STRIP_STATIC = mainconf.getboolean('install', 'STRIP_STATIC')
IGNORE_MISSING = mainconf.getboolean('install', 'IGNORE_MISSING')
IGNORE_OWNERSHIP = mainconf.getboolean('install', 'IGNORE_OWNERSHIP')
CONFLICTS = mainconf.getboolean('merge', 'CONFLICTS')
BACKUP = mainconf.getboolean('merge', 'BACKUP')
SCRIPTS = mainconf.getboolean('merge', 'SCRIPTS')
TRIGGERS = mainconf.getboolean('merge', 'TRIGGERS')

# parse repositories configuration file
if not os.path.isfile(REPOSITORIES_CONF):
    message.warning('Repositories configuration file does not exist', \
        REPOSITORIES_CONF)
    REPOSITORIES = ['git://github.com/fluxer/core.git']
else:
    REPOSITORIES = []
    for line in misc.file_readsmart(REPOSITORIES_CONF):
        if misc.url_supported(line) or os.path.exists(line):
            REPOSITORIES.append(line)

    if not REPOSITORIES:
        message.critical('Repositories configuration file is empty')
        sys.exit(2)

# parse mirrors configuration file
if not os.path.isfile(MIRRORS_CONF):
    message.warning('Mirrors configuration file does not exist', \
        MIRRORS_CONF)
    MIRRORS = ['http://distfiles.gentoo.org/distfiles']
else:
    MIRRORS = []
    for line in misc.file_readsmart(MIRRORS_CONF):
        if misc.url_supported(line, False):
            MIRRORS.append(line)

    if not MIRRORS and MIRROR:
        message.critical('Mirrors configuration file is empty')
        sys.exit(2)

# parse PGP keys servers configuration file
if not os.path.isfile(KEYSERVERS_CONF):
    message.warning('PGP keys servers configuration file does not exist', \
        KEYSERVERS_CONF)
    KEYSERVERS = ['pool.sks-keyservers.net']
else:
    KEYSERVERS = []
    for line in misc.file_readsmart(KEYSERVERS_CONF):
        KEYSERVERS.append(line)

    if not KEYSERVERS and VERIFY:
        message.critical('PGP keys servers configuration file is empty')
        sys.exit(2)

# override module variables from configuration, each class will override
# them again because a user of the library may want to change them
# (overriding the config). the software build bot was such an example
# (which is no longer available in this source tree) doing all sort of
# things including building as specifiec user and root at the same time
# which involved creating new objects and such. the complexity comming
# out of these is for a reason - only the capital letter globals are
# ment to be changed by the user (at any time) and the rest is to be
# done by the library
misc.OFFLINE = OFFLINE
misc.TIMEOUT = TIMEOUT
misc.ROOT_DIR = ROOT_DIR
misc.GPG_DIR = GPG_DIR
misc.SHELL = SHELL
database.ROOT_DIR = ROOT_DIR
database.CACHE_DIR = CACHE_DIR
database.LOCAL_DIR = LOCAL_DIR
database.IGNORE = IGNORE
database.NOTIFY = NOTIFY


class Local(object):
    ''' Class for printing local targets metadata '''
    def __init__(self, pattern, do_name=False, do_version=False, \
        do_release=False, do_description=False, do_depends=False, \
        do_optdepends=False, do_autodepends=False, do_reverse=False, \
        do_size=False, do_footprint=False, do_backup=False, plain=False):
        self.pattern = pattern
        self.do_name = do_name
        self.do_version = do_version
        self.do_release = do_release
        self.do_description = do_description
        self.do_depends = do_depends
        self.do_optdepends = do_optdepends
        self.do_autodepends = do_autodepends
        self.do_reverse = do_reverse
        self.do_size = do_size
        self.do_footprint = do_footprint
        self.do_backup = do_backup
        self.plain = plain
        misc.OFFLINE = OFFLINE
        misc.TIMEOUT = TIMEOUT
        misc.ROOT_DIR = ROOT_DIR
        misc.GPG_DIR = GPG_DIR
        misc.SHELL = SHELL
        database.ROOT_DIR = ROOT_DIR
        database.CACHE_DIR = CACHE_DIR
        database.LOCAL_DIR = LOCAL_DIR
        database.IGNORE = IGNORE
        database.NOTIFY = NOTIFY

    def main(self):
        ''' Print local target metadata for every match '''
        matches = []
        aliases = database.remote_aliases()
        if self.pattern in aliases:
            for alias in database.remote_alias(self.pattern):
                if database.local_search(alias):
                    matches.append(alias)
        else:
            for target in database.local_all(basename=True):
                if re.search(self.pattern, target):
                    matches.append(target)

        # a stupid way of preventing lots of data being written to system logs
        # for an example when printing the footprint of lots of targets, maybe
        # is should be done only when self.plain is evaluated as True since
        # the output will have no value outside of the wrapper's scope
        msglogstatus = message.LOG_STATUS
        message.LOG_STATUS = [syslog.LOG_DEBUG, syslog.LOG_CRIT, syslog.LOG_ALERT]
        for target in matches:
            metadata = database.local_metadata(target, 'all')
            metadatamap = {
                'name': ('Name', self.do_name, target),
                'version': ('Version', self.do_version, metadata['version']),
                'release': ('Release', self.do_release, metadata['release']),
                'description': ('Description', self.do_description, metadata['description']),
                'depends': ('Depends', self.do_depends, ' '.join(metadata['depends'])),
                'optdepends': ('Optional depends', self.do_optdepends, ' '.join(metadata['optdepends'])),
                'autodepends': ('Automatic depends', self.do_autodepends, ' '.join(metadata['autodepends'])),
                'reverse': ('Reverse depends', self.do_reverse, lambda: ' '.join(database.local_rdepends(target))),
                'size': ('Size', self.do_size, metadata['size']),
                'footprint': ('Footprint', self.do_footprint, '\n'.join(metadata['footprint'])),
                'backup': ('Backup', self.do_backup, ' '.join(metadata['backup'])),
            }

            for metadata in metadatamap:
                if metadatamap[metadata][1]:
                    data = metadatamap[metadata][2]
                    if self.plain:
                        if metadata == 'reverse':
                            # since the reverse dependencies data is
                            # calculated every time and not static do it
                            # only if there is a reason for it
                            data = data()
                        print(data)
                    else:
                        if metadata == 'reverse':
                            data = data()
                        elif metadata == 'size':
                            data = misc.string_unit(data, 'auto', True)
                        message.sub_info(metadatamap[metadata][0], data)
        message.LOG_STATUS = msglogstatus


class Remote(object):
    ''' Class for printing remote targets metadata '''
    def __init__(self, pattern, do_name=False, do_version=False, \
        do_release=False, do_description=False, do_depends=False, \
        do_makedepends=False, do_optdepends=False, do_checkdepends=False, \
        do_sources=False, do_pgpkeys=False, do_options=False, \
        do_backup=False, plain=False):
        self.pattern = pattern
        self.do_name = do_name
        self.do_version = do_version
        self.do_release = do_release
        self.do_description = do_description
        self.do_depends = do_depends
        self.do_makedepends = do_makedepends
        self.do_optdepends = do_optdepends
        self.do_checkdepends = do_checkdepends
        self.do_sources = do_sources
        self.do_pgpkeys = do_pgpkeys
        self.do_options = do_options
        self.do_backup = do_backup
        self.plain = plain
        misc.OFFLINE = OFFLINE
        misc.TIMEOUT = TIMEOUT
        misc.ROOT_DIR = ROOT_DIR
        misc.GPG_DIR = GPG_DIR
        misc.SHELL = SHELL
        database.ROOT_DIR = ROOT_DIR
        database.CACHE_DIR = CACHE_DIR
        database.LOCAL_DIR = LOCAL_DIR
        database.IGNORE = IGNORE
        database.NOTIFY = NOTIFY

    def main(self):
        ''' Print remote target metadata for every match '''
        matches = []
        aliases = database.remote_aliases()
        if self.pattern in aliases:
            matches = database.remote_alias(self.pattern)
        else:
            for target in database.remote_all(basename=True):
                if re.search(self.pattern, target):
                    matches.append(target)

        # same as in Local()
        msglogstatus = message.LOG_STATUS
        message.LOG_STATUS = [syslog.LOG_DEBUG, syslog.LOG_CRIT, syslog.LOG_ALERT]
        for target in matches:
            metadata = database.remote_metadata(target, 'all')
            metadatamap = {
                'name': ('Name', self.do_name, target),
                'version': ('Version', self.do_version, metadata['version']),
                'release': ('Release', self.do_release, metadata['release']),
                'description': ('Description', self.do_description, metadata['description']),
                'depends': ('Depends', self.do_depends, ' '.join(metadata['depends'])),
                'makedepends': ('Make depends', self.do_makedepends, ' '.join(metadata['makedepends'])),
                'optdepends': ('Optional depends', self.do_optdepends, ' '.join(metadata['optdepends'])),
                'checkdepends': ('Check depends', self.do_checkdepends, ' '.join(metadata['checkdepends'])),
                'sources': ('Sources', self.do_sources, ' '.join(metadata['sources'])),
                'pgpkeys': ('PGP keys', self.do_pgpkeys, ' '.join(metadata['pgpkeys'])),
                'options': ('Options', self.do_pgpkeys, ' '.join(metadata['options'])),
                'backup': ('Backup', self.do_backup, ' '.join(metadata['backup'])),
            }

            for metadata in metadatamap:
                if metadatamap[metadata][1]:
                    data = metadatamap[metadata][2]
                    if self.plain:
                        print(data)
                    else:
                        message.sub_info(metadatamap[metadata][0], data)
        message.LOG_STATUS = msglogstatus


class Repo(object):
    ''' Class for dealing with repositories '''
    def __init__(self, repositories, do_clean=False, do_sync=False, \
        do_update=False, do_prune=False):
        self.repositories = repositories
        self.do_clean = do_clean
        self.do_sync = do_sync
        self.do_prune = do_prune
        self.do_update = do_update
        misc.OFFLINE = OFFLINE
        misc.TIMEOUT = TIMEOUT
        misc.ROOT_DIR = ROOT_DIR
        misc.GPG_DIR = GPG_DIR
        misc.SHELL = SHELL
        database.ROOT_DIR = ROOT_DIR
        database.CACHE_DIR = CACHE_DIR
        database.LOCAL_DIR = LOCAL_DIR
        database.IGNORE = IGNORE
        database.NOTIFY = NOTIFY

    def clean(self):
        ''' Clean repository '''
        if os.path.isdir(self.repository_dir):
            message.sub_info('Removing', self.repository_dir)
            misc.dir_remove(self.repository_dir)
        else:
            message.sub_debug('Dirctory does not exist', self.repository_dir)

    def sync(self):
        ''' Sync repository '''
        misc.dir_create('%s/repositories' % CACHE_DIR)

        if os.path.exists(self.repository_url):
            # repository is local path, create a copy of it
            message.sub_info('Cloning local', self.repository_name)
            shutil.copytree(self.repository_url, self.repository_dir)
        else:
            message.sub_info('Cloning/pulling remote', self.repository_name)
            misc.fetch(self.repository_url, self.repository_dir)

    def prune(self):
        ''' Remove repositories that are no longer in the config '''
        rdir = '%s/repositories' % CACHE_DIR
        if not os.path.exists(rdir):
            return

        for spath in os.listdir(rdir):
            valid = False
            for repo in REPOSITORIES:
                if os.path.basename(repo) == spath:
                    valid = True

            sfull = '%s/%s' % (rdir, spath)
            if not valid and not os.path.isfile(sfull):
                message.sub_warning('Removing', sfull)
                misc.dir_remove(sfull)

    def update(self):
        ''' Check repositories for updates '''
        message.sub_info('Checking for updates')
        for target in database.local_all(basename=True):
            if not database.remote_search(target):
                message.sub_warning('Target not in any repository', target)
                continue

            message.sub_debug('Checking', target)
            latest = database.local_uptodate(target)
            downgrade = database.local_downgrade(target)
            optchange = []
            optdepends = database.local_metadata(target, 'optdepends')
            for opt in database.remote_metadata(target, 'optdepends'):
                if database.local_uptodate(opt) and not opt in optdepends:
                    optchange.append(opt)
            version = database.remote_metadata(target, 'version')
            if not latest and target in IGNORE:
                message.sub_warning('New version of %s (ignored) available' % \
                    target, version)
            elif not latest and optchange:
                message.sub_warning('New optional dependency in effect for %s' % \
                    target, optchange)
            elif not latest:
                message.sub_warning('New version of %s available' % \
                    target, version)
            elif downgrade:
                message.sub_warning('Older version of %s available' % \
                    target, version)

    def main(self):
        ''' Execute action for every repository '''
        for repository in self.repositories:
            # compute only once by asigning class variables, in cases when
            # clean and sync is done this is more optimal but triggers
            # http://pylint-messages.wikidot.com/messages:w0201
            self.repository_url = repository
            self.repository_name = os.path.basename(self.repository_url)
            self.repository_dir = '%s/repositories/%s' % (CACHE_DIR, \
                self.repository_name)

            if self.do_clean:
                message.sub_info('Starting cleanup of', self.repository_name)
                self.clean()

            if self.do_sync:
                message.sub_info('Starting sync of', self.repository_name)
                self.sync()

        if self.do_prune:
            message.sub_info('Starting prune of', self.repository_name)
            self.prune()

        if self.do_update:
            message.sub_info('Starting update of', self.repository_name)
            self.update()


class Source(object):
    ''' Class for dealing with sources '''
    def __init__(self, targets, do_clean=False, do_fetch=False, \
        do_prepare=False, do_compile=False, do_check=False, do_install=False, \
        do_merge=False, do_remove=False, do_depends=False, do_reverse=False, \
        do_update=False, automake=False, autoremove=False):
        self.targets = targets
        self.do_clean = do_clean
        self.do_fetch = do_fetch
        self.do_prepare = do_prepare
        self.do_compile = do_compile
        self.do_check = do_check
        self.do_install = do_install
        self.do_merge = do_merge
        self.do_remove = do_remove
        self.do_depends = do_depends
        self.do_reverse = do_reverse
        self.do_update = do_update
        self.automake = automake
        self.autoremove = autoremove
        self.verify = VERIFY
        self.mirror = MIRROR
        self.purge_paths = PURGE_PATHS
        self.compress_man = COMPRESS_MAN
        self.strip_binaries = STRIP_BINARIES
        self.strip_shared = STRIP_SHARED
        self.strip_static = STRIP_STATIC
        self.ignore_missing = IGNORE_MISSING
        self.ignore_ownership = IGNORE_OWNERSHIP
        misc.OFFLINE = OFFLINE
        misc.TIMEOUT = TIMEOUT
        misc.ROOT_DIR = ROOT_DIR
        misc.GPG_DIR = GPG_DIR
        misc.SHELL = SHELL
        database.ROOT_DIR = ROOT_DIR
        database.CACHE_DIR = CACHE_DIR
        database.LOCAL_DIR = LOCAL_DIR
        database.IGNORE = IGNORE
        database.NOTIFY = NOTIFY
        # https://en.wikipedia.org/wiki/Comparison_of_command_shells
        bang_regexp = 'sh|bash|dash|ksh|csh|tcsh|tclsh|scsh|fish|zsh'
        bang_regexp += '|ash|python|perl|php|ruby|lua|wish|(?:g)?awk'
        bang_regexp += '|gbr2|gbr3'
        # find the base of the interpreter (e.g. bash), used to find match in the target or local target
        self.shebang_regex = re.compile('^#!.*(?: |\\t|/)((?:' + bang_regexp + ')(?:[^\\s]+)?)(?:.*\\s)')

    def autosource(self, targets, automake=False, autoremove=False):
        ''' Handle targets build/remove without affecting current object '''
        if automake:
            obj = Source(targets, do_check=self.do_check, \
                do_reverse=self.do_reverse, do_update=False, automake=True)
        else:
            obj = Source(targets, do_reverse=self.do_reverse, \
                autoremove=autoremove)
        obj.main()

    def setup_environment(self):
        ''' Setup environment and directories for build '''
        os.putenv('SOURCE_DIR', self.source_dir)
        os.putenv('INSTALL_DIR', self.install_dir)
        os.putenv('CHOST', CHOST)
        os.putenv('CFLAGS', CFLAGS)
        os.putenv('CXXFLAGS', CXXFLAGS)
        os.putenv('CPPFLAGS', CPPFLAGS)
        os.putenv('LDFLAGS', LDFLAGS)
        os.putenv('MAKEFLAGS', MAKEFLAGS)
        for target in self.target_optdepends:
            envtarget = misc.string_illegal(target.upper())
            # OPTIONAL_<target>_BOOL and OPTIONAL_<target>_SWITCH are for use
            # with CMake, OPTIONAL_<target> is a generic one that can be used
            # with Autotools
            if database.local_search(target):
                message.sub_debug('Enabling optional', target)
                os.putenv('OPTIONAL_%s_BOOL' % envtarget, 'TRUE')
                os.putenv('OPTIONAL_%s_SWITCH' % envtarget, 'ON')
                os.putenv('OPTIONAL_%s' % envtarget, 'yes')
            else:
                message.sub_debug('Disabling optional', target)
                os.putenv('OPTIONAL_%s_BOOL' % envtarget, 'FALSE')
                os.putenv('OPTIONAL_%s_SWITCH' % envtarget, 'OFF')
                os.putenv('OPTIONAL_%s' % envtarget, 'no')

        misc.dir_create(self.source_dir)
        misc.dir_create(self.install_dir)

    def pre_update_databases(self, content, action):
        ''' Update common databases before merge/remove '''
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
                if not os.path.exists('%s/%s' % (ROOT_DIR, m)):
                    message.sub_warning('File does not exist', m)
                    continue
                message.sub_info('Deleting info page', m)
                misc.system_chroot((install_info, '--delete', m, \
                    '%s/share/info/dir' % sys.prefix))

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
                    message.sub_info('Uninstalling XDG MIMEs', m)
                    misc.system_chroot((xdg_mime, 'uninstall', m))
                done.append(m)

    def post_update_databases(self, content, action):
        ''' Update common databases after merge/remove '''
        if not TRIGGERS:
            return

        adjcontent = '\n'.join(content)
        ldconfig = misc.whereis('ldconfig', False, True)
        ldconfig_regex = '(.*\\.so)(?:$|\\s)'
        message.sub_debug('ldconfig', ldconfig or '')
        match = misc.string_search(ldconfig_regex, adjcontent, escape=False)
        if match and ldconfig:
            message.sub_info('Updating shared libraries cache')
            message.sub_debug(match)
            misc.system_chroot((ldconfig))

        mandb = misc.whereis('mandb', False, True)
        mandb_regex = '(.*share/man.*)(?:$|\\s)'
        message.sub_debug('mandb', mandb or '')
        match = misc.string_search(mandb_regex, adjcontent, escape=False)
        if match and mandb:
            message.sub_info('Updating manual pages database')
            message.sub_debug(match)
            command = [mandb, '--quiet']
            mancache = '%s/var/cache/man' % ROOT_DIR
            misc.dir_create(mancache)
            if os.path.exists('%s/index.db' % mancache):
                for m in match:
                    command.extend(('-f', m))
                misc.system_chroot(command)
            else:
                command.append('-c')
                misc.system_chroot(command)

        desktop_database = misc.whereis('update-desktop-database', False, True)
        desktop_database_regex = '(.*share/applications/).*(?:$|\\s)'
        message.sub_debug('update-desktop-database', desktop_database or '')
        match = misc.string_search(desktop_database_regex, adjcontent, escape=False)
        if match and desktop_database:
            message.sub_info('Updating desktop database')
            message.sub_debug(match)
            misc.system_chroot((desktop_database, \
                '%s/share/applications' % sys.prefix))

        mime_database = misc.whereis('update-mime-database', False, True)
        mime_database_regex = '(.*share/mime/).*(?:$|\\s)'
        message.sub_debug('update-mime-database', mime_database or '')
        match = misc.string_search(mime_database_regex, adjcontent, escape=False)
        if match and mime_database:
            message.sub_info('Updating MIME database')
            message.sub_debug(match)
            misc.system_chroot((mime_database, '%s/share/mime' % sys.prefix))

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
                    message.sub_info('Updating icon resources', base)
                    misc.system_chroot((icon_resources, 'forceupdate', '--theme', base))
                if (action == 'merge' or action == 'upgrade') \
                    and os.path.isfile('%s/%s/index.theme' % (ROOT_DIR, m)) and icon_cache:
                    message.sub_info('Updating icons cache', base)
                    misc.system_chroot((icon_cache, '-q', '-t', '-i', '-f', m))
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
                    message.sub_info('Installing XDG MIMEs', m)
                    misc.system_chroot((xdg_mime, 'install', '--novendor', m))
                elif action == 'upgrade':
                    message.sub_info('Updating XDG MIMEs', m)
                    misc.system_chroot((xdg_mime, 'install', '--novendor', m))
                done.append(m)

        gio_querymodules = misc.whereis('gio-querymodules', False, True)
        gio_querymodules_regex = '(?:^|\\s)(.*/gio/modules/.*)(?:$|\\s)'
        message.sub_debug('gio-querymodules', gio_querymodules or '')
        match = misc.string_search(gio_querymodules_regex, adjcontent, escape=False)
        if match and gio_querymodules:
            message.sub_info('Updating GIO modules cache')
            message.sub_debug(match)
            misc.system_chroot((gio_querymodules, os.path.dirname(match[0])))

        pango_querymodules = misc.whereis('pango-querymodules', False, True)
        pango_querymodules_regex = '(?:^|\\s)(.*/pango/.*/modules/.*)(?:$|\\s)'
        message.sub_debug('pango-querymodules', pango_querymodules or '')
        match = misc.string_search(pango_querymodules_regex, adjcontent, escape=False)
        if match and pango_querymodules:
            message.sub_info('Updating pango modules cache')
            message.sub_debug(match)
            misc.system_chroot((pango_querymodules, '--update-cache'))

        # TODO: use --update-cache, requires GTK+ version >= 2.24.20
        gtk2_immodules = misc.whereis('gtk-query-immodules-2.0', False, True)
        gtk2_immodules_regex = '(?:^|\\s)(.*/gtk-2.0/.*/immodules/.*)(?:$|\\s)'
        message.sub_debug('gtk-query-imodules-2.0', gtk2_immodules or '')
        match = misc.string_search(gtk2_immodules_regex, adjcontent, escape=False)
        if match and gtk2_immodules:
            message.sub_info('Updating GTK-2.0 imodules cache')
            message.sub_debug(match)
            misc.dir_create('%s/etc/gtk-2.0' % ROOT_DIR)
            misc.system_chroot(gtk2_immodules + \
                ' > /etc/gtk-2.0/gtk.immodules', bshell=True)

        gtk3_immodules = misc.whereis('gtk-query-immodules-3.0', False, True)
        gtk3_immodules_regex = '(?:^|\\s)(.*/gtk-3.0/.*/immodules/.*)(?:$|\\s)'
        message.sub_debug('gtk-query-imodules-3.0', gtk3_immodules or '')
        match = misc.string_search(gtk3_immodules_regex, adjcontent, escape=False)
        if match and gtk3_immodules:
            message.sub_info('Updating GTK-3.0 imodules cache')
            message.sub_debug(match)
            misc.dir_create('%s/etc/gtk-3.0' % ROOT_DIR)
            misc.system_chroot('%s > /etc/gtk-3.0/gtk.immodules' % gtk3_immodules, \
                bshell=True)

        gdk_pixbuf = misc.whereis('gdk-pixbuf-query-loaders', False, True)
        gdk_pixbuf_regex = '(?:^|\\s)(.*/gdk-pixbuf.*)(?:$|\\s)'
        message.sub_debug('gdk-pixbuf-query-loaders', gdk_pixbuf or '')
        match = misc.string_search(gdk_pixbuf_regex, adjcontent, escape=False)
        if match and gdk_pixbuf:
            message.sub_info('Updating gdk pixbuffer loaders')
            message.sub_debug(match)
            misc.system_chroot((gdk_pixbuf, '--update-cache'))

        glib_schemas = misc.whereis('glib-compile-schemas', False, True)
        glib_schemas_regex = '(?:^|\\s)(.*/schemas)/.*(?:$|\\s)'
        message.sub_debug('glib-compile-schemas', glib_schemas or '')
        match = misc.string_search(glib_schemas_regex, adjcontent, escape=False)
        if match and glib_schemas:
            message.sub_info('Updating GSettings schemas')
            message.sub_debug(match)
            misc.system_chroot((glib_schemas, match[0]))

        install_info = misc.whereis('install-info', False, True)
        install_info_regex = '(?:^|\\s)(.*share/info/.*)(?:$|\\s)'
        message.sub_debug('install-info', install_info or '')
        match = misc.string_search(install_info_regex, adjcontent, escape=False)
        if match and install_info:
            message.sub_debug(match)
            for m in match:
                if action == 'remove':
                    continue
                message.sub_info('Installing info page', m)
                misc.system_chroot((install_info, m, \
                    '%s/share/info/dir' % sys.prefix))

        udevadm = misc.whereis('udevadm', False, True)
        udevadm_regex = '(?:^|\\s)(.*/udev/rules.d/.*)(?:$|\\s)'
        message.sub_debug('udevadm', udevadm or '')
        match = misc.string_search(udevadm_regex, adjcontent, escape=False)
        if match and udevadm:
            if os.path.exists('%s/run/udev/control' % ROOT_DIR) \
                or os.path.exists('%s/var/run/udev/control' % ROOT_DIR):
                message.sub_info('Reloading udev rules and hwdb')
                message.sub_debug(match)
                misc.system_chroot((udevadm, 'control', '--reload'))

        mkinitfs_run = False
        depmod = misc.whereis('depmod', False, True)
        depmod_regex = '(?:^|\\s)(?:/)?(?:usr/?)?lib/modules/(.*?)/.*(?:$|\\s)'
        message.sub_debug('depmod', depmod or '')
        match = misc.string_search(depmod_regex, adjcontent, escape=False)
        if match and depmod:
            message.sub_info('Updating module dependencies')
            message.sub_debug(match)
            misc.system_chroot((depmod, match[0]))
            mkinitfs_run = True

        mkinitfs = misc.whereis('mkinitfs', False, True)
        mkinitfs_regex = '(?:^|\\s)(?:/)?(boot/vmlinuz-(.*)|etc/mkinitfs/.*)(?:$|\\s)'
        message.sub_debug('mkinitfs', mkinitfs or '')
        match = misc.string_search(mkinitfs_regex, adjcontent, escape=False)
        if (match or mkinitfs_run) and mkinitfs:
            message.sub_info('Updating initramfs image')
            message.sub_debug(match or mkinitfs_run)
            if match and match[0][1]:
                # new kernel being installed
                misc.system_chroot((mkinitfs, '-k', match[0][1]))
            else:
                misc.system_chroot((mkinitfs))

        grub_mkconfig = misc.whereis('grub-mkconfig', False, True)
        os_prober = misc.whereis('os-prober', False, True)
        grub_mkconfig_regex = '(?:^|\\s)(?:/)?(boot/.*|etc/grub.d/.*)(?:$|\\s)'
        message.sub_debug('grub-mkconfig', grub_mkconfig or '')
        match = misc.string_search(grub_mkconfig_regex, adjcontent, escape=False)
        if match and grub_mkconfig:
            if os_prober:
                message.sub_info('Updating Operating System entries')
                misc.system_chroot((os_prober))
            message.sub_info('Updating GRUB configuration')
            message.sub_debug(match)
            misc.dir_create('%s/boot/grub' % ROOT_DIR)
            misc.system_chroot((grub_mkconfig, '-o', '/boot/grub/grub.cfg'))

    def remove_target_file(self, sfile):
        ''' Remove target file '''
        sfull = '%s/%s' % (ROOT_DIR, sfile)
        if os.path.isfile(sfull):
            message.sub_debug('Removing', sfull)
            os.unlink(sfull)

    def remove_target_dir(self, sdir):
        ''' Remove target directory '''
        sfull = '%s/%s' % (ROOT_DIR, sdir)
        if os.path.isdir(sfull) and not os.listdir(sfull):
            message.sub_debug('Removing', sfull)
            if os.path.islink(sfull):
                os.unlink(sfull)
            else:
                os.rmdir(sfull)
            self.remove_target_dir(os.path.dirname(sdir))

    def remove_target_link(self, slink):
        ''' Remove target symlink '''
        sfull = '%s/%s' % (ROOT_DIR, slink)
        if os.path.islink(sfull) and \
            not os.path.exists('%s/%s' % (ROOT_DIR, os.readlink(sfull))):
            message.sub_debug('Removing', sfull)
            os.unlink(sfull)

    def clean(self):
        ''' Clean target files '''
        if os.path.isdir(self.install_dir) and self.do_install:
            message.sub_info('Removing', self.install_dir)
            misc.dir_remove(self.install_dir)
        elif os.path.isdir(self.install_dir) and not self.do_prepare:
            message.sub_info('Removing', self.install_dir)
            misc.dir_remove(self.install_dir)
        else:
            message.sub_debug('Dirctory does not exist', self.install_dir)

        if os.path.isdir(self.source_dir) and self.do_prepare:
            message.sub_info('Removing', self.source_dir)
            misc.dir_remove(self.source_dir)
        elif os.path.isdir(self.source_dir) and not self.do_install:
            message.sub_info('Removing', self.source_dir)
            misc.dir_remove(self.source_dir)
        else:
            message.sub_debug('Dirctory does not exist', self.source_dir)

    def fetch(self):
        ''' Fetch target sources '''
        misc.dir_create(self.sources_dir)

        message.sub_info('Preparing PGP keys')
        if self.target_pgpkeys and self.verify:
            message.sub_debug(self.target_pgpkeys)
            misc.gpg_receive(self.target_pgpkeys, KEYSERVERS, self.target_name)

        message.sub_info('Fetching sources')
        for src_url in self.target_sources:
            src_base = misc.url_normalize(src_url, True)
            local_file = '%s/%s' % (self.sources_dir, src_base)
            src_file = '%s/%s' % (self.target_dir, src_url)

            if not os.path.isfile(src_file):
                message.sub_debug('Fetching', src_url)
                if self.mirror:
                    misc.fetch(src_url, local_file, MIRRORS, 'distfiles/')
                else:
                    misc.fetch(src_url, local_file)

        if self.verify:
            for src_url in self.target_sources:
                src_base = misc.url_normalize(src_url, True)
                local_file = '%s/%s' % (self.sources_dir, src_base)

                src_signature = misc.gpg_findsig(local_file)
                if src_signature:
                    message.sub_debug('Verifying signature', src_url)
                    misc.gpg_verify(local_file, src_signature, self.target_name)

    def prepare(self, optional=False):
        ''' Prepare target sources '''
        message.sub_info('Checking dependencies')
        dependencies = database.remote_mdepends(self.target, \
            cdepends=self.do_check, ldepends=True)

        if dependencies and self.do_depends:
            message.sub_info('Building dependencies', dependencies)
            self.autosource(dependencies, automake=True)
            message.sub_info('Resuming preparations of', self.target_name)
        elif dependencies and self.automake:
            # the dependencies have been pre-calculated on automake by
            # remote_mdepends() above breaking on circular, any dependencies
            # detected now are because they are last in the graph but depend
            # on one in higher level
            message.sub_warning('Circular dependencies in %s' % \
                self.target_name, dependencies)
        elif dependencies:
            message.sub_warning('Dependencies missing', dependencies)

        self.setup_environment()
        misc.dir_create(self.sources_dir)
        message.sub_info('Preparing sources')
        for src_url in self.target_sources:
            src_base = misc.url_normalize(src_url, True)
            local_file = '%s/%s' % (self.sources_dir, src_base)
            src_file = '%s/%s' % (self.target_dir, src_base)
            link_file = '%s/%s' % (self.source_dir, src_base)

            if os.path.islink(link_file):
                message.sub_debug('Already linked', src_file)
            elif os.path.isdir(local_file):
                message.sub_debug('Copying', src_file)
                shutil.copytree(local_file, link_file, True)
            elif os.path.isfile(src_file):
                message.sub_debug('Linking', src_file)
                os.symlink(src_file, link_file)
            elif os.path.isfile(local_file):
                message.sub_debug('Linking', local_file)
                os.symlink(local_file, link_file)

            if misc.archive_supported(link_file):
                message.sub_debug('Extracting', link_file)
                misc.archive_decompress(link_file, self.source_dir)

        if not misc.file_search('\nsrc_prepare()', \
            self.srcbuild, escape=False):
            if optional:
                message.sub_warning('src_prepare() not defined')
                return
            else:
                message.sub_critical('src_prepare() not defined')
                sys.exit(2)

        misc.system_command((misc.whereis(SHELL), '-e', '-c', \
            'source %s && umask 0022 && src_prepare' % \
            self.srcbuild), cwd=self.source_dir)

    def compile(self, optional=False):
        ''' Compile target sources '''
        if not misc.file_search('\nsrc_compile()', \
            self.srcbuild, escape=False):
            if optional:
                message.sub_warning('src_compile() not defined')
                return
            else:
                message.sub_critical('src_compile() not defined')
                sys.exit(2)

        self.setup_environment()
        misc.system_command((misc.whereis(SHELL), '-e', '-c', \
            'source %s && umask 0022 && src_compile' % \
            self.srcbuild), cwd=self.source_dir)

    def check(self, optional=False):
        ''' Check target sources '''
        if not misc.file_search('\nsrc_check()', \
            self.srcbuild, escape=False):
            if optional:
                message.sub_warning('src_check() not defined')
                return
            else:
                message.sub_critical('src_check() not defined')
                sys.exit(2)

        self.setup_environment()
        misc.system_command((misc.whereis(SHELL), '-e', '-c', \
            'source %s && umask 0022 && src_check' % \
            self.srcbuild), cwd=self.source_dir)

    def install(self):
        ''' Install targets files '''

        if not misc.file_search('\nsrc_install()', \
            self.srcbuild, escape=False):
            message.sub_critical('src_install() not defined')
            sys.exit(2)

        self.setup_environment()

        misc.system_command((misc.whereis(SHELL), '-e', '-c', \
            'source %s && umask 0022 && src_install' % \
            self.srcbuild), cwd=self.source_dir)

        message.sub_info('Indexing content')
        target_content = misc.list_all(self.install_dir)

        if self.purge_paths:
            message.sub_info('Purging unwanted files and directories')
            for spath in misc.string_search(self.purge_paths, \
                    '\n'.join(target_content), exact=True, escape=False):
                spath = spath.strip()
                message.sub_debug('Purging', spath)
                if os.path.isdir(spath):
                    misc.dir_remove(spath)
                elif os.path.isfile(spath) or os.path.islink(spath):
                    os.unlink(spath)

        if not self.ignore_ownership:
            message.sub_info('Checking permissions')
            for sfile in target_content:
                if not os.path.exists(sfile):
                    continue
                message.sub_debug('Checking permissions of', sfile)
                stat = os.stat(sfile)
                owner_unknown = False
                try:
                    pwd.getpwuid(stat.st_uid)
                    grp.getgrgid(stat.st_gid)
                except KeyError:
                    owner_unknown = True
                if owner_unknown:
                    message.sub_warning('Unknown owner of', sfile)
                    os.chown(sfile, 0, 0)
                # TODO: is there utility to pull those from /etc/login.defs?
                elif stat.st_gid >= 1000 or stat.st_uid >= 1000:
                    message.sub_warning('Owner of %s is user' % sfile, \
                        '%d, %d' % (stat.st_gid, stat.st_uid))
                    os.chown(sfile, 0, 0)

        if self.compress_man:
            message.sub_info('Compressing manual pages')
            manpath = misc.whereis('manpath', fallback=False)
            # if manpath (provided by man-db) is not present fallback to
            # something sane
            if not manpath:
                mpaths = ('/usr/local/share/man/', '/local/share/man/', \
                    '/usr/share/man/', '/share/man/', '/usr/man/')
            else:
                mpaths = misc.system_communicate((manpath, '--global')).split(':')

            for spath in target_content:
                for sdir in mpaths:
                    if not sdir in spath:
                        continue
                    if not spath.endswith('.gz') and os.path.isfile(spath):
                        message.sub_debug('Compressing', spath)
                        misc.archive_compress((spath,), '%s.gz' % spath, '')
                        os.unlink(spath)
                    elif os.path.islink(spath) and \
                        not os.path.isfile(os.path.realpath(spath)):
                        message.sub_debug('Adjusting link', spath)
                        link = os.readlink(spath)
                        os.unlink(spath)
                        if not spath.endswith('.gz'):
                            os.symlink('%s.gz' % link, spath)
                        else:
                            os.symlink(link, spath)

        message.sub_info('Re-indexing content')
        lscripts = []
        lbinaries = []
        lshared = []
        lstatic = []
        target_content = []
        for sfile in misc.list_files(self.install_dir):
            if LOCAL_DIR in sfile:
                continue
            message.sub_debug('Checking MIME of', sfile)
            smime = misc.file_mime(sfile, bquick=True)
            target_content.append(sfile)
            if smime == 'application/x-executable':
                lbinaries.append(sfile)
            elif smime == 'application/x-sharedlib':
                lshared.append(sfile)
            elif smime == 'application/x-archive':
                lstatic.append(sfile)
            elif smime == 'text/plain' or smime == 'text/x-shellscript' \
                or smime == 'text/x-python' or smime == 'text/x-perl' \
                or smime == 'text/x-php' or smime == 'text/x-ruby' \
                or smime == 'text/x-lua' or smime == 'text/x-tcl' \
                or smime == 'text/x-awk' or smime == 'text/x-gawk':
                lscripts.append(sfile)

        message.sub_info('Stripping binaries and libraries')
        if self.strip_binaries or self.strip_shared or self.strip_static:
            strip = misc.whereis('strip')
        if self.strip_binaries and lbinaries:
            message.sub_debug('Stripping executables', lbinaries)
            cmd = [strip, '--strip-all']
            cmd.extend(lbinaries)
            misc.system_command(cmd)
        if self.strip_shared and lshared:
            message.sub_debug('Stripping shared libraries', lshared)
            cmd = [strip, '--strip-unneeded']
            cmd.extend(lshared)
            misc.system_command(cmd)
        if self.strip_static and lstatic:
            message.sub_debug('Stripping static libraries', lstatic)
            cmd = [strip, '--strip-debug']
            cmd.extend(lstatic)
            misc.system_command(cmd)

        message.sub_info('Checking runtime dependencies')
        autodepends = []
        for sfile in lbinaries:
            autodepends = misc.system_readelf(sfile, bsearch=False)
        for sfile in lshared:
            autodepends.extend(misc.system_readelf(sfile, bsearch=False))

        for sfile in lscripts:
            smatch = self.shebang_regex.findall(misc.file_read(sfile))
            if smatch:
                autodepends.append(smatch[0].strip())

        found = []
        depends = []
        depends.extend(self.target_depends)

        for dep in autodepends:
            if dep in found:
                continue
            for sfile in target_content:
                if sfile.endswith('/%s' % dep) and os.access(sfile, os.X_OK):
                    message.sub_debug('Dependency is in target', dep)
                    found.append(dep)
                    break

        for local in database.local_all(basename=True):
            lfootprint = database.local_metadata(local, 'footprint')
            for dep in autodepends:
                if dep in found:
                    continue
                for sfile in lfootprint:
                    if sfile.endswith('/%s' % dep) and os.access(sfile, os.X_OK):
                        message.sub_debug('Dependency %s is in local' % dep, local)
                        if not local in depends:
                            depends.append(local)
                        found.append(dep)
                        break

        missing_detected = False
        for dep in autodepends:
            if not dep in found:
                if not self.ignore_missing:
                    message.sub_critical('Dependency needed, not in any local', dep)
                    missing_detected = True
                else:
                    message.sub_warning('Dependency needed, not in any local', dep)
        if missing_detected:
            sys.exit(2)

        message.sub_info('Assembling metadata')
        metadata = '%s/%s' % (self.install_dir, self.target_metadata)
        footprint = []
        optdepends = []
        backup = {}
        for sfile in target_content:
            sstripped = sfile.replace(self.install_dir, '')
            # ignore local target files, they are not wanted in the footprint
            if LOCAL_DIR in sfile:
                continue
            footprint.append(sstripped)
            if sfile.endswith('.conf') or misc.string_lstrip(sstripped, '/') in self.target_backup:
                sreal = os.path.realpath(sfile)
                if not sreal.startswith(self.install_dir):
                    # symlink to full path
                    sreal = '%s/%s' % (self.install_dir, sreal)
                backup[sstripped] = misc.file_checksum(sreal)
        for target in self.target_optdepends:
            if database.local_search(target):
                optdepends.append(target)
        data = [
            ('version', self.target_version),
            ('release', self.target_release),
            ('description', self.target_description),
            ('depends', depends),
            ('optdepends', optdepends),
            ('autodepends', autodepends),
            ('backup', backup),
            ('size', misc.dir_size(self.install_dir)),
            ('footprint', footprint),
            ('builddate', time.ctime()),
        ]
        misc.dir_create(os.path.dirname(metadata))
        misc.json_write(metadata, OrderedDict(data))

        message.sub_info('Assembling SRCBUILD')
        shutil.copy(self.srcbuild, '%s/%s' % \
            (self.install_dir, self.target_srcbuild))

        message.sub_info('Compressing tarball')
        misc.dir_create(os.path.dirname(self.target_tarball))
        misc.archive_compress((self.install_dir,), self.target_tarball, \
            self.install_dir)

    def merge(self):
        ''' Merget target to system '''
        message.sub_info('Indexing content')
        new_content = []
        for sfile in misc.archive_list(self.target_tarball):
            new_content.append('/%s' % sfile)
        if not '/%s' % self.target_metadata in new_content:
            message.sub_critical('Invalid tarball', self.target_tarball)
            sys.exit(2)
        new_content.sort()
        old_content = database.local_metadata(self.target_name, 'footprint') or []
        backup_content = database.local_metadata(self.target_name, 'backup') or {}

        if CONFLICTS:
            conflict_detected = False
            message.sub_info('Checking for conflicts')
            for target in database.local_all(basename=True):
                if target == self.target_name:
                    continue
                message.sub_debug('Checking against', target)
                footprint = frozenset(database.local_metadata(target, 'footprint'))
                diff = footprint.difference(new_content)
                if footprint != diff:
                    message.sub_critical('File/link conflicts with %s' % target, \
                        list(footprint.difference(diff)))
                    conflict_detected = True

            if conflict_detected:
                sys.exit(2)

        # store state installed or not, it must be done before the decompression
        target_upgrade = database.local_search(self.target_name)

        if target_upgrade and SCRIPTS \
            and misc.file_search('\npre_upgrade()', self.srcbuild, escape=False):
            message.sub_info('Executing pre_upgrade()')
            misc.system_script(self.srcbuild, 'pre_upgrade')
        elif misc.file_search('\npre_install()', self.srcbuild, escape=False) \
            and SCRIPTS:
            message.sub_info('Executing pre_install()')
            misc.system_script(self.srcbuild, 'pre_install')

        if target_upgrade and old_content:
            self.pre_update_databases(old_content, 'upgrade')
        elif new_content:
            self.pre_update_databases(new_content, 'merge')

        if BACKUP:
            message.sub_info('Creating backup files')
            for sfile in backup_content:
                sfull = '%s%s' % (ROOT_DIR, sfile)
                if not os.path.isfile(sfull):
                    message.sub_warning('File does not exist', sfull)
                elif not backup_content[sfile] == misc.file_checksum(sfull):
                    message.sub_debug('Backing up', sfull)
                    shutil.copy2(sfull, '%s.backup' % sfull)
                else:
                    message.sub_debug('Backup skipped', sfull)

        message.sub_info('Decompressing tarball')
        misc.archive_decompress(self.target_tarball, ROOT_DIR)

        if target_upgrade:
            message.sub_info('Removing obsolete files and directories')
            remove_content = frozenset(old_content).difference(new_content)
            message.sub_debug('Removing files')
            for sfile in remove_content:
                sfull = '%s%s' % (ROOT_DIR, sfile.encode('utf-8'))
                # skip files moved from real to symlink directory
                sresolved = os.path.realpath(sfull)
                if not ROOT_DIR == '/':
                    sresolved.replace(ROOT_DIR, '/')
                if sresolved in new_content:
                    continue
                # never delete files in the pseudo filesystems and the target's
                # metadata/SRCBUILD
                elif sfile.startswith(('/dev/', '/sys/', '/proc/', LOCAL_DIR)):
                    continue
                self.remove_target_file(sfile)
            remove_content = reversed(tuple(remove_content))
            message.sub_debug('Removing directories')
            for sfile in remove_content:
                self.remove_target_dir(os.path.dirname(sfile))
            message.sub_debug('Removing links')
            for sfile in remove_content:
                self.remove_target_link(sfile)

            if misc.file_search('\npost_upgrade()', self.srcbuild, escape=False) \
                and SCRIPTS:
                message.sub_info('Executing post_upgrade()')
                misc.system_script(self.srcbuild, 'post_upgrade')
        elif misc.file_search('\npost_install()', self.srcbuild, escape=False) \
            and SCRIPTS:
            message.sub_info('Executing post_install()')
            misc.system_script(self.srcbuild, 'post_install')

        if target_upgrade:
            self.post_update_databases(new_content, 'upgrade')
        else:
            self.post_update_databases(new_content, 'merge')

        if target_upgrade:
            message.sub_info('Checking reverse dependencies')
            rdepends = database.local_rdepends(self.target_name)

            if rdepends and self.do_reverse:
                for target in rdepends:
                    message.sub_debug('Checking', target)
                    dependencies = ''
                    for dep in database.local_metadata(target, 'autodepends'):
                        dependencies += '%s|' % (re.escape(dep))
                    dependencies = dependencies[:-1]
                    if dependencies and not database.local_belongs(dependencies, escape=False, exact=True):
                        self.autosource([target], automake=True)
                        break
            elif rdepends:
                message.sub_warning('Targets may need rebuild', rdepends)

        # do not wait for the cache notifier to kick in
        database.LOCAL_CACHE = {}

    def remove(self):
        ''' Remove target files from system '''
        if not database.local_search(self.target_name):
            message.sub_critical('Already removed', self.target_name)
            sys.exit(2)

        message.sub_info('Checking dependencies')
        depends_detected = database.local_rdepends(self.target_name)
        # on autoremove ignore reverse dependencies asuming they have been
        # processed already and passed to the class initializer in proper order
        # by the initial checker with indirect reverse dependencies on
        if depends_detected and self.do_reverse and not self.autoremove:
            message.sub_info('Removing reverse dependencies', depends_detected)
            self.autosource(depends_detected, autoremove=True)
            message.sub_info('Resuming removal of', self.target_name)
        elif depends_detected and not self.autoremove:
            message.sub_critical('Other targets depend on %s' % \
                self.target_name, depends_detected)
            sys.exit(2)

        if misc.file_search('\npre_remove()', self.srcbuild, escape=False) \
            and SCRIPTS:
            message.sub_info('Executing pre_remove()')
            misc.system_script(self.srcbuild, 'pre_remove')

        message.sub_info('Indexing content')
        target_content = database.local_metadata(self.target_name, 'footprint')

        if target_content:
            self.pre_update_databases(target_content, 'remove')

            message.sub_info('Removing files')
            for sfile in target_content:
                self.remove_target_file(sfile)

            message.sub_info('Removing directories')
            for sfile in reversed(target_content):
                self.remove_target_dir(os.path.dirname(sfile))

            message.sub_info('Removing links')
            for sfile in reversed(target_content):
                self.remove_target_link(sfile)

        if misc.file_search('\npost_remove()', self.srcbuild, escape=False) \
            and SCRIPTS:
            message.sub_info('Executing post_remove()')
            misc.system_script(self.srcbuild, 'post_remove')

        message.sub_info('Removing metadata and SRCBUILD')
        self.remove_target_file(self.target_metadata)
        self.remove_target_file(self.target_srcbuild)
        self.remove_target_dir('%s/%s' % (LOCAL_DIR, self.target_name))

        if target_content:
            self.post_update_databases(target_content, 'remove')

        # do not wait for the cache notifier to kick in
        database.LOCAL_CACHE = {}

    def main(self):
        ''' Execute action for every target '''
        # resolve aliases and meta groups
        for alias in database.remote_aliases():
            if alias in self.targets:
                position = self.targets.index(alias)
                self.targets[position:position + 1] = \
                    database.remote_alias(alias)

        for target in self.targets:
            # make sure target is absolute path
            if os.path.isdir(target):
                target = os.path.abspath(target)

            target_name = os.path.basename(target)
            if target_name in IGNORE:
                message.sub_warning('Ignoring target', target_name)
                continue

            target_dir = database.remote_search(target)
            # fallback to the local SRCBUILD, only on target removal
            if not target_dir and (self.do_remove or self.autoremove):
                target_dir = database.local_search(target)
            if not target_dir:
                message.sub_critical('Invalid target', target)
                sys.exit(2)

            # set target properties
            self.target = target
            self.target_name = target_name
            self.target_dir = target_dir
            self.srcbuild = '%s/SRCBUILD' % self.target_dir
            self.target_version = database.remote_metadata(self.target_dir, 'version')
            self.target_release = database.remote_metadata(self.target_dir, 'release')
            self.target_description = database.remote_metadata(self.target_dir, 'description')
            self.target_depends = database.remote_metadata(self.target_dir, 'depends')
            self.target_optdepends = database.remote_metadata(self.target_dir, 'optdepends')
            self.target_sources = database.remote_metadata(self.target_dir, 'sources')
            self.target_pgpkeys = database.remote_metadata(self.target_dir, 'pgpkeys')
            self.target_options = database.remote_metadata(self.target_dir, 'options')
            self.target_backup = database.remote_metadata(self.target_dir, 'backup')
            self.source_dir = '%s/%s/%s/source' % (BUILD_DIR, self.target_name, self.target_version)
            self.install_dir = '%s/%s/%s/install' % (BUILD_DIR, self.target_name, self.target_version)
            self.target_metadata = 'var/local/spm/%s/metadata.json' % self.target_name
            self.target_srcbuild = 'var/local/spm/%s/SRCBUILD' % self.target_name
            self.sources_dir = '%s/sources/%s' % (CACHE_DIR, self.target_name)
            self.target_tarball = '%s/tarballs/%s_%s.tar.gz' % (CACHE_DIR, \
                self.target_name, self.target_version)

            if database.local_uptodate(self.target) \
                and not database.local_downgrade(self.target) and self.do_update:
                message.sub_warning('Target is up-to-date', self.target)
                continue

            for option in self.target_options:
                if option == 'verify' and not self.verify:
                    message.sub_warning('Overriding VERIFY to', 'True')
                    self.verify = True
                elif option == '!verify' and self.verify:
                    message.sub_warning('Overriding VERIFY to', 'False')
                    self.verify = False

                if option == 'mirror' and not self.mirror:
                    message.sub_warning('Overriding MIRROR to', 'True')
                    self.mirror = True
                elif option == '!mirror' and self.mirror:
                    message.sub_warning('Overriding MIRROR to', 'False')
                    self.mirror = False

                if option == 'man' and not self.compress_man:
                    message.sub_warning('Overriding COMPRESS_MAN to', 'True')
                    self.compress_man = True
                elif option == '!man' and self.compress_man:
                    message.sub_warning('Overriding COMPRESS_MAN to', 'False')
                    self.compress_man = False

                if option == 'binaries' and not self.strip_binaries:
                    message.sub_warning('Overriding STRIP_BINARIES to', 'True')
                    self.strip_binaries = True
                elif option == '!binaries' and self.strip_binaries:
                    message.sub_warning('Overriding STRIP_BINARIES to', 'False')
                    self.strip_binaries = False

                if option == 'shared' and not self.strip_shared:
                    message.sub_warning('Overriding STRIP_SHARED to', 'True')
                    self.strip_shared = True
                elif option == '!shared' and self.strip_shared:
                    message.sub_warning('Overriding STRIP_SHARED to', 'False')
                    self.strip_shared = False

                if option == 'static' and not self.strip_static:
                    message.sub_warning('Overriding STRIP_STATIC to', 'True')
                    self.strip_static = True
                elif option == '!static' and self.strip_static:
                    message.sub_warning('Overriding STRIP_STATIC to', 'False')
                    self.strip_static = False

                if option == 'missing' and not self.ignore_missing:
                    message.sub_warning('Overriding IGNORE_MISSING to', 'True')
                    self.ignore_missing = True
                elif option == '!missing' and self.ignore_missing:
                    message.sub_warning('Overriding IGNORE_MISSING to', 'False')
                    self.ignore_missing = False

                if option == 'ownership' and not self.ignore_ownership:
                    message.sub_warning('Overriding IGNORE_MISSING to', 'True')
                    self.ignore_ownership = True
                elif option == '!ownership' and self.ignore_ownership:
                    message.sub_warning('Overriding IGNORE_OWNERSHIP to', 'False')
                    self.ignore_ownership = False

                # that's a bit of exception since it is a string
                if option == '!purge' and self.purge_paths:
                    message.sub_warning('Overriding PURGE_PATHS to', 'False')
                    self.purge_paths = False

            if self.do_clean or self.automake:
                message.sub_info('Starting cleanup of', self.target_name)
                self.clean()

            if self.do_fetch or self.automake:
                message.sub_info('Starting fetch of', self.target_name)
                self.fetch()

            if self.do_prepare or self.automake:
                message.sub_info('Starting preparations of', self.target_name)
                self.prepare(True)

            if self.do_compile or self.automake:
                message.sub_info('Starting compile of', self.target_name)
                self.compile(True)

            if self.do_check:
                message.sub_info('Starting check of', self.target_name)
                self.check(True)

            if self.do_install or self.automake:
                message.sub_info('Starting install of', self.target_name)
                self.install()

            if self.do_merge or self.automake:
                message.sub_info('Starting merge of', self.target_name)
                self.merge()

            if self.do_remove or self.autoremove:
                message.sub_info('Starting remove of', self.target_name)
                self.remove()

            # reset values so that overrides apply only to single target
            self.verify = VERIFY
            self.mirror = MIRROR
            self.purge_paths = PURGE_PATHS
            self.compress_man = COMPRESS_MAN
            self.strip_binaries = STRIP_BINARIES
            self.strip_shared = STRIP_SHARED
            self.strip_static = STRIP_STATIC
            self.ignore_missing = IGNORE_MISSING
            self.ignore_ownership = IGNORE_OWNERSHIP

wantscookie = '''
                       _           |
      -*~*-          _|_|_         |.===.       `  _ ,  '        ()_()
      (o o)          (o o)         {}o o{}     -  (o)o)  -       (o o)
--ooO--(_)--Ooo--ooO--(_)--Ooo--ooO--(_)--Ooo--ooO'(_)--Ooo--ooO--`o'--Ooo--
'''

class Who(object):
    ''' Class for printing file owner '''
    def __init__(self, pattern, plain=False):
        self.pattern = pattern
        self.plain = plain
        misc.OFFLINE = OFFLINE
        misc.TIMEOUT = TIMEOUT
        misc.ROOT_DIR = ROOT_DIR
        misc.GPG_DIR = GPG_DIR
        misc.SHELL = SHELL
        database.ROOT_DIR = ROOT_DIR
        database.CACHE_DIR = CACHE_DIR
        database.LOCAL_DIR = LOCAL_DIR
        database.IGNORE = IGNORE
        database.NOTIFY = NOTIFY

    def main(self):
        ''' Print owner of files pattern '''
        for target in database.local_belongs(self.pattern, escape=False):
            if self.plain:
                print(target)
            else:
                message.sub_info('Match in', target)
