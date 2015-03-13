#!/bin/python2

import sys, curses, syslog


# http://stackoverflow.com/questions/107705/python-output-buffering
class Unbuffered(object):
    ''' Override output behaviour '''
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
        self.DEBUG = False
        self.CATCH = False

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

    def log_message(self, status, msg):
        ''' Log message to system log '''
        if self.LOG:
            if status == 'info':
                status = syslog.LOG_INFO
            elif status == 'warning':
                status = syslog.LOG_ALERT
            elif status == 'critical':
                status = syslog.LOG_CRIT
            elif status == 'debug':
                status = syslog.LOG_DEBUG
            else:
                raise(Exception('Invalid log status', status))
            syslog.syslog(status, str(msg))

    def info(self, msg, marker=None):
        ''' Print message with information status '''
        if not marker is None:
            print('%s* %s%s: %s%s%s' % (self.cmarker, self.cnormal, msg, \
                self.cinfo, marker, self.cnormal))
            self.log_message('info', '%s: %s' % (msg, marker))
        else:
            print('%s* %s%s' % (self.cmarker, self.cnormal, msg))
            self.log_message('info', msg)


    def warning(self, msg, marker=None):
        ''' Print message with warning status '''
        if not marker is None:
            sys.stderr.write('%s* %s%s: %s%s%s\n' % (self.cwarning, \
                self.cnormal, msg, self.cwarning, marker, self.cnormal))
            self.log_message('warning', '%s: %s' % (msg, marker))
        else:
            sys.stderr.write('%s* %s%s\n' % (self.cwarning, self.cnormal, msg))
            self.log_message('warning', msg)

    def critical(self, msg, marker=None):
        ''' Print message with critical status '''
        if not marker is None:
            if self.CATCH:
                raise Exception(msg, marker)
            sys.stderr.write('%s* %s%s: %s%s%s\n' % (self.ccritical, \
                self.cnormal, msg, self.ccritical, marker, self.cnormal))
            self.log_message('critical', '%s: %s' % (msg, marker))
        else:
            if self.CATCH:
                raise Exception(msg)
            sys.stderr.write('%s* %s%s\n' % (self.ccritical, self.cnormal, msg))
            self.log_message('critical', msg)

    def debug(self, msg, marker=None):
        ''' Print message with debug status '''
        if self.DEBUG:
            if not marker is None:
                print('%s* %s%s: %s%s%s' % (self.cdebug, self.cnormal, msg, \
                    self.cdebug, marker, self.cnormal))
                self.log_message('debug', '%s: %s' % (msg, marker))
            else:
                print('%s* %s%s' % (self.cdebug, self.cnormal, msg))
                self.log_message('debug', msg)

    def sub_info(self, msg, marker=None):
        ''' Print sub-message with information status '''
        if not marker is None:
            print('%s  => %s%s: %s%s%s' % (self.cmarker, self.cnormal, msg, \
                self.cinfo, marker, self.cnormal))
            self.log_message('info', '%s: %s' % (msg, marker))
        else:
            print('%s  => %s%s' % (self.cmarker, self.cnormal, msg))
            self.log_message('info', msg)

    def sub_warning(self, msg, marker=None):
        ''' Print sub-message with warning status '''
        if not marker is None:
            sys.stderr.write('%s  => %s%s: %s%s%s\n' % (self.cwarning, \
                self.cnormal, msg, self.cwarning, marker, self.cnormal))
            self.log_message('warning', '%s: %s' % (msg, marker))
        else:
            sys.stderr.write('%s  => %s%s\n' % (self.cwarning, \
                self.cnormal, msg))
            self.log_message('warning', msg)

    def sub_critical(self, msg, marker=None):
        ''' Print sub-message with critical status '''
        if not marker is None:
            if self.CATCH:
                raise Exception(msg, marker)
            sys.stderr.write('%s  => %s%s: %s%s%s\n' % (self.ccritical, \
                self.cnormal, msg, self.ccritical, marker, self.cnormal))
            self.log_message('critical', '%s: %s' % (msg, marker))
        else:
            if self.CATCH:
                raise Exception(msg)
            sys.stderr.write('%s  => %s%s\n' % (self.ccritical, \
                self.cnormal, msg))
            self.log_message('critical', msg)

    def sub_debug(self, msg, marker=None):
        ''' Print sub-message with debug status '''
        if self.DEBUG:
            if not marker is None:
                print('%s  => %s%s: %s%s%s' % (self.cdebug, self.cnormal, \
                    msg, self.cdebug, marker, self.cnormal))
                self.log_message('debug', '%s: %s' % (msg, marker))
            else:
                print('%s  => %s%s' % (self.cdebug, self.cnormal, msg))
                self.log_message('debug', msg)
