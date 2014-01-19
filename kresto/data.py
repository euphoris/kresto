from cStringIO import StringIO
import os
import zipfile

import html2text
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage

from .corpus import Corpus


def load_corpus(path):
    c = Corpus()
    if os.path.isdir(path):
        for root, _, files in os.walk(path):
            for filename in files:
                with open(os.path.join(root, filename)) as f:
                    c.add_text(extract_text(f, filename))
    else:
        if path.endswith('.zip'):
            with zipfile.ZipFile(path) as zf:
                for name in zf.namelist():
                    if not name.endswith('/'):
                        with zf.open(name) as f:
                            c.add_text(extract_text(f, name))
        else:
            with open(path) as f:
                c.add_text(extract_text(f, path))
    return c


def extract_text(fp, path):
    """Extract text from a file"""
    if path.endswith('pdf'):
        caching = True
        rsrcmgr = PDFResourceManager(caching=caching)
        outfp = StringIO()
        device = TextConverter(rsrcmgr, outfp, codec='utf-8',
                               laparams=LAParams(), imagewriter=None)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        pages = PDFPage.get_pages(fp, set(), maxpages=0, caching=caching,
                                  check_extractable=True)
        for page in pages:
            page.rotate %= 360
            interpreter.process_page(page)
        device.close()
        content = outfp.getvalue()
        outfp.close()
    else:
        content = fp.read()
        if path.endswith('html') or path.endswith('htm'):
            h = html2text.HTML2Text()
            h.ignore_links = True
            content = h.handle(content)
    return content