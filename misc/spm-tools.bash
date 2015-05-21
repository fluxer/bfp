# SPMT Bash completion by Ivailo Monev <xakepa10@gmail.com>

_spm_tools()
{
    local action cur prev
    local main_options merge_options clean_options edit_options sane_options
    local lint_options check_options dist_options which_options pack_options
    local pkg_options serve_options disowned_options upload_options
    local online_options

    actions='merge clean edit sane lint check dist which pack pkg serve disowned upload'

    main_options='-h --help --debug --version'

    merge_options='-h --help'

    clean_options='-h --help'

    edit_options='-h --help'

    sane_options='-h --help -e --enable -d --disable -n --null -m --maintainer
        -N --note -v --variables -t --triggers -u --users -g --groups
        -s --signatures -a --all'

    lint_options='-h --help -m --man -u --udev -s --symlink -d --doc -M --module
        -f --footprint -b --builddir -o --ownership -e --executable -p --path
        -n --shebang -k --backup -c --conflicts -D --debug -a --all'

    check_options='-h --help -f --fast -a --adjust -D --depends -R --reverse'

    dist_options='-h --help -s --sources -c --clean -d --directory'

    which_options='-h --help -c --cat -p --plain'

    pack_options='-h --help -d --directory'

    pkg_options='-h --help -d --directory'

    serve_options='-h --help -p --port -a --address'

    disowned_options='-h --help -d --directory -c --cross -p --plain'

    upload_options='-h --help -H --host -u --user -d --directory -i --insecure'

    online_options='-h --help'

    _get_comp_words_by_ref cur prev
    _get_first_arg

    if [[ -z ${arg} ]];then
        COMPREPLY=($(compgen -W "${actions}" -- "${cur}"))
    elif [[ ${arg} = merge ]]; then
        COMPREPLY=($(compgen -f -W "${merge_options}" -- "${cur}"))
    elif [[ ${arg} = clean ]]; then
        COMPREPLY=($(compgen -W "${clean_options}" -- "${cur}"))
    elif [[ ${arg} = edit ]]; then
        COMPREPLY=($(compgen -W "${edit_options}" -- "${cur}"))
    elif [[ ${arg} = sane ]];then
        COMPREPLY=($(compgen -W "${sane_options}" -- "${cur}"))
    elif [[ ${arg} = lint ]];then
        COMPREPLY=($(compgen -W "${lint_options}" -- "${cur}"))
    elif [[ ${arg} = check ]];then
        COMPREPLY=($(compgen -W "${check_options}" -- "${cur}"))
    elif [[ ${arg} = dist ]];then
        COMPREPLY=($(compgen -W "${dist_options}" -- "${cur}"))
    elif [[ ${arg} = which ]];then
        COMPREPLY=($(compgen -W "${which_options}" -- "${cur}"))
    elif [[ ${arg} = pack ]];then
        COMPREPLY=($(compgen -W "${pack_options}" -- "${cur}"))
    elif [[ ${arg} = pkg ]];then
        COMPREPLY=($(compgen -W "${pkg_options}" -- "${cur}"))
    elif [[ ${arg} = serve ]];then
        COMPREPLY=($(compgen -W "${serve_options}" -- "${cur}"))
    elif [[ ${arg} = disowned ]];then
        COMPREPLY=($(compgen -W "${disowned_options}" -- "${cur}"))
    elif [[ ${arg} = upload ]];then
        COMPREPLY=($(compgen -W "${upload_options}" -- "${cur}"))
    elif [[ ${arg} = upload ]];then
        COMPREPLY=($(compgen -W "${online_options}" -- "${cur}"))
    fi
}

complete -F _spm_tools spm-tools
