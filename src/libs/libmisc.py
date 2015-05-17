#!/bin/python2

'''
A module to handle various tasks fuzz free.

The Misc() class packs a lot - files, directories, urls, archives and even
processes handling.

Magic() is specifiec to file types (MIMEs) recognition via libmagic (part of
file). It is a thin wrapper around it.

Inotify() is another wrapper but around inotify system calls. It can be used
to monitor for file/directory changes on filesystems.

'''

import sys, os, re, tarfile, zipfile, subprocess, shutil, shlex, pwd, inspect
import types, gzip, bz2, time, ctypes, ctypes.util, getpass, base64
from struct import unpack
from fcntl import ioctl
from termios import FIONREAD
if int(sys.version_info[0]) < 3:
    from urlparse import urlparse
    from urllib2 import urlopen
    from urllib2 import Request
    from urllib2 import URLError
    from httplib import BadStatusLine
else:
    from urllib.parse import urlparse
    from urllib.request import urlopen
    from urllib.request import Request
    from urllib.error import URLError
    from http.client import BadStatusLine


class Misc(object):
    ''' Various methods for every-day usage '''
    def __init__(self):
        self.OFFLINE = False
        self.TIMEOUT = 30
        self.ROOT_DIR = '/'
        self.GPG_DIR = os.path.expanduser('~/.gnupg')
        self.CATCH = False
        self.SIGNPASS = None
        self.magic = Magic()
        self.python2 = False
        self.python3 = False
        if int(sys.version_info[0]) < 3:
            self.python2 = True
        else:
            self.python3 = True

    def typecheck(self, a, b):
        ''' Poor man's variable type checking, do not use with Python 3000 '''
        if not isinstance(a, b):
            line = inspect.currentframe().f_back.f_lineno
            raise TypeError('Variable is not %s (%d)' % (str(b), line))

    def whereis(self, program, fallback=True, chroot=False):
        ''' Find full path to executable from PATH '''
        if self.python2:
            self.typecheck(program, (types.StringTypes))
            self.typecheck(fallback, (types.BooleanType))
            self.typecheck(chroot, (types.BooleanType))

        program = os.path.basename(program)
        for path in os.environ.get('PATH', '/bin:/usr/bin').split(':'):
            exe = os.path.join(path, program)
            # normalize because os.path.join sucks and can't be used in this case
            if chroot and os.path.isfile(os.path.realpath(self.ROOT_DIR + exe)):
                return exe
            elif os.path.isfile(exe):
                return exe

        if fallback:
            # in the future, fallback will return program and let OSError be
            # raised at higher level, e.g. by subprocess
            raise OSError('Program not found in PATH', program)
        return None

    def getpass(self, sprompt='Password: '):
        ''' Get password from user input '''
        if self.python2:
            self.typecheck(sprompt, (types.StringTypes))
        if not sys.stdin.isatty():
            raise Exception('Standard input is not a TTY')
        return getpass.getpass(sprompt)

    def string_encode(self, string):
        ''' String wrapper to ensure Python3 compat '''
        if self.python3 and isinstance(string, bytes):
            return string.decode('utf-8')
        elif self.python3 and isinstance(string, str):
            return string.encode('utf-8')
        else:
            return string

    def string_convert(self, variant):
        ''' Convert input to string but only if it is not string '''
        if isinstance(variant, (list, tuple)):
            return ' '.join(variant)
        elif isinstance(variant, dict):
            return ' '.join(list(variant.keys()))
        return variant

    def string_unit_guess(self, svar):
        ''' Guess the units to be used by string_unit() '''
        if self.python2:
            self.typecheck(svar, (types.StringTypes))

        lenght = len(svar)
        if lenght > 6:
            return 'Mb'
        elif lenght > 3:
            return 'Kb'
        else:
            return 'b'

    def string_unit(self, svar, sunit='Mb', bprefix=False):
        ''' Convert bytes to humar friendly units '''
        if self.python2:
            self.typecheck(svar, (types.StringTypes))
            self.typecheck(sunit, (types.StringTypes))
            self.typecheck(bprefix, (types.BooleanType))

        if sunit == 'Mb':
            if bprefix:
                return '%d%s' % (int(svar) / (1024 * 1024), 'Mb')
            return int(svar) / (1024 * 1024)
        elif sunit == 'Kb':
            if bprefix:
                return '%d%s' % (int(svar) / 1024, 'Kb')
            return int(svar) / 1024
        else:
            if bprefix:
                return '%d%s' % (int(svar), 'b')
            return svar

    def string_search(self, string, string2, exact=False, escape=True):
        ''' Search for string in other string or list '''
        if self.python2:
            self.typecheck(string, (types.StringTypes))
            self.typecheck(string2, (types.StringTypes, types.TupleType, types.ListType))
            self.typecheck(exact, (types.BooleanType))
            self.typecheck(escape, (types.BooleanType))

        if exact and escape:
            return re.findall('(?:\\s|^)' + re.escape(string) + '(?:\\s|$)', \
                self.string_convert(string2))
        elif exact:
            return re.findall('(?:\\s|^)' + string + '(?:\\s|$)', \
                self.string_convert(string2))
        elif escape:
            return re.findall(re.escape(string), self.string_convert(string2))
        else:
            return re.findall(string, self.string_convert(string2))

    def file_name(self, sfile, basename=True):
        ''' Get name of file without the extension '''
        if self.python2:
            self.typecheck(sfile, (types.StringTypes))
            self.typecheck(basename, (types.BooleanType))

        if basename:
            return os.path.splitext(os.path.basename(sfile))[0]
        return os.path.splitext(sfile)[0]

    def file_extension(self, sfile):
        ''' Get the extension of file '''
        if self.python2:
            self.typecheck(sfile, (types.StringTypes))

        return os.path.splitext(sfile)[1].lstrip('.')

    def file_touch(self, sfile):
        ''' Touch a file, making sure it exists '''
        if self.python2:
            self.typecheck(sfile, (types.StringTypes))

        if not os.path.isfile(sfile):
            self.file_write(sfile, '')

    def file_delete(self, sfile):
        ''' Delete file but only if it exists, handles links too '''
        if self.python2:
            self.typecheck(sfile, (types.StringTypes))

        if os.path.isfile(os.path.realpath(sfile)):
            os.unlink(sfile)

    def file_read(self, sfile):
        ''' Get file content '''
        if self.python2:
            self.typecheck(sfile, (types.StringTypes))

        rfile = open(sfile, 'rb')
        try:
            content = rfile.read()
        finally:
            rfile.close()
        return self.string_encode(content)

    def file_read_nonblock(self, sfile, ibuffer=1024):
        ''' Get file content non-blocking '''
        if self.python2:
            self.typecheck(sfile, (types.StringTypes))
            self.typecheck(ibuffer, (types.IntType))

        fd = os.open(sfile, os.O_NONBLOCK)
        try:
            content = os.read(fd, ibuffer)
        finally:
            os.close(fd)
        return content

    def file_readlines(self, sfile):
        ''' Get file content, split by new line, as list '''
        if self.python2:
            self.typecheck(sfile, (types.StringTypes))

        rfile = open(sfile, 'rb')
        try:
            content = rfile.read().splitlines()
        finally:
            rfile.close()
        return self.string_encode(content)

    def file_write(self, sfile, content, mode='w'):
        ''' Write data to file '''
        if self.python2:
            self.typecheck(sfile, (types.StringTypes))
            self.typecheck(content, (types.StringTypes))
            self.typecheck(mode, (types.StringTypes))

        self.dir_create(os.path.dirname(sfile))
        wfile = open(sfile, mode)
        try:
            wfile.write(content)
        finally:
            wfile.close()

    def file_write_nonblock(self, sfile, content):
        ''' Write data to file non-blocking (overwrites) '''
        if self.python2:
            self.typecheck(sfile, (types.StringTypes))
            self.typecheck(content, (types.StringTypes))

        self.dir_create(os.path.dirname(sfile))
        fd = os.open(sfile, os.O_NONBLOCK | os.O_WRONLY)
        try:
            os.write(fd, content)
        finally:
            os.close(fd)

    def file_search(self, string, sfile, exact=False, escape=True):
        ''' Search for string in file '''
        if self.python2:
            self.typecheck(string, (types.StringTypes))
            self.typecheck(sfile, (types.StringTypes))
            self.typecheck(exact, (types.BooleanType))
            self.typecheck(escape, (types.BooleanType))

        return self.string_search(string, self.file_read(sfile), exact=exact, \
            escape=escape)

    def file_mime(self, sfile, resolve=False):
        ''' Get file type, you should use Magic().get() instead '''
        if self.python2:
            self.typecheck(sfile, (types.StringTypes))
            self.typecheck(resolve, (types.BooleanType))

        if resolve:
            sfile = os.path.realpath(sfile)
        return self.string_encode(self.magic.get(sfile))

    def file_substitute(self, string, string2, sfile):
        ''' Substitue a string with another in file '''
        self.typecheck(string, (types.StringTypes))
        self.typecheck(string2, (types.StringTypes))
        self.typecheck(sfile, (types.StringTypes))

        self.file_write(sfile, re.sub(string, string2, self.file_read(sfile)))

    def gpg_receive(self, lkeys, lservers=None):
        ''' Import PGP keys as (somewhat) trusted '''
        if self.python2:
            self.typecheck(lkeys, (types.ListType, types.TupleType))
            self.typecheck(lservers, (types.NoneType, types.ListType, types.TupleType))

        if self.OFFLINE:
            return
        if lservers is None:
            lservers = []
        self.dir_create(self.GPG_DIR, ipermissions=0o700)
        cmd = [self.whereis('gpg2'), '--homedir', self.GPG_DIR]
        for server in lservers:
            cmd.extend(('--keyserver', server))
        # FIXME: do --refresh-keys if already imported
        cmd.append('--recv-keys')
        cmd.extend(lkeys)
        self.system_command(cmd)

    def gpg_sign(self, sfile, skey=None, sprompt='Passphrase: '):
        ''' Sign a file with PGP signature via GnuPG '''
        if self.python2:
            self.typecheck(sfile, (types.StringTypes))
            self.typecheck(skey, (types.NoneType, types.StringTypes))
            self.typecheck(sprompt, (types.StringTypes))

        self.dir_create(self.GPG_DIR, ipermissions=0o700)
        cmd = [self.whereis('gpg2'), '--homedir', self.GPG_DIR]
        if skey:
            cmd.extend(('--default-key', skey))
        cmd.extend(('--yes', '--no-tty', '--passphrase-fd', '0'))
        cmd.extend(('--detach-sig', '--sign', '--batch', sfile))
        if not self.SIGNPASS:
            self.SIGNPASS = base64.encodestring(self.getpass(sprompt))
        self.system_input(cmd, base64.decodestring(self.SIGNPASS))

    def gpg_verify(self, sfile, ssignature=None):
        ''' Verify file PGP signature via GnuPG '''
        if self.python2:
            self.typecheck(sfile, (types.StringTypes))
            self.typecheck(ssignature, (types.NoneType, types.StringTypes))

        self.dir_create(self.GPG_DIR, ipermissions=0o700)
        cmd = [self.whereis('gpg2'), '--homedir', self.GPG_DIR]
        # in case the signature is passed instead of the file to verify
        if sfile.endswith('.sig'):
            sfile = sfile.replace('.sig', '')
        elif sfile.endswith('.asc'):
            sfile = sfile.replace('.asc', '')
        if not ssignature:
            sig2 = '%s.asc' % sfile
            if os.path.isfile(sig2):
                ssignature = sig2
            else:
                ssignature = '%s.sig' % sfile
        cmd.extend(('--verify', '--batch', ssignature, sfile))
        self.system_command(cmd)

    def dir_create(self, sdir, demote='', ipermissions=0):
        ''' Create directory if it does not exist, including leading paths '''
        if self.python2:
            self.typecheck(sdir, (types.StringTypes))
            self.typecheck(demote, (types.StringTypes))
            self.typecheck(ipermissions, (types.IntType))

        if not os.path.isdir(sdir) and not os.path.islink(sdir):
            # sadly, demoting works only for sub-processes
            if demote:
                self.system_command((self.whereis('mkdir'), '-p', sdir), demote=demote)
            else:
                os.makedirs(sdir)
        if ipermissions:
            os.chmod(sdir, ipermissions)

    def dir_remove(self, sdir):
        ''' Remove directory recursively '''
        if self.python2:
            self.typecheck(sdir, (types.StringTypes))

        for f  in self.list_files(sdir):
            os.unlink(f)
        for d in self.list_dirs(sdir, btopdown=False):
            if os.path.islink(d):
                os.unlink(d)
            else:
                os.rmdir(d)
        if os.path.islink(sdir):
            os.unlink(sdir)
        else:
            os.rmdir(sdir)

    def dir_size(self, sdir):
        ''' Get size of directory '''
        if self.python2:
            self.typecheck(sdir, (types.StringTypes))

        size = 0
        for sfile in self.list_files(sdir):
            if os.path.islink(sfile):
                continue
            size += os.path.getsize(sfile)
        return size

    def dir_current(self):
        ''' Get current directory with fallback '''
        try:
            cwd = os.getcwd()
        except OSError:
            cwd = '/'
        return cwd

    def list_files(self, sdir, bcross=True, btopdown=True):
        ''' Get list of files in directory recursively '''
        if self.python2:
            self.typecheck(sdir, (types.StringTypes))
            self.typecheck(bcross, (types.BooleanType))
            self.typecheck(btopdown, (types.BooleanType))

        slist = []
        for root, subdirs, files in os.walk(sdir, btopdown):
            if not bcross:
                subdirs[:] = [
                    d for d in subdirs
                    if not os.path.ismount(os.path.join(root, d))]
            for sfile in files:
                slist.append(os.path.join(root, sfile))
        return slist

    def list_dirs(self, sdir, bcross=True, btopdown=True):
        ''' Get list of directories in directory recursively '''
        if self.python2:
            self.typecheck(sdir, (types.StringTypes))
            self.typecheck(bcross, (types.BooleanType))
            self.typecheck(btopdown, (types.BooleanType))

        slist = []
        for root, subdirs, files in os.walk(sdir, btopdown):
            if not bcross:
                subdirs[:] = [
                    d for d in subdirs
                    if not os.path.ismount(os.path.join(root, d))]
            for d in subdirs:
                slist.append(os.path.join(root, d))
        return slist

    def list_all(self, sdir, bcross=True, btopdown=True):
        ''' Get list of files and directories in directory recursively '''
        if self.python2:
            self.typecheck(sdir, (types.StringTypes))
            self.typecheck(bcross, (types.BooleanType))
            self.typecheck(btopdown, (types.BooleanType))

        slist = []
        for root, subdirs, files in os.walk(sdir, btopdown):
            if not bcross:
                subdirs[:] = [
                    d for d in subdirs
                    if not os.path.ismount(os.path.join(root, d))]
            for d in subdirs:
                slist.append(os.path.join(root, d))
            for sfile in files:
                slist.append(os.path.join(root, sfile))
        return slist

    def url_normalize(self, surl, basename=False):
        ''' Normalize URL, optionally get basename '''
        if self.python2:
            self.typecheck(surl, (types.StringTypes))
            self.typecheck(basename, (types.BooleanType))

        path = urlparse(surl).path
        if basename:
            return os.path.basename(path)
        return path


    def url_ping(self, surl='http://www.google.com', lmirrors=None, ssuffix=''):
        ''' Ping URL, optionally URL base on mirrors '''
        if self.python2:
            self.typecheck(surl, (types.StringTypes))
            self.typecheck(lmirrors, (types.NoneType, types.ListType))
            self.typecheck(ssuffix, (types.StringTypes))

        if self.OFFLINE:
            return False

        lurls = []
        if lmirrors:
            for mirror in lmirrors:
                sbase = self.url_normalize(surl, True)
                snewurl = '%s/%s%s' % (mirror, ssuffix, sbase)
                lurls.append(snewurl)
        lurls.append(surl)

        for url in lurls:
            try:
                p = urlopen(url, timeout=self.TIMEOUT)
                p.close()
                return True
            except (URLError, BadStatusLine):
                pass
        return False

    def fetch_request(self, surl, data=None):
        ''' Returns urlopen object, it is NOT closed! '''
        if self.python2:
            self.typecheck(surl, (types.StringTypes))
            self.typecheck(data, (types.NoneType, types.DictType))

        if data is None:
            data = {}
        request = Request(surl, headers=data)
        # SSL verification works OOTB only on Python >= 2.7.9 (officially)
        if sys.version_info[2] >= 9:
            import ssl
            ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            return urlopen(request, timeout=self.TIMEOUT, context=ctx)
        else:
            return urlopen(request, timeout=self.TIMEOUT)

    def fetch_plain(self, surl, destination, iretry=3):
        ''' Download file, iretry is passed internally! '''
        if self.python2:
            self.typecheck(surl, (types.StringTypes))
            self.typecheck(destination, (types.StringTypes))
            self.typecheck(iretry, (types.IntType))

        if self.OFFLINE:
            return

        rfile = self.fetch_request(surl)
        # not all requests have content-lenght:
        # http://en.wikipedia.org/wiki/Chunked_transfer_encoding
        rsize = rfile.headers.get('Content-Length', '0')
        if os.path.exists(destination):
            lsize = str(os.path.getsize(destination))
            last = '%s.last' % destination
            if lsize == rsize:
                return rfile.close()
            elif lsize > rsize or (os.path.isfile(last) and not self.file_read(last) == rsize):
                lsize = '0'
                os.unlink(destination)
                # PGP signatures are small in size and it's easy for the
                # fetcher to get confused if the file to be download is
                # re-uploaded with minimal changes so force the signature fetch
                sig1 = '%s.sig' % destination
                sig2 = '%s.asc' % destination
                if os.path.isfile(sig1):
                    os.unlink(sig1)
                if os.path.isfile(sig2):
                    os.unlink(sig2)
            if rfile.headers.get('Accept-Ranges') == 'bytes':
                # setup new request with custom header
                rfile.close()
                rfile = self.fetch_request(surl, {'Range': 'bytes=%s-' % lsize})
        self.dir_create(os.path.dirname(destination))
        lfile = open(destination, 'ab')
        try:
            # since the local file size changes use persistent units based on
            # remote file size
            units = self.string_unit_guess(rsize)
            while True:
                msg = 'Downloading: %s, %s/%s' % (self.url_normalize(surl, True), \
                    self.string_unit(str(os.path.getsize(destination)), units), \
                    self.string_unit(rsize, units, True))
                sys.stdout.write(msg)
                chunk = rfile.read(10240)
                if not chunk:
                    break
                lfile.write(chunk)
                # in Python 3000 that would be print(blah, end='')
                sys.stdout.write('\r' * len(msg))
                sys.stdout.flush()
        except URLError as detail:
            if not iretry == 0:
                self.fetch(surl, destination, iretry-1)
            else:
                detail.url = surl
                raise detail
        finally:
            self.file_write('%s.last' % destination, rsize)
            sys.stdout.write('\n')
            lfile.close()
            rfile.close()

    def fetch_git(self, surl, destination):
        ''' Clone/pull Git repository '''
        if self.python2:
            self.typecheck(surl, (types.StringTypes))
            self.typecheck(destination, (types.StringTypes))

        if self.OFFLINE:
            return

        git = self.whereis('git')
        if os.path.isdir('%s/.git' % destination):
            self.system_command((git, 'pull', surl), cwd=destination)
        else:
            self.system_command((git, 'clone', '--depth=1', surl, \
                destination))
            # allow gracefull pulls and merges
            self.system_command((git, 'config', 'user.name', \
                'spm'), cwd=destination)
            self.system_command((git, 'config', 'user.email', \
                'spm@unnatended.fake'), cwd=destination)

    def fetch_svn(self, surl, destination):
        ''' Clone/pull SVN repository '''
        if self.python2:
            self.typecheck(surl, (types.StringTypes))
            self.typecheck(destination, (types.StringTypes))

        if self.OFFLINE:
            return

        svn = self.whereis('svn')
        if os.path.isdir('%s/.svn' % destination):
            self.system_command((svn, 'up'), cwd=destination)
        else:
            self.system_command((svn, 'co', '--depth=infinity', surl, \
                destination))

    def fetch(self, surl, destination, lmirrors=None, ssuffix='', iretry=3):
        ''' Download file from mirror if possible, iretry is passed internally! '''
        if self.python2:
            self.typecheck(surl, (types.StringTypes))
            self.typecheck(destination, (types.StringTypes))
            self.typecheck(lmirrors, (types.NoneType, types.TupleType, types.ListType))
            self.typecheck(ssuffix, (types.StringTypes))
            self.typecheck(iretry, (types.IntType))

        # create a local copy of lmirrors to avoid changing lmirrors as it's a
        # reference and lmirrors.pop() modifies the value of external modules
        # which is not desired. mymirrors = lmirrors is not a solution!
        mymirrors = []
        if lmirrors:
            mymirrors.extend(lmirrors)
        sbase = self.url_normalize(surl, True)
        if mymirrors:
            smirror = mymirrors[0]
            mymirrors.pop(0)
            snewurl = '%s/%s%s' % (smirror, ssuffix, sbase)
        else:
            snewurl = surl
        try:
            # mirrors are not supported for VCS repos on purpose
            if surl.startswith('git://') or sbase.endswith('.git'):
                self.fetch_git(surl, destination)
            elif surl.startswith('svn://'):
                self.fetch_svn(surl, destination)
            elif snewurl.startswith(('http://', 'https://', 'ftp://', \
                'ftps://')):
                self.fetch_plain(snewurl, destination, 0)
            else:
                raise Exception('Unsupported URL', surl)
        except URLError as detail:
            if not iretry == 0:
                return self.fetch(surl, destination, mymirrors, ssuffix, iretry-1)
            raise detail

    def archive_supported(self, sfile):
        ''' Test if file is archive that can be handled properly '''
        if self.python2:
            self.typecheck(sfile, (types.StringTypes))

        if os.path.isdir(sfile):
            return False
        smime = self.file_mime(sfile, True)
        if smime == 'application/x-xz' \
            or smime == 'application/x-lzma' \
            or smime == 'application/x-gzip' \
            or smime == 'application/x-bzip2' \
            or tarfile.is_tarfile(sfile) \
            or zipfile.is_zipfile(sfile):
            return True
        return False

    def archive_compress(self, lpaths, sfile, strip):
        ''' Create archive from list of files and/or directories '''
        if self.python2:
            self.typecheck(lpaths, (types.TupleType, types.ListType))
            self.typecheck(sfile, (types.StringTypes))
            self.typecheck(strip, (types.StringTypes))

        self.dir_create(os.path.dirname(sfile))

        if sfile.endswith(('tar.bz2', '.tar.gz')):
            tarf = tarfile.open(sfile, 'w:' + self.file_extension(sfile))
            try:
                for item in lpaths:
                    tarf.add(item, item.lstrip(strip))
            finally:
                tarf.close()
        elif sfile.endswith('.zip'):
            zipf = zipfile.ZipFile(sfile, mode='w')
            try:
                for item in lpaths:
                    zipf.write(item, item.lstrip(strip))
            finally:
                zipf.close()
        elif sfile.endswith(('.xz', '.lzma')):
            tar = self.whereis('bsdtar', fallback=False)
            if not tar:
                tar = self.whereis('tar')
            command = [tar, '-caf', sfile, '-C', strip]
            for f in lpaths:
                command.append(f.replace(strip, '.'))
            self.system_command(command)
        elif sfile.endswith('.gz'):
            if len(lpaths) > 1:
                raise Exception('GZip', 'format can hold only single file')
            gzipf = gzip.GzipFile(sfile, 'wb')
            for f in lpaths:
                gzipf.write(self.file_read(f))
            gzipf.close()
        elif sfile.endswith('.bz2'):
            if len(lpaths) > 1:
                raise Exception('BZip', 'format can hold only single file')
            bzipf = bz2.BZ2File(sfile, 'wb')
            for f in lpaths:
                bzipf.write(self.file_read(f))
            bzipf.close()

    def archive_decompress(self, sfile, sdir, demote=''):
        ''' Extract archive to directory '''
        if self.python2:
            self.typecheck(sfile, (types.StringTypes))
            self.typecheck(sdir, (types.StringTypes))
            self.typecheck(demote, (types.StringTypes))

        self.dir_create(sdir)

        # WARNING!!! the -P option is not supported by Busybox's `tar` applet.

        # standard tarfile library locks the filesystem and upon interrupt the
        # filesystem stays locked which is bad. on top of that the tarfile
        # library can not replace files while they are being used thus external
        # utilities are used for extracting Tar archives.
        smime = self.file_mime(sfile, True)
        if smime == 'application/x-xz' \
            or smime == 'application/x-lzma' \
            or tarfile.is_tarfile(sfile) or zipfile.is_zipfile(sfile):
            bsdtar = self.whereis('bsdtar', fallback=False)
            if bsdtar:
                self.system_command((bsdtar, '-xpPf', sfile, '-C', sdir), \
                    demote=demote)
            else:
                self.system_command((self.whereis('tar'), '-xphf', sfile, \
                    '-C', sdir), demote=demote)
        elif smime == 'application/x-gzip':
            gfile = gzip.GzipFile(sfile, 'rb')
            self.file_write(self.file_name(sfile, False), gfile.read())
            gfile.close()
        elif smime == 'application/x-bzip2':
            bfile = bz2.BZ2File(sfile, 'rb')
            self.file_write(self.file_name(sfile, False), bfile.read())
            bfile.close()

    def archive_list(self, sfile):
        ''' Get list of files in archive '''
        if self.python2:
            self.typecheck(sfile, (types.StringTypes))

        content = []
        smime = self.file_mime(sfile, True)
        if tarfile.is_tarfile(sfile):
            tfile = tarfile.open(sfile)
            try:
                for member in tfile.getmembers():
                    if not member.isdir():
                        content.append(member.name)
            finally:
                tfile.close()
        elif zipfile.is_zipfile(sfile):
            zfile = zipfile.ZipFile(sfile)
            content = zfile.namelist()
            zfile.close()
        elif smime == 'application/x-xz' or smime == 'application/x-lzma':
            bsdtar = self.whereis('bsdtar', fallback=False)
            if bsdtar:
                content = self.system_output((bsdtar, '-tf', \
                    sfile)).splitlines()
            else:
                content = self.system_output((self.whereis('tar'), \
                    '-tf', sfile)).splitlines()
        elif smime == 'application/x-gzip':
            content = self.file_name(sfile, True).split()
        elif smime == 'application/x-bzip2':
            content = self.file_name(sfile, True).split()
        return content

    def archive_size(self, star, lpaths):
        ''' Get size of file(s) in Tar archive '''
        if self.python2:
            self.typecheck(star, (types.StringTypes))
            self.typecheck(lpaths, (types.TupleType, types.ListType))

        sizes = []
        tar = tarfile.open(star, 'r')
        try:
            for i in tar.getmembers():
                for sfile in lpaths:
                    if i.name == sfile:
                        sizes.append(i.size)
        finally:
            tar.close()
        return sizes

    def archive_content(self, star, lpaths):
        ''' Get content of file(s) in Tar archive '''
        if self.python2:
            self.typecheck(star, (types.StringTypes))
            self.typecheck(lpaths, (types.TupleType, types.ListType))

        content = []
        tar = tarfile.open(star, 'r')
        for i in tar.getmembers():
            for sfile in lpaths:
                if i.name == sfile:
                    t = tar.extractfile(i)
                    content.append(t.read())
                    t.close()
        tar.close()
        return content

    def system_demote(self, suser):
        ''' Change priviledges to different user, returns function pointer! '''
        if self.python2:
            self.typecheck(suser, (types.StringTypes))

        group = suser
        if suser and ':' in suser:
            group = suser.split(':')[1]
            suser = suser.split(':')[0]
        if not suser or not group:
            return
        # lambda
        def result():
            pw_uid = pwd.getpwnam(suser).pw_uid
            pw_gid = pwd.getpwnam(group).pw_gid
            pw_dir = pwd.getpwnam(suser).pw_dir
            # os.initgroups(suser, pw_gid)
            os.setgid(0)
            os.setgid(pw_gid)
            os.setuid(pw_uid)
            os.putenv('USER', suser)
            os.putenv('LOGNAME', suser)
            os.putenv('HOME', pw_dir)
            os.putenv('PWD', pw_dir)
        return result

    def system_output(self, command, shell=False, cwd='', demote=''):
        ''' Get output of external utility '''
        if self.python2:
            self.typecheck(command, (types.StringType, types.TupleType, types.ListType))
            self.typecheck(shell, (types.BooleanType))
            self.typecheck(cwd, (types.StringTypes))
            self.typecheck(demote, (types.StringTypes))

        if not cwd:
            cwd = self.dir_current()
        elif not os.path.isdir(cwd):
            cwd = '/'

        pipe = subprocess.Popen(command, stdout=subprocess.PIPE, \
            env={'LC_ALL': 'C'}, shell=shell, cwd=cwd, preexec_fn=self.system_demote(demote))
        output = pipe.communicate()[0].strip()
        return self.string_encode(output)

    def system_input(self, command, sinput, shell=False, demote=''):
        ''' Send input to external utility '''
        if self.python2:
            self.typecheck(command, (types.StringType, types.TupleType, types.ListType))
            self.typecheck(sinput, (types.StringTypes))
            self.typecheck(shell, (types.BooleanType))
            self.typecheck(demote, (types.StringTypes))

        if isinstance(command, str) and not shell:
            command = shlex.split(command)
        pipe = subprocess.Popen(command, stdin=subprocess.PIPE, \
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, \
            env={'LC_ALL': 'C'}, shell=shell, preexec_fn=self.system_demote(demote))
        out, err = pipe.communicate(input=sinput)
        if pipe.returncode != 0:
            raise(Exception('%s %s' % (out, err)))

    def system_scanelf(self, sfile, sformat='#F%n', sflags='', demote=''):
        ''' Get information about ELF files '''
        if self.python2:
            self.typecheck(sfile, (types.StringTypes))
            self.typecheck(sformat, (types.StringTypes))
            self.typecheck(sflags, (types.StringTypes))
            self.typecheck(demote, (types.StringTypes))

        return self.system_output((self.whereis('scanelf'), '-yCBF', \
            sformat, sflags, sfile), demote=demote)

    def system_command(self, command, shell=False, cwd='', catch=False, demote=''):
        ''' Execute system command safely '''
        if self.python2:
            self.typecheck(command, (types.StringType, types.TupleType, types.ListType))
            self.typecheck(shell, (types.BooleanType))
            self.typecheck(cwd, (types.StringTypes))
            self.typecheck(catch, (types.BooleanType))
            self.typecheck(demote, (types.StringTypes))

        if not cwd:
            cwd = self.dir_current()
        elif not os.path.isdir(cwd):
            cwd = '/'
        if isinstance(command, str) and not shell:
            command = shlex.split(command)
        if catch or self.CATCH:
            pipe = subprocess.Popen(command, stderr=subprocess.PIPE, \
                shell=shell, cwd=cwd, preexec_fn=self.system_demote(demote))
            pipe.wait()
            if pipe.returncode != 0:
                raise(Exception(pipe.communicate()[1].strip()))
            return pipe.returncode
        else:
            return subprocess.check_call(command, shell=shell, cwd=cwd, \
                preexec_fn=self.system_demote(demote))

    def system_chroot(self, command, shell=False, sinput=None):
        ''' Execute command in chroot environment '''
        if self.python2:
            self.typecheck(command, (types.StringType, types.TupleType, types.ListType))
            self.typecheck(shell, (types.BooleanType))
            self.typecheck(sinput, (types.NoneType, types.StringTypes))

        # prevent stupidity
        if self.ROOT_DIR == '/':
            return

        real_root = os.open('/', os.O_RDONLY)
        mount = self.whereis('mount')
        umount = self.whereis('umount')
        try:
            for s in ('/proc', '/dev', '/sys'):
                sdir = self.ROOT_DIR + s
                if not os.path.ismount(sdir):
                    self.dir_create(sdir)
                    self.system_command((mount, '--rbind', s, sdir))
            os.chroot(self.ROOT_DIR)
            os.chdir('/')
            if sinput:
                self.system_input(command, shell=shell, sinput=sinput)
            else:
                self.system_command(command, shell=shell)
        finally:
            os.fchdir(real_root)
            os.chroot('.')
            os.close(real_root)
            for s in ('/proc', '/dev', '/sys'):
                sdir = self.ROOT_DIR + s
                if os.path.ismount(sdir):
                    self.system_command((umount, '-f', '-l', sdir))

    def system_script(self, sfile, function):
        ''' Execute a function from Bash script '''
        if self.python2:
            self.typecheck(sfile, (types.StringTypes))
            self.typecheck(function, (types.StringTypes))

        if self.ROOT_DIR == '/':
            self.system_command((self.whereis('bash'), '-e', '-c', \
                'source %s && %s' % (sfile, function)), cwd=self.ROOT_DIR)
        else:
            stmp = os.path.join(self.ROOT_DIR, 'tmpscript')
            shutil.copy(sfile, stmp)
            try:
                self.system_chroot(('bash', '-e', '-c', \
                    'source /tmpscript && %s' % function))
            finally:
                os.remove(stmp)

    def system_trigger(self, command, shell=False):
        ''' Execute trigger '''
        if self.python2:
            self.typecheck(command, (types.StringType, types.TupleType, types.ListType))
            self.typecheck(shell, (types.BooleanType))

        if self.ROOT_DIR == '/':
            self.system_command(command, shell=shell, cwd=self.ROOT_DIR)
        else:
            self.system_chroot(command, shell=shell)


class Inotify(object):
    ''' Inotify wrapper '''
    def __init__(self):
        self.ACCESS = 0x00000001        # IN_ACCESS
        self.MODIFY = 0x00000002        # IN_MODIFY
        self.ATTRIB = 0x00000004        # IN_ATTRIB
        self.WRITE = 0x00000008         # IN_CLOSE_WRITE
        self.CLOSE = 0x00000010         # IN_CLOSE_NOWRITE
        self.OPEN = 0x00000020          # IN_OPEN
        self.MOVED_FROM = 0x00000040    # IN_MOVED_FROM
        self.MOVED_TO = 0x00000080      # IN_MOVED_TO
        self.CREATE = 0x00000100        # IN_CREATE
        self.DELETE = 0x00000200        # IN_DELETE
        self.DELETE_SELF = 0x00000400   # IN_DELETE_SELF
        self.MOVE_SELF = 0x00000800     # IN_MOVE_SELF
        self.UNMOUNT = 0x00002000       # IN_UNMOUNT
        self.Q_OVERFLOW = 0x00004000    # IN_Q_OVERFLOW
        self.IGNORED = 0x00008000       # IN_IGNORED
        self.ONLYDIR = 0x01000000       # IN_ONLYDIR
        self.DONT_FOLLOW = 0x02000000   # IN_DONT_FOLLOW
        self.MASK_ADD = 0x20000000      # IN_MASK_ADD
        self.ISDIR = 0x40000000         # IN_ISDIR
        self.ONESHOT = 0x80000000       # IN_ONESHOT

        self.watched = {}
        libc = ctypes.util.find_library('c')
        self.libc = ctypes.CDLL(libc, use_errno=True)
        self.fd = self.libc.inotify_init()
        if self.fd == -1:
            raise Exception('Inotify', self.error())

    def __del__(self):
        self.close()

    def error(self):
        ''' Get last error as string '''
        return os.strerror(ctypes.get_errno())

    def event_read(self):
        ''' Read event from the inotify file descriptor '''
        size_int = ctypes.c_int()
        while ioctl(self.fd, FIONREAD, size_int) == -1:
            time.sleep(1)
        size = size_int.value
        if not size:
            return
        data = os.read(self.fd, size)
        deb = 0
        while deb < size:
            fin = deb+16
            wd, mask, cookie, name_len = unpack('iIII', data[deb:fin])
            deb, fin = fin, fin+name_len
            name = unpack('%ds' % name_len, data[deb:fin])
            name = misc.string_encode(name[0]).rstrip('\0')
            deb = fin
            yield wd, mask, cookie, name

    def watch_add(self, path, mask=None, recursive=True):
        ''' Add path to watcher '''
        if not mask:
            mask = self.MODIFY | self.CREATE | self.DELETE
        if recursive and os.path.isdir(path):
            for d in os.listdir(path):
                full = os.path.join(path, d)
                if not os.path.isdir(full):
                    continue
                self.watch_add(misc.string_encode(full), mask)
        wd = self.libc.inotify_add_watch(self.fd, path, mask)
        if wd == -1:
            raise Exception('Inotfiy', self.error())
        self.watched[path] = wd
        return wd

    def watch_remove(self, path):
        ''' Remove path from watcher '''
        if not path in self.watched:
            return
        wd = self.watched[path]
        ret = self.libc.inotify_rm_watch(self.fd, wd)
        if ret == -1:
            raise Exception('Inotify', self.error())
        self.watched.pop(path)

    def watch_list(self):
        ''' Get a list of paths watched '''
        return list(self.watched.keys())

    def watch_loop(self, path, callback, mask=None, recursive=True):
        ''' Start watching for events '''
        self.watch_add(path, mask, recursive)
        while True:
            for wd, mask, cookie, name in self.event_read():
                callback((wd, mask, cookie, name))
            time.sleep(1)

    def close(self):
        ''' Close inotify descriptor '''
        if self.fd:
            os.close(self.fd)

class Magic(object):
    ''' Magic wrapper '''
    def __init__(self, flags=None):
        self.NONE = 0x000000            # No flags
        self.DEBUG = 0x000001           # Turn on debugging
        self.SYMLINK = 0x000002         # Follow symlinks
        self.COMPRESS = 0x000004        # Check inside compressed files
        self.DEVICES = 0x000008         # Look at the contents of devices
        self.MIME = 0x000010            # Return a mime string
        self.MIME_ENCODING = 0x000400   # Return the MIME encoding
        self.CONTINUE = 0x000020        # Return all matches
        self.CHECK = 0x000040           # Print warnings to stderr
        self.PRESERVE_ATIME = 0x000080  # Restore access time on exit
        self.RAW = 0x000100             # Don't translate unprintable chars
        self.ERROR = 0x000200           # Handle ENOENT etc as real errors
        self.NO_CHECK_COMPRESS = 0x001000 # Don't check for compressed files
        self.NO_CHECK_TAR = 0x002000    # Don't check for tar files
        self.NO_CHECK_SOFT = 0x004000   # Don't check magic entries
        self.NO_CHECK_APPTYPE = 0x008000 # Don't check application type
        self.NO_CHECK_ELF = 0x010000    # Don't check for elf details
        self.NO_CHECK_ASCII = 0x020000  # Don't check for ascii files
        self.NO_CHECK_TROFF = 0x040000  # Don't check ascii/troff
        self.NO_CHECK_FORTRAN = 0x080000 # Don't check ascii/fortran
        self.NO_CHECK_TOKENS = 0x100000 # Don't check ascii/tokens

        self.libmagic = ctypes.CDLL('libmagic.so', use_errno=True)
        if not flags:
            flags = self.NONE | self.MIME # | self.NO_CHECK_COMPRESS | self.NO_CHECK_TAR
        self.flags = flags
        self.cookie = self.libmagic.magic_open(self.flags)
        self.libmagic.magic_load(self.cookie, None)

        self._magic_file = self.libmagic.magic_file
        self._magic_file.restype = ctypes.c_char_p
        self._magic_file.argtypes = [ctypes.c_void_p, ctypes.c_char_p]

    def __del__(self):
        if self.cookie and self.libmagic.magic_close:
            self.libmagic.magic_close(self.cookie)

    def error(self):
        ''' Get last error as string '''
        return ctypes.get_errno()

    def get(self, path):
        ''' Get MIME type of path '''
        result = self._magic_file(self.cookie, misc.string_encode(path))
        if not result or result == -1:
            # libmagic 5.09 has a bug where it might fail to identify the
            # mimetype of a file and returns null from magic_file (and
            # likely _buffer), but also does not return an error message.
            if (self.flags & self.MIME):
                return 'application/octet-stream'
            raise Exception(self.error())
        return result

misc = Misc()
