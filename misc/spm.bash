# SPM Bash completion by Ivailo Monev <xakepa10@laimg.moc>

_spm()
{
    local action cur prev
    local main_options repo_options remote_options source_options
    local local_options who_options who_options

    actions='repo remote source local who'

    main_options='-h --help --cache --build --root --gpg --ignore --notify
        --mirror --timeout --verify --chost --cflags --cxxflags --cppflags
        --ldflags --makeflags --purge --man --split --binaries --shared
        --static --missing --ownership --conflicts --backup --scripts --debug
        --version'

    repo_options='-h --help -c --clean -s --sync -u --update -a --all'

    remote_options='-h --help -n --name -v --version -r --release
        -d --description -D --depends -m --makedepends -O --optdepends
        -c --checkdepends -s --sources -k --pgpkeys -o --options -b --backup
        -p --plain'

    source_options='-h --help -C --clean -f --fetch -p --prepare -c --compile
        -k --check -i --install -m --merge -r --remove -D --depends
        -R --reverse -u --update -a --automake'

    local_options='-h --help -n --name -v --version -R --release
        -d --description -D --depends -O --optdepends -r --reverse -s --size
        -f --footprint -b --backup -p --plain'

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
    elif [[ ${arg} = local ]];then
        COMPREPLY=($(compgen -W "${local_options}" -- "${cur}"))
    elif [[ ${arg} = who ]];then
        COMPREPLY=($(compgen -W "${who_options}" -- "${cur}"))
    fi
}

complete -F _spm spm
