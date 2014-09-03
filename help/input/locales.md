## Things you should know before getting started

The following [environment variables](https://en.wikipedia.org/wiki/Environment_variable)
can be used to setup the locales:

- LANG
- LC_CTYPE
- LC_NUMERIC
- LC_TIME
- LC_COLLATE
- LC_MONETARY
- LC_MESSAGES
- LC_ALL
- LC_PAPER
- LC_NAME
- LC_ADDRESS
- LC_TELEPHONE
- LC_MEASUREMENT
- LC_IDENTIFICATION

LC_ALL overrides all other variables prefix with LC_. Usually what you want to
export is LANG and LC_ALL unless you want to mix different locales.

## Getting your hands dirty

### Generate locales

First you must edit as **root** the */etc/locale.conf* file and uncomment the
desired locales. After this you must generate them, to do so execute the
following as **root**:

    locale-gen

By default the following locales are enabled but not generated:

- cs_CZ.UTF-8 UTF-8
- de_DE.UTF-8 UTF-8
- de_DE ISO-8859-1
- de_DE@euro ISO-8859-15
- en_HK ISO-8859-1
- en_PH ISO-8859-1
- en_US.UTF-8 UTF-8
- en_US ISO-8859-1
- es_MX ISO-8859-1
- fa_IR UTF-8
- fr_FR.UTF-8 UTF-8
- fr_FR ISO-8859-1
- fr_FR@euro ISO-8859-15
- it_IT ISO-8859-1
- tr_TR.UTF-8 UTF-8
- zh_CN.GB18030 GB18030

### Create script

Depending on the [Shell](http://en.wikipedia.org/wiki/Unix_shell) you are using
you may want to adjust the command bellow. If you are using
[Bourne Shell](http://en.wikipedia.org/wiki/Bourne_shell) compatible Shell you
most likely are not going to have to.

Login as **root** and execute the following:

    cat > /etc/profile.d/locales.sh << EOF
    #!/bin/sh
    
    export LANG=desired_locales
    export LC_ALL=desired_locales
    EOF

The changes will take effect on your next login.
