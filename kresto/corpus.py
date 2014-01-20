# encoding: utf8
import collections
import re

import nltk
from sqlalchemy import Column, Integer, Text, create_engine, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import create_session


Base = declarative_base()

whitespace_re = re.compile(r'\s+')
hyphen_re = re.compile(r'(\w)-\s+(\w)')


stemmer = nltk.LancasterStemmer()


class Sentence(Base):
    __tablename__ = 'sentences'

    id = Column(Integer, primary_key=True)
    raw = Column(Text)
    _words = Column(Text)
    _vocab = Column(Text)
    _stems = Column(Text)

    def __init__(self, raw, id=None):
        raw = whitespace_re.sub(' ', raw.strip())
        raw = hyphen_re.sub(r'\1\2', raw)
        try:  # ligatures
            raw = raw.replace('ﬀ', 'ff') \
                .replace('ﬁ', 'fi') \
                .replace('ﬂ', 'fl') \
                .replace('ﬃ', 'ffi') \
                .replace('ﬄ', 'ffl')
        except UnicodeDecodeError:
            pass

        words = nltk.word_tokenize(raw)
        vocab = set(w.lower() for w in words)
        kwargs = {
            'raw': raw,
            '_words': ' '.join(words),
            '_vocab': ' ' + ' '.join(vocab) + ' ',
            '_stems': ' ' + ' '.join(stemmer.stem(w) for w in vocab) + ' '
        }
        if id:
            kwargs['id'] = id
        super(Sentence, self).__init__(**kwargs)

    @property
    def tokens(self):
        return nltk.pos_tag(self.words)

    @property
    def words(self):
        return self._words.split()

    @property
    def vocab(self):
        return set(self._vocab.split())

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
        self.engine = create_engine('sqlite://')
        Base.metadata.create_all(self.engine)

        if text:
            self.add_text(text)

    def session(self):
        return create_session(bind=self.engine)

    def add_text(self, text):
        tokenizer = nltk.PunktSentenceTokenizer()
        sentences = tokenizer.sentences_from_text(text)

        db = self.session()

        for s in sentences:
            with db.begin():
                db.add(Sentence(s))

    def concordance(self, words, stem=False):
        if stem:
            words = [stemmer.stem(w.lower()) for w in words]
            index = Sentence._stems
        else:
            words = [w.lower() for w in words]
            index = Sentence._vocab

        db = self.session()
        query = (index.contains(' '+word+' ') for word in words)
        return db.query(Sentence).filter(and_(*query)).all()

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
                btw = ' '.join(sentence.words[(i1 + 1):i2])
                counter[btw] += 1
        return counter

    def load_index(self, fp, index):
        """
        Deprecated
        """
        n = int(fp.readline().strip())
        for _ in range(n):
            line = fp.readline().strip().split()
            word = line[0]
            for s_id in line[1:]:
                index[word].add(self.sentences[int(s_id) - 1])

    @classmethod
    def load(cls, fp):
        c = cls()
        n = int(fp.readline().strip())
        db = c.session()
        with db.begin():
            for i in range(1, n + 1):
                db.add(Sentence(fp.readline().strip(), i))
        return c

    @staticmethod
    def dump_index(fp, index):
        """
        Deprecated
        """
        fp.write('{}\n'.format(len(index)))
        for stem, sentences in index.items():
            fp.write(stem + ' ')
            fp.write(' '.join(str(s.id) for s in sentences))
            fp.write('\n')

    def dump(self, fp):
        db = self.session()
        sentences = db.query(Sentence)
        fp.write('{}\n'.format(sentences.count()))
        for s in sentences.order_by('id'):
            fp.write(s.raw + '\n')
