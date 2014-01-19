from __future__ import print_function

import argparse
import cmd
import re
import sys

import nltk

from .data import load_corpus
from kresto.corpus import Corpus


def sort_items(counter):
    return sorted(counter.items(), key=lambda (_, n): n, reverse=True)


def create_parser(nword):
    parser = argparse.ArgumentParser()
    parser.add_argument('words', nargs=nword)
    parser.add_argument('--limit', '-l', type=int, default=20)
    parser.add_argument('--stem', '-s', action='store_const', const=True,
                        default=False)
    return parser


parser = create_parser('+')
between_parser = create_parser(2)

file_parser = argparse.ArgumentParser()
file_parser.add_argument('filename')


def parse(args):
    return parser.parse_args(args.split())


class CmdShell(cmd.Cmd, object):
    def __init__(self, cps):
        super(CmdShell, self).__init__()
        self.corpus = cps
        self._stemmer = nltk.LancasterStemmer()

    def do_find(self, args):
        args = parse(args)
        if args.stem:
            words = [self._stemmer.stem(w) for w in args.words]
        else:
            words = args.words
        sentences = self.corpus.concordance(words, args.stem)

        match_re = re.compile('('+'|'.join(words)+')', flags=re.IGNORECASE)

        for i, sentence in enumerate(sentences):
            print(i, ') ', sep='', end='')
            c = 0
            for word in sentence.words:
                b = sentence.raw[c:].find(word)
                if b < 0:
                    continue
                print(sentence.raw[c:c+b], end='')
                c += b + len(word)

                if (word in words or
                        (args.stem and self._stemmer.stem(word) in words)):
                    print('\033[30;43m', word, '\033[0m', sep='', end='')
                else:
                    print(word, end='')
            print()

            if i >= args.limit:
                break

    def do_verb(self, args):
        args = parse(args)
        counter = sort_items(self.corpus.find_tag(args.words, 'VB', args.stem))
        for token, count in counter[:args.limit]:
            word, tag = token
            print(word, tag, count)

    def do_with(self, args):
        args = parse(args)
        counter = sort_items(self.corpus.used_with(args.words, args.stem))
        for word, n in counter[:args.limit]:
            print(word, n)

    def do_between(self, args):
        args = between_parser.parse_args(args.split())
        counter = self.corpus.between(args.words[0], args.words[1], args.stem)
        counter = sort_items(counter)
        for word, n in counter[:args.limit]:
            print(word, n)

    def do_load(self, args):
        args = file_parser.parse_args(args.split())
        with open(args.filename) as f:
            self.corpus = Corpus.load(f)

    def do_dump(self, args):
        args = file_parser.parse_args(args.split())
        with open(args.filename, 'w') as f:
            self.corpus.dump(f)

    def do_quit(self, args):
        return True

    do_EOF = do_quit


def run_command():
    try:
        filename = sys.argv[1]
        cps = load_corpus(filename)
    except IndexError:
        cps = Corpus()

    shell = CmdShell(cps)
    shell.cmdloop()
