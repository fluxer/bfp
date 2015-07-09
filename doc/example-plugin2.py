#!/usr/bin/python2

import gettext
_ = gettext.translation('spm', fallback=True).gettext

import libmessage, libspm, libmisc
message = libmessage.Message()
misc = libmisc.Misc()

# in case someone wants to use the pluging without setting up a parser a simple
# class that gets the job done is a nice to have
class Goodbye(libspm.Source):
    def main(self):
        reboot = False
        # schedule systme reboot if the kernel is going to be installed
        if 'linux' in self.targets:
            reboot = True
        self.autosource(self.targets, automake=True)
        if reboot:
            misc.system_command(misc.whereis('reboot'))


# that's what spm-tools is dealing with at runtime
class Main(object):
    def __init__(self, subparsers):
        goodbye_parser = subparsers.add_parser('goodbye')
        goodbye_parser.add_argument('TARGETS', nargs='+', type=str, \
            help=_('Targets to apply actions on'))

    def run(self, ARGS):
        if ARGS.mode == 'goodbye':
            message.info(_('Runtime information'))
            message.sub_info(_('TARGETS'), ARGS.TARGETS)
            message.info(_('Poking the world...'))
            m = Goodbye(ARGS.TARGETS)
            m.main()


# finally, standalone usage. without Goodbye() anything that wants to access the
# pluging will have to write similar code instead of just Goodbye(['foo']).main()
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(prog='spm-tools', \
        description='Source Package Manager Tools Goodbye World plugin')
    subparsers = parser.add_subparsers(dest='mode')
    m = Main(subparsers)
    ARGS = parser.parse_args()
    m.run(ARGS)