#!/usr/bin/python

import subprocess, os

import libmisc
import libmessage
import libservice
message = libmessage.Message()
misc = libmisc.Misc()
service = libservice.Service()


class Power(object):
    ''' Power manager '''
    def __init__(self):
        ''' Initializer '''
        self.initialized = False
        self.ipc = '/run/power.fifo'
        # set custom log file
        message.LOG_FILE = '/var/log/power.log'

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

    def do_reboot(self):
        message.sub_info('Rebooting system...')
        self.pre_actions(self.REBOOT_PRE)
        service.system_reboot()

    def do_shutdown(self):
        message.sub_info('Shutting system down...')
        self.pre_actions(self.SHUTDOWN_PRE)
        service.system_shutdown()

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
