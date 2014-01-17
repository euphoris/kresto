import os.path

from kresto.data import load_corpus


curpath = os.path.dirname(os.path.realpath(__file__))
fixtures_path = os.path.join(curpath, 'fixtures')
license_path = os.path.join(fixtures_path, 'license')


def test_load_corpus_from_directory():
    corpus = load_corpus(fixtures_path)
    assert len(corpus.concordance(['software'])) == 26


def test_load_corpus_from_single_file_gpl():
    gpl_path = os.path.join(license_path, 'gpl.txt')
    corpus = load_corpus(gpl_path)
    assert len(corpus.concordance(['software'])) == 23


def test_load_corpus_from_single_file_bsd():
    bsd_path = os.path.join(license_path, 'bsd.txt')
    corpus = load_corpus(bsd_path)
    assert len(corpus.concordance(['software'])) == 3


def test_load_corpus_from_zipfile():
    zip_path = os.path.join(fixtures_path, 'license.zip')
    corpus = load_corpus(zip_path)
    assert corpus
