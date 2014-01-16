from __future__ import print_function

import cmd
import re
import sys

from .data import load_corpus


def sort_items(counter):
    return sorted(counter.items(), key=lambda (_, n): n, reverse=True)


class CmdShell(cmd.Cmd, object):
    def __init__(self, cps):
        super(CmdShell, self).__init__()
        self.corpus = cps

    def do_find(self, args):
        words = args.split(' ')
        sentences = self.corpus.concordance(words)
        match_re = re.compile('('+'|'.join(words)+')', flags=re.IGNORECASE)

        for i, sentence in enumerate(sentences):
            print(i, ') ',
                  match_re.sub('\033[30;43m\\1\033[0m', sentence.raw),
                  sep='')

    def do_verb(self, args):
        words = args.split(' ')
        counter = sort_items(self.corpus.find_tag(words, tag='VB'))
        counter = sorted(counter, key=lambda (_, n): n, reverse=True)
        for token, count in counter:
            word, tag = token
            print(word, tag, count)

    def do_with(self, args):
        words = args.split(' ')
        counter = sort_items(self.corpus.used_with(words))
        for word, n in counter:
            print(word, n)

    def do_quit(self, args):
        return True

    do_EOF = do_quit


def run_command():
    try:
        filename = sys.argv[1]
    except IndexError:
        print('kresto [filename]')
        sys.exit(-1)

    shell = CmdShell(load_corpus(filename))
    shell.cmdloop()

