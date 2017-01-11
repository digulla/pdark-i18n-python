# -*- coding: utf-8 -*-
#
# Copyright 2017 Aaron Digulla
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# This is the main module

from io import StringIO
import collections
import inspect
import locale
import logging
import os
import re
import traceback

__all__ = [
    'i18n',
    'I18NMessage',
    'TranslationService'
]

log = logging.getLogger(__name__)

def getLogger(o):
    '''Get a logger for an instance'''
    clz = o.__class__
    return logging.getLogger('%s.%s' % (clz.__module__, clz.__name__))

class I18NMessage(object):
    '''Encode the information which message to display and the arguments for the message.
    
    Methods decorated with @i18n will return instanes of this type.'''
    def __init__(self, key, locale=None, *args, **kwargs):
        self.key, self.locale, self.args, self.kwargs = key, locale, args, kwargs
    
    def __repr__(self):
        if self.locale is None:
            return 'I18NMessage(%s, %r, %r)' % (self.key, self.args, self.kwargs)
        
        return 'I18NMessage(%s, locale=%r, %r, %r)' % (self.key, self.locale, self.args, self.kwargs)

    def __eq__(self):
        '''Two messages are the same when the key is the same and the arguments are the same.
        
        The locale is irrelevant.'''
        return isinstance(other, I18NMessage) and self.key == other.key and self.args == other.args and self.kwargs == other.kwargs

    def with_locale(self, locale):
        '''Create a new I18N message with a different locale.
        
        Use this to specify preferred locales for messages.
        A typical use case is when you need to display a message
        in two languages on the same screen, like language selectors
        which often display "German - Deutsch" or vocabulary learning.'''
        return I18NMessage(self.key, locale, *self.args, **self.kwargs)

# Module names: file name of the module (with path)
i18nKnownModules = {}

def registerModuleForAutoConfig(func):
    '''Collect all modules which have I18N methods and functions in a single place.
    
    The list of modules can later be used to discover text files
    which contain messages.
    '''
    module = inspect.getmodule(func)

    global i18nKnownModules
    if not module.__name__ in i18nKnownModules:
        log.info('Registering new module %s', module.__name__)
        i18nKnownModules[module.__name__] = inspect.getfile(func)

    return module

def i18n(func):
    '''Decoration for a function or method which can be used to create I18N messages.
    
    If the method returns None, for example when a function only uses
    pass as body, a default I18N message will be supplied. The key 
    of the message is built from the module + the function name.
    All the arguments to the function are passed to the I18N message.
    
    This way, you can do nothing to get the default behavior.
    Or you can return your own I18N message.
    Or you can just check the arguments and return None to
    still get the default behavior.
    '''
    module = registerModuleForAutoConfig(func)

    key = '%s.%s' % (module.__name__, func.__name__)
    def wrapped_func(*args, **kwargs):
        #print 'wrapped_func',key,args,kwargs
        callargs = inspect.getcallargs(func, *args, **kwargs)
        
        result = func(*args, **kwargs)
        if result is None:
            return I18NMessage(key, None, *args, **callargs)
        
        return result

    return wrapped_func

class DetailFormatter(object):
    '''Interface for detail formatters.'''
    def format(self, inst):
        return repr(inst)

class DetailFormatterFactory(object):
    '''Interface for a factory of detail formatters.'''
    
    def can_handle(self, inst):
        '''Return True if this factory can create formatters for this object'''
        return False
    
    def create_formatter(self, locale):
        '''Actually create a formatter for an object.
        
        Factories can create new formatters with every call or return the same
        instance when it's stateless.'''
        raise NotImplementedError()

class StringFormatter(DetailFormatter):
    def format(self, inst):
        return inst

class StringFormatterFactory(DetailFormatterFactory):
    '''Formatter for plain strings.
    
    This exists because we want error messages for
    all types that don't have an formatter.'''
    def __init__(self):
        self.inst = StringFormatter()

    def can_handle(self, inst):
        return isinstance(inst, str)
    
    def create_formatter(self, locale):
        return self.inst

class I18nMessageFormatter(DetailFormatter):
    '''Formatter which turns I18NMessage into strings.'''
    def __init__(self, ts, locale):
        self.ts = ts
        self.locale = locale
    
    def format(self, inst):
        return self.ts.translate(inst, self.locale)

class I18nMessageFormatterFactory(object):
    def __init__(self, ts):
        self.ts = ts

    def can_handle(self, inst):
        return isinstance(inst, I18NMessage)
    
    def create_formatter(self, locale):
        # Maybe cache formatter per locale?
        return I18nMessageFormatter(self.ts, locale)

class ListFormatter(DetailFormatter):
    def __init__(self, ts, locale, **options):
        self.ts = ts
        self.locale = locale
        self.options = options
        
        self.empty_message = I18NMessage('pdark.i18n.list.empty')
        self.comma_message = I18NMessage('pdark.i18n.list.comma')
        self.and_message = I18NMessage('pdark.i18n.list.and')
        self.or_message = I18NMessage('pdark.i18n.list.or')
    
    def format(self, inst):
        if len(inst) == 0:
            return self.ts.translate(self.empty_message, self.locale)
        
        def process(item):
            options = {}
            formatter = self.ts.formatter_factory.create_formatter(self.locale, item, options)
            return formatter.format(item)
        
        as_strings = [process(item) for item in inst]
        
        if len(inst) == 1:
            return as_strings[0]
        
        tail = as_strings[-1]
        head = as_strings[0:-1]
        
        if len(head) > 1:
            joiner = self.ts.translate(self.comma_message, self.locale)
            head = joiner.join(head)
        else:
            head = head[0]
        
        # TODO "neither...nor"
        joiner = self.ts.translate(self.get_tail_joiner(), self.locale)
        return joiner.join((head, tail))
    
    def get_tail_joiner(self):
        if self.options.get('type') == 'or':
            return self.or_message
        
        return self.and_message

class ListFormatterFactory(DetailFormatterFactory):
    def __init__(self, ts):
        self.ts = ts

    def can_handle(self, inst):
        return isinstance(inst, (list, tuple))
    
    def create_formatter(self, locale, **options):
        return ListFormatter(self.ts, locale, **options)

class NumberFormatter(DetailFormatter):
    def __init__(self, ts, locale, plural=None):
        self.ts = ts
        self.locale = locale
        
        self.plural_message_base = None
        self.plural_message_base = plural
        
        self.int_message = I18NMessage('pdark.i18n.number.int')
        self.float_message = I18NMessage('pdark.i18n.number.float')

    def format(self, inst):
        message = self.int_message if isinstance(inst, int) else self.float_message
        spec = self.ts.translate(message, self.locale)
        
        if self.plural_message_base is None:
            # Note: There is no simple way to format a number according to a locale without breaking stuff. 
            # Use the formatter from pdark.i18n.babel if you need locale aware formatting of numbers.
            return spec % inst
        
        if inst == 0:
            text = self.get_plural_message('zero')
        elif inst == 1:
            text = self.get_plural_message('one')
        elif inst == 2:
            text = self.get_plural_message('two')
        else:
            # TODO how to handle "few" and "many"?
            text = self.get_plural_message('other')
        
        return '%s %s' % (spec % inst, text)
    
    def get_plural_message(self, tag):
        key = self.plural_message_base + '.one'
        message = I18NMessage(key)
        try:
            return self.ts.translate(message, self.locale)
        except I18nException:
            if tag == 'other':
                raise
            
            key = self.plural_message_base + '.other'
            message = I18NMessage(key)
            return self.ts.translate(message, self.locale)

class NumberFormatterFactory(DetailFormatterFactory):
    def __init__(self, ts):
        self.ts = ts

    def can_handle(self, inst):
        return isinstance(inst, (int, float))
    
    def create_formatter(self, locale, **options):
        return NumberFormatter(self.ts, locale, **options)

class DefaultFormatterFactory(object):
    '''A factory to create formatters for various objects.'''
    def __init__(self, ts):
        self.ts = ts
        self.delegates = [
            StringFormatterFactory(),
            I18nMessageFormatterFactory(ts),
            ListFormatterFactory(ts),
            NumberFormatterFactory(ts),
        ]
        self.cache = {}
    
    def register(self, *delegates):
        self.delegates.extend(delegates)
    
    def create_formatter(self, locale, inst, options):
        delegate = self.cache.get(type(inst))
        if delegate is not None:
            return delegate.create_formatter(locale, **options)
        
        for delegate in self.delegates:
            if delegate.can_handle(inst):
                self.cache[type(inst)] = delegate
                return delegate.create_formatter(locale, **options)
        
        raise I18nException('No factory can handle %s %r' % (type(inst), inst,))

class I18nException(Exception):
    pass

class MissingTextStrategy(object):
    '''Strategy how to handle missing texts.'''
    pass

class LogMissingTextStrategy(MissingTextStrategy):
    '''Just log missing texts and directly convert the I18N message to string.
    
    This strategy is most useful during production when you don't want the
    application to stop working just because a translation is missing.'''
    def __init__(self):
        super(LogMissingTextStrategy, self).__init__()
        
        self.log = getLogger(self)        
    
    def apply(self, i18n_message, locale):
        self.log.warn('Missing text for %r', i18n_message.key)
        return text_message_formatter(repr(i18n_message))

class FailOnMissingTextsStrategy(MissingTextStrategy):
    '''Throw an exception on missing texts.
    
    This strategy is most useful during development to catch problems early.'''
    def __init__(self):
        super(FailOnMissingTextsStrategy, self).__init__()
    
    def apply(self, i18n_message, locale):
        raise I18nException('Missing text for %r' % i18n_message.key)

class MessageProvider(object):
    '''Get the MessageFormatter instance which knows how to build the text
    for an I18NMessage.
    
    Create a new instance of this type if you have a new source for
    texts.'''
    def __init__(self, missing_text_strategy=None):
        self.log = getLogger(self)

        self.missing_text_strategy = self.create_missing_text_strategy(missing_text_strategy)
    
    def create_missing_text_strategy(self, missing_text_strategy):
        if missing_text_strategy is None:
            return FailOnMissingTextsStrategy()
        
        return missing_text_strategy
    
    def lookup_message(self, i18n_message, locale):
        '''Return an instance of MessageFormatter.'''
        return self.missing_text_strategy.apply(i18n_message, locale)

class SimpleMessageProvider(MessageProvider):
    '''Very simple implementation of a message provider which allows to
    add messages to a pool.
    
    '''
    def __init__(self, default_locale, parser, missing_text_strategy=None, locale_fallback_strategy=None):
        super(SimpleMessageProvider, self).__init__(missing_text_strategy)
        
        self.default_locale = default_locale
        self.parser = parser
        
        self.pattern_cache = collections.defaultdict(dict)
        self.locale_fallback_strategy =  self.create_locale_fallback_strategy(locale_fallback_strategy)

    def create_locale_fallback_strategy(self, locale_fallback_strategy):
        if locale_fallback_strategy is None:
            return LocaleFallbackStrategy(self.default_locale)
        
        return locale_fallback_strategy

    def register_message(self, key, locale, pattern):
        keys = self.pattern_cache[locale]
        # TODO lazy parsing since we don't need all the messages at once and we probably never need all of them
        keys[key] = self.parser.parse(pattern)

    def lookup_message(self, i18n_message, locale):
        fallback_locales = self.locale_fallback_strategy.apply(locale)
        key = i18n_message.key
        self.log.debug('Looking for %r with locales %r', key, fallback_locales)
        for lc in fallback_locales:
            formatter = self.lookup_single_locale(key, lc)
            if formatter is not None:
                return formatter

        return self.missing_text_strategy.apply(i18n_message, locale)

    def lookup_single_locale(self, key, locale):
        #self.log.debug('lookup_single_locale: Trying %s', locale)
        keys = self.pattern_cache.get(locale, None)
        if keys is None:
            return None
        
        formatter = keys.get(key, None)
        if formatter is not None:
            self.log.debug('lookup_single_locale: Found key %r for %r', key, locale)
        
        return formatter

class TranslationService(object):
    '''This service is the core of the whole system.
    
    It connects all the other parts, namely the message provider and the
    formatter factory.'''
    def __init__(self, default_locale=None, formatter_factory=None, message_provider=None):
        self.log = getLogger(self)
        
        self.default_locale = self.determine_default_locale(default_locale)
        self.formatter_factory = self.create_formatter_factory(formatter_factory)
        self.message_provider = self.create_message_provider(message_provider)
    
    def determine_default_locale(self, default_locale):
        if default_locale is None:
            return locale.getdefaultlocale()[0]
        
        return default_locale
    
    def create_formatter_factory(self, formatter_factory):
        if formatter_factory is None:
            return DefaultFormatterFactory(self)
        
        return formatter_factory
    
    def create_message_provider(self, message_provider):
        if message_provider is None:
            parser = MessageParser(self)
            return SimpleMessageProvider(self.default_locale, parser)
        
        return message_provider
    
    def translate(self, i18n_message, locale=None):
        '''Translate a I18N message: Get the message itself from the message provider
        and format it using the arguments.'''
        try:
            if locale is None:
                locale = i18n_message.locale
            
            if locale is None:
                locale = self.default_locale
            
            formatter = self.message_provider.lookup_message(i18n_message, locale)
            if formatter is None:
                raise I18nException('Missing formatter for %r, locale=%r' % (i18n_message, locale))
            
            args = i18n_message.args
            kwargs = i18n_message.kwargs

            try:
                result = formatter.format(locale, args, kwargs)
            except Exception as e:
                raise I18nException('Error formatting with %r, args=%r, kwargs=%r: %s' % (formatter, args, kwargs, e)) from e
            return result
            
        except Exception as e:
            raise I18nException('Error translating %r, locale=%r: %s' % (i18n_message, locale, e)) from e

class LocaleFallbackStrategy(object):
    '''Determine the order in which locales will be searched.
    
    This strategy will strip details from the end of the locale:
    'de_CH' with a default 'en_US' will search 'de_CH', 'de', 'en_US' and 'en'.'''
    def __init__(self, default_locale):
        self.default_locale = default_locale
    
    def apply(self, locale):
        result = []
        self.split_locale(result, locale)
        self.split_locale(result, self.default_locale)
        return result
    
    def split_locale(self, result, locale):
        while locale is not None:
            result.append(locale)

            pos = locale.rfind('_')
            if pos < 0:
                break

            locale = locale[:pos]        

class Fragment(object): pass

class TextFragment(Fragment):
    '''A plain text fragment of a message.'''
    def __init__(self, text):
        self.text = text
    
    def append_to(self, buffer, locale, args, kwargs):
        buffer.write(self.text)
    
    def __repr__(self):
        return 'text(%r)' % self.text

class ArgumentFragment(Fragment):
    '''A fragment which references a parameter of the I18N message.'''
    def __init__(self, ts, ref, options):
        self.ts, self.ref, self.options = ts, ref, options

    def append_to(self, buffer, locale, args, kwargs):
        value = self.ref.get(args, kwargs)
        #print('ref=%r value=%r' % (self.ref, value))
        formatter = self.ts.formatter_factory.create_formatter(locale, value, self.options)
        #print('formatter=%r' % formatter)
        text = formatter.format(value)
        buffer.write(text)

    def __repr__(self):
        if len(self.options) == 0:
            return 'arg(%r)' % (self.ref,)
        
        return 'arg(%r, %r)' % (self.ref, self.options)

class IndexRef(object):
    '''Access a parameter by index (0, 1, ... n)'''
    def __init__(self, index):
        self.index = index
    
    def get(self, args, kwargs):
        return args[self.index]
    
    def __repr__(self):
        return '[%d]' % self.index

class NameRef(object):
    '''Access a parameter by name.
    
    This is the preferred way since 
    
    - it prevents problems when parameters are added or removed
    
    - it makes it easier to spot mistakes
    
    - people can still have an idea what the parameter means when they 
    translate messages
    
    - it's not that much slower
    '''
    def __init__(self, name):
        self.name = name
    
    def get(self, args, kwargs):
        return kwargs[self.name]
    
    def __repr__(self):
        return '[%r]' % self.name

class MessageFormatter(object):
    '''Efficiently collect all fragments into a single string.'''
    def __init__(self, fragments):
        self.fragments = tuple(fragments)
    
    def format(self, locale, args, kwargs):
        buffer = StringIO()
        
        for fragment in self.fragments:
            fragment.append_to(buffer, locale, args, kwargs)
        
        return buffer.getvalue()
    
    def __repr__(self):
        return 'MessageFormatter%r' % (self.fragments,)

def text_message_formatter(text):
    '''Convenience function to turn a string into a message.'''
    return MessageFormatter(TextFragment(text))

class MessageParser(object):
    '''Parse a pattern into a MessageFormatter.
    
    See test_formatting.py for examples.'''
    
    def __init__(self, ts):
        self.ts = ts
        
        self.start_pattern = re.compile(r'\{+')
    
    def parse(self, message):
        if isinstance(message, str):
            return MessageFormatter([TextFragment(message)])
        
        fragments = []
        
        try:
            self.parse0(fragments, message)
        except Exception as e:
            raise I18nException('Error parsing %r' % (message,)) from e
        
        return MessageFormatter(fragments)
    
    def parse0(self, fragments, message):
        for part in message:
            if isinstance(part, str):
                fragments.append(TextFragment(part))
            elif isinstance(part, dict):
                arg = part['arg']
                
                options = dict(part)
                del options['arg']
                
                if isinstance(arg, int):
                    ref = IndexRef(arg)
                else:
                    ref = NameRef(arg)
                
                fragments.append(ArgumentFragment(self.ts, ref, options))
            else:
                raise I18nException('Unsupported part: %r' % part)
