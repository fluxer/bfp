## Xorg video

If you happen to have issues with Xorg try appending the following to you boot
arguments:

> noapic noapm nodma nomce nolapic nomodeset nosmp vga=normal

To make this permanent update your [bootloader](bootloader.html) configuration.

## Xorg input

If the X server starts but input devices do not respond after that there may be
two causes:

- udev is not running

- the input drivers (xorg-input-drivers) are not build against the current X
server (xorg-server)

For the first issue you verify that udev daemon is actually running:

    pgrep udevd

If nothing is printed then the udev deamon is not running. You can start it by
hand before running Xorg and see if that helps:

    udevd --daemon
    udevadm trigger --action=add --type=subsystems
    udevadm trigger --action=add --type=devices

For the second issue all you have to do is this:

    sudo spm source -aD xorg-input-drivers