#!/usr/bin/python

''' System initializer '''

import os, sys, subprocess, ConfigParser, shlex, curses

import libmessage
message = libmessage.Message()
import libmisc
misc = libmisc.Misc()


class Init(object):
    ''' System initializer '''
    def __init__(self):
        ''' Initializer '''
        self.initialized = False
        self.ipc = '/run/init.fifo'
        # set custom log file
        message.LOG_FILE = '/var/log/init.log'
        # FIXME: bad reference
        self.shell = False

    def ipc_create(self):
        ''' Create fifo for communication '''
        if not os.path.exists(self.ipc):
            misc.file_write(self.ipc, '')
            # os.mkfifo(self.ipc)
        # set owner of IPC to root:power
        os.chown(self.ipc, 0, 20)
        # sadly, something is wrong with mkfifo permissions set
        os.chmod(self.ipc, 0664)
        os.setsid()
        # to ensure fifo cleanup only from the running daemon not
        # possible second instance variable is asigned
        self.initialized = True

    def ipc_read(self):
        ''' Read IPC and return a tuple of service and action '''
        if not os.path.exists(self.ipc):
            self.ipc_create()
            return None, None
        content = misc.file_read_nonblock(self.ipc).strip().split('#')
        service = content[0]
        # in some cases no service is written, use service for action
        if len(content) == 2:
            action = content[1]
        else:
            action = None
        return service, action

    def ipc_write(self, service, action):
        ''' Write service and action to IPC '''
        misc.file_write(self.ipc, service + '#' + action)

    def service_check(self, service):
        ''' Check if service is valid '''
        spath = os.path.join('/etc/services.d', service)
        if os.path.isfile(spath) or os.path.isfile(service):
            return True
        return False

    def service_read(self, service):
        ''' Read service file '''
        config = ConfigParser.SafeConfigParser()
        config.read(service)

        # asign variables to the object
        self.service_name = os.path.basename(service.replace('.conf', ''))
        self.start_command = config.get('Exec', 'Start')
        self.stop_command = config.get('Exec', 'Stop')
        self.start_message = config.get('Options', 'StartMsg')
        self.stop_message = config.get('Options', 'StopMsg')
        self.wait = config.getboolean('Options', 'Wait')
        self.shell = config.getboolean('Options', 'Shell')
        self.restart = config.getboolean('Options', 'Restart')
        self.delay = config.getboolean('Options', 'Delay')

    def exec_command(self, command):
        ''' Exec command in sane manner '''
        # split command the smart way preserving brackets
        if not self.shell:
            command = shlex.split(command)
        pipe = subprocess.Popen(command, shell=self.shell,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env={'PATH': '/usr/sbin:/usr/bin:/sbin:/bin'})
        if self.wait:
            pipe.wait()
        if pipe.returncode > 0:
            stdout, stderr = pipe.communicate()
            if stderr:
                message.sub_warning(stderr)
            elif stdout:
                message.sub_warning(stdout)
            else:
                message.sub_warning('Command failed with status',
                    pipe.returncode)
            return pipe.returncode

    def service_start(self, service):
        ''' Start a service '''
        self.service_check(service)
        self.service_read(service)
        if self.start_command:
            if self.start_message:
                message.sub_info(self.start_message)
            else:
                message.sub_info('Starting service', self.service_name)
            self.exec_command(self.start_command)

    def service_stop(self, service):
        ''' Stop a service '''
        self.service_check(service)
        self.service_read(service)
        if self.stop_command:
            if self.stop_message:
                message.sub_info(self.stop_message)
            else:
                message.sub_info('Stopping service', self.service_name)
            self.exec_command(self.stop_command)

    def system_boot(self):
        ''' Start all services during system boot '''
        for service in sorted(misc.list_files('/etc/services.d')):
            self.service_start(service)

    def system_reboot(self):
        ''' Stop all services and reboot the system '''
        for service in sorted(misc.list_files('/etc/services.d')):
            self.service_stop(service)
        message.info('Rebooting system...')
        # FIXME: do some ctype magic
        self.exec_command('reboot -f')

    def system_shutdown(self):
        ''' Stop all services and shutdown the system '''
        for service in sorted(misc.list_files('/etc/services.d')):
            self.service_stop(service)
        message.info('Shutting down system...')
        # FIXME: do some ctype magic
        self.exec_command('shutdown -n -h now')
