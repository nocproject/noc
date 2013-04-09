# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Translation utilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.template import Template, Context


def get_translated_text(lang, texts, name):
    if lang not in texts:
        # Fallback to "en" when no translation for language
        lang = "en"
    if lang in texts and name not in texts[lang] and lang != "en":
        # Fallback to "en" when not translation for message
        lang = "en"
    try:
        return texts[lang][name]
    except KeyError:
        return "--- UNTRANSLATED MESSAGE ---"


def get_translated_template(lang, texts, name, vars):
    t = Template(get_translated_text(lang, texts, name))
    return t.render(Context(vars))
