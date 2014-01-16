import collections
import re

import nltk


whitespace_re = re.compile('\s+')


class Sentence():
    def __init__(self, raw):
        self.raw = whitespace_re.sub(' ', raw.strip())
        self.words = nltk.word_tokenize(self.raw)
        self._tokens = None
        self.vocab = set(w.lower() for w in self.words)

    @property
    def tokens(self):
        if not self._tokens:
            self._tokens = nltk.pos_tag(self.words)
        return self._tokens

    def __hash__(self):
        return hash(self.raw)


class Corpus():
    def __init__(self, text=None):
        self.index = collections.defaultdict(set)
        self.sentences = []

        if text:
            self.add_text(text)

    def add_text(self, text):
        tokenizer = nltk.PunktSentenceTokenizer()
        sentences = tokenizer.sentences_from_text(text)

        for s in sentences:
            sntn = Sentence(s)
            self.sentences.append(sntn)
            
            for v in sntn.vocab:
                self.index[v].add(sntn)


    def concordance(self, words):
        if words:
            index = set(self.index[words[0]])
        else:
            return set()

        for word in words[1:]:
            index &= self.index[word]
        return index
