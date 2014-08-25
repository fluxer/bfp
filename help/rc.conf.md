## NAME

rc.conf - Initscripts main configuration file

## DESCRIPTION

The *rc.conf* file is the system configuration file for **initscripts**.
The format is **Bash**. It contains several commonly-edited settings such
as timezone; keymap; kernel modules; daemons to load at start-up; etc. It is
split up in a few sections to categorize configuration settings: system time,
virtual consoles, hardware and misc.

Note: if the value of variable is empty (null), the feature it configures is left untouched.

## CONFIGURATION FORMAT

### TIME_ZONE=<string>

Specifies the timezone. The setting takes effect on boot by ensuring that F</etc/localtime> is a symlink
to the correct zoneinfo file. Possible time zones are the relative path to a zoneinfo file starting
from the directory */share/zoneinfo*. For example, a German time zones would be *Europe/Berlin*,
which refers to the file */share/zoneinfo/Europe/Berlin*.

Default: *empty*

### HARDWARE_CLOCK=<utc|localtime|other>

How to interpret/update the hardware clock. (used by **hwclock** daemon)

#### utc

most robust, allows operating systems to abstract local time and ease DST.

#### localtime

apply timezone (and DST) in hardware clock, discouraged. Choose this if you dualboot with
an OS which cannot handle UTC BIOS times correctly, like Windows. Note that recent Windows
versions can use UTC, which is preferable.

#### other

any other value will result in the hardware clock being left untouched (useful for virtualization)

Default: *empty*

### CONSOLE_FONT=<string>

Defines the console font to load with the B<setfont> program on boot.
Possible fonts are found in */lib/kbd/consolefonts* (only needed for non-US).

Default: *empty*

### CONSOLE_MAP=<string>

Defines the console map to load with the **setfont** program on boot. Possible maps are found in
*/lib/kbd/consoletrans*. Set this to a map suitable for the appropriate locale (8859-1 for Latin1,
for example) if you're using an UTF-8 locale and use programs that generate 8-bit output.

Default: *empty*

### KEYMAP=<string>

Defines the keymap to load with the **loadkeys** program on boot. Possible keymaps are
found in */lib/kbd/keymaps*.

Default: *empty*

Note: This settings are only valid for your TTYs, not any graphical B<Window Managers> or B<X11>/B<Xorg>. If you're
using B<X11> for everyday work, don't bother, as it only affects the output of Linux Console applications.

### MODULES=(<array>)

Modules to load at boot-up. Blacklisted modules are not loaded.

Default: *empty*

### USE_SWAP=<yes|no>

Enable swap partitions activation

Default: *no*

### USE_COLOR=<yes|no>

Use ANSI color sequences in start-up messages

Default: *yes*

### USE_PARALLEL=<yes|no>

Use parallelization of actions where possible

Default: *yes*

### HOSTNAME=<string>

Hostname of machine.

Default: *tiny*

### DAEMONS=(<array>)

Daemons to be started at start-up.

If you are sure nothing else touches your hardware clock (such as ntpd or
by dual-booting), you might want to enable 'hwclock'. Note that this will only
make a difference if the B<hwclock> program has been calibrated correctly.

If you use a network filesystem, you should enable **netfs**.

Default: *sysklogd dcron dhcpcd*

## FILES

*/etc/rc.conf*
    System configuration file for Initscripts.

## RESOURCES

Arch Linux initscripts: http://projects.archlinux.org/initscripts.git

Initscripts fork: https://bitbucket.org/smil3y/initscripts

## SEE ALSO

**hwclock**(8), **loadkeys**(1), **setfont**(8), **modprobe.d**(5), **hostname**(1), [initscripts](initscripts.html), [rc.d](rc.d.html)

## AUTHOR

Written by Dieter Plaetinck, Tom Gundersen and others. Forked by Ivailo Monev.
