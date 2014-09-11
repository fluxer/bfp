## NAME

initscripts - System initialization scripts

## DESCRIPTION

Set of [Bash](http://en.wikipedia.org/wiki/Bash_(Unix_shell)) scripts to bring
the system up in usable state with the help of [Busybox's](http://www.busybox.net/)
**init**

## OVERVIEW

Every [Operating System](http://en.wikipedia.org/wiki/Operating_system)
requires some sort of process control initialization program which brings the
system up to state in which the user can operate, **init** is one of them and
is [Linux](http://en.wikipedia.org/wiki/Linux) specifiec. But it can not handle
the process on itself alone thus the **initscripts** assist it to do its job.

**init** executes different programs in different stages
([runlevels](http://en.wikipedia.org/wiki/Runlevel)) which breaks down the
whole process so it fits different use cases (such as administration and
repairs), there are four (3) scripts in that matter:

### rc.sysinit

system initialization

### rc.wait

wait script

### rc.shutdown

system shutdown (halt or reboot)

*/etc/rc.sysinit* is first script that is executed. It makes sure that all
preperations are done on the system environment.
[Pseudo filesystems](http://en.wikipedia.org/wiki/List_of_file_systems#Pseudo-_and_virtual_file_systems),
[devices nodes](http://en.wikipedia.org/wiki/Device_file), [environmental
variables](http://en.wikipedia.org/wiki/Environment_variable) and others are
initialized to sane defaults.

*/etc/rc.wait* continues where *rc.sysinit* left off and can be used to make
additional system state changes.

*/etc/rc.shutdown* is responsible to halt or reboot the system without breakage
such as filesystem inconsistency. It is almost the same as *rc.sysinit* but in
reverse order.

But there is a reason why those are **Bash** scripts and not **C**/**C++**
binaries or something else, that is portability, share-code feature, and most
of all easily hackable by anyone who wants to get involved with it and
contribute. This is done by providing a common file */etc/rc.d/functions* which
holds functions and sane environmental variables. Among the other things it is
also used by the [deamons](http://en.wikipedia.org/wiki/Daemon_(computing))
which should run on the system to avoid dublicating code functionality.

## CONFIGURATION

Configring the **initscripts** behavior is done via a single file -
*/etc/rc.conf*. More about that in its help page [rc.conf](rc.conf.html). If
you want to go deeper into this you will have to take a look at **boot**(7),
**init**(8) and/or [inittab](inittab.html).

## FUNCTIONS

The */etc/rc.d/functions* file is used by all initialization scripts (see
overview) to be source of all code that is shared among them, provides extra
functions for the daemons and other third-party scripts and tools. The
functions which are defind in */etc/rc.d/functions* are grouped in the format
*group_program_action*, all of those do not contain special characters to avoid
confusion and to be easy to pick up.

### group

group of functions with simmilar functionality, three (3) characters string

### program

program to be executed, one (1) word string

### action

action to be taken by the program, one (1) word string

## HOOKS

Functions can be used to include custom code in various places in the
**initscripts**. Those functions reside in */etc/rc.d/functions.d*. The format
is **Bash** and should follow the example:

    function_name() { ... }

    add_hook hook function_name

where *hook* is the stage in which this function should be inserted and
executed. The first word before the underscore represents the rc script in
which the function is inserted, the second word represends the action that will
follow after the function. This is useful in case you want to override, add or
remove certain feature of the **initscripts**.

It is allowed to register several hook functions for the same *hook* as in
regular **Bash** script. Is is also allowed to register the same hook function
for several *hooks*.

The following hooks are supported

### sysinit_start

at the beginning of *rc.sysinit*, before the Kernel paramters are configured

### sysinit_udevstart

before UDev daemon is launched

### sysinit_modules

before the user-specified modules are loaded

### sysinit_udevsettle

before uevents are settled

### sysinit_hwclock

before system time is adjusted

### sysinit_swap

before Swap partitions are activated

### sysinit_remount

before Root filesystem is remounted read-write

### sysinit_leftovers

before leftover-files are removed

### sysinit_seed

before random-seed is restored

### sysinit_dmesg

before dmesg log is saved

### sysinit_fsck

before all local checks are performed

### sysinit_mount

before all local filesystems are mounted

### sysinit_timezone

before Time Zone is setuped

### sysinit_consoles

before virtual Consoles are setuped

### sysinit_consolefont

before Console fonts are setuped

### sysinit_consolemap

before Console map is setuped

### sysinit_keyboardmap

before Keyboard map is setuped

### sysinit_hostname

before hostname is setuped

### sysinit_loopback

before loopback interface is broght up

### sysinit_daemons

before automatic daemons are started

### sysinit_end

at the end of *rc.sysinit*

### shutdown_start

at the beginning of *rc.shutdown*, before daemons are stopped

### shutdown_udevstop

before UDev daemon is stopped

### shutdown_seed

before random-seed is saved

### shutdown_timezone

before Time Zone is setuped

### shutdown_killall

before all processes are killed

### shutdown_swap

before swap-backend filesystems are unmounted

### shutdown_umount

before all filesystems are unmounted

### shutdown_poweroff

at the end of *rc.shutdown*

## DAEMONS

Daemons are **Bash** scripts which run processes in the background to do their
thing, waiting for input, specifiec event to accure or something else. Those
daemons can be started, stopped and/or restarted when needed using the
[rc.d](rc.d.html) tool which is also provided by **initscripts** and are
located in separate directory */etc/rc.d*. More information about it in
[rc.d](rc.d.html) help page.

## EXAMPLES

The following is example daemon script, use it as a reference when writing
daemon scripts:

    #!/bin/bash
    #
    # /etc/rc.d/privoxy: start/restart/stop privoxy daemon
    #

    . /etc/rc.conf
    . /etc/rc.d/functions

    _bin=$(type -pf privoxy)
    _args="/etc/privoxy/config"
    _pid=$(pidof -o %PPID privoxy)

    case "$1" in
        start)
            if [ -z "$_pid" ]; then
                exec_cmd "Starting Privacy Enhancing Proxy" "$_bin" $_args
                [ "$?" = "0" ] && echo "$(pidof -o %PPID privoxy)" > /run/privoxy.pid
            fi
            ;;

        stop)
            if [ -n "$_pid" ];then
                exec_cmd "Stopping Privacy Enhancing Proxy" kill "$_pid"
                [ "$?" = "0" ] && rm -f /run/privoxy.pid
            fi
            ;;

        restart)
            $0 stop
            sleep 3
            $0 start
            ;;

        *)
            echo "usage: $0 {start|stop|restart}"
            exit 1
            ;;
    esac

    # End of file

## FILES

### /etc/rc.sysinit

System initialization script

### /etc/rc.wait

Wait script

### /etc/rc.shutdown

System shutdown (halt or reboot) script

### /etc/rc.d/functions

Common functions and share-code script

### /etc/rc.d/functions.d

Directory containing available functions on the system

### /etc/rc.d

Directory containing available daemons on the system

## RESOURCES

Arch Linux initscripts: <http://projects.archlinux.org/initscripts.git>

Initscripts fork: <https://bitbucket.org/smil3y/initscripts>

## AUTHOR

Written by Sebastien Luttringer and Dave Reisner. Forked by Ivailo Monev.

## COPYRIGHT

Copyright (c) 2012-2014 Ivailo Monev licensed through custom License


## SEE ALSO

**boot**(7), **init**(8), [inittab](inittab.html), **mount**(8), **sysctl**(8),
**udev**(7), **modprobe**(8), **hwclock**(8), **fsck**(8), **urandom**(8),
**swapon**(8), **loadkeys**(1), **setfont**(8), **hostname**(1), **ip**(8),
**killall5**(8), [rc.conf](rc.conf.html), [rc.d](rc.d.html),
[tmpfiles](tmpfiles.html), [tmpfiles.d](tmpfiles.d.html)
