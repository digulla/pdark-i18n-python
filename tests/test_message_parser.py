# -*- coding: utf-8 -*-
#
# Copyright 2017 Aaron Digulla
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from pdark.i18n import MessageParser, TranslationService
from pdark.i18n.test_support import *

EN_US_LOCALE = 'en_US'

def parse(input):
    ts = TranslationService(default_locale=EN_US_LOCALE)
    result = MessageParser(ts).parse(input)
    return result

def test_plain_text():
    actual = parse('xxx')
    assert "MessageFormatter(text('xxx'),)" == repr(actual)

def test_just_arg0():
    actual = parse([{'arg': 0}])
    assert "MessageFormatter(arg([0]),)" == repr(actual)

def test_just_arg_with_text_before():
    actual = parse(['a', {'arg': 0}])
    assert "MessageFormatter(text('a'), arg([0]))" == repr(actual)

def test_just_arg_with_text_after():
    actual = parse([{'arg': 0}, 'b'])
    assert "MessageFormatter(arg([0]), text('b'))" == repr(actual)

def test_just_arg_with_text_around():
    actual = parse(['a', {'arg': 0}, 'b'])
    assert "MessageFormatter(text('a'), arg([0]), text('b'))" == repr(actual)

def test_just_arg0_with_options():
    actual = parse([{'arg': 0, 'options': ['a','b','c']}])
    assert "MessageFormatter(arg([0], {'options': ['a', 'b', 'c']}),)" == repr(actual)

def test_escape_open():
    actual = parse('{')
    assert "MessageFormatter(text('{'),)" == repr(actual)

def test_many_open():
    actual = parse('{{{')
    assert "MessageFormatter(text('{{{'),)" == repr(actual)

def test_escape_close():
    actual = parse('}')
    assert "MessageFormatter(text('}'),)" == repr(actual)

def test_many_close():
    actual = parse('}}}')
    assert "MessageFormatter(text('}}}'),)" == repr(actual)

def test_escape_with_text():
    actual = parse('{a}')
    assert "MessageFormatter(text('{a}'),)" == repr(actual)

def test_escape_with_arg0():
    actual = parse(['{', {'arg': 0}, '}'])
    assert "MessageFormatter(text('{'), arg([0]), text('}'))" == repr(actual)

def test_escape_before_param():
    actual = parse(['{a}', {'arg': 0}])
    assert "MessageFormatter(text('{a}'), arg([0]))" == repr(actual)

if __name__ == '__main__':
    unittest.main()
