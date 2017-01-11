# -*- coding: utf-8 -*-
# Python module
#
# Copyright 2017 Aaron Digulla
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Code to register formatters for date&time values using the excellent Babel library

import datetime
from babel.dates import format_date

class BabelDateFormatter(object):
    def __init__(self, style, pattern, locale):
        self.locale = locale
        self.format_ = style if pattern is None else pattern
    
    def __repr__(self):
        return 'BabelDateFormatter(%r, %r)' % (self.format_, self.locale)
    
    def format(self, inst):
        return format_date(inst, format=self.format_, locale=self.locale)

class DateFormatterFactory(object):
    def __init__(self, ts):
        self.ts = ts
        self.predefined_patterns = set(('short', 'long', 'full', 'medium')) # Formats defined by Babel; see http://babel.pocoo.org/en/latest/dates.html
    
    def can_handle(self, inst):
        return isinstance(inst, datetime.date)
    
    def create_formatter(self, locale, style='medium', pattern=None):
        return BabelDateFormatter(style, pattern, locale)

def setup(ts):
    ts.formatter_factory.register(DateFormatterFactory(ts))
