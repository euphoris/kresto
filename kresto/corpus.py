# encoding: utf8
import collections
import re

import nltk


whitespace_re = re.compile(r'\s+')
hyphen_re = re.compile(r'(\w)-\s+(\w)')


class Sentence():
    def __init__(self, raw, id=None):
        self.id = id

        raw = whitespace_re.sub(' ', raw.strip())
        raw = hyphen_re.sub(r'\1\2', raw)
        try:  # ligatures
            raw = raw.replace('ﬀ', 'ff')\
                .replace('ﬁ', 'fi') \
                .replace('ﬂ', 'fl') \
                .replace('ﬃ', 'ffi') \
                .replace('ﬄ', 'ffl')
        except UnicodeDecodeError:
            pass
        self.raw = raw

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
        self.last_sentence_id = 0

        if text:
            self.add_text(text)

    def add_text(self, text):
        tokenizer = nltk.PunktSentenceTokenizer()
        sentences = tokenizer.sentences_from_text(text)

        for s in sentences:
            sntn = Sentence(s, self.last_sentence_id)
            self.sentences.append(sntn)
            self.last_sentence_id += 1

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

    def load_index(self, fp, index):
        n = int(fp.readline().strip())
        for _ in range(n):
            line = fp.readline().strip().split()
            word = line[0]
            for s_id in line[1:]:
                index[word].add(self.sentences[int(s_id)])

    @classmethod
    def load(cls, fp):
        c = cls()
        n = int(fp.readline().strip())
        for i in range(n):
            s = Sentence(fp.readline().strip(), i)
            c.sentences.append(s)
        c.last_sentence_id = n

        c.load_index(fp, c.index)
        c.load_index(fp, c.stem_index)
        return c

    @staticmethod
    def dump_index(fp, index):
        fp.write('{}\n'.format(len(index)))
        for stem, sentences in index.items():
            fp.write(stem + ' ')
            fp.write(' '.join(str(s.id) for s in sentences))
            fp.write('\n')

    def dump(self, fp):
        fp.write('{}\n'.format(len(self.sentences)))
        for i, s in enumerate(self.sentences):
            fp.write(s.raw + '\n')

        self.dump_index(fp, self.index)
        self.dump_index(fp, self.stem_index)
