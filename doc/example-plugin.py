#!/usr/bin/python2

import gettext
_ = gettext.translation('spm', fallback=True).gettext

import libmessage
message = libmessage.Message()

# in case someone wants to use the pluging without setting up a parser a simple
# class that gets the job done is a nice to have
class Hello(object):
    def __init__(self, msg='Hello World from SPM Tools!'):
        self.msg = msg

    def main(self):
        print(self.msg)


# that's what spm-tools is dealing with at runtime
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


# finally, standalone usage. without Hello() anything that wants to access the
# pluging will have to write similar code instead of just Hello('foo').main()
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(prog='spm-tools', \
        description='Source Package Manager Tools Hello World plugin')
    subparsers = parser.add_subparsers(dest='mode')
    m = Main(subparsers)
    ARGS = parser.parse_args()
    m.run(ARGS)