# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## pyparsing parser
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import BaseParser


class BasePyParser(BaseParser):
    def __init__(self, managed_object):
        super(BasePyParser, self).__init__(managed_object)
        self.pending_facts = []

    def create_parser(self):
        """
        Return ParserElement instance
        """
        raise NotImplementedError()

    def parse(self, config):
        """
        Parse config, yield and modify facts
        """
        parser = self.create_parser()
        for _ in parser.scanString(config):
            for f in self.iter_facts():
                yield f

    def on_tokens(self, tokens):
        print "@@@", tokens
