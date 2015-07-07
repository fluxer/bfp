#!/usr/bin/python2

import gettext
_ = gettext.translation('spm', fallback=True).gettext

import libmessage
message = libmessage.Message()


class Hello(object):
    def __init__(self, msg='Hello World from SPM Tools!'):
        self.msg = msg

    def main(self):
        print(self.msg)

class Main(object):
    def __init__(self, subparsers):
        hello_parser = subparsers.add_parser('hello')
        hello_parser.add_argument('-m', '--msg', \
            default='Hello World from SPM Tools!', \
            help=_('Set message to greet with'))

    def run(self, ARGS):
        if ARGS.mode == 'hello':
            message.info(_('Runtime information'))
            message.sub_info(_('MESSAGE'), ARGS.msg)
            message.info(_('Poking the world...'))
            m = Hello(ARGS.msg)
            m.main()
