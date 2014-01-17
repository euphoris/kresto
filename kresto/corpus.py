import collections
import re
import html2text

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

    def load_text(self, fp, name):
        """Load texts from a file"""
        content = fp.read()
        if name.endswith('html') or name.endswith('htm'):
            h = html2text.HTML2Text()
            h.ignore_links = True
            content = h.handle(content)
        self.add_text(content)

    def concordance(self, words):
        words = [w.lower() for w in words]

        if words:
            index = set(self.index[words[0]])
        else:
            return set()

        for word in words[1:]:
            index &= self.index[word]
        return index

    def find_tag(self, words, tag):
        index = self.concordance(words)
        verb_counter = collections.Counter()
        for sentence in index:
            verbs = (t for t in sentence.tokens if t[1].startswith(tag))
            for verb in verbs:
                verb_counter[verb] += 1
        return verb_counter

    def used_with(self, words):
        index = self.concordance(words)
        exclude = set(w.lower() for w in words) | STOP_WORD_SET
        vocab_counter = collections.Counter()
        for sentence in index:
            for word in (sentence.vocab - exclude):
                vocab_counter[word] += 1
        return vocab_counter