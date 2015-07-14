#!/usr/bin/python2

import gettext
_ = gettext.translation('spm', fallback=True).gettext

import libmessage, libspm, libmisc, time
message = libmessage.Message()
misc = libmisc.Misc()

# in case someone wants to use the pluging without setting up a parser a simple
# class that gets the job done is a nice to have
class Goodbye(libspm.Source):
    def __init__(self, targets):
        super(Goodbye, self).__init__(targets)
        self.targets = targets
        self.backupdir = '/backup'
        misc.dir_create(self.backupdir)

    def main(self):
        reboot = False
        # schedule systme reboot if kernel is going to be installed
        if 'linux' in self.targets:
            reboot = True
        # do you care about your decoder?
        if 'ffmpeg' in self.targets:
            target_version = database.local_metadata(target, 'version')
            target_packfile = '%s/%s_%s.tar.xz' % (self.backupdir, \
                os.path.basename(target), target_version)
            content = database.local_metadata(target, 'footprint')
            # add metadata directory, it is not listed in the footprint
            content.append('%s/%s' % (libspm.LOCAL_DIR, target))

            message.sub_info(_('Compressing'), target_packfile)
            misc.archive_compress(content, target_packfile, '/')
        # wanna rollback in case of driver messup?
        if 'nvidia' in self.targets:
            misc.system_command((misc.whereis('btrfs'), 'subvolume', \
                'snapshot', '/', '%s/%s' % \
                 (self.backupdir, time.strftime('%Y.%m.%d-%H.%M.%S'))))
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