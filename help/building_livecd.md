## Things you should know before getting started

The build tool requires the following packages to be present in the host OS
environment:

- git
- spm>=2.1.1
- squashfs-tools>=4.2
- grub>=2.00
- xorriso

**Important:** The software will be build on the host system and then installed
to separate root directory, this means that the software may link to unwanted
libraries such as X11, acl or libxml2. You will have to either build on minimal
setup or remaster a LiveCD snapshot and build the software in chroot.

## Tools of the trade

The tool you are going to use is builder. Its sources are located at
https://bitbucket.org/smil3y/builder.it is a set of scripts to assist in
building LiveCDs using profiles. The base profile is used as shared, meaning
that files from it are used only if files in the profile you choosed at runtime
don't exists in the profile directory. This is to minimize the impact on the
files you need to worry about when creating your own profile.

## Getting your hands dirty

First you will need the sources of LSDB. To obtain a fresh copy issue the
following in [Terminal](http://en.wikipedia.org/wiki/Computer_terminal#Text_terminals):

    git clone --depth=1 https://bitbucket.org/smil3y/builder.git

Or, if you already have a copy of the sources, just update them:

    cd builder
    git pull origin master

### Official profile

The official profile named *base* should be used to as an example. It is ment
to create a base setup on top of which you can expand.

### Custom profile

To create a new profile you can create an empty directory in the profiles
directpry of the builder main tree:

    cd builder
    mkdir -v profiles/custom

Now, you can copy only the preferences.conf file from the base profile so that
the defaults provided in the base profile are used for the rest of the build:

    cp -v profiles/base/preferences.conf profiles/custom

The next step is editing the preferences.conf file to your liking, in this
example [Vim](http://en.wikipedia.org/wiki/Vim_(text_editor)) will be used as
it is shipped by default by almost every disitribution out there:

    vim profiles/custom/preferences.conf

Quick notes:

- Press "A" to switch to "INSERT" mode

- Press "Esc" to switch back to "VIEW" mode

- Type ":wq" and then "ENTER" to save and exit

### Building

After you are fine with the changes you've made build an ISO image:
    sudo ./build.sh custom -d -b

The final ISO image you can find in the main LSDB directory.

### Remastering

In case you want to make minor changes to a official LiveCD snapshot you can
remaster the snapshot instead of building one from scratch, this will save you
a lot of time. You will make use of the LiveCD build system for that so make
sure you have a local copy of it.

To remaster a snapshot all you have to do is extract the *root.sfs* file from
the ISO image and unsquash it as follows:

    bsdtar -xf BASE-x86_64-20131006.iso live/root.sfs
    sudo unsquashfs -d base_root_$(uname -m) live/root.sfs

Then, you can chroot into the extracted filesystem:

    sudo ./build.sh base -c

Once you are done with the customization rebuild the ISO image:
    sudo ./build.sh base -b
