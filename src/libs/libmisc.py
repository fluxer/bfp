#!/bin/python2

import sys, os, re, tarfile, zipfile, subprocess, shutil, shlex, libmagic
if sys.version < '3':
    import urlparse
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
        self.EXTERNAL = False
        self.ROOT_DIR = '/'
        self.CATCH = False

    def whereis(self, program, fallback=True, chroot=False):
        ''' Find full path to executable '''
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
        return tuple([int(x) for x in variant.split('.') if x.isdigit()])

    def string_encode(self, string):
        ''' String wrapper to ensure Python3 compat '''
        if sys.version_info[0] >= 3 and isinstance(string, bytes):
            return string.decode('utf-8')
        else:
            return string

    def string_convert(self, string):
        ''' Conver input to string but only if it really is list '''
        if isinstance(string, list) or isinstance(string, tuple):
            return ' '.join(string)
        return string

    def string_search(self, string, string2, exact=False, escape=True):
        ''' Search for string in other string or list '''
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
        dspecials = {'%20': ' '}
        sresult = urlparse(surl).path
        for schar in dspecials:
            sresult = sresult.replace(schar, dspecials[schar])
        if basename:
            return os.path.basename(sresult)
        return sresult

    def file_name(self, sfile, basename=True):
        ''' Get name of file without the extension '''
        if basename:
            return os.path.splitext(os.path.basename(sfile))[0]
        return os.path.splitext(sfile)[0]

    def file_extension(self, sfile):
        ''' Get the extension of file '''
        return os.path.splitext(sfile)[1].lstrip('.')

    def file_touch(self, sfile):
        ''' Touch a file, making sure it exists '''
        if not os.path.isfile(sfile):
            self.file_write(sfile, '')

    def file_read(self, sfile):
        ''' Get file content '''
        rfile = open(sfile, 'rb')
        content = rfile.read()
        rfile.close()
        return self.string_encode(content)

    def file_read_nonblock(self, sfile, sbuffer=1024):
        ''' Get file content non-blocking '''
        fd = os.open(sfile, os.O_NONBLOCK)
        content = os.read(fd, sbuffer)
        os.close(fd)
        return content

    def file_readlines(self, sfile):
        ''' Get file content, split by new line, as list '''
        rfile = open(sfile, 'rb')
        content = rfile.read().splitlines()
        rfile.close()
        return self.string_encode(content)

    def file_write(self, sfile, content, mode='w'):
        ''' Write data to file '''
        self.dir_create(os.path.dirname(sfile))

        wfile = open(sfile, mode)
        wfile.write(content)
        wfile.close()

    def file_write_nonblock(self, sfile, content):
        ''' Write data to file non-blocking (overwrites) '''
        self.dir_create(os.path.dirname(sfile))

        fd = os.open(sfile, os.O_NONBLOCK | os.O_WRONLY)
        os.write(fd, content)
        os.close(fd)

    def file_search(self, string, sfile, exact=False, escape=True):
        ''' Search for string in file '''
        return self.string_search(string, self.file_read(sfile), exact=exact, \
            escape=escape)

    def file_mime(self, sfile):
        ''' Get file type '''
        # symlinks are not handled properly by magic, on purpose
        # https://github.com/ahupp/python-magic/pull/31
        if os.path.islink(sfile):
            return 'inode/symlink'
        return self.string_encode(libmagic.from_file(sfile, mime=True))

    def file_substitute(self, string, string2, sfile):
        ''' Substitue a string with another in file '''
        self.file_write(sfile, re.sub(string, string2, self.file_read(sfile)))

    def dir_create(self, sdir):
        ''' Create directory if it does not exist, including leading paths '''
        if not os.path.isdir(sdir) and not os.path.islink(sdir):
            os.makedirs(sdir)

    def dir_remove(self, sdir):
        ''' Remove directory recursively '''
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

    def list_files(self, directory):
        ''' Get list of files in directory recursively '''
        slist = []
        for root, subdirs, files in os.walk(directory):
            for sfile in files:
                slist.append(os.path.join(root, sfile))
        return slist

    def list_dirs(self, directory):
        ''' Get list of directories in directory recursively '''
        slist = []
        for root, subdirs, files in os.walk(directory):
            for sdir in subdirs:
                slist.append(os.path.join(root, sdir))
        return slist

    def list_all(self, directory):
        ''' Get list of files and directories in directory recursively '''
        slist = []
        for root, subdirs, files in os.walk(directory):
            for sdir in subdirs:
                slist.append(os.path.join(root, sdir))
            for sfile in files:
                slist.append(os.path.join(root, sfile))
        return slist

    def fetch_check(self, url, destination):
        ''' Check if remote file and file sizes are equal '''
        # not all requests can get content-lenght , this means that there is
        # no way to tell if the archive is corrupted (checking if size == 0 is
        # not enough) so the source is re-feteched

        if self.OFFLINE:
            return True
        elif os.path.isfile(destination):
            local_size = os.path.getsize(destination)
            rfile = urlopen(url, timeout=self.TIMEOUT)
            remote_size = rfile.headers.get('content-length')
            rfile.close()

            if not remote_size:
                return False
            elif int(local_size) == int(remote_size):
                return True
        else:
            return False

    def fetch_internal(self, url, destination):
        ''' Download file using internal library '''
        if self.OFFLINE:
            return

        rfile = urlopen(url, timeout=self.TIMEOUT)
        dest_dir = os.path.dirname(destination)
        self.dir_create(dest_dir)

        output = open(destination, 'wb')
        output.write(rfile.read())
        output.close()
        rfile.close()

    def fetch(self, url, destination):
        ''' Download file using external utilities, fallback to internal '''
        if self.OFFLINE:
            return

        dest_dir = os.path.dirname(destination)
        self.dir_create(dest_dir)

        curl = self.whereis('curl', fallback=False)
        wget = self.whereis('wget', fallback=False)
        if self.EXTERNAL and curl:
            self.system_command((curl, '--connect-timeout', str(self.TIMEOUT), \
                '--fail', '--retry', '10', '--location', '--continue-at', '-', \
                url, '--output', destination))
        elif self.EXTERNAL and wget:
            self.system_command((wget, '--timeout', str(self.TIMEOUT), \
                '--continue', url, '--output-document', destination))
        else:
            self.fetch_internal(url, destination)

    def archive_supported(self, sfile):
        ''' Test if file is archive that can be handled properly '''
        if os.path.isdir(sfile):
            return False
        if sfile.endswith(('.xz', '.lzma', '.gz')) \
            or tarfile.is_tarfile(sfile) \
            or zipfile.is_zipfile(sfile):
            return True
        return False

    def archive_compress(self, variant, sfile, strip):
        ''' Create archive from directory '''
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

    def archive_decompress(self, sfile, sdir):
        ''' Extract archive to directory '''
        self.dir_create(sdir)

        # WARNING!!! the -P option is not supported by the
        # Busybox version of `tar`.

        # standard tarfile library locks the filesystem and upon interrupt the
        # filesystem stays locked which is bad. on top of that the tarfile
        # library can not replace files while they are being used thus the
        # external utilities are used for extracting tar archives.

        # altought bsdtar can (or should) handle Zip files it is not used for them.
        if sfile.endswith(('.xz', '.lzma')) \
            or tarfile.is_tarfile(sfile):
            bsdtar = self.whereis('bsdtar', fallback=False)
            # if bsdtar is present but tar is not do not fail and make tar
            # requirement only if bsdtar is not available
            if not bsdtar:
                tar = self.whereis('tar')
            if bsdtar:
                self.system_command((bsdtar, '-xpPf', sfile, '-C', sdir))
            else:
                self.system_command((tar, '-xphf', sfile, '-C', sdir))
        elif zipfile.is_zipfile(sfile):
            zfile = zipfile.ZipFile(sfile, 'r')
            zfile.extractall(path=sdir)
            zfile.close()
        elif sfile.endswith('.gz'):
            # FIXME: implement gzip decompression
            raise(Exception('Gzip decompression not implemented yet'))

    def archive_list(self, sfile):
        ''' Get list of files in archive '''
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
        size = 0
        tar = tarfile.open(star, 'r')
        for i in tar.getmembers():
            if i.name == sfile:
                size = i.size
                break
        tar.close()
        return size

    def system_output(self, command, shell=False):
        ''' Get output of external utility '''
        pipe = subprocess.Popen(command, stdout=subprocess.PIPE, \
            env={'LC_ALL': 'C'}, shell=shell)
        output = pipe.communicate()[0].strip()
        return self.string_encode(output)

    def system_input(self, command, input, shell=False):
        ''' Send input to external utility '''
        pipe = subprocess.Popen(command, stdin=subprocess.PIPE, \
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, \
            env={'LC_ALL': 'C'}, shell=shell)
        out, err = pipe.communicate(input=input)
        if pipe.returncode != 0:
            raise(Exception('%s %s' % (out, err)))

    def system_scanelf(self, sfile, sformat='#F%n', sflags=''):
        ''' Get information about ELF files '''
        return self.system_output((self.whereis('scanelf'), '-CBF', \
            sformat, sflags, sfile))

    def system_command(self, command, shell=False, cwd=None, catch=False):
        ''' Execute system command safely '''
        if not cwd:
            cwd = self.dir_current()
        elif not os.path.isdir(cwd):
            cwd = '/'
        if isinstance(command, str) and not shell:
            command = shlex.split(command)
        if catch or self.CATCH:
            pipe = subprocess.Popen(command, stderr=subprocess.PIPE, \
                shell=shell, cwd=cwd)
            pipe.wait()
            if pipe.returncode != 0:
                raise(Exception(pipe.communicate()[1].strip()))
            return pipe.returncode
        else:
            return subprocess.check_call(command, shell=shell, cwd=cwd)

    def system_chroot(self, command, shell=False):
        ''' Execute command in chroot environment '''
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
        if self.ROOT_DIR == '/':
            self.system_command(command, shell=shell, cwd=self.ROOT_DIR)
        else:
            self.system_chroot(command, shell=shell)
