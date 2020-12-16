#!/usr/bin/python2

import libmisc, libpackage, timeit, tempfile, os
misc = libmisc.Misc()
database = libpackage.Database()

def create_remote(name, version, release, description, depends='', \
        makedepends='', sources='', options='', backup='', optdepends=''):
    sdir = '%s/repositories/test/%s' % (database.CACHE_DIR, name)
    os.makedirs(sdir)
    srcbuild = open('%s/SRCBUILD' % sdir, 'w')
    srcbuild.write('version=%s' % version)
    srcbuild.write('\nrelease=%s' % release)
    srcbuild.write('\ndescription="%s"' % description)
    srcbuild.write('\ndepends=(%s)' % depends)
    srcbuild.write('\nmakedepends=(%s)' % makedepends)
    srcbuild.write('\noptdepends=(%s)' % optdepends)
    srcbuild.write('\ncheckdepends=(%s)' % name)
    srcbuild.write('\nsources=(%s)' % sources)
    srcbuild.write('\noptions=(%s)' % options)
    srcbuild.write('\nbackup=(%s)' % backup)
    srcbuild.close()

def create_local(name, version, release, description, depends='', \
        optdepends='', backup='', footprint=''):
    data = {}
    data['version'] = version
    data['release'] = release
    data['description'] = description
    data['depends'] = str(depends).split()
    data['optdepends'] = str(optdepends).split()
    data['backup'] = str(backup).split()
    data['footprint'] = str(footprint).split()
    sdir = '%s/%s' % (database.LOCAL_DIR, name)
    os.makedirs(sdir)
    misc.json_write('%s/metadata.json' % sdir, data)

def benchmark_remote(t):
    # do not setup database notifier to avoid hitting the system limit
    # which is usually ~8200
    database.NOTIFY = False
    database.ROOT_DIR = tempfile.mkdtemp()
    database.CACHE_DIR = '%s/var/cache/spm' % database.ROOT_DIR
    database.BUILD_DIR = '%s/var/tmp/spm' % database.ROOT_DIR
    database.LOCAL_DIR = '%s/var/local/spm' % database.ROOT_DIR
    try:
        # print('preparing for benchmark...')
        for r in range(5000):
            create_remote(r, r, r, r, r, r, r, r, r)
        # print('running benchmark %d...' % t)
        print(timeit.timeit(database.remote_all, number=1))
        database.REMOTE_CACHE = {}
    finally:
        # print('cleaning up ...')
        misc.dir_remove(database.ROOT_DIR)

def benchmark_local(t):
    # do not setup database notifier to avoid hitting the system limit
    # which is usually ~8200
    database.NOTIFY = False
    database.ROOT_DIR = tempfile.mkdtemp()
    database.CACHE_DIR = '%s/var/cache/spm' % database.ROOT_DIR
    database.BUILD_DIR = '%s/var/tmp/spm' % database.ROOT_DIR
    database.LOCAL_DIR = '%s/var/local/spm' % database.ROOT_DIR
    try:
        # print('preparing for benchmark...')
        for r in range(5000):
            create_local(r, r, r, r, r, r, r, r)
        # print('running benchmark %d...' % t)
        print(timeit.timeit(database.local_all, number=1))
        database.LOCAL_CACHE = {}
    finally:
        # print('cleaning up ...')
        misc.dir_remove(database.ROOT_DIR)

for t in range(3):
    # best of three
    benchmark_remote(t)
for t in range(3):
    # best of three
    benchmark_local(t)
