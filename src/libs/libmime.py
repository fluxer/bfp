#!/usr/bin/python

import os, ConfigParser, subprocess
import libmisc
misc = libmisc.Misc()

class Mime(object):
    def __init__(self):
        self.conf = ConfigParser.ConfigParser()
        self.read()

    def read(self):
        self.conf.read('/etc/mime.conf')

    def write(self):
        with open('/etc/mime.conf', 'a+') as fd:
            self.conf.write(fd)

    def get_icon(self, smime):
        if self.conf.has_section(smime):
            return self.conf.get(smime, 'icon')
        return None

    def get_program(self, smime):
        if self.conf.has_section(smime):
            return self.conf.get(smime, 'program')
        return None

    def get_mimes(self):
        # return self.conf.sections()
        mimes = []
        for line in misc.system_output((misc.whereis('file'), '-r', '-l')).splitlines(): 
            a = line.split(' : ')
            if len(a) == 2:
                mime = a[1].split('[')[1].rstrip(']')
                if mime and not mime in mimes:
                    mimes.append(mime)
        return sorted(mimes)

    def get_programs(self):
        programs = misc.list_files('/bin')
        if os.geteuid() == 0:
            programs.extend(misc.list_files('/sbin'))
        return programs

    def open(self, svar):
        smime = misc.file_mime(svar)
        sprogram = self.get_program(smime)
        if sprogram:
            subprocess.call((sprogram, svar))
        else:
            raise(Exception('Unregistered mime', smime))

    def register(self, smime, sprogram, sicon=''): 
        if self.conf.has_section(smime):
            return
        self.read()
        self.conf.add_section(smime)
        self.conf.set(smime, 'program', sprogram)
        self.conf.set(smime, 'icon', sicon)
        self.write()

    def unregister(self, smime):
        if not self.conf.has_section(smime):
            return
        self.read()
        self.conf.remove_option(smime, 'program')
        self.conf.remove_option(smime, 'icon')
        self.conf.remove_section(smime)
        self.write()

