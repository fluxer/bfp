#!/bin/python2

from PyQt4 import QtCore, QtGui
import sys, os, time, libdesktop, libsystem, libmessage

# prepare for lift-off
app = QtGui.QApplication(sys.argv)
Dialog = QtGui.QProgressDialog() # 'QManager'
config = libdesktop.Config()
general = libdesktop.General()
system = libsystem.System()
message = libmessage.Message()

def setLook():
    general.set_style(app)
setLook()

def setValues():
    if system.get_power_supply() == 'DC':
        system.LID_VALUE = config.LID_BATTERY
        system.CPU_VALUE = config.CPU_BATTERY
        system.BACKLIGHT_VALUE = config.BACKLIGHT_BATTERY
    else:
        system.LID_VALUE = config.LID_POWER
        system.CPU_VALUE = config.CPU_POWER
        system.BACKLIGHT_VALUE = config.BACKLIGHT_POWER
setValues()

# watch configs for changes
def reload_manager():
    global config
    reload(libdesktop)
    config = libdesktop.Config()
    setLook()
    setValues()

watcher1 = QtCore.QFileSystemWatcher()
watcher1.addPath(config.settings.fileName())
watcher1.fileChanged.connect(reload_manager)

class LidThread(QtCore.QThread):
    def run(self):
        ''' Monitor LID state '''
        message.sub_info('Monitoring LID state')
        if not os.path.exists('/proc/acpi/button/lid/LID/state'):
            message.sub_warning('No LID support')
            return
        while True:
            before = system.get_lid_status()
            time.sleep(2)
            after = system.get_lid_status()
            if not before == after:
                message.sub_debug('LID status changed', after)
                if after == 'closed' and system.LID_VALUE == 'suspend':
                    system.do_suspend()
                elif after == 'closed' and system.LID_VALUE == 'shutdown':
                    system.do_shutdown()
                elif after == 'closed':
                    message.sub_warning('Invalid value for LID action', system.LID_VALUE)
                    system.do_suspend()

class PowerThread(QtCore.QThread):
    def run(self):
        ''' Monitor power state '''
        message.sub_info('Monitoring power state')
        while True:
            before = system.get_power_supply()
            time.sleep(2)
            after = system.get_power_supply()
            if not before == after:
                message.sub_debug('Power state changed', after)
                if after == 'DC':
                    system.LID_VALUE = config.LID_BATTERY
                    system.CPU_VALUE = config.CPU_BATTERY
                    system.BACKLIGHT_VALUE = config.BACKLIGHT_BATTERY
                    capacity = system.get_battery_capacity()
                    if capacity < 15:
                        message.sub_warning('Low battery', capacity)
                        if config.LOW_BATTERY == 'suspend':
                            system.do_suspend()
                        elif config.LOW_BATTERY == 'shutdown':
                            system.do_shutdown()
                        else:
                            # FIXME: notify every 2 minites
                            message.sub_warning('Low battery', capacity)
                else:
                    system.LID_VALUE = config.LID_POWER
                    system.CPU_VALUE = config.CPU_POWER
                    system.BACKLIGHT_VALUE = config.BACKLIGHT_POWER
                system.do_cpu_governor()
                system.do_backlight()

class BlockThread(QtCore.QThread):
    def run(self):
        ''' Monitor block devices state '''
        message.sub_info('Monitoring block devices state')
        while True:
            before = os.listdir('/sys/class/block')
            time.sleep(2)
            after = os.listdir('/sys/class/block')
            for f in after:
                if '.tmp' in f:
                    continue
                if not f in before:
                    system.do_mount('/dev/' + f)
                    message.sub_info('Device mounted', f)
            for f in before:
                if '.tmp' in f:
                    continue
                if not f in after:
                    system.do_unmount('/dev/' + f)
                    message.sub_info('Device unmounted', f)
            time.sleep(2)

t1 = LidThread()
t1.start()
t2 = PowerThread()
t2.start()
t3 = BlockThread()
t3.start()

sys.exit(app.exec_())
