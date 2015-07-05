#!/usr/bin/python2

'''
A messaging module with fancy printing, logging and piped process handling.

Unbuffered() is not something you should deal with, it will be used to override
standard output forcing it to flush if stdout is not a TTY. Same goes for
colors - if stdout is not TTY then they will be automatically disabled. And
the cherry here is the logging, it logs everything passed to the messager
unless told otherwise.
'''

import sys, curses, syslog

# http://stackoverflow.com/questions/107705/python-output-buffering
class Unbuffered(object):
    ''' Override output behaviour to suitable for piped process '''
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
            if isinstance(msg, (list, tuple, bool)):
                msg = str(msg)
            if not isinstance(msg, str):
                msg = msg.encode('utf-8')
            syslog.syslog(status, msg)

    def info(self, msg, marker=None):
        ''' Print message with information status '''
        if not marker is None:
            print('%s* %s%s: %s%s%s' % (self.cmarker, self.cnormal, msg, \
                self.cinfo, marker, self.cnormal))
            self.log_message(syslog.LOG_INFO, '%s: %s' % (msg, marker))
        else:
            print('%s* %s%s' % (self.cmarker, self.cnormal, msg))
            self.log_message(syslog.LOG_INFO, msg)

    def warning(self, msg, marker=None):
        ''' Print message with warning status '''
        if not marker is None:
            sys.stderr.write('%s* %s%s: %s%s%s\n' % (self.cwarning, \
                self.cnormal, msg, self.cwarning, marker, self.cnormal))
            self.log_message(syslog.LOG_ALERT, '%s: %s' % (msg, marker))
        else:
            sys.stderr.write('%s* %s%s\n' % (self.cwarning, self.cnormal, msg))
            self.log_message(syslog.LOG_ALERT, msg)

    def critical(self, msg, marker=None):
        ''' Print message with critical status '''
        if not marker is None:
            if self.CATCH:
                raise Exception(msg, marker)
            sys.stderr.write('%s* %s%s: %s%s%s\n' % (self.ccritical, \
                self.cnormal, msg, self.ccritical, marker, self.cnormal))
            self.log_message(syslog.LOG_CRIT, '%s: %s' % (msg, marker))
        else:
            if self.CATCH:
                raise Exception(msg)
            sys.stderr.write('%s* %s%s\n' % (self.ccritical, self.cnormal, msg))
            self.log_message(syslog.LOG_CRIT, msg)

    def debug(self, msg, marker=None):
        ''' Print message with debug status '''
        if self.DEBUG:
            if not marker is None:
                print('%s* %s%s: %s%s%s' % (self.cdebug, self.cnormal, msg, \
                    self.cdebug, marker, self.cnormal))
                self.log_message(syslog.LOG_DEBUG, '%s: %s' % (msg, marker))
            else:
                print('%s* %s%s' % (self.cdebug, self.cnormal, msg))
                self.log_message(syslog.LOG_DEBUG, msg)

    def sub_info(self, msg, marker=None):
        ''' Print sub-message with information status '''
        if not marker is None:
            print('%s  -> %s%s: %s%s%s' % (self.cmarker, self.cnormal, msg, \
                self.cinfo, marker, self.cnormal))
            self.log_message(syslog.LOG_INFO, '%s: %s' % (msg, marker))
        else:
            print('%s  -> %s%s' % (self.cmarker, self.cnormal, msg))
            self.log_message(syslog.LOG_INFO, msg)

    def sub_warning(self, msg, marker=None):
        ''' Print sub-message with warning status '''
        if not marker is None:
            sys.stderr.write('%s  -> %s%s: %s%s%s\n' % (self.cwarning, \
                self.cnormal, msg, self.cwarning, marker, self.cnormal))
            self.log_message(syslog.LOG_ALERT, '%s: %s' % (msg, marker))
        else:
            sys.stderr.write('%s  -> %s%s\n' % (self.cwarning, \
                self.cnormal, msg))
            self.log_message(syslog.LOG_ALERT, msg)

    def sub_critical(self, msg, marker=None):
        ''' Print sub-message with critical status '''
        if not marker is None:
            if self.CATCH:
                raise Exception(msg, marker)
            sys.stderr.write('%s  => %s%s: %s%s%s\n' % (self.ccritical, \
                self.cnormal, msg, self.ccritical, marker, self.cnormal))
            self.log_message(syslog.LOG_CRIT, '%s: %s' % (msg, marker))
        else:
            if self.CATCH:
                raise Exception(msg)
            sys.stderr.write('%s  => %s%s\n' % (self.ccritical, \
                self.cnormal, msg))
            self.log_message(syslog.LOG_CRIT, msg)

    def sub_debug(self, msg, marker=None):
        ''' Print sub-message with debug status '''
        if self.DEBUG:
            if not marker is None:
                print('%s  -> %s%s: %s%s%s' % (self.cdebug, self.cnormal, \
                    msg, self.cdebug, marker, self.cnormal))
                self.log_message(syslog.LOG_DEBUG, '%s: %s' % (msg, marker))
            else:
                print('%s  -> %s%s' % (self.cdebug, self.cnormal, msg))
                self.log_message(syslog.LOG_DEBUG, msg)
