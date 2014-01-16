import pytest
from kresto.corpus import Corpus


@pytest.fixture(scope='module')
def cps():
    return Corpus('Hello world! This is an example. What a wonderful world!')


def test_corpus(cps):
    assert len(cps.sentences) == 3

    sent = cps.sentences[1]
    assert len(sent.words) == 5
    assert 'this' in sent.vocab
    assert 'world' not in sent.vocab


def test_index(cps):
    assert len(cps.index['world']) == 2
    assert len(cps.index['example']) == 1


def test_concordance(cps):
    assert len(cps.concordance(['world'])) == 2
    assert len(cps.concordance(['what', 'world'])) == 1
    assert len(cps.concordance(['bye'])) == 0
    assert len(cps.concordance([])) == 0


def test_find_verb(cps):
    verbs = cps.find_tag(['example'], 'VB')
    assert verbs.items() == [(('is', 'VBZ'), 1)]


def test_used_with(cps):
    counter = cps.used_with(['world'])
    assert counter['hello'] == 1
