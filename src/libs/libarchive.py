#!/usr/bin/python2

import os, sys, types, ctypes
import libmisc
misc = libmisc.Misc()

try:
    lib = ctypes.cdll.LoadLibrary('libarchive.so')
except OSError as msg:
    raise ImportError('Could not find libarchive.so')


### libarchive  interface
class Libarchive(object):
    ''' Python CTypes interface to libarchive '''

    class ArchiveException(Exception):
        pass

    # These are our structs for libarchive (hopefully)
    class Archive(ctypes.Structure):
        pass

    class ArchiveEntry(ctypes.Structure):
        pass

    ### Initialization
    def __init__(self):
        self.lib = lib
        # constants
        self.ARCH_EOF = 1
        self.ARCH_OK = 0
        self.ARCH_RETRY = -10
        self.ARCH_WARN = -20
        self.ARCH_FAILED = -25
        self.ARCH_FATAL = -30
        self.ExtractFlags = 4 | 2 | 32 | 64 # TIME,PERM,ACL,FFLAGS

        # function symbols and their return types
        self.versionNumber = self.lib.archive_version_number
        self._entryNew = self.lib.archive_entry_new
        self._entryNew.restype = ctypes.POINTER(self.ArchiveEntry)
        self._readNew = self.lib.archive_read_new
        self._readNew.restype = ctypes.POINTER(self.Archive)
        self._readDiskNew = self.lib.archive_read_disk_new
        self._readDiskNew.restype = ctypes.POINTER(self.Archive)
        self._writeNew = self.lib.archive_write_new
        self._writeNew.restype = ctypes.POINTER(self.Archive)
        self._writeDiskNew = self.lib.archive_write_disk_new
        self._writeDiskNew.restype = ctypes.POINTER(self.Archive)

        # reading
        self._readClose = self.lib.archive_read_close
        self._readDataBlock = self.lib.archive_read_data_block
        self._readDataSkip = self.lib.archive_read_data_skip
        self._readNextHeader = self.lib.archive_read_next_header
        self._readOpenFilename = self.lib.archive_read_open_filename
        self._readSupportFilterAll = self.lib.archive_read_support_compression_all
        self._readSupportFormatAll = self.lib.archive_read_support_format_all

        # writing
        self._writeOpenFilename = self.lib.archive_write_open_filename
        self._writeClose = self.lib.archive_write_close
        self._writeDataBlock = self.lib.archive_write_data_block
        self._writeDiskSetOptions = self.lib.archive_write_disk_set_options
        self._writeDiskSetLookup = self.lib.archive_write_disk_set_standard_lookup
        self._writeFinishEntry = self.lib.archive_write_finish_entry
        self._writeHeader = self.lib.archive_write_header
        self._filterBzip2 = self.lib.archive_write_add_filter_bzip2
        self._filterBzip2.restype = ctypes.POINTER(self.Archive)
        self._filterGzip = self.lib.archive_write_add_filter_gzip
        self._filterGzip.restype = ctypes.POINTER(self.Archive)
        self._filterLZMA = self.lib.archive_write_set_compression_lzma
        self._filterLZMA.restype = ctypes.POINTER(self.Archive)
        self._filterNone = self.lib.archive_write_add_filter_none
        self._filterNone.restype = ctypes.POINTER(self.Archive)
        self._formatGnuTar = self.lib.archive_write_set_format_gnutar
        self._formatGnuTar.restype = ctypes.POINTER(self.Archive)
        self._formatUsTar = self.lib.archive_write_set_format_ustar
        self._formatUsTar.restype = ctypes.POINTER(self.Archive)
        self._formatPax = self.lib.archive_write_set_format_pax
        self._formatPax.restype = ctypes.POINTER(self.Archive)
        self._formatPaxRestricted = self.lib.archive_write_set_format_pax_restricted
        self._formatPaxRestricted.restype = ctypes.POINTER(self.Archive)

        # info
        self._entrySize = self.lib.archive_entry_size
        self._entryType = self.lib.archive_entry_filetype
        self._entrySymlink = self.lib.archive_entry_symlink

        # this is due to a problem where libarchive version below v3.x do not have
        # the archive_read_free symbol. And archive_read_finish will only be kept
        # about until version 4 of the library, so no sense in not being forward
        # compatible about it.
        if int(self.versionNumber()) < int(3001002):
            self._readFree = self.lib.archive_read_finish
            self._writeFree = self.lib.archive_write_finish
        else:
            self._readFree = self.lib.archive_read_free
            self._writeFree = self.lib.archive_write_free

        # string return types
        self._entryPathname = self.lib.archive_entry_pathname
        self._entryPathname.restype = ctypes.c_char_p
        self._errorString = self.lib.archive_error_string
        self._errorString.restype = ctypes.c_char_p

    ### Private methods
    def _copyData(self, archiveR, archiveW):
        r = ctypes.c_int()
        buff = ctypes.c_void_p()
        size = ctypes.c_int()
        offs = ctypes.c_longlong()

        while True:
            # read in a block
            r = self._readDataBlock(
                archiveR,           # Archive (reading)
                ctypes.byref(buff), # Buffer pointer
                ctypes.byref(size), # Size pointer
                ctypes.byref(offs)) # Offset pointer

            # check ourselves
            if r == self.ARCH_EOF:
                return self.ARCH_OK
            if r != self.ARCH_OK:
                return r

            # write out a block
            r = self._writeDataBlock(
                archiveW,     # Archive (writing)
                buff,         # Buffer data
                size,         # Size data
                offs)         # Offset data

            # And check ourselves again
            if r != self.ARCH_OK:
                raise self.ArchiveException(self._errorString(archiveW))

    def _addEntry(self, spath, archive, strip):
        entry = self._entryNew()
        stat = os.stat(spath)
        # http://linux.die.net/man/2/stat
        self.lib.archive_entry_set_pathname(entry, types.StringType(misc.string_lstrip(spath, strip)))
        # self.lib.archive_entry_set_pathname(entry, spath)
        self.lib.archive_entry_set_size(entry, ctypes.c_int64(stat.st_size))
        # self.lib.archive_entry_set_filetype(entry)
        self.lib.archive_entry_set_mode(entry, stat.st_mode)
        self.lib.archive_entry_set_perm(entry, stat.st_mode)
        # self.lib.archive_entry_copy_stat(entry, stat)
        if self._writeHeader(archive, entry) != self.ARCH_OK:
            self.lib.archive_entry_free(entry)
            raise self.ArchiveException(self._errorString(archive))
        with open(spath, 'rb') as f:
            self.lib.archive_write_data(archive, f.read(), stat.st_size)
        self.lib.archive_entry_free(entry)
        return True

    ### Public methods
    def listArchive(self, fname, append=''):
        ''' List the contents of archive (returns a list of path/filenames) '''
        archive = self._readNew() # Archive struct
        entry = self._entryNew()  # Entry struct
        content = []

        # detect compression and archive type
        self._readSupportFilterAll(archive)
        self._readSupportFormatAll(archive)

        # open, analyse, and close our archive
        if self._readOpenFilename(archive, fname, 10240) != self.ARCH_OK:
            raise self.ArchiveException(self._errorString(archive))

        while self._readNextHeader(archive, ctypes.byref(entry)) == self.ARCH_OK:
            content.append('%s%s' % (append, self._entryPathname(entry)))
            self._readDataSkip(archive) # Not strictly necessary

        if self._readFree(archive) != self.ARCH_OK:
            raise self.ArchiveException(self._errorString(archive))

        # You did good soldier
        return content

    def extractArchive(self, fname, preserve=False):
        ''' Extract the contents of archive '''

        # preserve permissions
        if preserve:
            self.ExtractFlags = self.ExtractFlags | 80 | 200 # XATTR, MAC_METADATA

        # setup our structs
        arch = self._readNew()
        ext = self._writeDiskNew()
        entry = self._entryNew()

        # detect archive type and compression
        self._readSupportFormatAll(arch)
        self._readSupportFilterAll(arch)

        # set our writer options
        self._writeDiskSetOptions(ext, self.ExtractFlags)
        self._writeDiskSetLookup(ext)

        # open the archive
        self._readOpenFilename(arch, fname, 10240)

        # get our first header
        ret = self._readNextHeader(arch, ctypes.byref(entry))
        while ret != self.ARCH_EOF:
            if ret != self.ARCH_OK or ret < self.ARCH_WARN:
                raise self.ArchiveException(self._errorString(arch))

            # write out our header
            ret = self._writeHeader(ext, entry)
            if ret != self.ARCH_OK:
                raise self.ArchiveException(self._errorString(ext))
            elif self._entrySize(entry) > 0:
                # copy the contents into their new home
                self._copyData(arch, ext)

            # close that entry up
            ret = self._writeFinishEntry(ext)
            if ret != self.ARCH_OK:
                raise self.ArchiveException(self._errorString(ext))

            # And get ready to head back to the top
            ret = self._readNextHeader(arch, ctypes.byref(entry))

        # cleanup
        self._readClose(arch)
        self._readFree(arch)
        self._writeClose(ext)
        self._writeFree(ext)

        # You did good soldier
        return self.ARCH_OK

    def createArchive(self, paths, output, strip='/'):
        ''' Create archive '''
        retv = True              # Return value
        archive = self._writeNew() # Archive struct

        if output.endswith('.bz2'):
            self._filterBzip2(archive)
        elif output.endswith('.gz'):
            self._filterBzip2(archive)
        elif output.endswith(('.xz', '.lzma')):
            self._filterLZMA(archive)
        else:
            self._filterNone(archive)

        self._formatPaxRestricted(archive)

        if os.path.isfile(output):
            # XXX: raise error?
            os.remove(output)

        # open, analyse, and close our archive
        if self._writeOpenFilename(archive, output, 10240) != self.ARCH_OK:
            raise self.ArchiveException(self._errorString(archive))

        for spath in paths:
            if os.path.isdir(spath):
                breakfree = False
                for root, dirs, files in os.walk(spath):
                    if breakfree:
                        break
                    for sfile in files:
                        if breakfree:
                            break
                        if not self._addEntry(os.path.join(root, sfile), archive, strip):
                            retv = False
                            breakfree = True
                            break
            else:
                if not self._addEntry(spath, archive, strip):
                    retv = False
                    break

        self._writeClose(archive)
        self._writeFree(archive)

        # return value
        return retv

    def supportedArchive(self, fname):
        ''' Check if the archive is supported '''
        retv = False              # Return value
        archive = self._readNew() # Archive struct

        # detect compression and archive type
        self._readSupportFilterAll(archive)
        self._readSupportFormatAll(archive)

        # open, analyse, and close our archive
        if self._readOpenFilename(archive, fname, 10240) == self.ARCH_OK:
            retv = True

        if self._readClose(archive) != self.ARCH_OK:
            raise self.ArchiveException(self._errorString(archive))

        # You did good soldier
        return retv

### Main argument handling / operations
if __name__ == '__main__':
    amode = '-x'
    afiles = []
    try:
        # Chug through the remaining arguments and process them
        for arg in sys.argv[1:]:
            # Handle different modes
            if arg == '-x' or arg == '-t' or arg == '-c':
                amode = arg
            else:
                afiles.append(arg)

        obj = Libarchive()
        if amode == '-x':
            for afile in afiles:
                print('Extracting %s...' % afile)
                obj.extractArchive(afile)
        elif amode == '-t':
            for afile in afiles:
                print('Listing %s...' % afile)
                print(obj.listArchive(afile))
        elif amode == '-c':
            print('Creating %s...' % afiles[0])
            obj.createArchive(afiles[1:], afiles[0])
    except Exception as msg:
        print(msg)
        sys.exit(1)
