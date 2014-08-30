## Things you should know before getting started
Since Tiny GNU/Linux is targeted at advanced users there is some maintenance
involved in using it. Bellow are noted some things you should be aware of and
the how you can handle them.

## Configuration files
(Source Package Manager](spm.html) will backup all files with .conf extension
as well as those explicitly specified in the backup array of the SRCBUILD with
a .backup extension on merge if the content of the file has changed, usually
when you (the user) has done so.

For an example, if you upgrade initscripts and you've changed the content of
/etc/rc.conf the file will be replaced but backed up before that as
/etc/rc.conf.backup. You can find all backup files using the `find` command
like so:

    sudo find / -xdev -type f -name '*.backup'

or if you have separate /usr, /var and /boot:

    sudo find / /usr /var /boot -xdev -type f -name '*.backup'

Then, you can use `diff` to compare the files content:

    sudo diff -u /etc/rc.conf.backup /etc/rc.conf

In this case the lines prefixed with plus sign (+) are not present in
/etc/rc.conf.backup but are in /etc/rc.conf and the opposite for the lines
prefixed with minus sigh (-). You can merge the files manually with your 
ext-editor of choice or just replace the new file with the backup file but
beware for new variables and options in the new configuration file.

**Tip:** Source Package Manager Tools can help you with this task but they are
not yet released and under development. To install them you will have to pull
the latest spm from [Git](https://bitbucket.org/smil3y/bfp/).

## Kernel modules
Third-party kernel modules must be rebuild when you recompile the kernel
(linux port). For an example, with nvidia all you have to do is rebuild nvidia:

    sudo spm source -aD nvidia

**Tip:**: Using the "-u" or "--update" flag will not trigger the rebuild if
nvidia is not newer version so avoid using it in this case

Alternatively, you can use dkms, assuming that the sources required to build
the module are in sub-directory of /usr/src, like so (in this example,
virtualbox-bin):

    sudo dkms remove vboxhost/$(spm local -vp virtualbox-bin) --all
    sudo dkms install vboxhost/$(spm local -vp virtualbox-bin)

## Recovering disk space
You may notice that after building KDE, Chromium or other space (and time)
consuming ports your root (/) or var (/var) partitions starts filling up,
that's because building is done in /var/tmp/spm (by default). Source are kept
in /var/cache/spm/sources and tarballs of the files to be installed in
/var/cache/spm/tarballs. If you root or var partitions are small you may
cleanup those on regular basis or create a cron job for that (FIXME).

In addition, altought documentation is usually not installed there still may be
some files in /share/docs that you may get rid of.

# X.Org

Upon X.Org stack upgrade we highly recommend that you rebuild it in the proper
order via the alias:

    sudo spm source -aDR xorg

## Dealing with obsolete and removed ports

Sometimes, when you sync and check the repositories for updates
(via `spm repo -csu`) you will notice warnings like this:

    => Target not in any repository: qastools
    => Target not in any repository: qterminal-git
    => Target not in any repository: qtermwidget-git

This can mean one of the following:
- the ports have been removed
- the ports have been renamed
- the ports are installed from outside the available repositories

How to know what exactly happened? You can read the RSS feed on our home page
or visit [this](https://bitbucket.org/smil3y/mini/commits/all) page where our
repositories are stored and search the commit messages.

In the first case you can create a dummy file SRCBUILD in a directory with name
matching the removed port to be able to remove the port from your system. An
example with qastools:

    mkdir qastools
    touch qastools/SRCBUILD
    sudo spm source -rR qastools
    rm -rf qastools

In the seconds case, there is no need to remove the port from your system and
all you have to do is rename the local directory of the port to the new name to
avoid conflicts in case you attempt to build the new target. A rename can
happen for an example when the port has been stabelized and no longer pulled
from the latest source but a stable release is used instead. An example with
qterminal-git:

    sudo mv /var/local/spm/qterminal-git /var/local/spm/qterminal

In the third case, you can safely ignore the warning as you've installed a port
of your own and it's up to you when and how you should update it.