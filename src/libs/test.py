#!/bin/python2

import unittest, tempfile, os, sys, types

import libmisc
misc = libmisc.Misc()
import libpackage
database = libpackage.Database()


class TestSuite(unittest.TestCase):
    database.ROOT_DIR = tempfile.mkdtemp()

    def create_remote(self, name, sdir, version, description, depends='', \
        makedepends='', sources='', options='', backup=''):
        sdir = database.CACHE_DIR + '/repositories/test/' + name
        os.makedirs(sdir)
        srcbuild = open(sdir + '/SRCBUILD', 'w')
        srcbuild.write('version=' + version)
        srcbuild.write('\ndescription="' + description + '"')
        srcbuild.write('\ndepends=(' + misc.string_convert(depends) + ')')
        srcbuild.write('\nmakedepends=(' + misc.string_convert(makedepends) + ')')
        srcbuild.write('\ncheckdepends=(' + name + ')')
        srcbuild.write('\nsources=(' + misc.string_convert(sources) + ')')
        srcbuild.write('\noptions=(' + misc.string_convert(options) + ')')
        srcbuild.write('\nbackup=(' + misc.string_convert(backup) + ')')
        srcbuild.close()

    def create_local(self, name, sdir, version, description, depends='', \
            size='1', footprint='\n'):
        os.makedirs(sdir)
        metadata = open(sdir + '/metadata', 'w')
        metadata.write('version=' + version)
        metadata.write('\ndescription=' + description)
        metadata.write('\ndepends=' + depends)
        metadata.write('\nsize=' + size)
        metadata.close()
        fprint = open(sdir + '/footprint', 'w')
        fprint.write(footprint)
        fprint.close()

    def setUp(self):
        database.CACHE_DIR = database.ROOT_DIR + '/var/cache/spm'
        database.BUILD_DIR = database.ROOT_DIR + '/var/tmp/spm'
        database.LOCAL_DIR = database.ROOT_DIR + '/var/local/spm'

        if os.path.isdir(database.ROOT_DIR):
            misc.dir_remove(database.ROOT_DIR)

        os.makedirs(database.ROOT_DIR)
        os.makedirs(database.CACHE_DIR)
        os.makedirs(database.BUILD_DIR)
        os.makedirs(database.LOCAL_DIR)

        # dummy remote target
        self.remote_name = 'glibc'
        self.remote_dir = database.CACHE_DIR + '/repositories/test/' + \
            self.remote_name
        self.remote_version = '2.16.1'
        self.remote_description = 'SPM test target'
        self.remote_depends = ['filesystem', 'linux-api-headers', 'tzdata']
        self.remote_makedepends = ['circular']
        self.remote_source = ['\n', '', 'http://ftp.gnu.org/gnu/glibc/glibc-2.16.0.tar.xz']
        self.remote_options = ['!binaries', 'shared', '!static', 'man']
        self.remote_backup = ['etc/ld.so.conf', 'etc/nsswitch.conf']
        self.create_remote(self.remote_name, self.remote_dir, \
            self.remote_version, self.remote_description, self.remote_depends, \
            self.remote_makedepends, self.remote_source, self.remote_options, \
            self.remote_backup)

        # second dummy remote target
        self.remote2_name = 'dummy'
        self.remote2_dir = database.CACHE_DIR + '/repositories/test/' + \
            self.remote2_name
        self.remote2_version = '999'
        self.remote2_description = 'SPM circular test target'
        self.remote2_makedepends = [self.remote_name]
        self.create_remote(self.remote2_name, self.remote2_dir, \
            self.remote2_version, self.remote2_description, \
            makedepends=self.remote2_makedepends)

        # third dummy remote target
        self.remote3_name = 'dummy2'
        self.remote3_dir = database.CACHE_DIR + '/repositories/test/' + \
            self.remote3_name
        self.remote3_version = '1.0.1'
        self.remote3_description = 'SPM up-to-date test target'
        self.remote3_makedepends = [self.remote_name]
        self.create_remote(self.remote3_name, self.remote3_dir, \
            self.remote3_version, self.remote3_description, \
            makedepends=self.remote3_makedepends)

        # dummy local target
        self.local_name = 'dummy'
        self.local_dir = database.LOCAL_DIR + '/' + self.local_name
        self.local_version = '9999'
        self.local_description = 'SPM dummy local test target'
        self.local_depends = self.remote_name
        self.local_size = '12345'
        self.local_footprint = '/etc/dummy.conf\n/lib/libdummy.so'
        self.create_local(self.local_name, self.local_dir, \
            self.local_version, self.local_description, self.local_depends, \
            self.local_size, self.local_footprint)

        # second dummy local target
        self.local2_name = 'dummy2'
        self.local2_dir = database.LOCAL_DIR + '/' + self.local2_name
        self.local2_version = '1.0.0'
        self.local2_description = 'SPM dummy reverse test target'
        self.local2_depends = self.local_name
        self.local2_size = '12345'
        self.local2_footprint = '/etc/dummy2.conf\n/lib/libdummy2.so'
        self.create_local(self.local2_name, self.local2_dir, \
            self.local2_version, self.local2_description, \
            self.local2_depends, self.local2_size, self.local2_footprint)

        # second dummy local target
        self.local3_name = 'dummy3'
        self.local3_dir = database.LOCAL_DIR + '/' + self.local3_name
        self.local3_version = '1.0.0'
        self.local3_description = 'SPM dummy empty depends test target'
        self.local3_depends = ''
        self.local3_size = '12345'
        self.local3_footprint = ''
        self.create_local(self.local3_name, self.local3_dir, \
            self.local3_version, self.local3_description, \
            self.local3_depends, self.local3_size, self.local3_footprint)

    def tearDown(self):
        misc.dir_remove(database.ROOT_DIR)

    # string/regexp match checks
    def test_search_string_simple_true(self):
        self.assertTrue(misc.string_search('bar', 'foo_bar_baz'), True)

    def test_search_string_simple_false(self):
        self.assertEqual(misc.string_search('barz', 'foo_bar_baz'), [])

    def test_search_string_regexp(self):
        self.assertTrue(misc.string_search('ab+', 'abcbdef', escape=False), \
            True)

    def test_search_string_exact_begining_true(self):
        self.assertTrue(misc.string_search('foo', 'foo bar', exact=True), True)

    def test_search_string_exact_begining_false(self):
        self.assertEqual(misc.string_search('foo', 'foobar', exact=True), [])

    def test_search_string_exact_middle_true(self):
        self.assertTrue(misc.string_search('bar', 'foo\tbar\nbaz', \
            exact=True), True)

    def test_search_string_exact_middle_false(self):
        self.assertEqual(misc.string_search('bar', 'foobarbaz', exact=True), \
            [])

    def test_search_string_exact_middle_false2(self):
        self.assertEqual(misc.string_search('.(bar).', 'foo bar baz', \
            exact=True), [])

    def test_search_string_exact_end_true(self):
        self.assertTrue(misc.string_search('bar', 'foo\tbar', exact=True), \
            True)

    def test_search_string_exact_end_false(self):
        self.assertEqual(misc.string_search('bar', 'foobar', exact=True), [])

    def test_search_string_exact_in_list_true(self):
        self.assertTrue(misc.string_search('bar', ['foo', 'bar', 'baz'], \
            exact=True), True)

    def test_search_string_exact_in_list_false(self):
        self.assertEqual(misc.string_search('barz', ['foo', 'bar', 'baz'], \
            exact=True), [])

    def test_search_string_exact_escape(self):
        self.assertTrue(misc.string_search('bar\nbaz', 'bar\nbaz', \
            exact=True, escape=True), True)

    # remote targets checks
    def test_remote_target_search_true(self):
        self.assertEqual(database.remote_search(self.remote_name), \
            self.remote_dir)

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

    def test_remote_target_checkdepends(self):
        self.assertEqual(database.remote_metadata(self.remote_name, \
            'checkdepends'), [self.remote_name])

    def test_remote_target_source(self):
        self.assertEqual(database.remote_metadata(self.remote_name, 'sources'), \
            ['http://ftp.gnu.org/gnu/glibc/glibc-2.16.0.tar.xz'])

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

    # local targets checks
    def test_local_target_version(self):
        self.assertEqual(database.local_metadata(self.local_name, 'version'), \
            self.local_version)

    def test_local_target_description(self):
        self.assertEqual(database.local_metadata(self.local_name, \
            'description'), self.local_description)

    def test_local_target_depends(self):
        self.assertEqual(database.local_metadata(self.local_name, 'depends'), \
            [self.local_depends])

    def test_local_target_depends_empty(self):
        self.assertEqual(database.local_metadata(self.local3_name, 'depends'), \
            [])

    def test_local_target_size(self):
        self.assertEqual(database.local_metadata(self.local_name, 'size'), \
            self.local_size)

    def test_local_search_true(self):
        self.assertTrue(database.local_search(self.local_name), True)

    def test_local_search_false(self):
        self.assertEqual(database.local_search('foobar'), None)

    def test_local_belongs_true(self):
        self.assertEqual(database.local_belongs('/etc/dummy.conf'), \
            [self.local_name])

    def test_local_belongs_false(self):
        self.assertEqual(database.local_belongs('/lib/foobar.so'), [])

    def test_local_uptodate_true(self):
        self.assertEqual(database.local_uptodate('dummy'), True)

    def test_local_uptodate_false(self):
        self.assertEqual(database.local_uptodate('dummy2'), False)

    def test_local_rdepends_true(self):
        self.assertEqual(database.local_rdepends(self.local_name), \
            self.local2_name.split())

    # misc checks
    def test_file_mime_python(self):
        self.assertEqual(misc.file_mime('libmagic.py'), 'text/x-python')

    def test_type_str_true(self):
        misc.typecheck('foo', (types.StringType))

    def test_type_str_false(self):
        with self.assertRaises(TypeError):
            misc.typecheck(1, (types.StringType))

    def test_type_int_true(self):
        misc.typecheck(1991, (types.IntType))

    def test_type_int_false(self):
        with self.assertRaises(TypeError):
            misc.typecheck('bar', (types.IntType))

    def test_type_float_true(self):
        misc.typecheck(11.0, (types.FloatType))

    def test_type_float_false(self):
        with self.assertRaises(TypeError):
            misc.typecheck(7, (types.UnicodeType))

    def test_type_list_true(self):
        misc.typecheck(['a', 'b', 'c'], (types.ListType))

    def test_type_list_false(self):
        with self.assertRaises(TypeError):
            misc.typecheck('meh', (types.ListType))

    def test_type_list_false2(self):
        with self.assertRaises(TypeError):
            misc.typecheck(('f', 'o', '0'), (types.ListType))

    def test_type_tuple_true(self):
        misc.typecheck(('a', 'b', 'c'), (types.TupleType))

    def test_type_tuple_false(self):
        with self.assertRaises(TypeError):
            misc.typecheck(3.14, (types.TupleType))

suite = unittest.TestLoader().loadTestsFromTestCase(TestSuite)
result = unittest.TextTestRunner(verbosity=2).run(suite)
if result.failures or result.errors:
    sys.exit(1)
