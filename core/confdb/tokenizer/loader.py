# ----------------------------------------------------------------------
# Tokenizer loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.loader.base import BaseLoader
from .base import BaseTokenizer


class TokenizerLoader(BaseLoader):
    name = "tokenizer"
    base_cls = BaseTokenizer
    base_path = ("core", "confdb", "tokenizer")


# Create singleton object
loader = TokenizerLoader()
