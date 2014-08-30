## Things you should know before getting started

By default Tiny GNU/Linux setups the following groups:

    root:x:0:
    bin:x:1:
    sys:x:2:
    kmem:x:3:
    tape:x:4:
    tty:x:5:
    wheel:x:6:root
    daemon:x:7:
    floppy:x:8:
    disk:x:9:
    lp:x:10:
    dialout:x:11:
    audio:x:12:
    video:x:13:
    utmp:x:14:
    usb:x:15:
    cdrom:x:16:
    mail:x:17:
    uucp:x:18:
    network:x:19:
    power:x:20:
    nogroup:x:99:
    users:x:100:
    messagebus:x:101:messagebus

Groups for use with daemons are added from the install scripts of the
respective port.

## Tools of the trade

For adding, deleting and modifying users useradd, userdel and usermod commands
will be used. For adding, deleting and modifying groups groupadd, groupdel and
groupmod commands will be used.

## Getting your hands dirty

### Users

#### Adding users

Adding a user can be done with the following command:

    useradd -m -g users -G tty,tape,wheel,disk,lp,audio,video,usb,cdrom,network,power,sudo user_name

- **-m** creates the user home directory as /home/<user_name>

- **-g** defines the group name or number of the user's initial login group.
The group name must exist.

- **-G** introduces a list of supplementary groups which the user is also a
member of. Each group is separated from the next by a comma with no intervening
spaces. The default is for the user to belong only to the initial group.

**Tip:** The behavior of useradd will depend on the variables contained in
/etc/login.defs.

#### Deleting users

Delete a user can be done with the following command:

    userdel -r user_name

- **-r** delete user's home directory and mail spool.

#### Editing users

To add a user to additional groups:
 usermod -a -G additional_groups user_name

- **-a** append the user to the supplemental GROUPS mentioned by the -G option
without removing him/her from other groups.

- **-G** introduces a list of supplementary groups which the user will also a
member of. Each group is separated from the next by a comma with no intervening
spaces.

#### Groups

TODO