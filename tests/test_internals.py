# -*- coding: utf-8 -*-
#
# Copyright 2017 Aaron Digulla
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from pdark.i18n import LocaleFallbackStrategy
from pdark.i18n.test_support import *
import locale
import unittest

setupLogging()

class TestLocaleFallbackStrategy(unittest.TestCase):
    def test_short_locales(self):
        s = LocaleFallbackStrategy('en')
        actual = s.apply('de')
        assert ['de', 'en'] == actual

    def test_same_locales(self):
        s = LocaleFallbackStrategy('en')
        actual = s.apply('en')
        assert ['en', 'en'] == actual
        
    def test_longer_locales(self):
        s = LocaleFallbackStrategy('en_US')
        actual = s.apply('de_CH')
        assert ['de_CH', 'de', 'en_US', 'en'] == actual

if __name__ == '__main__':
    unittest.main()
