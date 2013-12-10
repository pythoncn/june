from june.filters import markdown


def test_none():
    assert markdown(None) == ''


def test_block_code():
    s = '\n'.join([
        'hello world',
        '',
        '```py',
        'def hello()',
        '    pass',
        '```',
        ''
    ])
    assert 'py' in markdown(s, False)
    assert 'highlight' in markdown(s)


def test_gist():
    gist = 'https://gist.github.com/lepture/5167275'
    assert '</script>' in markdown(gist)
