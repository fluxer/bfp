#!/usr/bin/python2

'''
A module to handle various tasks fuzz free.

The Misc() class packs a lot - files, directories, urls, archives and even
processes handling.

Magic() is specifiec to file types (MIMEs) recognition via libmagic (part of
file). It is a thin wrapper around it.

Inotify() is another wrapper but around inotify system calls. It can be used
to monitor for file/directory changes on filesystems.

'''

import sys, os, re, tarfile, zipfile, subprocess, shutil, shlex, inspect, json
import types, gzip, bz2, time, ctypes, ctypes.util, getpass, base64, hashlib
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
        self.BUFFER = 10240
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
            exe = '%s/%s' % (path, program)
            # normalize because os.path.join sucks and can't be used in this case
            if chroot and os.path.isfile(os.path.realpath('%s/%s' % (self.ROOT_DIR, exe))):
                return exe
            elif not chroot and os.path.isfile(exe):
                return exe

        if fallback:
            # in the future, fallback will return program and let OSError be
            # raised at higher level, e.g. by subprocess
            raise OSError('Program not found in PATH', program)

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

    def string_unit_guess(self, string):
        ''' Guess the units to be used by string_unit() '''
        if self.python2:
            self.typecheck(string, (types.StringTypes))

        lenght = len(string)
        if lenght > 6:
            return 'Mb'
        elif lenght > 3:
            return 'Kb'
        else:
            return 'b'

    def string_unit(self, string, sunit='Mb', bprefix=False):
        ''' Convert bytes to humar friendly units '''
        if self.python2:
            self.typecheck(string, (types.StringTypes))
            self.typecheck(sunit, (types.StringTypes))
            self.typecheck(bprefix, (types.BooleanType))

        if sunit == 'Mb':
            if bprefix:
                return '%d%s' % (int(string) / (1024 * 1024), 'Mb')
            return int(string) / (1024 * 1024)
        elif sunit == 'Kb':
            if bprefix:
                return '%d%s' % (int(string) / 1024, 'Kb')
            return int(string) / 1024
        else:
            if bprefix:
                return '%d%s' % (int(string), 'b')
            return string

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

    def string_checksum(self, data, smethod='sha256'):
        ''' Return a hex checksum of string '''
        if self.python2:
            self.typecheck(data, (types.StringTypes))
            self.typecheck(smethod, (types.StringTypes))

        return getattr(hashlib, smethod)(data).hexdigest()

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

    def file_read(self, sfile):
        ''' Get file content '''
        if self.python2:
            self.typecheck(sfile, (types.StringTypes))

        rfile = open(sfile, 'rb', self.BUFFER)
        try:
            content = rfile.read()
        finally:
            rfile.close()
        return self.string_encode(content)

    def file_readlines(self, sfile):
        ''' Get file content, split by new line, as list '''
        if self.python2:
            self.typecheck(sfile, (types.StringTypes))

        rfile = open(sfile, 'rb', self.BUFFER)
        try:
            content = rfile.read().splitlines()
        finally:
            rfile.close()
        return self.string_encode(content)

    def file_readsmart(self, sfile):
        ''' Get file content, split by new line, as list ignoring blank and comments '''
        if self.python2:
            self.typecheck(sfile, (types.StringTypes))

        content = []
        for line in self.file_readlines(sfile):
            line = self.string_encode(line.strip())
            if not line or line.startswith('#'):
                continue
            content.append(line)
        return content

    def file_write(self, sfile, content, mode='w'):
        ''' Write data to file safely

            the cool thing about this helper is that it does not dump files if
            it fails to write the file when the mode is "a" (append) '''
        if self.python2:
            self.typecheck(sfile, (types.StringTypes))
            self.typecheck(content, (types.StringTypes))
            self.typecheck(mode, (types.StringTypes))

        self.dir_create(os.path.dirname(sfile))
        original = None
        if os.path.isfile(sfile):
            original = self.file_read(sfile)
        wfile = open(sfile, mode, self.BUFFER)
        try:
            wfile.write(content)
        except:
            if original and not 'a' in mode:
                wfile.write(original)
            raise
        finally:
            wfile.close()

    def file_search(self, string, sfile, exact=False, escape=True):
        ''' Search for string in file '''
        if self.python2:
            self.typecheck(string, (types.StringTypes))
            self.typecheck(sfile, (types.StringTypes))
            self.typecheck(exact, (types.BooleanType))
            self.typecheck(escape, (types.BooleanType))

        return self.string_search(string, self.file_read(sfile), exact=exact, \
            escape=escape)

    def file_mime(self, sfile, bresolve=False, bquick=False):
        ''' Get file type, you should propably use Magic().get() instead '''
        if self.python2:
            self.typecheck(sfile, (types.StringTypes))
            self.typecheck(bresolve, (types.BooleanType))
            self.typecheck(bquick, (types.BooleanType))

        if bresolve:
            sfile = os.path.realpath(sfile)

        if bquick:
            # pre-computed but unreliable MIME types, if you want to add more
            # then please have in mind that the extension may be shared with
            # multiple MIME types and missleading
            if os.path.islink(sfile):
                return 'inode/symlink'
            elif sfile.endswith(('.c', '.h', '.cpp', '.hpp', '.S')):
                return 'text/x-c'
            elif sfile.endswith(('.sh', '.bash')):
                return 'text/x-shellscript'
            elif sfile.endswith('.pl'):
                return 'text/x-perl'
            elif sfile.endswith('.py'):
                return 'text/x-python'
            elif sfile.endswith('.rb'):
                return 'text/x-ruby'
            elif sfile.endswith('.awk'):
                return 'text/x-awk'
            elif sfile.endswith('.html'):
                return 'text/html'
            elif sfile.endswith(('.txt', '.desktop')):
                return 'text/plain'
            elif sfile.endswith('/Makefile'):
                return 'text/x-makefile'
            elif sfile.endswith('.bmp'):
                return 'image/bmp'
            elif sfile.endswith('.gif'):
                return 'image/gif'
            elif sfile.endswith(('.jpeg', '.jpg')):
                return 'image/jpeg'
            elif sfile.endswith('.png'):
                return 'image/png'
            elif sfile.endswith('.svg'):
                return 'image/svg+xml'
            elif sfile.endswith('.mo'):
                # GNU message catalog
                return 'application/octet-stream'
            elif sfile.endswith('.xml'):
                return 'application/xml'
            elif sfile.endswith('.xhtml'):
                return 'application/xhtml+xml'

        return self.string_encode(self.magic.get(sfile))

    def file_substitute(self, string, string2, sfile):
        ''' Substitue a string with another in file '''
        if self.python2:
            self.typecheck(string, (types.StringTypes))
            self.typecheck(string2, (types.StringTypes))
            self.typecheck(sfile, (types.StringTypes))

        self.file_write(sfile, re.sub(string, string2, self.file_read(sfile)))

    def file_checksum(self, sfile, smethod='sha256'):
        ''' Return a hex checksum of file

            the reason to use this method would be if you wan to ensure that
            big files are read in chunks (according to self.BUFFER) preventing
            OOM kill, safety first '''
        if self.python2:
            self.typecheck(sfile, (types.StringTypes))
            self.typecheck(smethod, (types.StringTypes))

        return self.string_checksum(misc.string_encode(self.file_read(sfile)), smethod)

    def json_read(self, sfile):
        ''' Get JSON file content '''
        if self.python2:
            self.typecheck(sfile, (types.StringTypes))

        content = None
        f = open(sfile, 'r', self.BUFFER)
        try:
            content = json.load(f)
        finally:
            f.close()
        return content

    def json_write(self, sfile, content, mode='w'):
        ''' Write data to JSON file '''
        if self.python2:
            self.typecheck(sfile, (types.StringTypes))
            # self.typecheck(content, (types.StringTypes))
            self.typecheck(mode, (types.StringTypes))

        f = open(sfile, mode, self.BUFFER)
        try:
            json.dump(content, f, indent=4)
        finally:
            f.close()

    def gpg_findsig(self, sfile, bensure=True):
        ''' Attempts to guess the signature for local file '''
        if self.python2:
            self.typecheck(sfile, (types.StringTypes))
            self.typecheck(bensure, (types.BooleanType))

        sig1 = '%s.sig' % sfile
        sig2 = '%s.asc' % sfile
        sig3 = '%s.sign' % self.file_name(sfile, False)
        if os.path.isfile(sig1):
            return sig1
        elif os.path.isfile(sig2):
            return sig2
        elif not sfile.endswith('.sign') and os.path.isfile(sig3):
            return sig3
        elif bensure:
            return sig1

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
        gpg = self.whereis('gpg2', False)
        if not gpg:
            gpg = self.whereis('gpg')
        cmd = [gpg, '--homedir', self.GPG_DIR]
        for server in lservers:
            cmd.extend(('--keyserver', server))
        try:
            checkcmd = []
            checkcmd.extend(cmd)
            checkcmd.append('--list-public-keys')
            checkcmd.extend(lkeys)
            self.system_command(checkcmd)
            # if it does not fail refresh the keys
            cmd.append('--refresh-keys')
        except subprocess.CalledProcessError:
            # otherwise (presumably) the key is not in the keyring
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
        gpg = self.whereis('gpg2', False)
        if not gpg:
            gpg = self.whereis('gpg')
        cmd = [gpg, '--homedir', self.GPG_DIR]
        if skey:
            cmd.extend(('--default-key', skey))
        cmd.extend(('--yes', '--no-tty', '--passphrase-fd', '0'))
        cmd.extend(('--detach-sig', '--sign', '--batch', sfile))
        if not self.SIGNPASS:
            self.SIGNPASS = base64.encodestring(self.getpass(sprompt))
        self.system_communicate(cmd, sinput=base64.decodestring(self.SIGNPASS))

    def gpg_verify(self, sfile, ssignature=None):
        ''' Verify file PGP signature via GnuPG '''
        if self.python2:
            self.typecheck(sfile, (types.StringTypes))
            self.typecheck(ssignature, (types.NoneType, types.StringTypes))

        self.dir_create(self.GPG_DIR, ipermissions=0o700)
        gpg = self.whereis('gpg2', False)
        if not gpg:
            gpg = self.whereis('gpg')
        if not ssignature:
            ssignature = self.gpg_findsig(sfile)
        shell = False
        if ssignature.endswith('.sign'):
            # exception for no gain, get piped!
            shell = True
            if sfile.endswith('.xz'):
                cmd = '%s -cdk ' % misc.whereis('unxz')
            elif sfile.endswith('.bz2'):
                cmd = '%s -cdk ' % misc.whereis('bunzip')
            elif sfile.endswith('.gz'):
                cmd = '%s -ck ' % misc.whereis('gunzip')
            else:
                raise(Exception('In memory verification does not support', sfile))
            cmd = '%s %s | %s --homedir %s --verify --batch %s -' % \
                (cmd, sfile, gpg, self.GPG_DIR, ssignature)
        else:
            cmd = [gpg, '--homedir', self.GPG_DIR]
            cmd.extend(('--verify', '--batch', ssignature, sfile))
        self.system_command(cmd, shell=shell)

    def dir_create(self, sdir, ipermissions=0):
        ''' Create directory if it does not exist, including leading paths

        since Python 3.2 os.makedirs accepts exist_ok argument so you may use
        it instead of this method, however it applies permissions on all
        directories created - this one does not. it sets ipermissions on the
        last directory of the path passed, for the leading paths the default
        mask (0o777 usually) is used '''
        if self.python2:
            self.typecheck(sdir, (types.StringTypes))
            self.typecheck(ipermissions, (types.IntType))

        if not os.path.isdir(sdir) and not os.path.islink(sdir):
            os.makedirs(sdir)
        if ipermissions:
            os.chmod(sdir, ipermissions)

    def dir_remove(self, sdir):
        ''' Remove directory recursively

            this method exists only because in some older versions of Python
            shutil.rmtree() does not handle symlinks properly. If you have
            Python 2.7.9 >= use shutil.rmtree() instead '''
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
                    if not os.path.ismount('%s/%s' % (root, d))]
            for sfile in files:
                slist.append('%s/%s' % (root, sfile))
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
                    if not os.path.ismount('%s/%s' % (root, d))]
            for d in subdirs:
                slist.append('%s/%s' % (root, d))
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
                    if not os.path.ismount('%s/%s' % (root, d))]
            for d in subdirs:
                slist.append('%s/%s' % (root, d))
            for sfile in files:
                slist.append('%s/%s' % (root, sfile))
        return slist

    def url_supported(self, surl, bvcs=True):
        ''' Check if URL is supported by the fetcher '''
        if self.python2:
            self.typecheck(surl, (types.StringTypes))
            self.typecheck(bvcs, (types.BooleanType))

        startprotocols = ['http://', 'https://', 'ftp://', 'ftps://']
        endprotocols = []
        if bvcs:
            startprotocols.extend(('git://', 'ssh://', 'rsync://', 'svn://'))
            endprotocols.extend(('.git', '.svn'))
        if surl.startswith(tuple(startprotocols)):
            return True
        elif surl.endswith(tuple(endprotocols)):
            return True
        return False

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
                r = self.fetch_request(url)
                r.close()
                return True
            except (URLError, BadStatusLine):
                pass
        return False

    def fetch_request(self, surl, data=None):
        ''' Returns urlopen object, it is NOT closed!

            when supported, SSL context is set to secure the request '''
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
        ''' Download file, iretry is passed internally!

            resume, https and (not so much) pretty printing during the download
            process is all that it can do for you '''
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
        lfile = open(destination, 'ab', self.BUFFER)
        try:
            # since the local file size changes use persistent units based on
            # remote file size (which is not much of persistent when the
            # transfer is chunked, doh! proper content-lenght _may_ be sent
            # on the next request but that's is too much to ask for from
            # the server and internet provider)
            units = self.string_unit_guess(rsize)
            while True:
                msg = 'Downloading: %s, %s/%s' % (self.url_normalize(surl, True), \
                    self.string_unit(str(os.path.getsize(destination)), units), \
                    self.string_unit(rsize, units, True))
                sys.stdout.write(msg)
                chunk = rfile.read(self.BUFFER)
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
        ''' Clone/pull Git repository

            a few things to notice - only the last checkout of the repo is
            requested and a fake user.name and user.email are set so that
            `git pull' does not fail '''
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

        # the .svn url extension is fake made up for the sake of the fetcher
        # to be able to recognize the protocol, strip it
        surl = surl.rstrip('.svn')
        svn = self.whereis('svn')
        if os.path.isdir('%s/.svn' % destination):
            self.system_command((svn, 'up'), cwd=destination)
        else:
            self.system_command((svn, 'co', '--depth=infinity', surl, \
                destination))

    def fetch_rsync(self, surl, destination):
        ''' Sync rsync path '''
        if self.python2:
            self.typecheck(surl, (types.StringTypes))
            self.typecheck(destination, (types.StringTypes))

        if self.OFFLINE:
            return

        rsync = self.whereis('rsync')
        self.system_command((rsync, '-cHpE', destination))

    def fetch(self, surl, destination, lmirrors=None, ssuffix='', iretry=3):
        ''' Download something from mirror if possible, iretry is passed
            internally!

            it supports SVN, Git, rsync and plain http(s)/ftp(s) URLs. if it
            is not able to recognize the protocol properly for you use
            fetch_plain() or whatever you need directly. '''
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
            elif surl.startswith('svn://') or sbase.endswith('.svn'):
                self.fetch_svn(surl, destination)
            elif surl.startswith('rsync://'):
                self.fetch_rsync(surl, destination)
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
        ''' Test if file is archive that can be handled properly

            the following applies to all archive methods:
            aside from the standard Bzip2, gzip, Tar and Zip formats they
            support XZ/LZMA '''
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

    def archive_compress(self, lpaths, sfile, strip, ilevel=9):
        ''' Create archive from list of files and/or directories, ilevel
            is compression level integer between 0 and 9 that applies only to
            tar, gzip and bzip2 archives '''
        if self.python2:
            self.typecheck(lpaths, (types.TupleType, types.ListType))
            self.typecheck(sfile, (types.StringTypes))
            self.typecheck(strip, (types.StringTypes))
            self.typecheck(ilevel, (types.IntType))

        self.dir_create(os.path.dirname(sfile))

        if sfile.endswith(('tar.bz2', '.tar.gz')):
            tarf = tarfile.open(sfile, 'w:' + self.file_extension(sfile), compresslevel=ilevel)
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
            gzipf = gzip.GzipFile(sfile, 'wb', compresslevel=ilevel)
            gzipf.write(self.string_encode(self.file_read(lpaths[0])))
            gzipf.close()
        elif sfile.endswith('.bz2'):
            if len(lpaths) > 1:
                raise Exception('BZip', 'format can hold only single file')
            bzipf = bz2.BZ2File(sfile, 'wb', compresslevel=ilevel)
            bzipf.write(self.string_encode(self.file_read(lpaths[0])))
            bzipf.close()

    def archive_decompress(self, sfile, sdir):
        ''' Extract archive to directory '''
        if self.python2:
            self.typecheck(sfile, (types.StringTypes))
            self.typecheck(sdir, (types.StringTypes))

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
                self.system_command((bsdtar, '-xpPf', sfile, '-C', sdir))
            else:
                self.system_command((self.whereis('tar'), '-xphf', sfile, \
                    '-C', sdir))
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
                for i in tfile:
                    if not i.isdir():
                        content.append(i.name)
            finally:
                tfile.close()
        elif zipfile.is_zipfile(sfile):
            zfile = zipfile.ZipFile(sfile)
            content = zfile.namelist()
            zfile.close()
        elif smime == 'application/x-xz' or smime == 'application/x-lzma':
            bsdtar = self.whereis('bsdtar', fallback=False)
            if bsdtar:
                for line in self.system_communicate((bsdtar, '-tpf', \
                    sfile)).splitlines():
                    content.append(line.lstrip('./'))
            else:
                for line in self.system_communicate((self.whereis('tar'), \
                    '-tf', sfile)).splitlines():
                    content.append(line.lstrip('./'))
        elif smime == 'application/x-gzip':
            content = self.file_name(sfile, True).split()
        elif smime == 'application/x-bzip2':
            content = self.file_name(sfile, True).split()
        return content

    def system_communicate(self, command, shell=False, cwd=None, sinput=None):
        ''' Get output and optionally send input to external utility

            it resets the environment and sets LC_ALL to "C" to ensure locales
            are not respected, passing input is possible if sinput is different
            than None. if something goes wrong you get standard output (stdout)
            and standard error (stderr) as an Exception '''
        if self.python2:
            self.typecheck(command, (types.StringType, types.TupleType, types.ListType))
            self.typecheck(sinput, (types.NoneType, types.StringTypes))
            self.typecheck(shell, (types.BooleanType))
            self.typecheck(cwd, (types.NoneType, types.StringTypes))
            self.typecheck(sinput, (types.NoneType, types.StringTypes))

        if not cwd:
            cwd = self.dir_current()
        elif not os.path.isdir(cwd):
            cwd = '/'
        if isinstance(command, str) and not shell:
            command = shlex.split(command)
        pipe = subprocess.Popen(command, stdin=subprocess.PIPE, \
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, \
            env={'LC_ALL': 'C'}, shell=shell, cwd=cwd)
        out, err = pipe.communicate(input=sinput)
        if pipe.returncode != 0:
            raise(Exception('%s %s' % (out, err)))
        return self.string_encode(out.strip())

    def system_scanelf(self, sfile, sformat='#F%n', sflags=''):
        ''' Get information about ELF files '''
        if self.python2:
            self.typecheck(sfile, (types.StringTypes))
            self.typecheck(sformat, (types.StringTypes))
            self.typecheck(sflags, (types.StringTypes))

        return self.system_communicate((self.whereis('scanelf'), '-yCBF', \
            sformat, sflags, sfile))

    def system_command(self, command, shell=False, cwd=''):
        ''' Execute system command safely

            ensuring current directory is something that exists, handle string
            commands properly for subprocess and if something goes wrong you
            can get standard error (stderr) as an Exception. the last one exists
            for consumers that need more than: "Command failed, exit status 1" '''
        if self.python2:
            self.typecheck(command, (types.StringType, types.TupleType, types.ListType))
            self.typecheck(shell, (types.BooleanType))
            self.typecheck(cwd, (types.StringTypes))

        if not cwd:
            cwd = self.dir_current()
        elif not os.path.isdir(cwd):
            cwd = '/'
        if isinstance(command, str) and not shell:
            command = shlex.split(command)
        stderr = None
        if self.CATCH:
            stderr = subprocess.PIPE
        pipe = subprocess.Popen(command, stderr=stderr, shell=shell, cwd=cwd)
        pipe.wait()
        if pipe.returncode != 0:
            if self.CATCH:
                raise(Exception(pipe.communicate()[1].strip()))
            raise(subprocess.CalledProcessError(pipe.returncode, command))

    def system_chroot(self, command, shell=False, sinput=None):
        ''' Execute command in chroot environment '''
        if self.python2:
            self.typecheck(command, (types.StringType, types.TupleType, types.ListType))
            self.typecheck(shell, (types.BooleanType))
            self.typecheck(sinput, (types.NoneType, types.StringTypes))

        # prevent stupidity
        if self.ROOT_DIR == '/':
            return

        mount = self.whereis('mount')
        umount = self.whereis('umount')
        chroot = self.whereis('chroot')
        if isinstance(command, str):
            command = '%s %s %s' % (chroot, self.ROOT_DIR, command)
        elif isinstance(command, list):
            command.insert(0, chroot)
            command.insert(1, self.ROOT_DIR)
        elif isinstance(command, tuple):
            mycommand = [chroot, self.ROOT_DIR]
            mycommand.extend(command)
            command = mycommand
        try:
            for s in ('/proc', '/dev', '/dev/pts', '/dev/shm', '/sys'):
                sdir = '%s%s' % (self.ROOT_DIR, s)
                if os.path.isdir(s) and not os.path.ismount(sdir):
                    self.dir_create(sdir)
                    self.system_command((mount, '--bind', s, sdir))
            if sinput:
                self.system_communicate(command, shell=shell, sinput=sinput)
            else:
                self.system_command(command, shell=shell)
        finally:
            for s in ('/proc', '/dev', '/dev/pts', '/dev/shm', '/sys'):
                sdir = '%s%s' % (self.ROOT_DIR, s)
                if os.path.ismount(sdir):
                    self.system_command((umount, '-f', '-l', sdir))

    def system_script(self, sfile, function):
        ''' Execute a function from Bash script respecting self.ROOT_DIR '''
        if self.python2:
            self.typecheck(sfile, (types.StringTypes))
            self.typecheck(function, (types.StringTypes))

        if self.ROOT_DIR == '/':
            self.system_command((self.whereis('bash'), '-e', '-c', \
                'source %s && %s' % (sfile, function)), cwd=self.ROOT_DIR)
        else:
            stmp = '%s/tmpscript' % self.ROOT_DIR
            shutil.copy(sfile, stmp)
            try:
                self.system_chroot(('bash', '-e', '-c', \
                    'source /tmpscript && %s' % function))
            finally:
                os.remove(stmp)

    def system_trigger(self, command, shell=False):
        ''' Execute trigger

            that's a shortcur for a conditional chroot command depending
            on self.ROOT_DIR '''
        if self.python2:
            self.typecheck(command, (types.StringType, types.TupleType, types.ListType))
            self.typecheck(shell, (types.BooleanType))

        if self.ROOT_DIR == '/':
            self.system_command(command, shell=shell, cwd='/')
        else:
            self.system_chroot(command, shell=shell)


class Inotify(object):
    ''' Inotify wrapper '''
    def __init__(self):
        self.ACCESS = 0x00000001        # IN_ACCESS
        self.MODIFY = 0x00000002        # IN_MODIFY
        self.ATTRIB = 0x00000004        # IN_ATTRIB
        self.CLOSE_WRITE = 0x00000008   # IN_CLOSE_WRITE
        self.CLOSE_NOWRITE = 0x00000010 # IN_CLOSE_NOWRITE
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
        self.EXCL_UNLINK = 0x04000000   # IN_EXCL_UNLINK
        self.MASK_ADD = 0x20000000      # IN_MASK_ADD
        self.ISDIR = 0x40000000         # IN_ISDIR
        self.ONESHOT = 0x80000000       # IN_ONESHOT

        # sysctl -n fs.inotify.max_user_watches
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

    def watch_add(self, path, mask=None):
        ''' Add path to watcher '''
        if not mask:
            mask = self.MODIFY | self.CREATE | self.DELETE
        wd = self.libc.inotify_add_watch(self.fd, misc.string_encode(path), mask)
        if wd < 0:
            raise Exception('Inotfiy', self.error())
        self.watched[path] = wd
        return wd

    def watch_remove(self, path):
        ''' Remove path from watcher '''
        if not path in self.watched:
            return
        wd = self.watched[path]
        ret = self.libc.inotify_rm_watch(self.fd, wd)
        if ret < 0:
            raise Exception('Inotify', self.error())
        self.watched.pop(path)

    def watch_list(self):
        ''' Get a list of paths watched '''
        return list(self.watched.keys())

    def watch_loop(self, paths, callback, mask=None):
        ''' Start watching for events '''
        for path in paths:
            self.watch_add(path, mask)
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
        self.MIME_TYPE = 0x000010       # Return the MIME type
        self.CONTINUE = 0x000020        # Return all matches
        self.CHECK = 0x000040           # Print warnings to stderr
        self.PRESERVE_ATIME = 0x000080  # Restore access time on exit
        self.RAW = 0x000100             # Don't translate unprintable chars
        self.ERROR = 0x000200           # Handle ENOENT etc as real errors
        self.MIME_ENCODING = 0x000400   # Return the MIME encoding
        self.MIME = self.MIME_TYPE | self.MIME_ENCODING
        self.APPLE = 0x000800           # Return the Apple creator and type
        self.NO_CHECK_COMPRESS = 0x001000 # Don't check for compressed files
        self.NO_CHECK_TAR = 0x002000    # Don't check for tar files
        self.NO_CHECK_SOFT = 0x004000   # Don't check magic entries
        self.NO_CHECK_APPTYPE = 0x008000 # Don't check application type
        self.NO_CHECK_ELF = 0x010000    # Don't check for elf details
        self.NO_CHECK_TEXT = 0x020000   # Don't check for text files
        self.NO_CHECK_CDF = 0x040000    # Don't check for cdf files
        self.NO_CHECK_TOKENS = 0x100000 # Don't check ascii/tokens
        self.NO_CHECK_ENCODING = 0x200000 # Don't check text encodings
        self.NO_CHECK_BUILTIN = self.NO_CHECK_COMPRESS | self.NO_CHECK_TAR | \
            self.NO_CHECK_SOFT | self.NO_CHECK_APPTYPE | self.NO_CHECK_ELF | \
            self.NO_CHECK_TEXT | self.NO_CHECK_CDF | self.NO_CHECK_TOKENS | \
            self.NO_CHECK_ENCODING

        self.libmagic = ctypes.CDLL('libmagic.so', use_errno=True)
        if not flags:
            flags = self.NONE | self.MIME_TYPE | self.PRESERVE_ATIME | \
            self.NO_CHECK_ENCODING # | self.NO_CHECK_COMPRESS | self.NO_CHECK_TAR
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
            if (self.flags & self.MIME_TYPE):
                return 'application/octet-stream'
            raise Exception(self.error())
        return result

misc = Misc()
