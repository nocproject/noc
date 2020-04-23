# ----------------------------------------------------------------------
# VLANConstraint
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator

# Third-party modules
from typing import Dict, Set
import cachetools

# NOC modules
from noc.inv.models.link import Link
from noc.inv.models.subinterface import SubInterface
from .base import BaseConstraint


class VLANConstraint(BaseConstraint):
    """
    Follow only links with specific VLANs

    :param vlan: VLAN id to check
    :param allow_tagged: Allow links with tagged `vlan`
    :param allow_untagged: Allow links with untagged `vlan`
    :param strict: True - Both ends of the links must satisfy criteria,
        False - At least one end of the link must satisfy criteria.
    """

    def __init__(
        self,
        vlan: int = 1,
        allow_tagged: bool = True,
        allow_untagged: bool = True,
        strict: bool = True,
    ) -> None:
        super(VLANConstraint, self).__init__()
        self.vlan = vlan
        self.allow_tagged = allow_tagged
        self.allow_untagged = allow_untagged
        self._is_valid_link_cache: Dict[Link, bool] = {}
        self.strict = strict

    @cachetools.cachedmethod(operator.attrgetter("_is_valid_link_cache"))
    def is_valid_link(self, link: Link) -> bool:
        bridged_mo: Set[int] = set()
        tagged_mo: Set[int] = set()
        untagged_mo: Set[int] = set()
        l3_mo = set()
        for doc in SubInterface._get_collection().find(
            {"interface": {"$in": link.interface_ids}},
            {
                "_id": 0,
                "managed_object": 1,
                "enabled_afi": 1,
                "untagged_vlan": 1,
                "tagged_vlans": 1,
                "vlan_ids": 1,
            },
        ):
            if "BRIDGE" in doc["enabled_afi"]:
                bridged_mo.add(doc["managed_object"])
            if doc.get("untagged_vlan") == self.vlan:
                untagged_mo.add(doc["managed_object"])
            if self.vlan in doc.get("tagged_vlans", []):
                tagged_mo.add(doc["managed_object"])
            if self.vlan in doc.get("vlan_ids", []):
                l3_mo.add(doc["managed_object"])
        if self.strict:
            # Both ends must satisfy
            if len(bridged_mo) > 1 and (
                (self.allow_tagged and len(tagged_mo) > 1)
                or (self.allow_untagged and len(untagged_mo) > 1)
            ):
                # Bridge-to-Bridge
                return True
            if (
                len(bridged_mo) == 1
                and ((self.allow_tagged and tagged_mo) or (self.allow_untagged and untagged_mo))
                and len(l3_mo) == 1
            ):
                # L3 to bridge
                return True
        else:
            if len(bridged_mo) == 1 and (
                (self.allow_tagged and len(tagged_mo) > 1)
                or (self.allow_untagged and len(untagged_mo) > 1)
            ):
                # Bridge-to-Bridge
                return True
            if len(l3_mo) == 1:
                # L3 to bridge
                return True
        return False
