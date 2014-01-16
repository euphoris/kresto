import collections
import re

import nltk


whitespace_re = re.compile('\s+')


class Sentence():
    def __init__(self, raw):
        self.raw = whitespace_re.sub(' ', raw.strip())
        self.words = nltk.word_tokenize(self.raw)
        self.vocab = set(w.lower() for w in self.words)

    def __hash__(self):
        return hash(self.raw)


class Corpus():
    def __init__(self, text):
        self.index = collections.defaultdict(set)
        self.sentences = []

        tokenizer = nltk.PunktSentenceTokenizer()
        sentences = tokenizer.sentences_from_text(text)

        for s in sentences:
            sntn = Sentence(s)
            self.sentences.append(sntn)
            
            for v in sntn.vocab:
                self.index[v].add(sntn)


    def concordance(self, *words):
        try:
            index = set(self.index[words[0]])
        except IndexError:
            return set()

        for word in words[1:]:
            index &= self.index[word]
        return index
