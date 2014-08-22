#!/bin/python2

import sys, curses
from datetime import datetime


# http://stackoverflow.com/questions/107705/python-output-buffering
class Unbuffered(object):
    ''' Override print behaviour '''
    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        ''' Write to stdout without buffering '''
        self.stream.write(data)
        self.stream.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)


class Message(object):
    ''' Print fancy messages with logging '''
    def __init__(self):
        self.LOG = True
        self.LOG_FILE = '/var/log/syslog.log'
        self.DEBUG = False

        try:
            curses.setupterm()
            self.COLORS = curses.tigetnum('colors')
        except curses.error:
            self.COLORS = 0

        if self.COLORS >= 8 and sys.stdout.isatty():
            self.cmarker = '\033[1;34m'
            self.cinfo = '\033[1;32m'
            self.cwarning = '\033[1;33m'
            self.ccritical = '\033[1;31m'
            self.cdebug = '\033[1;36m'
            self.cnormal = '\033[0m'
        else:
            self.cmarker = ''
            self.cinfo = ''
            self.cwarning = ''
            self.ccritical = ''
            self.cdebug = ''
            self.cnormal = ''
            sys.stdout = Unbuffered(sys.stdout)

        self.log_message('--------------------- %s ---------------------' % \
            datetime.today())

    def log_message(self, msg):
        ''' Log message to file '''
        if self.LOG:
            try:
                lfile = open(self.LOG_FILE, 'a')
                lfile.write(msg + '\n')
                lfile.close()
            except:
                pass

    def info(self, msg, marker=None):
        ''' Print message with INFO status '''
        if not marker is None:
            print('%s* %s%s: %s%s%s' % (self.cmarker, self.cnormal, msg, \
                self.cinfo, marker, self.cnormal))
            self.log_message('[INFO] %s: %s' % (msg, marker))
        else:
            print('%s* %s%s' % (self.cmarker, self.cnormal, msg))
            self.log_message('[INFO] %s' % msg)


    def warning(self, msg, marker=None):
        ''' Print message with WARNING status '''
        if not marker is None:
            sys.stderr.write('%s* %s%s: %s%s%s\n' % (self.cwarning, \
                self.cnormal, msg, self.cwarning, marker, self.cnormal))
            self.log_message('[WARNING] %s: %s' % (msg, marker))
        else:
            sys.stderr.write('%s* %s%s\n' % (self.cwarning, self.cnormal, msg))
            self.log_message('[WARNING] %s' % msg)

    def critical(self, msg, marker=None):
        ''' Print message with CRITICAL status '''
        if not marker is None:
            sys.stderr.write('%s* %s%s: %s%s%s\n' % (self.ccritical, \
                self.cnormal, msg, self.ccritical, marker, self.cnormal))
            self.log_message('[CRITICAL] %s: %s' % (msg, marker))
        else:
            sys.stderr.write('%s* %s%s\n' % (self.ccritical, self.cnormal, msg))
            self.log_message('[CRITICAL] %s' % msg)

    def debug(self, msg, marker=None):
        ''' Print message with DEBUG status '''
        if self.DEBUG:
            if not marker is None:
                print('%s* %s%s: %s%s%s' % (self.cdebug, self.cnormal, msg, \
                    self.cdebug, marker, self.cnormal))
                self.log_message('[DEBUG] %s: %s' % (msg, marker))
            else:
                print('%s* %s%s' % (self.cdebug, self.cnormal, msg))
                self.log_message('[DEBUG] %s' % msg)

    def sub_info(self, msg, marker=None):
        ''' Print sub-message with INFO status '''
        if not marker is None:
            print('%s  => %s%s: %s%s%s' % (self.cmarker, self.cnormal, msg, \
                self.cinfo, marker, self.cnormal))
            self.log_message('[INFO] %s: %s' % (msg, marker))
        else:
            print('%s  => %s%s' % (self.cmarker, self.cnormal, msg))
            self.log_message('[INFO] %s' % msg)

    def sub_warning(self, msg, marker=None):
        ''' Print sub-message with WARNING status '''
        if not marker is None:
            sys.stderr.write('%s  => %s%s: %s%s%s\n' % (self.cwarning, \
                self.cnormal, msg, self.cwarning, marker, self.cnormal))
            self.log_message('[WARNING] %s: %s' % (msg, marker))
        else:
            sys.stderr.write('%s  => %s%s\n' % (self.cwarning, self.cnormal, msg))
            self.log_message('[WARNING] %s' % msg)

    def sub_critical(self, msg, marker=None):
        ''' Print sub-message with CRITICAL status '''
        if not marker is None:
            sys.stderr.write('%s  => %s%s: %s%s%s\n' % (self.ccritical, \
                self.cnormal, msg, self.ccritical, marker, self.cnormal))
            self.log_message('[CRITICAL] %s: %s' % (msg, marker))
        else:
            sys.stderr.write('%s  => %s%s\n' % (self.ccritical, self.cnormal, msg))
            self.log_message('[CRITICAL] %s' % msg)

    def sub_debug(self, msg, marker=None):
        ''' Print sub-message with DEBUG status '''
        if self.DEBUG:
            if not marker is None:
                print('%s  => %s%s: %s%s%s' % (self.cdebug, self.cnormal, msg, \
                    self.cdebug, marker, self.cnormal))
                self.log_message('[DEBUG] %s: %s' % (msg, marker))
            else:
                print('%s  => %s%s' % (self.cdebug, self.cnormal, msg))
                self.log_message('[DEBUG] %s' % msg)
