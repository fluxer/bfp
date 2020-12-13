#!/usr/bin/python2

# stub for gettext
def _(arg):
    return arg

import sys, argparse, subprocess, tarfile, zipfile, shutil, os, re, difflib
import pwd, grp
if sys.version < '3':
    import ConfigParser as configparser
    from urllib2 import HTTPError
    from urllib2 import URLError
    import SimpleHTTPServer as HTTPServer
    import SocketServer as socketserver
else:
    import configparser
    from urllib.error import HTTPError
    from urllib.error import URLError
    import http.server as HTTPServer
    import socketserver

import libmessage
message = libmessage.Message()
import libspm
misc = libspm.misc
database = libspm.database
misc.GPG_DIR = libspm.GPG_DIR
misc.SHELL = libspm.SHELL

app_version = "1.12.0 (284a667)"

class Check(object):
    ''' Check runtime dependencies of local targets '''
    def __init__(self, targets, do_depends=False, do_reverse=False):
        self.targets = []
        for target in targets:
            self.targets.extend(database.remote_alias(target))
        self.do_depends = do_depends
        self.do_reverse = do_reverse
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
            target_autodepends = database.local_metadata(target, 'autodepends')

            missing_detected = False
            for sfile in target_autodepends:
                # TODO: take different root dir into account
                # sfile = '%s%s' % (libspm.ROOT_DIR, sfile)
                message.sub_debug(_('Path'), sfile)
                if not database.local_belongs(sfile):
                    message.sub_critical(_('Dependency needed, not in any local'), sfile)
                    missing_detected = True
            if missing_detected:
                sys.exit(2)


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
        self.targets = []
        for target in targets:
            self.targets.extend(database.remote_alias(target))
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
            # confused so normalize the path first
            target_basename = os.path.basename(os.path.normpath(target))

            target_version = database.remote_metadata(target, 'version')
            target_distfile = '%s/%s_%s.tar.gz' % (self.directory, \
                target_basename, target_version)
            target_sources = database.remote_metadata(target, 'sources')
            target_pgpkeys = database.remote_metadata(target, 'pgpkeys')

            if self.do_sources:
                message.sub_info(_('Preparing PGP keys'))
                if target_pgpkeys and libspm.VERIFY:
                    misc.gpg_receive(target_pgpkeys, libspm.KEYSERVERS, target)

                message.sub_info(_('Preparing sources'))
                for src_url in target_sources:
                    src_base = misc.url_normalize(src_url, True)
                    src_file = '%s/%s' % (target_directory, src_url)

                    if not os.path.isfile(src_file):
                        message.sub_debug(_('Fetching'), src_url)
                        misc.fetch(src_url, src_file, libspm.MIRRORS, 'distfiles/')

                if libspm.VERIFY:
                    for src_url in target_sources:
                        src_base = misc.url_normalize(src_url, True)
                        src_file = '%s/%s' % (self.directory, src_base)
                        src_signature = misc.gpg_findsig(src_file)
                        if src_signature:
                            message.sub_debug(_('Verifying'), src_url)
                            misc.gpg_verify(src_file, src_signature, target)

            message.sub_info(_('Compressing'), target_distfile)
            misc.archive_compress((target_directory,), target_distfile, \
                target_directory)

            if self.do_clean:
                message.sub_info(_('Purging sources'))
                for src_url in target_sources:
                    src_base = misc.url_normalize(src_url, True)
                    src_file = '%s/%s' % (target_directory, src_base)
                    if misc.url_supported(src_url):
                        if os.path.isfile(src_file):
                            message.sub_debug(_('Removing'), src_file)
                            os.unlink(src_file)
                        elif os.path.isdir(src_file):
                            message.sub_debug(_('Removing'), src_file)
                            misc.dir_remove(src_file)


class Lint(object):
    ''' Check sanity of local targets '''
    def __init__(self, targets, man=False, udev=False, symlink=False, \
        purge=False, module=False, footprint=False, builddir=False, \
        permissions=False, executable=False, path=False, shebang=False, \
        backup=False, conflicts=False):
        self.targets = []
        for target in targets:
            self.targets.extend(database.remote_alias(target))
        self.man = man
        self.udev = udev
        self.symlink = symlink
        self.purge = purge
        self.module = module
        self.footprint = footprint
        self.builddir = builddir
        self.permissions = permissions
        self.executable = executable
        self.path = path
        self.shebang = shebang
        self.backup = backup
        self.conflicts = conflicts

    def _check_ownership(self, spath):
        stat = os.stat(spath)
        try:
            pwd.getpwuid(stat.st_uid)
            grp.getgrgid(stat.st_gid)
        except KeyError:
            message.sub_warning(_('Unknown owner of'), spath)

        # TODO: is there utility to pull those from /etc/login.defs?
        if stat.st_gid >= 1000 or stat.st_uid >= 1000:
            message.sub_warning('Owner of %s is user' % spath, \
                '%d, %d' % (stat.st_gid, stat.st_uid))

        smime = misc.file_mime(spath, bquick=True)
        if (smime in misc.binarymimes or smime == 'application/x-sharedlib') \
            and not os.access(spath, os.X_OK):
            message.sub_warning('Binary/library is not executable', spath)

    def main(self):
        ''' Looks for target match and then execute action for every target '''
        for target in database.local_all(basename=True):
            if target in self.targets:
                message.sub_info(_('Checking'), target)
                target_footprint_lines = []
                target_footprint = ''
                for sfile in database.local_metadata(target, 'footprint'):
                    sfull = '%s/%s' % (libspm.ROOT_DIR, sfile)
                    if not os.path.exists(os.path.realpath(sfull)):
                        message.sub_warning(_('File does not exist'), sfull)
                    else:
                        target_footprint_lines.append(sfull)
                        target_footprint += '%s\n' % sfull

                if self.man:
                    message.sub_debug(_('Checking for missing man pages in'), target)
                    if not '/share/man/' in target_footprint:
                        message.sub_warning(_('No manual page(s)'))

                if self.udev:
                    message.sub_debug(_('Checking udev rules in'), target)
                    if misc.string_search('(\\s|^)/lib/udev/rules.d/', \
                        target_footprint, escape=False) \
                        and misc.string_search('(\\s|^)/usr/(s)?bin/', \
                        target_footprint, escape=False):
                        message.sub_warning(_('Cross-filesystem udev rule(s)'))

                if self.symlink:
                    message.sub_debug(_('Checking symlinks in'), target)
                    for sfile in target_footprint_lines:
                        if os.path.islink(sfile):
                            if not sfile.startswith('/usr/') \
                                and os.path.realpath(sfile).startswith('/usr/'):
                                message.sub_warning(_('Cross-filesystem symlink'), sfile)
                            elif not sfile.startswith('/var/') \
                                and os.path.realpath(sfile).startswith('/var/'):
                                message.sub_warning(_('Cross-filesystem symlink'), sfile)
                            elif not sfile.startswith('/boot/') \
                                and os.path.realpath(sfile).startswith('/boot/'):
                                message.sub_warning(_('Cross-filesystem symlink'), sfile)
                        elif os.stat(sfile).st_nlink == 2:
                            message.sub_warning(_('Hardlink'), sfile)

                if self.purge:
                    message.sub_debug(_('Checking for paths that must be purged in'), target)
                    if misc.string_search(libspm.PURGE_PATHS, target_footprint, escape=False):
                        message.sub_warning(_('Target has paths to be purged'))

                if self.module:
                    message.sub_debug(_('Checking for misplaced modules in'), target)
                    for sfile in target_footprint_lines:
                        if sfile.endswith(('.ko', '.ko.gz', '.ko.bz2', 'ko.xz')) \
                            and not os.path.dirname(sfile).endswith('/misc'):
                            message.sub_warning(_('Extra module(s) in non-standard directory'), sfile)

                if self.footprint:
                    message.sub_debug(_('Checking footprint of'), target)
                    if not target_footprint:
                        message.sub_warning(_('Empty footprint'))

                if self.builddir:
                    message.sub_debug(_('Checking build traces in'), target)
                    for sfile in target_footprint_lines:
                        if os.path.islink(sfile):
                            continue
                        # FIXME: Python 3000
                        if misc.file_search(libspm.BUILD_DIR, sfile):
                            message.sub_warning(_('Build directory trace(s)'), sfile)

                if self.permissions:
                    message.sub_debug(_('Checking permissions in'), target)
                    for sfile in target_footprint_lines:
                        if os.path.islink(sfile):
                            continue
                        self._check_ownership(sfile)
                        self._check_ownership(os.path.dirname(sfile))

                if self.executable:
                    message.sub_debug(_('Checking for non-executables in'), target)
                    # FIXME: false positives if run as non-root
                    for sfile in target_footprint_lines:
                        if os.path.islink(sfile):
                            continue
                        if sfile.startswith(('/bin', '/sbin', '/usr/bin', '/usr/sbin')) \
                            and not os.access(sfile, os.X_OK):
                            message.sub_warning(_('File in PATH is not executable'), sfile)

                if self.path:
                    message.sub_debug(_('Checking for PATH overlapping in'), target)
                    for sfile in target_footprint_lines:
                        if sfile.startswith(('/bin', '/sbin', '/usr/bin', '/usr/sbin')):
                            for spath in ('/bin', '/sbin', '/usr/bin', '/usr/sbin'):
                                xfile = '%s/%s' % (spath, os.path.basename(sfile))
                                if sfile == xfile or not os.path.exists(xfile):
                                    continue
                                regex = '(/usr)?/(s)?bin/' + re.escape(os.path.basename(sfile)) + '(\\s|$)'
                                match = database.local_belongs(regex, escape=False)
                                if len(match) > 1:
                                    message.sub_warning(_('File in PATH overlaps with'), match)

                if self.shebang:
                    message.sub_debug(_('Checking shebangs in'), target)
                    for sfile in target_footprint_lines:
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
                            match = misc.file_search(bang_regexp, sfile, escape=False)
                            if match:
                                match = match[0].replace('#!', '').strip().split()[0]
                                if not database.local_belongs(match, exact=True, escape=False):
                                    message.sub_warning(_('Invalid shebang'), sfile)

                if self.backup:
                    message.sub_debug(_('Checking possible backups in'), target)
                    for sfile in target_footprint_lines:
                        backups = database.remote_metadata(target, 'backup')
                        if not os.path.exists(sfile) and misc.string_lstrip(sfile, '/') in backups:
                            message.sub_warning(_('Possibly unnecessary backup of file'), sfile)
                        # TODO: this cries for improvement, should .ini be checked for?
                        elif sfile.endswith('.cnf') and not misc.string_lstrip(sfile, '/') in backups:
                            message.sub_warning(_('Possibly undefined backup of file'), sfile)

                if self.conflicts:
                    message.sub_debug(_('Checking for conflicts in'), target)
                    for local in database.local_all(basename=True):
                        if local == target:
                            continue
                        footprint = frozenset(database.local_metadata(local, 'footprint'))
                        diff = footprint.difference(target_footprint_lines)
                        if footprint != diff:
                            message.sub_critical(_('File/link conflicts with %s') % local, \
                                list(footprint.difference(diff)))


class Sane(object):
    ''' Check sanity of SRCBUILDs '''
    def __init__(self, targets, enable=False, disable=False, null=False, \
        maintainer=False, note=False, variables=False, triggers=False, \
        users=False, groups=False, signatures=False, pulse=False):
        self.targets = []
        for target in targets:
            self.targets.extend(database.remote_alias(target))
        self.enable = enable
        self.disable = disable
        self.null = null
        self.maintainer = maintainer
        self.note = note
        self.variables = variables
        self.triggers = triggers
        self.users = users
        self.groups = groups
        self.signatures = signatures
        self.pulse = pulse

    def main(self):
        ''' Looks for target match and then execute action for every target '''
        for target in self.targets:
            match = database.remote_search(target)
            if match:
                message.sub_info(_('Checking'), target)
                srcbuild = misc.file_read('%s/SRCBUILD' % match)

                if self.enable:
                    if '--enable-' in srcbuild:
                        message.sub_warning(_('Explicit --enable argument(s)'))
                    if '--with-' in srcbuild:
                        message.sub_warning(_('Explicit --with argument(s)'))

                if self.disable:
                    if '--disable-' in srcbuild:
                        message.sub_warning(_('Explicit --disable argument(s)'))
                    if '--without-' in srcbuild:
                        message.sub_warning(_('Explicit --without argument(s)'))

                if self.null:
                    if '/dev/null' in srcbuild:
                        message.sub_warning(_('Possible /dev/null output redirection'))

                if self.maintainer:
                    if not misc.string_search('(?:\\s|^)# [mM]aintainer:', srcbuild, escape=False):
                        message.sub_warning(_('No maintainer mentioned'))

                if self.note:
                    if misc.string_search('(FIXME|TODO)', srcbuild, escape=False):
                        message.sub_warning(_('FIXME/TODO note(s)'))

                if self.variables:
                    essential_regex = '(?:version|description)'
                    string_regex = '(?:version|release|description)'
                    array_regex = '(?:(?:make|opt|check)?depends|sources|pgpkeys|options|backup)'
                    if not misc.string_search('(?:\\s|^)%s=' % essential_regex, srcbuild, escape=False):
                        message.sub_warning(_('Essential variable(s) missing'))
                    if misc.string_search('(?:\\s|^)%s=\(' % string_regex, srcbuild, escape=False):
                        message.sub_warning(_('String variable(s) defined as array'))
                    if misc.string_search('(?:\\s|^)%s=[^\(]' % array_regex, srcbuild, escape=False):
                        message.sub_warning(_('Array variable(s) defined as string'))

                if self.triggers:
                    regex = '(?:\\s|^)(ldconfig|mandb|update-desktop-database'
                    regex += '|update-mime-database|xdg-icon-resource|depmod'
                    regex += '|gio-querymodules|pango-querymodules|install-info'
                    regex += '|gtk-query-immodules-2.0|gtk-query-immodules-3.0'
                    regex += '|gdk-pixbuf-query-loaders|glib-compile-schemas'
                    regex += '|gtk-update-icon-cache|mkinitfs|grub-mkconfig'
                    regex += '|xdg-mime|udevadm)(?:\\s|$)'
                    if misc.string_search(regex, srcbuild, escape=False):
                        message.sub_warning(_('Possible unnecessary triggers invocation(s)'))

                if self.users:
                    if misc.string_search('useradd|adduser', srcbuild, escape=False) \
                        and not misc.string_search('userdel|deluser', srcbuild, escape=False):
                        message.sub_warning(_('User(s) added but not deleted'))

                if self.groups:
                    if misc.string_search('groupadd|addgroup', srcbuild, escape=False) \
                        and not misc.string_search('groupdel|delgroup', srcbuild, escape=False):
                        message.sub_warning(_('Group(s) added but not deleted'))

                if self.signatures:
                    sources = database.remote_metadata(target, 'sources')
                    pgpkeys = database.remote_metadata(target, 'pgpkeys')
                    for src in sources:
                        if misc.url_supported(src, False):
                            for ext in ('sig', 'asc', 'sign'):
                                sig1 = '%s.%s' % (src, ext)
                                sig2 = '%s.%s' % (misc.file_name(src, False), ext)
                                if sig1 in sources or sig2 in sources:
                                    message.sub_debug(_('Signature already in sources for'), src)
                                    continue

                                message.sub_debug(_('Probing for'), sig1)
                                message.sub_debug(_('Probing for'), sig2)
                                if misc.url_ping(sig1):
                                    message.sub_warning(_('Signature available but not in sources'), sig1)
                                    if not pgpkeys:
                                        message.sub_warning(_('Signature in sources but no pgpkeys'), src)
                                    break
                                elif misc.url_ping(sig2):
                                    message.sub_warning(_('Signature available but not in sources'), sig2)
                                    if not pgpkeys:
                                        message.sub_warning(_('Signature in sources but no pgpkeys'), src)
                                    break

                if self.pulse:
                    sources = database.remote_metadata(target, 'sources')
                    for src in sources:
                        if misc.url_supported(src, False):
                            if not misc.url_ping(src):
                                message.sub_warning(_('Source not reachable'), src)
                                # TODO: check mirrors too


class Merge(object):
    ''' Merge backup files '''
    def __init__(self):
        self.targets = database.local_all(basename=True)

    def merge(self, origfile, backfile):
        message.sub_warning(_('Backup file detected'), backfile)
        editor = os.environ.get('EDITOR') or misc.whereis('vim')
        finput = input
        if misc.python2:
            finput = raw_input
        action = finput(_('''
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
                misc.file_read(backfile).splitlines(), \
                misc.file_read(origfile).splitlines())):
                print(line)
            print('*' * 80 + '\n')
            self.merge(origfile, backfile)
        elif action == '2':
            misc.system_command((editor, origfile))
            self.merge(origfile, backfile)
        elif action == '3':
            misc.system_command((editor, backfile))
            self.merge(origfile, backfile)
        elif action == '4':
            shutil.copy2(backfile, origfile)
            os.unlink(backfile)
        elif action == '5':
            os.unlink(backfile)

    def main(self):
        for target in self.targets:
            message.sub_info(_('Checking'), target)
            backup = database.local_metadata(target, 'backup') or {}
            for sfile in backup:
                origfile = '%s/%s' % (libspm.ROOT_DIR, sfile)
                backfile = '%s.backup' % origfile
                if os.path.isfile(origfile) and os.path.isfile(backfile):
                    # the checksums are not used since the backup file can be edited
                    if misc.file_read(origfile) == misc.file_read(backfile):
                        message.sub_debug(_('Original and backup are not different'), origfile)
                        continue
                    self.merge(origfile, backfile)


class Edit(object):
    ''' Edit SRCBUILDs from repository via EDITOR (fallbacks to vim) '''
    def __init__(self, targets):
        self.targets = []
        for target in targets:
            self.targets.extend(database.remote_alias(target))

    def main(self):
        editor = os.environ.get('EDITOR') or misc.whereis('vim')
        for target in self.targets:
            match = database.remote_search(target)
            if match:
                misc.system_command((editor, '%s/SRCBUILD' % match))


class Which(object):
    ''' Print full path to SRCBUILD of target(s) '''
    def __init__(self, pattern, cat=False, plain=False):
        self.pattern = pattern
        self.cat = cat
        self.plain = plain

    def main(self):
        for target in database.remote_all(basename=False):
            if re.search(self.pattern, os.path.basename(target)):
                if self.plain:
                    print(target)
                else:
                    message.sub_info(_('Match'), target)
                if self.cat:
                    print(misc.file_read('%s/SRCBUILD' % target))


class Pack(object):
    ''' Pack local (installed) target files into tarball '''
    def __init__(self, targets, directory=misc.dir_current()):
        self.targets = []
        for target in targets:
            self.targets.extend(database.remote_alias(target))
        self.directory = directory

    def main(self):
        for target in self.targets:
            if database.local_search(target):
                target_version = database.local_metadata(target, 'version')
                target_packfile = '%s/%s_%s.tar.gz' % (self.directory, \
                    os.path.basename(target), target_version)

                content = []
                for sfile in database.local_metadata(target, 'footprint'):
                    content.append('%s/%s' % (libspm.ROOT_DIR, sfile))
                # add metadata directory, it is not listed in the footprint
                content.append('%s/%s' % (libspm.LOCAL_DIR, target))

                message.sub_info(_('Compressing'), target_packfile)
                misc.archive_compress(content, target_packfile, libspm.ROOT_DIR)
            else:
                message.sub_critical(_('Invalid target'), target)
                sys.exit(2)


class Serve(object):
    ''' Share cache directories with local network parties '''
    def __init__(self, port, address):
        self.port = port
        self.address = address

    def main(self):
        httpd = None
        try:
            message.sub_info(_('Serving caches directory'))
            os.chdir(libspm.CACHE_DIR)
            handler = HTTPServer.SimpleHTTPRequestHandler
            httpd = socketserver.TCPServer((self.address, self.port), handler)
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
        lhostfiles = []
        ltargetsfiles = []
        if self.cross:
            lhostfiles = misc.list_files(self.directory)
        else:
            lmounts = []
            for spath in misc.list_all(self.directory):
                if os.path.ismount(spath):
                    lmounts.append(spath)
                    continue
                shouldappend = True
                for smount in lmounts:
                    if spath.startswith(smount):
                        shouldappend = False
                        break
                if not os.path.isdir(spath) and shouldappend:
                    lhostfiles.append(spath)

        for target in database.local_all():
            ltargetsfiles.extend(database.local_metadata(target, 'footprint'))
        if not self.plain:
            message.sub_info(_('Searching for disowned files'))
        for sfile in lhostfiles:
            if not sfile in ltargetsfiles:
                if self.plain:
                    print(sfile)
                else:
                    message.sub_info(_('Disowned file'), sfile)


if __name__ == '__main__':
    try:
        EUID = os.geteuid()

        class OverrideRootDir(argparse.Action):
            ''' Override system root directory '''
            def __call__(self, parser, namespace, values, option_string=None):
                full_path = os.path.abspath(values) + '/'
                libspm.ROOT_DIR = full_path
                libspm.LOCAL_DIR = full_path + 'var/local/spm'
                misc.ROOT_DIR = libspm.ROOT_DIR
                database.ROOT_DIR = libspm.ROOT_DIR
                database.CACHE_DIR = libspm.CACHE_DIR
                database.LOCAL_DIR = libspm.LOCAL_DIR
                setattr(namespace, self.dest, values)

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
        lint_parser.add_argument('-P', '--purge', action='store_true', \
            help=_('Check for purge paths'))
        lint_parser.add_argument('-M', '--module', action='store_true', \
            help=_('Check for module(s) in non-standard directory'))
        lint_parser.add_argument('-f', '--footprint', action='store_true', \
            help=_('Check for footprint consistency'))
        lint_parser.add_argument('-b', '--builddir', action='store_true', \
            help=_('Check for build directory trace(s)'))
        lint_parser.add_argument('-o', '--permissions', action='store_true', \
            help=_('Check permissions'))
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
        sane_parser.add_argument('-s', '--signatures', action='store_true', \
            help=_('Check for signature(s) not in the sources array'))
        sane_parser.add_argument('-p', '--pulse', action='store_true', \
            help=_('Check for source(s) not being available'))
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

        if EUID == 0:
            pack_parser = subparsers.add_parser('pack')
            pack_parser.add_argument('-d', '--directory', type=str, \
                default=misc.dir_current(), help=_('Set output directory'))
            pack_parser.add_argument('TARGETS', nargs='+', type=str, \
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

        parser.add_argument('--root', type=str, action=OverrideRootDir, \
            help=_('Change system root directory'))
        parser.add_argument('--debug', nargs=0, action=OverrideDebug, \
            help=_('Enable debug messages'))
        parser.add_argument('--version', action='version', \
            version='Source Package Manager Tools v%s' % app_version, \
            help=_('Show SPM Tools version and exit'))

        ARGS = parser.parse_args()
        if not sys.stdin.isatty() and ARGS.TARGETS == ['-']:
            ARGS.TARGETS = sys.stdin.read().split()

        if ARGS.mode == 'dist':
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
            message.sub_info(_('ROOT_DIR'), libspm.ROOT_DIR)
            message.sub_info(_('DEPENDS'), ARGS.depends)
            message.sub_info(_('REVERSE'), ARGS.reverse)
            message.sub_info(_('TARGETS'), ARGS.TARGETS)
            message.info(_('Poking locals...'))
            m = Check(ARGS.TARGETS, ARGS.depends, ARGS.reverse)
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
                ARGS.purge = True
                ARGS.module = True
                ARGS.footprint = True
                ARGS.builddir = True
                ARGS.permissions = True
                ARGS.executable = True
                ARGS.path = True
                ARGS.shebang = True
                ARGS.backup = True
                ARGS.conflicts = True

            message.info(_('Runtime information'))
            message.sub_info(_('MAN'), ARGS.man)
            message.sub_info(_('UDEV'), ARGS.udev)
            message.sub_info(_('SYMLINK'), ARGS.symlink)
            message.sub_info(_('PURGE'), ARGS.purge)
            message.sub_info(_('MODULE'), ARGS.module)
            message.sub_info(_('FOOTPRINT'), ARGS.footprint)
            message.sub_info(_('BUILDDIR'), ARGS.builddir)
            message.sub_info(_('PERMISSIONS'), ARGS.permissions)
            message.sub_info(_('EXECUTABLE'), ARGS.executable)
            message.sub_info(_('PATH'), ARGS.path)
            message.sub_info(_('SHEBANG'), ARGS.shebang)
            message.sub_info(_('BACKUP'), ARGS.backup)
            message.sub_info(_('CONFLICTS'), ARGS.conflicts)
            message.sub_info(_('TARGETS'), ARGS.TARGETS)
            message.info(_('Poking locals...'))

            m = Lint(ARGS.TARGETS, ARGS.man, ARGS.udev, ARGS.symlink, \
                ARGS.purge, ARGS.module, ARGS.footprint, ARGS.builddir, \
                ARGS.permissions, ARGS.executable, ARGS.path, ARGS.shebang, \
                ARGS.backup, ARGS.conflicts)
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
                ARGS.signatures = True
                ARGS.pulse = True

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
            message.sub_info(_('SIGNATURES'), ARGS.signatures)
            message.sub_info(_('PULSE'), ARGS.pulse)
            message.sub_info(_('TARGETS'), ARGS.TARGETS)
            message.info(_('Poking remotes...'))

            m = Sane(ARGS.TARGETS, ARGS.enable, ARGS.disable, ARGS.null, \
                ARGS.maintainer, ARGS.note, ARGS.variables, ARGS.triggers, \
                ARGS.users, ARGS.groups, ARGS.signatures, ARGS.pulse)
            m.main()

        elif ARGS.mode == 'merge':
            message.info(_('Runtime information'))
            message.sub_info(_('ROOT_DIR'), libspm.ROOT_DIR)
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

        if not ARGS.mode and misc.python3:
            parser.print_help()

    except configparser.Error as detail:
        message.critical('CONFIGPARSER', detail)
        sys.exit(3)
    except subprocess.CalledProcessError as detail:
        message.critical('SUBPROCESS', detail)
        sys.exit(4)
    except (HTTPError, URLError) as detail:
        if hasattr(detail, 'url') and hasattr(detail, 'code'):
            # misc.fetch() provides the URL, HTTPError provides the code
            message.critical('URLLIB', "%s: '%s' (%s)" % (detail.url, detail.reason, \
                detail.code))
        elif hasattr(detail, 'url'):
            message.critical('URLLIB', "%s: '%s'" % (detail.url, detail.reason))
        else:
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
