## NAME

tmpfiles - Creates, deletes and cleans up volatile and temporary files and directories

## SYNOPSIS

    tmpfiles [OPTIONS...]>

## DESCRIPTION

**tmpfiles** creates, deletes and cleans up volatile and temporary files and directories,
based on the configuration file format and location specified in *tmpfiles.d*.

If invoked with no arguments, it applies all directives from all configuration files.
If one or more filenames are passed on the command line, only the directives in these
files are applied. If only the basename of a configuration file is specified, all
configuration directories as specified in *tmpfiles.d* are searched for a matching file.

## OPTIONS

The following options are understood:

### --create

If this option is passed all files and directories marked with *f*, *F*, *d*, *D* in the
configuration files are created. Files and directories marked with *z*, *Z* have their
ownership, access mode and security labels set.

### --clean

If this option is passed all files and directories with an age parameter configured will
be cleaned up.

### --remove

If this option is passed all files and directories marked with I<r>, I<R> in the configuration
files are removed.

### --prefix=<PATH>

Only apply rules that apply to paths with the specified prefix.

### --help

Prints a short help text and exits.

It is possible to combine *--create*, *--clean*, and *--remove* in one invocation. For example,
during boot the following command line is executed to ensure that all temporary and
volatile directories are removed and created according to the configuration file:

    tmpfiles --remove --create

## EXIT STATUS

On success 0 is returned, a non-zero failure code otherwise.

## SEE ALSO

[tmpfiles.d](tmpfiles.d.html)