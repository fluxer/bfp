#!/usr/bin/python2

import unittest, tempfile, os, sys, types

import libmisc
misc = libmisc.Misc()
import libpackage
database = libpackage.Database()


class TestSuite(unittest.TestCase):
    database.ROOT_DIR = tempfile.mkdtemp()

    def create_remote(self, name, version, release, description, \
        depends='', makedepends='', sources='', pgpkeys='', options='', \
        backup='', optdepends=''):
        sdir = '%s/repositories/test/%s' % (database.CACHE_DIR, name)
        os.makedirs(sdir)
        srcbuild = open('%s/SRCBUILD' % sdir, 'w')
        srcbuild.write('version=%s' % version)
        srcbuild.write('\nrelease=%s' % release)
        srcbuild.write('\ndescription="%s"' % description)
        srcbuild.write('\ndepends=(%s)' % misc.string_convert(depends))
        srcbuild.write('\nmakedepends=(%s)' % misc.string_convert(makedepends))
        srcbuild.write('\noptdepends=(%s)' % misc.string_convert(optdepends))
        srcbuild.write('\ncheckdepends=(%s)' % name)
        srcbuild.write('\nsources=(%s)' % misc.string_convert(sources))
        srcbuild.write('\npgpkeys=(%s)' % misc.string_convert(pgpkeys))
        srcbuild.write('\noptions=(%s)' % misc.string_convert(options))
        srcbuild.write('\nbackup=(%s)' % misc.string_convert(backup))
        srcbuild.close()

    def create_local(self, name, version, release, description, depends='', \
            size='1', footprint='\n', optdepends=''):
        sdir = '%s/%s' % (database.LOCAL_DIR, name)
        os.makedirs(sdir)
        data = {}
        data['version'] = version
        data['release'] = release
        data['description'] = description
        data['depends'] = depends
        data['optdepends'] = optdepends
        data['size'] = size
        data['footprint'] = footprint
        misc.json_write('%s/metadata.json' % sdir, data)
        misc.file_touch('%s/SRCBUILD' % sdir)

    def setUp(self):
        database.CACHE_DIR = '%s/var/cache/spm' % database.ROOT_DIR
        database.BUILD_DIR = '%s/var/tmp/spm' % database.ROOT_DIR
        database.LOCAL_DIR = '%s/var/local/spm' % database.ROOT_DIR

        if os.path.isdir(database.ROOT_DIR):
            misc.dir_remove(database.ROOT_DIR)

        os.makedirs(database.ROOT_DIR)
        os.makedirs(database.CACHE_DIR)
        os.makedirs(database.BUILD_DIR)
        os.makedirs(database.LOCAL_DIR)

        # dummy remote target
        self.remote_name = 'glibc'
        self.remote_version = '2.16.1'
        self.remote_release = '1'
        self.remote_description = 'SPM test target'
        self.remote_depends = ['filesystem', 'linux-api-headers', 'tzdata']
        self.remote_makedepends = ['circular']
        self.remote_optdepends = ['dummy']
        self.remote_source = ['\n', '', 'http://ftp.gnu.org/gnu/glibc/glibc-2.16.0.tar.xz']
        self.remote_pgpkeys = ['25EF0A436C2A4AFF']
        self.remote_options = ['!binaries', 'shared', '!static', 'man']
        self.remote_backup = ['etc/ld.so.conf', 'etc/nsswitch.conf']
        self.create_remote(self.remote_name, self.remote_version, \
            self.remote_release, self.remote_description, self.remote_depends, \
            self.remote_makedepends, self.remote_source, self.remote_pgpkeys, \
            self.remote_options, self.remote_backup, self.remote_optdepends)

        # second dummy remote target
        self.remote2_name = 'dummy'
        self.remote2_version = '999'
        self.remote2_release = '1'
        self.remote2_description = 'SPM circular test target'
        self.remote2_makedepends = [self.remote_name]
        self.create_remote(self.remote2_name, self.remote2_version, \
            self.remote2_release, self.remote2_description, \
            makedepends=self.remote2_makedepends)

        # third dummy remote target
        self.remote3_name = 'dummy2'
        self.remote3_version = '1.0.1'
        self.remote3_release = '1'
        self.remote3_description = 'SPM up-to-date test target'
        self.remote3_makedepends = [self.remote_name]
        self.create_remote(self.remote3_name, self.remote3_version, \
            self.remote3_release, self.remote3_description, \
            makedepends=self.remote3_makedepends)

        # third dummy remote target
        self.remote4_name = 'dummy3'
        self.remote4_version = '1.0.0'
        self.remote4_release = '2'
        self.remote4_description = 'SPM up-to-date release test target'
        self.create_remote(self.remote4_name, self.remote4_version, \
            self.remote4_release, self.remote4_description)

        # dummy local target
        self.local_name = 'dummy'
        self.local_version = '9999'
        self.local_release = '1'
        self.local_description = 'SPM dummy local test target'
        self.local_depends = [self.remote_name]
        self.local_size = '12345'
        self.local_footprint = '/etc/dummy.conf\n/lib/libdummy.so'
        self.local_optdepends = [self.remote2_name]
        self.create_local(self.local_name, self.local_version, \
            self.local_release, self.local_description, self.local_depends, \
            self.local_size, self.local_footprint, self.local_optdepends)

        # second dummy local target
        self.local2_name = 'dummy2'
        self.local2_version = '1.0.0'
        self.local2_release = '1'
        self.local2_description = 'SPM dummy reverse test target'
        self.local2_depends = [self.local_name]
        self.local2_size = '12345'
        self.local2_footprint = ['/etc/dummy2.conf', '/lib/libdummy2.so']
        self.create_local(self.local2_name, self.local2_version, \
            self.local2_release, self.local2_description, \
            self.local2_depends, self.local2_size, self.local2_footprint)

        # third dummy local target
        self.local3_name = 'dummy3'
        self.local3_version = '1.0.0'
        self.local3_release = '1'
        self.local3_description = 'SPM dummy empty depends and release test target'
        self.local3_depends = []
        self.local3_size = '12345'
        self.local3_footprint = []
        self.create_local(self.local3_name, self.local3_version, \
            self.local3_release, self.local3_description, \
            self.local3_depends, self.local3_size, self.local3_footprint)

    def tearDown(self):
        misc.dir_remove(database.ROOT_DIR)

    # string/regexp match checks
    def test_search_string_simple_true(self):
        self.assertTrue(misc.string_search('bar', 'foo_bar_baz'))

    def test_search_string_simple_false(self):
        self.assertEqual(misc.string_search('barz', 'foo_bar_baz'), [])

    def test_search_string_regexp(self):
        self.assertTrue(misc.string_search('ab+', 'abcbdef', escape=False))

    def test_search_string_exact_begining_true(self):
        self.assertTrue(misc.string_search('foo', 'foo bar', exact=True))

    def test_search_string_exact_begining_false(self):
        self.assertEqual(misc.string_search('foo', 'foobar', exact=True), [])

    def test_search_string_exact_middle_true(self):
        self.assertTrue(misc.string_search('bar', 'foo\tbar\nbaz', exact=True))

    def test_search_string_exact_middle_false(self):
        self.assertEqual(misc.string_search('bar', 'foobarbaz', exact=True), \
            [])

    def test_search_string_exact_middle_false2(self):
        self.assertEqual(misc.string_search('.(bar).', 'foo bar baz', \
            exact=True), [])

    def test_search_string_exact_end_true(self):
        self.assertTrue(misc.string_search('bar', 'foo\tbar', exact=True))

    def test_search_string_exact_end_false(self):
        self.assertEqual(misc.string_search('bar', 'foobar', exact=True), [])

    def test_search_string_exact_in_list_true(self):
        self.assertTrue(misc.string_search('bar', ['foo', 'bar', 'baz'], \
            exact=True))

    def test_search_string_exact_in_list_false(self):
        self.assertEqual(misc.string_search('barz', ['foo', 'bar', 'baz'], \
            exact=True), [])

    def test_search_string_exact_escape(self):
        self.assertTrue(misc.string_search('bar\nbaz', 'bar\nbaz', \
            exact=True, escape=True))

    def test_url_ping_true(self):
        self.assertTrue(misc.url_ping())

    def test_url_ping_false(self):
        misc.OFFLINE = True
        self.assertFalse(misc.url_ping())
        misc.OFFLINE = False

    # remote targets checks
    def test_remote_target_search_true(self):
        self.assertEqual(database.remote_search(self.remote_name), \
            '%s/repositories/test/%s' % (database.CACHE_DIR, self.remote_name))

    def test_remote_target_search_false(self):
        self.assertEqual(database.remote_search('foobar'), None)

    def test_remote_target_version(self):
        self.assertEqual(database.remote_metadata(self.remote_name, 'version'), \
            self.remote_version)

    def test_remote_target_description(self):
        self.assertEqual(database.remote_metadata(self.remote_name, \
            'description'), self.remote_description)

    def test_remote_target_depends(self):
        self.assertEqual(database.remote_metadata(self.remote_name, 'depends'), \
            self.remote_depends)

    def test_remote_target_makedepends(self):
        self.assertEqual(database.remote_metadata(self.remote_name, \
            'makedepends'), self.remote_makedepends)

    def test_remote_target_optdepends(self):
        self.assertEqual(database.remote_metadata(self.remote_name, \
            'optdepends'), self.remote_optdepends)

    def test_remote_target_checkdepends(self):
        self.assertEqual(database.remote_metadata(self.remote_name, \
            'checkdepends'), [self.remote_name])

    def test_remote_target_source(self):
        self.assertEqual(database.remote_metadata(self.remote_name, 'sources'), \
            ['http://ftp.gnu.org/gnu/glibc/glibc-2.16.0.tar.xz'])

    def test_remote_target_pgpkeys(self):
        self.assertEqual(database.remote_metadata(self.remote_name, 'pgpkeys'), \
            self.remote_pgpkeys)

    def test_remote_target_options(self):
        self.assertEqual(database.remote_metadata(self.remote_name, 'options'), \
            self.remote_options)

    def test_remote_target_backup(self):
        self.assertEqual(database.remote_metadata(self.remote_name, 'backup'), \
            self.remote_backup)

    def test_remote_target_footprint(self):
        self.assertEqual(database.local_metadata(self.local_name, 'footprint'), \
            self.local_footprint)

    def test_remote_mdepends_true(self):
        self.assertEqual(database.remote_mdepends(self.remote_name), \
            self.remote_depends + self.remote_makedepends)

    def test_remote_database_update(self):
        pre = database.remote_all()
        misc.dir_remove('%s/repositories/test/%s' % \
            (database.CACHE_DIR, self.remote3_name))
        post = database.remote_all()
        self.assertFalse(pre == post)

    # local targets checks
    def test_local_target_version(self):
        self.assertEqual(database.local_metadata(self.local_name, 'version'), \
            self.local_version)

    def test_local_target_description(self):
        self.assertEqual(database.local_metadata(self.local_name, \
            'description'), self.local_description)

    def test_local_target_depends(self):
        self.assertEqual(database.local_metadata(self.local_name, 'depends'), \
            self.local_depends)

    def test_local_target_depends_empty(self):
        self.assertEqual(database.local_metadata(self.local3_name, 'depends'), \
            [])

    def test_local_target_optdepends(self):
        self.assertEqual(database.local_metadata(self.local_name, 'optdepends'), \
            [self.remote2_name])

    def test_local_target_size(self):
        self.assertEqual(database.local_metadata(self.local_name, 'size'), \
            self.local_size)

    def test_local_search_true(self):
        self.assertTrue(database.local_search(self.local_name))

    def test_local_search_false(self):
        self.assertEqual(database.local_search('foobar'), None)

    def test_local_belongs_true(self):
        self.assertEqual(database.local_belongs('/etc/dummy.conf'), \
            [self.local_name])

    def test_local_belongs_false(self):
        self.assertEqual(database.local_belongs('/lib/foobar.so'), [])

    def test_local_uptodate_version_true(self):
        self.assertTrue(database.local_uptodate('dummy'))

    def test_local_uptodate_version_false(self):
        self.assertFalse(database.local_uptodate('dummy2'))

    def test_local_uptodate_release_false(self):
        self.assertFalse(database.local_uptodate('dummy3'))

    def test_local_rdepends_true(self):
        self.assertEqual(database.local_rdepends(self.local_name), \
            self.local2_name.split())

    def test_local_database_update_true(self):
        pre = database.local_all()
        misc.dir_remove('%s/%s' % (database.LOCAL_DIR, self.local3_name))
        post = database.local_all()
        self.assertFalse(pre == post)

    # misc checks
    def test_file_mime_python(self):
        self.assertEqual(misc.file_mime('libmisc.py'), 'text/x-python')

    def test_file_mime_makefile(self):
        self.assertEqual(misc.file_mime('Makefile'), 'text/x-makefile')

    def test_system_communicate_output_true(self):
        self.assertEqual(misc.system_communicate(('echo', 'output')), 'output')

    @unittest.skipIf(misc.python3, 'Python 3000')
    def test_type_str_true(self):
        misc.typecheck('foo', (types.StringType))

    @unittest.skipIf(misc.python3, 'Python 3000')
    def test_type_str_false(self):
        with self.assertRaises(TypeError):
            misc.typecheck(1, (types.StringType))

    @unittest.skipIf(misc.python3, 'Python 3000')
    def test_type_int_true(self):
        misc.typecheck(1991, (types.IntType))

    @unittest.skipIf(misc.python3, 'Python 3000')
    def test_type_int_false(self):
        with self.assertRaises(TypeError):
            misc.typecheck('bar', (types.IntType))

    @unittest.skipIf(misc.python3, 'Python 3000')
    def test_type_float_true(self):
        misc.typecheck(11.0, (types.FloatType))

    @unittest.skipIf(misc.python3, 'Python 3000')
    def test_type_float_false(self):
        with self.assertRaises(TypeError):
            misc.typecheck(7, (types.UnicodeType))

    @unittest.skipIf(misc.python3, 'Python 3000')
    def test_type_list_true(self):
        misc.typecheck(['a', 'b', 'c'], (types.ListType))

    @unittest.skipIf(misc.python3, 'Python 3000')
    def test_type_list_false(self):
        with self.assertRaises(TypeError):
            misc.typecheck('meh', (types.ListType))

    @unittest.skipIf(misc.python3, 'Python 3000')
    def test_type_list_false2(self):
        with self.assertRaises(TypeError):
            misc.typecheck(('f', 'o', '0'), (types.ListType))

    @unittest.skipIf(misc.python3, 'Python 3000')
    def test_type_tuple_true(self):
        misc.typecheck(('a', 'b', 'c'), (types.TupleType))

    @unittest.skipIf(misc.python3, 'Python 3000')
    def test_type_tuple_false(self):
        with self.assertRaises(TypeError):
            misc.typecheck(3.14, (types.TupleType))

suite = unittest.TestLoader().loadTestsFromTestCase(TestSuite)
result = unittest.TextTestRunner(verbosity=2).run(suite)
if result.failures or result.errors:
    sys.exit(1)
