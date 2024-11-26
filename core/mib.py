# ----------------------------------------------------------------------
# MIB lookup utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from threading import Lock

# Third-party modules
from typing import Union, Tuple, Dict, Optional, Any, Callable

# NOC modules
from noc.config import config
from noc.core.snmp.util import render_tc

logger = logging.getLogger(__name__)


class MIBRegistry(object):
    PATHS = config.get_customized_paths("cmibs")
    load_lock = Lock()

    def __init__(self):
        self.mib: Dict[str, str] = {}
        self.hints = {}
        self.loaded_mibs = set()

    def __getitem__(self, item: Union[str, Tuple[str, int]]) -> str:
        def maybe_get(k: str) -> str:
            v = self.mib.get(k)
            if v is not None:
                return v
            # Missed in the MIB or missed MIB
            mib_name = k.split("::", 1)[0]
            with self.load_lock:
                if self.is_loaded(mib_name):
                    # Missed in the MIB
                    raise KeyError(item)
                # Load MIB
                self.load_mib(mib_name)
            # Get or raise KeyError
            return self.mib[k]

        if isinstance(item, str):
            if ":" not in item:
                return item  # No conversion needed
            if "." in item:
                # <name>(.\d)+
                name, rest = item.split(".", 1)
                return maybe_get(name) + "." + rest
            # <name>
            return maybe_get(item)
        # (<name>, int)
        return ".".join([maybe_get(item[0])] + [str(x) for x in item[1:]])

    @staticmethod
    def mib_to_modname(name: str) -> str:
        """
        Convert MIB name to module name (without .py)
        :param name: MIB name, like IF-MIB
        :return: Module name, like if_mib
        """
        return name.lower().replace("-", "_")

    def load_mib(self, name: str) -> None:
        """
        Load MIB by name

        :param name: MIB name, like IF-MIB
        :return:
        """
        mod_name = self.mib_to_modname(name)
        if self.is_loaded(name):
            return
        for root in self.PATHS:
            if root != "cmibs":
                # Custom script
                base_name = "noc.custom"
            else:
                # Common script
                base_name = "noc"
            logger.debug("Loading MIB: %s", name)
            mn = "%s.cmibs.%s" % (base_name, mod_name)
            try:
                m = __import__(mn, {}, {}, ["MIB"])
            except ModuleNotFoundError:
                continue
            self.mib.update(getattr(m, "MIB"))
            if hasattr(m, "DISPLAY_HINTS"):
                self.hints.update(m.DISPLAY_HINTS)
            self.loaded_mibs.add(name)
            return
        raise KeyError(name)

    def is_loaded(self, name: str) -> bool:
        """
        Check MIB is loaded
        :param name:
        :return:
        """
        return name in self.loaded_mibs

    def reset(self) -> None:
        """
        Reset MIB cache

        :return:
        """
        with self.load_lock:
            self.mib = {}
            self.loaded_mibs = set()

    @staticmethod
    def longest_match(d: Dict[str, Any], k: str) -> Optional[Any]:
        """
        Returns longest match of key `k` in dict `d`
        :param d:
        :param k:
        :return:
        """
        for prefix in d:
            if prefix == k or k.startswith(prefix + "."):
                return d.get(prefix)
        return None

    def render(
        self,
        oid: str,
        value: bytes,
        display_hints: Dict[str, Callable[[str, bytes], Union[str, bytes]]] = None,
    ) -> str:
        """Apply display-hint"""
        if display_hints:
            hint = self.longest_match(display_hints, oid)
            if hint:
                return hint(oid, value)
        hint = self.longest_match(self.hints, oid)
        if hint:
            return render_tc(value, hint[0], hint[1])
        return value.decode(encoding="latin1", errors="backslashreplace")


# MIB singleton
mib = MIBRegistry()
