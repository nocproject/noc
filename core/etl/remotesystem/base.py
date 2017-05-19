# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Base Remote System
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016, The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from noc.lib.log import PrefixLoggerAdapter

logger = logging.getLogger(__name__)


class BaseRemoteSystem(object):
    extractors = {}

    extractors_order = [
        "admdiv",
        "networksegment",
        "container",
        "terminationgroup",
        "managedobjectprofile",
        "administrativedomain",
        "ttsystem",
        "managedobject",
        "link",
        "subscriber",
        "serviceprofile",
        "service",
        "ttmap"
    ]

    def __init__(self, remote_system):
        self.remote_system = remote_system
        self.name = remote_system.name
        self.config = self.remote_system.config
        self.logger = PrefixLoggerAdapter(logger, self.name)

    def get_loader_chain(self):
        from noc.core.etl.loader.chain import LoaderChain

        chain = LoaderChain(self)
        for ld in self.extractors_order:
            chain.get_loader(ld)
        return chain

    def extract(self, extractors=None):
        extractors = extractors or []
        for en in reversed(self.extractors_order):
            if extractors and en not in extractors:
                self.logger.info("Skipping extractor %s", en)
            if en not in self.extractors:
                self.logger.info(
                    "Extractor %s is not implemented. Skipping", en)
            # @todo: Config
            xc = self.extractors[en]()
            xc.extract()

    def load(self, loaders=None):
        loaders = loaders or []
        # Build chain
        chain = self.get_loader_chain()
        # Add & Modify
        for l in chain:
            if loaders and l not in loaders:
                l.load_mappings()
                continue
            l.load()
            l.save_state()
        # Remove in reverse order
        for l in reversed(list(chain)):
            l.purge()

    def check(self, out):
        chain = self.get_loader_chain()
        # Check
        summary = []
        n_errors = 0
        for l in chain:
            n = l.check(chain)
            if n:
                ss = "%d errors" % n
            else:
                ss = "OK"
            summary += ["%s.%s: %s" % (self.name, l.name, ss)]
            n_errors += n
        if summary:
            out.write("Summary:\n")
            out.write("\n".join(summary) + "\n")
        return n_errors

    @classmethod
    def extractor(cls, c):
        """
        Decorator for extractor
        :return: 
        """
        cls.extractors[c.name] = c
        return c
