#!/usr/bin/python2

import os, time, shutil, glob, libmisc
misc = libmisc.Misc()

class JDB(object):
    ''' A simple JSON format database for use with mulptile processes '''
    def __init__(self, dbfile):
        self.dbfile = dbfile
        self.dbbackup = '%s.bkp' % self.dbfile
        self.dblock = '%s.%s' % (self.dbfile, os.getpid())
        self.dbwindow = 0.5

    def init(self):
        if not os.path.isfile(self.dbfile):
            misc.dir_create(os.path.dirname(self.dbfile))
            self.write({'dbsane': True})

    def read(self, iretry=3):
        while glob.glob('%s.[0-9]*' % self.dbfile):
            time.sleep(self.dbwindow)
        # race me, please!
        data = {}
        try:
            misc.file_touch(self.dblock)
            data = misc.json_read(self.dbfile)
        finally:
            if os.path.isfile(self.dblock):
                os.unlink(self.dblock)
            time.sleep(self.dbwindow)
            if not 'dbsane' in data:
                # fault tollerance
                if iretry > 0:
                    return self.read(iretry-1)
                raise(Exception('Corrupted database', self.dbfile))
        return data

    def write(self, data):
        if not 'dbsane' in data:
            raise(Exception('Corrupted data', self.dbfile))
        while glob.glob('%s.[0-9]*' % self.dbfile):
            time.sleep(self.dbwindow)
        # race me, please!
        try:
            misc.file_touch(self.dblock)
            if os.path.isfile(self.dbfile):
                shutil.copy2(self.dbfile, self.dbbackup)
            misc.json_write(self.dbfile, data)
        finally:
            if os.path.isfile(self.dblock):
                os.unlink(self.dblock)
            time.sleep(self.dbwindow)

if __name__ == '__main__':
    import random
    db = JDB('/tmp/cache.json')
    db.init()
    while True:
        data = db.read()
        data[random.random()] = random.random()
        db.write(data)
