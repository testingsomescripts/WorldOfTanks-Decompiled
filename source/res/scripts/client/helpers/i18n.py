# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/i18n.py
import types
import json
import gettext
from errno import ENOENT
from collections import defaultdict
from encodings import utf_8
import ResMgr
from debug_utils import LOG_WARNING, LOG_CURRENT_EXCEPTION
_I18N_KEY_PREFIX = '#'
_I18N_KEY_SEPARATOR = ':'
_I18N_EMPTY_FLAG = '?empty?'
_I18N_EMPTY_TEXT = ''

class _PyFileWrapper(object):

    def __init__(self, bwDataSection):
        self._ds = bwDataSection

    def read(self):
        return self._ds.asBinary


class _Translations(gettext.GNUTranslations):

    def gettext(self, message):
        if message not in self._catalog:
            return message
        tmsg = self._catalog[message]
        if self._output_charset:
            return tmsg.encode(self._output_charset)
        return tmsg.encode(self._charset) if self._charset else tmsg


def _getTranslator(domain):
    mofile = ResMgr.openSection('text/LC_MESSAGES/%s.mo' % domain)
    if mofile is None:
        raise IOError(ENOENT, 'Translation file is not found', domain)
    return _Translations(_PyFileWrapper(mofile))


class _TranslatorsCache(defaultdict):

    def __missing__(self, key):
        self[key] = value = _getTranslator(key)
        return value


g_translators = _TranslatorsCache()

def convert(utf8String):
    try:
        return utf_8.decode(utf8String)[0]
    except Exception:
        LOG_CURRENT_EXCEPTION()
        LOG_WARNING('Wrong UTF8 string', utf8String)
        return utf_8.decode('----')[0]


def isValidKey(key):
    return key and key[0] == _I18N_KEY_PREFIX and _I18N_KEY_SEPARATOR in key


def doesTextExist(key):
    if not isValidKey(key):
        return False
    moName, subkey = key[1:].split(_I18N_KEY_SEPARATOR, 1)
    if not moName or not subkey:
        return False
    translator = g_translators[moName]
    text = translator.gettext(subkey)
    return text != subkey


def makeString(key, *args, **kwargs):
    try:
        if not key or key[0] != _I18N_KEY_PREFIX:
            return key
        moName, subkey = key[1:].split(_I18N_KEY_SEPARATOR, 1)
        if not moName or not subkey:
            return key
        translator = g_translators[moName]
        text = translator.gettext(subkey)
        if text == _I18N_EMPTY_FLAG:
            text = _I18N_EMPTY_TEXT
        if args:
            try:
                text = text % args
            except TypeError:
                LOG_WARNING("Arguments do not match string read by key '%s': %s", (key, args))
                return key

        elif kwargs:
            try:
                text = text % kwargs
            except TypeError:
                LOG_WARNING("Arguments do not match string read by key '%s': %s", (key, kwargs))
                return key

        return text
    except Exception:
        LOG_CURRENT_EXCEPTION()
        LOG_WARNING('Key string incompatible with args', key, args, kwargs)
        return key


def makeStringJSON(key, argsStr):
    try:
        args = json.loads(argsStr)
        if isinstance(args, dict):
            utf8args = {}
            for k, v in args.iteritems():
                utf8args[k.encode('utf-8')] = v.encode('utf-8')

            return makeString(key, **utf8args)
        utf8args = []
        for v in args:
            if isinstance(v, str):
                utf8args.append(v.encode('utf-8'))
            utf8args.append(v)

        return makeString(key, *tuple(utf8args))
    except Exception:
        LOG_CURRENT_EXCEPTION()
        LOG_WARNING('Failed to translate JSON-encoded string to dict or list', key, argsStr)
        return key


def encodeUtf8(string):
    return string.encode('utf-8', 'ignore') if isinstance(string, types.UnicodeType) else string
