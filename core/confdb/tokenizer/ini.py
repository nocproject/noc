# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# INI file tokenizer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# Third-party modules
from six.moves.configparser import RawConfigParser
from six import StringIO
import six

# NOC modules
from .base import BaseTokenizer


class INITokenizer(BaseTokenizer):
    """
    .ini file parser. Yields (section, key, value)
    """

    name = "ini"

    def __init__(self, data):
        super(INITokenizer, self).__init__(data)
        self.config = RawConfigParser()
        if six.PY3:
            self.config.read_string(data)
        else:
            f = StringIO(data)
            self.config.readfp(f)

    def __iter__(self):
        for section in sorted(self.config.sections()):
            for k, v in sorted(self.config.items(section)):
                yield section, k, v
