#!/bin/python2

import sys, os, re, tarfile, zipfile, subprocess, shutil, shlex, pwd, inspect
import libmagic
if sys.version < '3':
    from urlparse import urlparse
    from urllib2 import urlopen
    from urllib2 import URLError
    from urllib2 import urlopen
    from httplib import BadStatusLine
else:
    import urllib.parse as urlparse
    from urllib.error import URLError
    from urllib.request import urlopen
    from http.client import BadStatusLine


class Misc(object):
    ''' Various methos for every-day usage '''
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
            raise(TypeError('Variable is not ' + str(b) + ' (' + str(line) + ')'))

    def whereis(self, program, fallback=True, chroot=False):
        ''' Find full path to executable '''
        self.typecheck(program, str)
        self.typecheck(fallback, bool)
        self.typecheck(chroot, bool)

        program = os.path.basename(program)
        for path in os.environ.get('PATH', '/bin:/usr/bin').split(':'):
            if chroot:
                path = self.ROOT_DIR + path
            exe = os.path.join(path, program)
            if os.path.isfile(exe):
                return exe
        if fallback:
            # if only the OSError exception was a bit more robust. in the
            # future, fallback will return program and let OSError be raised
            # at higher level
            raise OSError('Program not found in PATH', program)
        return None

    def ping(self, url='http://www.google.com'):
        ''' Ping URL '''
        self.typecheck(url, str)

        if self.OFFLINE:
            return
        try:
            p = urlopen(url, timeout=self.TIMEOUT)
            p.close()
            return True
        except (URLError, BadStatusLine):
            return False

    def version(self, variant):
        ''' Convert input to tuple suitable for version comparison '''
        # if None is passed, e.g. on invalid remote target, the split will fail
        if not variant:
            return ()
        self.typecheck(variant, str)
        return tuple([int(x) for x in variant.split('.') if x.isdigit()])

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
        self.typecheck(svar, str)

        lenght = len(svar)
        if lenght > 7:
            return 'Mb'
        elif lenght > 4:
            return 'Kb'
        else:
            return 'b'

    def string_unit(self, svar, sunit='Mb', bprefix=False):
        ''' Convert bytes to humar friendly units '''
        self.typecheck(svar, str)
        self.typecheck(sunit, str)
        self.typecheck(bprefix, bool)

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
        self.typecheck(string, str)
        self.typecheck(string, str)
        self.typecheck(exact, bool)
        self.typecheck(escape, bool)

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
        # http://www.w3schools.com/tags/ref_urlencode.asp
        self.typecheck(surl, str)
        self.typecheck(basename, bool)

        dspecials = {'%20': ' '}
        sresult = urlparse(surl).path
        for schar in dspecials:
            sresult = sresult.replace(schar, dspecials[schar])
        if basename:
            return os.path.basename(sresult)
        return sresult

    def file_name(self, sfile, basename=True):
        ''' Get name of file without the extension '''
        self.typecheck(sfile, str)
        self.typecheck(basename, bool)

        if basename:
            return os.path.splitext(os.path.basename(sfile))[0]
        return os.path.splitext(sfile)[0]

    def file_extension(self, sfile):
        ''' Get the extension of file '''
        self.typecheck(sfile, str)

        return os.path.splitext(sfile)[1].lstrip('.')

    def file_touch(self, sfile):
        ''' Touch a file, making sure it exists '''
        self.typecheck(sfile, str)

        if not os.path.isfile(sfile):
            self.file_write(sfile, '')

    def file_read(self, sfile):
        ''' Get file content '''
        self.typecheck(sfile, str)

        rfile = open(sfile, 'rb')
        content = rfile.read()
        rfile.close()
        return self.string_encode(content)

    def file_read_nonblock(self, sfile, ibuffer=1024):
        ''' Get file content non-blocking '''
        self.typecheck(sfile, str)
        self.typecheck(ibuffer, int)

        fd = os.open(sfile, os.O_NONBLOCK)
        content = os.read(fd, sbuffer)
        os.close(fd)
        return content

    def file_readlines(self, sfile):
        ''' Get file content, split by new line, as list '''
        self.typecheck(sfile, str)

        rfile = open(sfile, 'rb')
        content = rfile.read().splitlines()
        rfile.close()
        return self.string_encode(content)

    def file_write(self, sfile, content, mode='w'):
        ''' Write data to file '''
        self.typecheck(sfile, str)
        self.typecheck(content, str)
        self.typecheck(mode, str)

        self.dir_create(os.path.dirname(sfile))
        wfile = open(sfile, mode)
        wfile.write(content)
        wfile.close()

    def file_write_nonblock(self, sfile, content):
        ''' Write data to file non-blocking (overwrites) '''
        self.typecheck(sfile, str)
        self.typecheck(content, str)

        self.dir_create(os.path.dirname(sfile))
        fd = os.open(sfile, os.O_NONBLOCK | os.O_WRONLY)
        os.write(fd, content)
        os.close(fd)

    def file_search(self, string, sfile, exact=False, escape=True):
        ''' Search for string in file '''
        self.typecheck(string, str)
        self.typecheck(sfile, str)
        self.typecheck(exact, bool)
        self.typecheck(escape, bool)

        return self.string_search(string, self.file_read(sfile), exact=exact, \
            escape=escape)

    def file_mime(self, sfile):
        ''' Get file type '''
        self.typecheck(sfile, str)

        # symlinks are not handled properly by magic, on purpose
        # https://github.com/ahupp/python-magic/pull/31
        if os.path.islink(sfile):
            return 'inode/symlink'
        return self.string_encode(libmagic.from_file(sfile, mime=True))

    def file_substitute(self, string, string2, sfile):
        ''' Substitue a string with another in file '''
        self.typecheck(string, str)
        self.typecheck(string2, str)
        self.typecheck(sfile, str)

        self.file_write(sfile, re.sub(string, string2, self.file_read(sfile)))

    def dir_create(self, sdir, demote=''):
        ''' Create directory if it does not exist, including leading paths '''
        self.typecheck(sdir, (str, unicode))
        self.typecheck(demote, str)

        if not os.path.isdir(sdir) and not os.path.islink(sdir):
            # sadly, demoting works only for sub-processes
            if demote:
                self.system_command((self.whereis('mkdir'), '-p', sdir), demote=demote)
            else:
                os.makedirs(sdir)

    def dir_remove(self, sdir):
        ''' Remove directory recursively '''
        self.typecheck(sdir, str)

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
        self.typecheck(sdir, str)

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

    def list_files(self, sdir, cross=True):
        ''' Get list of files in directory recursively '''
        self.typecheck(sdir, str)
        self.typecheck(cross, bool)

        slist = []
        for root, subdirs, files in os.walk(sdir):
            if not cross:
                subdirs[:] = [
                    d for d in subdirs
                    if not os.path.ismount(os.path.join(root, d))]
            for sfile in files:
                slist.append(os.path.join(root, sfile))
        return slist

    def list_dirs(self, sdir, cross=True):
        ''' Get list of directories in directory recursively '''
        self.typecheck(sdir, str)
        self.typecheck(cross, bool)

        slist = []
        for root, subdirs, files in os.walk(sdir):
            if not cross:
                subdirs[:] = [
                    d for d in subdirs
                    if not os.path.ismount(os.path.join(root, d))]
            for d in subdirs:
                slist.append(os.path.join(root, d))
        return slist

    def list_all(self, sdir, cross=True):
        ''' Get list of files and directories in directory recursively '''
        self.typecheck(sdir, str)
        self.typecheck(cross, bool)

        slist = []
        for root, subdirs, files in os.walk(sdir):
            if not cross:
                subdirs[:] = [
                    d for d in subdirs
                    if not os.path.ismount(os.path.join(root, d))]
            for d in subdirs:
                slist.append(os.path.join(root, d))
            for sfile in files:
                slist.append(os.path.join(root, sfile))
        return slist

    def fetch_check(self, surl, destination):
        ''' Check if remote file and local file sizes are equal '''
        self.typecheck(surl, (str, unicode))
        self.typecheck(destination, (str, unicode))

        # not all requests can get content-lenght , this means that there is
        # no way to tell if the archive is corrupted (checking if size == 0 is
        # not enough) so the source is re-feteched

        if self.OFFLINE:
            return True
        elif os.path.isfile(destination):
            local_size = os.path.getsize(destination)
            rfile = urlopen(surl, timeout=self.TIMEOUT)
            remote_size = rfile.headers.get('content-length')
            rfile.close()

            if not remote_size:
                return False
            elif int(local_size) == int(remote_size):
                return True
        else:
            return False

    def fetch(self, surl, destination, iretry=3):
        ''' Download file using internal library, retry is passed internally! '''
        self.typecheck(surl, (str, unicode))
        self.typecheck(destination, (str, unicode))
        self.typecheck(iretry, int)

        if self.OFFLINE:
            return

        # SSL verification works OOTB only on Python >= 2.7.9 (officially)
        if sys.version_info[2] >= 9:
            import ssl
            ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            rfile = urlopen(surl, timeout=self.TIMEOUT, context=ctx)
        else:
            rfile = urlopen(surl, timeout=self.TIMEOUT)
        self.dir_create(os.path.dirname(destination))

        # same exception as in fetch_check(), the beaty of the 'net:
        # http://en.wikipedia.org/wiki/Chunked_transfer_encoding
        # even a simple hack to waint until 'Transfer-Encoding' goes
        # away and the server is ready to serve the file is not enough
        # for GitHub, maybe others too. as such an ugly workaround is
        # to set the final size to 0
        rsize = rfile.headers.get('content-length', '0')
        mode = 'wb'
        if os.path.exists(destination) and rfile.headers.get('Accept-Ranges'):
            rfile.headers['Range'] = 'bytes=%s-%s' % (os.path.getsize(destination), rsize)
            mode = 'ab'

        output = open(destination, mode)
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
                output.write(chunk)
                # in Python 3000 that would be print(blah, end='')
                sys.stdout.write('\r' * len(msg))
                sys.stdout.flush()
        except URLError:
            if not iretry == 0:
                self.fetch(surl, destination, iretry-1)
            else:
                raise
        finally:
            sys.stdout.write('\n')
            output.close()
            rfile.close()

    def archive_supported(self, sfile):
        ''' Test if file is archive that can be handled properly '''
        self.typecheck(sfile, str)

        if os.path.isdir(sfile):
            return False
        if sfile.endswith(('.xz', '.lzma', '.gz')) \
            or tarfile.is_tarfile(sfile) \
            or zipfile.is_zipfile(sfile):
            return True
        return False

    def archive_compress(self, variant, sfile, strip):
        ''' Create archive from directory '''
        self.typecheck(variant, (str, list, tuple))
        self.typecheck(sfile, str)
        self.typecheck(strip, str)

        self.dir_create(os.path.dirname(sfile))
        if isinstance(variant, str):
            variant = [variant]

        if sfile.endswith(('.bz2', '.gz')):
            tar = tarfile.open(sfile, 'w:' + self.file_extension(sfile))
            for item in variant:
                tar.add(item, item.lstrip(strip))
            tar.close()
        elif sfile.endswith('.zip'):
            zipf = zipfile.ZipFile(sfile, mode='w')
            for item in variant:
                zipf.write(item, item.lstrip(strip))
            zipf.close()
        elif sfile.endswith(('.xz', '.lzma')):
            # FIXME: implement lzma/xz compression
            raise(Exception('LZMA/XZ compression not implemented yet'))

    def archive_decompress(self, sfile, sdir, demote=''):
        ''' Extract archive to directory '''
        self.typecheck(sfile, str)
        self.typecheck(sdir, str)
        self.typecheck(demote, str)

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
                self.system_command((bsdtar, '-xpPf', sfile, '-C', sdir), demote=demote)
            else:
                self.system_command((self.whereis('tar'), '-xphf', sfile, '-C', sdir), demote=demote)
        elif sfile.endswith('.gz'):
            # FIXME: implement gzip decompression
            raise(Exception('Gzip decompression not implemented yet'))

    def archive_list(self, sfile):
        ''' Get list of files in archive '''
        self.typecheck(sfile, str)

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

    def archive_size(self, star, sfile):
        ''' Get size of file in archive '''
        self.typecheck(star, str)
        self.typecheck(sfile, str)

        size = 0
        tar = tarfile.open(star, 'r')
        for i in tar.getmembers():
            if i.name == sfile:
                size = i.size
                break
        tar.close()
        return size

    def system_demote(self, suser):
        ''' Change priviledges to different user, returns function pointer! '''
        self.typecheck(suser, str)

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

    def system_output(self, command, shell=False, demote=''):
        ''' Get output of external utility '''
        self.typecheck(command, (str, list, tuple))
        self.typecheck(shell, bool)
        self.typecheck(demote, str)

        pipe = subprocess.Popen(command, stdout=subprocess.PIPE, \
            env={'LC_ALL': 'C'}, shell=shell, preexec_fn=self.system_demote(demote))
        output = pipe.communicate()[0].strip()
        return self.string_encode(output)

    def system_input(self, command, input, shell=False, demote=''):
        ''' Send input to external utility '''
        self.typecheck(command, (str, list, tuple))
        self.typecheck(input, str)
        self.typecheck(shell, bool)
        self.typecheck(demote, str)

        pipe = subprocess.Popen(command, stdin=subprocess.PIPE, \
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, \
            env={'LC_ALL': 'C'}, shell=shell, preexec_fn=self.system_demote(demote))
        out, err = pipe.communicate(input=input)
        if pipe.returncode != 0:
            raise(Exception('%s %s' % (out, err)))

    def system_scanelf(self, sfile, sformat='#F%n', sflags='', demote=''):
        ''' Get information about ELF files '''
        self.typecheck(sfile, str)
        self.typecheck(sformat, str)
        self.typecheck(sflags, str)
        self.typecheck(demote, str)

        return self.system_output((self.whereis('scanelf'), '-CBF', \
            sformat, sflags, sfile), demote=demote)

    def system_command(self, command, shell=False, cwd='', catch=False, demote=''):
        ''' Execute system command safely '''
        self.typecheck(command, (str, list, tuple))
        self.typecheck(shell, bool)
        self.typecheck(cwd, str)
        self.typecheck(catch, bool)
        self.typecheck(demote, str)

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

    def system_chroot(self, command, shell=False):
        ''' Execute command in chroot environment '''
        self.typecheck(command, (str, list, tuple))
        self.typecheck(shell, str)

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
            self.system_command(command, shell=shell)
        finally:
            os.fchdir(real_root)
            os.chroot('.')
            os.close(real_root)
            for s in ('/proc', '/dev', '/sys'):
                sdir = self.ROOT_DIR + s
                if os.path.ismount(sdir):
                    self.system_command((umount, '-f', '-l', sdir))

    def system_script(self, srcbuild, function):
        ''' Execute pre/post actions '''
        self.typecheck(srcbuild, str)
        self.typecheck(function, str)

        if self.ROOT_DIR == '/':
            self.system_command((self.whereis('bash'), '-e', '-c', \
                'source ' + srcbuild + ' && ' + function), cwd=self.ROOT_DIR)
        else:
            shutil.copy(srcbuild, os.path.join(self.ROOT_DIR, 'SRCBUILD'))
            self.system_chroot(('bash', '-e', '-c', \
                'source /SRCBUILD && ' + function))
            os.remove(os.path.join(self.ROOT_DIR, 'SRCBUILD'))

    def system_trigger(self, command, shell=False):
        ''' Execute trigger '''
        self.typecheck(command, (str, list, tuple))
        self.typecheck(shell, bool)

        if self.ROOT_DIR == '/':
            self.system_command(command, shell=shell, cwd=self.ROOT_DIR)
        else:
            self.system_chroot(command, shell=shell)
