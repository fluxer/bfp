#!/usr/bin/python2

import os
import sys
import ConfigParser

import libmessage
message = libmessage.Message()


MAIN_CONF = '/etc/desktop.conf'

if not os.path.isfile(MAIN_CONF):
    message.warning('Configuration file does not exist', MAIN_CONF)

    GENERAL_STYLE_FILE = None
    GENERAL_ICONTHEME = None
    MENU_FILE = '/etc/xdg/menus/kde-applications.menu'
    WALLPAPER_FILE = "/home/smil3y/Wallpapers/wallpaper-250964.jpg"
    WALLPAPER_STYLE = "stretch"
else:
    conf = ConfigParser.SafeConfigParser()
    conf.read(MAIN_CONF)

    GENERAL_STYLE_FILE = conf.get('general', 'STYLESHEET')
    GENERAL_ICONTHEME = conf.get('general', 'ICONTHEME')
    MENU_FILE = conf.get('general', 'MENU')
    WALLPAPER_FILE = conf.get('wallpaper', 'FILE')
    WALLPAPER_STYLE = conf.get('wallpaper', 'STYLE')
