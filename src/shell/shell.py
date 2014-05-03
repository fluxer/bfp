#!/usr/bin/python

''' Basic shell '''

import os, sys, subprocess, cmd

class Shell(cmd.Cmd):
    ''' Custom cmd class '''
    # intro = '\n << Welcome! >> \n'
    status = 0
    prompt = os.path.realpath(os.curdir) + ', 0 >> '
    path = ('/sbin', '/bin', '/usr/sbin', '/usr/bin')

    def external(self, args):
        ''' Execute program with optional arguments passed '''
        p = subprocess.Popen(args.split())
        p.wait()
        # change prompt to show current directory and command return code
        self.prompt = os.path.realpath(os.curdir) + ', ' + str(p.returncode) + ' >> '

    def do_foo(self, args):
        ''' Foo command, eastern egg '''
        print('You foo, go to bar!')

    def do_cd(self, args):
        ''' Change current directory '''
        # change directory
        os.chdir(args)
        # change prompt to show current directory
        self.prompt = os.path.realpath(os.curdir) + ', 0 >> '

    def do_exit(self, args):
        ''' Exit the shell '''
        sys.exit(0)

    def completedefault(self, text, line, begidx, endidx):
        ''' Autocomplete default command '''
        sall = []
        # easy split of the line
        command, args, line = self.parseline(line)
        if args:
            sdir = os.path.dirname(args)
            sbase = os.path.basename(args)
            if os.path.isdir(sdir):
                for i in os.listdir(sdir):
                    if i.startswith(sbase):
                        sall.append(i)
            return sall
        else:
            return os.listdir(os.curdir)

    def default(self, args):
        ''' External binary callback '''
        # easy split of the line
        command, args, line = self.parseline(args)
        # check if external command if available
        for path in self.path:
            if os.path.isfile(path + '/' + command):
                return self.external(line)
        # execute internal command or bail out
        return cmd.Cmd.default(self, args)

try:
    Shell().cmdloop()
except KeyboardInterrupt:
    print('\nKeyboard Interrupt')
    sys.exit(2)
except Exception as detail:
    print('ERROR', detail)
    sys.exit(1)
