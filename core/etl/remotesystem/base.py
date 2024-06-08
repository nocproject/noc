# ----------------------------------------------------------------------
# Base Remote System
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021, The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from typing import Optional

# NOC modules
from noc.core.log import PrefixLoggerAdapter

logger = logging.getLogger(__name__)


class BaseRemoteSystem(object):
    extractors = {}

    extractors_order = [
        "label",
        "networksegmentprofile",
        "networksegment",
        "object",
        "container",
        "resourcegroup",
        "managedobjectprofile",
        "administrativedomain",
        "authprofile",
        "l2domain",
        "ttsystem",
        "project",
        "ipvrf",
        "ipprefixprofile",
        "ipprefix",
        "ipaddressprofile",
        "ipaddress",
        "managedobject",
        "link",
        "sensor",
        "subscriberprofile",
        "subscriber",
        "serviceprofile",
        "service",
        "fmevent",
        "admdiv",
        "street",
        "building",
        "address",
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

    def extract(self, extractors=None, incremental: bool = False, checkpoint: Optional[str] = None):
        extractors = extractors or []
        for en in reversed(self.extractors_order):
            if extractors and en not in extractors:
                self.logger.info("Skipping extractor %s", en)
                continue
            if en not in self.extractors:
                self.logger.info("Extractor %s is not implemented. Skipping", en)
                continue
            # @todo: Config
            xc = self.extractors[en](self)
            xc._force_checkpoint = checkpoint
            xc.extract(incremental=incremental)

    def load(self, loaders=None):
        loaders = loaders or []
        # Build chain
        chain = self.get_loader_chain()
        # Add & Modify
        for ll in chain:
            if loaders and ll.name not in loaders:
                ll.load_mappings()
                continue
            ll.load()
            ll.save_state()
        # Remove in reverse order
        for ll in reversed(list(chain)):
            ll.purge()

    def check(self, out):
        chain = self.get_loader_chain()
        # Check
        summary = []
        n_errors = 0
        for ll in chain:
            n = ll.check(chain)
            if n:
                ss = "%d errors" % n
            else:
                ss = "OK"
            summary += ["%s.%s: %s" % (self.name, ll.name, ss)]
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
