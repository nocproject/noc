# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Tokenizer loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from noc.core.loader.base import BaseLoader
from .base import BaseTokenizer


class TokenizerLoader(BaseLoader):
    name = "tokenizer"
    base_cls = BaseTokenizer
    base_path = ("core", "tokenizer")


# Create singleton object
loader = TokenizerLoader()
