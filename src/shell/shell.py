#!/usr/bin/python

''' Basic shell '''

import os, sys, subprocess
try:
    # cmd2 is more feature rich
    import cmd2 as core
except ImportError:
    import cmd as core

class Shell(core.Cmd):
    # intro = '\n << Welcome! >> \n'
    status = 0
    prompt = os.path.realpath(os.curdir) + ', 0 >> '

    def exec_cmd(self, cmd):
        ''' Execute program with optional arguments passed '''
        p = subprocess.Popen(cmd.split())
        p.wait()
        self.prompt = os.path.realpath(os.curdir) + ', ' + str(p.returncode) + ' >> '

    def do_foo(self, args):
        ''' Foo command, eastern egg '''
        print('You foo, go to bar!')

    def do_cd(self, args):
        ''' Change current directory '''
        os.chdir(args)
        self.prompt = os.path.realpath(os.curdir) + ', 0 >> '

    def completedefault(self, text, line, begidx, endidx):
        ''' Autocomplete default command '''
        sdir = text
        if not sdir:
            sdir = os.curdir
        if text:
            sall = []
            for i in os.listdir(sdir):
                if i.startswith(text):
                    sall.append(i)
            return sall
        else:
            return os.listdir(os.curdir)

    def default(self, args):
        ''' External binary callback '''
        program = args.split()[0]
        for path in os.environ.get('PATH', '/usr/bin:/bin').split(':'):
            exe = path + '/' + program
            if os.path.isfile(exe):
                return self.exec_cmd(args)
        return core.Cmd.default(self, args)

''' Main loop '''
try:
    Shell().cmdloop()
except KeyboardInterrupt:
    print('\nKeyboard Interrupt')
    sys.exit(2)
except Exception as detail:
    print('ERROR', detail)
    sys.exit(1)
