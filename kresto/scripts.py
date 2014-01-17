from __future__ import print_function

import argparse
import cmd
import re
import sys

from .data import load_corpus


def sort_items(counter):
    return sorted(counter.items(), key=lambda (_, n): n, reverse=True)


parser = argparse.ArgumentParser()
parser.add_argument('words', nargs='+')
parser.add_argument('--limit', '-l', type=int, default=20)

between_parser = argparse.ArgumentParser()
between_parser.add_argument('words', nargs=2)
between_parser.add_argument('--limit', '-l', type=int, default=20)


def parse(args):
    return parser.parse_args(args.split())



class CmdShell(cmd.Cmd, object):
    def __init__(self, cps):
        super(CmdShell, self).__init__()
        self.corpus = cps

    def do_find(self, args):
        args = parse(args)
        sentences = self.corpus.concordance(args.words)
        match_re = re.compile('('+'|'.join(args.words)+')', flags=re.IGNORECASE)

        for i, sentence in enumerate(sentences):
            print(i, ') ',
                  match_re.sub('\033[30;43m\\1\033[0m', sentence.raw),
                  sep='')
            if i >= args.limit:
                break

    def do_verb(self, args):
        args = parse(args)
        counter = sort_items(self.corpus.find_tag(args.words, tag='VB'))
        for token, count in counter[:args.limit]:
            word, tag = token
            print(word, tag, count)

    def do_with(self, args):
        args = parse(args)
        counter = sort_items(self.corpus.used_with(args.words))
        for word, n in counter[:args.limit]:
            print(word, n)

    def do_between(self, args):
        args = between_parser.parse_args(args.split())
        counter = sort_items(self.corpus.between(args.words[0], args.words[1]))
        for word, n in counter[:args.limit]:
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
