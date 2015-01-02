# SPM Bash completion by Ivailo Monev <xakepa10@gmail.com>

_spm()
{
    local action cur prev
    local main_options repo_options remote_options binary_options source_options
    local local_options who_options

    actions='repo remote source binary local who'

    main_options='-h --help --cache --build --root --ignore --demote --mirror
        --timeout--external --chost --cflags --cxxflags --cppflags --ldflags
        --makeflags--man --binaries --shared --static --rpath --pycompile
        --missing --conflicts --backup --scripts --debug --version'

    repo_options='-h --help -c --clean -s --sync -u --update -a --all'

    remote_options='-h --help -n --name -v --version -d --description -D
        --depends -m --makedepends -c --checkdepends -s --sources -o --options
        -b --backup -p --plain'

    source_options='-h --help -C --clean -p --prepare -c --compile -k --check
        -i --install -m --merge -r --remove -D --depends -R --reverse -u
        --update -a --automake'

    binary_options='-h --help -m --merge -r --remove -D --depends -R --reverse -u
        --update'

    local_options='-h --help -n --name -v --version -d --description -D
        --depends -r --reverse -s --size -f --footprint -p --plain'

    who_options='-h --help -p --plain'

    _get_comp_words_by_ref cur prev
    _get_first_arg

    if [[ -z ${arg} ]];then
        COMPREPLY=($(compgen -W "${actions}" -- "${cur}"))
    elif [[ ${arg} = repo ]]; then
        COMPREPLY=($(compgen -f -W "${repo_options}" -- "${cur}"))
    elif [[ ${arg} = remote ]]; then
        COMPREPLY=($(compgen -W "${remote_options}" -- "${cur}"))
    elif [[ ${arg} = source ]]; then
        COMPREPLY=($(compgen -W "${source_options}" -- "${cur}"))
    elif [[ ${arg} = binary ]]; then
        COMPREPLY=($(compgen -W "${binary_options}" -- "${cur}"))
    elif [[ ${arg} = local ]];then
        COMPREPLY=($(compgen -W "${local_options}" -- "${cur}"))
    elif [[ ${arg} = who ]];then
        COMPREPLY=($(compgen -W "${who_options}" -- "${cur}"))
    fi
}

complete -F _spm spm
