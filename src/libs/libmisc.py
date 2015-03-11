#!/bin/python2

import sys, os, re, tarfile, zipfile, subprocess, shutil, shlex, pwd, inspect
import types, gzip, time, libmagic
if int(sys.version_info[0]) < 3:
    from urlparse import urlparse
    from urllib2 import urlopen
    from urllib2 import Request
    from urllib2 import URLError
    from httplib import BadStatusLine
else:
    import urllib.parse as urlparse
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
        self.CATCH = False

    def typecheck(self, a, b):
        ''' Poor man's variable type checking '''
        # FIXME: implement file, directory, and url type check?
        if not isinstance(a, b):
            line = inspect.currentframe().f_back.f_lineno
            raise(TypeError('Variable is not %s (%d)' % (str(b), line)))

    def whereis(self, program, fallback=True, chroot=False):
        ''' Find full path to executable '''
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

    def ping(self, url='http://www.google.com'):
        ''' Ping URL '''
        self.typecheck(url, (types.StringTypes))

        if self.OFFLINE:
            return
        try:
            p = urlopen(url, timeout=self.TIMEOUT)
            p.close()
            return True
        except (URLError, BadStatusLine):
            return False

    def string_encode(self, string):
        ''' String wrapper to ensure Python3 compat '''
        if int(sys.version_info[0]) >= 3 and isinstance(string, bytes):
            return string.decode('utf-8')
        else:
            return string

    def string_convert(self, string):
        ''' Convert input to string but only if it is not string '''
        if isinstance(string, (list, tuple)):
            return ' '.join(string)
        return string

    def string_unit_guess(self, svar):
        ''' Guess the units to be used by string_unit() '''
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
        self.typecheck(string, (types.StringTypes))
        self.typecheck(string, (types.StringTypes))
        self.typecheck(exact, (types.BooleanType))
        self.typecheck(escape, (types.BooleanType))

        if exact and escape:
            return re.findall('(\\s|^)' + re.escape(string) + '(\\s|$)', \
                self.string_convert(string2))
        elif exact:
            return re.findall('(\\s|^)' + string + '(\\s|$)', \
                self.string_convert(string2))
        elif escape:
            return re.findall(re.escape(string), self.string_convert(string2))
        else:
            return re.findall(string, self.string_convert(string2))

    def url_normalize(self, surl, basename=False):
        ''' Normalize URL, optionally get basename '''
        self.typecheck(surl, (types.StringTypes))
        self.typecheck(basename, (types.BooleanType))

        # http://www.w3schools.com/tags/ref_urlencode.asp
        dspecials = {'%20': ' '}
        sresult = urlparse(surl).path
        for schar in dspecials:
            sresult = sresult.replace(schar, dspecials[schar])
        if basename:
            return os.path.basename(sresult)
        return sresult

    def file_name(self, sfile, basename=True):
        ''' Get name of file without the extension '''
        self.typecheck(sfile, (types.StringTypes))
        self.typecheck(basename, (types.BooleanType))

        if basename:
            return os.path.splitext(os.path.basename(sfile))[0]
        return os.path.splitext(sfile)[0]

    def file_extension(self, sfile):
        ''' Get the extension of file '''
        self.typecheck(sfile, (types.StringTypes))

        return os.path.splitext(sfile)[1].lstrip('.')

    def file_touch(self, sfile):
        ''' Touch a file, making sure it exists '''
        self.typecheck(sfile, (types.StringTypes))

        if not os.path.isfile(sfile):
            self.file_write(sfile, '')

    def file_read(self, sfile):
        ''' Get file content '''
        self.typecheck(sfile, (types.StringTypes))

        rfile = open(sfile, 'rb')
        content = rfile.read()
        rfile.close()
        return self.string_encode(content)

    def file_read_nonblock(self, sfile, ibuffer=1024):
        ''' Get file content non-blocking '''
        self.typecheck(sfile, (types.StringTypes))
        self.typecheck(ibuffer, (types.IntType))

        fd = os.open(sfile, os.O_NONBLOCK)
        content = os.read(fd, ibuffer)
        os.close(fd)
        return content

    def file_readlines(self, sfile):
        ''' Get file content, split by new line, as list '''
        self.typecheck(sfile, (types.StringTypes))

        rfile = open(sfile, 'rb')
        content = rfile.read().splitlines()
        rfile.close()
        return self.string_encode(content)

    def file_write(self, sfile, content, mode='w'):
        ''' Write data to file '''
        self.typecheck(sfile, (types.StringTypes))
        self.typecheck(content, (types.StringTypes))
        self.typecheck(mode, (types.StringTypes))

        self.dir_create(os.path.dirname(sfile))
        wfile = open(sfile, mode)
        wfile.write(content)
        wfile.close()

    def file_write_nonblock(self, sfile, content):
        ''' Write data to file non-blocking (overwrites) '''
        self.typecheck(sfile, (types.StringTypes))
        self.typecheck(content, (types.StringTypes))

        self.dir_create(os.path.dirname(sfile))
        fd = os.open(sfile, os.O_NONBLOCK | os.O_WRONLY)
        os.write(fd, content)
        os.close(fd)

    def file_search(self, string, sfile, exact=False, escape=True):
        ''' Search for string in file '''
        self.typecheck(string, (types.StringTypes))
        self.typecheck(sfile, (types.StringTypes))
        self.typecheck(exact, (types.BooleanType))
        self.typecheck(escape, (types.BooleanType))

        return self.string_search(string, self.file_read(sfile), exact=exact, \
            escape=escape)

    def file_mime(self, sfile):
        ''' Get file type '''
        self.typecheck(sfile, (types.StringTypes))

        # symlinks are not handled properly by magic, on purpose
        # https://github.com/ahupp/python-magic/pull/31
        if os.path.islink(sfile):
            return 'inode/symlink'
        return self.string_encode(libmagic.from_file(sfile, mime=True))

    def file_substitute(self, string, string2, sfile):
        ''' Substitue a string with another in file '''
        self.typecheck(string, (types.StringTypes))
        self.typecheck(string2, (types.StringTypes))
        self.typecheck(sfile, (types.StringTypes))

        self.file_write(sfile, re.sub(string, string2, self.file_read(sfile)))

    def dir_create(self, sdir, demote=''):
        ''' Create directory if it does not exist, including leading paths '''
        self.typecheck(sdir, (types.StringTypes))
        self.typecheck(demote, (types.StringTypes))

        if not os.path.isdir(sdir) and not os.path.islink(sdir):
            # sadly, demoting works only for sub-processes
            if demote:
                self.system_command((self.whereis('mkdir'), '-p', sdir), demote=demote)
            else:
                os.makedirs(sdir)

    def dir_remove(self, sdir):
        ''' Remove directory recursively '''
        self.typecheck(sdir, (types.StringTypes))

        for root, dirs, files in os.walk(sdir):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                if os.path.islink(os.path.join(root, d)):
                    os.unlink(os.path.join(root, d))
        for root, dirs, files in os.walk(sdir, topdown=False):
            for d in dirs:
                s = os.path.join(root, d)
                if os.path.islink(s):
                    os.unlink(s)
                else:
                    os.rmdir(s)
        if os.path.islink(sdir):
            os.unlink(sdir)
        else:
            os.rmdir(sdir)

    def dir_size(self, sdir):
        ''' Get size of directory '''
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

    def list_files(self, sdir, bcross=True):
        ''' Get list of files in directory recursively '''
        self.typecheck(sdir, (types.StringTypes))
        self.typecheck(bcross, (types.BooleanType))

        slist = []
        for root, subdirs, files in os.walk(sdir):
            if not bcross:
                subdirs[:] = [
                    d for d in subdirs
                    if not os.path.ismount(os.path.join(root, d))]
            for sfile in files:
                slist.append(os.path.join(root, sfile))
        return slist

    def list_dirs(self, sdir, bcross=True):
        ''' Get list of directories in directory recursively '''
        self.typecheck(sdir, (types.StringTypes))
        self.typecheck(bcross, (types.BooleanType))

        slist = []
        for root, subdirs, files in os.walk(sdir):
            if not bcross:
                subdirs[:] = [
                    d for d in subdirs
                    if not os.path.ismount(os.path.join(root, d))]
            for d in subdirs:
                slist.append(os.path.join(root, d))
        return slist

    def list_all(self, sdir, bcross=True):
        ''' Get list of files and directories in directory recursively '''
        self.typecheck(sdir, (types.StringTypes))
        self.typecheck(bcross, (types.BooleanType))

        slist = []
        for root, subdirs, files in os.walk(sdir):
            if not bcross:
                subdirs[:] = [
                    d for d in subdirs
                    if not os.path.ismount(os.path.join(root, d))]
            for d in subdirs:
                slist.append(os.path.join(root, d))
            for sfile in files:
                slist.append(os.path.join(root, sfile))
        return slist

    def fetch_request(self, surl, data=None):
        ''' Returns urlopen object, it is NOT closed! '''
        self.typecheck(surl, (types.StringTypes))
        if not data:
            data = {}
        self.typecheck(data, (types.DictType))

        request = Request(surl)
        for item in data:
            request.add_header(item, data[item])
        # SSL verification works OOTB only on Python >= 2.7.9 (officially)
        if sys.version_info[2] >= 9:
            import ssl
            ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            return urlopen(request, timeout=self.TIMEOUT, context=ctx)
        else:
            return urlopen(request, timeout=self.TIMEOUT)

    def fetch_check(self, surl, destination):
        ''' Check if remote has to be downloaded '''
        self.typecheck(surl, (types.StringTypes))
        self.typecheck(destination, (types.StringTypes))

        if self.OFFLINE:
            return True
        elif os.path.isfile(destination):
            rfile = self.fetch_request(surl)
            # not all requests have content-lenght:
            # http://en.wikipedia.org/wiki/Chunked_transfer_encoding
            rsize = rfile.headers.get('Content-Length', '0')
            rfile.close()
            lsize = os.path.getsize(destination)
            rtime = rfile.headers.get('Last-Modified', '0')
            if rtime == '0':
                rtime = rfile.headers.get('Date', '0')
            rtime = time.mktime(time.strptime(rtime,
                '%a, %d %b %Y %H:%M:%S GMT'))
            ltime = os.stat(destination).st_mtime
            if not rtime == ltime or not int(lsize) == int(rsize):
                return False
            return True
        else:
            return False

    def fetch(self, surl, destination, iretry=3, iblock=60):
        ''' Download file, iretry and iblock are passed internally! '''
        self.typecheck(surl, (types.StringTypes))
        self.typecheck(destination, (types.StringTypes))
        self.typecheck(iretry, (types.IntType))
        self.typecheck(iblock, (types.IntType))

        if self.OFFLINE:
            return

        rfile = self.fetch_request(surl)
        self.dir_create(os.path.dirname(destination))

        # not all requests have content-lenght:
        # http://en.wikipedia.org/wiki/Chunked_transfer_encoding
        rsize = rfile.headers.get('Content-Length', '0')
        rtime = rfile.headers.get('Last-Modified', '0')
        if rtime == '0':
            rtime = rfile.headers.get('Date', '0')
        if rsize == '0' or rtime == '0':
            # block until the server is ready to serve the whole file
            rfile.close()
            if not iblock == 0:
                return self.fetch(surl, destination, iretry, iblock-1)
            raise(Exception('Bogus response header from %s, good luck!' % surl))

        rtime = time.mktime(time.strptime(rtime, '%a, %d %b %Y %H:%M:%S GMT'))
        if os.path.exists(destination):
            lsize = str(os.path.getsize(destination))
            ltime = os.stat(destination).st_mtime
            if lsize > rsize or not ltime == rtime:
                lsize = '0'
                os.unlink(destination)
            if rfile.headers.get('Accept-Ranges') == 'bytes':
                # setup new request with custom header
                rfile.close()
                rfile = self.fetch_request(surl, {'Range': 'bytes=%s-' % lsize})
        lfile = open(destination, 'ab')
        cache = 10240
        try:
            # since the local file size changes use persistent units based on
            # remote file size
            units = self.string_unit_guess(rsize)
            while True:
                msg = 'Downloading: %s, %s/%s' % (self.url_normalize(surl, True), \
                    self.string_unit(str(os.path.getsize(destination)), units), \
                    self.string_unit(rsize, units, True))
                sys.stdout.write(msg)
                chunk = rfile.read(cache)
                if not chunk:
                    break
                lfile.write(chunk)
                # in Python 3000 that would be print(blah, end='')
                sys.stdout.write('\r' * len(msg))
                sys.stdout.flush()
        except URLError:
            if not iretry == 0:
                self.fetch(surl, destination, iretry-1, iblock)
            else:
                raise
        finally:
            if os.path.exists(destination):
                os.utime(destination, (rtime, rtime))
            sys.stdout.write('\n')
            lfile.close()
            rfile.close()

    def archive_supported(self, sfile):
        ''' Test if file is archive that can be handled properly '''
        self.typecheck(sfile, (types.StringTypes))

        if os.path.isdir(sfile):
            return False
        if sfile.endswith(('.xz', '.lzma', '.gz')) \
            or tarfile.is_tarfile(sfile) \
            or zipfile.is_zipfile(sfile):
            return True
        return False

    def archive_compress(self, lpaths, sfile, strip):
        ''' Create archive from directory '''
        self.typecheck(lpaths, (types.TupleType, types.ListType))
        self.typecheck(sfile, (types.StringTypes))
        self.typecheck(strip, (types.StringTypes))

        self.dir_create(os.path.dirname(sfile))

        if sfile.endswith(('.bz2', '.tar.gz')):
            tar = tarfile.open(sfile, 'w:' + self.file_extension(sfile))
            for item in lpaths:
                tar.add(item, item.lstrip(strip))
            tar.close()
        elif sfile.endswith('.zip'):
            zipf = zipfile.ZipFile(sfile, mode='w')
            for item in lpaths:
                zipf.write(item, item.lstrip(strip))
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
            # FIXME: strip
            gzipf = gzip.GzipFile(sfile, 'wb')
            for f in lpaths:
                gzipf.writelines(self.file_read(f))
            gzipf.close()

    def archive_decompress(self, sfile, sdir, demote=''):
        ''' Extract archive to directory '''
        self.typecheck(sfile, (types.StringTypes))
        self.typecheck(sdir, (types.StringTypes))
        self.typecheck(demote, (types.StringTypes))

        self.dir_create(sdir)

        # WARNING!!! the -P option is not supported by the
        # Busybox version of `tar`.

        # standard tarfile library locks the filesystem and upon interrupt the
        # filesystem stays locked which is bad. on top of that the tarfile
        # library can not replace files while they are being used thus the
        # external utilities are used for extracting tar archives.
        if sfile.endswith(('.xz', '.lzma')) \
            or tarfile.is_tarfile(sfile) or zipfile.is_zipfile(sfile):
            bsdtar = self.whereis('bsdtar', fallback=False)
            if bsdtar:
                self.system_command((bsdtar, '-xpPf', sfile, '-C', sdir), \
                    demote=demote)
            else:
                self.system_command((self.whereis('tar'), '-xphf', sfile, \
                    '-C', sdir), demote=demote)
        elif sfile.endswith('.gz'):
            gfile = gzip.GzipFile(sfile, 'rb')
            self.file_write(sfile.rstrip('.gz'), gfile.read())
            gfile.close()

    def archive_list(self, sfile):
        ''' Get list of files in archive '''
        self.typecheck(sfile, (types.StringTypes))

        content = []
        if tarfile.is_tarfile(sfile):
            tfile = tarfile.open(sfile)
            content = tfile.getnames()
            tfile.close()
        elif zipfile.is_zipfile(sfile):
            zfile = zipfile.ZipFile(sfile)
            content = zfile.namelist()
            zfile.close()
        elif sfile.endswith(('.xz', '.lzma')):
            content = self.system_output((self.whereis('tar'), \
                '-tf', sfile)).split('\n')
        elif sfile.endswith('.gz'):
            # FIXME: implement gzip listing
            raise(Exception('Gzip listing not implemented yet'))
        return content

    def archive_size(self, star, lpaths):
        ''' Get size of file(s) in Tar archive '''
        self.typecheck(star, (types.StringTypes))
        self.typecheck(lpaths, (types.TupleType, types.ListType))

        sizes = []
        tar = tarfile.open(star, 'r')
        for i in tar.getmembers():
            for sfile in lpaths:
                if i.name == sfile:
                    sizes.append(i.size)
        tar.close()
        return sizes

    def archive_content(self, star, lpaths):
        ''' Get content of file(s) in Tar archive '''
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

    def system_input(self, command, input, shell=False, demote=''):
        ''' Send input to external utility '''
        self.typecheck(command, (types.StringType, types.TupleType, types.ListType))
        self.typecheck(input, (types.StringTypes))
        self.typecheck(shell, (types.BooleanType))
        self.typecheck(demote, (types.StringTypes))

        pipe = subprocess.Popen(command, stdin=subprocess.PIPE, \
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, \
            env={'LC_ALL': 'C'}, shell=shell, preexec_fn=self.system_demote(demote))
        out, err = pipe.communicate(input=input)
        if pipe.returncode != 0:
            raise(Exception('%s %s' % (out, err)))

    def system_scanelf(self, sfile, sformat='#F%n', sflags='', demote=''):
        ''' Get information about ELF files '''
        self.typecheck(sfile, (types.StringTypes))
        self.typecheck(sformat, (types.StringTypes))
        self.typecheck(sflags, (types.StringTypes))
        self.typecheck(demote, (types.StringTypes))

        return self.system_output((self.whereis('scanelf'), '-CBF', \
            sformat, sflags, sfile), demote=demote)

    def system_command(self, command, shell=False, cwd='', catch=False, demote=''):
        ''' Execute system command safely '''
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

    def system_chroot(self, command, shell=False, input=None):
        ''' Execute command in chroot environment '''
        self.typecheck(command, (types.StringType, types.TupleType, types.ListType))
        self.typecheck(shell, (types.BooleanType))

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
            if input:
                self.system_input(command, shell=shell, input=input)
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
        ''' Execute pre/post actions '''
        self.typecheck(sfile, (types.StringTypes))
        self.typecheck(function, (types.StringTypes))

        if self.ROOT_DIR == '/':
            self.system_command((self.whereis('bash'), '-e', '-c', \
                'source ' + sfile + ' && ' + function), cwd=self.ROOT_DIR)
        else:
            stmp = os.path.join(self.ROOT_DIR, 'tmpscript')
            shutil.copy(sfile, stmp)
            try:
                self.system_chroot(('bash', '-e', '-c', \
                    'source /tmpscript && ' + function))
            finally:
                os.remove(stmp)

    def system_trigger(self, command, shell=False):
        ''' Execute trigger '''
        self.typecheck(command, (types.StringType, types.TupleType, types.ListType))
        self.typecheck(shell, (types.BooleanType))

        if self.ROOT_DIR == '/':
            self.system_command(command, shell=shell, cwd=self.ROOT_DIR)
        else:
            self.system_chroot(command, shell=shell)
