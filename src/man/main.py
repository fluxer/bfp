#!/bin/python2

import sys, os


try:
    import libmessage
    message = libmessage.Message()
    import libmisc
    misc = libmisc.Misc()

    if not len(sys.argv) > 1:
        sys.stderr.write('usage: man <page>\n')
        sys.exit(1)

    search_exact = True
    search_match = True
    man_sections = ('1', '2', '3', '4', '5', '6', '7', '8')
    man_pages = []
    for path in ('/man', '/share/man', '/local/share/man'):
        man_pages.extend(misc.list_files(path))

    for arg in sys.argv[1:]:
        found = False
        if search_exact:
            for man in man_pages:
                if found:
                    break
                for sec in man_sections:
                    if '/' + arg + '.' + sec in man:
                        found = True
                        os.system('man ' + man)
                        break

        if not found and search_match:
            for man in man_pages:
                for sec in man_sections:
                    if arg in man and '.' + sec in man:
                        found = True
                        os.system('man ' + man)

        if not found:
            message.warning('No match found for', arg)
except OSError as detail:
    message.critical('OS', detail)
    sys.exit(3)
except IOError as detail:
    message.critical('IO', detail)
    sys.exit(4)
except KeyboardInterrupt:
    message.critical('Interrupt signal received')
    sys.exit(5)
except SystemExit:
    sys.exit(2)
except Exception as detail:
    message.critical('Unexpected error', detail)
    sys.exit(1)
#finally:
#    raise
