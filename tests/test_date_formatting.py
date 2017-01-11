# -*- coding: utf-8 -*-
#
# Copyright 2017 Aaron Digulla
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from pdark.i18n import *
from pdark.i18n.test_support import *
import locale
import datetime
import unittest
import pdark.i18n.babel

DEFAULT_LOCALE = locale.getlocale()
EN_LOCALE = 'en'
EN_US_LOCALE = 'en_US'
DE_LOCALE = 'de_DE'
IT_LOCALE = 'it'

@i18n
def default_date(date):
    '''This method uses the default date formatter.'''
    pass

@i18n
def date_short(date):
    '''This method configures the date formatter with a symbolic argument'''
    pass

@i18n
def date_long(date):
    '''This method configures the date formatter with a symbolic argument'''
    pass

@i18n
def date_explicit_format(date):
    '''This method configures the date formatter with an explicit format argument'''
    pass

@i18n
def day_name_full(date):
    '''Just the weekday as locale's ful name'''
    pass

DATE = datetime.date(2016, 12, 26)

class TestFormatting(unittest.TestCase):
    def setUp(self):
        self.service = TranslationService(default_locale=EN_LOCALE)
        pdark.i18n.babel.setup(self.service)
        
        message_provider = self.service.message_provider
        message_provider.register_message('test_date_formatting.default_date', EN_LOCALE, ['Default date format: ', {'arg': 'date'}])
        message_provider.register_message('test_date_formatting.default_date', IT_LOCALE, ['Default Italian date format: ', {'arg': 'date'}])
        message_provider.register_message('test_date_formatting.default_date', DE_LOCALE, ['Default German date format: ', {'arg': 'date'}])
        
        message_provider.register_message('test_date_formatting.date_short', EN_LOCALE, ['Short date format: ', {'arg': 'date', 'style': 'short'}])
        
        message_provider.register_message('test_date_formatting.date_long', EN_LOCALE, ['Long date format: ', {'arg': 'date', 'style': 'long'}])
        
        message_provider.register_message('test_date_formatting.date_explicit_format', EN_LOCALE, ['Explicit date format: ', {'arg': 'date', 'pattern': 'yyyy-MM-dd'}])

    def test_default_date_repr(self):
        message = default_date(DATE)
        assert repr(message) == "I18NMessage(test_date_formatting.default_date, (datetime.date(2016, 12, 26),), {'date': datetime.date(2016, 12, 26)})"
    
    def test_default_date_args(self):
        message = default_date(DATE)
        assert message.args == (DATE,)
    
    def test_default_date(self):
        message = default_date(DATE)
        text = self.service.translate(message)
        assert text == 'Default date format: Dec 26, 2016'

    def test_default_date_italian(self):
        message = default_date(DATE)
        text = self.service.translate(message, IT_LOCALE)
        assert 'Default Italian date format: 26 dic 2016' == text

    def test_default_date_german(self):
        message = default_date(DATE)
        text = self.service.translate(message, DE_LOCALE)
        assert text == 'Default German date format: 26.12.2016'

    def test_date_short_repr(self):
        message = date_short(DATE)
        assert repr(message) == "I18NMessage(test_date_formatting.date_short, (datetime.date(2016, 12, 26),), {'date': datetime.date(2016, 12, 26)})"

    def test_date_short(self):
        message = date_short(DATE)
        text = self.service.translate(message)
        assert text == 'Short date format: 12/26/16'

    def test_date_long_repr(self):
        message = date_long(DATE)
        assert repr(message) == "I18NMessage(test_date_formatting.date_long, (datetime.date(2016, 12, 26),), {'date': datetime.date(2016, 12, 26)})"

    def test_date_long(self):
        message = date_long(DATE)
        text = self.service.translate(message)
        assert text == 'Long date format: December 26, 2016'

    def test_date_long_german(self):
        message = date_long(DATE)
        text = self.service.translate(message, DE_LOCALE)
        # There is no long translation for the text but Babel can still look up the German month names.
        assert text == 'Long date format: 26. Dezember 2016'
        
    def test_date_explicit_format_repr(self):
        message = date_explicit_format(DATE)
        assert repr(message) == "I18NMessage(test_date_formatting.date_explicit_format, (datetime.date(2016, 12, 26),), {'date': datetime.date(2016, 12, 26)})"
        
    def test_date_explicit_format(self):
        message = date_explicit_format(DATE)
        text = self.service.translate(message)
        assert text == 'Explicit date format: 2016-12-26'


if __name__ == '__main__':
    unittest.main()
