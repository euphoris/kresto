from __future__ import print_function

import cmd
import re
import sys

from .corpus import Corpus


class CmdShell(cmd.Cmd, object):
    def __init__(self, cps):
        super(CmdShell, self).__init__()
        self.corpus = cps

    def do_find(self, args):
        words = args.split(' ')
        sentences = self.corpus.concordance(*words)
        match_re = re.compile('('+'|'.join(words)+')', flags=re.IGNORECASE)

        for i, sentence in enumerate(sentences):
            print(i, ') ',
                  match_re.sub('\033[30;43m\\1\033[0m', sentence.raw),
                  sep='')

    def do_quit(self, args):
        return True

    do_EOF = do_quit


def run_command():
    try:
        filename = sys.argv[1]
    except IndexError:
        print('kresto [filename]')
        sys.exit(-1)

    with open(filename) as f:
        text = f.read()
        cps = Corpus(text)

    shell = CmdShell(cps)
    shell.cmdloop()

