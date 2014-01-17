from kresto.scripts import parser


def test_parser_words():
    args = parser.parse_args('hello world'.split())
    assert args.words == ['hello', 'world']


def test_parser_limit_default():
    args = parser.parse_args('hello world'.split())
    assert args.limit == 20


def test_parser_limit():
    args = parser.parse_args('hello world -l 10'.split())
    assert args.limit == 10
