# ----------------------------------------------------------------------
# INI file tokenizer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from configparser import RawConfigParser

# NOC modules
from .base import BaseTokenizer


class INITokenizer(BaseTokenizer):
    """
    .ini file parser. Yields (section, key, value)
    """

    name = "ini"

    def __init__(self, data):
        super().__init__(data)
        self.config = RawConfigParser()
        self.config.read_string(data)

    def __iter__(self):
        for section in sorted(self.config.sections()):
            for k, v in sorted(self.config.items(section)):
                yield section, k, v
