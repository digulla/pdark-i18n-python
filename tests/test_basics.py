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
import unittest

setupLogging()

EN_LOCALE = 'en'
EN_US_LOCALE = 'en_US'
DE_LOCALE = 'de_DE'
IT_LOCALE = 'it'

@i18n
def color():
    '''Definition of an I18N method without arguments.'''
    pass

@i18n
def hello(name):
    '''The most simple definition of an I18N method with arguments.
    Calling it will return an "I18NMessage"'''
    pass

@i18n
def and_list(*items):
    '''Show how elements are formatted into an 'a,b and c' type list'''
    pass

@i18n
def or_list(*items):
    '''Show how elements are formatted into an 'a,b or c' type list'''
    pass

@i18n
def number(n):
    '''Formatting of numbers.'''
    pass

@i18n
def plural(n):
    '''How to get 1 house and 2 houses'''
    pass

class TestSimple(unittest.TestCase):
    def setUp(self):
        self.service = TranslationService(default_locale=EN_US_LOCALE)
        
        message_provider = self.service.message_provider
        message_provider.register_message('test_basics.color', EN_LOCALE, 'colour')
        message_provider.register_message('test_basics.color', EN_US_LOCALE, 'color')
        
        message_provider.register_message('test_basics.hello', EN_LOCALE, ['Hello, ', {'arg': 'name'}, '.'])
        message_provider.register_message('test_basics.hello', IT_LOCALE, ['Ciao, ', {'arg': 'name'}, '.'])
        
        # TODO read from config file
        message_provider.register_message('pdark.i18n.list.and', EN_LOCALE, ' and ')
        message_provider.register_message('pdark.i18n.list.and', DE_LOCALE, ' und ')
        message_provider.register_message('pdark.i18n.list.or', EN_LOCALE, ' or ')
        message_provider.register_message('pdark.i18n.list.or', DE_LOCALE, ' oder ')
        message_provider.register_message('pdark.i18n.list.comma', EN_LOCALE, ', ')
        message_provider.register_message('pdark.i18n.list.empty', EN_LOCALE, '')
        
        message_provider.register_message('test_basics.and_list', EN_LOCALE, [{'arg': 'items'}])
        
        message_provider.register_message('test_basics.or_list', EN_LOCALE, [{'arg': 'items', 'type': 'or'}])
        
        message_provider.register_message('test_basics.number', EN_LOCALE, [{'arg': 'n'}])
        message_provider.register_message('pdark.i18n.number.int', EN_LOCALE, '%d')
        message_provider.register_message('pdark.i18n.number.float', EN_LOCALE, '%.2f')
        
        message_provider.register_message('test_basics.plural.one', EN_LOCALE, 'house')
        message_provider.register_message('test_basics.plural.other', EN_LOCALE, 'houses')
        message_provider.register_message('test_basics.plural', EN_LOCALE, [{'arg': 'n', 'plural': 'test_basics.plural'}])
    
    def test_hello(self):
        '''Show how to use the I18N system to get a message.'''
        message = hello("user")
        
        # This is what you'd write in a real test
        assert repr(message) == "I18NMessage(test_basics.hello, ('user',), {'name': 'user'})"
        
    def test_hello_ui(self):
        '''This is how the UI part of the code would turn the message into a string.'''
        message = hello("user")
        text = self.service.translate(message)
        assert text == 'Hello, user.'
    
    def test_hello_type(self):
        message = hello("user")
        assert isinstance(message, I18NMessage)
    
    def test_hello_id(self):
        message = hello("user")
        assert message.key == 'test_basics.hello'
    
    def test_hello_args(self):
        message = hello("user")
        assert message.args == ('user',)
    
    def test_hello_kwargs(self):
        message = hello("user")
        # The I18N framework copies all positional parameters into kwargs,
        # so you can refer to parameters by name instead of the error prone {0} syntax.
        # Not convinced? Add or remove a parameter...
        assert message.kwargs == {'name': 'user'}
    
    def test_hello_locale(self):
        message = hello("user")
        assert message.locale == None
    
    def test_hello_override_locale(self):
        message = hello("user")
        override = message.with_locale(IT_LOCALE)
        assert override.locale == IT_LOCALE
        assert message.locale == None

    def test_locale_it(self):
        '''Like the previous example but simulating an Italian environment'''
        self.service = TranslationService(default_locale=IT_LOCALE)
        self.service.message_provider.register_message('test_basics.hello', IT_LOCALE, ['Ciao, ', {'arg': 'name'}, '.'])
        
        message = hello("user")
        text = self.service.translate(message)
        assert text == 'Ciao, user.'

    def test_message_locale_it(self):
        '''Code might want to create messages which prefer a
        certain locale'''
        message = hello("user").with_locale(IT_LOCALE)
        text = self.service.translate(message)
        assert text == 'Ciao, user.'

    def test_enforce_locale_it(self):
        '''In other cases, you may want to specify the locale
        when you do the translation.'''
        message = hello("user")
        text = self.service.translate(message, IT_LOCALE)
        assert text == 'Ciao, user.'

    def test_override_message_locale(self):
        '''This also works for messages which have a preferred locale.'''
        message = hello("user").with_locale(DE_LOCALE)
        text = self.service.translate(message, IT_LOCALE)
        assert text == 'Ciao, user.'
    
    def test_locale_fallback_en_us(self):
        message = color()
        text = self.service.translate(message, EN_US_LOCALE)
        assert text == 'color'
    
    def test_locale_fallback_en(self):
        message = color()
        text = self.service.translate(message, EN_LOCALE)
        assert text == 'colour'

    def test_nested_message_repr(self):
        inner = color()
        outer = hello(inner)
        assert "I18NMessage(test_basics.hello, (I18NMessage(test_basics.color, (), {}),), {'name': I18NMessage(test_basics.color, (), {})})" == repr(outer)

    def test_nested_message_en_us(self):
        inner = color()
        outer = hello(inner)
        text = self.service.translate(outer, EN_US_LOCALE)
        assert 'Hello, color.' == text
        
    def test_nested_message(self):
        inner = color()
        outer = hello(inner)
        text = self.service.translate(outer, EN_LOCALE)
        assert 'Hello, colour.' == text

    def test_empty_list(self):
        message = and_list()
        text = self.service.translate(message)
        assert '' == text

    def test_single_item_list(self):
        message = and_list('a')
        text = self.service.translate(message)
        assert 'a' == text

    def test_two_item_list(self):
        message = and_list('a', 'b')
        text = self.service.translate(message)
        assert 'a and b' == text

    def test_three_item_list(self):
        message = and_list('a', 'b', 'c')
        text = self.service.translate(message)
        assert 'a, b and c' == text

    def test_three_item_list_german(self):
        message = and_list('a', 'b', 'c')
        text = self.service.translate(message, DE_LOCALE)
        assert 'a, b und c' == text

    def test_empty_or_list(self):
        message = or_list()
        text = self.service.translate(message)
        assert '' == text

    def test_single_item_or_list(self):
        message = or_list('a')
        text = self.service.translate(message)
        assert 'a' == text

    def test_two_item_or_list(self):
        message = or_list('a', 'b')
        text = self.service.translate(message)
        assert 'a or b' == text

    def test_three_item_or_list(self):
        message = or_list('a', 'b', 'c')
        text = self.service.translate(message)
        assert 'a, b or c' == text

    def test_three_item_or_list_german(self):
        message = or_list('a', 'b', 'c')
        text = self.service.translate(message, DE_LOCALE)
        assert 'a, b oder c' == text

    def test_int_numer_0(self):
        message = number(0)
        text = self.service.translate(message)
        assert '0' == text

    def test_int_numer_negative(self):
        message = number(-1234)
        text = self.service.translate(message)
        assert '-1234' == text

    def test_int_numer_one(self):
        message = number(1)
        text = self.service.translate(message)
        assert '1' == text

    def test_int_numer_big(self):
        message = number(1234)
        text = self.service.translate(message)
        assert '1234' == text

    def test_int_numer_huge(self):
        message = number(123456789012345678901234567890)
        text = self.service.translate(message)
        assert '123456789012345678901234567890' == text

    def test_float_numer_0(self):
        message = number(0.)
        text = self.service.translate(message)
        assert '0.00' == text

    def test_float_numer_rounding(self):
        message = number(3.1415)
        text = self.service.translate(message)
        assert '3.14' == text

    def test_float_numer_rounding(self):
        message = number(3.145)
        text = self.service.translate(message)
        assert '3.15' == text

    def test_plural_none(self):
        message = plural(0)
        text = self.service.translate(message)
        assert '0 houses'

    def test_plural_one(self):
        message = plural(1)
        text = self.service.translate(message)
        assert '1 house'

    def test_plural_two(self):
        message = plural(2)
        text = self.service.translate(message)
        assert '2 houses'

    def test_plural_10(self):
        message = plural(10)
        text = self.service.translate(message)
        assert '10 houses'

if __name__ == '__main__':
    unittest.main()
