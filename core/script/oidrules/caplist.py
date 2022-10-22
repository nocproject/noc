# ----------------------------------------------------------------------
# CapabilityListRule
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .oid import OIDRule


class CapabilityListRule(OIDRule):
    """
    Expand {{item}} from capability
    capability: String capability, separated by *separator*
    separator: String separator, comma by default
    strip: Strip resulting item, remove spaces from both sides
    """

    name = "caplist"

    def __init__(
        self,
        oid,
        type=None,
        scale=1,
        units="1",
        capability=None,
        separator=",",
        strip=True,
        default=None,
        labels=None,
    ):
        super().__init__(oid, type=type, scale=scale, units=units)
        self.capability = capability
        self.separator = separator
        self.strip = strip
        self.default = default
        self.labels = tuple(labels) if labels else None

    def iter_oids(self, script, cfg):
        if self.capability and script.has_capability(self.capability):
            for i in script.capabilities[self.capability].split(self.separator):
                if self.strip:
                    i = i.strip()
                if not i:
                    continue
                oid = self.expand_oid(item=i)
                if not oid:
                    continue
                if self.labels is None:
                    yield oid, self.type, self.scale, self.units, cfg.labels
                    continue
                labels = []
                for item in self.labels:
                    if "item" in item:
                        item = item.replace("item", i)
                    labels.append(item)
                yield oid, self.type, self.scale, self.units, tuple(labels)
        else:
            if self.default is not None:
                oid = self.expand_oid(item=self.default)
                if oid:
                    yield oid, self.type, self.scale, self.units, cfg.labels
