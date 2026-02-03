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
from typing import Optional, List, Dict, Tuple, Any

# NOC modules
from noc.core.log import PrefixLoggerAdapter
from noc.core.fm.event import Event

logger = logging.getLogger(__name__)
FM_EVENT_EXTRACTOR = "fmevent"


@dataclass(frozen=True)
class StepResult:
    step: str
    loader: str
    duration: float
    error: Optional[str] = None
    summary: Optional[Dict[str, int]] = None

    @property
    def has_changed(self) -> bool:
        if not self.summary:
            return False
        changes = 0
        for s, c in self.summary.items():
            if s in {"add", "change", "delete"}:
                changes += c
        return bool(changes)


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
        "pmagent",
        "managedobject",
        "link",
        "sensor",
        "subscriberprofile",
        "subscriber",
        "serviceprofile",
        "service",
        FM_EVENT_EXTRACTOR,
        "admdiv",
        "street",
        "building",
        "address",
        "maintenance",
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
            if not self.extractors or en not in self.extractors[self.__module__]:
                self.logger.info("Extractor %s is not implemented. Skipping", en)
                continue
            # @todo: Config
            xc = self.extractors[self.__module__][en](self)
            xc._force_checkpoint = checkpoint
            t0 = perf_counter()
            if en == FM_EVENT_EXTRACTOR and self.remote_system.event_sync_mode == "P":
                self.logger.info("For event extractor enable push policy. Skipping")
                continue
            if en == FM_EVENT_EXTRACTOR and not incremental:
                incremental = self.remote_system.event_sync_mode == "I"
            xc.extract(incremental=incremental)
            r.append(
                StepResult(
                    step="extract",
                    loader=en,
                    summary={
                        "extract": xc.extracted,
                        "fatal_problems": len(xc.fatal_problems),
                        "quality_problems": len(xc.quality_problems),
                    },
                    duration=round(perf_counter() - t0, 2),
                )
            )
        return r

    def load(self, loaders=None) -> List[StepResult]:
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
            ll.load()
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
                    duration=round(perf_counter() - t0, 2),
                )
            )
        # Remove in reverse order
        for ll in reversed(list(chain)):
            ll.purge()
        return r

    def check(self, extractors=None, out=None) -> Tuple[int, List[StepResult]]:
        extractors = extractors or []
        chain = self.get_loader_chain()
        # Check
        summary = []
        r = []
        n_errors = 0
        for ll in chain:
            if extractors and ll.name not in extractors:
                continue
            t0 = perf_counter()
            n = ll.check(chain)
            if n:
                ss = "%d errors" % n
            else:
                ss = "OK"
            summary += [f"{self.name}.{ll.name}: {ss}"]
            n_errors += n
            r.append(
                StepResult(
                    step="check",
                    loader=ll.name,
                    summary={"check_errors": n},
                    duration=round(perf_counter() - t0, 2),
                )
            )
        if summary and out:
            out.write("Summary:\n")
            out.write("\n".join(summary) + "\n")
        return n_errors, r

    def get_events(self, events: List[Dict[str, Any]], deferred, **kwargs) -> List[Event]:
        """Push extract FM Events"""
        if not self.extractors or FM_EVENT_EXTRACTOR not in self.extractors[self.__module__]:
            self.logger.info("Extractor %s is not implemented. Skipping", FM_EVENT_EXTRACTOR)
            return []
        if self.remote_system.event_sync_mode != "P":
            return []
        xc = self.extractors[self.__module__][FM_EVENT_EXTRACTOR](self)
        if not hasattr(xc, "get_collected_events"):
            return []
        return xc.get_collected_events(events, deferred)

    def get_metric_extractor(self):
        """"""
        if "metric" in self.extractors[self.__module__]:
            return self.extractors[self.__module__]["metric"](self)
        return None

    @classmethod
    def extractor(cls, c):
        """Decorator for extractor"""
        if cls.__module__ not in cls.extractors:
            cls.extractors[cls.__module__] = {}
        cls.extractors[cls.__module__][c.name] = c
        cls.extractors[c.name] = c
        return c
