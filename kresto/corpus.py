import collections
import re

import nltk


whitespace_re = re.compile(r'\s+')


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


SYMBOL_SET = set('!@#$%^&*()-_+=,.<>;\':"[]{}`~')

RP_SET = {'a', 'an', 'the', 'this', 'these', 'that', 'those', 'any', 'all'}

PRN_SET = {'i', 'my', 'me',
            'we', 'our', 'us',
            'you', 'your',
            'she', 'her',
            'he', 'his', 'him',
            'they', 'their', 'them'}

IN_SET = {'aboard', 'about', 'above', 'across', 'after', 'against', 'along',
          'amid', 'among', 'anti', 'around', 'as', 'at', 'before', 'behind',
          'below', 'beneath', 'beside', 'besides', 'between', 'beyond', 'but',
          'by', 'concerning', 'considering', 'despite', 'down',
          'during', 'except', 'excepting', 'excluding', 'following',
          'for', 'from', 'in', 'inside', 'into', 'like', 'minus', 'near', 'of',
          'off', 'on', 'onto', 'opposite', 'outside', 'over', 'past', 'per',
          'plus', 'regarding', 'round', 'save', 'since', 'than',
          'through', 'to', 'toward', 'towards', 'under', 'underneath',
          'unlike', 'until', 'up', 'upon', 'versus', 'via', 'with', 'within',
          'without', }

STOP_WORD_SET = SYMBOL_SET | RP_SET | PRN_SET | IN_SET


class Corpus():
    def __init__(self, text=None):
        self._stemmer = nltk.LancasterStemmer()
        self.index = collections.defaultdict(set)
        self.stem_index = collections.defaultdict(set)
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
                s = self._stemmer.stem(v)
                self.stem_index[s].add(sntn)

    def concordance(self, words, stem=False):
        if stem:
            words = [self._stemmer.stem(w.lower()) for w in words]
            index = self.stem_index
        else:
            words = [w.lower() for w in words]
            index = self.index

        if words:
            idx = set(index[words[0]])
        else:
            return set()

        for word in words[1:]:
            idx &= index[word]
        return idx

    def find_tag(self, words, tag, stem=False):
        index = self.concordance(words, stem)
        verb_counter = collections.Counter()
        for sentence in index:
            verbs = (t for t in sentence.tokens if t[1].startswith(tag))
            for verb in verbs:
                verb_counter[verb] += 1
        return verb_counter

    def used_with(self, words, stem=False):
        index = self.concordance(words, stem)
        exclude = set(w.lower() for w in words) | STOP_WORD_SET
        vocab_counter = collections.Counter()
        for sentence in index:
            for word in (sentence.vocab - exclude):
                vocab_counter[word] += 1
        return vocab_counter

    def between(self, word1, word2, stem=False):
        index = self.concordance([word1, word2], stem)
        counter = collections.Counter()
        for sentence in index:
            words = [w.lower() for w in sentence.words]
            i1 = words.index(word1)
            i2 = words.index(word2)
            if i1 < i2:
                btw = ' '.join(sentence.words[i1+1:i2])
                counter[btw] += 1
        return counter
