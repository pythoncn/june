from june.markdown import rich_markdown, plain_markdown


def test_none():
    assert rich_markdown(None) == ''
    assert plain_markdown(None) == ''


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
    assert 'language-py' in rich_markdown(s, False)
    assert 'highlight' in rich_markdown(s)

    assert 'language-py' not in plain_markdown(s)
    assert 'highlight' not in plain_markdown(s)


def test_gist():
    gist = 'https://gist.github.com/lepture/5167275'
    assert '</script>' in rich_markdown(gist)
