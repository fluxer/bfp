#!/bin/python2

import sys
import os
import tarfile
import zipfile
import gzip
import shutil
import re
import ConfigParser
import compileall
from datetime import datetime

import libmessage
message = libmessage.Message()
import libmisc
misc = libmisc.Misc()
import libpackage
database = libpackage.Database()

MAIN_CONF = '/etc/spm.conf'
REPOSITORIES_CONF = '/etc/spm/repositories.conf'
MIRRORS_CONF = '/etc/spm/mirrors.conf'

if not os.path.isfile(MAIN_CONF):
    message.warning('Configuration file does not exist', MAIN_CONF)

    CACHE_DIR = '/var/cache/spm'
    BUILD_DIR = '/var/tmp/spm'
    ROOT_DIR = '/'
    LOCAL_DIR = ROOT_DIR + 'var/local/spm'
    OFFLINE = False
    MIRROR = False
    TIMEOUT = 30
    EXTERNAL = False
    IGNORE = []
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
    IGNORE = conf.get('spm', 'IGNORE').split(' ')
    OFFLINE = conf.getboolean('prepare', 'OFFLINE')
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
    PYTHON_COMPILE = conf.getboolean('install', 'PYTHON_COMPILE')
    IGNORE_MISSING = conf.getboolean('install', 'IGNORE_MISSING')
    CONFLICTS = conf.getboolean('merge', 'CONFLICTS')
    BACKUP = conf.getboolean('merge', 'BACKUP')
    SCRIPTS = conf.getboolean('merge', 'SCRIPTS')
    TRIGGERS = conf.getboolean('merge', 'TRIGGERS')

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

misc.OFFLINE = OFFLINE
misc.TIMEOUT = TIMEOUT
misc.EXTERNAL = EXTERNAL
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
        misc.EXTERNAL = EXTERNAL
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

                if self.do_version and self.plain:
                    print(database.local_metadata(target, 'version'))
                elif self.do_version:
                    message.sub_info('Version', database.local_metadata(target, 'version'))

                if self.do_description and self.plain:
                    print(database.local_metadata(target, 'description'))
                elif self.do_description:
                    message.sub_info('Description', database.local_metadata(target, 'description'))

                if self.do_depends and self.plain:
                    print(misc.string_convert(database.local_metadata(target, 'depends')))
                elif self.do_depends:
                    message.sub_info('Depends', database.local_metadata(target, 'depends'))

                if self.do_reverse and self.plain:
                    print(misc.string_convert(database.local_rdepends(target)))
                elif self.do_reverse:
                    message.sub_info('Reverse depends', database.local_rdepends(target))

                if self.do_size and self.plain:
                    print(database.local_metadata(target, 'size'))
                elif self.do_size:
                    message.sub_info('Size', database.local_metadata(target, 'size'))

                if self.do_footprint and self.plain:
                    print(database.local_footprint(target))
                elif self.do_footprint:
                    message.sub_info('Footprint', database.local_footprint(target))


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
        misc.EXTERNAL = EXTERNAL
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

                if self.do_version and self.plain:
                    print(database.remote_metadata(target, 'version'))
                elif self.do_version:
                    message.sub_info('Version', database.remote_metadata(target, 'version'))

                if self.do_description and self.plain:
                    print(database.remote_metadata(target, 'description'))
                elif self.do_description:
                    message.sub_info('Description', database.remote_metadata(target, 'description'))

                if self.do_depends and self.plain:
                    print(misc.string_convert(database.remote_metadata(target, 'depends')))
                elif self.do_depends:
                    message.sub_info('Depends', database.remote_metadata(target, 'depends'))

                if self.do_makedepends and self.plain:
                    print(misc.string_convert(database.remote_metadata(target, 'makedepends')))
                elif self.do_makedepends:
                    message.sub_info('Make depends', database.remote_metadata(target, 'makedepends'))

                if self.do_checkdepends and self.plain:
                    print(misc.string_convert(database.remote_metadata(target, 'checkdepends')))
                elif self.do_checkdepends:
                    message.sub_info('Check depends', database.remote_metadata(target, 'checkdepends'))

                if self.do_sources and self.plain:
                    print(misc.string_convert(database.remote_metadata(target, 'sources')))
                elif self.do_sources:
                    message.sub_info('Sources', database.remote_metadata(target, 'sources'))

                if self.do_options and self.plain:
                    print(misc.string_convert(database.remote_metadata(target, 'options')))
                elif self.do_options:
                    message.sub_info('Options', database.remote_metadata(target, 'options'))

                if self.do_backup and self.plain:
                    print(misc.string_convert(database.remote_metadata(target, 'backup')))
                elif self.do_backup:
                    message.sub_info('Backup', database.remote_metadata(target, 'backup'))


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
        misc.EXTERNAL = EXTERNAL
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
        misc.dir_create(rdir)

        if os.path.exists(self.repository_url):
            # repository is local path, create a copy of it
            message.sub_info('Cloning local', self.repository_name)
            shutil.copytree(self.repository_url, self.repository_dir)
        elif os.path.isdir(self.repository_dir):
            # existing Git repository
            message.sub_info('Updating repository', self.repository_name)
            misc.system_command((misc.whereis('git'), 'pull', '--depth=1', \
                self.repository_url), cwd=self.repository_dir)
        else:
            # non-existing Git repository, fetch
            message.sub_info('Cloning remote', self.repository_name)
            misc.system_command((misc.whereis('git'), 'clone', '--depth=1', \
                self.repository_url, self.repository_dir))

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
            local_version = database.local_metadata(target, 'version')
            remote_version = database.remote_metadata(target, 'version')

            if misc.version(local_version) < misc.version(remote_version):
                message.sub_warning('New version of %s available' % target, remote_version)

    def main(self):
        ''' Execute action for every repository '''
        for repository in self.repositories_urls:
            # compute only once by asigning class variables, in cases when
            # clean and sync is done this is more optimal but triggers
            # http://pylint-messages.wikidot.com/messages:w0201
            self.repository_url = repository
            self.repository_name = os.path.basename(self.repository_url)
            self.repository_dir = os.path.join(CACHE_DIR, 'repositories', self.repository_name)

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
        do_remove=False, do_depends=False, do_reverse=False, do_update=False):
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
        self.autoremove = False
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
        misc.EXTERNAL = EXTERNAL
        database.ROOT_DIR = ROOT_DIR
        database.CACHE_DIR = CACHE_DIR
        database.LOCAL_DIR = LOCAL_DIR
        database.IGNORE = IGNORE

    def set_global(self, target):
        ''' Set target properties, used to reset all of them '''
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

    def update_databases(self, content):
        ''' Update common databases '''
        if not TRIGGERS:
            return

        run_ldconfig = True
        run_mandb = True
        run_desktop_database = True
        run_mime_database = True
        run_icon_resource = True
        run_gio_querymodules = True
        run_pango_querymodules = True
        run_gtk2_immodules = True
        run_gtk3_immodules = True
        run_pixbuf_query = True
        run_install_info = True
        run_compile_schemas = True
        run_depmod = True
        run_icon_cache = True
        for sfile in sorted(content):
            sfile = '/' + sfile
            if sfile.endswith('.so') and os.path.isfile(os.path.join(ROOT_DIR, 'etc/ld.so.conf')) \
                and run_ldconfig:
                message.sub_info('Updating shared libraries cache')
                message.sub_debug(sfile)
                misc.system_command((misc.whereis('ldconfig'), '-r', ROOT_DIR))
                run_ldconfig = False
            elif '/share/man' in sfile and misc.whereis('mandb', fallback=False) \
                and run_mandb:
                if os.path.isdir(sfile):
                    continue
                message.sub_info('Updating manual pages database')
                message.sub_debug(sfile)
                misc.system_command(('mandb', '--quiet'))
                run_mandb = False
            elif '/share/applications/' in sfile \
                and misc.whereis('update-desktop-database', fallback=False) \
                and run_desktop_database:
                message.sub_info('Updating desktop database')
                message.sub_debug(sfile)
                misc.system_command(('update-desktop-database', os.path.dirname(sfile)))
                run_desktop_database = False
            elif '/share/mime/' in sfile and misc.whereis('update-mime-database', \
                fallback=False) and run_mime_database:
                message.sub_info('Updating mime database')
                message.sub_debug(sfile)
                misc.system_command(('update-mime-database', sys.prefix + 'share/mime'))
                run_mime_database = False
            elif '/share/icons/' in sfile and misc.whereis('xdg-icon-resource', \
                fallback=False) and run_icon_resource:
                message.sub_info('Updating icon resources')
                message.sub_debug(sfile)
                misc.system_command(('xdg-icon-resource', 'forceupdate', '--theme', 'hicolor'))
                run_icon_resource = False
            elif '/gio/modules/' in sfile and misc.whereis('gio-querymodules', \
                fallback=False) and run_gio_querymodules:
                message.sub_info('Updating GIO modules cache')
                sdir = os.path.dirname(sfile)
                message.sub_debug(sdir)
                misc.system_command(('gio-querymodules', sdir))
                run_gio_querymodules = False
            elif '/pango/' in sfile and '/modules/' in sfile \
                and misc.whereis('pango-querymodules', fallback=False) \
                and run_pango_querymodules:
                message.sub_info('Updating pango modules cache')
                message.sub_debug(sfile)
                misc.system_command(('pango-querymodules', '--update-cache'))
                run_pango_querymodules = False
            elif '/gtk-2.0/' in sfile and '/immodules/' in sfile \
                and misc.whereis('gtk-query-immodules-2.0', fallback=False) \
                and run_gtk2_immodules:
                message.sub_info('Updating GTK-2.0 imodules cache')
                message.sub_debug(sfile)
                misc.file_write('/etc/gtk-2.0/gtk.immodules', \
                    misc.system_output('gtk-query-immodules-2.0'))
                run_gtk2_immodules = False
            elif '/gtk-3.0/' in sfile and '/immodules/' in sfile \
                and misc.whereis('gtk-query-immodules-3.0', fallback=False) \
                and run_gtk3_immodules:
                message.sub_info('Updating GTK-3.0 imodules cache')
                message.sub_debug(sfile)
                misc.file_write('/etc/gtk-3.0/gtk.immodules', \
                    misc.system_output('gtk-query-immodules-3.0'))
                run_gtk3_immodules = False
            elif '/gdk-pixbuf' in sfile and '/loaders/' in sfile \
                and misc.whereis('gdk-pixbuf-query-loaders', fallback=False) \
                and run_pixbuf_query:
                message.sub_info('Updating gdk pixbuffer loaders')
                message.sub_debug(sfile)
                misc.file_write('/etc/gtk-2.0/gdk-pixbuf.loaders', \
                    misc.system_output('gdk-pixbuf-query-loaders'))
                run_pixbuf_query = False
            elif '/schemas/' in sfile and misc.whereis('glib-compile-schemas', \
                fallback=False) and run_compile_schemas:
                message.sub_info('Updating GSettings schemas')
                # gconfpkg --uninstall network-manager-applet
                message.sub_debug(sfile)
                misc.system_command(('glib-compile-schemas', os.path.dirname(sfile)))
                run_compile_schemas = False
            elif sfile.endswith('.ko') and misc.whereis('depmod', \
                fallback=False) and run_depmod:
                message.sub_info('Updating module dependencies')
                message.sub_debug(sfile)
                misc.system_command(('depmod'))
                run_depmod = False
            # upon target remove sfile may not exist thus some triggers fail
            elif not os.path.isfile(sfile):
                continue
            elif '/share/info' in sfile and misc.whereis('install-info', \
                fallback=False) and run_install_info:
                # install-info --delete $infodir/$file.gz $infodir/dir
                message.sub_info('Updating info pages')
                sdir = os.path.dirname(sfile)
                message.sub_debug(sdir)
                for sfile in misc.list_files(sdir):
                    misc.system_command(('install-info', sfile, os.path.join(sdir, 'dir')))
                run_install_info = False
            elif '/share/icons/' in sfile and misc.whereis('gtk-update-icon-cache', \
                fallback=False) and run_icon_cache:
                # extract the proper directory from sfile, e.g. /usr/share/icons/hicolor
                sdir = misc.string_search('(/(?:.*?)?/share/icons/(?:.*?))', sfile, escape=False)
                sdir = misc.string_convert(sdir)
                if not os.path.isfile(os.path.join(sdir, 'index.theme')):
                    continue
                message.sub_info('Updating icons cache')
                message.sub_debug(sdir)
                misc.system_command(('gtk-update-icon-cache', '-q', '-t', '-i', '-f', sdir))
                run_icon_cache = False

    def remove_target_file(self, sfile):
        ''' Remove target file '''
        sfull = (os.path.join(ROOT_DIR + sfile))
        if os.path.isfile(sfull):
            message.sub_debug('Removing', sfull)
            os.unlink(sfull)

    def remove_target_dir(self, sdir):
        ''' Remove target directory '''
        sfull = (os.path.join(ROOT_DIR + sdir))
        if os.path.isdir(sfull) and not os.listdir(sfull):
            message.sub_debug('Removing', sfull)
            if os.path.islink(sfull):
                os.unlink(sfull)
            else:
                os.rmdir(sfull)

    def clean(self):
        ''' Clean target files '''
        self.set_global(self.target)

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
            self.original_target = self.target
            self.main(missing_dependencies, automake=True)
            message.sub_info('Resuming %s preparations at' % \
                os.path.basename(self.original_target), datetime.today())
            self.set_global(self.original_target)
        elif missing_dependencies:
            message.sub_warning('Dependencies missing', missing_dependencies)

        if not os.path.isdir(self.source_dir):
            os.makedirs(self.source_dir)
        if not os.path.isdir(self.sources_dir):
            os.makedirs(self.sources_dir)

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
                        '--depth=1', src_url), cwd=link_file)
                else:
                    message.sub_debug('Cloning initial copy', src_url)
                    misc.system_command((misc.whereis('git'), 'clone', \
                        '--depth=1', src_url, link_file))
                continue

            elif src_url.startswith(('http://', 'https://', 'ftp://', \
                'ftps://')):
                if not internet:
                    message.sub_warning('Internet connection is down')
                elif self.mirror:
                    for mirror in MIRRORS:
                        url = mirror + '/' + src_base
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

            if src_base.endswith(('.xz', '.lzma')) \
                or tarfile.is_tarfile(link_file) or zipfile.is_zipfile(link_file):
                decompressed = False
                for sfile in misc.archive_list(link_file):
                    if not os.path.exists(os.path.join(self.source_dir, sfile)):
                        message.sub_debug('Extracting', link_file)
                        misc.archive_decompress(link_file, self.source_dir)
                        decompressed = True
                        break
                if not decompressed:
                    message.sub_debug('Already extracted', link_file)

    def compile(self):
        ''' Compile target sources '''
        self.set_global(self.target)

        misc.system_command((misc.whereis('bash'), '-e', '-c', 'source ' + \
            self.srcbuild + ' && umask 0022 && src_compile'), cwd=self.source_dir)

    def check(self):
        ''' Check target sources '''
        self.set_global(self.target)

        misc.system_command((misc.whereis('bash'), '-e', '-c', 'source ' + \
            self.srcbuild + ' && umask 0022 && src_check'), cwd=self.source_dir)

    def install(self):
        ''' Install targets files '''
        self.set_global(self.target)

        if not os.path.isdir(self.install_dir):
            os.makedirs(self.install_dir)

        misc.system_command((misc.whereis('bash'), '-e', '-c', 'source ' + \
            self.srcbuild + ' && umask 0022 && src_install'), cwd=self.source_dir)

        if COMPRESS_MAN:
            message.sub_info('Compressing manual pages')
            manpath = misc.whereis('manpath', fallback=False)
            # if manpath (provided by man-db) is not present fallback to something sane
            if not manpath:
                mpaths = ('/usr/local/share/man', '/usr/share/man', '/usr/man')
            else:
                mpaths = misc.system_output((manpath, '--global')).split(':')

            for sdir in mpaths:
                for sfile in misc.list_files(self.install_dir + sdir):
                    if not sfile.endswith('.gz') and os.path.isfile(sfile):
                        message.sub_debug('Compressing', sfile)
                        # using gzip instead of tarfile as tarfiles sets wrong header
                        f_in = open(sfile, 'rb')
                        f_out = gzip.open(sfile + '.gz', 'wb')
                        f_out.writelines(f_in)
                        f_out.close()
                        f_in.close()
                        os.unlink(sfile)
                    elif os.path.islink(sfile) and not os.path.isfile(os.path.realpath(sfile)):
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
            # skip footprint and metadata, they are listed when re-installing
            if sfile == os.path.join(self.install_dir, self.target_footprint) \
                or sfile == os.path.join(self.install_dir, self.target_metadata):
                continue
            elif sfile.endswith('/.packlist') or sfile.endswith('/perllocal.pod') \
                or sfile.endswith('/share/info/dir'):
                os.unlink(sfile)
                continue
            target_content[sfile] = misc.file_mime(sfile)

        if self.strip_binaries or self.strip_shared or self.strip_static or self.strip_rpath:
            message.sub_info('Stripping binaries and libraries')
            strip = misc.whereis('strip')
            scanelf = misc.whereis('scanelf')
            for sfile, smime in target_content.iteritems():
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

                if (smime == 'application/x-executable' or smime == 'application/x-sharedlib' \
                    or smime == 'application/x-archive') and self.strip_rpath:
                    # we do not check if RPATH is present at all to reduce spawning scanelf twice
                    message.sub_debug('Stripping RPATH', sfile)
                    misc.system_command((scanelf, '-CBXrq', sfile))

        if self.python_compile:
            # FIXME: this blindly assumes that .py files are not placed in /bin, /sbin, etc.
            message.sub_info('Byte-compiling Python files')
            for sfile in target_content.keys():
                if not sfile.endswith('.py'):
                    continue
                message.sub_debug('Compiling Python file', sfile)
                compileall.compile_file(sfile, force=True, quiet=True)

        message.sub_info('Checking runtime dependencies')
        missing_detected = False
        for sfile, smime in target_content.iteritems():
            if os.path.islink(sfile):
                continue

            if smime == 'application/x-executable' or smime == 'application/x-sharedlib':
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

                    if match == self.target_name or misc.string_search(lib, target_content.keys()):
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
                for bang in ('sh', 'bash', 'dash', 'ksh', 'csh', 'tcsh', \
                    'tclsh', 'scsh', 'fish', 'zsh', 'ash', 'python', \
                    'python2', 'python3', 'perl', 'php', 'ruby', 'lua', \
                    'wish', 'awk' 'gawk'):
                    bang_regexp = '^#!(/usr)?/(s)?bin/(env )?' + bang + '(\\s|$)'
                    file_regexp = '(/usr)?/(s)?bin/' + bang
                    self_file_regexp = self.install_dir + '(/usr)?/(s)?bin/' + bang

                    if misc.file_search(bang_regexp, sfile, exact=False, escape=False):
                        match = database.local_belongs(file_regexp, exact=True, escape=False)
                        if match and len(match) > 1:
                            message.sub_warning('Multiple providers for %s' % bang, match)
                            if self.target_name in match:
                                match = self.target_name
                            else:
                                match = match[0]
                        match = misc.string_convert(match)

                        if match == self.target_name or misc.string_search(self_file_regexp, \
                            target_content.keys(), exact=True, escape=False):
                            message.sub_debug('Dependency needed but in self', match)
                        elif match and match in self.target_depends:
                            message.sub_debug('Dependency needed but in depends', match)
                        elif match and not match in self.target_depends:
                            message.sub_debug('Dependency needed but in local', match)
                            self.target_depends.append(match)
                        elif self.ignore_missing:
                            message.sub_warning('Dependency needed, not in any local', bang)
                        else:
                            message.sub_critical('Dependency needed, not in any local', bang)
                            missing_detected = True
        if missing_detected:
            sys.exit(2)

        message.sub_info('Assembling metadata')
        if not os.path.isdir(os.path.join(self.install_dir, 'var/local/spm', self.target_name)):
            os.makedirs(os.path.join(self.install_dir, 'var/local/spm', self.target_name))
        metadata = open(os.path.join(self.install_dir, self.target_metadata), 'w')
        metadata.write('version=' + self.target_version + '\n')
        metadata.write('description=' + self.target_description + '\n')
        metadata.write('depends=' + misc.string_convert(self.target_depends) + '\n')
        metadata.write('size=' + str(misc.dir_size(self.install_dir)) + '\n')
        metadata.close()

        message.sub_info('Assembling footprint')
        misc.file_write(os.path.join(self.install_dir, self.target_footprint), \
            '\n'.join(sorted(target_content.keys())).replace(self.install_dir, ''))

        message.sub_info('Compressing tarball')
        if not os.path.isdir(os.path.join(CACHE_DIR, 'tarballs')):
            os.makedirs(os.path.join(CACHE_DIR, 'tarballs'))
        misc.archive_compress(self.install_dir, self.target_tarball)

    def merge(self):
        ''' Merget target to system '''
        self.set_global(self.target)

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

        # store state installed or not, always true if done later on
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
            for sfile in new_content:
                full_file = os.path.join(ROOT_DIR, sfile)
                if not os.path.isfile(full_file):
                    continue
                if sfile.endswith('.conf') or sfile in self.target_backup:
                    if os.path.getsize(full_file) == misc.archive_size(self.target_tarball, sfile):
                        continue

                    message.sub_debug('Backing up', full_file)
                    shutil.copy2(full_file, full_file + '.backup')

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


            if misc.file_search('\npost_upgrade()', self.srcbuild, escape=False) \
                and SCRIPTS:
                message.sub_info('Executing post_upgrade()')
                misc.system_script(self.srcbuild, 'post_upgrade')
        elif misc.file_search('\npost_install()', self.srcbuild, escape=False) \
            and SCRIPTS:
            message.sub_info('Executing post_install()')
            misc.system_script(self.srcbuild, 'post_install')

        self.update_databases(new_content)

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
                        if smime == 'application/x-executable' or smime == 'application/x-sharedlib':
                            libraries = misc.system_scanelf(sfile)
                            if not libraries:
                                continue # static binary
                            for lib in libraries.split(','):
                                if not database.local_belongs(lib):
                                    self.main(target.split(), automake=True)
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
        depends_detected = database.local_rdepends(self.target_name)
        if depends_detected and self.do_reverse:
            message.sub_info('Removing reverse dependencies', depends_detected)
            self.autoremove = True
            self.original_target = self.target
            self.main(depends_detected)
            message.sub_info('Resuming %s removing at' % \
                os.path.basename(self.original_target), datetime.today())
            self.set_global(self.original_target)
        elif depends_detected:
            message.sub_critical('Other targets depend on %s' % \
                self.target_name, depends_detected)
            sys.exit(2)

        if misc.file_search('\npre_remove()', self.srcbuild, escape=False) and SCRIPTS:
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

        if database.local_installed(self.target_name):
            message.sub_info('Removing footprint and metadata')
            misc.dir_remove(os.path.join(LOCAL_DIR, self.target_name))

        if misc.file_search('\npost_remove()', self.srcbuild, escape=False) \
            and SCRIPTS:
            message.sub_info('Executing post_remove()')
            misc.system_script(self.srcbuild, 'post_remove')

        if os.path.isfile(footprint):
            self.update_databases(target_content)

    def main(self, targets=None, automake=False):
        ''' Execute action for every target '''
        if not targets:
            targets = self.targets

        for target in targets:
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

            self.set_global(target)

            if database.local_uptodate(self.target) and self.do_update and not automake:
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

            if self.do_clean or automake:
                message.sub_info('Starting %s cleanup at' % self.target_name, datetime.today())
                self.clean()

            if self.do_prepare or automake:
                message.sub_info('Starting %s preparations at' % self.target_name, datetime.today())
                self.prepare()

            if self.do_compile or automake:
                if not misc.file_search('\nsrc_compile()', self.srcbuild, escape=False):
                    message.sub_warning('src_compile() not defined')
                else:
                    message.sub_info('Starting %s compile at' % self.target_name, datetime.today())
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
                if not misc.file_search('\nsrc_check()', self.srcbuild, escape=False):
                    message.sub_warning('src_check() not defined')
                else:
                    message.sub_info('Starting %s check at' % self.target_name, datetime.today())
                    os.putenv('SOURCE_DIR', self.source_dir)
                    os.putenv('INSTALL_DIR', self.install_dir)
                    os.putenv('CHOST', CHOST)
                    os.putenv('CFLAGS', CFLAGS)
                    os.putenv('CXXFLAGS', CXXFLAGS)
                    os.putenv('CPPFLAGS', CPPFLAGS)
                    os.putenv('LDFLAGS', LDFLAGS)
                    os.putenv('MAKEFLAGS', MAKEFLAGS)
                    self.check()

            if self.do_install or automake:
                if not misc.file_search('\nsrc_install()', self.srcbuild, escape=False):
                    message.sub_critical('src_install() not defined')
                    sys.exit(2)

                message.sub_info('Starting %s install at' % self.target_name, datetime.today())
                os.putenv('SOURCE_DIR', self.source_dir)
                os.putenv('INSTALL_DIR', self.install_dir)
                os.putenv('CHOST', CHOST)
                os.putenv('CFLAGS', CFLAGS)
                os.putenv('CXXFLAGS', CXXFLAGS)
                os.putenv('CPPFLAGS', CPPFLAGS)
                os.putenv('LDFLAGS', LDFLAGS)
                os.putenv('MAKEFLAGS', MAKEFLAGS)
                self.install()

            if self.do_merge or automake:
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


class Who(object):
    ''' Class for printing file owner '''
    def __init__(self, pattern, plain=False):
        self.pattern = pattern
        self.plain = plain
        misc.OFFLINE = OFFLINE
        misc.TIMEOUT = TIMEOUT
        misc.EXTERNAL = EXTERNAL
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
