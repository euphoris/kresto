# encoding: utf8
from cStringIO import StringIO

import pytest
from kresto.corpus import Corpus, Sentence


text = '''Hello world!
          This is an example of corpus.
          What a wonderful world!
          Stemming is easy'''


@pytest.fixture
def cps():
    return Corpus(text)


def test_corpus(cps):
    db = cps.session()
    sentences = db.query(Sentence)
    assert sentences.count() == len(text.split('\n'))

    sent = sentences[1]
    assert sent.raw == 'This is an example of corpus.'
    assert 'this' in sent.vocab
    assert 'world' not in sent.vocab


def test_concordance(cps):
    assert len(cps.concordance(['world'])) == 2
    assert len(cps.concordance(['what', 'world'])) == 1
    assert len(cps.concordance(['bye'])) == 0
    assert len(cps.concordance([])) == 4


def test_find_verb(cps):
    verbs = cps.find_tag(['example'], 'VB')
    assert verbs.items() == [(('is', 'VBZ'), 1)]


def test_used_with(cps):
    counter = cps.used_with(['world'])
    assert counter['hello'] == 1


def test_stop_word(cps):
    counter = cps.used_with(['example'])
    assert counter['of'] == 0


def test_between(cps):
    counter = cps.between('what', 'world')
    assert counter['a wonderful'] == 1


def test_stem(cps):
    counter = cps.concordance(['stem'], stem=True)
    assert len(counter) == 1


def test_dump(cps):
    f = StringIO()
    cps.dump(f)
    sentences = '\n'.join(line.strip() for line in text.split('\n'))
    assert f.getvalue().startswith('4\n' + sentences)
    f.close()


def test_load(cps):
    f = StringIO()
    cps.dump(f)
    content = f.getvalue()

    f = StringIO(content)
    c = Corpus.load(f)

    raw = lambda ss: set(s.raw for s in ss)
    assert raw(c.concordance([])) == raw(cps.concordance([]))
    assert raw(c.concordance(['the'])) == raw(cps.concordance(['the']))


def test_hyphen():
    s = Sentence('hello wo- rld.')
    assert s.raw == 'hello world.'


def test_ligatures():
    s = Sentence('He justiﬁed his answer.')
    assert s.raw == 'He justified his answer.'
