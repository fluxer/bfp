#!/bin/python2

import os, subprocess, libmisc
misc = libmisc.Misc()

'''
Ever wanted to bust your partitions? Use Block().

Your system is in a need of a reboot? Use Power().

Expect failures if ran as regular user.
'''

class Block(object):
    ''' Block device helper '''
    def __init__(self):
        ''' Initializer '''
        pass

    def mounted(self, variant):
        ''' Check if device/directory is mounted '''
        if os.path.ismount(variant):
            return variant
        if misc.file_search(variant, '/proc/mounts'):
            return variant
        if variant.startswith('/dev'):
            # /dev -> UUID
            uuid = self.info(variant, 'UUID')
            if misc.file_search(uuid, '/proc/mounts'):
                return uuid
        # UUID -> /dev
        uuid = '/dev/disk/by-uuid/%s' % variant
        if os.path.exists(uuid):
            dev = self.info(uuid, 'DEVNAME')
            if misc.file_search(dev, '/proc/mounts'):
                return dev

    def unmount(self, variant):
        ''' unmount a block device '''
        device = self.mounted(variant)
        if device:
            misc.system_command((misc.whereis('umount'), '-fl', device))

    def mount(self, variant, mpoint):
        ''' Mount a block device '''
        self.unmount(variant)
        self.unmount(mpoint)
        misc.dir_create(mpoint)
        try:
            # modprobe the filesystem type module, and do not fail at that
            # as the module name may not be correct (known with some
            # filesystems) or even a built-in
            fstype = self.info(variant, 'TYPE')
            # TODO: ignore some filesystem types
            if fstype:
                misc.system_command((misc.whereis('modprobe'), '-b', fstype))
        except subprocess.CalledProcessError:
            pass
        misc.system_command((misc.whereis('mount'), variant, mpoint))

    def fsck(self, device, fstype):
        ''' Check the filesystem on a block device '''
        if fstype == 'swap':
            # nothing to do
            return
        elif fstype == 'ntfs' or fstype == 'vfat':
            command = (misc.whereis('fsck.vfat'), '-p', device)
        elif fstype == 'jfs':
            command = (misc.whereis('fsck.jfs'), '-f', '-p', device)
        elif fstype == 'btrfs':
            command = (misc.whereis('btrfsck'), '--repair', device)
        else:
            command = (misc.whereis('fsck.%s' % fstype), '-f', '-p', device)
        misc.system_command(command)

    def mkfs(self, device, fstype):
        ''' Create a filesystem on block device '''
        if fstype == 'swap':
            command = (misc.whereis('mkswap'), '-L', 'Swap', device)
        elif fstype == 'ntfs' or fstype == 'vfat':
            command = (misc.whereis('mkfs.%s' % fstype), device)
        elif fstype == 'jfs':
            command = (misc.whereis('mkfs.jfs'), '-q', device)
        elif fstype == 'btrfs':
            command = (misc.whereis('mkfs.btrfs'), '-f', device)
        else:
            command = (misc.whereis('mkfs.%s' % fstype), '-F', device)
        misc.system_command(command)

    def info(self, device, tag):
        ''' Get information about a block device '''
        for line in misc.system_communicate((misc.whereis('udevadm'), 'info', \
                '--name', device, '--query=property')).splitlines():
                line = misc.string_encode(line).strip()
                if line.startswith(('ID_FS_%s' % tag, tag)):
                    return line.split('=')[1]

class Power(object):
    ''' System power state management and information gathering helper '''
    def __init__(self):
        ''' Initializer '''
        self.REBOOT_PRE = None
        self.SHUTDOWN_PRE = None
        self.SUSPEND_PRE = None
        self.SUSPEND_DISK = 'suspend'
        self.SUSPEND_STATE = 'mem'
        self.SUSPEND_POST = None
        self.LID_VALUE = 'suspend'
        self.CPU_VALUE = 'performance'
        self.BACKLIGHT_VALUE = '15'

    def get_batteries(self):
        ''' Get battery devices '''
        batteries = []
        for sdir in os.listdir('/sys/class/power_supply'):
            if sdir.startswith('BAT') or sdir == 'battery':
                batteries.append('/sys/class/power_supply/%s' % sdir)
        return batteries

    def get_cpus(self):
        ''' Get CPU devices '''
        cpus = []
        for sdir in os.listdir('/sys/devices/system/cpu/'):
            if misc.string_search('cpu\d', sdir, exact=True, escape=False):
                cpus.append('/sys/devices/system/cpu/%s' % sdir)
        return cpus

    def get_backlights(self):
        ''' Get backlight devices '''
        backlights = []
        for sdir in os.listdir('/sys/class/backlight'):
            if sdir.startswith('acpi_'):
                backlights.append('/sys/class/backlight/%s' % sdir)
        return backlights

    def get_battery_capacity(self):
        ''' Get battery capacity '''
        # FIXME: support multiple batteries, wrappers will get complex tough
        capacity = 0
        for battery in self.get_batteries():
            fcapacity = '%s/capacity' % battery
            if os.path.isfile(fcapacity):
                capacity = int(misc.file_read(fcapacity).strip())
        return capacity

    def get_battery_status(self):
        ''' Get battery status '''
        # FIXME: support multiple batteries, wrappers will get complex tough
        status = 'Unknown'
        for battery in self.get_batteries():
            fstatus = '%s/status' % battery
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
            fstatus = '%s/max_brightness' % backlight
            if os.path.isfile(fstatus):
                status = misc.file_read(fstatus).strip()
        return status

    def get_cpu_governor(self):
        ''' Get current CPU governors '''
        status = []
        for cpu in self.get_cpus():
            sfile = '%s/cpufreq/scaling_governor' % cpu
            if os.path.isfile(sfile):
                status.append(misc.file_read(sfile).strip())
            else:
                raise(Exception('CPU does not support governing', cpu))
        return status

    def get_cpu_governors(self):
        ''' Get supported CPU governors '''
        governors = []
        for cpu in self.get_cpus():
            sfile = '%s/cpufreq/scaling_available_governors' % cpu
            if os.path.isfile(sfile):
                governors = misc.file_read(sfile).strip().split()
        return governors

    def get_power_disks(self):
        ''' Get supported suspend disk modes '''
        disks = []
        sfile = '/sys/power/disk'
        if os.path.isfile(sfile):
            disks = misc.file_read(sfile).strip()
            disks = disks.replace('[', '').replace(']', '')
            disks = disks.split()
        return disks

    def get_power_states(self):
        ''' Get supported suspend disk modes '''
        states = []
        sfile = '/sys/power/state'
        if os.path.isfile(sfile):
            states = misc.file_read(sfile).split()
        return states

    def pre_actions(self, actions):
        ''' Execute actions before major action '''
        if not actions:
            return
        for action in actions:
            misc.system_command((action))

    def post_actions(self, actions):
        ''' Execute actions after major action '''
        if not actions:
            return
        for action in actions:
            misc.system_command((action))

    def do_reboot(self):
        ''' Reboot the system '''
        self.pre_actions(self.REBOOT_PRE)
        misc.system_command((misc.whereis('reboot')))

    def do_shutdown(self):
        ''' Shutdown the system, unlike your usual shutdown helper this one
            works on system with SysVinit, Busybox and (hopefully) systemd '''
        self.pre_actions(self.SHUTDOWN_PRE)
        misc.system_command((misc.whereis('poweroff')))

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

    def do_cpu_governor(self, docpu='0'):
        ''' Change CPU governor '''
        # /sys/devices/cpu/power/control
        all_cpus = self.get_cpus()
        counter = 0
        for cpu in all_cpus:
            sfile = '%s/cpufreq/scaling_governor' % cpu
            if os.path.isfile(sfile):
                if docpu and not counter == int(docpu):
                    continue
                if not misc.file_read(sfile).strip() == self.CPU_VALUE:
                    misc.file_write(sfile, self.CPU_VALUE)
            counter += 1

    def do_backlight(self):
        ''' Change backlight '''
        for backlight in self.get_backlights():
            sfile = '%s/brightness' % backlight
            if os.path.isfile(sfile):
                if not misc.file_read(sfile).strip() == self.BACKLIGHT_VALUE:
                    misc.file_write(sfile, self.BACKLIGHT_VALUE)
