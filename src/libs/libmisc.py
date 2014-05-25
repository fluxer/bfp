#!/usr/bin/python

import os
import re
import urllib2
import tarfile
import zipfile
import subprocess
import httplib
import shutil

import libmagic


class Misc(object):
    def __init__(self):
        self.TIMEOUT = 30
        self.EXTERNAL = False
        self.ROOT_DIR = '/'

    def whereis(self, program, fallback=True):
        ''' Find full path to executable '''
        for path in os.environ.get('PATH', '/bin:/usr/bin').split(':'):
            exe = os.path.join(path, program)
            if os.path.isfile(exe):
                return exe
        if fallback:
            # if only the OSError exception was a bit more robust. in the future,
            # fallback will return program and let OSError be raised at higher level
            raise OSError('Program not found in PATH', program)
        return None

    def ping(self, url='http://www.google.com'):
        ''' Ping URL '''
        try:
            p = urllib2.urlopen(url, timeout=self.TIMEOUT)
            p.close()
            return True
        except (urllib2.URLError, httplib.BadStatusLine):
            return False

    def version(self, variant):
        ''' Convert input to tuple suitable for version comparison '''
        # if None is passed, e.g. on invalid remote target, the split will fail
        if not variant:
            return ()
        return tuple([int(x) for x in variant.split('.') if x.isdigit()])

    def string_convert(self, string):
        ''' Conver input to string but only if it really is list '''
        if isinstance(string, list) or isinstance(string, tuple):
            return ' '.join(string)
        return string

    def string_search(self, string, string2, exact=False, escape=True):
        ''' Search for string in other string or list '''
        if exact and escape:
            return re.findall('(\\s|^)' + re.escape(string) + '(\\s|$)', self.string_convert(string2))
        elif exact:
            return re.findall('(\\s|^)' + string + '(\\s|$)', self.string_convert(string2))
        elif escape:
            return re.findall(re.escape(string), self.string_convert(string2))
        else:
            return re.findall(string, self.string_convert(string2))

    def file_read(self, sfile):
        ''' Get file content '''
        rfile = open(sfile, 'r')
        content = rfile.read()
        rfile.close()
        return content

    def file_read_nonblock(self, sfile, sbuffer=1024):
        fd = os.open(sfile, os.O_NONBLOCK)
        content = os.read(fd, sbuffer)
        os.close(fd)
        return content

    def file_readlines(self, sfile):
        ''' Get file content, split by new line, as list '''
        rfile = open(sfile, 'r')
        content = rfile.read().splitlines()
        rfile.close()
        return content

    def file_write(self, sfile, content):
        ''' Write data to file (overwrites) '''
        dirname = os.path.dirname(sfile)
        self.dir_create(dirname)

        wfile = open(sfile, 'w')
        wfile.write(content)
        wfile.close()

    def file_search(self, string, sfile, exact=False, escape=True):
        ''' Search for string in file '''
        return self.string_search(string, self.file_read(sfile), exact=exact, escape=escape)

    def file_mime(self, sfile):
        ''' Get file type '''
        # symlinks are not handled properly by magic, on purpose
        # https://github.com/ahupp/python-magic/pull/31
        if os.path.islink(sfile):
            return 'inode/symlink'
        return libmagic.from_file(sfile, mime=True)

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
        ''' Get list of directories in directory recursively '''
        slist = []
        for root, subdirs, files in os.walk(directory):
            for sdir in subdirs:
                slist.append(os.path.join(root, sdir))
            for sfile in files:
                slist.append(os.path.join(root, sfile))
        return slist

    def fetch_check(self, url, destination):
        ''' Check if remote file and file sizes are equal '''
        # not all requests can get content-lenght , this means that there is no way
        # to tell if the archive is corrupted (checking if size == 0 is not enough)
        # so the source is re-feteched

        if os.path.isfile(destination):
            local_size = os.path.getsize(destination)
            rfile = urllib2.urlopen(url, timeout=self.TIMEOUT)
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
        rfile = urllib2.urlopen(url, timeout=self.TIMEOUT)
        dest_dir = os.path.dirname(destination)
        self.dir_create(dest_dir)

        output = open(destination, 'wb')
        output.write(rfile.read())
        output.close()
        rfile.close()

    def fetch(self, url, destination):
        ''' Download file using external utilities, fallback to internal '''
        dest_dir = os.path.dirname(destination)
        self.dir_create(dest_dir)

        curl = self.whereis('curl', fallback=False)
        wget = self.whereis('wget', fallback=False)
        if self.EXTERNAL and curl:
            subprocess.check_call((curl, '--connect-timeout', str(self.TIMEOUT),
                '--fail', '--retry', '10', '--location', '--continue-at', '-',
                url, '--output', destination))
        elif self.EXTERNAL and wget:
            subprocess.check_call((wget, '--timeout', str(self.TIMEOUT),
                '--continue', url, '--output-document', destination))
        else:
            self.fetch_internal(url, destination)

    def archive_supported(self, sfile):
        ''' Test if file is archive that can be handled properly '''
        if os.path.isdir(sfile):
            return False
        if sfile.endswith('.xz') or sfile.endswith('.lzma') or tarfile.is_tarfile(sfile) or zipfile.is_zipfile(sfile):
            return True
        return False

    def archive_compress(self, variant, sfile, method='bz2', chdir=None):
        ''' Create archive from directory '''
        self.dir_create(os.path.dirname(sfile))

        if isinstance(variant, str):
            variant = [variant]

        if chdir:
            os.chdir(chdir)

        if sfile.endswith('.bz2') or sfile.endswith('.gz'):
            tar = tarfile.open(sfile, 'w:' + method)
            for item in variant:
                if chdir:
                    tar.add(item.replace(chdir, './'))
                else:
                    tar.add(item, '')
            tar.close()
        elif sfile.endswith('.zip'):
            zip = zipfile.ZipFile(sfile, mode='w')
            for item in variant:
                if chdir:
                    zip.write(item.replace(chdir, './'))
                else:
                    zip.write(item)
            zip.close()
        elif sfile.endswith('.xz') or sfile.endswith('.lzma'):
            # FIXME: implement lzma/xz compression
            raise(Exception('Not implemented yet'))

    def archive_decompress(self, sfile, sdir):
        ''' Extract archive to directory '''
        self.dir_create(sdir)

        # WARNING!!! the -P option is not supported by the
        # Busybox version of `tar`.

        # standard tarfile library locks the filesystem and upon interrupt the
        # filesystem stays locked which is bad. on top of that the tarfile library
        # can not replace files while they are being used thus the external
        # utilities are used for extracting archives.

        # alotught bsdtar can (or should) handle Zip files we do not use it for them.
        if sfile.endswith('.xz') or sfile.endswith('.lzma') or tarfile.is_tarfile(sfile):
            bsdtar = self.whereis('bsdtar', fallback=False)
            tar = self.whereis('tar')
            if bsdtar:
                subprocess.check_call((bsdtar, '-xpPf', sfile, '-C', sdir))
            else:
                subprocess.check_call((tar, '-xphf', sfile, '-C', sdir))
        elif zipfile.is_zipfile(sfile):
            zfile = zipfile.ZipFile(sfile, 'r')
            zfile.extractall(path=sdir)
            zfile.close()

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
        elif sfile.endswith('.xz') or sfile.endswith('.lzma'):
            content = self.system_output((self.whereis('tar'), '-tf', sfile)).split('\n')
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


    def ipc_create(self, fifo, group=0, mode=0664):
        ''' Create fifo for communication '''
        if not os.path.exists(fifo):
            os.mkfifo(fifo, mode)
        # set owner of IPC to <group>:<group>
        # os.chown(fifo, group, group)
        # sadly, something is wrong with mkfifo permissions set
        # os.chmod(fifo, mode)

    def ipc_read(self, fifo):
        ''' Read IPC and return a tuple of service and action '''
        if not os.path.exists(fifo):
            # FIXME: needs proper permissions set
            # ipc_create(fifo)
            return None
        return self.file_read_nonblock(fifo).strip()

    def ipc_write(self, fifo, content):
        ''' Write service and action to IPC '''
        self.file_write(fifo, content)


    def system_output(self, command):
        ''' Get output of external utility '''
        pipe = subprocess.Popen(command, stdout=subprocess.PIPE, env={'LC_ALL': 'C'})
        return pipe.communicate()[0].strip()

    def system_scanelf(self, sfile, format='#F%n'):
        ''' Get information about ELF files '''
        return self.system_output((self.whereis('scanelf'), '-CBF', format, sfile))

    def system_chroot(self, command):
        ''' Execute command in chroot environment '''
        # prevent stupidity
        if self.ROOT_DIR == '/':
            return

        real_root = os.open('/', os.O_RDONLY)
        mount = self.whereis('mount')
        try:
            for s in ('/proc', '/dev', '/sys'):
                sdir = self.ROOT_DIR + s
                if not os.path.ismount(sdir):
                    self.dir_create(sdir)
                    subprocess.check_call((mount, '--rbind', s, sdir))
            os.chroot(self.ROOT_DIR)
            os.chdir('/')
            subprocess.check_call(command)
        finally:
            os.fchdir(real_root)
            os.chroot('.')
            os.close(real_root)
            for s in ('/proc', '/dev', '/sys'):
                sdir = self.ROOT_DIR + s
                if os.path.ismount(sdir):
                    subprocess.check_call((mount, '--force', '--lazy', sdir))

    def system_script(self, srcbuild, function):
        ''' Execute pre/post actions '''
        if self.ROOT_DIR == '/':
            subprocess.check_call((self.whereis('bash'), '-e', '-c', 'source ' + srcbuild + ' && ' + function),
                cwd=self.ROOT_DIR)
        else:
            shutil.copy(srcbuild, os.path.join(self.ROOT_DIR, 'SRCBUILD'))
            self.system_chroot(('bash', '-e', '-c', 'source /SRCBUILD && ' + function))
            os.remove(os.path.join(self.ROOT_DIR, 'SRCBUILD'))
