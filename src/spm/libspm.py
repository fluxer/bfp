#!/bin/python2

import sys
import os
import shutil
import re
import compileall, site
from datetime import datetime
if sys.version < '3':
    import ConfigParser as configparser
else:
    import configparser

import libmessage
message = libmessage.Message()
import libmisc
misc = libmisc.Misc()
import libpackage
database = libpackage.Database()


MAIN_CONF = '/etc/spm.conf'
REPOSITORIES_CONF = '/etc/spm/repositories.conf'
MIRRORS_CONF = '/etc/spm/mirrors.conf'
TRIGGERS_CONF = '/etc/spm/triggers.conf'

if not os.path.isfile(MAIN_CONF):
    message.warning('Configuration file does not exist', MAIN_CONF)

    CACHE_DIR = '/var/cache/spm'
    BUILD_DIR = '/var/tmp/spm'
    ROOT_DIR = '/'
    LOCAL_DIR = ROOT_DIR + 'var/local/spm'
    IGNORE = []
    DEMOTE = ''
    OFFLINE = False
    MIRROR = False
    TIMEOUT = 30
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
    PYTHON_COMPILE = False
    IGNORE_MISSING = False
    CONFLICTS = False
    BACKUP = False
    SCRIPTS = False
    TRIGGERS = False
else:
    conf = configparser.SafeConfigParser()
    conf.read(MAIN_CONF)

    CACHE_DIR = conf.get('spm', 'CACHE_DIR')
    BUILD_DIR = conf.get('spm', 'BUILD_DIR')
    ROOT_DIR = conf.get('spm', 'ROOT_DIR')
    LOCAL_DIR = ROOT_DIR + 'var/local/spm'
    IGNORE = conf.get('spm', 'IGNORE').split(' ')
    DEMOTE = conf.get('spm', 'DEMOTE')
    OFFLINE = conf.getboolean('prepare', 'OFFLINE')
    MIRROR = conf.getboolean('prepare', 'MIRROR')
    TIMEOUT = conf.getint('prepare', 'TIMEOUT')
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
    PYTHON_COMPILE = conf.getboolean('install', 'PYTHON_COMPILE')
    IGNORE_MISSING = conf.getboolean('install', 'IGNORE_MISSING')
    CONFLICTS = conf.getboolean('merge', 'CONFLICTS')
    BACKUP = conf.getboolean('merge', 'BACKUP')
    SCRIPTS = conf.getboolean('merge', 'SCRIPTS')
    TRIGGERS = conf.getboolean('merge', 'TRIGGERS')

# parse repositories configuration file
if not os.path.isfile(REPOSITORIES_CONF):
    message.warning('Repositories file does not exist', REPOSITORIES_CONF)
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
        message.critical('Repositories configuration file is empty')
        sys.exit(2)

# parse mirrors configuration file
if not os.path.isfile(MIRRORS_CONF):
    message.warning('Mirrors file does not exist', MIRRORS_CONF)
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
        message.critical('Mirrors configuration file is empty')
        sys.exit(2)

# override module variables from own configuration
misc.OFFLINE = OFFLINE
misc.TIMEOUT = TIMEOUT
misc.ROOT_DIR = ROOT_DIR
database.ROOT_DIR = ROOT_DIR
database.CACHE_DIR = CACHE_DIR
database.LOCAL_DIR = LOCAL_DIR
database.IGNORE = IGNORE

class Local(object):
    ''' Class for printing local targets metadata '''
    def __init__(self, pattern, do_name=False, do_version=False, \
        do_description=False, do_depends=False, do_reverse=False, \
        do_size=False, do_footprint=False, plain=False):
        self.pattern = pattern
        self.do_name = do_name
        self.do_version = do_version
        self.do_description = do_description
        self.do_depends = do_depends
        self.do_reverse = do_reverse
        self.do_size = do_size
        self.do_footprint = do_footprint
        self.plain = plain
        misc.OFFLINE = OFFLINE
        misc.TIMEOUT = TIMEOUT
        misc.ROOT_DIR = ROOT_DIR
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
                    message.sub_info('Name', target)

                if self.do_version:
                    data = database.local_metadata(target, 'version')
                    if self.plain:
                        print(data)
                    else:
                        message.sub_info('Version', data)

                if self.do_description:
                    data = database.local_metadata(target, 'description')
                    if self.plain:
                        print(data)
                    else:
                        message.sub_info('Description', data)

                if self.do_depends:
                    data = database.local_metadata(target, 'depends')
                    if self.plain:
                        print(misc.string_convert(data))
                    else:
                        message.sub_info('Depends', data)

                if self.do_reverse:
                    data = database.local_rdepends(target)
                    if self.plain:
                        print(misc.string_convert(data))
                    else:
                        message.sub_info('Reverse depends', data)

                if self.do_size:
                    data = database.local_metadata(target, 'size')
                    if self.plain:
                        print(data)
                    else:
                        message.sub_info('Size', data)

                if self.do_footprint:
                    data = database.local_footprint(target)
                    if self.plain:
                        print(data)
                    else:
                        message.sub_info('Footprint', data)


class Remote(object):
    ''' Class for printing remote targets metadata '''
    def __init__(self, pattern, do_name=False, do_version=False, \
        do_description=False, do_depends=False, do_makedepends=False, \
        do_checkdepends=False, do_sources=False, do_options=False, \
        do_backup=False, plain=False):
        self.pattern = pattern
        self.do_name = do_name
        self.do_version = do_version
        self.do_description = do_description
        self.do_depends = do_depends
        self.do_makedepends = do_makedepends
        self.do_checkdepends = do_checkdepends
        self.do_sources = do_sources
        self.do_options = do_options
        self.do_backup = do_backup
        self.plain = plain
        misc.OFFLINE = OFFLINE
        misc.TIMEOUT = TIMEOUT
        misc.ROOT_DIR = ROOT_DIR
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
                    message.sub_info('Name', target)

                # asigning data variable only for the sake of readability
                if self.do_version:
                    data = database.remote_metadata(target, 'version')
                    if self.plain:
                        print(data)
                    else:
                        message.sub_info('Version', data)

                if self.do_description:
                    data = database.remote_metadata(target, 'description')
                    if self.plain:
                        print(data)
                    else:
                        message.sub_info('Description', data)

                if self.do_depends:
                    data = database.remote_metadata(target, 'depends')
                    if self.plain:
                        print(misc.string_convert(data))
                    else:
                        message.sub_info('Depends', data)

                if self.do_makedepends:
                    data = database.remote_metadata(target, 'makedepends')
                    if self.plain:
                        print(misc.string_convert(data))
                    else:
                        message.sub_info('Make depends', data)

                if self.do_checkdepends:
                    data = database.remote_metadata(target, 'checkdepends')
                    if self.plain:
                        print(misc.string_convert(data))
                    else:
                        message.sub_info('Check depends', data)

                if self.do_sources:
                    data = database.remote_metadata(target, 'sources')
                    if self.plain:
                        print(misc.string_convert(data))
                    else:
                        message.sub_info('Sources', data)

                if self.do_options:
                    data = database.remote_metadata(target, 'options')
                    if self.plain:
                        print(misc.string_convert(data))
                    else:
                        message.sub_info('Options', data)

                if self.do_backup:
                    data = database.remote_metadata(target, 'backup')
                    if self.plain:
                        print(misc.string_convert(data))
                    else:
                        message.sub_info('Backup', data)


class Repo(object):
    ''' Class for dealing with repositories '''
    def __init__(self, repositories_urls, do_clean=False, do_sync=False, \
        do_update=False, do_prune=False):
        self.repositories_urls = repositories_urls
        self.do_clean = do_clean
        self.do_sync = do_sync
        self.do_prune = do_prune
        self.do_update = do_update
        misc.OFFLINE = OFFLINE
        misc.TIMEOUT = TIMEOUT
        misc.ROOT_DIR = ROOT_DIR
        database.ROOT_DIR = ROOT_DIR
        database.CACHE_DIR = CACHE_DIR
        database.LOCAL_DIR = LOCAL_DIR
        database.IGNORE = IGNORE

    def clean(self):
        ''' Clean repository '''
        if os.path.isdir(self.repository_dir):
            message.sub_info('Removing', self.repository_dir)
            misc.dir_remove(self.repository_dir)
        else:
            message.sub_debug('Dirctory is OK', self.repository_dir)

    def sync(self):
        ''' Sync repository '''
        rdir = os.path.join(CACHE_DIR, 'repositories')
        misc.dir_create(rdir, DEMOTE)

        if os.path.exists(self.repository_url):
            # repository is local path, create a copy of it
            message.sub_info('Cloning local', self.repository_name)
            shutil.copytree(self.repository_url, self.repository_dir)
        elif os.path.isdir(self.repository_dir):
            # existing Git repository
            message.sub_info('Updating repository', self.repository_name)
            misc.system_command((misc.whereis('git'), 'pull', '--depth=1', \
                self.repository_url), cwd=self.repository_dir, demote=DEMOTE)
        else:
            # non-existing Git repository, fetch
            message.sub_info('Cloning remote', self.repository_name)
            misc.system_command((misc.whereis('git'), 'clone', '--depth=1', \
                self.repository_url, self.repository_dir), demote=DEMOTE)

    def prune(self):
        ''' Remove repositories that are no longer in the config '''
        rdir = os.path.join(CACHE_DIR, 'repositories')
        if not os.path.exists(rdir):
            return

        for sdir in os.listdir(rdir):
            valid = False
            for line in misc.file_readlines('/etc/spm/repositories.conf'):
                if not line or line.startswith('#'):
                    continue

                if os.path.basename(line) == sdir:
                    valid = True

            if not valid:
                repo_dir = os.path.join(rdir, sdir)
                message.sub_warning('Removing', repo_dir)
                misc.dir_remove(repo_dir)

    def update(self):
        ''' Check repositories for updates '''
        message.sub_info('Checking for updates')
        for target in database.local_all(basename=True):
            target_dir = database.remote_search(target)
            if not target_dir:
                message.sub_warning('Target not in any repository', target)
                continue

            message.sub_debug('Checking', target)
            if not database.local_uptodate(target):
                message.sub_warning('New version of %s available' % target, \
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
                message.sub_info('Starting cleanup at', datetime.today())
                self.clean()

            if self.do_sync:
                message.sub_info('Starting sync at', datetime.today())
                self.sync()

        if self.do_prune:
            message.sub_info('Starting prune at', datetime.today())
            self.prune()

        if self.do_update:
            message.sub_info('Starting update at', datetime.today())
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
        self.mirror = MIRROR
        self.strip_binaries = STRIP_BINARIES
        self.strip_shared = STRIP_SHARED
        self.strip_static = STRIP_STATIC
        self.strip_rpath = STRIP_RPATH
        self.compress_man = COMPRESS_MAN
        self.ignore_missing = IGNORE_MISSING
        self.python_compile = PYTHON_COMPILE
        misc.OFFLINE = OFFLINE
        misc.TIMEOUT = TIMEOUT
        misc.ROOT_DIR = ROOT_DIR
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

    def update_databases(self, content, action):
        ''' Update common databases '''
        if not TRIGGERS:
            return

        ldconfig = misc.whereis('ldconfig', False, True)
        message.sub_debug('ldconfig', ldconfig or '')
        mandb = misc.whereis('mandb', False, True)
        message.sub_debug('mandb', mandb or '')
        desktop_database = misc.whereis('update-desktop-database', False, True)
        message.sub_debug('update-desktop-database', desktop_database or '')
        mime_database = misc.whereis('update-mime-database', False, True)
        message.sub_debug('update-mime-database', mime_database or '')
        icon_resources = misc.whereis('xdg-icon-resource', False, True)
        message.sub_debug('xdg-icon-resources', icon_resources or '')
        xmime = misc.whereis('xdg-mime', False, True)
        message.sub_debug('xdg-mime', xmime or '')
        gio_querymodules = misc.whereis('gio-querymodules', False, True)
        message.sub_debug('gio-querymodules', gio_querymodules or '')
        pango_querymodules = misc.whereis('pango-querymodules', False, True)
        message.sub_debug('pango-querymodules', pango_querymodules or '')
        gtk2_immodules = misc.whereis('gtk-query-immodules-2.0', False, True)
        message.sub_debug('gtk-query-imodules-2.0', gtk2_immodules or '')
        gtk3_immodules = misc.whereis('gtk-query-immodules-3.0', False, True)
        message.sub_debug('gtk-query-imodules-3.0', gtk3_immodules or '')
        gdk_pixbuf = misc.whereis('gdk-pixbuf-query-loaders', False, True)
        message.sub_debug('gdk-pixbuf-query-loaders', gdk_pixbuf or '')
        glib_schemas = misc.whereis('glib-compile-schemas', False, True)
        message.sub_debug('glib-compile-schemas', glib_schemas or '')
        udevadm = misc.whereis('udevadm', False, True)
        message.sub_debug('udevadm', udevadm or '')
        install_info = misc.whereis('install-info', False, True)
        message.sub_debug('install-info', install_info or '')
        icon_cache = misc.whereis('gtk-update-icon-cache', False, True)
        message.sub_debug('gtk-update-icon-cache', icon_cache or '')
        depmod = misc.whereis('depmod', False, True)
        message.sub_debug('depmod', depmod or '')
        depmod_run = False
        depmod_path = None
        mkinitfs = misc.whereis('mkinitfs', False, True)
        message.sub_debug('mkinitfs', mkinitfs or '')
        mkinitfs_run = False
        mkinitfs_path = None
        grub_mkconfig = misc.whereis('grub-mkconfig', False, True)
        message.sub_debug('grub-mkconfig', grub_mkconfig or '')
        grub_mkconfig_run = False
        grub_mkconfig_path = None
        for spath in content:
            if spath.endswith('.so') and ldconfig:
                message.sub_info('Updating shared libraries cache')
                message.sub_debug(spath)
                misc.system_trigger((ldconfig))
                ldconfig = False
            elif 'share/man' in spath and mandb:
                message.sub_info('Updating manual pages database')
                message.sub_debug(spath)
                misc.system_trigger((mandb, '--quiet'))
                mandb = False
            elif 'share/applications/' in spath and desktop_database:
                message.sub_info('Updating desktop database')
                message.sub_debug(spath)
                misc.system_trigger((desktop_database, \
                    sys.prefix + '/share/applications'))
                desktop_database = False
            elif 'share/mime/' in spath and mime_database:
                message.sub_info('Updating MIME database')
                message.sub_debug(spath)
                misc.system_trigger((mime_database, sys.prefix + '/share/mime'))
                mime_database = False
            elif 'share/icons/' in spath and icon_resources:
                message.sub_info('Updating icon resources')
                message.sub_debug(spath)
                misc.system_trigger((icon_resources, 'forceupdate', \
                    '--theme', 'hicolor'))
                icon_resources = False
            elif 'mime/' in spath and '-' in os.path.basename(spath) \
                and spath.endswith('.xml') and xmime:
                if action == 'merge':
                    message.sub_info('Installing XDG MIMEs')
                    message.sub_debug(spath)
                    misc.system_trigger((xmime, 'install', spath))
                elif action == 'remove':
                    message.sub_info('Uninstalling XDG MIMEs')
                    message.sub_debug(spath)
                    misc.system_trigger((xmime, 'uninstall', spath))
            elif '/gio/modules/' in spath and gio_querymodules:
                message.sub_info('Updating GIO modules cache')
                message.sub_debug(spath)
                misc.system_trigger((gio_querymodules, os.path.dirname(spath)))
                gio_querymodules = False
            elif '/pango/' in spath and '/modules/' in spath and pango_querymodules:
                message.sub_info('Updating pango modules cache')
                message.sub_debug(spath)
                misc.system_trigger((pango_querymodules, '--update-cache'))
                pango_querymodules = False
            elif '/gtk-2.0/' in spath and '/immodules/' in spath and gtk2_immodules:
                message.sub_info('Updating GTK-2.0 imodules cache')
                message.sub_debug(spath)
                misc.dir_create(ROOT_DIR + '/etc/gtk-2.0')
                misc.system_trigger(gtk2_immodules + \
                    ' > /etc/gtk-2.0/gtk.immodules', shell=True)
                gtk2_immodules = False
            elif '/gtk-3.0/' in spath and '/immodules/' in spath and gtk3_immodules:
                message.sub_info('Updating GTK-3.0 imodules cache')
                message.sub_debug(spath)
                misc.dir_create(ROOT_DIR + '/etc/gtk-3.0')
                misc.system_trigger(gtk3_immodules + \
                    ' > /etc/gtk-3.0/gtk.immodules', shell=True)
                gtk3_immodules = False
            elif '/gdk-pixbuf' in spath and gdk_pixbuf:
                message.sub_info('Updating gdk pixbuffer loaders')
                message.sub_debug(spath)
                misc.dir_create(ROOT_DIR + '/etc/gtk-2.0')
                misc.system_trigger(gdk_pixbuf + \
                    ' > /etc/gtk-2.0/gdk-pixbuf.loaders', shell=True)
                gdk_pixbuf = False
            elif '/schemas/' in spath and glib_schemas:
                message.sub_info('Updating GSettings schemas')
                message.sub_debug(spath)
                misc.system_trigger((glib_schemas, os.path.dirname(spath)))
                glib_schemas = False
            elif spath.startswith('lib/modules/') and depmod:
                # extract the kernel modules path, e.g. lib/modules/3.16.8
                depmod_path = misc.string_convert(misc.string_search('(?:usr/?)?lib/modules/(.*?)/', \
                    spath, escape=False))
                depmod_run = True
                mkinitfs_run = True
            elif '/udev/rules.d/' in spath and \
                (os.path.exists(ROOT_DIR + 'run/udev/control') \
                or os.path.exists(ROOT_DIR + 'var/run/udev/control')) and udevadm:
                message.sub_info('Reloading udev rules and hwdb')
                message.sub_debug(spath)
                misc.system_trigger((udevadm, 'control', '--reload'))
                udevadm = False
            elif spath.startswith(('boot/vmlinuz', 'etc/mkinitfs/')) and mkinitfs:
                mkinitfs_path = misc.string_convert(misc.string_search('boot/vmlinuz-(.*)', \
                    spath, escape=False))
                mkinitfs_run = True
            elif spath.startswith(('boot/', 'etc/grub.d/')) \
                and os.path.isfile(os.path.join(ROOT_DIR, 'boot/grub/grub.cfg')) \
                and grub_mkconfig:
                # the trigger executes only if grub.cfg is present asuming GRUB
                # is installed, otherwise there is no point in updating it
                grub_mkconfig_path = spath
                grub_mkconfig_run = True
            elif 'share/icons/' in spath and action == 'merge' and icon_cache:
                # extract the proper directory from spath, e.g. /share/icons/hicolor
                sdir = misc.string_search('((?:usr/?)?share/icons/(?:.*?))', \
                    spath, escape=False)
                sdir = misc.string_convert(sdir)
                if not os.path.isfile(ROOT_DIR + sdir + '/index.theme'):
                    continue
                message.sub_info('Updating icons cache')
                message.sub_debug(spath)
                misc.system_trigger((icon_cache, '-q', '-t', '-i', '-f', sdir))
                icon_cache = False
            elif 'share/info/' in spath and install_info:
                # allowed to run multiple times
                if action == 'merge':
                    message.sub_info('Installing info page', spath)
                    message.sub_debug(spath)
                    misc.system_trigger((install_info, spath, \
                        sys.prefix + '/share/info/dir'))
                elif action == 'remove':
                    message.sub_info('Deleting info page', spath)
                    message.sub_debug(spath)
                    misc.system_trigger((install_info, '--delete', spath, \
                    sys.prefix + '/share/info/dir'))
        # delayed triggers which need to run in specifiec order
        if depmod_run:
            message.sub_info('Updating module dependencies')
            message.sub_debug(depmod_path)
            misc.system_trigger((depmod, depmod_path))
        # distribution specifiec
        if mkinitfs_run:
            message.sub_info('Updating initramfs image')
            message.sub_debug(mkinitfs_path)
            if mkinitfs_path:
                # new kernel being installed
                misc.system_trigger((mkinitfs, '-k', mkinitfs_path))
            else:
                misc.system_trigger((mkinitfs))
        if grub_mkconfig_run:
            message.sub_info('Updating GRUB configuration')
            message.sub_debug(grub_mkconfig_path)
            misc.dir_create(ROOT_DIR + '/boot/grub')
            misc.system_trigger((grub_mkconfig, '-o', '/boot/grub/grub.cfg'))

    def remove_target_file(self, sfile):
        ''' Remove target file '''
        sfull = ROOT_DIR + sfile
        if os.path.isfile(sfull):
            message.sub_debug('Removing', sfull)
            os.unlink(sfull)

    def remove_target_dir(self, sdir):
        ''' Remove target directory '''
        sfull = ROOT_DIR + sdir
        if os.path.isdir(sfull) and not os.listdir(sfull):
            message.sub_debug('Removing', sfull)
            if os.path.islink(sfull):
                os.unlink(sfull)
            else:
                os.rmdir(sfull)

    def remove_target_link(self, slink):
        ''' Remove target link (sym/hard) '''
        sfull = ROOT_DIR + slink
        if os.path.islink(sfull) and \
            not os.path.exists(ROOT_DIR + '/' + os.readlink(sfull)):
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
            message.sub_debug('Dirctory is OK', self.install_dir)

        if os.path.isdir(self.source_dir) and self.do_prepare:
            message.sub_info('Removing', self.source_dir)
            misc.dir_remove(self.source_dir)
        elif os.path.isdir(self.source_dir) and not self.do_install:
            message.sub_info('Removing', self.source_dir)
            misc.dir_remove(self.source_dir)
        else:
            message.sub_debug('Dirctory is OK', self.source_dir)

    def prepare(self):
        ''' Prepare target sources '''
        message.sub_info('Checking dependencies')
        missing_dependencies = database.remote_mdepends(self.target, \
            cdepends=self.do_check)

        if missing_dependencies and self.do_depends:
            message.sub_info('Building dependencies', missing_dependencies)
            self.autosource(missing_dependencies, automake=True)
            message.sub_info('Resuming %s preparations at' % \
                os.path.basename(self.target), datetime.today())
        elif missing_dependencies:
            message.sub_warning('Dependencies missing', missing_dependencies)

        misc.dir_create(self.source_dir, DEMOTE)
        misc.dir_create(self.sources_dir, DEMOTE)

        message.sub_info('Preparing sources')
        for src_url in self.target_sources:
            src_base = os.path.basename(src_url)
            local_file = os.path.join(self.sources_dir, src_base)
            src_file = os.path.join(self.target_dir, src_base)
            link_file = os.path.join(self.source_dir, src_base)
            internet = misc.ping()

            if src_url.startswith('git://') or src_url.endswith('.git'):
                if not internet:
                    message.sub_warning('Internet connection is down')
                elif os.path.isdir(link_file):
                    message.sub_debug('Updating repository', src_url)
                    misc.system_command((misc.whereis('git'), 'pull', \
                        '--depth=1', src_url), cwd=link_file, demote=DEMOTE)
                else:
                    message.sub_debug('Cloning initial copy', src_url)
                    misc.system_command((misc.whereis('git'), 'clone', \
                        '--depth=1', src_url, link_file), demote=DEMOTE)
                continue

            elif src_url.startswith(('http://', 'https://', 'ftp://', \
                'ftps://')):
                if not internet:
                    message.sub_warning('Internet connection is down')
                elif self.mirror:
                    for mirror in MIRRORS:
                        url = mirror + '/distfiles/' + src_base
                        message.sub_debug('Checking mirror', mirror)
                        if misc.ping(url):
                            src_url = url
                            break

                if os.path.isfile(local_file) and internet:
                    message.sub_debug('Checking', local_file)
                    if misc.fetch_check(src_url, local_file):
                        message.sub_debug('Already fetched', src_url)
                    else:
                        message.sub_warning('Re-fetching', src_url)
                        misc.fetch(src_url, local_file)
                elif internet:
                    message.sub_debug('Fetching', src_url)
                    misc.fetch(src_url, local_file)

            if os.path.islink(link_file):
                message.sub_debug('Already linked', src_file)
            elif os.path.isfile(src_file):
                message.sub_debug('Linking', src_file)
                os.symlink(src_file, link_file)
            elif os.path.isfile(local_file):
                message.sub_debug('Linking', local_file)
                os.symlink(local_file, link_file)

            if misc.archive_supported(link_file):
                decompressed = False
                for sfile in misc.archive_list(link_file):
                    if not os.path.exists(os.path.join(self.source_dir, sfile)):
                        message.sub_debug('Extracting', link_file)
                        misc.archive_decompress(link_file, self.source_dir, DEMOTE)
                        decompressed = True
                        break
                if not decompressed:
                    message.sub_debug('Already extracted', link_file)

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

        misc.system_command((misc.whereis('bash'), '-e', '-c', 'source ' + \
            self.srcbuild + ' && umask 0022 && src_install'), \
            cwd=self.source_dir)

        if self.compress_man:
            message.sub_info('Compressing manual pages')
            manpath = misc.whereis('manpath', fallback=False)
            # if manpath (provided by man-db) is not present fallback to something sane
            if not manpath:
                mpaths = ('/usr/local/share/man', '/local/share/man', \
                    '/usr/share/man', '/share/man', '/usr/man', '/man')
            else:
                mpaths = misc.system_output((manpath, '--global')).split(':')

            for sdir in mpaths:
                for sfile in misc.list_files(self.install_dir + sdir):
                    if not sfile.endswith('.gz') and os.path.isfile(sfile):
                        message.sub_debug('Compressing', sfile)
                        misc.archive_compress(sfile, sfile + '.gz', '')
                        os.unlink(sfile)
                    elif os.path.islink(sfile) and \
                        not os.path.isfile(os.path.realpath(sfile)):
                        message.sub_debug('Adjusting link', sfile)
                        link = os.readlink(sfile)
                        if not sfile.endswith('.gz'):
                            os.unlink(sfile)
                            os.symlink(link + '.gz', sfile)
                        else:
                            os.unlink(sfile)
                            os.symlink(link, sfile)

        message.sub_info('Indexing content')
        target_content = {}
        for sfile in misc.list_files(self.install_dir):
            # skip footprint and metadata, they are not wanted in the footprint
            if sfile == os.path.join(self.install_dir, self.target_footprint) \
                or sfile == os.path.join(self.install_dir, self.target_metadata):
                continue
            # remove common conflict files/directories
            elif sfile.endswith('/.packlist') or sfile.endswith('/perllocal.pod') \
                or sfile.endswith('/share/info/dir'):
                os.unlink(sfile)
                continue
            target_content[sfile] = misc.file_mime(sfile)

        if self.strip_binaries or self.strip_shared or \
            self.strip_static or self.strip_rpath:
            message.sub_info('Stripping binaries and libraries')
            strip = misc.whereis('strip')
            scanelf = misc.whereis('scanelf')
            for sfile in target_content:
                smime = target_content[sfile]
                if os.path.islink(sfile):
                    continue

                if smime == 'application/x-executable' and self.strip_binaries:
                    message.sub_debug('Stripping executable', sfile)
                    misc.system_command((strip, '--strip-all', sfile))
                elif smime == 'application/x-sharedlib' and self.strip_shared:
                    message.sub_debug('Stripping shared library', sfile)
                    misc.system_command((strip, '--strip-unneeded', sfile))
                elif smime == 'application/x-archive' and self.strip_static:
                    message.sub_debug('Stripping static library', sfile)
                    misc.system_command((strip, '--strip-debug', sfile))

                if (smime == 'application/x-executable' or \
                    smime == 'application/x-sharedlib' \
                    or smime == 'application/x-archive') and self.strip_rpath:
                    # do not check if RPATH is present at all to avoid
                    # spawning scanelf twice
                    message.sub_debug('Stripping RPATH', sfile)
                    misc.system_command((scanelf, '-CBXrq', sfile))

        message.sub_info('Checking runtime dependencies')
        missing_detected = False
        for sfile in target_content:
            smime = target_content[sfile]
            if os.path.islink(sfile):
                continue

            if smime == 'application/x-executable' or \
                smime == 'application/x-sharedlib':
                libraries = misc.system_scanelf(sfile)
                if not libraries:
                    continue # static binary
                for lib in libraries.split(','):
                    match = database.local_belongs(lib)
                    if match and len(match) > 1:
                        message.sub_warning('Multiple providers for %s' % lib, match)
                        if self.target_name in match:
                            match = self.target_name
                        else:
                            match = match[0]
                    match = misc.string_convert(match)

                    # list() - Python 3000 dictionary compat
                    if match == self.target_name or \
                        misc.string_search(lib, list(target_content.keys())):
                        message.sub_debug('Library needed but in self', lib)
                    elif match and match in self.target_depends:
                        message.sub_debug('Library needed but in depends', match)
                    elif match and not match in self.target_depends:
                        message.sub_debug('Library needed but in local', match)
                        self.target_depends.append(match)
                    elif self.ignore_missing:
                        message.sub_warning('Library needed, not in any local', lib)
                    else:
                        message.sub_critical('Library needed, not in any local', lib)
                        missing_detected = True

            elif smime == 'text/plain' or smime == 'text/x-shellscript' \
                or smime == 'text/x-python' or smime == 'text/x-perl' \
                or smime == 'text/x-php' or smime == 'text/x-ruby' \
                or smime == 'text/x-lua' or smime == 'text/x-tcl' \
                or smime == 'text/x-awk' or smime == 'text/x-gawk':
                # https://en.wikipedia.org/wiki/Comparison_of_command_shells
                bang_regexp = '^#!(?:(?: )+)?(?:/.*)+(?:(?: )+)?'
                bang_regexp += '(?:sh|bash|dash|ksh|csh|tcsh|tclsh|scsh|fish'
                bang_regexp += '|zsh|ash|python|perl|php|ruby|lua|wish|(?:g)?awk'
                bang_regexp += '|gbr2|gbr3)'
                bang_regexp += '(?:(?:\\d(?:.)?)+)?(?:\\s|$)'
                omatch = misc.file_search(bang_regexp, sfile, exact=False, escape=False)
                if omatch:
                    fmatch = omatch[0].replace('#!', '').strip()
                    # in cases when the match has two entries (e,g, /usr/bin/env python)
                    # substite /env with the basename of the follow up argument as it
                    # may be full path (e.g. /usr/bin/env /usr/bin/python, as of the time
                    # if writing this UFW is an example) preserving other arguments
                    if '/env' in fmatch:
                        fmatch = re.sub('/env(?:(?: )+)?' + fmatch.split()[1], \
                            '/' + os.path.basename(fmatch.split()[1]), fmatch)
                    smatch = self.install_dir + fmatch
                    match = database.local_belongs(fmatch, exact=True, escape=False)
                    # attempt shebang correction by probing PATH for basename matchers
                    # first and altering the shebang next
                    if not match:
                        message.sub_debug('Attempting shebang correction on', sfile)
                        # search for match on the host
                        hmatch = misc.whereis(os.path.basename(fmatch), False)
                        if hmatch:
                            match = database.local_belongs(hmatch, exact=True, escape=False)
                            if match:
                                misc.file_substitute('^' + omatch[0].strip(), \
                                    '#!' + hmatch, sfile)
                                message.sub_debug('Successfuly corrected (host)', fmatch)
                        # fallback to the content of the target (self provided)
                        else:
                            # FIXME: this only extends to binaries in <blah>/(s)bin,
                            # if shebang uses some strange path (e.g. /opt/<exec>)
                            # then this will not work
                            for s in list(target_content.keys()):
                                if s.endswith('bin/' + os.path.basename(fmatch)):
                                    smatch = s.replace(self.install_dir, '')
                                    break
                            if smatch:
                                misc.file_substitute('^' + omatch[0].strip(), \
                                    '#!' + smatch, sfile)
                                message.sub_debug('Successfuly corrected (self)', fmatch)
                                match = [self.target_name] # database.local_belongs() returns list
                    if match and len(match) > 1:
                        message.sub_warning('Multiple providers for %s' % fmatch, match)
                        if self.target_name in match:
                            match = self.target_name
                        else:
                            match = match[0]
                    match = misc.string_convert(match)

                    if match == self.target_name or misc.string_search(smatch, \
                        list(target_content.keys()), exact=True, escape=False):
                        message.sub_debug('Dependency needed but in self', match)
                    elif match and match in self.target_depends:
                        message.sub_debug('Dependency needed but in depends', match)
                    elif match and not match in self.target_depends:
                        message.sub_debug('Dependency needed but in local', match)
                        self.target_depends.append(match)
                    elif self.ignore_missing:
                        message.sub_warning('Dependency needed, not in any local', fmatch)
                    else:
                        message.sub_critical('Dependency needed, not in any local', fmatch)
                        missing_detected = True
        if missing_detected:
            sys.exit(2)

        if self.python_compile:
            message.sub_info('Byte-compiling Python modules')
            for sfile in target_content.keys():
                for spath in site.getsitepackages():
                    if not spath in sfile:
                        continue
                    message.sub_debug('Compiling Python file', sfile)
                    # force build the caches to prevent access time issues with
                    # .pyc files being older that .py files because .py files
                    # when modified after the usual installation procedure
                    compileall.compile_file(sfile, force=True, quiet=True)

        message.sub_info('Assembling metadata')
        misc.dir_create(os.path.join(self.install_dir, 'var/local/spm', self.target_name))
        metadata = open(os.path.join(self.install_dir, self.target_metadata), 'w')
        metadata.write('version=' + self.target_version + '\n')
        metadata.write('description=' + self.target_description + '\n')
        metadata.write('depends=' + misc.string_convert(self.target_depends) + '\n')
        metadata.write('size=' + str(misc.dir_size(self.install_dir)) + '\n')
        metadata.close()

        message.sub_info('Assembling footprint')
        misc.file_write(os.path.join(self.install_dir, self.target_footprint), \
            '\n'.join(sorted(list(target_content.keys()))).replace(self.install_dir, ''))

        message.sub_info('Compressing tarball')
        misc.dir_create(os.path.join(CACHE_DIR, 'tarballs'))
        misc.archive_compress(self.install_dir, self.target_tarball, \
            self.install_dir)

    def merge(self):
        ''' Merget target to system '''
        message.sub_info('Indexing content')
        new_content = misc.archive_list(self.target_tarball)
        old_content = database.local_footprint(self.target_name)

        if CONFLICTS:
            conflict_detected = False

            regex = '(?:\\s|^)('
            # first item is null ('') because root ('/') is stripped
            for sfile in new_content[1:]:
                if os.path.isdir(os.path.join(ROOT_DIR, sfile)):
                    continue
                regex += '/' + re.escape(sfile) + '|'
            regex = regex.rstrip('|') + ')(?:\\s|$)'

            message.sub_info('Checking for conflicts')
            for target in database.local_all(basename=True):
                if target == self.target_name:
                    continue

                match = misc.string_search(regex, database.local_footprint(target), escape=False)
                if match:
                    for m in match:
                        message.sub_critical('File/link conflict with %s' % target, m)
                    conflict_detected = True

            if conflict_detected:
                sys.exit(2)

        # store state installed or not, it must be done before the decompression
        target_upgrade = database.local_installed(self.target_name)

        if target_upgrade and SCRIPTS \
            and misc.file_search('\npre_upgrade()', self.srcbuild, escape=False):
            message.sub_info('Executing pre_upgrade()')
            misc.system_script(self.srcbuild, 'pre_upgrade')
        elif misc.file_search('\npre_install()', self.srcbuild, escape=False) \
            and SCRIPTS:
            message.sub_info('Executing pre_install()')
            misc.system_script(self.srcbuild, 'pre_install')

        if BACKUP:
            message.sub_info('Backing up files')
            check = []
            for sfile in new_content:
                if not os.path.isfile(os.path.join(ROOT_DIR, sfile)):
                    continue
                if sfile.endswith('.conf') or sfile in self.target_backup:
                    check.append(sfile)

            if check:
                content = misc.archive_content(self.target_tarball, check)
                counter = 0
                for sfile in check:
                    full_file = os.path.join(ROOT_DIR, sfile)
                    if not misc.file_read(full_file) == content[counter]:
                        message.sub_debug('Backing up', full_file)
                        shutil.copy2(full_file, full_file + '.backup')
                    counter+=1

        message.sub_info('Decompressing tarball')
        misc.archive_decompress(self.target_tarball, ROOT_DIR)

        if target_upgrade:
            message.sub_info('Removing obsolete files and directories')
            adjusted = []
            for sfile in new_content:
                adjusted.append('/' + sfile)
            remove_content = list(set(old_content.split('\n')) - set(adjusted))
            for sfile in remove_content:
                # the footprint and metadata files will be deleted otherwise,
                # also make sure we respect ROOT_DIR different than /
                if LOCAL_DIR in sfile:
                    continue
                # never delete files in the pseudo filesystems
                elif sfile.startswith(('/dev/', '/sys/', '/proc/')):
                    continue

                # files moved from symlink directory to the real directory
                # will be deleted, e.g. from /lib64 to /lib where /lib64 is
                # symlink to /lib. To prevent this skip these files
                sdir = os.path.join(ROOT_DIR, os.path.dirname(sfile))
                if os.path.islink(sdir) and os.path.isdir(os.path.realpath(sdir)):
                    continue

                self.remove_target_file(sfile)
            for sfile in reversed(remove_content):
                self.remove_target_dir(os.path.dirname(sfile))
            for sfile in reversed(remove_content):
                self.remove_target_link(sfile)

            if misc.file_search('\npost_upgrade()', self.srcbuild, escape=False) \
                and SCRIPTS:
                message.sub_info('Executing post_upgrade()')
                misc.system_script(self.srcbuild, 'post_upgrade')
        elif misc.file_search('\npost_install()', self.srcbuild, escape=False) \
            and SCRIPTS:
            message.sub_info('Executing post_install()')
            misc.system_script(self.srcbuild, 'post_install')

        self.update_databases(new_content, 'merge')

        if target_upgrade:
            self.rebuild = []
            message.sub_info('Checking reverse dependencies')
            needs_rebuild = database.local_rdepends(self.target_name)

            if needs_rebuild and self.do_reverse:
                for target in needs_rebuild:
                    break_free = False
                    if target in self.rebuild:
                        continue
                    message.sub_debug('Checking', target)
                    footprint = database.local_footprint(target)
                    for sfile in footprint.split():
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
                message.sub_warning('Targets may need rebuild', needs_rebuild)

    def remove(self):
        ''' Remove target files from system '''
        if not database.local_installed(self.target_name):
            message.sub_critical('Already removed', self.target_name)
            sys.exit(2)

        message.sub_info('Checking dependencies')
        depends_detected = database.local_rdepends(self.target_name, indirect=True)
        # on autoremove ignore reverse dependencies asuming they have been
        # processed already and passed to the class initializer in proper order
        # by the initial checker with indirect reverse dependencies on
        if depends_detected and self.do_reverse and not self.autoremove:
            message.sub_info('Removing reverse dependencies', depends_detected)
            self.autosource(depends_detected, autoremove=True)
            message.sub_info('Resuming %s removing at' % \
                os.path.basename(self.target), datetime.today())
        elif depends_detected and not self.autoremove:
            message.sub_critical('Other targets depend on %s' % \
                self.target_name, depends_detected)
            sys.exit(2)

        if misc.file_search('\npre_remove()', self.srcbuild, escape=False) \
            and SCRIPTS:
            message.sub_info('Executing pre_remove()')
            misc.system_script(self.srcbuild, 'pre_remove')

        footprint = os.path.join(ROOT_DIR, self.target_footprint)
        if os.path.isfile(footprint):
            message.sub_info('Indexing content')
            target_content = misc.file_readlines(footprint)

            message.sub_info('Removing files')
            for sfile in target_content:
                self.remove_target_file(sfile)

            message.sub_info('Removing directories')
            for sfile in reversed(target_content):
                self.remove_target_dir(os.path.dirname(sfile))

            message.sub_info('Removing links')
            for sfile in reversed(target_content):
                self.remove_target_link(sfile)

        if database.local_installed(self.target_name):
            message.sub_info('Removing footprint and metadata')
            misc.dir_remove(os.path.join(LOCAL_DIR, self.target_name))

        if misc.file_search('\npost_remove()', self.srcbuild, escape=False) \
            and SCRIPTS:
            message.sub_info('Executing post_remove()')
            misc.system_script(self.srcbuild, 'post_remove')

        self.update_databases(target_content, 'remove')

    def main(self):
        ''' Execute action for every target '''
        for target in self.targets:
            # make sure target is absolute path
            if os.path.isdir(target):
                target = os.path.abspath(target)

            target_name = os.path.basename(target)
            if target_name in IGNORE:
                message.sub_warning('Ignoring target', target_name)
                continue

            if not database.remote_search(target):
                message.sub_critical('Invalid target', target)
                sys.exit(2)

            # set target properties
            self.target = target
            self.target_name = os.path.basename(target)
            self.target_dir = database.remote_search(target)
            self.srcbuild = os.path.join(self.target_dir, 'SRCBUILD')
            self.source_dir = os.path.join(BUILD_DIR, self.target_name, 'source')
            self.install_dir = os.path.join(BUILD_DIR, self.target_name, 'install')
            self.target_version = database.remote_metadata(self.target_dir, 'version')
            self.target_description = database.remote_metadata(self.target_dir, 'description')
            self.target_depends = database.remote_metadata(self.target_dir, 'depends')
            self.target_makedepends = database.remote_metadata(self.target_dir, 'makedepends')
            self.target_sources = database.remote_metadata(self.target_dir, 'sources')
            self.target_options = database.remote_metadata(self.target_dir, 'options')
            self.target_backup = database.remote_metadata(self.target_dir, 'backup')
            self.target_footprint = os.path.join('var/local/spm', self.target_name, 'footprint')
            self.target_metadata = os.path.join('var/local/spm', self.target_name, 'metadata')
            self.sources_dir = os.path.join(CACHE_DIR, 'sources', self.target_name)
            self.target_tarball = os.path.join(CACHE_DIR, 'tarballs', \
            self.target_name + '_' + self.target_version + '.tar.bz2')

            if database.local_uptodate(self.target) and self.do_update:
                message.sub_warning('Target is up-to-date', self.target)
                continue

            for option in self.target_options:
                if option == 'mirror' and not self.mirror:
                    message.sub_warning('Overriding MIRROR to', 'True')
                    self.mirror = True
                elif option == '!mirror' and self.mirror:
                    message.sub_warning('Overriding MIRROR to', 'False')
                    self.mirror = False

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

                if option == 'rpath' and not self.strip_rpath:
                    message.sub_warning('Overriding STRIP_RPATH to', 'True')
                    self.strip_rpath = True
                elif option == '!rpath' and self.strip_rpath:
                    message.sub_warning('Overriding STRIP_RPATH to', 'False')
                    self.strip_rpath = False

                if option == 'man' and not self.compress_man:
                    message.sub_warning('Overriding COMPRESS_MAN to', 'True')
                    self.compress_man = True
                elif option == '!man' and self.compress_man:
                    message.sub_warning('Overriding COMPRESS_MAN to', 'False')
                    self.compress_man = False

                if option == 'missing' and not self.ignore_missing:
                    message.sub_warning('Overriding IGNORE_MISSING to', 'True')
                    self.ignore_missing = True
                elif option == '!missing' and self.ignore_missing:
                    message.sub_warning('Overriding IGNORE_MISSING to', 'False')
                    self.ignore_missing = False

                if option == 'pycompile' and not self.python_compile:
                    message.sub_warning('Overriding PYTHON_COMPILE to', 'True')
                    self.python_compile = True
                elif option == '!pycompile' and self.python_compile:
                    message.sub_warning('Overriding PYTHON_COMPILE to', 'False')
                    self.python_compile = False

            if self.do_clean:
                message.sub_info('Starting %s cleanup at' % \
                    self.target_name, datetime.today())
                self.clean()

            if self.do_prepare:
                message.sub_info('Starting %s preparations at' % \
                    self.target_name, datetime.today())
                self.prepare()

            if self.do_compile:
                if not misc.file_search('\nsrc_compile()', \
                    self.srcbuild, escape=False):
                    message.sub_warning('src_compile() not defined')
                else:
                    message.sub_info('Starting %s compile at' % \
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
                    message.sub_warning('src_check() not defined')
                else:
                    message.sub_info('Starting %s check at' % \
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
                    message.sub_critical('src_install() not defined')
                    sys.exit(2)

                message.sub_info('Starting %s install at' % \
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
                message.sub_info('Starting %s merge at' % self.target_name, datetime.today())
                self.merge()

            if self.do_remove or self.autoremove:
                message.sub_info('Starting %s remove at' % self.target_name, datetime.today())
                self.remove()

            # reset values so that overrides apply only to single target
            self.mirror = MIRROR
            self.strip_binaries = STRIP_BINARIES
            self.strip_shared = STRIP_SHARED
            self.strip_static = STRIP_STATIC
            self.strip_rpath = STRIP_RPATH
            self.python_compile = PYTHON_COMPILE
            self.compress_man = COMPRESS_MAN
            self.ignore_missing = IGNORE_MISSING


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
        message.sub_info('Checking dependencies')
        missing_dependencies = database.remote_mdepends(self.target)

        if missing_dependencies and self.do_depends:
            message.sub_info('Fetching dependencies', missing_dependencies)
            self.autobinary(missing_dependencies, automake=True)
            message.sub_info('Resuming %s preparations at' % \
                os.path.basename(self.target), datetime.today())
        elif missing_dependencies:
            message.sub_warning('Dependencies missing', missing_dependencies)

        message.sub_info('Preparing tarballs')
        src_base = self.target_name + '_' + self.target_version + '.tar.bz2'
        local_file = self.target_tarball
        internet = misc.ping()

        if not internet:
            message.sub_warning('Internet connection is down')
        else:
            src_url = None
            for mirror in MIRRORS:
                url = mirror + '/tarballs/' + os.uname()[4] + '/' + src_base
                message.sub_debug('Checking mirror', mirror)
                if misc.ping(url):
                    src_url = url
                    break

        if os.path.isfile(local_file) and internet and src_url:
            message.sub_debug('Checking', local_file)
            if misc.fetch_check(src_url, local_file):
                message.sub_debug('Already fetched', src_url)
            else:
                message.sub_warning('Re-fetching', src_url)
                misc.fetch(src_url, local_file)
        elif internet and src_url:
            message.sub_debug('Fetching', src_url)
            misc.fetch(src_url, local_file)

    def main(self):
        ''' Execute action for every target '''
        for target in self.targets:
            # make sure target is absolute path
            if os.path.isdir(target):
                target = os.path.abspath(target)

            target_name = os.path.basename(target)
            if target_name in IGNORE:
                message.sub_warning('Ignoring target', target_name)
                continue

            if not database.remote_search(target):
                message.sub_critical('Invalid target', target)
                sys.exit(2)

            # set target properties
            self.target = target
            self.target_name = os.path.basename(target)
            self.target_dir = database.remote_search(target)
            self.srcbuild = os.path.join(self.target_dir, 'SRCBUILD')
            self.source_dir = os.path.join(BUILD_DIR, self.target_name, 'source')
            self.install_dir = os.path.join(BUILD_DIR, self.target_name, 'install')
            self.target_version = database.remote_metadata(self.target_dir, 'version')
            self.target_description = database.remote_metadata(self.target_dir, 'description')
            self.target_depends = database.remote_metadata(self.target_dir, 'depends')
            self.target_makedepends = database.remote_metadata(self.target_dir, 'makedepends')
            self.target_sources = database.remote_metadata(self.target_dir, 'sources')
            self.target_options = database.remote_metadata(self.target_dir, 'options')
            self.target_backup = database.remote_metadata(self.target_dir, 'backup')
            self.target_footprint = os.path.join('var/local/spm', self.target_name, 'footprint')
            self.target_metadata = os.path.join('var/local/spm', self.target_name, 'metadata')
            self.sources_dir = os.path.join(CACHE_DIR, 'sources', self.target_name)
            self.target_tarball = os.path.join(CACHE_DIR, 'tarballs', \
            self.target_name + '_' + self.target_version + '.tar.bz2')

            if database.local_uptodate(self.target) and self.do_update:
                message.sub_warning('Target is up-to-date', self.target)
                continue

            if self.do_merge:
                message.sub_info('Starting %s preparations at' % \
                    self.target_name, datetime.today())
                self.prepare()
                message.sub_info('Starting %s merge at' % self.target_name, datetime.today())
                self.merge()

            if self.do_remove or self.autoremove:
                message.sub_info('Starting %s remove at' % self.target_name, datetime.today())
                self.remove()


class Who(object):
    ''' Class for printing file owner '''
    def __init__(self, pattern, plain=False):
        self.pattern = pattern
        self.plain = plain
        misc.OFFLINE = OFFLINE
        misc.TIMEOUT = TIMEOUT
        misc.ROOT_DIR = ROOT_DIR
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
                message.sub_info('Match in', target)
