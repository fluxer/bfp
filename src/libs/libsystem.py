#!/usr/bin/python

import subprocess, os, shlex, ConfigParser

import libmisc
import libmessage
message = libmessage.Message()
misc = libmisc.Misc()

class System(object):
    ''' Power manager '''
    def __init__(self):
        ''' Initializer '''
        self.initialized = False
        self.ipc = '/run/system.fifo'
        # set custom log file
        message.LOG_FILE = '/var/log/system.log'

        self.MOUNT_PRE = None
        self.MOUNT_POST = None
        self.UNMOUNT_PRE = None
        self.UNMOUNT_POST = None
        self.REBOOT_PRE = None
        self.SHUTDOWN_PRE = None
        self.SUSPEND_PRE = None
        self.SUSPEND_DISK = 'platform'
        self.SUSPEND_STATE = 'mem'
        self.SUSPEND_POST = None
        self.BATTERY_LID = 'shutdown'
        self.BATTERY_LOW = 'suspend'
        self.BATTERY_CPU = 'ondemand'
        self.POWER_LID = 'suspend'
        self.POWER_CPU = 'performance'
        self.POWER_BACKLIGHT = '15'

        # changed depending on power state
        self.LID_VALUE = self.POWER_LID
        self.CPU_VALUE = self.POWER_CPU
        self.BACKLIGHT_VALUE = self.POWER_BACKLIGHT

    def get_batteries(self):
        batteries = []
        for sdir in os.listdir('/sys/class/power_supply'):
            if sdir.startswith('BAT') or sdir == 'battery':
                batteries.append(os.path.join('/sys/class/power_supply', sdir))
        return batteries

    def get_cpus(self):
        cpus = []
        for sdir in os.listdir('/sys/devices/system/cpu/'):
            if misc.string_search('cpu\d', sdir, exact=True, escape=False):
                cpus.append(os.path.join('/sys/devices/system/cpu', sdir))
        return cpus

    def get_backlights(self):
        backlights = []
        for sdir in os.listdir('/sys/class/backlight'):
            if sdir.startswith('acpi_'):
                backlights.append(os.path.join('/sys/class/backlight', sdir))
        return backlights

    def check_battery_capacity(self):
        # FIXME: support multiple batteries, wrappers will get complex tough
        capacity = 'Unknown'
        for battery in self.get_batteries():
            fcapacity = os.path.join(battery, 'capacity')
            if os.path.isfile(fcapacity):
                capacity = misc.file_read(fcapacity).strip()
        return capacity

    def check_battery_status(self):
        # FIXME: support multiple batteries, wrappers will get complex tough
        status = 'Unknown'
        for battery in self.get_batteries():
            fstatus = os.path.join(battery, 'status')
            if os.path.isfile(fstatus):
                status = misc.file_read(fstatus).strip()
        return status

    def check_lid_status(self):
        status = 'Unknown'
        flid = '/proc/acpi/button/lid/LID/state'
        if os.path.isfile(flid):
            status = misc.file_read(flid).split()[1]
        return status

    def check_power_supply(self):
        # FIXME: this will be bogus with multiple batteries
        if self.check_battery_status() == 'Discharging':
            return 'DC'
        return 'AC'

    def check_backlight_max(self):
        # FIXME: support multiple screens, wrappers will get complex tough
        status = 'Unknown'
        for backlight in self.get_backlights():
            fstatus = os.path.join(backlight, 'max_brightness')
            if os.path.isfile(fstatus):
                status = misc.file_read(fstatus).strip()
        return status

    def check_mounted(self, string):
        for line in misc.file_readlines('/proc/mounts'):
            device, directory, type, options, fsck, fsck2 = line.split()
            if device == string or directory == string:
                return True
        return False


    def pre_actions(self, actions):
        if not actions:
            return
        for action in actions:
            message.sub_info('Executing pre-action', action)
            subprocess.check_call((action))

    def post_actions(self, actions):
        if not actions:
            return
        for action in actions:
            message.sub_info('Executing post-action', action)
            subprocess.check_call((action))

    def do_boot(self):
        ''' Start all services during system boot '''
        for service in sorted(misc.list_files('/etc/services.d')):
            self.service_start(service)

    def do_reboot(self):
        ''' Stop all services and reboot the system '''
        for service in sorted(misc.list_files('/etc/services.d')):
            self.service_stop(service)
        message.info('Rebooting system...')
        # FIXME: do some ctype magic
        self.exec_command('reboot -f')

    def do_shutdown(self):
        ''' Stop all services and shutdown the system '''
        for service in sorted(misc.list_files('/etc/services.d')):
            self.service_stop(service)
        message.info('Shutting down system...')
        # FIXME: do some ctype magic
        self.exec_command('shutdown -c -P -h now')

    def do_suspend(self):
        message.sub_info('Suspending system...')
        if not misc.file_search(self.SUSPEND_DISK, '/sys/power/disk'):
            message.sub_critical('Unsupported disk mode', self.SUSPEND_DISK)
            return
        elif not misc.file_search(self.SUSPEND_STATE, '/sys/power/state'):
            message.sub_critical('Unsupported state mode', self.SUSPEND_STATE)
            return

        self.pre_actions(self.SUSPEND_PRE)
        misc.file_write('/sys/power/disk', self.SUSPEND_DISK)
        misc.file_write('/sys/power/state', self.SUSPEND_STATE)
        self.post_actions(self.SUSPEND_POST)

    def do_mount(self, device):
        message.sub_info('Mounting device', device)
        self.pre_actions(self.MOUNT_PRE)
        directory = '/media/' + os.path.basename(device)
        if not os.path.isdir(directory):
            os.makedirs(directory)
        if not self.check_mounted(device):
            subprocess.check_call((misc.whereis('mount'), device, directory))
        else:
            return
        self.post_actions(self.MOUNT_POST)

    def do_unmount(self, device):
        message.sub_info('Unmounting device', device)
        self.pre_actions(self.UNMOUNT_PRE)
        directory = '/media/' + os.path.basename(device)
        if self.check_mounted(device):
            subprocess.check_call((misc.whereis('umount'), device))
        elif os.path.ismount(directory):
            subprocess.check_call((misc.whereis('umount'), directory))
        else:
            return
        if os.path.isdir(directory):
            os.rmdir(directory)
        self.post_actions(self.UNMOUNT_POST)

    def do_cpu_governor(self):
        # /sys/devices/cpu/power/control
        message.sub_info('Changing CPU governor')
        for cpu in self.get_cpus():
            sfile = os.path.join(cpu, 'cpufreq/scaling_governor')
            if os.path.isfile(sfile):
                if not misc.file_read(sfile).strip() == self.CPU_VALUE:
                    message.sub_debug('CPU governor changed', self.CPU_VALUE)
                    misc.file_write(sfile, self.CPU_VALUE)
                else:
                    message.sub_debug('CPU governor preserved', self.CPU_VALUE)

    def do_backlight(self):
        message.sub_info('Changing backlight')
        for backlight in self.get_backlights():
            sfile = os.path.join(backlight, 'brightness')
            if os.path.isfile(sfile):
                if not misc.file_read(sfile).strip() == self.BACKLIGHT_VALUE:
                    message.sub_debug('Brightness changed', self.BACKLIGHT_VALUE)
                    misc.file_write(sfile, self.CPU_VALUE)
                else:
                    message.sub_debug('Brightness preserved', self.BACKLIGHT_VALUE)

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
