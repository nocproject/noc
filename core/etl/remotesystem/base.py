# ----------------------------------------------------------------------
# Base Remote System
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024, The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from dataclasses import dataclass
from time import perf_counter
from typing import Optional, List, Dict, Tuple

# NOC modules
from noc.core.log import PrefixLoggerAdapter

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class StepResult:
    step: str
    loader: str
    duration: int
    error: Optional[str] = None
    summary: Optional[Dict[str, int]] = None


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
        self.name: str = remote_system.name
        self.config: Dict[str, str] = self.remote_system.config
        self.logger = PrefixLoggerAdapter(logger, self.name)

    def get_loader_chain(self):
        from noc.core.etl.loader.chain import LoaderChain

        chain = LoaderChain(self)
        for ld in self.extractors_order:
            chain.get_loader(ld)
        return chain

    def extract(
        self, extractors=None, incremental: bool = False, checkpoint: Optional[str] = None
    ) -> List[StepResult]:
        extractors = extractors or []
        r = []
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
            t0 = perf_counter()
            xc.extract(incremental=incremental)
            r.append(
                StepResult(
                    step="extract",
                    loader=en,
                    summary={
                        "extract": 0,
                        "fatal_problems": len(xc.fatal_problems),
                        "quality_problems": len(xc.quality_problems),
                    },
                    duration=int(perf_counter() - t0),
                )
            )
        return r

    def load(self, loaders=None, check_current_state: bool = False) -> List[StepResult]:
        loaders = loaders or []
        # Build chain
        chain = self.get_loader_chain()
        r = []
        # Add & Modify
        for ll in chain:
            if loaders and ll.name not in loaders:
                ll.load_mappings()
                continue
            t0 = perf_counter()
            ll.load(check_state_exists=check_current_state)
            ll.save_state()
            r.append(
                StepResult(
                    step="load",
                    loader=ll.name,
                    summary={
                        "add": ll.c_add,
                        "change": ll.c_change,
                        "delete": len(ll.pending_deletes),
                    },
                    duration=int(perf_counter() - t0),
                )
            )
        # Remove in reverse order
        for ll in reversed(list(chain)):
            ll.purge()
        return r

    def check(self, out) -> Tuple[int, List[StepResult]]:
        chain = self.get_loader_chain()
        # Check
        summary = []
        r = []
        n_errors = 0
        for ll in chain:
            t0 = perf_counter()
            n = ll.check(chain)
            if n:
                ss = "%d errors" % n
            else:
                ss = "OK"
            summary += ["%s.%s: %s" % (self.name, ll.name, ss)]
            n_errors += n
            r.append(
                StepResult(
                    step="check",
                    loader=ll.name,
                    summary={"check_errors": n},
                    duration=int(perf_counter() - t0),
                )
            )
        if summary:
            out.write("Summary:\n")
            out.write("\n".join(summary) + "\n")
        return n_errors, r

    @classmethod
    def extractor(cls, c):
        """Decorator for extractor"""
        cls.extractors[c.name] = c
        return c
