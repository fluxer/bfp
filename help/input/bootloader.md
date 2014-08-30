## Things you should know before getting started

[GRUB](http://www.gnu.org/software/grub/) is the default bootloader shipped
with Tiny GNU/Linux and by default it doesn't support
[EFI/UEFI](http://en.wikipedia.org/wiki/Unified_Extensible_Firmware_Interface).
If you must use a bootloader with such feature you may recompile it with
support for it or use [gummiboot](http://freedesktop.org/wiki/Software/gummiboot),
[elilo](https://sourceforge.net/projects/elilo/),
[efilinux](https://github.com/mfleming/efilinux) or other EFI/UEFI friendly
bootloader.

## Getting your hands dirty

### Editing GRUB configuration file
The GRUB configuration file is located in /boot/grub/grub.conf. You can edit it
via text-editor of choice as **root**:

    vim /boot/grub/grub.conf

Other GRUB related files are:

> /etc/default/grub
>
> /etc/grub.d/*

### Detecting other Operating Systems

os-prober is piece of software that will help GRUB to detect other Operating
Systems installed, such as Windows. It is part of the base, to make use of it
run the following:

    os-prober
    update-grub
