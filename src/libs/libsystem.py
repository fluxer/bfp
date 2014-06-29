#!/bin/python2

import subprocess, os

import libmisc
misc = libmisc.Misc()


class System(object):
    ''' System state management and information gathering '''
    def __init__(self):
        ''' Initializer '''
        self.MOUNT_PRE = None
        self.MOUNT_POST = None
        self.UNMOUNT_PRE = None
        self.UNMOUNT_POST = None
        self.REBOOT_PRE = None
        self.SHUTDOWN_PRE = None
        self.SUSPEND_PRE = None
        self.SUSPEND_DISK = 'suspend'
        self.SUSPEND_STATE = 'mem'
        self.SUSPEND_POST = None
        self.BATTERY_LID = 'shutdown'
        self.BATTERY_CPU = 'ondemand'
        self.BATTERY_BACKLIGHT = '15'
        self.BATTERY_LOW = 'suspend'
        self.POWER_LID = 'suspend'
        self.POWER_CPU = 'performance'
        self.POWER_BACKLIGHT = '15'

        # changed depending on power state
        self.LID_VALUE = self.POWER_LID
        self.CPU_VALUE = self.POWER_CPU
        self.BACKLIGHT_VALUE = self.POWER_BACKLIGHT

    def get_batteries(self):
        ''' Get battery devices '''
        batteries = []
        for sdir in os.listdir('/sys/class/power_supply'):
            if sdir.startswith('BAT') or sdir == 'battery':
                batteries.append(os.path.join('/sys/class/power_supply', sdir))
        return batteries

    def get_cpus(self):
        ''' Get CPU devices '''
        cpus = []
        for sdir in os.listdir('/sys/devices/system/cpu/'):
            if misc.string_search('cpu\d', sdir, exact=True, escape=False):
                cpus.append(os.path.join('/sys/devices/system/cpu', sdir))
        return cpus

    def get_backlights(self):
        ''' Get backlight devices '''
        backlights = []
        for sdir in os.listdir('/sys/class/backlight'):
            if sdir.startswith('acpi_'):
                backlights.append(os.path.join('/sys/class/backlight', sdir))
        return backlights

    def get_battery_capacity(self):
        ''' Get battery capacity '''
        # FIXME: support multiple batteries, wrappers will get complex tough
        capacity = 0
        for battery in self.get_batteries():
            fcapacity = os.path.join(battery, 'capacity')
            if os.path.isfile(fcapacity):
                capacity = int(misc.file_read(fcapacity).strip())
        return capacity

    def get_battery_status(self):
        ''' Get battery status '''
        # FIXME: support multiple batteries, wrappers will get complex tough
        status = 'Unknown'
        for battery in self.get_batteries():
            fstatus = os.path.join(battery, 'status')
            if os.path.isfile(fstatus):
                status = misc.file_read(fstatus).strip()
        return status

    def get_lid_status(self):
        ''' Get Lid status '''
        status = 'Unknown'
        flid = '/proc/acpi/button/lid/LID/state'
        if os.path.isfile(flid):
            status = misc.file_read(flid).split()[1]
        return status

    def get_power_supply(self):
        ''' Get power supply '''
        # FIXME: this will be bogus with multiple batteries
        if self.get_battery_status() == 'Discharging':
            return 'DC'
        return 'AC'

    def get_backlight_max(self):
        ''' Get maximum value of backlight '''
        # FIXME: support multiple screens, wrappers will get complex tough
        status = 'Unknown'
        for backlight in self.get_backlights():
            fstatus = os.path.join(backlight, 'max_brightness')
            if os.path.isfile(fstatus):
                status = misc.file_read(fstatus).strip()
        return status

    def get_cpu_governor(self):
        ''' Get CPU governor '''
        # FIXME: support multiple CPUs, wrappers will get complex tough
        status = 'Unknown'
        for cpu in self.get_cpus():
            sfile = os.path.join(cpu, 'cpufreq/scaling_governor')
            if os.path.isfile(sfile):
                status = misc.file_read(sfile).strip()
        return status

    def check_mounted(self, string):
        ''' Check if block device is mounted '''
        for line in misc.file_readlines('/proc/mounts'):
            sdevice, sdirectory, stype, soptions, sfsck, sfsck2 = line.split()
            if sdevice == string or sdirectory == string:
                return True
        return False

    def pre_actions(self, actions):
        ''' Execute actions before major action '''
        if not actions:
            return
        for action in actions:
            subprocess.check_call((action))

    def post_actions(self, actions):
        ''' Execute actions after major action '''
        if not actions:
            return
        for action in actions:
            subprocess.check_call((action))

    def do_reboot(self):
        ''' Reboot the system '''
        subprocess.check_call((misc.whereis('reboot')))

    def do_shutdown(self):
        ''' Shutdown the system '''
        subprocess.check_call((misc.whereis('poweroff')))

    def do_suspend(self):
        ''' Put system in sleep state '''
        if not misc.file_search(self.SUSPEND_DISK, '/sys/power/disk'):
            raise(Exception('Unsupported disk mode', self.SUSPEND_DISK))
        elif not misc.file_search(self.SUSPEND_STATE, '/sys/power/state'):
            raise(Exception('Unsupported state mode', self.SUSPEND_STATE))

        self.pre_actions(self.SUSPEND_PRE)
        misc.file_write('/sys/power/disk', self.SUSPEND_DISK)
        misc.file_write('/sys/power/state', self.SUSPEND_STATE)
        self.post_actions(self.SUSPEND_POST)

    def do_mount(self, device):
        ''' Mount a block device '''
        self.pre_actions(self.MOUNT_PRE)
        directory = '/media/' + os.path.basename(device)
        if not os.path.isdir(directory):
            os.makedirs(directory)
        if not self.check_mounted(device):
            subprocess.check_call((misc.whereis('mount'), device, directory))
            self.post_actions(self.MOUNT_POST)

    def do_unmount(self, device):
        ''' Unmount a block device '''
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
        ''' Change CPU governor '''
        # /sys/devices/cpu/power/control
        for cpu in self.get_cpus():
            sfile = os.path.join(cpu, 'cpufreq/scaling_governor')
            if os.path.isfile(sfile):
                if not misc.file_read(sfile).strip() == self.CPU_VALUE:
                    misc.file_write(sfile, self.CPU_VALUE)

    def do_backlight(self):
        ''' Change backlight '''
        for backlight in self.get_backlights():
            sfile = os.path.join(backlight, 'brightness')
            if os.path.isfile(sfile):
                if not misc.file_read(sfile).strip() == self.BACKLIGHT_VALUE:
                    misc.file_write(sfile, self.BACKLIGHT_VALUE)
