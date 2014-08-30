## NAME

rc.d - Initscripts daemons tool

## SYNOPSIS

    rc.d action [option] [daemon [daemon] ...]

## DESCRITPTION

The **rc.d** program controls rc (daemon) scripts on the system.

## ACTIONS

The actions supported by a rc scripts may be different from script to
script, but commonly supported actions include:

### start

Starts the daemon if it is not already running

### stop

Stops a running daemon

### restart

Restarts a running daemon

## OPTIONS

    -a, --auto            Execute action on daemon defined in */etc/rc.conf*
    -n, --noauto          Execute action on daemons not defined in */etc/rc.conf*
    -A, --all             Execute action on all daemons
    -s, --started         Execute action on all running daemons
    -S, --stopped         Execute action on all stopped daemons

## EXAMPLES

Starts the **sshd** and **gpm** daemons:

    rc.d start sshd gpm

Starts all daemons which are runned at startup:

    rc.d start --auto

Stops the **crond** daemon:

    rc.d stop crond

Stops all daemons which are not runned at startup:

    rc.d stop --noauto

Stops all daemons which are runned at startup, but only those that are not running:

    rc.d stop --auto --stopped

Restarts the **crond** daemon:

    rc.d restart crond

Restarts all daemons which are not runned at startup and **sshd**:

    rc.d restart --noauto sshd

## FILES

### /etc/rc.d

Directory containing available daemons on the system

### /run/daemons

Directory containing state of running daemons

## RESOURCES

Arch Linux initscripts: <http://projects.archlinux.org/initscripts.git>

Initscripts fork: <https://bitbucket.org/smil3y/initscripts>

## AUTHOR

Written by Sebastien Luttringer and Dave Reisner. Forked by Ivailo Monev.

## COPYRIGHT

Copyright (c) 2012-2014 Ivailo Monev licensed through the GPLv2 License

## SEE ALSO

[initscripts](initscripts.html), [rc.conf](rc.conf.html)
