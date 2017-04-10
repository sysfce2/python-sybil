import pytest
from sybil.compat import StringIO
from sybil.parsers.codeblock import CodeBlockParser
from tests.helpers import document_from_sample


def test_basic():
    document = document_from_sample('codeblock.txt')
    regions = list(CodeBlockParser()(document))
    assert len(regions) == 4
    namespace = document.namespace
    namespace['y'] = namespace['z'] = 0
    assert regions[0].evaluate(namespace) is None
    assert namespace['y'] == 1
    assert namespace['z'] == 0
    with pytest.raises(Exception) as excinfo:
        regions[1].evaluate(namespace)
    assert str(excinfo.value) == 'boom!'
    assert regions[2].evaluate(namespace) is None
    assert namespace['y'] == 1
    assert namespace['z'] == 1
    assert regions[3].evaluate(namespace) is None
    assert namespace['bin'] == b'x'
    assert namespace['uni'] == u'x'
    assert '__builtins__' not in namespace


def test_future_imports():
    document = document_from_sample('codeblock_future_imports.txt')
    regions = list(CodeBlockParser(['print_function'])(document))
    assert len(regions) == 2
    buffer = StringIO()
    namespace = {'buffer': buffer}
    assert regions[0].evaluate(namespace) is None
    assert buffer.getvalue() == (
        'pathalogical worst case for line numbers\n'
    )
    # the future import line drops the firstlineno by 1
    assert regions[0].parsed.co_firstlineno == 2
    assert regions[1].evaluate(namespace) is None
    assert buffer.getvalue() == (
        'pathalogical worst case for line numbers\n'
        'still should work and have good line numbers\n'
    )
    # the future import line drops the firstlineno by 1
    assert regions[1].parsed.co_firstlineno == 8