#!/bin/python2

import gettext
_ = gettext.translation('spm', fallback=True).gettext

import sys
import argparse
import subprocess
import tarfile
import zipfile
import shutil
import os
import re
import difflib
import pwd, grp
import SimpleHTTPServer, SocketServer
if sys.version < '3':
    import ConfigParser as configparser
    from urllib2 import HTTPError
    from urllib2 import urlopen
else:
    import configparser
    from urllib.error import HTTPError
    from urllib.request import urlopen

import libmessage
message = libmessage.Message()
import libmisc
misc = libmisc.Misc()
import libpackage
database = libpackage.Database()
import libspm


app_version = "1.6.1 (a1de806)"

class Check(object):
    ''' Check runtime dependencies of local targets '''
    def __init__(self, targets, do_fast=False, do_depends=False, \
        do_reverse=False, do_adjust=False):
        self.targets = targets
        self.do_fast = do_fast
        self.do_depends = do_depends
        self.do_reverse = do_reverse
        self.do_adjust = do_adjust
        self.check_targets = []

        for target in database.local_all(basename=True):
            if target in self.targets:
                if self.do_reverse:
                    self.check_targets.extend(database.local_rdepends(target))
                elif self.do_depends:
                    self.check_targets.extend(database.local_metadata(target, 'depends'))
                else:
                    self.check_targets.append(target)

    def main(self):
        ''' Check if runtime dependencies of target are satisfied '''
        for target in self.check_targets:
            message.sub_info(_('Checking'), target)
            target_metadata = os.path.join(libspm.LOCAL_DIR, target, 'metadata')
            target_footprint = database.local_metadata(target, 'footprint')
            target_depends = database.local_metadata(target, 'depends')
            target_adepends = []

            missing_detected = False
            required = []
            for sfile in target_footprint.splitlines():
                sfile = os.path.join(libspm.ROOT_DIR, sfile)
                if os.path.islink(sfile):
                    continue
                elif not os.path.isfile(sfile):
                    continue
                elif self.do_fast:
                    if '/include/' in sfile or '/share/man' in sfile \
                        or '/share/locale/' in sfile or '/share/i18n/' in sfile \
                        or '/share/info/' in sfile:
                        message.sub_debug(_('Skipping'), sfile)
                        continue

                message.sub_debug(_('Path'), sfile)
                smime = misc.file_mime(sfile)
                if smime == 'application/x-executable' or smime == 'application/x-sharedlib':
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
                    bang_regexp = '^#!(?:(?: )+)?(?:/.*)+(?:(?: )+)?'
                    bang_regexp += '(?:sh|bash|dash|ksh|csh|tcsh|tclsh|scsh|fish'
                    bang_regexp += '|zsh|ash|python|perl|php|ruby|lua|wish|(?:g)?awk)'
                    bang_regexp += '(?:(?:\\d(?:.)?)+)?(?:\\s|$)'
                    fmatch = misc.file_search(bang_regexp, sfile, exact=False, escape=False)
                    if fmatch:
                        fmatch = fmatch[0].replace('#!', '').strip().split()[0]
                        required.append(fmatch)

            checked = []
            for lib in required:
                if lib in checked:
                    continue
                slib = os.path.realpath(lib)
                match = database.local_belongs('(?:^|\\s)%s(?:$|\\s)' % re.escape(slib), escape=False)
                if match and len(match) > 1:
                    message.sub_warning(_('Multiple providers for %s') % slib, match)
                    if target in match:
                        match = target
                    else:
                        match = match[0]
                match = misc.string_convert(match)
                if not match in target_adepends and not match == target:
                    target_adepends.append(match)

                if match == target or slib in target_footprint.splitlines():
                    message.sub_debug(_('Dependency needed but in target'), match)
                elif match and match in target_depends:
                    message.sub_debug(_('Dependency needed but in dependencies'), match)
                elif match and not match in target_depends:
                    message.sub_debug(_('Dependency needed but in local'), match)
                    target_depends.append(match)
                elif libspm.IGNORE_MISSING:
                    message.sub_warning(_('Dependency needed, not in any local'), slib)
                else:
                    message.sub_critical(_('Dependency needed, not in any local'), slib)
                    missing_detected = True
                checked.append(lib)
            if missing_detected:
                sys.exit(2)

            for a in target_depends:
                if not a in target_adepends:
                    message.sub_warning(_('Unnecessary explicit dependencies'), a)

            if self.do_adjust:
                message.sub_debug(_('Adjusting target dependencies'))
                content = misc.file_read(target_metadata)
                for line in misc.file_readlines(target_metadata):
                    if line.startswith('depends='):
                        content = content.replace(line, \
                            'depends=%s' % misc.string_convert(target_depends))
                misc.file_write(target_metadata, content)


class Clean(object):
    ''' Check for targets that are not required by other '''
    def __init__(self):
        # don't bother for targets in the base group
        self.base_targets = database.remote_alias('base')

    def main(self):
        ''' Looks for target match and then execute action for every target '''
        for target in database.local_all(basename=True):
            if target in self.base_targets:
                continue

            if not database.local_rdepends(target):
                message.sub_warning(_('Unneded target'), target)


class Dist(object):
    ''' Distribute ports '''
    def __init__(self, targets, do_sources=False, do_clean=False, \
        directory=misc.dir_current()):
        self.targets = targets
        self.do_sources = do_sources
        self.do_clean = do_clean
        self.directory = directory

    def main(self):
        ''' Looks for target match and then execute action for every target '''
        for target in self.targets:
            target_directory = database.remote_search(target)
            if not target_directory:
                message.sub_critical(_('Invalid target'), target)
                sys.exit(2)
            # in case target is a directory ending with a slash basename gets
            # confused so normalize the path before first
            target_basename = os.path.basename(os.path.normpath(target))

            target_version = database.remote_metadata(target, 'version')
            target_distfile = os.path.join(self.directory, \
                target_basename + '_' + target_version + '.tar.bz2')
            target_sources = database.remote_metadata(target, 'sources')

            if self.do_sources:
                message.sub_info(_('Preparing sources'))
                for src_url in target_sources:
                    src_base = os.path.basename(src_url)
                    src_file = os.path.join(target_directory, src_base)
                    internet = misc.ping()

                    if src_url.startswith('git://') or src_url.endswith('.git'):
                        if not internet:
                            message.sub_warning(_('Internet connection is down'))
                        elif os.path.isdir(src_file):
                            message.sub_debug(_('Updating Git repository'), src_url)
                            misc.system_command((misc.whereis('git'), \
                                'pull', src_url), cwd=src_file)
                        else:
                            git = misc.whereis('git')
                            message.sub_debug(_('Cloning Git repository'), src_url)
                            misc.system_command((git, 'clone', '--depth=1', \
                                src_url, src_file))
                            message.sub_debug(_('Setting up user information for repository'))
                            # allow gracefull pulls and merges
                            misc.system_command((git, 'config', 'user.name', \
                                'spm'), cwd=src_file)
                            misc.system_command((git, 'config', 'user.email', \
                                'spm@unnatended.fake'), cwd=src_file)
                        continue

                    elif src_url.startswith(('http://', 'https://', 'ftp://', \
                        'ftps://')):
                        if not internet:
                            message.sub_warning(_('Internet connection is down'))
                        elif libspm.MIRROR:
                            for mirror in libspm.MIRRORS:
                                url = mirror + '/' + src_base
                                message.sub_debug(_('Checking mirror'), mirror)
                                if misc.ping(url):
                                    src_url = url
                                    break

                        if os.path.isfile(src_file) and internet:
                            message.sub_debug(_('Checking'), src_file)
                            if misc.fetch_check(src_url, src_file):
                                message.sub_debug(_('Already fetched'), src_url)
                            else:
                                message.sub_warning(_('Re-fetching'), src_url)
                                misc.fetch(src_url, src_file)
                        elif internet:
                            message.sub_debug(_('Fetching'), src_url)
                            misc.fetch(src_url, src_file)

            message.sub_info(_('Compressing'), target_distfile)
            misc.archive_compress((target_directory,), target_distfile, target_directory)

            if self.do_clean:
                message.sub_info(_('Purging sources'))
                for src_url in target_sources:
                    src_base = os.path.basename(src_url)

                    src_file = os.path.join(target_directory, src_base)
                    if src_url.startswith(('http://', 'https://', 'ftp://', \
                        'ftps://')):
                        if os.path.isfile(src_file):
                            message.sub_debug(_('Removing'), src_file)
                            os.unlink(src_file)
                    elif src_url.startswith('git://') or src_url.endswith('.git'):
                        if os.path.isdir(src_file):
                            message.sub_debug(_('Removing'), src_file)
                            misc.dir_remove(src_file)


class Lint(object):
    ''' Check sanity of local targets '''
    def __init__(self, targets, man=False, udev=False, symlink=False, \
        doc=False, module=False, footprint=False, builddir=False, \
        ownership=False, executable=False, path=False, shebang=False, \
        backup=False, conflicts=False, debug=False):
        self.targets = targets
        self.man = man
        self.udev = udev
        self.symlink = symlink
        self.doc = doc
        self.module = module
        self.footprint = footprint
        self.builddir = builddir
        self.ownership = ownership
        self.executable = executable
        self.path = path
        self.shebang = shebang
        self.backup = backup
        self.conflicts = conflicts
        self.debug = debug

    def main(self):
        ''' Looks for target match and then execute action for every target '''
        for target in database.local_all(basename=True):
            if target in self.targets:
                message.sub_info(_('Checking'), target)
                target_footprint = database.local_metadata(target, 'footprint')

                if self.man:
                    if not misc.string_search('/share/man/', target_footprint):
                        message.sub_warning(_('No manual page(s)'))

                if self.udev:
                    if misc.string_search('(\\s|^)/lib/udev/rules.d/', \
                        target_footprint, escape=False) \
                        and misc.string_search('(\\s|^)/usr/(s)?bin/', \
                        target_footprint, escape=False):
                        message.sub_warning(_('Cross-filesystem udev rule(s)'))

                if self.symlink:
                    for sfile in target_footprint.splitlines():
                        if os.path.exists(sfile) and os.path.islink(sfile):
                            if not sfile.startswith('/usr/') \
                                and os.path.realpath(sfile).startswith('/usr/'):
                                message.sub_warning(_('Cross-filesystem symlink'), sfile)
                            elif not sfile.startswith('/var/') \
                                and os.path.realpath(sfile).startswith('/var/'):
                                message.sub_warning(_('Cross-filesystem symlink'), sfile)
                            elif not sfile.startswith('/boot/') \
                                and os.path.realpath(sfile).startswith('/boot/'):
                                message.sub_warning(_('Cross-filesystem symlink'), sfile)

                if self.doc:
                    if misc.string_search('/doc/|/gtk-doc', target_footprint, escape=False):
                        message.sub_warning(_('Documentation provided'))

                if self.module:
                    for sfile in target_footprint.splitlines():
                        # FIXME: compressed modules
                        if sfile.endswith('.ko') and not os.path.dirname(sfile).endswith('/misc'):
                            message.sub_warning(_('Extra module(s) in non-standard directory'))

                if self.footprint:
                    if not target_footprint:
                        message.sub_warning(_('Empty footprint'))
                    for sfile in target_footprint.splitlines():
                        if not os.path.exists(sfile):
                            message.sub_warning(_('File does not exist'), sfile)

                if self.builddir:
                    for sfile in target_footprint.splitlines():
                        if os.path.islink(sfile):
                            continue
                        elif not os.path.exists(sfile):
                            message.sub_debug(_('File does not exist'), sfile)
                            continue

                        if misc.file_search(libspm.BUILD_DIR, sfile):
                            message.sub_warning(_('Build directory trace(s)'), sfile)

                if self.ownership:
                    for sfile in target_footprint.splitlines():
                        if os.path.islink(sfile):
                            continue
                        elif not os.path.exists(sfile):
                            message.sub_debug(_('File does not exist'), sfile)
                            continue

                        stat = os.stat(sfile)
                        unkown = False
                        try:
                            pwd.getpwuid(stat.st_uid)
                        except KeyError:
                            unkown = True
                        try:
                            grp.getgrgid(stat.st_gid)
                        except KeyError:
                            unkown = True
                        if unkown:
                            message.sub_warning(_('Unknown owner of'), sfile)

                if self.executable:
                    # FIXME: false positives
                    for sfile in target_footprint.splitlines():
                        if not os.path.exists(sfile):
                            message.sub_debug(_('File does not exist'), sfile)
                            continue
                        if os.path.islink(sfile):
                            continue

                        if sfile.startswith(('/bin', '/sbin', '/usr/bin', '/usr/sbin')) \
                            and not os.access(sfile, os.X_OK):
                            message.sub_warning(_('File in PATH is not executable'), sfile)

                if self.path:
                    for sfile in target_footprint.splitlines():
                        if not os.path.exists(sfile):
                            message.sub_debug(_('File does not exist'), sfile)
                            continue

                        if sfile.startswith(('/bin', '/sbin', '/usr/bin', '/usr/sbin')):
                            for spath in ('/bin', '/sbin', '/usr/bin', '/usr/sbin'):
                                xfile = spath + '/' + os.path.basename(sfile)
                                if sfile == xfile or not os.path.exists(xfile):
                                    continue
                                regex = '(/usr)?/(s)?bin/' + re.escape(os.path.basename(sfile)) + '(\\s|$)'
                                match = database.local_belongs(regex, escape=False)
                                if len(match) > 1:
                                    message.sub_warning(_('File in PATH overlaps with'), match)

                if self.shebang:
                    for sfile in target_footprint.splitlines():
                        if os.path.islink(sfile):
                            continue
                        elif not os.path.exists(sfile):
                            message.sub_debug(_('File does not exist'), sfile)
                            continue
                        smime = misc.file_mime(sfile)
                        if smime == 'text/plain' or smime == 'text/x-shellscript' \
                            or smime == 'text/x-python' or smime == 'text/x-perl' \
                            or smime == 'text/x-php' or smime == 'text/x-ruby' \
                            or smime == 'text/x-lua' or smime == 'text/x-tcl' \
                            or smime == 'text/x-awk' or smime == 'text/x-gawk':
                            # https://en.wikipedia.org/wiki/Comparison_of_command_shells
                            bang_regexp = '^#!(?:(?: )+)?(?:/.*)+(?:(?: )+)?'
                            bang_regexp += '(?:sh|bash|dash|ksh|csh|tcsh|tclsh|scsh|fish'
                            bang_regexp += '|zsh|ash|python|perl|php|ruby|lua|wish|(?:g)?awk)'
                            bang_regexp += '(?:(?:\\d(?:.)?)+)?(?:\\s|$)'
                            match = misc.file_search(bang_regexp, sfile, exact=False, escape=False)
                            if match:
                                match = match[0].replace('#!', '').strip().split()[0]
                                if not database.local_belongs(match, exact=True, escape=False):
                                    message.sub_warning(_('Invalid shebang'), sfile)

                if self.backup:
                    for sfile in target_footprint.splitlines():
                        backups = database.remote_metadata(target, 'backup')
                        if not os.path.exists(sfile) and sfile.lstrip('/') in backups:
                            message.sub_warning(_('Possibly unnecessary backup of file'), sfile)
                        elif sfile.endswith('.conf') and not sfile.lstrip('/') in backups:
                            message.sub_warning(_('Possibly undefined backup of file'), sfile)

                if self.conflicts:
                    for sfile in target_footprint.splitlines():
                        for local in database.local_all(basename=True):
                            if local == target:
                                continue
                            if sfile.lstrip('/') in database.local_metadata(local, 'footprint').splitlines():
                                message.sub_warning(_('Possibly conflicting file with %s') % local, sfile)

                if self.debug:
                    found_debug = 'lib/debug/' in target_footprint
                    found_exe = False
                    if not found_debug:
                        for sfile in target_footprint.splitlines():
                            if not os.path.exists(sfile):
                                message.sub_debug(_('File does not exist'), sfile)
                                continue
                            smime = misc.file_mime(sfile)
                            if smime == 'application/x-executable' \
                                or smime == 'application/x-sharedlib' \
                                or smime == 'application/x-archive':
                                found_exe = True
                                break
                    if not found_debug and found_exe:
                        message.sub_warning(_('Debug symbols missing'))


class Sane(object):
    ''' Check sanity of SRCBUILDs '''
    def __init__(self, targets, enable=False, disable=False, null=False, \
        maintainer=False, note=False, variables=False, triggers=False, \
        users=False, groups=False):
        self.targets = targets
        self.enable = enable
        self.disable = disable
        self.null = null
        self.maintainer = maintainer
        self.note = note
        self.variables = variables
        self.triggers = triggers
        self.users = users
        self.groups = groups

    def main(self):
        ''' Looks for target match and then execute action for every target '''
        for target in self.targets:
            match = database.remote_search(target)
            if match:
                message.sub_info(_('Checking'), target)
                target_srcbuild = os.path.join(match, 'SRCBUILD')

                if self.enable:
                    if misc.file_search('--enable-', target_srcbuild):
                        message.sub_warning(_('Explicit --enable argument(s)'))
                    if misc.file_search('--with-', target_srcbuild):
                        message.sub_warning(_('Explicit --with argument(s)'))

                if self.disable:
                    if misc.file_search('--disable-', target_srcbuild):
                        message.sub_warning(_('Explicit --disable argument(s)'))
                    if misc.file_search('--without-', target_srcbuild):
                        message.sub_warning(_('Explicit --without argument(s)'))

                if self.null:
                    if misc.file_search('/dev/null', target_srcbuild):
                        message.sub_warning(_('Possible /dev/null output redirection'))

                if self.maintainer:
                    if not misc.file_search('(\\s|^)# [mM]aintainer:', target_srcbuild, escape=False):
                        message.sub_warning(_('No maintainer mentioned'))

                if self.note:
                    if misc.file_search('(FIXME|TODO)', target_srcbuild, escape=False):
                        message.sub_warning(_('FIXME/TODO note(s)'))

                if self.variables:
                    content = misc.file_read(target_srcbuild)
                    if not 'version=' in content or not 'description=' in content:
                        message.sub_warning(_('Essential variable(s) missing'))
                    if 'version=(' in content or 'description=(' in content:
                        message.sub_warning(_('String variable(s) defined as array'))
                    # TODO: check for arrays defined as strings

                if self.triggers:
                    regex = '(?:\\s|^)(ldconfig|mandb|update-desktop-database'
                    regex += '|update-mime-database|xdg-icon-resource|depmod'
                    regex += '|gio-querymodules|pango-querymodules|install-info'
                    regex += '|gtk-query-immodules-2.0|gtk-query-immodules-3.0'
                    regex += '|gdk-pixbuf-query-loaders|glib-compile-schemas'
                    regex += '|gtk-update-icon-cache|mkinitfs|grub-mkconfig'
                    regex += '|update-grub)(?:\\s|$)'
                    if misc.file_search(regex, target_srcbuild, escape=False):
                        message.sub_warning(_('Possible unnecessary triggers invocation(s)'))

                if self.users:
                    if misc.file_search('useradd|adduser', target_srcbuild, escape=False) \
                        and not misc.file_search('userdel|deluser', target_srcbuild, escape=False):
                        message.sub_warning(_('User(s) added but not deleted'))

                if self.groups:
                    if misc.file_search('groupadd|addgroup', target_srcbuild, escape=False) \
                        and not misc.file_search('groupdel|delgroup', target_srcbuild, escape=False):
                        message.sub_warning(_('Group(s) added but not deleted'))


class Merge(object):
    ''' Merge backup files '''
    def __init__(self):
        self.targets = database.local_all(basename=True)

    def merge(self, sfile):
        message.sub_warning(_('Backup file detected'), sfile + '.backup')
        editor = os.environ.get('EDITOR')
        if not editor:
            editor = misc.whereis('vim')
        action = raw_input(_('''
    What do you want to do:

        1. View difference
        2. Edit original
        3. Edit backup
        4. Replace original with backup
        5. Remove backup
        *. Continue
'''))
        if action == '1':
            print('\n' + '*' * 80)
            for line in list(difflib.Differ().compare( \
                misc.file_readlines(sfile + '.backup'), \
                misc.file_readlines(sfile))):
                print(line)
            print('*' * 80 + '\n')
            self.merge(sfile)
        elif action == '2':
            misc.system_command((editor, sfile))
            self.merge(sfile)
        elif action == '3':
            misc.system_command((editor, sfile + '.backup'))
            self.merge(sfile)
        elif action == '4':
            shutil.copy2(sfile + '.backup', sfile)
        elif action == '5':
            os.unlink(sfile + '.backup')

    def main(self):
        for target in self.targets:
            message.sub_info(_('Checking'), target)
            backups = database.remote_metadata(target, 'backup')
            if not backups:
                backups = []
            for sfile in database.local_metadata(target, 'footprint').splitlines():
                if sfile.endswith('.conf'):
                    backups.append(os.path.join(libspm.ROOT_DIR, sfile))

            for sfile in backups:
                original_file = os.path.join(libspm.ROOT_DIR, sfile)

                if os.path.isfile(original_file + '.backup'):
                    self.merge(original_file)


class Edit(object):
    ''' Edit SRCBUILDs from repository via EDITOR (fallbacks to vim) '''
    def __init__(self, targets):
        self.targets = targets

    def main(self):
        editor = os.environ.get('EDITOR')
        if not editor:
            editor = misc.whereis('vim')
        for target in self.targets:
            match = database.remote_search(target)
            if match:
                misc.system_command((editor, os.path.join(match, 'SRCBUILD')))


class Which(object):
    ''' Print full path to SRCBUILD of target(s) '''
    def __init__(self, pattern, cat=False, plain=False):
        self.pattern = pattern
        self.cat = cat
        self.plain = plain

    def main(self):
        for target in database.remote_all(basename=False):
            if re.search(self.pattern, target):
                if self.plain:
                    print(target)
                else:
                    message.sub_info(_('Match'), target)
                if self.cat:
                    print(misc.file_read(target + '/SRCBUILD'))


class Pack(object):
    ''' Pack local (installed) target files into tarball '''
    def __init__(self, targets, directory=misc.dir_current()):
        self.targets = targets
        self.directory = directory

    def main(self):
        for target in self.targets:
            if database.local_search(target):
                target_version = database.remote_metadata(target, 'version')
                target_packfile = os.path.join(self.directory, \
                    os.path.basename(target) + '_' + target_version + '.tar.bz2')

                content = database.local_metadata(target, 'footprint').splitlines()
                # add metadata directory, it is not listed in the footprint
                content.append(os.path.join(libspm.LOCAL_DIR, target))

                message.sub_info(_('Compressing'), target_packfile)
                misc.archive_compress(content, target_packfile, '/')


class Pkg(object):
    ''' Fetch Arch Linux package files '''
    def __init__(self, targets, directory=misc.dir_current()):
        self.targets = targets
        self.directory = directory
        self.GIT_DIRS = (
            '/svntogit/packages.git/plain/%s/trunk',
            '/svntogit/community.git/plain/%s/trunk'
        )
        self.GIT_URL = 'http://projects.archlinux.org'


    def get_git_links(self, pkgname):
        """Search the Git interface on archlinux.org."""
        for d in self.GIT_DIRS:
            url = self.GIT_URL + d % pkgname
            try:
                f = urlopen(url)
                for line in f:
                    m = re.search(r"href='(.+?)'>(.+?)<".encode('utf-8'), line)
                    if m:
                        href = m.group(1).decode()
                        name = m.group(2).decode()
                        if name[:2] != '..':
                            yield self.GIT_URL + href, name
                f.close()
                return
            except HTTPError as e:
                if e.code != 404:
                    raise

    def main(self):
        not_found = []
        for target in self.targets:
            urls = list(self.get_git_links(target))
            if urls:
                message.sub_info(_('Fetching package files'), target)
                message.sub_debug(_('Webpage'), os.path.dirname(urls[0][0]))
                pkgdir = os.path.join(self.directory, target)
                misc.dir_create(pkgdir)
                for href, name in urls:
                    message.sub_debug(_('Fetching'), href)
                    misc.fetch(href, os.path.join(pkgdir, name))
            else:
                not_found.append(target)

        if not_found:
            for target in not_found:
                message.sub_critical(_('Invalid target'), target)
            sys.exit(2)


class Serve(object):
    ''' Serve cache directories with local network parties '''
    def __init__(self, port, address):
        self.port = port
        self.address = address

    def main(self):
        httpd = None
        try:
            message.sub_info(_('Serving caches directory'))
            os.chdir(libspm.CACHE_DIR)
            handler = SimpleHTTPServer.SimpleHTTPRequestHandler
            httpd = SocketServer.TCPServer((self.address, self.port), handler)
            httpd.serve_forever()
        finally:
            if httpd:
                httpd.shutdown()


class Disowned(object):
    ''' Print all files on the system not owned by a target '''
    def __init__(self, directory='/', cross=False, plain=False):
        self.directory = directory
        self.cross = cross
        self.plain = plain

    def main(self):
        if not self.plain:
            message.sub_info(_('Caching host files, this may take a while'))
        lhostfiles = misc.list_files(self.directory, self.cross)
        if not self.plain:
            message.sub_info(_('Searching for disowned files'))
        for sfile in lhostfiles:
            if not database.local_belongs(sfile, True):
                if self.plain:
                    print(sfile)
                else:
                    message.sub_info(_('Disowned file'), sfile)


try:
    EUID = os.geteuid()

    class OverrideDebug(argparse.Action):
        ''' Override printing of debug messages '''
        def __call__(self, parser, namespace, values, option_string=None):
            message.DEBUG = True
            setattr(namespace, self.dest, values)

    parser = argparse.ArgumentParser(prog='spm-tools', \
        description='Source Package Manager Tools', \
        epilog=_('NOTE: Some features are available only to the root user.'))
    subparsers = parser.add_subparsers(dest='mode')

    if EUID == 0:
        dist_parser = subparsers.add_parser('dist')
        dist_parser.add_argument('-s', '--sources', action='store_true', \
            help=_('Include all sources in the archive'))
        dist_parser.add_argument('-c', '--clean', action='store_true', \
            help=_('Clean all sources after creating archive'))
        dist_parser.add_argument('-d', '--directory', type=str, \
            default=misc.dir_current(), help=_('Set output directory'))
        dist_parser.add_argument('TARGETS', nargs='+', type=str, \
            help=_('Targets to apply actions on'))

    check_parser = subparsers.add_parser('check')
    check_parser.add_argument('-f', '--fast', action='store_true', \
        help=_('Skip some files/links'))
    check_parser.add_argument('-a', '--adjust', action='store_true', \
        help=_('Adjust target depends'))
    check_parser.add_argument('-D', '--depends', action='store_true', \
        help=_('Check dependencies of target'))
    check_parser.add_argument('-R', '--reverse', action='store_true', \
        help=_('Check reverse dependencies of target'))
    check_parser.add_argument('TARGETS', nargs='+', type=str, \
        help=_('Targets to apply actions on'))

    clean_parser = subparsers.add_parser('clean')

    lint_parser = subparsers.add_parser('lint')
    lint_parser.add_argument('-m', '--man', action='store_true', \
        help=_('Check for missing manual page(s)'))
    lint_parser.add_argument('-u', '--udev', action='store_true', \
        help=_('Check for cross-filesystem udev rule(s)'))
    lint_parser.add_argument('-s', '--symlink', action='store_true', \
        help=_('Check for cross-filesystem symlink(s)'))
    lint_parser.add_argument('-d', '--doc', action='store_true', \
        help=_('Check for documentation'))
    lint_parser.add_argument('-M', '--module', action='store_true', \
        help=_('Check for module(s) in non-standard directory'))
    lint_parser.add_argument('-f', '--footprint', action='store_true', \
        help=_('Check for footprint consistency'))
    lint_parser.add_argument('-b', '--builddir', action='store_true', \
        help=_('Check for build directory trace(s)'))
    lint_parser.add_argument('-o', '--ownership', action='store_true', \
        help=_('Check ownership'))
    lint_parser.add_argument('-e', '--executable', action='store_true', \
        help=_('Check for non-executable(s) in PATH'))
    lint_parser.add_argument('-p', '--path', action='store_true', \
        help=_('Check for overlapping executable(s) in PATH'))
    lint_parser.add_argument('-n', '--shebang', action='store_true', \
        help=_('Check for incorrect shebang of scripts'))
    lint_parser.add_argument('-k', '--backup', action='store_true', \
        help=_('Check for incorrect or incomplete backup of files'))
    lint_parser.add_argument('-c', '--conflicts', action='store_true', \
        help=_('Check for conflicts between targets'))
    lint_parser.add_argument('-D', '--debug', action='store_true', \
        help=_('Check for missing debug symbols'))
    lint_parser.add_argument('-a', '--all', action='store_true', \
        help=_('Perform all checks'))
    lint_parser.add_argument('TARGETS', nargs='+', type=str, \
        help=_('Targets to apply actions on'))

    sane_parser = subparsers.add_parser('sane')
    sane_parser.add_argument('-e', '--enable', action='store_true', \
        help=_('Check for explicit --enable argument(s)'))
    sane_parser.add_argument('-d', '--disable', action='store_true', \
        help=_('Check for explicit --disable argument(s)'))
    sane_parser.add_argument('-n', '--null', action='store_true', \
        help=_('Check for /dev/null output redirection(s)'))
    sane_parser.add_argument('-m', '--maintainer', action='store_true', \
        help=_('Check for missing maintainer'))
    sane_parser.add_argument('-N', '--note', action='store_true', \
        help=_('Check for FIXME/TODO note(s)'))
    sane_parser.add_argument('-v', '--variables', action='store_true', \
        help=_('Check for essential variables'))
    sane_parser.add_argument('-t', '--triggers', action='store_true', \
        help=_('Check for unnecessary triggers invocation(s)'))
    sane_parser.add_argument('-u', '--users', action='store_true', \
        help=_('Check for user(s) being added but not deleted'))
    sane_parser.add_argument('-g', '--groups', action='store_true', \
        help=_('Check for group(s) being added but not deleted'))
    sane_parser.add_argument('-a', '--all', action='store_true', \
        help=_('Perform all checks'))
    sane_parser.add_argument('TARGETS', nargs='+', type=str, \
        help=_('Targets to apply actions on'))

    if EUID == 0:
        merge_parser = subparsers.add_parser('merge')

    if EUID == 0:
        edit_parser = subparsers.add_parser('edit')
        edit_parser.add_argument('TARGETS', nargs='+', type=str, \
            help=_('Targets to apply actions on'))

    which_parser = subparsers.add_parser('which')
    which_parser.add_argument('-c', '--cat', action='store_true', \
        help=_('Display content of SRCBUILD'))
    which_parser.add_argument('-p', '--plain', action='store_true', \
        help=_('Print in plain format'))
    which_parser.add_argument('PATTERN', type=str, \
        help=_('Pattern to search for in remote targets'))

    pack_parser = subparsers.add_parser('pack')
    pack_parser.add_argument('-d', '--directory', type=str, \
        default=misc.dir_current(), help=_('Set output directory'))
    pack_parser.add_argument('TARGETS', nargs='+', type=str, \
        help=_('Targets to apply actions on'))

    pkg_parser = subparsers.add_parser('pkg')
    pkg_parser.add_argument('-d', '--directory', type=str, \
        default=misc.dir_current(), help=_('Set output directory'))
    pkg_parser.add_argument('TARGETS', nargs='+', type=str, \
        help=_('Targets to apply actions on'))

    serve_parser = subparsers.add_parser('serve')
    serve_parser.add_argument('-p', '--port', action='store', \
        type=int, default=8000, help=_('Use port for the server'))
    serve_parser.add_argument('-a', '--address', action='store', \
        type=str, default='', help=_('Use address for the server'))

    disowned_parser = subparsers.add_parser('disowned')
    disowned_parser.add_argument('-d', '--directory', type=str, \
        default='/', help=_('Set lookup directory'))
    disowned_parser.add_argument('-c', '--cross', action='store_true', \
        help=_('Scan cross-filesystem'))
    disowned_parser.add_argument('-p', '--plain', action='store_true', \
        help=_('Print in plain format'))

    parser.add_argument('--debug', nargs=0, action=OverrideDebug, \
        help=_('Enable debug messages'))
    parser.add_argument('--version', action='version', \
        version='Source Package Manager Tools v%s' % app_version, \
        help=_('Show SPM Tools version and exit'))

    ARGS = parser.parse_args()

    if ARGS.mode == 'dist':
        if 'world' in ARGS.TARGETS:
            position = ARGS.TARGETS.index('world')
            ARGS.TARGETS[position:position+1] = \
                database.local_all(basename=True)

        for alias in database.remote_aliases():
            if alias in ARGS.TARGETS:
                position = ARGS.TARGETS.index(alias)
                ARGS.TARGETS[position:position+1] = \
                    database.remote_alias(alias)

        message.info(_('Runtime information'))
        message.sub_info(_('SOURCES'), ARGS.sources)
        message.sub_info(_('CLEAN'), ARGS.clean)
        message.sub_info(_('DIRECTORY'), ARGS.directory)
        message.sub_info(_('TARGETS'), ARGS.TARGETS)
        message.info(_('Poking remotes...'))
        m = Dist(ARGS.TARGETS, ARGS.sources, ARGS.clean, ARGS.directory)
        m.main()

    elif ARGS.mode == 'check':
        message.info(_('Runtime information'))
        message.sub_info(_('FAST'), ARGS.fast)
        message.sub_info(_('DEPENDS'), ARGS.depends)
        message.sub_info(_('REVERSE'), ARGS.reverse)
        message.sub_info(_('ADJUST'), ARGS.adjust)
        message.sub_info(_('TARGETS'), ARGS.TARGETS)
        message.info(_('Poking locals...'))
        m = Check(ARGS.TARGETS, ARGS.fast, ARGS.depends, ARGS.reverse, \
            ARGS.adjust)
        m.main()

    elif ARGS.mode == 'clean':
        message.info(_('Poking locals...'))
        m = Clean()
        m.main()

    elif ARGS.mode == 'lint':
        if ARGS.all:
            ARGS.man = True
            ARGS.udev = True
            ARGS.symlink = True
            ARGS.doc = True
            ARGS.module = True
            ARGS.footprint = True
            ARGS.builddir = True
            ARGS.ownership = True
            ARGS.executable = True
            ARGS.path = True
            ARGS.shebang = True
            ARGS.backup = True
            ARGS.conflicts = True
            ARGS.debug = True

        message.info(_('Runtime information'))
        message.sub_info(_('MAN'), ARGS.man)
        message.sub_info(_('UDEV'), ARGS.udev)
        message.sub_info(_('SYMLINK'), ARGS.symlink)
        message.sub_info(_('DOC'), ARGS.doc)
        message.sub_info(_('MODULE'), ARGS.module)
        message.sub_info(_('FOOTPRINT'), ARGS.footprint)
        message.sub_info(_('BUILDDIR'), ARGS.builddir)
        message.sub_info(_('OWNERSHIP'), ARGS.ownership)
        message.sub_info(_('EXECUTABLE'), ARGS.executable)
        message.sub_info(_('PATH'), ARGS.path)
        message.sub_info(_('SHEBANG'), ARGS.shebang)
        message.sub_info(_('BACKUP'), ARGS.backup)
        message.sub_info(_('CONFLICTS'), ARGS.conflicts)
        message.sub_info(_('DEBUG'), ARGS.debug)
        message.sub_info(_('TARGETS'), ARGS.TARGETS)
        message.info(_('Poking locals...'))

        m = Lint(ARGS.TARGETS, ARGS.man, ARGS.udev, ARGS.symlink, ARGS.doc, \
            ARGS.module, ARGS.footprint, ARGS.builddir, ARGS.ownership, \
            ARGS.executable, ARGS.path, ARGS.shebang, ARGS.backup, \
            ARGS.conflicts, ARGS.debug)
        m.main()

    elif ARGS.mode == 'sane':
        if ARGS.all:
            ARGS.enable = True
            ARGS.disable = True
            ARGS.null = True
            ARGS.maintainer = True
            ARGS.note = True
            ARGS.variables = True
            ARGS.triggers = True
            ARGS.users = True
            ARGS.groups = True

        message.info(_('Runtime information'))
        message.sub_info(_('ENABLE'), ARGS.enable)
        message.sub_info(_('DISABLE'), ARGS.disable)
        message.sub_info(_('NULL'), ARGS.null)
        message.sub_info(_('MAINTAINER'), ARGS.maintainer)
        message.sub_info(_('NOTE'), ARGS.note)
        message.sub_info(_('VARIABLES'), ARGS.variables)
        message.sub_info(_('TRIGGERS'), ARGS.triggers)
        message.sub_info(_('USERS'), ARGS.users)
        message.sub_info(_('GROUPS'), ARGS.groups)
        message.sub_info(_('TARGETS'), ARGS.TARGETS)
        message.info(_('Poking remotes...'))

        m = Sane(ARGS.TARGETS, ARGS.enable, ARGS.disable, ARGS.null, \
            ARGS.maintainer, ARGS.note, ARGS.variables, ARGS.triggers, \
            ARGS.users, ARGS.groups)
        m.main()

    elif ARGS.mode == 'merge':
        message.info(_('Poking locals...'))
        m = Merge()
        m.main()

    elif ARGS.mode == 'edit':
        message.info(_('Runtime information'))
        message.sub_info(_('TARGETS'), ARGS.TARGETS)
        message.info(_('Poking remotes...'))
        m = Edit(ARGS.TARGETS)
        m.main()

    elif ARGS.mode == 'which':
        if not ARGS.plain:
            message.info(_('Runtime information'))
            message.sub_info(_('PATTERN'), ARGS.PATTERN)
        m = Which(ARGS.PATTERN, ARGS.cat, ARGS.plain)
        m.main()

    elif ARGS.mode == 'pack':
        message.info(_('Runtime information'))
        message.sub_info(_('DIRECTORY'), ARGS.directory)
        message.sub_info(_('TARGETS'), ARGS.TARGETS)
        m = Pack(ARGS.TARGETS, ARGS.directory)
        m.main()

    elif ARGS.mode == 'pkg':
        message.info(_('Runtime information'))
        message.sub_info(_('DIRECTORY'), ARGS.directory)
        message.sub_info(_('TARGETS'), ARGS.TARGETS)
        m = Pkg(ARGS.TARGETS, ARGS.directory)
        m.main()

    elif ARGS.mode == 'serve':
        message.info(_('Runtime information'))
        message.sub_info(_('CACHE_DIR'), libspm.CACHE_DIR)
        message.sub_info(_('PORT'), ARGS.port)
        message.sub_info(_('ADDRESS'), ARGS.address)
        m = Serve(ARGS.port, ARGS.address)
        m.main()

    elif ARGS.mode == 'disowned':
        if not ARGS.plain:
            message.info(_('Runtime information'))
            message.sub_info(_('DIRECTORY'), ARGS.directory)
            message.sub_info(_('CROSS'), ARGS.cross)
        m = Disowned(ARGS.directory, ARGS.cross, ARGS.plain)
        m.main()

except configparser.Error as detail:
    message.critical('CONFIGPARSER', detail)
    sys.exit(3)
except subprocess.CalledProcessError as detail:
    message.critical('SUBPROCESS', detail)
    sys.exit(4)
except HTTPError as detail:
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
