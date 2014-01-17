import os
import zipfile

from .corpus import Corpus


def load_corpus(path):
    c = Corpus()
    if os.path.isdir(path):
        for root, _, files in os.walk(path):
            for filename in files:
                with open(os.path.join(root, filename)) as f:
                    c.add_text(f.read())
    else:
        if path.endswith('.zip'):
            with zipfile.ZipFile(path) as zf:
                for name in zf.namelist():
                    if not name.endswith('/'):
                        with zf.open(name) as f:
                            c.add_text(f.read())
        else:
            with open(path) as f:
                c.add_text(f.read())
    return c
