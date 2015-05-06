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
    # Optional regular expression to match interface block range
    # Must contain group *name* holding interface name
    RX_INTERFACE_BLOCK = None
    # Enable packrat optimization
    ENABLE_PACKRAT = True

    def __init__(self, managed_object):
        super(BasePyParser, self).__init__(managed_object)
        self.pending_facts = []

    def create_parser(self):
        """
        Return ParserElement instance
        """
        raise NotImplementedError()

    def preprocess(self, config):
        """
        Perform config preprocessing
        """
        return config

    def parse(self, config):
        """
        Parse config, yield and modify facts
        """
        parser = self.create_parser()
        if self.ENABLE_PACKRAT:
            parser.enablePackrat()
        for _ in parser.scanString(self.preprocess(config)):
            for f in self.iter_facts():
                yield f
        if self.RX_INTERFACE_BLOCK:
            for match in self.RX_INTERFACE_BLOCK.finditer(config):
                self.register_interface_section(
                    match.group("name"),
                    match.start(), match.end()
                )

    def on_tokens(self, tokens):
        print "@@@", tokens
